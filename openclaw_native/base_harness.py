#!/usr/bin/env python3
"""
AutoMAS OpenClaw Native Harness Framework v1.0

统一的基础架构，所有 harness 版本继承此类。
提供标准化的：检查点、日志、错误处理、结果输出。
"""

import json
import time
import os
import sys
import traceback
from dataclasses import dataclass, asdict, field
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


# ============== 标准化 Result 类 ==============

@dataclass
class TaskResult:
    """标准化的任务结果"""
    task_id: str
    task_type: str
    executor_output: str = ""
    quality_score: float = 0.0
    depth_score: int = 3
    completeness_score: int = 3
    actionability_score: int = 3
    executor_tokens: int = 0
    evaluator_tokens: int = 0
    executor_latency_ms: float = 0.0
    evaluator_latency_ms: float = 0.0
    is_suspicious: bool = False
    suspicious_reason: str = ""
    error: str = ""
    iterations: int = 1
    used_web_search: bool = False
    reflection_type: str = "none"  # none, light, extended
    
    def to_dict(self) -> Dict:
        d = asdict(self)
        d['executor_output'] = self.executor_output[:500] if self.executor_output else ""
        return d


@dataclass 
class BenchmarkSummary:
    """标准化的汇总结果"""
    harness_version: str = ""
    paradigm: str = ""
    timestamp: str = ""
    elapsed_seconds: float = 0.0
    total_tasks: int = 0
    core_avg_score: float = 0.0
    gen_avg_score: float = 0.0
    gen_code_avg_score: float = 0.0
    gen_research_avg_score: float = 0.0
    core_review_avg_score: float = 0.0
    avg_actionability_level: float = 0.0
    total_executor_tokens: int = 0
    avg_latency_ms: float = 0.0
    composite_score: float = 0.0
    tasks_with_reflection: int = 0
    tasks_with_web_search: int = 0
    errors_count: int = 0
    
    def to_dict(self) -> Dict:
        return asdict(self)


# ============== 统一 Harness 基类 ==============

