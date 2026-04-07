"""
MAS Core System - Generation 1
Tree-based Supervisor-Worker Architecture
"""

import json
import uuid
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum

class TaskType(Enum):
    RESEARCH = "research"
    CODE = "code"
    REVIEW = "review"

@dataclass
class AgentMessage:
    task_id: str
    task_type: TaskType
    payload: Dict[str, Any]
    context: List[Dict]
    
    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False)
    
    @classmethod
    def from_json(cls, data: str) -> 'AgentMessage':
        d = json.loads(data)
        d['task_type'] = TaskType(d['task_type'])
        return cls(**d)

class KnowledgeBase:
    """共享知识库 - 向量存储简化版"""
    
    def __init__(self):
        self.store: Dict[str, List[str]] = {}
        self.vector_index: Dict[str, List[float]] = {}
    
    def add(self, key: str, value: str, embedding: Optional[List[float]] = None):
        if key not in self.store:
            self.store[key] = []
        self.store[key].append(value)
        if embedding:
            self.vector_index[key] = embedding
    
    def query(self, key: str) -> List[str]:
        return self.store.get(key, [])
    
    def search(self, query: str) -> List[str]:
        # 简化版 - 关键词匹配
        results = []
        for values in self.store.values():
            for v in values:
                if any(kw in v for kw in query.split()[:3]):
                    results.append(v)
        return results[:5]

class ContextBuffer:
    """短期记忆 - 上下文缓冲"""
    
    def __init__(self, max_size: int = 100):
        self.max_size = max_size
        self.buffer: List[Dict] = []
    
    def add(self, entry: Dict):
        self.buffer.append(entry)
        if len(self.buffer) > self.max_size:
            self.buffer.pop(0)
    
    def get_recent(self, n: int = 10) -> List[Dict]:
        return self.buffer[-n:]
    
    def clear(self):
        self.buffer = []

class WorkerAgent:
    """Worker Agent - 专业任务处理器"""
    
    def __init__(self, agent_type: TaskType, model_name: str = "minimax/MiniMax-M2"):
        self.agent_type = agent_type
        self.model_name = model_name
        self.name = f"{agent_type.value}_agent"
    
    def process(self, message: AgentMessage) -> Dict[str, Any]:
        """处理任务 - 模拟实现"""
        start = time.time()
        
        # 模拟不同类型任务处理
        if self.agent_type == TaskType.RESEARCH:
            outputs = self._research_handler(message)
        elif self.agent_type == TaskType.CODE:
            outputs = self._code_handler(message)
        else:
            outputs = self._review_handler(message)
        
        latency = (time.time() - start) * 1000
        
        return {
            "status": "success",
            "outputs": outputs,
            "completeness": 0.85,
            "correctness": 0.90,
            "tokens": len(message.payload.get("query", "")) * 10,
            "latency_ms": latency
        }
    
    def _research_handler(self, message: AgentMessage) -> List[str]:
        return ["技术分析", "代码示例", "benchmark数据"]
    
    def _code_handler(self, message: AgentMessage) -> List[str]:
        return ["完整代码", "测试用例", "复杂度分析"]
    
    def _review_handler(self, message: AgentMessage) -> List[str]:
        return ["风险列表", "缓解方案", "优先级排序"]

class SupervisorAgent:
    """Supervisor Agent - 任务编排器"""
    
    def __init__(self, model_name: str = "minimax/MiniMax-M2"):
        self.model_name = model_name
        self.workers: Dict[TaskType, WorkerAgent] = {
            TaskType.RESEARCH: WorkerAgent(TaskType.RESEARCH),
            TaskType.CODE: WorkerAgent(TaskType.CODE),
            TaskType.REVIEW: WorkerAgent(TaskType.REVIEW),
        }
        self.knowledge_base = KnowledgeBase()
        self.context_buffer = ContextBuffer()
    
    def execute(self, task: Dict) -> Dict[str, Any]:
        """执行任务"""
        task_id = task.get("id", str(uuid.uuid4()))
        task_type_str = task.get("type", "research")
        
        # 路由到对应Worker
        try:
            task_type = TaskType(task_type_str)
        except ValueError:
            task_type = TaskType.RESEARCH
        
        worker = self.workers.get(task_type, self.workers[TaskType.RESEARCH])
        
        # 构建消息
        message = AgentMessage(
            task_id=task_id,
            task_type=task_type,
            payload={"query": task["query"], "task": task},
            context=self.context_buffer.get_recent()
        )
        
        # 执行
        start = time.time()
        result = worker.process(message)
        total_latency = (time.time() - start) * 1000
        
        # 更新记忆
        self.context_buffer.add({
            "task_id": task_id,
            "task_type": task_type_str,
            "result": result,
            "timestamp": time.time()
        })
        
        # 更新知识库
        self.knowledge_base.add(
            key=task_type_str,
            value=f"task:{task_id} - {task['query'][:50]}",
            embedding=None
        )
        
        return {
            "task_id": task_id,
            "status": result["status"],
            "outputs": result["outputs"],
            "completeness": result["completeness"],
            "correctness": result["correctness"],
            "tokens": result["tokens"],
            "total_latency_ms": total_latency
        }

class MASSystem:
    """MAS系统入口"""
    
    def __init__(self):
        self.supervisor = SupervisorAgent()
    
    def execute(self, task: Dict) -> Dict[str, Any]:
        return self.supervisor.execute(task)

# 便捷函数
def create_mas_system() -> MASSystem:
    return MASSystem()
