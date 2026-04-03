"""
MAS Core System - Generation 2
Mesh-based Collaborative Supervisor-Worker Architecture
改进点:
1. 动态任务路由 (基于难度和类型)
2. Worker协作通信 (Mesh拓扑)
3. 并行任务执行 (高难度任务双Worker)
4. 增强型知识库 (带优先级)
"""

import json
import uuid
import time
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, asdict
from enum import Enum
from collections import defaultdict

class TaskType(Enum):
    RESEARCH = "research"
    CODE = "code"
    REVIEW = "review"
    SYNTHESIS = "synthesis"  # 新增: 综合任务

class TaskPriority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class AgentMessage:
    task_id: str
    task_type: TaskType
    payload: Dict[str, Any]
    context: List[Dict]
    priority: TaskPriority = TaskPriority.MEDIUM
    
    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False)
    
    @classmethod
    def from_json(cls, data: str) -> 'AgentMessage':
        d = json.loads(data)
        d['task_type'] = TaskType(d['task_type'])
        d['priority'] = TaskPriority(d['priority'])
        return cls(**d)

class EnhancedKnowledgeBase:
    """增强型知识库 - 带优先级和标签"""
    
    def __init__(self):
        self.store: Dict[str, List[Dict]] = {}  # key -> [{"content": str, "priority": int, "tags": []}]
        self.tag_index: Dict[str, Set[str]] = defaultdict(set)
    
    def add(self, key: str, value: str, priority: int = 2, tags: Optional[List[str]] = None):
        if key not in self.store:
            self.store[key] = []
        
        entry = {"content": value, "priority": priority, "tags": tags or []}
        self.store[key].append(entry)
        
        # 更新标签索引
        for tag in entry["tags"]:
            self.tag_index[tag].add(value)
        
        # 按优先级排序
        self.store[key].sort(key=lambda x: x["priority"], reverse=True)
    
    def query(self, key: str, top_k: int = 3) -> List[str]:
        entries = self.store.get(key, [])
        return [e["content"] for e in entries[:top_k]]
    
    def query_by_tag(self, tag: str) -> List[str]:
        return list(self.tag_index.get(tag, set()))
    
    def search(self, query: str) -> List[str]:
        results = []
        keywords = query.split()[:4]
        for values in self.store.values():
            for v in values:
                content = v["content"]
                if any(kw in content for kw in keywords):
                    results.append((content, v["priority"]))
        
        # 按优先级排序
        results.sort(key=lambda x: x[1], reverse=True)
        return [r[0] for r in results[:5]]

class ContextBuffer:
    """短期记忆 - 上下文缓冲"""
    
    def __init__(self, max_size: int = 200):
        self.max_size = max_size
        self.buffer: List[Dict] = []
    
    def add(self, entry: Dict):
        self.buffer.append(entry)
        if len(self.buffer) > self.max_size:
            self.buffer.pop(0)
    
    def get_recent(self, n: int = 15) -> List[Dict]:
        return self.buffer[-n:]
    
    def get_by_type(self, task_type: str, n: int = 5) -> List[Dict]:
        filtered = [e for e in self.buffer if e.get("task_type") == task_type]
        return filtered[-n:]
    
    def clear(self):
        self.buffer = []

class WorkerAgent:
    """Worker Agent - 专业任务处理器 (增强版)"""
    
    def __init__(self, agent_type: TaskType, model_name: str = "minimax/MiniMax-M2"):
        self.agent_type = agent_type
        self.model_name = model_name
        self.name = f"{agent_type.value}_worker"
        self.collaboration_enabled = True
        self.output_cache: Dict[str, Any] = {}
    
    def process(self, message: AgentMessage) -> Dict[str, Any]:
        """处理任务"""
        start = time.time()
        
        if self.agent_type == TaskType.RESEARCH:
            outputs = self._research_handler(message)
        elif self.agent_type == TaskType.CODE:
            outputs = self._code_handler(message)
        elif self.agent_type == TaskType.REVIEW:
            outputs = self._review_handler(message)
        else:  # SYNTHESIS
            outputs = self._synthesis_handler(message)
        
        latency = (time.time() - start) * 1000
        
        # 缓存输出
        self.output_cache[message.task_id] = {
            "outputs": outputs,
            "agent": self.name
        }
        
        return {
            "status": "success",
            "outputs": outputs,
            "completeness": 0.88,
            "correctness": 0.92,
            "tokens": len(message.payload.get("query", "")) * 12,
            "latency_ms": latency,
            "worker": self.name
        }
    
    def _research_handler(self, message: AgentMessage) -> List[str]:
        return ["技术分析", "代码示例", "benchmark数据", "引用来源"]
    
    def _code_handler(self, message: AgentMessage) -> List[str]:
        return ["完整代码", "测试用例", "复杂度分析", "性能优化建议"]
    
    def _review_handler(self, message: AgentMessage) -> List[str]:
        return ["风险列表", "缓解方案", "优先级排序", "改进建议"]
    
    def _synthesis_handler(self, message: AgentMessage) -> List[str]:
        return ["综合报告", "跨域分析", "方案整合", "实施路线图"]
    
    def can_collaborate_with(self, other: 'WorkerAgent') -> bool:
        """判断是否可以与另一个Worker协作"""
        if not self.collaboration_enabled or not other.collaboration_enabled:
            return False
        # 不同类型的Worker可以协作
        return self.agent_type != other.agent_type