class BaseHarness:
    """
    统一的 Harness 基类
    所有版本应继承此类并实现 execute_task()
    """
    
    # API 配置（子类可覆盖）
    API_CONFIG = {
        "base_url": "https://api.minimaxi.com/anthropic",
        "model": "MiniMax-M2.7"
    }
    
    # 默认检查点文件
    CHECKPOINT_FILE = "checkpoint.json"
    RESULTS_FILE = "results.json"
    
    def __init__(self, api_key: str, checkpoint_file: str = None, results_file: str = None):
        self.api_key = api_key
        if checkpoint_file:
            self.CHECKPOINT_FILE = checkpoint_file
        if results_file:
            self.RESULTS_FILE = results_file
        
        # 运行时状态
        self.checkpoint: Dict = {}
        self.results: List[TaskResult] = []
        self.start_time: float = 0.0
        self.task_definitions: List[Dict] = []
        
        # 加载检查点
        self._load_checkpoint()
        
        logger.info(f"{self.__class__.__name__} initialized")
    
    # ============== 核心方法（子类实现） ==============
    
    def get_task_definitions(self) -> List[Dict]:
        """返回任务定义列表，子类必须实现"""
        raise NotImplementedError
    
    def execute_single_task(self, task: Dict) -> TaskResult:
        """执行单个任务，子类必须实现"""
        raise NotImplementedError
    
    def compute_composite_score(self, results: List[TaskResult]) -> float:
        """计算综合分数，子类可覆盖"""
        core = [r for r in results if not r.task_id.startswith("gen_")]
        gen = [r for r in results if r.task_id.startswith("gen_")]
        
        core_avg = sum(r.quality_score for r in core) / len(core) if core else 0
        gen_avg = sum(r.quality_score for r in gen) / len(gen) if gen else 0
        
        avg_action = sum(r.actionability_score for r in results) / len(results) if results else 0
        
        # 标准权重
        return core_avg * 0.45 + gen_avg * 0.45 + (avg_action * 10) * 0.1
    
    # ============== 标准生命周期 ==============
    
    def run_benchmark(self, force_rerun: bool = False) -> Dict:
        """运行完整 benchmark"""
        self.start_time = time.time()
        self.task_definitions = self.get_task_definitions()
        
        logger.info(f"Starting benchmark with {len(self.task_definitions)} tasks")
        
        # 加载已完成的
        completed = set(self.checkpoint.get("tasks_completed", []))
        results = []
        
        for i, task in enumerate(self.task_definitions):
            task_id = task["id"]
            
            if task_id in completed and not force_rerun:
                logger.info(f"[{task_id}] SKIP (already completed)")
                # 从检查点恢复结果
                for r in self.checkpoint.get("results", []):
                    if r["task_id"] == task_id:
                        results.append(TaskResult(**r))
                        break
                continue
            
            logger.info(f"[{task_id}] Running ({task['type']})...")
            
            try:
                result = self._run_task_with_error_handling(task)
            except Exception as e:
                logger.error(f"[{task_id}] EXCEPTION: {e}")
                result = TaskResult(
                    task_id=task_id,
                    task_type=task.get("type", "unknown"),
                    error=str(e)
                )
            
            results.append(result)
            
            # 保存检查点
            completed.add(task_id)
            self.checkpoint["tasks_completed"] = list(completed)
            self.checkpoint["results"] = [r.to_dict() for r in results]
            self._save_checkpoint()
            
            # 日志
            error_mark = " [ERROR]" if result.error else ""
            reflect_mark = f" [R:{result.reflection_type}]" if result.reflection_type != "none" else ""
            search_mark = " [SEARCH]" if result.used_web_search else ""
            logger.info(f"[{task_id}] Score: {result.quality_score}{error_mark}{reflect_mark}{search_mark}")
        
        # 计算汇总
        elapsed = time.time() - self.start_time
        summary = self._compute_summary(results, elapsed)
        
        # 保存结果
        self._save_results(summary, results)
        
        return {
            "summary": summary,
            "results": results
        }
    
    def _run_task_with_error_handling(self, task: Dict) -> TaskResult:
        """运行任务，包含错误处理和超时保护"""
        try:
            return self.execute_single_task(task)
        except Exception as e:
            logger.warning(f"[{task['id']}] Error in execute_single_task: {e}")
            logger.warning(traceback.format_exc())
            
            # 返回错误结果
            return TaskResult(
                task_id=task["id"],
                task_type=task.get("type", "unknown"),
                error=str(e),
                executor_latency_ms=0,
                evaluator_latency_ms=0
            )
    
    def _compute_summary(self, results: List[TaskResult], elapsed: float) -> BenchmarkSummary:
        """计算汇总统计"""
        total = len(results)
        core = [r for r in results if not r.task_id.startswith("gen_")]
        gen = [r for r in results if r.task_id.startswith("gen_")]
        
        core_avg = sum(r.quality_score for r in core) / len(core) if core else 0
        gen_avg = sum(r.quality_score for r in gen) / len(gen) if gen else 0
        
        # Gen 子类统计
        gen_code = [r for r in gen if r.task_type == "code"]
        gen_research = [r for r in gen if r.task_type == "research"]
        gen_review = [r for r in gen if r.task_type == "review"]
        
        gen_code_avg = sum(r.quality_score for r in gen_code) / len(gen_code) if gen_code else 0
        gen_research_avg = sum(r.quality_score for r in gen_research) / len(gen_research) if gen_research else 0
        
        total_tokens = sum(r.executor_tokens for r in results)
        avg_latency = sum(r.executor_latency_ms + r.evaluator_latency_ms for r in results) / total if total > 0 else 0
        avg_action = sum(r.actionability_score for r in results) / total if total > 0 else 0
        
        composite = self.compute_composite_score(results)
        
        return BenchmarkSummary(
            harness_version=self.__class__.__name__,
            paradigm=getattr(self, 'PARADIGM', 'unknown'),
            timestamp=datetime.now().isoformat(),
            elapsed_seconds=elapsed,
            total_tasks=total,
            core_avg_score=core_avg,
            gen_avg_score=gen_avg,
            gen_code_avg_score=gen_code_avg,
            gen_research_avg_score=gen_research_avg,
            avg_actionability_level=avg_action,
            total_executor_tokens=total_tokens,
            avg_latency_ms=avg_latency,
            composite_score=composite,
            tasks_with_reflection=sum(1 for r in results if r.iterations > 1),
            tasks_with_web_search=sum(1 for r in results if r.used_web_search),
            errors_count=sum(1 for r in results if r.error)
        )
    
    # ============== 检查点管理 ==============
    
    def _load_checkpoint(self):
        """加载检查点"""
        if os.path.exists(self.CHECKPOINT_FILE):
            try:
                with open(self.CHECKPOINT_FILE, 'r') as f:
                    self.checkpoint = json.load(f)
                logger.info(f"Loaded checkpoint with {len(self.checkpoint.get('tasks_completed', []))} tasks completed")
            except Exception as e:
                logger.warning(f"Could not load checkpoint: {e}")
                self.checkpoint = {}
        else:
            self.checkpoint = {}
    
    def _save_checkpoint(self):
        """保存检查点"""
        try:
            with open(self.CHECKPOINT_FILE, 'w') as f:
                json.dump(self.checkpoint, f, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save checkpoint: {e}")
    
    # ============== 结果保存 ==============
    
    def _save_results(self, summary: BenchmarkSummary, results: List[TaskResult]):
        """保存最终结果"""
        output = {
            "harness_version": summary.harness_version,
            "paradigm": summary.paradigm,
            "timestamp": summary.timestamp,
            "elapsed_seconds": summary.elapsed_seconds,
            "summary": summary.to_dict(),
            "individual_results": [r.to_dict() for r in results]
        }
        
        try:
            with open(self.RESULTS_FILE, 'w') as f:
                json.dump(output, f, ensure_ascii=False, indent=2)
            logger.info(f"Results saved to {self.RESULTS_FILE}")
        except Exception as e:
            logger.error(f"Failed to save results: {e}")
    
    # ============== 工具方法 ==============
    
    def call_api(self, prompt: str, system_prompt: str = "", 
                 max_tokens: int = 2048, timeout: int = 120, 
                 max_retries: int = 2) -> Dict:
        """标准 API 调用"""
        import urllib.request
        
        for attempt in range(max_retries + 1):
            start = time.time()
            try:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "anthropic-version": "2023-06-01"
                }
                payload = {
                    "model": self.API_CONFIG["model"],
                    "max_tokens": max_tokens,
                    "system": system_prompt or "You are a helpful AI assistant.",
                    "messages": [{"role": "user", "content": prompt}]
                }
                data = json.dumps(payload).encode('utf-8')
                req = urllib.request.Request(
                    f"{self.API_CONFIG['base_url']}/v1/messages",
                    data=data, headers=headers, method='POST'
                )
                
                with urllib.request.urlopen(req, timeout=timeout) as response:
                    result = json.loads(response.read().decode('utf-8'))
                
                latency = (time.time() - start) * 1000
                content = ""
                for item in result.get("content", []):
                    if item.get("type") == "text":
                        content = item.get("text", "")
                        break
                
                return {
                    "content": content,
                    "latency_ms": latency,
                    "input_tokens": result.get("usage", {}).get("input_tokens", 0),
                    "output_tokens": result.get("usage", {}).get("output_tokens", 0),
                    "error": None
                }
                
            except Exception as e:
                if attempt < max_retries:
                    logger.warning(f"API call failed (attempt {attempt+1}): {e}")
                    time.sleep(2 ** attempt)
                else:
                    return {
                        "content": "", "latency_ms": 0,
                        "input_tokens": 0, "output_tokens": 0,
                        "error": str(e)
                    }
        
        return {"content": "", "latency_ms": 0, "input_tokens": 0, "output_tokens": 0, "error": "Max retries exceeded"}
    
    def parse_evaluator_response(self, response_text: str) -> Dict:
        """标准 evaluator 响应解析"""
        try:
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                return json.loads(response_text[json_start:json_end])
        except:
            pass
        return {"overall_score": 50, "depth": {"level": 3}, "completeness": {"level": 3}, "actionability": {"level": 3}}
    
    # ============== 对比工具 ==============
    
    @staticmethod
    def compare_results(result_files: List[str]) -> str:
        """对比多个结果文件，输出表格"""
        lines = []
        lines.append("=" * 80)
        lines.append("BENCHMARK COMPARISON")
        lines.append("=" * 80)
        
        all_results = []
        for f in result_files:
            if os.path.exists(f):
                try:
                    with open(f, 'r') as fp:
                        d = json.load(fp)
                        summary = d.get("summary", {})
                        all_results.append({
                            "file": os.path.basename(f),
                            "composite": summary.get("composite_score", 0),
                            "core": summary.get("core_avg_score", 0),
                            "gen": summary.get("gen_avg_score", 0),
                            "action": summary.get("avg_actionability_level", 0),
                            "gen_code": summary.get("gen_code_avg_score", 0)
                        })
                except Exception as e:
                    lines.append(f"\nError reading {f}: {e}")
        
        if all_results:
            lines.append(f"\n{'File':<35} {'Composite':>10} {'Core':>8} {'Gen':>8} {'Action':>8} {'GenCode':>8}")
            lines.append("-" * 80)
            for r in sorted(all_results, key=lambda x: -x["composite"]):
                lines.append(f"{r['file']:<35} {r['composite']:>10.2f} {r['core']:>8.2f} {r['gen']:>8.2f} {r['action']:>8.2f} {r['gen_code']:>8.2f}")
        
        return "\n".join(lines)


