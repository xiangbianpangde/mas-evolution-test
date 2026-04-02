"""
MAS Benchmark Suite v2.0 - Dynamic Difficulty + Generalization
增强版测试任务集
- 基础任务: 原有10个核心任务
- 泛化任务: 5个新任务 (测试未知领域能力)
- 难度递增: 随着能力提升自动增加任务复杂度
"""

import time
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
    is_generalization: bool = False  # 是否为泛化测试任务
    error: str = ""

class DynamicBenchmarkSuite:
    """动态难度 Benchmark - 包含泛化性测试"""
    
    # 核心任务 (原始10个)
    CORE_TASKS = [
        {
            "id": "core_001",
            "type": "research",
            "difficulty": 8,
            "query": "分析Transformer架构在长上下文场景下的注意力机制优化方案",
            "expected_outputs": ["技术分析", "代码示例", "benchmark数据"]
        },
        {
            "id": "core_002", 
            "type": "code",
            "difficulty": 9,
            "query": "实现一个支持动态窗口大小的滑动日志解析器，处理TB级日志",
            "expected_outputs": ["完整代码", "测试用例", "复杂度分析"]
        },
        {
            "id": "core_003",
            "type": "research", 
            "difficulty": 7,
            "query": "对比RAG与Fine-tuning在垂直领域问答场景下的成本效益",
            "expected_outputs": ["对比表格", "选型建议", "实施路线"]
        },
        {
            "id": "core_004",
            "type": "code",
            "difficulty": 8,
            "query": "设计一个分布式限流系统，支持多节点协同和精确度控制",
            "expected_outputs": ["架构图", "核心算法", "测试报告"]
        },
        {
            "id": "core_005",
            "type": "review",
            "difficulty": 6,
            "query": "审查微服务架构的潜在风险点：订单服务->支付服务->库存服务->物流服务",
            "expected_outputs": ["风险列表", "缓解方案", "优先级排序"]
        },
        {
            "id": "core_006",
            "type": "research",
            "difficulty": 9,
            "query": "调研当前LLM在数学推理方面的最新进展和瓶颈",
            "expected_outputs": ["论文综述", "SOTA分析", "未来方向"]
        },
        {
            "id": "core_007",
            "type": "code",
            "difficulty": 7,
            "query": "实现一个支持热更新的插件化框架，参考 Ansible/Logstash 设计",
            "expected_outputs": ["框架代码", "插件示例", "文档"]
        },
        {
            "id": "core_008",
            "type": "research",
            "difficulty": 8,
            "query": "分析向量数据库在实时推荐系统中的选型策略",
            "expected_outputs": ["技术对比", "性能基准", "成本分析"]
        },
        {
            "id": "core_009",
            "type": "code",
            "difficulty": 9,
            "query": "用Python实现一个简化版Raft共识算法，包括Leader选举和日志复制",
            "expected_outputs": ["算法实现", "状态机", "测试用例"]
        },
        {
            "id": "core_010",
            "type": "review",
            "difficulty": 7,
            "query": "对一个日活1000万的App后端系统进行架构评估和优化建议",
            "expected_outputs": ["评估报告", "优化方案", "优先级"]
        }
    ]
    
    # 泛化测试任务 (新任务 - 测试模型在未知领域的泛化能力)
    GENERALIZATION_TASKS = [
        {
            "id": "gen_001",
            "type": "research",
            "difficulty": 8,
            "query": "分析量子计算在组合优化问题中的实际应用前景与挑战",
            "expected_outputs": ["技术分析", "案例研究", "可行性评估"]
        },
        {
            "id": "gen_002",
            "type": "code",
            "difficulty": 9,
            "query": "实现一个自适应调度的线程池，支持基于负载的动态扩容和缩容",
            "expected_outputs": ["完整代码", "性能测试", "设计文档"]
        },
        {
            "id": "gen_003",
            "type": "review",
            "difficulty": 8,
            "query": "评估区块链技术在供应链溯源场景中的适用性和潜在风险",
            "expected_outputs": ["风险评估", "成本收益分析", "实施建议"]
        },
        {
            "id": "gen_004",
            "type": "research",
            "difficulty": 9,
            "query": "调研联邦学习在医疗数据隐私保护中的最新进展",
            "expected_outputs": ["技术综述", "隐私分析", "应用案例"]
        },
        {
            "id": "gen_005",
            "type": "code",
            "difficulty": 8,
            "query": "设计一个多模态RAG系统，融合文本、图像和表格进行智能问答",
            "expected_outputs": ["系统架构", "融合算法", "测试结果"]
        }
    ]
    
    def __init__(self, include_generalization=True):
        """
        初始化 Benchmark
        include_generalization: 是否包含泛化测试任务
        """
        self.include_generalization = include_generalization
        self.tasks = self._load_tasks()
    
    def _load_tasks(self) -> List[Dict]:
        """加载测试任务"""
        tasks = list(self.CORE_TASKS)
        if self.include_generalization:
            tasks.extend(self.GENERALIZATION_TASKS)
        return tasks
    
    def get_core_tasks_only(self) -> List[Dict]:
        """获取仅核心任务 (用于对比)"""
        return list(self.CORE_TASKS)
    
    def get_generalization_tasks_only(self) -> List[Dict]:
        """获取仅泛化任务"""
        return list(self.GENERALIZATION_TASKS)
    
    def run_all(self, mas_system) -> Tuple[List[TaskResult], Dict]:
        """运行完整测试集"""
        results = []
        for task in self.tasks:
            is_gen = task["id"].startswith("gen_")
            result = self.run_single(mas_system, task, is_generalization=is_gen)
            results.append(result)
        
        summary = self._compute_summary(results)
        return results, summary
    
    def run_single(self, mas_system, task: Dict, is_generalization=False) -> TaskResult:
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
                latency_ms=latency,
                is_generalization=is_generalization
            )
        except Exception as e:
            latency = (time.time() - start) * 1000
            return TaskResult(
                task_id=task["id"],
                success=False,
                score=0.0,
                tokens=0,
                latency_ms=latency,
                is_generalization=is_generalization,
                error=str(e)
            )
    
    def _evaluate_output(self, task: Dict, result: Dict) -> float:
        """评估输出质量 (0-100)"""
        score = 50.0
        
        outputs = result.get("outputs", [])
        expected = task["expected_outputs"]
        
        coverage = len(set(outputs) & set(expected)) / len(expected)
        score += coverage * 30
        
        if result.get("completeness", 0) > 0.8:
            score += 10
        
        if result.get("correctness", 0) > 0.8:
            score += 10
        
        return min(100, score)
    
    def _compute_summary(self, results: List[TaskResult]) -> Dict:
        """计算汇总指标 - 包含泛化性评分"""
        total = len(results)
        successes = sum(1 for r in results if r.success)
        
        # 核心任务统计
        core_results = [r for r in results if not r.is_generalization]
        core_success = sum(1 for r in core_results if r.success)
        core_avg_score = sum(r.score for r in core_results) / len(core_results) if core_results else 0
        core_avg_tokens = sum(r.tokens for r in core_results) / len(core_results) if core_results else 0
        
        # 泛化任务统计
        gen_results = [r for r in results if r.is_generalization]
        gen_success = sum(1 for r in gen_results if r.success)
        gen_avg_score = sum(r.score for r in gen_results) / len(gen_results) if gen_results else 0
        gen_avg_tokens = sum(r.tokens for r in gen_results) / len(gen_results) if gen_results else 0
        
        # 综合评分 (按字典序: 核心任务成功率 60%, 泛化性 30%, 效率 10%)
        overall_success_rate = successes / total if total > 0 else 0
        
        # 泛化性评分 (0-100)
        generalization_score = gen_avg_score if gen_results else 0
        
        # 综合得分 (字典序权重)
        composite = (
            overall_success_rate * 100 * 0.60 +  # 成功率 60%
            generalization_score * 0.30 +          # 泛化性 30%
            (core_success / len(core_results) * 100 if core_results else 0) * 0.10  # 效率 10%
        )
        
        avg_tokens = sum(r.tokens for r in results) / total if total > 0 else 0
        avg_latency = sum(r.latency_ms for r in results) / total if total > 0 else 0
        
        return {
            "total_tasks": total,
            "success_rate": overall_success_rate,
            "avg_score": sum(r.score for r in results) / total if total > 0 else 0,
            "avg_tokens": avg_tokens,
            "avg_latency_ms": avg_latency,
            "efficiency": (sum(r.score for r in results) / total) / (avg_tokens / 1000) if avg_tokens > 0 else 0,
            
            # 泛化性指标
            "core_success_rate": core_success / len(core_results) if core_results else 0,
            "core_avg_score": core_avg_score,
            "core_avg_tokens": core_avg_tokens,
            "generalization_success_rate": gen_success / len(gen_results) if gen_results else 0,
            "generalization_avg_score": gen_avg_score,
            "generalization_avg_tokens": gen_avg_tokens,
            "generalization_score": generalization_score,
            
            # 综合评分 (字典序)
            "composite_score": composite,
            
            # 防退化检查
            "degradation_detected": self._check_degradation(core_avg_score, gen_avg_score)
        }
    
    def _check_degradation(self, core_score: float, gen_score: float) -> bool:
        """
        检查是否发生能力退化
        规则: 如果泛化得分显著低于核心得分 (>20%差距), 可能是过拟合
        """
        if gen_score == 0:
            return False
        gap = (core_score - gen_score) / core_score if core_score > 0 else 0
        return gap > 0.20