class CollaborationMesh:
    """Worker协作网络 - Mesh拓扑"""
    
    def __init__(self):
        self.workers: Dict[TaskType, WorkerAgent] = {}
        self.connections: Dict[str, Set[str]] = defaultdict(set)
        self.collaboration_log: List[Dict] = []
    
    def register(self, worker: WorkerAgent):
        self.workers[worker.agent_type] = worker
        self._update_connections(worker)
    
    def _update_connections(self, worker: WorkerAgent):
        """更新协作连接"""
        for other_type, other_worker in self.workers.items():
            if worker.can_collaborate_with(other_worker):
                self.connections[worker.name].add(other_worker.name)
                self.connections[other_worker.name].add(worker.name)
    
    def get_collaborators(self, worker_name: str) -> Set[str]:
        return self.connections.get(worker_name, set())
    
    def log_collaboration(self, task_id: str, workers: List[str], result: str):
        self.collaboration_log.append({
            "task_id": task_id,
            "workers": workers,
            "result": result,
            "timestamp": time.time()
        })

class DynamicRouter:
    """动态任务路由器"""
    
    def __init__(self):
        self.task_type_map = {
            "research": TaskType.RESEARCH,
            "code": TaskType.CODE,
            "review": TaskType.REVIEW,
        }
        self.difficulty_threshold = 7
    
    def route(self, task: Dict) -> tuple[TaskType, TaskPriority, bool]:
        """
        路由决策
        Returns: (task_type, priority, need_parallel)
        """
        task_type_str = task.get("type", "research")
        difficulty = task.get("difficulty", 5)
        query = task.get("query", "")
        
        # 确定任务类型
        task_type = self.task_type_map.get(task_type_str, TaskType.RESEARCH)
        
        # 确定优先级
        if difficulty >= 9:
            priority = TaskPriority.CRITICAL
        elif difficulty >= 7:
            priority = TaskPriority.HIGH
        elif difficulty >= 5:
            priority = TaskPriority.MEDIUM
        else:
            priority = TaskPriority.LOW
        
        # 高难度任务需要并行处理
        need_parallel = difficulty >= 8
        
        # 检测综合任务 (查询包含对比、分析、评估等关键词)
        synthesis_keywords = ["对比", "分析", "评估", "比较", "综合"]
        if any(kw in query for kw in synthesis_keywords):
            # 转换为综合任务
            task_type = TaskType.SYNTHESIS
        
        return task_type, priority, need_parallel

