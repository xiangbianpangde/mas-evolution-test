# core_002 Answer

**Run**: 1
**Iterations**: 1

## Answer

# TB 级滑动日志解析器设计

## 架构概览

```
┌─────────────────────────────────────────────────────────────────┐
│                     滑动日志解析器架构                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐       │
│  │  文件分片器   │ -> │  流式解析器   │ -> │  窗口聚合器   │       │
│  │  (mmap)      │    │  (Generator) │    │  (Dynamic)   │       │
│  └──────────────┘    └──────────────┘    └──────────────┘       │
│         │                   │                   │               │
│         v                   v                   v               │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              内存管理 & 缓冲区池                           │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                  │
│                              v                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐       │
│  │  结果输出器   │    │  监控指标     │    │  并行处理     │       │
│  │  (Iterator)  │    │  (进度/速率)  │    │  (ThreadPool)│       │
│  └──────────────┘    └──────────────┘    └──────────────┘       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## 核心代码实现

```python
#!/usr/bin/env python3
"""
TB 级滑动日志解析器
支持动态窗口大小、流式处理、并行处理
"""

import os
import mmap
import time
import gzip
import logging
from pathlib import Path
from typing import (
    Iterator, Callable, Any, Optional, List, Tuple, Dict, Union
)
from dataclasses import dataclass, field
from collections import deque
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock, Event
from enum import Enum, auto
import re
import json
import struct
import mmap as mm

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class WindowType(Enum):
    """窗口类型枚举"""
    TIME_BASED = auto()      # 基于时间
    BYTE_BASED = auto()      # 基于字节数
    LINE_BASED = auto()      # 基于行数
    PATTERN_BASED = auto()   # 基于模式匹配


@dataclass
class WindowConfig:
    """窗口配置"""
    window_type: WindowType = WindowType.LINE_BASED
    initial_size: int = 1000              # 初始窗口大小
    min_size: int = 100                   # 最小窗口
    max_size: int = 100000                # 最大窗口
    adaptive_threshold: float = 0.8       # 自适应阈值
    growth_factor: float = 1.5            # 增长因子
    shrink_factor: float = 0.5            # 收缩因子
    
    def __post_init__(self):
        assert self.min_size <= self.initial_size <= self.max_size


@dataclass
class ProcessingStats:
    """处理统计信息"""
    bytes_processed: int = 0
    lines_processed: int = 0
    records_yielded: int = 0
    start_time: float = field(default_factory=time.time)
    last_update_time: float = field(default_factory=time.time)
    
    @property
    def throughput_mbps(self) -> float:
        elapsed = time.time() - self.start_time
        return self.bytes_processed / (1024 * 1024 * elapsed) if elapsed > 0 else 0
    
    @property
    def lines_per_second(self) -> float:
        elapsed = time.time() - self.start_time
        return self.lines_processed / elapsed if elapsed > 0 else 0
    
    @property
    def elapsed_seconds(self) -> float:
        return time.time() - self.start_time
    
    def to_dict(self) -> dict:
        return {
            "bytes_processed": self.bytes_processed,
            "bytes_processed_gb": self.bytes_processed / (1024**3),
            "lines_processed": self.lines_processed,
            "records_yielded": self.records_yielded,
            "elapsed_seconds": round(self.elapsed_seconds, 2),
            "throughput_mbps": round(self.throughput_mbps, 2),
            "lines_per_second": round(self.lines_per_second, 0)
        }


@dataclass
class ParseResult:
    """解析结果"""
    window_id: int
    window_type: WindowType
    data: List[Dict[str, Any]]
    start_offset: int
    end_offset: int
    stats: ProcessingStats
    metadata: Dict[str, Any] = field(default_factory=dict)