# ============== 标准任务定义 ==============

STANDARD_TASKS = [
    # Core 任务
    {"id": "core_001", "type": "research", "difficulty": 8,
     "query": "分析 Transformer 架构在长上下文场景下的注意力机制优化方案"},
    {"id": "core_002", "type": "code", "difficulty": 9,
     "query": "实现一个支持动态窗口大小的滑动日志解析器，处理 TB 级日志"},
    {"id": "core_003", "type": "research", "difficulty": 7,
     "query": "对比 RAG 与 Fine-tuning 在垂直领域问答场景下的成本效益"},
    {"id": "core_004", "type": "code", "difficulty": 8,
     "query": "设计一个分布式限流系统，支持多节点协同和精确度控制"},
    {"id": "core_005", "type": "review", "difficulty": 6,
     "query": "评审微服务架构的链路调用复杂度，给出优化建议"},
    {"id": "core_006", "type": "research", "difficulty": 9,
     "query": "分析 LLM 数学推理能力的技术瓶颈与解决方案"},
    {"id": "core_007", "type": "code", "difficulty": 7,
     "query": "实现一个插件化框架，支持热更新和依赖管理"},
    {"id": "core_008", "type": "research", "difficulty": 8,
     "query": "分析向量数据库在实时推荐系统中的选型策略"},
    {"id": "core_009", "type": "code", "difficulty": 9,
     "query": "实现简化版 Raft 共识算法，包含 Leader 选举和日志复制"},
    {"id": "core_010", "type": "review", "difficulty": 7,
     "query": "评审日活 1000 万 App 后端系统的架构设计"},
    # Gen 任务
    {"id": "gen_001", "type": "research", "difficulty": 8,
     "query": "分析量子计算在组合优化问题中的实际应用前景与挑战"},
    {"id": "gen_002", "type": "code", "difficulty": 9,
     "query": "实现一个自适应调度的线程池，支持基于负载的动态扩容和缩容"},
    {"id": "gen_003", "type": "review", "difficulty": 8,
     "query": "评估区块链技术在供应链溯源场景中的适用性和潜在风险"},
    {"id": "gen_004", "type": "research", "difficulty": 9,
     "query": "调研联邦学习在医疗数据隐私保护中的最新进展"},
    {"id": "gen_005", "type": "code", "difficulty": 8,
     "query": "设计一个多模态 RAG 系统，融合文本、图像和表格进行智能问答"},
]


if __name__ == "__main__":
    print("BaseHarness Framework v1.0")
    print(f"\nStandard tasks: {len(STANDARD_TASKS)}")
    print(f"  Core: {sum(1 for t in STANDARD_TASKS if not t['id'].startswith('gen_'))}")
    print(f"  Gen: {sum(1 for t in STANDARD_TASKS if t['id'].startswith('gen_'))}")
    print(f"\nUsage: Create a subclass that implements get_task_definitions() and execute_single_task()")