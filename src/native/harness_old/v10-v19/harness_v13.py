#!/usr/bin/env python3
"""
OpenClaw Native Harness v13.0 - Multi-Example Calibration + Ensemble Eval

v12 教训：单样本 Few-Shot 可能不够稳定
v13 方案：
1. 增加 2 Good + 2 Bad examples（共4个）覆盖不同场景
2. Ensemble Evaluation：运行 2 次 Evaluator 取平均，降低随机性
3. 显式分数范围指导，减少评分模糊性
"""

import json
import time
import os
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Tuple

API_CONFIG = {
    "base_url": "https://api.minimaxi.com/anthropic",
    "model": "MiniMax-M2.7"
}

@dataclass
class TaskResult:
    task_id: str
    task_type: str
    executor_output: str
    quality_score: float
    depth_score: int
    completeness_score: int
    actionability_score: int
    executor_tokens: int
    evaluator_tokens: int
    executor_latency_ms: float
    evaluator_latency_ms: float
    is_suspicious: bool = False
    suspicious_reason: str = ""
    error: str = ""

class RealLLMCaller:
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    def call(self, prompt: str, system_prompt: str = "", max_tokens: int = 2048, timeout: int = 120) -> Dict[str, Any]:
        import urllib.request
        
        start = time.time()
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01"
            }
            
            payload = {
                "model": API_CONFIG["model"],
                "max_tokens": max_tokens,
                "system": system_prompt or "You are a helpful AI assistant.",
                "messages": [{"role": "user", "content": prompt}]
            }
            
            data = json.dumps(payload).encode('utf-8')
            req = urllib.request.Request(
                f"{API_CONFIG['base_url']}/v1/messages",
                data=data,
                headers=headers,
                method='POST'
            )
            
            with urllib.request.urlopen(req, timeout=timeout) as response:
                result = json.loads(response.read().decode('utf-8'))
            
            latency = (time.time() - start) * 1000
            
            raw_content = result.get("content", [])
            content = ""
            for item in raw_content:
                if item.get("type") == "text":
                    content = item.get("text", "")
                    break
            
            tokens = result.get("usage", {}).get("output_tokens", 0)
            
            return {
                "success": True,
                "content": content,
                "tokens_used": tokens,
                "latency_ms": latency,
                "error": None
            }
            
        except Exception as e:
            latency = (time.time() - start) * 1000
            return {
                "success": False,
                "content": "",
                "tokens_used": 0,
                "latency_ms": latency,
                "error": str(e)
            }

