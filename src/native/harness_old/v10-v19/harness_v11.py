#!/usr/bin/env python3
"""
OpenClaw Native Harness v11.0 - Actionability-Focused Executor

核心改进（相对于 v10）：
v10 问题：Actionability 评分最低（L2.7），Executor 输出的建议过于抽象
v11 改进：Executor prompts 强制要求具体可执行的输出

关键变化：
1. Executor prompts 强调"具体步骤"和"参数"
2. 要求提供伪代码/实现细节
3. 要求提供预期结果和成功标准
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

class HarnessV11:
    """
    v11.0 Actionability-Focused Architecture
    
    v10 结果分析：
    - Depth: L3.1 (好)
    - Completeness: L2.9 (中)
    - Actionability: L2.7 (最低！)
    
    v11 改进：强化 Actionability
    """
    
    # v11 Executor prompts - 强调可操作性
    EXECUTOR_PROMPTS = {
        "research": """你是一个专业的研究分析师。进行深度技术分析，输出必须可直接指导实践。

任务：{query}

输出要求（必须全部满足）：
1. **技术原理**：深入分析原理（为什么/如何工作），包含关键公式或伪代码
2. **代码示例**：提供完整可运行的代码（不是片段），包含输入输出示例
3. **Benchmark数据**：包含具体数字对比（延迟/吞吐量/准确率等）
4. **实施步骤**：分点列出具体实施步骤，每步包含：
   - 所需工具/库
   - 关键参数设置
   - 预期结果
   - 验证方法
5. **局限性**：诚实分析局限性和适用边界

**重要**：实施步骤必须足够具体，读者看完可以直接动手执行！

输出 500+ 字。""",

        "code": """你是一个专业的代码工程师。生成可直接部署的代码解决方案。

任务：{query}

输出要求（必须全部满足）：
1. **完整代码**：完整可运行的代码，包含所有 import 和依赖
2. **使用示例**：提供 2-3 个使用示例，包括输入输出
3. **配置参数**：列出所有可配置参数及默认值
4. **API设计**：如果涉及 API，提供接口签名和说明
5. **部署步骤**：分步说明如何部署和运行
6. **测试验证**：说明如何验证代码正确性

**重要**：代码必须可直接复制运行，不需要读者补充任何内容！

输出完整代码和说明，500+ 字。""",

        "review": """你是一个专业的架构评审专家。输出的建议必须可直接执行。

任务：{query}

输出要求（必须全部满足）：
1. **风险列表**：每个风险必须包含：
   - 风险名称
   - 影响程度（1-5）和发生概率（1-5）
   - 具体触发条件
   - 潜在损失估计
2. **缓解方案**：每个风险必须对应一个方案，方案包含：
   - 实施步骤（具体！）
   - 所需资源（人力/时间/成本）
   - 预期效果
3. **优先级排序**：P0/P1/P2，并说明排序依据
4. **快速修复**：列出 3 个可在 1 天内实施的短期改进
5. **长期规划**：列出 3 个需要 1 周以上的长期改进

**重要**：每个方案必须具体到读者知道第一步做什么！

输出完整评审报告，500+ 字。"""
    }
    
    # v11 严格评估器（与 v10 相同）
    STRICT_EVALUATOR = """你是一个严格的技术评估专家。评估输出质量的 5 个等级。

评分标准：
- L5: 卓越 - 有独到见解，包含具体可执行步骤，包含数字证据
- L4: 优秀 - 分析深入，有具体方案
- L3: 合格 - 技术正确，但方案需要进一步细化才能执行
- L2: 不足 - 方案过于抽象，缺少关键细节
- L1: 差 - 方案不可行或严重缺失

评估维度：
1. 技术深度：分析是否有深度
2. 完整性：是否覆盖所有方面
3. 可操作性：建议/代码是否可以直接执行

输出 JSON（不用 markdown 代码块）：
{{"depth": {{"level": 1-5, "evidence": "具体引用"}}, "completeness": {{"level": 1-5, "evidence": "具体引用"}}, "actionability": {{"level": 1-5, "evidence": "具体引用"}}, "overall_score": 0-100, "reasoning": "说明"}}

---
{content}
---

请严格评分。"""

    def __init__(self, api_key: str):
        self.llm = RealLLMCaller(api_key)
    
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
        
        is_suspicious = False
        if executor_latency < 5000 and len(executor_output) > 1000:
            is_suspicious = True
        
        evaluator_start = time.time()
        evaluator_response = self.llm.call(
            prompt=self.STRICT_EVALUATOR.format(content=executor_output[:4000]),
            system_prompt="你是一个严格的技术评估专家。",
            max_tokens=1024
        )
        evaluator_latency = (time.time() - evaluator_start) * 1000
        
        quality_score = 50
        depth_score = 3
        completeness_score = 3
        actionability_score = 3
        
        if evaluator_response["success"]:
            try:
                content = evaluator_response["content"]
                if "{" in content and "}" in content:
                    json_str = content[content.index("{"):content.rindex("}")+1]
                    result = json.loads(json_str)
                    
                    depth_score = int(result.get("depth", {}).get("level", 3))
                    completeness_score = int(result.get("completeness", {}).get("level", 3))
                    actionability_score = int(result.get("actionability", {}).get("level", 3))
                    quality_score = float(result.get("overall_score", 50))
            except:
                pass
        
        return TaskResult(
            task_id=task_id, task_type=task_type,
            executor_output=executor_output[:500],
            quality_score=quality_score,
            depth_score=depth_score,
            completeness_score=completeness_score,
            actionability_score=actionability_score,
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
    
    harness = HarnessV11(api_key)
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
    print("OpenClaw Harness v11.0 - Actionability-Focused Executor")
    print("核心：强化可操作性要求，提升 Actionability 评分")
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
        "harness_version": "v11.0",
        "architecture": "Actionability-Focused Executor",
        "timestamp": datetime.now().isoformat(),
        "elapsed_seconds": elapsed,
        "summary": summary,
        "individual_results": [asdict(r) for r in results]
    }
    
    output_file = "/root/.openclaw/workspace/mas_repo/openclaw_native/benchmark_results_v11_gen1.json"
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\n[保存] 结果已保存至: {output_file}")
    return summary

if __name__ == "__main__":
    main()
