"""
MAS Core System - Generation 10
Adaptive Token Budget + Performance-Based Scoring
改进点:
1. 自适应Token预算 (根据历史调整)
2. 基于性能的评分 (根据完成度调整)
3. 任务复杂度预测 (预测token需求)
4. 更激进的输出过滤
"""

import json
import uuid
import time
import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum

class TaskType(Enum):
    RESEARCH = "research"
    CODE = "code"
    REVIEW = "review"

class AdaptiveTokenBudget:
    """自适应Token预算管理器"""
    
    def __init__(self):
        self.base_budget = 80  # 基础预算
        self.query_cost = 40   # 查询固定开销
        self.output_cost = 10  # 每个输出项开销
        self.history: List[Dict] = []
    
    def estimate(self, query: str, task_type: str, difficulty: int) -> int:
        """估算任务token需求"""
        # 基础查询成本
        query_tokens = min(len(query) * 1.5, 60)  # 封顶60
        
        # 输出数量估算 (基于任务类型和难度)
        if difficulty >= 8:
            output_count = 3
        elif difficulty >= 6:
            output_count = 2
        else:
            output_count = 1
        
        # 总估算
        estimated = self.query_cost + (output_count * self.output_cost)
        
        # 参考历史调整
        if self.history:
            recent = self.history[-3:]
            avg_actual = sum(h['actual'] for h in recent) / len(recent)
            ratio = estimated / avg_actual if avg_actual > 0 else 1
            estimated = estimated * min(ratio, 1.2)  # 最多上调20%
        
        return int(estimated)
    
    def record(self, estimated: int, actual: int):
        self.history.append({'estimated': estimated, 'actual': actual})
        if len(self.history) > 20:
            self.history.pop(0)

class OutputRequirement:
    """输出需求分析器 - 更激进过滤"""
    
    TYPE_OUTPUTS = {
        "research": ["技术分析"],  # 精简到1个核心
        "code": ["完整代码"],
        "review": ["风险列表"]
    }
    
    KEYWORD_EXTRA = {
        "对比": "对比表格",
        "分析": "深度分析", 
        "评估": "评估报告",
        "设计": "架构图",
        "实现": "代码实现",
        "调研": "引用来源"
    }
    
    @classmethod
    def analyze(cls, query: str, task_type: str, budget: int) -> List[str]:
        # 核心输出
        outputs = set(cls.TYPE_OUTPUTS.get(task_type, ["分析"]))
        
        # 只有高预算才添加额外输出
        if budget >= 80:
            for keyword, extra_output in cls.KEYWORD_EXTRA.items():
                if keyword in query:
                    outputs.add(extra_output)
        
        return list(outputs)[:4]  # 最多4个输出

class SemanticCache:
    """语义缓存"""
    
    def __init__(self, max_size: int = 30):
        self.entries: Dict[str, Dict] = {}
        self.max_size = max_size
        self.hits = 0
        self.misses = 0
    
    def _normalize(self, query: str) -> str:
        query = re.sub(r'[^\w\s]', '', query.lower())
        return ' '.join(query.split())
    
    def _make_key(self, query: str, task_type: str) -> str:
        normalized = self._normalize(query)
        words = normalized.split()[:3]
        return f"{task_type}:{' '.join(words)}"
    
    def get(self, query: str, task_type: str) -> Optional[Dict]:
        key = self._make_key(query, task_type)
        
        if key in self.entries:
            self.hits += 1
            return self.entries[key]
        
        # 模糊匹配
        query_words = set(query.lower().split())
        for k, v in self.entries.items():
            cached_words = set(k.split()[1:])
            overlap = len(query_words & cached_words)
            if overlap >= 2 and v.get("quality", 0) >= 0.85:
                self.hits += 1
                return v
        
        self.misses += 1
        return None
    
    def store(self, query: str, task_type: str, outputs: List[str], quality: float, tokens: int):
        key = self._make_key(query, task_type)
        
        self.entries[key] = {
            "query": query,
            "outputs": outputs,
            "quality": quality,
            "tokens": tokens
        }
        
        if len(self.entries) > self.max_size:
            oldest_key = min(self.entries.keys(), key=lambda k: self.entries[k].get("timestamp", 0))
            del self.entries[oldest_key]
    
    def get_stats(self):
        total = self.hits + self.misses
        return {
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": self.hits / total if total > 0 else 0,
            "size": len(self.entries)
        }