class HarnessV13:
    """
    v13.0 Multi-Example Calibration + Ensemble Eval
    
    v12 改进：Few-Shot 效果显著 (51.97 vs 41.73)
    v13 方案：
    1. 增加更多 examples 覆盖不同质量层次
    2. Ensemble Eval 降低评分方差
    3. 显式分数区间指导
    """
    
    # Good Example 1 - 高 Actionability (详细方案)
    GOOD_EXAMPLE_1 = """
## 示例1：好的输出（高 Actionability）

问题：如何优化 Redis 缓存性能？

输出：
1. **问题诊断**：
   - 使用 `redis-cli --latency` 检测延迟，当前 P99=50ms
   - 观察 `hit rate` = 85%，低于 95% 目标

2. **优化步骤**：
   - 步骤1：设置 key 过期时间 `EXPIRE session:{id} 3600`
   - 步骤2：使用 pipeline 批量操作：
     ```python
     pipe = redis.pipeline()
     pipe.get(k1); pipe.get(k2); pipe.get(k3)
     results = pipe.execute()
     ```
   - 步骤3：部署 Redis Cluster 分散热点

3. **验证方法**：
   - 运行 `redis-cli --intrinsic-latency 5` 基准测试
   - 监控 `redis_exporter` 的 `redis_memory_used_bytes` 指标

预期结果：P95 延迟从 50ms 降至 5ms"""
    
    # Good Example 2 - 架构分析
    GOOD_EXAMPLE_2 = """
## 示例2：好的输出（深度分析）

问题：微服务架构如何处理分布式事务？

输出：
1. **问题分析**：
   - 传统 ACID 事务在分布式场景下不适用
   - 需要在一致性(C)与可用性(A)间取舍（CAP定理）

2. **方案对比**：
   | 方案 | 一致性 | 复杂度 | 适用场景 |
   |------|--------|--------|----------|
   | 2PC | 强 | 高 | 银行核心 |
   | Saga | 最终 | 中 | 电商订单 |
   | TCC | 最终 | 中高 | 支付 |

3. **推荐实践**：
   - 使用 Seata 框架，支持 AT/Saga 模式
   - 配置超时机制：transaction.timeout=30s
   - 做好幂等：每个操作要有 unique request id

关键结论：绝大多数场景用 Saga + 幂等设计即可。"""

    # Bad Example 1 - 过于抽象
    BAD_EXAMPLE_1 = """
## 示例1：差的输出（过于抽象）

问题：如何优化 Redis 缓存性能？

输出：
1. 建议优化：
   - 使用 pipeline
   - 设置过期时间
   - 监控性能

2. 注意事项：
   - 注意缓存穿透
   - 注意内存管理

问题诊断：缺少具体步骤、参数、代码示例。"""

    # Bad Example 2 - 缺少验证
    BAD_EXAMPLE_2 = """
## 示例2：差的输出（缺少验证）

问题：微服务架构如何处理分布式事务？

输出：
1. 分布式事务很复杂
2. 可以用 Seata
3. 需要做好幂等

问题诊断：有方案名称但缺少配置、代码、验证方法。"""

    # v13 Executor prompts with 4 examples
    EXECUTOR_PROMPTS = {
        "research": """你是一个专业的研究分析师。分析技术问题并给出可操作的建议。

任务：{query}

参考下面示例理解高质量输出的标准：

""" + GOOD_EXAMPLE_1 + """

""" + GOOD_EXAMPLE_2 + """

VS

""" + BAD_EXAMPLE_1 + """

""" + BAD_EXAMPLE_2 + """

请按照好示例的标准输出你的分析。
要求：
- 包含具体步骤、数字、参数
- 有代码示例（如适用）
- 有验证方法和预期结果""",

        "code": """你是一个专业的代码工程师。编写可直接运行的代码。

任务：{query}

参考下面示例：

""" + GOOD_EXAMPLE_1 + """

""" + GOOD_EXAMPLE_2 + """

VS

""" + BAD_EXAMPLE_1 + """

""" + BAD_EXAMPLE_2 + """

好的代码示例应该：
- 包含完整可运行的代码（所有 import）
- 有使用示例（输入/输出）
- 有错误处理
- 有配置说明

请按好示例标准输出你的代码。""",

        "review": """你是一个专业的架构评审专家。评审架构并给出可操作的改进建议。

任务：{query}

参考下面示例：

""" + GOOD_EXAMPLE_1 + """

""" + GOOD_EXAMPLE_2 + """

VS

""" + BAD_EXAMPLE_1 + """

""" + BAD_EXAMPLE_2 + """

好的评审应该：
- 分析深入，有表格对比（如适用）
- 每个风险有触发条件和影响
- 每个建议有具体步骤
- 有验证方法

请按好示例标准输出你的评审。"""
    }
    
    # v13 Evaluator with explicit score ranges
    STRICT_EVALUATOR = """你是一个严格的技术评估专家。

评分标准（按分数区间）：

**90-100分**：超越预期
- 有独到见解，非常详细的方案
- 代码完整可运行，有测试用例
- 有具体数字支撑（如延迟ms、吞吐量QPS）
- 验证方法完整

**70-89分**：达到预期
- 分析深入，有具体方案
- 代码基本完整
- 有配置参数和步骤说明
- 有验证方法

**50-69分**：基本合格
- 技术正确，方案可行
- 但细节不足（如缺少参数、步骤模糊）
- 需要补充才能实施

**30-49分**：不足
- 方案过于抽象或缺少关键步骤
- 缺少具体参数或代码不完整
- 难以直接实施

**0-29分**：差
- 方案不可行或方向错误
- 缺少关键组件

输出 JSON（不用 markdown）：
{{"depth": {{"level": 1-5, "reason": "原因"}}, "completeness": {{"level": 1-5, "reason": "原因"}}, "actionability": {{"level": 1-5, "reason": "原因"}}, "overall_score": 0-100, "reasoning": "说明"}}

---
{content}
---

请先判断属于哪个分数区间，然后给出具体评分。"""

    def __init__(self, api_key: str):
        self.llm = RealLLMCaller(api_key)
    
    def parse_evaluator_response(self, content: str) -> Dict:
        """Parse evaluator response with robust error handling"""
        try:
            if "{" in content and "}" in content:
                json_str = content[content.index("{"):content.rindex("}")+1]
                result = json.loads(json_str)
                return {
                    "depth": int(result.get("depth", {}).get("level", 3)),
                    "completeness": int(result.get("completeness", {}).get("level", 3)),
                    "actionability": int(result.get("actionability", {}).get("level", 3)),
                    "quality_score": float(result.get("overall_score", 50))
                }
        except:
            pass
        return {"depth": 3, "completeness": 3, "actionability": 3, "quality_score": 50}
    
    def execute_task(self, task: Dict) -> TaskResult:
        task_id = task["id"]
        task_type = task["type"]
        query = task["query"]
        
        # Execute task
        executor_start = time.time()
        executor_system = self.EXECUTOR_PROMPTS.get(task_type, self.EXECUTOR_PROMPTS["research"])
        executor_response = self.llm.call(
            prompt=f"任务：{query}",
            system_prompt=executor_system,
            max_tokens=2048
        )
        executor_latency = (time.time() - executor_start) * 1000
        
        if not executor_response["success"]:
            return TaskResult(
                task_id=task_id, task_type=task_type,
                executor_output="",
                quality_score=0, depth_score=0, completeness_score=0, actionability_score=0,
                executor_tokens=0, evaluator_tokens=0,
                executor_latency_ms=executor_latency, evaluator_latency_ms=0,
                error=executor_response["error"]
            )
        
        executor_output = executor_response["content"]
        executor_tokens = executor_response["tokens_used"]
        
        # Suspicious detection
        is_suspicious = False
        if executor_latency < 5000 and len(executor_output) > 1000:
            is_suspicious = True
        
        # Ensemble Evaluation: Run 2 times and average
        evaluator_start = time.time()
        
        eval_results = []
        total_eval_tokens = 0
        
        for i in range(2):
            eval_response = self.llm.call(
                prompt=self.STRICT_EVALUATOR.format(content=executor_output[:4000]),
                system_prompt="你是一个严格的技术评估专家。",
                max_tokens=1024
            )
            if eval_response["success"]:
                total_eval_tokens += eval_response["tokens_used"]
                parsed = self.parse_evaluator_response(eval_response["content"])
                eval_results.append(parsed)
        
        evaluator_latency = (time.time() - evaluator_start) * 1000
        
        # Average ensemble results
        if eval_results:
            avg_depth = sum(r["depth"] for r in eval_results) / len(eval_results)
            avg_completeness = sum(r["completeness"] for r in eval_results) / len(eval_results)
            avg_actionability = sum(r["actionability"] for r in eval_results) / len(eval_results)
            avg_quality = sum(r["quality_score"] for r in eval_results) / len(eval_results)
        else:
            avg_depth = avg_completeness = avg_actionability = avg_quality = 50
        
        return TaskResult(
            task_id=task_id, task_type=task_type,
            executor_output=executor_output[:500],
            quality_score=avg_quality,
            depth_score=round(avg_depth),
            completeness_score=round(avg_completeness),
            actionability_score=round(avg_actionability),
            executor_tokens=executor_tokens,
            evaluator_tokens=total_eval_tokens,
            executor_latency_ms=executor_latency,
            evaluator_latency_ms=evaluator_latency,
            is_suspicious=is_suspicious
        )

