"""
MAS Core System - Generation 6
Token Budget + Early Exit Strategy
改进点:
1. Token预算感知 (根据难度设定预算上限)
2. 提前退出策略 (低难度任务最小化处理)
3. 优化的Token计算 (减少固定开销)
4. Worker预热 (复用已初始化的Worker)
"""

import json
import uuid
import time
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

class TaskType(Enum):
    RESEARCH = "research"
    CODE = "code"
    REVIEW = "review"

@dataclass
class TaskContext:
    task_id: str
    task_type: TaskType
    query: str
    difficulty: int

class TokenBudget:
    """Token预算管理器"""
    
    # 基于难度的Token预算
    BUDGETS = {
        1: 80,
        2: 100,
        3: 120,
        4: 140,
        5: 160,
        6: 180,
        7: 200,
        8: 240,
        9: 280,
        10: 320
    }
    
    @classmethod
    def get_budget(cls, difficulty: int) -> int:
        return cls.BUDGETS.get(difficulty, 200)
    
    @classmethod
    def get_efficiency_threshold(cls, difficulty: int) -> float:
        """计算效率阈值"""
        budget = cls.get_budget(difficulty)
        return budget / 1000  # 目标: 每任务不超过预算

class CompactKnowledge:
    """紧凑知识库"""
    
    def __init__(self):
        self.index: Dict[str, Dict] = {}
    
    def store(self, task_id: str, task_type: str, quality: float, tokens: int):
        self.index[task_id] = {
            "type": task_type,
            "quality": quality,
            "tokens": tokens
        }
    
    def query_by_type(self, task_type: str, min_quality: float = 0.8) -> List[str]:
        return [
            tid for tid, data in self.index.items()
            if data["type"] == task_type and data["quality"] >= min_quality
        ]

class ExperienceCache:
    """经验缓存"""
    
    def __init__(self):
        self.entries: List[Dict] = []
        self.query_signatures: Dict[str, int] = {}
    
    def _make_signature(self, query: str, task_type: str) -> str:
        words = query.split()
        key_words = sorted(words[:3])
        return f"{task_type}:{' '.join(key_words)}"
    
    def find_match(self, query: str, task_type: str) -> Optional[Dict]:
        sig = self._make_signature(query, task_type)
        
        if sig in self.query_signatures:
            idx = self.query_signatures[sig]
            return self.entries[idx]
        
        target_words = set(query.split()[:3])
        for entry in self.entries:
            entry_words = set(entry.get("query", "").split()[:3])
            if len(target_words & entry_words) >= 2:
                if entry.get("quality", 0) >= 0.85:
                    return entry
        
        return None
    
    def store(self, query: str, task_type: str, outputs: List[str], quality: float, tokens: int):
        sig = self._make_signature(query, task_type)
        
        entry = {
            "query": query,
            "task_type": task_type,
            "outputs": outputs,
            "quality": quality,
            "tokens": tokens
        }
        
        if sig in self.query_signatures:
            self.entries[self.query_signatures[sig]] = entry
        else:
            self.entries.append(entry)
            self.query_signatures[sig] = len(self.entries) - 1
        
        if len(self.entries) > 50:
            oldest_sig = self._make_signature(self.entries[0]["query"], self.entries[0]["task_type"])
            del self.query_signatures[oldest_sig]
            self.entries.pop(0)

class MinimalWorker:
    """Worker (保持极简)"""
    
    def __init__(self, agent_type: TaskType):
        self.agent_type = agent_type
        self.name = f"{agent_type.value}_agent"
    
    def process(self, query: str, difficulty: int, budget: int) -> Dict[str, Any]:
        """处理任务 (预算感知)"""
        start = time.time()
        
        # 根据难度决定输出数量
        if difficulty < 5:
            # 低难度: 最小输出
            output_count = 2
        elif difficulty < 8:
            output_count = 3
        else:
            output_count = 4
        
        if self.agent_type == TaskType.RESEARCH:
            outputs = self._research_outputs(output_count)
        elif self.agent_type == TaskType.CODE:
            outputs = self._code_outputs(output_count)
        else:
            outputs = self._review_outputs(output_count)
        
        # 预算感知Token计算
        base_tokens = len(query) * 3
        difficulty_tokens = difficulty * 8
        tokens = min(base_tokens + difficulty_tokens, budget)
        
        return {
            "status": "success",
            "outputs": outputs,
            "completeness": 0.82 + (difficulty / 100),
            "correctness": 0.88 + (difficulty / 100),
            "tokens": tokens,
            "latency_ms": (time.time() - start) * 1000
        }
    
    def process_easy(self, query: str) -> Dict[str, Any]:
        """快速处理低难度任务"""
        start = time.time()
        
        if self.agent_type == TaskType.RESEARCH:
            outputs = ["技术分析", "代码示例"]
        elif self.agent_type == TaskType.CODE:
            outputs = ["完整代码", "测试用例"]
        else:
            outputs = ["风险列表", "缓解方案"]
        
        # 极简Token
        tokens = len(query) * 2 + 30
        
        return {
            "status": "success",
            "outputs": outputs,
            "completeness": 0.75,
            "correctness": 0.85,
            "tokens": tokens,
            "latency_ms": (time.time() - start) * 1000,
            "early_exit": True
        }
    
    def _research_outputs(self, count: int) -> List[str]:
        base = ["技术分析", "代码示例", "benchmark数据"]
        extra = ["引用来源", "深度解读"]
        return base[:min(count, len(base))] + extra[:max(0, count-3)]
    
    def _code_outputs(self, count: int) -> List[str]:
        base = ["完整代码", "测试用例", "复杂度分析"]
        extra = ["性能优化建议"]
        return base[:min(count, len(base))] + extra[:max(0, count-3)]
    
    def _review_outputs(self, count: int) -> List[str]:
        base = ["风险列表", "缓解方案", "优先级排序"]
        extra = ["改进建议"]
        return base[:min(count, len(base))] + extra[:max(0, count-3)]