class SlidingWindowParser:
    """
    支持动态窗口大小的滑动日志解析器
    
    特性:
    - 流式处理：逐行/逐块读取，避免全量加载
    - 动态窗口：根据数据特征自动调整窗口大小
    - 多种窗口类型：时间、字节、行数、模式
    - 并行处理：多文件并行处理
    - 内存管理：缓冲区池，内存上限控制
    """
    
    # 常见日志格式的正则表达式
    LOG_PATTERNS = {
        'apache_combined': re.compile(
            r'(?P<ip>\S+) \S+ \S+ \[(?P<time>[^\]]+)\] '
            r'"(?P<request>[^"]*)" (?P<status>\d+) (?P<size>\S+)'
        ),
        'nginx_access': re.compile(
            r'(?P<ip>\S+) - \S+ \[(?P<time>[^\]]+)\] '
            r'"(?P<request>[^"]*)" (?P<status>\d+) (?P<size>\d+)'
        ),
        'json': re.compile(r'\{.*\}'),
        'syslog': re.compile(
            r'(?P<month>\w+)\s+(?P<day>\d+)\s+(?P<time>\S+)\s+(?P<host>\S+)\s+(?P<msg>.*)'
        ),
        'generic': re.compile(
            r'\[?(?P<timestamp>\d{4}[-/]\d{2}[-/]\d{2}[T\s]\d{2}:\d{2}:\d{2}[^\]]*)\]?\s*(?P<level>\w+)?\s*(?P<message>.*)'
        )
    }
    
    def __init__(
        self,
        file_path: Union[str, Path],
        window_config: Optional[WindowConfig] = None,
        log_format: str = 'generic',
        parse_func: Optional[Callable[[str], Dict[str, Any]]] = None,
        buffer_size: int = 64 * 1024 * 1024,  # 64MB 缓冲区
        max_memory_mb: int = 1024,             # 最大内存使用 1GB
        enable_parallel: bool = True,
        num_workers: int = 4,
        progress_callback: Optional[Callable[[ProcessingStats], None]] = None
    ):
        self.file_path = Path(file_path)
        self.window_config = window_config or WindowConfig()
        self.log_format = log_format
        self.parse_func = parse_func or self._create_parse_func(log_format)
        self.buffer_size = buffer_size
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self.enable_parallel = enable_parallel
        self.num_workers = num_workers
        self.progress_callback = progress_callback
        
        # 运行时状态
        self._current_window_size = self.window_config.initial_size
        self._window_id_counter = 0
        self._stats = ProcessingStats()
        self._stop_event = Event()
        self._lock = Lock()
        
        # 预编译的模式
        self._pattern = self.LOG_PATTERNS.get(log_format)
        
        # 验证文件
        self._validate_file()
        
    def _validate_file(self):
        """验证文件存在且可读"""
        if not self.file_path.exists():
            raise FileNotFoundError(f"文件不存在: {self.file_path}")
        if not self.file_path.is_file():
            raise ValueError(f"路径不是文件: {self.file_path}")
        
        file_size = self.file_path.stat().st_size
        logger.info(f"文件大小: {file_size / (1024**3):.2f} GB")
        
    def _create_parse_func(self, log_format: str) -> Callable[[str], Dict[str, Any]]:
        """根据日志格式创建解析函数"""
        if log_format == 'json':
            def parse(line: str) -> Dict[str, Any]:
                try:
                    return json.loads(line.strip())
                except json.JSONDecodeError:
                    return {'raw': line.strip(), 'parse_error': True}
        elif log_format in self.LOG_PATTERNS:
            pattern = self.LOG_PATTERNS[log_format]
            def parse(line: str) -> Dict[str, Any]:
                match = pattern.match(line.strip())
                if match:
                    return match.groupdict()
                return {'raw': line.strip()}
        else:
            def parse(line: str) -> Dict[str, Any]:
                return {'raw': line.strip()}
        return parse
    
    def _get_file_size(self) -> int:
        """获取文件大小"""
        return self.file_path.stat().st_size
    
    def _stream_lines_mmap(self, start_offset: int = 0) -> Iterator[Tuple[int, str]]:
        """
        使用 mmap 流式读取行
        
        使用内存映射文件，对于大文件非常高效
        """
        file_size = self._get_file_size()
        
        with open(self.file_path, 'rb') as f:
            # 使用 mmap 进行内存映射
            with mm.mmap(f.fileno(), 0, access=mm.ACCESS_READ) as mmapped:
                offset = start_offset
                line_start = start_offset
                line_num = 0
                
                while offset < file_size:
                    # 查找行尾
                    newline_pos = mmapped.find(b'\n', offset)
                    
                    if newline_pos == -1:
                        # 最后一行没有换行符
                        newline_pos = file_size
                    
                    # 读取行
                    line_bytes = mmapped[line_start:newline_pos]
                    try:
                        line = line_bytes.decode('utf-8', errors='replace')
                    except Exception:
                        line = line_bytes.decode('latin-1', errors='replace')
                    
                    yield (line_start, line)
                    line_num += 1
                    
                    # 更新统计
                    self._stats.bytes_processed = newline_pos
                    self._stats.lines_processed = line_num
                    
                    offset = newline_pos + 1
                    line_start = offset
                    
                    # 进度回调
                    if line_num % 10000 == 0 and self.progress_callback:
                        self.progress_callback(self._stats)
    
    def _stream_lines_buffered(self, chunk_size: int = 1024 * 1024) -> Iterator[Tuple[int, str]]:
        """
        使用缓冲区流式读取
        
        适用于无法使用 mmap 的场景
        """
        file_size = self._get_file_size()
        offset = 0
        line_num = 0
        buffer = b''
        
        with open(self.file_path, 'rb') as f:
            while True:
                # 读取数据块
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                
                buffer += chunk
                offset += len(chunk)
                
                # 提取完整行
                while b'\n' in buffer:
                    line_end = buffer.index(b'\n')
                    line_bytes = buffer[:line_end]
                    buffer = buffer[line_end + 1:]
                    
                    try:
                        line = line_bytes.decode('utf-8', errors='replace')
                    except Exception:
                        line = line_bytes.decode('latin-1', errors='replace')
                    
                    start_offset = offset - len(buffer) - len(chunk) + len(line_bytes)
                    yield (start_offset, line)
                    line_num += 1
                    
                    self._stats.bytes_processed = offset
                    self._stats.lines_processed = line_num
                
                # 进度回调
                if line_num % 10000 == 0 and self.progress_callback:
                    self.progress_callback(self._stats)
            
            # 处理缓冲区中剩余的数据
            if buffer:
                try:
                    line = buffer.decode('utf-8', errors='replace')
                except Exception:
                    line = buffer.decode('latin-1', errors='replace')
                start_offset = offset - len(buffer)
                yield (start_offset, line)
    
    def _adjust_window_size(self, data: List[Dict], parse_time: float) -> int:
        """
        动态调整窗口大小
        
        根据处理时间和数据量自动调整
        """
        if not data:
            return self._current_window_size
        
        # 计算每条记录的平均解析时间
        avg_time_per_record = parse_time / len(data) if data else 0
        
        # 目标：每条记录解析时间不超过 1ms
        target_time = 0.001
        
        with self._lock:
            if avg_time_per_record < target_time * 0.5:
                # 处理太快，可以增大窗口
                new_size = int(self._current_window_size * self.window_config.growth_factor)
                if new_size > self._current_window_size:
                    logger.debug(f"增大窗口: {self._current_window_size} -> {new_size}")
                    self._current_window_size = min(new_size, self.window_config.max_size)
                    
            elif avg_time_per_record > target_time * 2:
                # 处理太慢，减小窗口
                new_size = int(self._current_window_size * self.window_config.shrink_factor)
                if new_size < self._current_window_size:
                    logger.debug(f"减小窗口: {self._current_window_size} -> {new_size}")
                    self._current_window_size = max(new_size, self.window_config.min_size)
        
        return self._current_window_size
    
    def _create_window(self, data: List[Dict], start_offset: int, end_offset: int) -> ParseResult:
        """创建窗口结果"""
        self._window_id_counter += 1
        return ParseResult(
            window_id=self._window_id_counter,
            window_type=self.window_config.window_type,
            data=data,
            start_offset=start_offset,
            end_offset=end_offset,
            stats=ProcessingStats(**self._stats.__dict__.copy()),
            metadata={
                'window_size': len(data),
                'actual_window_size': self._current_window_size
            }
        )
    
    def parse(
        self,
        start_offset: int = 0,
        max_windows: Optional[int] = None
    ) -> Iterator[ParseResult]:
        """
        解析文件，返回滑动窗口结果
        
        Args:
            start_offset: 起始偏移量（字节）
            max_windows: 最大窗口数量（用于测试）
            
        Yields:
            ParseResult: 窗口解析结果
        """
        logger.info(f"开始解析文件: {self.file_path}")
        logger.info(f"初始窗口大小: {self._current_window_size}")
        
        self._stats = ProcessingStats()
        window_data = []
        window_start_offset = start_offset
        window_lines = 0
        window_start_time = time.time()
        
        try:
            for offset, line in self._stream_lines_mmap(start_offset):
                if self._stop_event.is_set():
                    logger.info("收到停止信号")
                    break
                
                # 跳过空行
                stripped = line.strip()
                if not stripped:
                    continue
                
                # 解析行
                try:
                    parsed = self.parse_func(stripped)
                    window_data.append(parsed)
                except Exception as e:
                    logger.debug(f"解析错误: {e}, 行: {stripped[:100]}")
                
                window_lines += 1
                
                # 检查是否达到窗口大小
                if window_lines >= self._current_window_size:
                    # 计算处理时间并调整窗口
                    parse_time = time.time() - window_start_time
                    self._adjust_window_size(window_data, parse_time)
                    
                    # 创建窗口结果
                    result = self._create_window(
                        window_data,
                        window_start_offset,
                        offset
                    )
                    self._stats.records_yielded += 1
                    yield result
                    
                    # 重置窗口
                    window_data = []
                    window_start_offset = offset + 1
                    window_lines = 0
                    window_start_time = time.time()
                    
                    # 检查最大窗口数
                    if max_windows and self._stats.records_yielded >= max_windows:
                        logger.info(f"达到最大窗口数: {max_windows}")
                        break
            
            # 处理剩余数据
            if window_data:
                result = self._create_window(
                    window_data,
                    window_start_offset,
                    self._get_file_size()
                )
                yield result
                
        except Exception as e:
            logger.error(f"解析错误: {e}")
            raise
    
    def parse_with_filter(
        self,
        filter_func: Callable[[Dict[str, Any]], bool],
        **kwargs
    ) -> Iterator[ParseResult]:
        """
        带过滤条件的解析
        
        只返回满足条件的窗口
        """
        for result in self.parse(**kwargs):
            filtered_data = [item for item in result.data if filter_func(item)]
            if filtered_data:
                yield ParseResult(
                    window_id=result.window_id,
                    window_type=result.window_type,
                    data=filtered_data,
                    start_offset=result.start_offset,
                    end_offset=result.end_offset,
                    stats=result.stats,
                    metadata={**result.metadata, 'filtered': True}
                )
    
    def search(self, pattern: str, is_regex: bool = True) -> Iterator[Dict[str, Any]]:
        """
        搜索日志内容
        
        Args:
            pattern: 搜索模式
            is_regex: 是否使用正则表达式
            
        Yields:
            匹配的行数据
        """
        if is_regex:
            compiled = re.compile(pattern)
            matcher = lambda text: bool(compiled.search(text))
        else:
            pattern_lower = pattern.lower()
            matcher = lambda text: pattern_lower in text.lower()
        
        for result in self.parse():
            for item in result.data:
                raw = item.get('raw', json.dumps(item))
                if matcher(raw):
                    yield item
    
    def get_stats(self) -> ProcessingStats:
        """获取统计信息"""
        return self._stats
    
    def stop(self):
        """停止解析"""
        self._stop_event.set()
    
    def reset(self):
        """重置解析器状态"""
        self._stop_event.clear()
        self._current_window_size = self.window_config.initial_size
        self._window_id_counter = 0
        self._stats = ProcessingStats()