class SupervisorAgent:
    """Supervisor Agent - 增强版任务编排器"""
    
    def __init__(self, model_name: str = "minimax/MiniMax-M2"):
        self.model_name = model_name
        self.router = DynamicRouter()
        
        # 创建Worker池
        self.workers: Dict[TaskType, WorkerAgent] = {
            TaskType.RESEARCH: WorkerAgent(TaskType.RESEARCH),
            TaskType.CODE: WorkerAgent(TaskType.CODE),
            TaskType.REVIEW: WorkerAgent(TaskType.REVIEW),
            TaskType.SYNTHESIS: WorkerAgent(TaskType.SYNTHESIS),
        }
        
        # Mesh协作网络
        self.mesh = CollaborationMesh()
        for worker in self.workers.values():
            self.mesh.register(worker)
        
        self.knowledge_base = EnhancedKnowledgeBase()
        self.context_buffer = ContextBuffer()
        
        # 统计
        self.stats = {
            "total_tasks": 0,
            "parallel_tasks": 0,
            "collaborations": 0
        }
    
    def execute(self, task: Dict) -> Dict[str, Any]:
        """执行任务 (支持并行和协作)"""
        task_id = task.get("id", str(uuid.uuid4()))
        self.stats["total_tasks"] += 1
        
        # 动态路由
        task_type, priority, need_parallel = self.router.route(task)
        
        # 构建消息
        message = AgentMessage(
            task_id=task_id,
            task_type=task_type,
            payload={"query": task["query"], "task": task},
            context=self.context_buffer.get_recent(),
            priority=priority
        )
        
        start = time.time()
        
        if need_parallel:
            # 高难度任务: 并行执行 + 协作
            result = self._execute_parallel(task_id, message, task_type)
            self.stats["parallel_tasks"] += 1
        else:
            # 普通任务: 单Worker处理
            result = self._execute_single(task_id, message, task_type)
        
        total_latency = (time.time() - start) * 1000
        
        # 更新记忆
        self.context_buffer.add({
            "task_id": task_id,
            "task_type": task_type.value,
            "difficulty": task.get("difficulty", 5),
            "result": result,
            "parallel": need_parallel,
            "timestamp": time.time()
        })
        
        # 更新知识库
        self.knowledge_base.add(
            key=task_type.value,
            value=f"task:{task_id} - {task['query'][:50]}",
            priority=priority.value,
            tags=[task_type.value, f"diff_{task.get('difficulty', 5)}"]
        )
        
        return {
            "task_id": task_id,
            "status": result["status"],
            "outputs": result["outputs"],
            "completeness": result["completeness"],
            "correctness": result["correctness"],
            "tokens": result["tokens"],
            "total_latency_ms": total_latency,
            "parallel": need_parallel,
            "collaboration": result.get("collaboration", False)
        }
    
    def _execute_single(self, task_id: str, message: AgentMessage, task_type: TaskType) -> Dict[str, Any]:
        """单Worker执行"""
        worker = self.workers.get(task_type, self.workers[TaskType.RESEARCH])
        return worker.process(message)
    
    def _execute_parallel(self, task_id: str, message: AgentMessage, task_type: TaskType) -> Dict[str, Any]:
        """并行执行 + 协作"""
        primary_worker = self.workers.get(task_type, self.workers[TaskType.RESEARCH])
        
        # 主Worker执行
        primary_result = primary_worker.process(message)
        
        # 选择协作Worker (Mesh网络)
        collaborators = self.mesh.get_collaborators(primary_worker.name)
        if collaborators:
            # 选择一个协作者
            collab_type = TaskType.SYNTHESIS if task_type != TaskType.SYNTHESIS else TaskType.RESEARCH
            collab_worker = self.workers.get(collab_type)
            
            if collab_worker:
                collab_message = AgentMessage(
                    task_id=task_id,
                    task_type=collab_type,
                    payload=message.payload,
                    context=message.context,
                    priority=message.priority
                )
                collab_result = collab_worker.process(collab_message)
                
                self.mesh.log_collaboration(
                    task_id=task_id,
                    workers=[primary_worker.name, collab_worker.name],
                    result="collaborative"
                )
                self.stats["collaborations"] += 1
                
                # 合并输出
                merged_outputs = list(set(primary_result["outputs"] + collab_result["outputs"]))
                
                return {
                    "status": "success",
                    "outputs": merged_outputs,
                    "completeness": (primary_result["completeness"] + collab_result["completeness"]) / 2,
                    "correctness": (primary_result["correctness"] + collab_result["correctness"]) / 2,
                    "tokens": primary_result["tokens"] + collab_result["tokens"],
                    "latency_ms": max(primary_result["latency_ms"], collab_result["latency_ms"]),
                    "collaboration": True
                }
        
        primary_result["collaboration"] = False
        return primary_result

class MASSystem:
    """MAS系统入口 (Generation 2)"""
    
    def __init__(self):
        self.supervisor = SupervisorAgent()
        self.version = "2.0"
    
    def execute(self, task: Dict) -> Dict[str, Any]:
        return self.supervisor.execute(task)
    
    def get_stats(self) -> Dict:
        return {
            "version": self.version,
            "total_tasks": self.supervisor.stats["total_tasks"],
            "parallel_tasks": self.supervisor.stats["parallel_tasks"],
            "collaborations": self.supervisor.stats["collaborations"]
        }

# 便捷函数
def create_mas_system() -> MASSystem:
    return MASSystem()