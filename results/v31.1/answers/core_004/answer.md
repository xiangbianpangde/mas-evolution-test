# core_004 Answer

**Run**: 2
**Iterations**: 1

## Answer

# 分布式限流系统设计方案

## 1. 架构简图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          分布式限流系统架构                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐                                  │
│  │ Gateway │    │ Gateway │    │ Gateway │   ← 接入层（多节点）              │
│  │ Node-1  │    │ Node-2  │    │ Node-3  │                                  │
│  └───┬─────┘    └───┬─────┘    └───┬─────┘                                  │
│      │              │              │                                         │
│      └──────────────┼──────────────┘                                        │
│                     ▼                                                        │
│         ┌───────────────────────┐                                           │
│         │   RateLimiter Client  │   ← SDK/中间件                            │
│         │   (本地缓存 + 预取)    │                                           │
│         └───────────┬───────────┘                                           │
│                     │                                                        │
│      ┌──────────────┼──────────────┐                                        │
│      ▼              ▼              ▼                                        │
│  ┌────────┐    ┌────────┐    ┌────────┐                                     │
│  │ Redis  │    │ Redis  │    │ Redis  │   ← 分布式协调层                    │
│  │Master  │───▶│ Slave  │───▶│ Slave  │     (哨兵/集群模式)                  │
│  └────────┘    └────────┘    └────────┘                                     │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────┐           │
│  │                     管理控制台                                │           │
│  │  • 实时监控 QPS、命中率、延迟                                 │           │
│  │  • 动态调整限流阈值                                          │           │
│  │  • 规则热更新                                                │           │
│  └─────────────────────────────────────────────────────────────┘           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

核心数据流：
┌─────────────────────────────────────────────────────────────────┐
│                                                                  │
│  请求 → 本地限流(快速拒绝) → Redis限流(精确控制) → 允许/拒绝       │
│           ↓                              ↓                       │
│     95%流量本地处理                  5%流量精确限流               │
│                                                                  │
│  本地缓存Key: sliding_window:{key}:{node_id}                     │
│  Redis Key:   rate_limit:{algorithm}:{key}                      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## 2. 核心代码（完整可运行）

