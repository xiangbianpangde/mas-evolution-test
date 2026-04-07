#!/usr/bin/env python3
"""
OpenClaw Native Harness v9.0 - Self-Reflection Architecture

核心改进（相对于 v6-v8）：
1. 添加自反射阶段：Executor 先输出初稿 → 自我反思 → 修订输出
2. 强制结构化输出：必须包含具体技术细节
3. 深度分析：要求提供具体的代码/数字/引用

架构演进：
v6-v8: Executor → Evaluator (单次通过，输出质量受限)
v9:    Executor → [Self-Reflection] → Revised → Evaluator (双次通过，更深)

防作弊：Reflection 仍然看不到 expected outputs
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
    draft_output: str
    reflection_output: str
    final_output: str
    quality_score: float
    technical_depth: float
    completeness: float
    actionability: float
    executor_draft_tokens: int
    executor_reflection_tokens: int
    evaluator_tokens: int
    draft_latency_ms: float
    reflection_latency_ms: float
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

class HarnessV9:
    """
    v9.0 Self-Reflection Harness
    
    核心：双次通过 + 深度分析
    Stage 1: Executor 生成初稿
    Stage 2: Executor 自我反思，识别不足
    Stage 3: Executor 基于反思修订输出
    Stage 4: Evaluator 独立评分
    """
    
    # Stage 1: 初稿生成
    DRAFT_PROMPTS = {
        "research": """你是一个专业的研究分析师。进行深度技术分析。

任务：{query}

要求：
1. 深入分析技术原理（为什么/如何工作）
2. 提供具体代码示例（可运行的）
3. 提供 benchmark 数据或性能对比（必须包含具体数字）
4. 引用具体论文/技术文档
5. 分析局限性和未来方向

输出结构化内容，长度 400+ 字。""",

        "code": """你是一个专业的代码工程师。生成高质量代码解决方案。

任务：{query}

要求：
1. 完整可运行的代码（不是片段）
2. 包含单元测试和集成测试
3. 提供架构设计图（用文字描述）
4. 分析时间和空间复杂度
5. 提供至少 2 个使用示例

输出完整代码和说明，长度 400+ 字。""",

        "review": """你是一个专业的架构评审专家。进行深度架构评审。

任务：{query}

要求：
1. 识别至少 5 个风险点，每个风险必须包含：影响程度(1-5)、发生概率(1-5)、具体描述
2. 每个风险必须有对应的缓解方案
3. 提供优先级排序（P0/P1/P2）
4. 分析成本效益
5. 给出具体可执行的改进计划

输出完整评审报告，长度 400+ 字。"""
    }
    
    # Stage 2: 自我反思
    REFLECTION_PROMPT = """你是一个严格的自我评审专家。审查你之前的输出，识别不足。

原始任务：{query}

你之前的输出：
---
{draft}
---

请严格审查上述输出，识别：
1. **技术深度不足**：哪些分析过于表面？
2. **关键缺失**：有哪些重要方面没有覆盖？
3. **具体性不足**：哪些建议/代码不够具体可执行？
4. **逻辑漏洞**：有哪些前后矛盾或推理跳跃？

只输出你识别的问题，格式如下：
1. [深度不足] 具体描述...
2. [关键缺失] 具体描述...
3. [具体性不足] 具体描述...
（列出 3-5 个问题即可）"""

    # Stage 3: 修订输出
    REVISION_PROMPT = """你是一个专业的技术分析师。基于自我反思，修订并改进你的输出。

原始任务：{query}

你之前的输出：
---
{draft}
---

你的自我反思问题：
---
{reflection}
---

请基于上述反思问题，修订并改进你的输出。重点关注：
1. 深化技术分析
2. 补充缺失的重要方面
3. 使建议/代码更加具体可执行

输出修订后的完整内容，长度 400+ 字。"""

    # Stage 4: 评分
    EVALUATOR_PROMPT = """你是一个严格的质量评估专家。根据内容的多个维度进行评分。

评估标准（每个维度 0-100）：
1. **技术深度**：分析是否深入、原理是否清晰、是否有独到见解
2. **完整性**：是否覆盖任务的主要方面、是否有遗漏
3. **可操作性**：建议/代码是否具体可执行、是否可以直接落地

最终评分 = (技术深度 + 完整性 + 可操作性) / 3

