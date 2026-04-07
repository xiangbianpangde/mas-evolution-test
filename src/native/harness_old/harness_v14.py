#!/usr/bin/env python3
"""
OpenClaw Native Harness v14.0 - Actionability-Focused Refinement

v13 教训：4 examples + ensemble 反而降低 actionability (L2.3 vs v12's L3.1)
v14 策略：回归 v12 的简洁设计，但针对 actionability 做专项优化

核心改进：
1. 恢复 2 examples (v12 风格)，不去追求更多
2. 去掉 ensemble eval (节省 50% evaluator tokens)
3. 专注于 Actionability 的具体指导：强调"步骤、数字、验证"
4. 优化 example 内容，让 Good Example 更具体可执行
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

class HarnessV14:
    """
    v14.0 Actionability-Focused Refinement
    
    v12 教训：2 examples 是最优的
    v13 错误：4 examples + ensemble eval 反而降低 actionability
    
    v14 策略：
    1. 回归 v12 的 2 examples 简洁设计
    2. 去掉 ensemble eval（省 tokens）
    3. 优化 Good Example：更强调具体步骤、数字、验证
    4. 保持整体简洁，不增加复杂度
    """
    
    # v14 Good Example - 更强调可执行性
    GOOD_EXAMPLE = """
## 好的输出标准（必须满足）

问题：如何优化 Redis 缓存性能？

输出示例：
1. **诊断步骤**：
   - 命令：`redis-cli --latency` → 当前 P99=50ms
   - 命令：`redis-cli info stats | grep hit_rate` → 当前 85%

2. **具体优化**：
   - 步骤1：`EXPIRE session:{id} 3600`（设置 1 小时过期）
   - 步骤2：使用 pipeline 批量操作
     ```python
     pipe = redis.pipeline()
     pipe.get("key1"); pipe.get("key2"); pipe.execute()
     ```
   - 步骤3：配置 `maxmemory-policy allkeys-lru`

3. **验证方法**：
   - 命令：`redis-cli --intrinsic-latency 5`
   - 指标：监控 `redis_exporter.rocketmq_broker_stats` 中的 hit_rate
   - 目标：P99 < 10ms, hit_rate > 95%

关键：有数字(50ms→10ms)、有命令、有代码、有验证"""
    
    # v14 Bad Example - 缺少可操作性
    BAD_EXAMPLE = """
## 差的输出（常见问题）

问题：如何优化 Redis 缓存性能？

问题输出：
1. 建议使用 pipeline
2. 建议设置过期时间
3. 建议监控性能

问题诊断：
- 缺少具体命令和参数
- 缺少代码实现
- 缺少验证方法
- 建议太空泛，无法直接执行"""

    # v14 Executor prompts - 简洁风格
    EXECUTOR_PROMPTS = {
        "research": """你是一个专业的研究分析师。分析技术问题并给出可操作的建议。

任务：{query}

参考下面标准，理解什么是高质量输出：

好的输出标准：
- 有具体数字（延迟ms、吞吐量QPS、百分比）
- 有具体命令或代码
- 有验证方法
- 步骤清晰可直接执行

""" + GOOD_EXAMPLE + """

VS

""" + BAD_EXAMPLE + """

请按照好标准输出你的分析。输出 300+ 字。""",

        "code": """你是一个专业的代码工程师。编写可直接运行的代码。

任务：{query}

好的代码标准：
- 完整可运行（有 import）
- 有使用示例（输入/输出）
- 有配置说明
- 有验证方法

""" + GOOD_EXAMPLE + """

VS

""" + BAD_EXAMPLE + """

请按照好标准输出你的代码。""",

        "review": """你是一个专业的架构评审专家。评审架构并给出可操作的改进建议。

任务：{query}

好的评审标准：
- 每个风险有具体触发条件
- 每个建议有具体步骤
- 有验证方法
- 有预期效果

""" + GOOD_EXAMPLE + """

VS

""" + BAD_EXAMPLE + """

请按照好标准输出你的评审。"""
    }
    
    # v14 Evaluator - 简化版，去掉 ensemble
    STRICT_EVALUATOR = """你是一个严格的技术评估专家。

评分标准：
- L5: 卓越 - 有具体数字/命令/代码，有验证方法，可直接执行
- L4: 优秀 - 分析深入，方案具体
- L3: 合格 - 技术正确，但方案需要细化
- L2: 不足 - 方案过于抽象，缺少关键步骤
- L1: 差 - 方案不可行

输出 JSON（不用 markdown）：
{{"depth": {{"level": 1-5, "reason": "原因"}}, "completeness": {{"level": 1-5, "reason": "原因"}}, "actionability": {{"level": 1-5, "reason": "原因"}}, "overall_score": 0-100, "reasoning": "说明"}}

---
{content}
---

请严格评分。"""

    def __init__(self, api_key: str):
        self.llm = RealLLMCaller(api_key)
    
    def parse_evaluator_response(self, content: str) -> Dict:
        """Parse evaluator response"""
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
        
        # Single evaluation (no ensemble)
        evaluator_start = time.time()
        evaluator_response = self.llm.call(
            prompt=self.STRICT_EVALUATOR.format(content=executor_output[:4000]),
            system_prompt="你是一个严格的技术评估专家。",
            max_tokens=1024
        )
        evaluator_latency = (time.time() - evaluator_start) * 1000
        
        parsed = self.parse_evaluator_response(
            evaluator_response["content"] if evaluator_response["success"] else ""
        )
        
        return TaskResult(
            task_id=task_id, task_type=task_type,
            executor_output=executor_output[:500],
            quality_score=parsed["quality_score"],
            depth_score=parsed["depth"],
            completeness_score=parsed["completeness"],
            actionability_score=parsed["actionability"],
            executor_tokens=executor_tokens,
            evaluator_tokens=evaluator_response["tokens_used"] if evaluator_response["success"] else 0,
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
    
    harness = HarnessV14(api_key)
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
    print("OpenClaw Harness v14.0 - Actionability-Focused")
    print("核心：回归 v12 简洁设计，强化 Actionability 指导")
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
        "harness_version": "v14.0",
        "architecture": "Actionability-Focused Refinement",
        "timestamp": datetime.now().isoformat(),
        "elapsed_seconds": elapsed,
        "summary": summary,
        "individual_results": [asdict(r) for r in results]
    }
    
    output_file = "/root/.openclaw/workspace/mas_repo/openclaw_native/benchmark_results_v14_gen1.json"
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\n[保存] 结果已保存至: {output_file}")
    return summary

if __name__ == "__main__":
    main()