```python
#!/usr/bin/env python3
"""
分布式限流系统 - 完整实现
支持：令牌桶、滑动窗口、漏桶 三种算法
特性：多节点协同、本地缓存、精确控制、高可用
"""

import time
import threading
import hashlib
import json
import uuid
from typing import Dict, Optional, Tuple, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict
import logging
from abc import ABC, abstractmethod
import statistics
import functools

# ============================================================================
# 依赖库安装提示（无外部依赖，纯标准库实现）
# ============================================================================
# pip install redis  # 如需Redis支持请安装
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# 配置管理
# ============================================================================

@dataclass
class RateLimitConfig:
    """限流配置"""
    algorithm: str = "sliding_window"  # token_bucket | sliding_window | leaky_bucket
    capacity: int = 100                 # 桶容量/窗口大小
    rate: float = 10.0                  # 速率（个/秒）
    refill_time: float = 1.0            # 补充时间（秒）
    enable_local_cache: bool = True     # 启用本地缓存
    local_cache_ttl: float = 0.1        # 本地缓存TTL（秒）
    sync_interval: float = 0.5         # 同步间隔（秒）
    cluster_mode: bool = False         # 集群模式
    nodes: list = field(default_factory=list)  # 集群节点列表
    
    def to_dict(self) -> Dict:
        return {
            "algorithm": self.algorithm,
            "capacity": self.capacity,
            "rate": self.rate,
            "refill_time": self.refill_time,
            "enable_local_cache": self.enable_local_cache,
            "local_cache_ttl": self.local_cache_ttl,
            "sync_interval": self.sync_interval,
            "cluster_mode": self.cluster_mode,
            "nodes": self.nodes
        }


class ConfigManager:
    """配置管理器 - 支持热更新"""
    
    def __init__(self):
        self._configs: Dict[str, RateLimitConfig] = {}
        self._lock = threading.RLock()
        self._watchers: list = []
        
    def register(self, key: str, config: RateLimitConfig):
        with self._lock:
            self._configs[key] = config
            logger.info(f"Registered rate limit config for key '{key}': {config}")
            
    def get(self, key: str) -> Optional[RateLimitConfig]:
        with self._lock:
            return self._configs.get(key)
            
    def update(self, key: str, config: RateLimitConfig):
        with self._lock:
            old_config = self._configs.get(key)
            self._configs[key] = config
            self._notify_watchers(key, old_config, config)
            logger.info(f"Updated rate limit config for key '{key}'")
            
    def watch(self, callback: Callable):
        self._watchers.append(callback)
        
    def _notify_watchers(self, key: str, old: RateLimitConfig, new: RateLimitConfig):
        for cb in self._watchers:
            try:
                cb(key, old, new)
            except Exception as e:
                logger.error(f"Config watcher error: {e}")


# ============================================================================
# 本地缓存 - 多级缓存架构
# ============================================================================

@dataclass
class LocalCacheEntry:
    """本地缓存条目"""
    tokens: float
    last_update: float
    ttl: float
    
    def is_expired(self, now: float) -> bool:
        return now - self.last_update > self.ttl


class LocalCache:
    """本地缓存 - 减少Redis访问"""
    
    def __init__(self, ttl: float = 0.1):
        self._cache: Dict[str, LocalCacheEntry] = {}
        self._lock = threading.Lock()
        self._ttl = ttl
        self._hits = 0
        self._misses = 0
        
    def get(self, key: str) -> Optional[float]:
        now = time.time()
        with self._lock:
            entry = self._cache.get(key)
            if entry and not entry.is_expired(now):
                self._hits += 1
                return entry.tokens
            self._misses += 1
            return None
            
    def set(self, key: str, tokens: float):
        now = time.time()
        with self._lock:
            self._cache[key] = LocalCacheEntry(
                tokens=tokens,
                last_update=now,
                ttl=self._ttl
            )
            
    def clear(self):
        with self._lock:
            self._cache.clear()
            
    def get_stats(self) -> Dict:
        total = self._hits + self._misses
        return {
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": self._hits / total if total > 0 else 0,
            "size": len(self._cache)
        }


# ============================================================================
# 限流算法接口
# ============================================================================

class AlgorithmType(Enum):
    TOKEN_BUCKET = "token_bucket"
    SLIDING_WINDOW = "sliding_window"
    LEAKY_BUCKET = "leaky_bucket"


class RateLimitAlgorithm(ABC):
    """限流算法基类"""
    
    @abstractmethod
    def allow_request(self, key: str, tokens: float = 1.0) -> Tuple[bool, Dict]:
        """检查是否允许请求"""
        pass
        
    @abstractmethod
    def reset(self, key: str):
        """重置限流器"""
        pass
        
    @abstractmethod
    def get_status(self, key: str) -> Dict:
        """获取当前状态"""
        pass


# ============================================================================
# 令牌桶算法
# ============================================================================

class TokenBucket(RateLimitAlgorithm):
    """
    令牌桶算法实现
    
    原理：
    - 桶容量：C（最大存储令牌数）
    - 速率：r（每秒生成令牌数）
    - 请求消耗：n个令牌
    - 允许条件：桶中令牌数 >= n
    
    优点：允许突发流量
    缺点：精度受时间影响
    """
    
    def __init__(self, capacity: int, rate: float, refill_time: float = 1.0):
        self._capacity = capacity
        self._rate = rate
        self._refill_time = refill_time
        self._buckets: Dict[str, Dict] = {}
        self._lock = threading.Lock()
        
    def _get_or_create_bucket(self, key: str) -> Dict:
        with self._lock:
            now = time.time()
            if key not in self._buckets:
                self._buckets[key] = {
                    "tokens": self._capacity,
                    "last_refill": now
                }
            else:
                # 补充令牌
                bucket = self._buckets[key]
                elapsed = now - bucket["last_refill"]
                refill_tokens = elapsed * (self._rate / self._refill_time)
                bucket["tokens"] = min(self._capacity, bucket["tokens"] + refill_tokens)
                bucket["last_refill"] = now
            return self._buckets[key]
            
    def allow_request(self, key: str, tokens: float = 1.0) -> Tuple[bool, Dict]:
        bucket = self._get_or_create_bucket(key)
        
        allowed = bucket["tokens"] >= tokens
        remaining = max(0, bucket["tokens"] - tokens) if allowed else bucket["tokens"]
        
        if allowed:
            bucket["tokens"] = remaining
            
        return allowed, {
            "algorithm": "token_bucket",
            "capacity": self._capacity,
            "remaining": int(remaining),
            "retry_after": 0 if allowed else (tokens - bucket["tokens"]) / self._rate
        }
        
    def reset(self, key: str):
        with self._lock:
            if key in self._buckets:
                del self._buckets[key]
                
    def get_status(self, key: str) -> Dict:
        bucket = self._get_or_create_bucket(key)
        return {
            "key": key,
            "algorithm": "token_bucket",
            "capacity": self._capacity,
            "current_tokens": int(bucket["tokens"]),
            "rate": self._rate
        }


# ============================================================================
# 滑动窗口算法
# ============================================================================

class SlidingWindow(RateLimitAlgorithm):
    """
    滑动窗口算法实现
    
    原理：
    - 窗口大小：W（秒）
    - 最大请求数：N
    - 时间戳列表：记录每次请求时间
    - 允许条件：窗口内请求数 < N
    
    优点：精度高，公平性好
    缺点：内存占用较高
    """
    
    def __init__(self, capacity: int, rate: float, window_size: float = 60.0):
        self._capacity = capacity
        self._rate = rate
        self._window_size = window_size
        self._requests: Dict[str, list] = {}
        self._lock = threading.Lock()
        
    def _cleanup_window(self, key: str, now: float):
        """清理过期的请求记录"""
        if key in self._requests:
            cutoff = now - self._window_size
            self._requests[key] = [
                ts for ts in self._requests[key] if ts > cutoff
            ]
            
    def allow_request(self, key: str, tokens: float = 1.0) -> Tuple[bool, Dict]:
        now = time.time()
        n = int(tokens)
        
        with self._lock:
            if key not in self._requests:
                self._requests[key] = []
                
            self._cleanup_window(key, now)
            
            count = len(self._requests[key])
            allowed = count + n <= self._capacity
            
            if allowed:
                for _ in range(n):
                    self._requests[key].append(now)
                    
        retry_after = 0
        if not allowed:
            # 计算需要等待多久
            oldest = min(self._requests.get(key, [now]))
            retry_after = max(0, (oldest + self._window_size) - now)
            
        return allowed, {
            "algorithm": "sliding_window",
            "window_size": self._window_size,
            "remaining": max(0, self._capacity - count - n),
            "reset": now + self._window_size,
            "retry_after": retry_after
        }
        
    def reset(self, key: str):
        with self._lock:
            if key in self._requests:
                del self._requests[key]
                
    def get_status(self, key: str) -> Dict:
        now = time.time()
        with self._lock:
            self._cleanup_window(key, now)
            count = len(self._requests.get(key, []))
            return {
                "key": key,
                "algorithm": "sliding_window",
                "window_size": self._window_size,
                "current_count": count,
                "max_count": self._capacity,
                "remaining": self._capacity - count
            }


# ============================================================================
# 漏桶算法
# ============================================================================

class LeakyBucket(RateLimitAlgorithm):
    """
    漏桶算法实现
    
    原理：
    - 桶容量：C
    - 漏出速率：r（个/秒）
    - 当前水量：w
    - 请求到达时：w += n
    - 允许条件：w <= C 且 漏出后 w >= 0
    
    优点：流量平滑
    缺点：不支持突发流量
    """
    
    def __init__(self, capacity: int, rate: float):
        self._capacity = capacity
        self._rate = rate
        self._buckets: Dict[str, Dict] = {}
        self._lock = threading.Lock()
        
    def _get_or_create_bucket(self, key: str) -> Dict:
        with self._lock:
            now = time.time()
            if key not in self._buckets:
                self._buckets[key] = {
                    "water": 0.0,
                    "last_leak": now
                }
            else:
                bucket = self._buckets[key]
                # 计算漏出的水量
                elapsed = now - bucket["last_leak"]
                leaked = elapsed * self._rate
                bucket["water"] = max(0, bucket["water"] - leaked)
                bucket["last_leak"] = now
            return self._buckets[key]
            
    def allow_request(self, key: str, tokens: float = 1.0) -> Tuple[bool, Dict]:
        bucket = self._get_or_create_bucket(key)
        
        # 检查桶能否容纳
        if bucket["water"] + tokens > self._capacity:
            return False, {
                "algorithm": "leaky_bucket",
                "capacity": self._capacity,
                "current_water": bucket["water"],
                "retry_after": (bucket["water"] + tokens - self._capacity) / self._rate
            }
            
        bucket["water"] += tokens
        
        return True, {
            "algorithm": "leaky_bucket",
            "capacity": self._capacity,
            "current_water": bucket["water"],
            "remaining": self._capacity - bucket["water"]
        }
        
    def reset(self, key: str):
        with self._lock:
            if key in self._buckets:
                del self._buckets[key]
                
    def get_status(self, key: str) -> Dict:
        bucket = self._get_or_create_bucket(key)
        return {
            "key": key,
            "algorithm": "leaky_bucket",
            "capacity": self._capacity,
            "current_water": bucket["water"],
            "rate": self._rate
        }


# ============================================================================
# Redis 分布式协调层
# ============================================================================

class RedisCoordinator:
    """
    Redis协调器 - 保证分布式环境下的原子性
    
    使用Lua脚本保证原子性操作
    """
    
    # Lua脚本：令牌桶
    TOKEN_BUCKET_SCRIPT = """
    local key = KEYS[1]
    local capacity = tonumber(ARGV[1])
    local rate = tonumber(ARGV[2])
    local now = tonumber(ARGV[3])
    local tokens_requested = tonumber(ARGV[4])
    
    local bucket = redis.call('HMGET', key, 'tokens', 'last_refill')
    local current_tokens = tonumber(bucket[1]) or capacity
    local last_refill = tonumber(bucket[2]) or now
    
    -- 补充令牌
    local elapsed = now - last_refill
    local refill_tokens = elapsed * rate
    current_tokens = math.min(capacity, current_tokens + refill_tokens)
    
    -- 检查是否允许
    if current_tokens >= tokens_requested then
        current_tokens = current_tokens - tokens_requested
        redis.call('HMSET', key, 'tokens', current_tokens, 'last_refill', now)
        redis.call('EXPIRE', key, 60)
        return {1, current_tokens}
    else
        redis.call('HMSET', key, 'tokens', current_tokens, 'last_refill', now)
        redis.call('EXPIRE', key, 60)
        return {0, current_tokens}
    end
    """
    
    # Lua脚本：滑动窗口日志
    SLIDING_WINDOW_SCRIPT = """
    local key = KEYS[1]
    local window = tonumber(ARGV[1])
    local limit = tonumber(ARGV[2])
    local now = tonumber(ARGV[3])
    local tokens_requested = tonumber(ARGV[4])
    
    -- 删除过期记录
    local cutoff = now - window
    redis.call('ZREMRANGEBYSCORE', key, '-inf', cutoff)
    
    -- 统计当前窗口内请求数
    local current = redis.call('ZCARD', key)
    
    if current + tokens_requested <= limit then
        -- 添加新请求
        for i = 1, tokens_requested do
            redis.call('ZADD', key, now, now .. '-' .. math.random(1000000))
        end
        redis.call('EXPIRE', key, window + 1)
        return {1, limit - current - tokens_requested}
    else
        return {0, limit - current}
    end
    """
    
    # Lua脚本：漏桶
    LEAKY_BUCKET_SCRIPT = """
    local key = KEYS[1]
    local capacity = tonumber(ARGV[1])
    local rate = tonumber(ARGV[2])
    local now = tonumber(ARGV[3])
    local tokens_requested = tonumber(ARGV[4])
    
    local bucket = redis.call('HMGET', key, 'water', 'last_leak')
    local water = tonumber(bucket[1]) or 0
    local last_leak = tonumber(bucket[2]) or now
    
    -- 漏出
    local elapsed = now - last_leak
    local leaked = elapsed * rate
    water = math.max(0, water - leaked)
    
    -- 检查容量
    if water + tokens_requested <= capacity then
        water = water + tokens_requested
        redis.call('HMSET', key, 'water', water, 'last_leak', now)
        redis.call('EXPIRE', key, 60)
        return {1, capacity - water}
    else
        redis.call('HMSET', key, 'water', water, 'last_leak', now)
        redis.call('EXPIRE', key, 60)
        return {0, capacity - water}
    end
    """
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        if not REDIS_AVAILABLE:
            raise ImportError("Redis library not available. Install with: pip install redis")
        
        self._pool = redis.ConnectionPool.from_url(redis_url)
        self._client = redis.Redis(connection_pool=self._pool)
        self._scripts = {}
        self._load_scripts()
        
    def _load_scripts(self):
        """加载Lua脚本"""
        self._scripts['token_bucket'] = self._client.register_script(self.TOKEN_BUCKET_SCRIPT)
        self._scripts['sliding_window'] = self._client.register_script(self.SLIDING_WINDOW_SCRIPT)
        self._scripts['leaky_bucket'] = self._client.register_script(self.LEAKY_BUCKET_SCRIPT)
        
    def token_bucket(self, key: str, capacity: int, rate: float, tokens: float = 1.0) -> Tuple[bool, Dict]:
        """Redis令牌桶"""
        result = self._scripts['token_bucket'](
            keys=[f"rl:token_bucket:{key}"],
            args=[capacity, rate, time.time(), tokens]
        )
        return bool(result[0]), {"remaining": result[1]}
        
    def sliding_window(self, key: str, window: float, limit: int, tokens: int = 1) -> Tuple[bool, Dict]:
        """Redis滑动窗口"""
        result = self._scripts['sliding_window'](
            keys=[f"rl:sliding_window:{key}"],
            args=[window, limit, time.time(), tokens]
        )
        return bool(result[0]), {"remaining": result[1]}
        
    def leaky_bucket(self, key