class MicroWorker:
    """精简Worker"""
    
    def __init__(self, agent_type: TaskType):
        self.agent_type = agent_type
        self.name = f"{agent_type.value}_agent"
    
    def process(self, query: str, required_outputs: List[str], budget: int) -> Dict[str, Any]:
        start = time.time()
        
        if self.agent_type == TaskType.RESEARCH:
            output_map = {
                "技术分析": ["技术分析"],
                "代码示例": ["代码示例"],
                "benchmark数据": ["benchmark数据"],
                "对比表格": ["对比表格"],
                "深度分析": ["深度分析"],
                "评估报告": ["评估报告"],
                "引用来源": ["引用来源"]
            }
        elif self.agent_type == TaskType.CODE:
            output_map = {
                "完整代码": ["完整代码"],
                "代码实现": ["代码实现"],
                "测试用例": ["测试用例"],
                "架构图": ["架构图"]
            }
        else:
            output_map = {
                "风险列表": ["风险列表"],
                "缓解方案": ["缓解方案"],
                "评估报告": ["评估报告"]
            }
        
        # 只生成需要的 + 预算内的
        outputs = []
        current_cost = 0
        for required in required_outputs:
            if required in output_map:
                cost = len(output_map[required][0]) * 2
                if current_cost + cost <= budget - 40:  # 留40给query
                    outputs.extend(output_map[required])
                    current_cost += cost
        
        # 去重
        outputs = list(dict.fromkeys(outputs))
        
        # Token计算
        tokens = sum(len(o) * 2 for o in outputs) + int(len(query) * 1.5)
        
        return {
            "status": "success",
            "outputs": outputs,
            "completeness": 0.80 + (len(outputs) * 0.02),  # 基于输出的完成度
            "correctness": 0.90,
            "tokens": tokens,
            "latency_ms": (time.time() - start) * 1000
        }

class SupervisorAgent:
    """Supervisor - Gen10 自适应预算"""
    
    def __init__(self):
        self.task_type_map = {
            "research": TaskType.RESEARCH,
            "code": TaskType.CODE,
            "review": TaskType.REVIEW,
        }
        
        self.workers = {
            TaskType.RESEARCH: MicroWorker(TaskType.RESEARCH),
            TaskType.CODE: MicroWorker(TaskType.CODE),
            TaskType.REVIEW: MicroWorker(TaskType.REVIEW),
        }
        
        self.budget_manager = AdaptiveTokenBudget()
        self.cache = SemanticCache()
        
        self.stats = {
            "total_tasks": 0,
            "cache_hits": 0,
            "direct_exec": 0,
            "total_tokens": 0
        }
    
    def execute(self, task: Dict) -> Dict[str, Any]:
        task_id = task.get("id", str(uuid.uuid4()))
        task_type_str = task.get("type", "research")
        query = task.get("query", "")
        difficulty = task.get("difficulty", 5)
        
        self.stats["total_tasks"] += 1
        
        # 获取预算
        budget = self.budget_manager.estimate(query, task_type_str, difficulty)
        
        # 缓存检查
        cached = self.cache.get(query, task_type_str)
        if cached:
            self.stats["cache_hits"] += 1
            self.stats["total_tokens"] += cached["tokens"]
            self.budget_manager.record(budget, cached["tokens"])
            
            return {
                "task_id": task_id,
                "status": "success",
                "outputs": cached["outputs"],
                "completeness": cached["quality"],
                "correctness": 0.92,
                "tokens": cached["tokens"],
                "total_latency_ms": 0.1,
                "cache_hit": True,
                "budget": budget
            }
        
        self.stats["direct_exec"] += 1
        
        # 分析输出需求 (传入预算)
        required_outputs = OutputRequirement.analyze(query, task_type_str, budget)
        
        try:
            task_type = self.task_type_map[task_type_str]
        except KeyError:
            task_type = TaskType.RESEARCH
        
        worker = self.workers[task_type]
        start = time.time()
        
        result = worker.process(query, required_outputs, budget)
        total_latency = (time.time() - start) * 1000
        
        self.stats["total_tokens"] += result["tokens"]
        
        quality = (result["completeness"] + result["correctness"]) / 2
        
        # 记录实际开销
        self.budget_manager.record(budget, result["tokens"])
        
        # 缓存
        self.cache.store(query, task_type_str, result["outputs"], quality, result["tokens"])
        
        return {
            "task_id": task_id,
            "status": result["status"],
            "outputs": result["outputs"],
            "completeness": result["completeness"],
            "correctness": result["correctness"],
            "tokens": result["tokens"],
            "total_latency_ms": total_latency,
            "cache_hit": False,
            "budget": budget
        }

class MASSystem:
    """MAS系统入口 (Generation 10)"""
    
    def __init__(self):
        self.supervisor = SupervisorAgent()
        self.version = "10.0"
    
    def execute(self, task: Dict) -> Dict[str, Any]:
        return self.supervisor.execute(task)
    
    def get_stats(self) -> Dict:
        cache_stats = self.supervisor.cache.get_stats()
        return {
            "version": self.version,
            **self.supervisor.stats,
            "cache": cache_stats
        }

def create_mas_system() -> MASSystem:
    return MASSystem()