class BenchmarkTasks:
    CORE_TASKS = [
        {"id": "core_001", "type": "research", "difficulty": 8,
         "query": "分析 Transformer 架构在长上下文场景下的注意力机制优化方案"},
        {"id": "core_002", "type": "code", "difficulty": 9,
         "query": "实现一个支持动态窗口大小的滑动日志解析器，处理TB级日志"},
        {"id": "core_003", "type": "research", "difficulty": 7,
         "query": "对比 RAG 与 Fine-tuning 在垂直领域问答场景下的成本效益"},
        {"id": "core_004", "type": "code", "difficulty": 8,
         "query": "设计一个分布式限流系统，支持多节点协同和精确度控制"},
        {"id": "core_005", "type": "review", "difficulty": 6,
         "query": "审查微服务架构的潜在风险点：订单服务->支付服务->库存服务->物流服务"},
        {"id": "core_006", "type": "research", "difficulty": 9,
         "query": "调研当前 LLM 在数学推理方面的最新进展和瓶颈"},
        {"id": "core_007", "type": "code", "difficulty": 7,
         "query": "实现一个支持热更新的插件化框架，参考 Ansible/Logstash 设计"},
        {"id": "core_008", "type": "research", "difficulty": 8,
         "query": "分析向量数据库在实时推荐系统中的选型策略"},
        {"id": "core_009", "type": "code", "difficulty": 9,
         "query": "用 Python 实现一个简化版 Raft 共识算法，包括 Leader 选举和日志复制"},
        {"id": "core_010", "type": "review", "difficulty": 7,
         "query": "对一个日活 1000 万的 App 后端系统进行架构评估和优化建议"},
    ]
    
    GENERALIZATION_TASKS = [
        {"id": "gen_001", "type": "research", "difficulty": 8,
         "query": "分析量子计算在金融领域的应用前景与风险"},
        {"id": "gen_002", "type": "code", "difficulty": 9,
         "query": "实现一个联邦学习框架的梯度聚合模块，支持多方数据协作"},
        {"id": "gen_003", "type": "review", "difficulty": 8,
         "query": "评估零知识证明（ZKP）在身份认证系统中的应用风险"},
        {"id": "gen_004", "type": "research", "difficulty": 9,
         "query": "调研脑机接口（BCI）技术的最新进展与商业化挑战"},
        {"id": "gen_005", "type": "code", "difficulty": 9,
         "query": "设计一个去中心化身份认证（DID）系统，支持跨平台互认"},
    ]