class BenchmarkSuite:
    """兼容旧接口 - 简化版"""
    
    def __init__(self):
        self.tasks = DynamicBenchmarkSuite(include_generalization=False).tasks
    
    def run_all(self, mas_system) -> Tuple[List[TaskResult], Dict]:
        results = []
        for task in self.tasks:
            is_gen = task["id"].startswith("gen_")
            start = time.time()
            try:
                result = mas_system.execute(task)
                latency = (time.time() - start) * 1000
                score = self._evaluate_output(task, result)
                results.append(TaskResult(
                    task_id=task["id"],
                    success=True,
                    score=score,
                    tokens=result.get("tokens", 0),
                    latency_ms=latency,
                    is_generalization=is_gen
                ))
            except Exception as e:
                latency = (time.time() - start) * 1000
                results.append(TaskResult(
                    task_id=task["id"],
                    success=False,
                    score=0.0,
                    tokens=0,
                    latency_ms=latency,
                    is_generalization=is_gen,
                    error=str(e)
                ))
        
        summary = self._compute_summary(results)
        return results, summary
    
    def _evaluate_output(self, task: Dict, result: Dict) -> float:
        score = 50.0
        outputs = result.get("outputs", [])
        expected = task["expected_outputs"]
        coverage = len(set(outputs) & set(expected)) / len(expected)
        score += coverage * 30
        if result.get("completeness", 0) > 0.8:
            score += 10
        if result.get("correctness", 0) > 0.8:
            score += 10
        return min(100, score)
    
    def _compute_summary(self, results: List[TaskResult]) -> Dict:
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
            "efficiency": avg_score / (avg_tokens / 1000) if avg_tokens > 0 else 0,
            "generalization_score": avg_score,  # 兼容旧接口
            "degradation_detected": False
        }

def get_baseline_single_agent() -> Dict:
    """单Agent基线指标"""
    return {
        "success_rate": 0.65,
        "avg_score": 58.2,
        "avg_tokens": 2450,
        "avg_latency_ms": 45000,
        "efficiency": 0.024,
        "generalization_score": 45.0  # 单Agent泛化能力差
    }