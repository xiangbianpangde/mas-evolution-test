"""
MAS Benchmark Suite v1.0
标准化测试任务集 - 评估MAS架构在复杂任务上的性能
"""

import time
import json
import random
from typing import Dict, List, Tuple
from dataclasses import dataclass

@dataclass
class TaskResult:
    task_id: str
    success: bool
    score: float
    tokens: int
    latency_ms: float
    error: str = ""

class BenchmarkSuite:
    """标准Benchmark - 10个高难度任务"""
    
    def __init__(self):
        self.tasks = self._load_tasks()
    
    def _load_tasks(self) -> List[Dict]:
        """加载测试任务"""
        return [
            {
                "id": "task_001",
                "type": "research",
                "difficulty": 8,
                "query": "分析Transformer架构在长上下文场景下的注意力机制优化方案",
                "expected_outputs": ["技术分析", "代码示例", "benchmark数据"]
            },
            {
                "id": "task_002", 
                "type": "code",
                "difficulty": 9,
                "query": "实现一个支持动态窗口大小的滑动日志解析器，处理TB级日志",
                "expected_outputs": ["完整代码", "测试用例", "复杂度分析"]
            },
            {
                "id": "task_003",
                "type": "research", 
                "difficulty": 7,
                "query": "对比RAG与Fine-tuning在垂直领域问答场景下的成本效益",
                "expected_outputs": ["对比表格", "选型建议", "实施路线"]
            },
            {
                "id": "task_004",
                "type": "code",
                "difficulty": 8,
                "query": "设计一个分布式限流系统，支持多节点协同和精确度控制",
                "expected_outputs": ["架构图", "核心算法", "测试报告"]
            },
            {
                "id": "task_005",
                "type": "review",
                "difficulty": 6,
                "query": "审查以下微服务架构的潜在风险点：订单服务->支付服务->库存服务->物流服务",
                "expected_outputs": ["风险列表", "缓解方案", "优先级排序"]
            },
            {
                "id": "task_006",
                "type": "research",
                "difficulty": 9,
                "query": "调研当前LLM在数学推理方面的最新进展和瓶颈",
                "expected_outputs": ["论文综述", "SOTA分析", "未来方向"]
            },
            {
                "id": "task_007",
                "type": "code",
                "difficulty": 7,
                "query": "实现一个支持热更新的插件化框架，参考 Ansible/Logstash 设计",
                "expected_outputs": ["框架代码", "插件示例", "文档"]
            },
            {
                "id": "task_008",
                "type": "research",
                "difficulty": 8,
                "query": "分析向量数据库在实时推荐系统中的选型策略",
                "expected_outputs": ["技术对比", "性能基准", "成本分析"]
            },
            {
                "id": "task_009",
                "type": "code",
                "difficulty": 9,
                "query": "用Python实现一个简化版Raft共识算法，包括Leader选举和日志复制",
                "expected_outputs": ["算法实现", "状态机", "测试用例"]
            },
            {
                "id": "task_010",
                "type": "review",
                "difficulty": 7,
                "query": "对一个日活1000万的App后端系统进行架构评估和优化建议",
                "expected_outputs": ["评估报告", "优化方案", "优先级"]
            }
        ]
    
    def run_all(self, mas_system) -> Tuple[List[TaskResult], Dict]:
        """运行完整测试集"""
        results = []
        for task in self.tasks:
            result = self.run_single(mas_system, task)
            results.append(result)
        
        summary = self._compute_summary(results)
        return results, summary
    
    def run_single(self, mas_system, task: Dict) -> TaskResult:
        """运行单个任务"""
        start = time.time()
        try:
            result = mas_system.execute(task)
            latency = (time.time() - start) * 1000
            score = self._evaluate_output(task, result)
            return TaskResult(
                task_id=task["id"],
                success=True,
                score=score,
                tokens=result.get("tokens", 0),
                latency_ms=latency
            )
        except Exception as e:
            latency = (time.time() - start) * 1000
            return TaskResult(
                task_id=task["id"],
                success=False,
                score=0.0,
                tokens=0,
                latency_ms=latency,
                error=str(e)
            )
    
    def _evaluate_output(self, task: Dict, result: Dict) -> float:
        """评估输出质量 (0-100)"""
        score = 50.0
        
        # 检查输出数量
        outputs = result.get("outputs", [])
        expected = task["expected_outputs"]
        
        coverage = len(set(outputs) & set(expected)) / len(expected)
        score += coverage * 30
        
        # 检查质量指标
        if result.get("completeness", 0) > 0.8:
            score += 10
        
        if result.get("correctness", 0) > 0.8:
            score += 10
        
        return min(100, score)
    
    def _compute_summary(self, results: List[TaskResult]) -> Dict:
        """计算汇总指标"""
        total = len(results)
        successes = sum(1 for r in results if r.success)
        avg_score = sum(r.score for r in results) / total if total > 0 else 0
        avg_tokens = sum(r.tokens for r in results) / total if total > 0 else 0
        avg_latency = sum(r.latency_ms for r in results) / total if total > 0 else 0
        
        return {
            "total_tasks": total,
            "success_rate": successes / total if total > 0 else 0,
            "avg_score": avg_score,
            "avg_tokens": avg_tokens,
            "avg_latency_ms": avg_latency,
            "efficiency": avg_score / (avg_tokens / 1000) if avg_tokens > 0 else 0
        }

def get_baseline_single_agent() -> Dict:
    """单Agent基线指标 (历史数据)"""
    return {
        "success_rate": 0.65,
        "avg_score": 58.2,
        "avg_tokens": 2450,
        "avg_latency_ms": 45000,
        "efficiency": 0.024
    }