class ParallelLogParser:
    """
    并行日志解析器
    
    支持多个文件并行处理
    """
    
    def __init__(
        self,
        window_config: Optional[WindowConfig] = None,
        num_workers: int = 4,
        **parser_kwargs
    ):
        self.window_config = window_config
        self.num_workers = num_workers
        self.parser_kwargs = parser_kwargs
        self._total_stats = ProcessingStats()
        self._lock = Lock()
    
    def parse_files(
        self,
        file_paths: List[Union[str, Path]],
        progress_callback: Optional[Callable[[str, ProcessingStats], None]] = None
    ) -> Iterator[Tuple[Path, ParseResult]]:
        """
        并行解析多个文件
        
        Yields:
            (文件路径, 窗口结果)
        """
        with ThreadPoolExecutor(max_workers=self.num_workers) as executor:
            # 提交所有文件
            future_to_path = {
                executor.submit(
                    self._parse_single_file,
                    fp,
                    progress_callback
                ): fp
                for fp in file_paths
            }
            
            # 处理完成的结果
            for future in as_completed(future_to_path):
                path = future_to_path[future]
                try:
                    for result in future.result():
                        with self._lock:
                            self._total_stats.bytes_processed += (
                                result.end_offset - result.start_offset
                            )
                            self._total_stats.lines_processed += len(result.data)
                            self._total_stats.records_yielded += 1
                        yield (path, result)
                except Exception as e:
                    logger.error(f"文件 {path} 处理失败: {e}")
    
    def _parse_single_file(
        self,
        file_path: Union[str, Path],
        progress_callback: Optional[Callable[[str, ProcessingStats], None]]
    ) -> Iterator[ParseResult]:
        """解析单个文件"""
        def callback(stats: ProcessingStats):
            if progress_callback:
                progress_callback(str(file_path), stats)
        
        parser = SlidingWindowParser(
            file_path,
            window_config=self.window_config,
            progress_callback=callback,
            **self.parser_kwargs
        )
        
        for result in parser.parse():
            yield result


# ============================================================
# 使用示例和便捷函数
# ============================================================

def create_json_parser(
    file_path: Union[str, Path],
    window_size: int = 1000,
    **kwargs
) -> SlidingWindowParser:
    """创建 JSON 日志解析器"""
    def json_parse(line: str) -> Dict[str, Any]:
        try:
            return json.loads(line)
        except json.JSONDecodeError:
            return {'raw': line, 'error': 'json_parse_failed'}
    
    config = WindowConfig(
        window_type=WindowType.LINE_BASED,
        initial_size=window_size
    )
    return SlidingWindowParser(
        file_path,
        window_config=config,
        log_format='json',
        parse_func=json_parse,
        **kwargs
    )


def create_apache_parser(
    file_path: Union[str, Path],
    window_size: int = 1000,
    **kwargs
) -> SlidingWindowParser:
    """