只输出 JSON：{"depth": 0-100, "completeness": 0-100, "actionability": 0-100, "overall": 0-100, "reasoning": "简要说明"}"""

    def __init__(self, api_key: str):
        self.llm = RealLLMCaller(api_key)
    
    def execute_task(self, task: Dict) -> TaskResult:
        task_id = task["id"]
        task_type = task["type"]
        query = task["query"]
        
        # ============ Stage 1: 初稿 ============
        draft_start = time.time()
        draft_system = self.DRAFT_PROMPTS.get(task_type, self.DRAFT_PROMPTS["research"])
        draft_response = self.llm.call(
            prompt=f"任务：{query}",
            system_prompt=draft_system,
            max_tokens=2048
        )
        draft_latency = (time.time() - draft_start) * 1000
        
        if not draft_response["success"]:
            return TaskResult(
                task_id=task_id, task_type=task_type,
                draft_output="", reflection_output="", final_output="",
                quality_score=0, technical_depth=0, completeness=0, actionability=0,
                executor_draft_tokens=0, executor_reflection_tokens=0, evaluator_tokens=0,
                draft_latency_ms=draft_latency, reflection_latency_ms=0, evaluator_latency_ms=0,
                error=draft_response["error"]
            )
        
        draft_output = draft_response["content"]
        draft_tokens = draft_response["tokens_used"]
        
        # 异常检测
        is_suspicious = False
        suspicious_reason = ""
        if draft_latency < 5000 and len(draft_output) > 1000:
            is_suspicious = True
            suspicious_reason = f"异常短延迟({draft_latency:.0f}ms)+长输出"
        
        # ============ Stage 2: 自我反思 ============
        reflection_start = time.time()
        reflection_response = self.llm.call(
            prompt=self.REFLECTION_PROMPT.format(query=query, draft=draft_output[:3000]),
            system_prompt="你是一个严格的自我评审专家。",
            max_tokens=1024
        )
        reflection_latency = (time.time() - reflection_start) * 1000
        
        reflection_output = ""
        reflection_tokens = 0
        if reflection_response["success"]:
            reflection_output = reflection_response["content"]
            reflection_tokens = reflection_response["tokens_used"]
        
        # ============ Stage 3: 修订输出 ============
        revision_start = time.time()
        revision_response = self.llm.call(
            prompt=self.REVISION_PROMPT.format(
                query=query, 
                draft=draft_output[:2000],
                reflection=reflection_output[:1000] if reflection_output else "无"
            ),
            system_prompt=draft_system,
            max_tokens=2048
        )
        revision_latency = (time.time() - revision_start) * 1000
        
        final_output = draft_output  # 默认用初稿
        if revision_response["success"] and revision_response["tokens_used"] > 100:
            final_output = revision_response["content"]
        
        # ============ Stage 4: 评分 ============
        evaluator_start = time.time()
        evaluator_response = self.llm.call(
            prompt=f"请评估以下内容的质量：\n\n{final_output[:4000]}",
            system_prompt=self.EVALUATOR_PROMPT,
            max_tokens=512
        )
        evaluator_latency = (time.time() - evaluator_start) * 1000
        
        quality_score = 50
        technical_depth = 50
        completeness = 50
        actionability = 50
        
        if evaluator_response["success"]:
            try:
                content = evaluator_response["content"]
                if "{" in content and "}" in content:
                    json_str = content[content.index("{"):content.rindex("}")+1]
                    result = json.loads(json_str)
                    technical_depth = float(result.get("depth", 50))
                    completeness = float(result.get("completeness", 50))
                    actionability = float(result.get("actionability", 50))
                    quality_score = float(result.get("overall", 50))
            except:
                pass
        
        return TaskResult(
            task_id=task_id, task_type=task_type,
            draft_output=draft_output[:500],
            reflection_output=reflection_output[:300],
            final_output=final_output[:500],
            quality_score=quality_score,
            technical_depth=technical_depth,
            completeness=completeness,
            actionability=actionability,
            executor_draft_tokens=draft_tokens,
            executor_reflection_tokens=reflection_tokens,
            evaluator_tokens=evaluator_response["tokens_used"] if evaluator_response["success"] else 0,
            draft_latency_ms=draft_latency,
            reflection_latency_ms=reflection_latency,
            evaluator_latency_ms=evaluator_latency,
            is_suspicious=is_suspicious,
            suspicious_reason=suspicious_reason
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
    
    harness = HarnessV9(api_key)
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
        print(f"[{task['id']}] Draft({task['type']})...", end=" ", flush=True)
        result = harness.execute_task(task)
        results.append(result)
        
        sus = " [SUSPICIOUS]" if result.is_suspicious else ""
        print(f"质量:{result.quality_score:.0f}(深:{result.technical_depth:.0f}完:{result.completeness:.0f}行:{result.actionability:.0f}) "
              f"延迟:{(result.draft_latency_ms+result.reflection_latency_ms)/1000:.1f}s{sus}")
    
    summary = compute_summary(results)
    return results, summary

def compute_summary(results: List[TaskResult]) -> Dict:
    core = [r for r in results if not getattr(r, 'is_generalization', False)]
    gen = [r for r in results if getattr(r, 'is_generalization', True)]
    
    core_avg = sum(r.quality_score for r in core) / len(core) if core else 0
    gen_avg = sum(r.quality_score for r in gen) / len(gen) if gen else 0
    
    core_depth = sum(r.technical_depth for r in core) / len(core) if core else 0
    core_complete = sum(r.completeness for r in core) / len(core) if core else 0
    core_action = sum(r.actionability for r in core) / len(core) if core else 0
    
    total_tokens = sum(r.executor_draft_tokens + r.executor_reflection_tokens + r.evaluator_tokens for r in results)
    avg_latency = sum(r.draft_latency_ms + r.reflection_latency_ms for r in results) / len(results) / 1000 if results else 0
    
    suspicious = sum(1 for r in results if r.is_suspicious)
    anti_cheat = (1 - suspicious / len(results)) if results else 0
    
    composite = 0.6 * core_avg * anti_cheat + 0.3 * gen_avg + 0.1 * min(100, 1000 / (avg_latency + 1))
    
    return {
        "total_tasks": len(results),
        "core_avg_score": core_avg,
        "gen_avg_score": gen_avg,
        "core_technical_depth": core_depth,
        "core_completeness": core_complete,
        "core_actionability": core_action,
        "total_tokens": total_tokens,
        "avg_latency_s": avg_latency,
        "suspicious_count": suspicious,
        "composite_score": composite,
        "anti_cheat_factor": anti_cheat
    }

def main():
    from datetime import datetime
    
    print("=" * 60)
    print("OpenClaw Harness v9.0 - Self-Reflection Architecture")
    print("核心：Draft → Reflection → Revision → Evaluate")
    print("=" * 60)
    
    start = time.time()
    results, summary = run_benchmark()
    elapsed = time.time() - start
    
    print("\n" + "=" * 60)
    print("Benchmark 结果汇总")
    print("=" * 60)
    print(f"\n[核心任务] 平均质量分: {summary['core_avg_score']:.1f}")
    print(f"  - 技术深度: {summary['core_technical_depth']:.1f}")
    print(f"  - 完整性: {summary['core_completeness']:.1f}")
    print(f"  - 可操作性: {summary['core_actionability']:.1f}")
    print(f"\n[泛化任务] 平均质量分: {summary['gen_avg_score']:.1f}")
    print(f"[Token消耗] 总计: {summary['total_tokens']}")
    print(f"[平均延迟] {summary['avg_latency_s']:.1f}秒/任务")
    print(f"[可疑检测] {summary['suspicious_count']} 个任务标记为可疑")
    print(f"\n[综合评分] {summary['composite_score']:.2f}/100")
    print(f"[抗欺骗系数] {summary['anti_cheat_factor']:.2f}")
    print(f"[总耗时] {elapsed:.0f}秒")
    
    output = {
        "harness_version": "v9.0",
        "architecture": "Self-Reflection: Draft → Reflection → Revision → Evaluate",
        "timestamp": datetime.now().isoformat(),
        "elapsed_seconds": elapsed,
        "summary": summary,
        "individual_results": [asdict(r) for r in results]
    }
    
    output_file = "/root/.openclaw/workspace/mas_repo/openclaw_native/benchmark_results_v9_gen1.json"
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\n[保存] 结果已保存至: {output_file}")
    return summary

if __name__ == "__main__":
    main()