def run_benchmark() -> Tuple[List[TaskResult], Dict]:
    api_key = os.environ.get("MINIMAX_API_KEY", "")
    if not api_key:
        api_key = "sk-cp-ZNEhSAB4-p-nraTwKzWoeLCpFPE-wY8If5v_1qxUvnW4_h0ryAunuH9_Vn-SItYx-D1AGFdRhD_6fn_9LhkpWG2yy6kUeRZBEjq8aFCUpruT5aFlM-Y5KDc"
    
    harness = HarnessV13(api_key)
    tasks = BenchmarkTasks()
    
    all_tasks = []
    for t in tasks.CORE_TASKS:
        t["is_generalization"] = False
        all_tasks.append(t)
    for t in tasks.GENERALIZATION_TASKS:
        t["is_generalization"] = True
        all_tasks.append(t)
    
    results = []
    
    for task in all_tasks:
        print(f"[{task['id']}] Executor({task['type']})...", end=" ", flush=True)
        result = harness.execute_task(task)
        results.append(result)
        
        sus = " [SUSPICIOUS]" if result.is_suspicious else ""
        print(f"质量:{result.quality_score:.0f}(深:L{result.depth_score}完:L{result.completeness_score}行:L{result.actionability_score}) "
              f"延迟:{result.executor_latency_ms/1000:.1f}s{sus}")
    
    summary = compute_summary(results)
    return results, summary