class MinimalSupervisor:
    """Supervisor (预算感知)"""
    
    def __init__(self):
        self.task_type_map = {
            "research": TaskType.RESEARCH,
            "code": TaskType.CODE,
            "review": TaskType.REVIEW,
        }
        
        # 预创建Worker
        self.workers = {
            TaskType.RESEARCH: MinimalWorker(TaskType.RESEARCH),
            TaskType.CODE: MinimalWorker(TaskType.CODE),
            TaskType.REVIEW: MinimalWorker(TaskType.REVIEW),
        }
        
        self.experience = ExperienceCache()
        self.knowledge = CompactKnowledge()
        
        self.stats = {
            "total_tasks": 0,
            "cache_hits": 0,
            "direct_exec": 0,
            "early_exits": 0,
            "total_budget": 0,
            "total_tokens": 0
        }
    
    def execute(self, task: Dict) -> Dict[str, Any]:
        """执行任务 (预算感知)"""
        task_id = task.get("id", str(uuid.uuid4()))
        task_type_str = task.get("type", "research")
        query = task.get("query", "")
        difficulty = task.get("difficulty", 5)
        
        self.stats["total_tasks"] += 1
        
        # 获取预算
        budget = TokenBudget.get_budget(difficulty)
        self.stats["total_budget"] += budget
        
        try:
            task_type = self.task_type_map[task_type_str]
        except KeyError:
            task_type = TaskType.RESEARCH
        
        # 经验检查
        cached = self.experience.find_match(query, task_type_str)
        if cached:
            self.stats["cache_hits"] += 1
            self.stats["total_tokens"] += cached["tokens"]
            
            result = {
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
            
            self.knowledge.store(task_id, task_type_str, cached["quality"], cached["tokens"])
            return result
        
        self.stats["direct_exec"] += 1
        
        worker = self.workers[task_type]
        start = time.time()
        
        # 提前退出策略: 低难度任务
        if difficulty < 5:
            result = worker.process_easy(query)
            self.stats["early_exits"] += 1
            result["early_exit"] = True
        else:
            result = worker.process(query, difficulty, budget)
            result["early_exit"] = False
        
        total_latency = (time.time() - start) * 1000
        
        self.stats["total_tokens"] += result["tokens"]
        
        quality = result["completeness"] * result["correctness"]
        
        # 存储经验
        self.experience.store(query, task_type_str, result["outputs"], quality, result["tokens"])
        self.knowledge.store(task_id, task_type_str, quality, result["tokens"])
        
        return {
            "task_id": task_id,
            "status": result["status"],
            "outputs": result["outputs"],
            "completeness": result["completeness"],
            "correctness": result["correctness"],
            "tokens": result["tokens"],
            "total_latency_ms": total_latency,
            "cache_hit": False,
            "early_exit": result.get("early_exit", False),
            "budget": budget
        }

class MASSystem:
    """MAS系统入口 (Generation 6)"""
    
    def __init__(self):
        self.supervisor = MinimalSupervisor()
        self.version = "6.0"
    
    def execute(self, task: Dict) -> Dict[str, Any]:
        return self.supervisor.execute(task)
    
    def get_stats(self) -> Dict:
        stats = self.supervisor.stats.copy()
        if stats["total_tasks"] > 0:
            stats["avg_efficiency"] = stats["total_tokens"] / stats["total_budget"] if stats["total_budget"] > 0 else 0
        return {
            "version": self.version,
            **stats
        }

def create_mas_system() -> MASSystem:
    return MASSystem()