def compute_summary(results: List[TaskResult]) -> Dict:
    core = [r for r in results if not getattr(r, 'is_generalization', False)]
    gen = [r for r in results if getattr(r, 'is_generalization', True)]
    
    core_avg = sum(r.quality_score for r in core) / len(core) if core else 0
    gen_avg = sum(r.quality_score for r in gen) / len(gen) if gen else 0
    
    avg_depth = sum(r.depth_score for r in results) / len(results) if results else 0
    avg_complete = sum(r.completeness_score for r in results) / len(results) if results else 0
    avg_action = sum(r.actionability_score for r in results) / len(results) if results else 0
    
    total_tokens = sum(r.executor_tokens + r.evaluator_tokens for r in results)
    avg_latency = sum(r.executor_latency_ms for r in results) / len(results) / 1000 if results else 0
    
    suspicious = sum(1 for r in results if r.is_suspicious)
    anti_cheat = (1 - suspicious / len(results)) if results else 0
    
    composite = 0.6 * core_avg * anti_cheat + 0.3 * gen_avg + 0.1 * min(100, 1000 / (avg_latency + 1))
    
    return {
        "total_tasks": len(results),
        "core_avg_score": core_avg,
        "gen_avg_score": gen_avg,
        "avg_depth_level": avg_depth,
        "avg_completeness_level": avg_complete,
        "avg_actionability_level": avg_action,
        "total_tokens": total_tokens,
        "avg_latency_s": avg_latency,
        "suspicious_count": suspicious,
        "composite_score": composite,
        "anti_cheat_factor": anti_cheat
    }

def main():
    from datetime import datetime
    
    print("=" * 60)
    print("OpenClaw Harness v13.0 - Multi-Example + Ensemble Eval")
    print("核心：4个示例 + 2次Evaluator取平均，降低评分方差")
    print("=" * 60)
    
    start = time.time()
    results, summary = run_benchmark()
    elapsed = time.time() - start
    
    print("\n" + "=" * 60)
    print("Benchmark 结果汇总")
    print("=" * 60)
    print(f"\n[核心任务] 平均质量分: {summary['core_avg_score']:.1f}")
    print(f"  - 平均深度等级: L{summary['avg_depth_level']:.1f}")
    print(f"  - 平均完整性等级: L{summary['avg_completeness_level']:.1f}")
    print(f"  - 平均可操作性等级: L{summary['avg_actionability_level']:.1f}")
    print(f"\n[泛化任务] 平均质量分: {summary['gen_avg_score']:.1f}")
    print(f"[Token消耗] 总计: {summary['total_tokens']}")
    print(f"[平均延迟] {summary['avg_latency_s']:.1f}秒/任务")
    print(f"[可疑检测] {summary['suspicious_count']} 个任务标记为可疑")
    print(f"\n[综合评分] {summary['composite_score']:.2f}/100")
    print(f"[抗欺骗系数] {summary['anti_cheat_factor']:.2f}")
    print(f"[总耗时] {elapsed:.0f}秒")
    
    output = {
        "harness_version": "v13.0",
        "architecture": "Multi-Example Calibration + Ensemble Eval",
        "timestamp": datetime.now().isoformat(),
        "elapsed_seconds": elapsed,
        "summary": summary,
        "individual_results": [asdict(r) for r in results]
    }
    
    output_file = "/root/.openclaw/workspace/mas_repo/openclaw_native/benchmark_results_v13_gen1.json"
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\n[保存] 结果已保存至: {output_file}")
    return summary

if __name__ == "__main__":
    main()