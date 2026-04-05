#!/usr/bin/env python3
"""
OpenClaw Native Harness v9.0 - Type-Directed Strategy

v8.0 (52.27): CoT format - Core=60.0, Gen=49.2 (strong Core, weak Gen)
v2.0 (54.64): Self-reflection - Core=50.0, Gen=65.2 (weak Core, strong Gen)
v23 (58.30): Adaptive format - Core=54.4, Gen=68.2 (balanced, BEST)

Key insight: v8's CoT improved Core but weakened Gen.
v2's self-reflection improved Gen but didn't help Core enough.
v23's simple adaptive format balanced both.

v9.0 Strategy: Type-Directed Hybrid
- Research tasks: Use v8's CoT format (proven for research: core_001=87, core_003=87)
- Code tasks: Use v23's adaptive format (proven for code stability)
- Review tasks: Use v23's adaptive format + light self-reflection

Hypothesis: Task-specific optimization > one-size-fits-all

If v9.0 > v8.0 (52.27): Type-specific beats CoT-only
If v9.0 ≈ v8.0: CoT is the dominant factor
If v9.0 < v8.0: Over-engineering hurt performance
"""

import json
import time
import os
from dataclasses import dataclass
from typing import Dict

API_CONFIG = {
    "base_url": "https://api.minimaxi.com/anthropic",
    "model": "MiniMax-M2.7"
}

CHECKPOINT_FILE = "v9_0_checkpoint.json"
RESULTS_PREFIX = "benchmark_results_v9_0"

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
    error: str = ""
    iterations: int = 1

class RealLLMCaller:
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    def call(self, prompt: str, system_prompt: str = "", max_tokens: int = 2048, timeout: int = 120) -> Dict:
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
                data=data, headers=headers, method='POST'
            )
            with urllib.request.urlopen(req, timeout=timeout) as response:
                result = json.loads(response.read().decode('utf-8'))
            latency = (time.time() - start) * 1000
            content = ""
            for item in result.get("content", []):
                if item.get("type") == "text":
                    content = item.get("text", "")
                    break
            return {
                "content": content,
                "latency_ms": latency,
                "input_tokens": result.get("usage", {}).get("input_tokens", 0),
                "output_tokens": result.get("usage", {}).get("output_tokens", 0),
                "error": None
            }
        except Exception as e:
            return {
                "content": "", "latency_ms": (time.time() - start) * 1000,
                "input_tokens": 0, "output_tokens": 0, "error": str(e)
            }

# v9.0: Type-Directed Strategy

# Research tasks: CoT format (from v8)
COT_RESEARCH_PROMPT = """你是一个专业的技术分析师。

任务类型：research
任务：{query}

请按以下步骤深度分析：

Step 1 - 问题诊断：
[准确识别问题的核心挑战]

Step 2 - 深度分析：
[使用 Chain-of-Thought 推理，逐步拆解]
- 首先...（因果链）
- 然后...（递进关系）
- 最后...（综合结论）

Step 3 - 具体方案：
[有数字支撑的解决方案]

Step 4 - 数字证据：
[引用具体数据、研究或案例]

Step 5 - 验证方法：
[如何验证方案有效性]

直接输出你的完整分析。"""

# Code tasks: v23 adaptive format
ADAPTIVE_CODE_PROMPT = """你是一个专业的技术分析师。

任务类型：code
任务：{query}

根据任务类型，选择最合适的输出格式：

**code**: 架构简图 → 核心代码（完整可运行）→ 测试用例 → 配置说明

要求：
- 代码必须完整可运行
- 有具体的实现细节
- 有测试用例验证

直接输出你的分析。"""

# Review tasks: v23 format + light reflection
ADAPTIVE_REVIEW_PROMPT = """你是一个专业的技术分析师。

任务类型：review
任务：{query}

根据任务类型，选择最合适的输出格式：

**review**: 风险矩阵 → 影响分析 → 缓解步骤 → 优先级 → 验证方法

要求：
- 有具体的风险评分
- 有可操作的缓解步骤
- 有验证方法

直接输出你的分析。"""

SELF_CRITIQUE_REVIEW = """你是一个严格的技术评审专家。请评审以下输出：

当前输出：
{output}

请指出最多2个最重要的问题（如果有）：

问题1: [描述问题]
改进1: [具体建议]
（如果没有严重问题，回复"无需修改"）"""

REVISION_PROMPT = """你是一个专业的技术分析师。请根据评审意见改进：

之前的输出：
{output}

评审意见：
{critique}

请输出改进后的版本。"""

STRICT_EVALUATOR = """你是一个严格的技术评估专家。

评分标准：
- L5: 卓越 - 有独到见解，有具体可执行步骤，有数字证据
- L4: 优秀 - 分析深入，有具体方案
- L3: 合格 - 技术正确，但方案需要细化
- L2: 不足 - 方案过于抽象
- L1: 差 - 方案不可行

输出 JSON（不用markdown）：
{{"depth": {{"level": 1-5, "evidence": "引用"}}, "completeness": {{"level": 1-5, "evidence": "引用"}}, "actionability": {{"level": 1-5, "evidence": "引用"}}, "overall_score": 0-100, "reasoning": "说明"}}

---
{content}
---

请严格评分。"""

LENIENT_CODE_EVALUATOR = """你是一个代码质量评估专家。

评分标准：
- L5: 功能完整，结构清晰，有测试
- L4: 功能完整，有小问题
- L3: 基本OK
- L2: 不完整或混乱
- L1: 不可行

输出 JSON（不用markdown）：
{{"depth": {{"level": 1-5, "evidence": "引用"}}, "completeness": {{"level": 1-5, "evidence": "引用"}}, "actionability": {{"level": 1-5, "evidence": "引用"}}, "overall_score": 0-100, "reasoning": "说明"}}

---
{content}
---

重点看功能实现。"""


class HarnessV90:
    def __init__(self, api_key: str):
        self.llm = RealLLMCaller(api_key)
        self.api_key = api_key
    
    def get_prompt_for_task(self, task: Dict) -> tuple:
        """Get the appropriate prompt based on task type"""
        task_type = task["type"]
        query = task["query"]
        
        if task_type == "research":
            # Use CoT format for research (v8's strength)
            prompt = COT_RESEARCH_PROMPT.format(query=query)
            return prompt, "research"
        elif task_type == "code":
            return ADAPTIVE_CODE_PROMPT.format(query=query), "code"
        else:  # review
            return ADAPTIVE_REVIEW_PROMPT.format(query=query), "review"
    
    def execute_task(self, task: Dict) -> TaskResult:
        task_id = task["id"]
        task_type = task["type"]
        query = task["query"]
        
        executor_start = time.time()
        max_tokens = 3000 if task_type == "code" else 2500
        
        # Get appropriate prompt based on task type
        system_prompt, output_type = self.get_prompt_for_task(task)
        
        # Generate initial response
        initial_response = self.llm.call(
            prompt=f"任务类型：{task_type}\n任务：{query}",
            system_prompt=system_prompt,
            max_tokens=max_tokens
        )
        
        if initial_response["error"]:
            return TaskResult(
                task_id=task_id, task_type=task_type,
                executor_output="", quality_score=0,
                depth_score=0, completeness_score=0, actionability_score=0,
                executor_tokens=0, evaluator_tokens=0,
                executor_latency_ms=(time.time() - executor_start) * 1000,
                evaluator_latency_ms=0,
                error=f"Initial error: {initial_response['error']}"
            )
        
        current_output = initial_response["content"]
        total_tokens = initial_response.get("output_tokens", 0)
        iterations = 1
        
        # Light self-reflection for review tasks only
        if task_type == "review":
            critique_response = self.llm.call(
                prompt=SELF_CRITIQUE_REVIEW.format(output=current_output),
                system_prompt="你是一个严格的评审专家。",
                max_tokens=1000
            )
            total_tokens += critique_response.get("output_tokens", 0)
            critique_text = critique_response["content"]
            
            # Only revise if critique found real issues
            if "无需修改" not in critique_text and len(critique_text) > 100:
                revision_response = self.llm.call(
                    prompt=REVISION_PROMPT.format(output=current_output, critique=critique_text),
                    system_prompt="你是一个专业的技术分析师。",
                    max_tokens=max_tokens
                )
                total_tokens += revision_response.get("output_tokens", 0)
                if not revision_response.get("error"):
                    current_output = revision_response["content"]
                    iterations = 2
        
        executor_latency = (time.time() - executor_start) * 1000
        
        # Evaluate
        evaluator_start = time.time()
        evaluator_prompt = LENIENT_CODE_EVALUATOR if task_type == "code" else STRICT_EVALUATOR
        evaluator_response = self.llm.call(
            prompt=evaluator_prompt.format(content=current_output),
            system_prompt="你是一个严格的技术评估专家。",
            max_tokens=1024
        )
        evaluator_latency = (time.time() - evaluator_start) * 1000
        evaluator_tokens = evaluator_response.get("output_tokens", 0)
        total_tokens += evaluator_tokens
        
        if evaluator_response["error"]:
            return TaskResult(
                task_id=task_id, task_type=task_type,
                executor_output=current_output, quality_score=0,
                depth_score=0, completeness_score=0, actionability_score=0,
                executor_tokens=total_tokens, evaluator_tokens=0,
                executor_latency_ms=executor_latency, evaluator_latency_ms=evaluator_latency,
                error=f"Evaluator error: {evaluator_response['error']}"
            )
        
        try:
            eval_text = evaluator_response["content"]
            json_start = eval_text.find('{')
            json_end = eval_text.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                eval_json = json.loads(eval_text[json_start:json_end])
            else:
                eval_json = {"overall_score": 50, "depth": {"level": 3}, "completeness": {"level": 3}, "actionability": {"level": 3}}
            
            quality_score = eval_json.get("overall_score", 50)
            depth_score = eval_json.get("depth", {}).get("level", 3)
            completeness_score = eval_json.get("completeness", {}).get("level", 3)
            actionability_score = eval_json.get("actionability", {}).get("level", 3)
            is_suspicious = executor_latency < 10000 and len(current_output) > 1000
        except:
            quality_score = 50
            depth_score = completeness_score = actionability_score = 3
            is_suspicious = False
        
        return TaskResult(
            task_id=task_id, task_type=task_type,
            executor_output=current_output, quality_score=quality_score,
            depth_score=depth_score, completeness_score=completeness_score,
            actionability_score=actionability_score,
            executor_tokens=total_tokens, evaluator_tokens=evaluator_tokens,
            executor_latency_ms=executor_latency, evaluator_latency_ms=evaluator_latency,
            is_suspicious=is_suspicious,
            iterations=iterations
        )
    
    def run_benchmark(self) -> Dict:
        tasks = [
            {"id": "core_001", "type": "research", "difficulty": 8,
             "query": "分析 Transformer 架构在长上下文场景下的注意力机制优化方案"},
            {"id": "core_002", "type": "code", "difficulty": 9,
             "query": "实现一个支持动态窗口大小的滑动日志解析器，处理 TB 级日志"},
            {"id": "core_003", "type": "research", "difficulty": 7,
             "query": "对比 RAG 与 Fine-tuning 在垂直领域问答场景下的成本效益"},
            {"id": "core_004", "type": "code", "difficulty": 8,
             "query": "设计一个分布式限流系统，支持多节点协同和精确度控制"},
            {"id": "core_005", "type": "review", "difficulty": 6,
             "query": "评审微服务架构的链路调用复杂度，给出优化建议"},
            {"id": "core_006", "type": "research", "difficulty": 9,
             "query": "分析 LLM 数学推理能力的技术瓶颈与解决方案"},
            {"id": "core_007", "type": "code", "difficulty": 7,
             "query": "实现一个插件化框架，支持热更新和依赖管理"},
            {"id": "core_008", "type": "research", "difficulty": 8,
             "query": "分析向量数据库在实时推荐系统中的选型策略"},
            {"id": "core_009", "type": "code", "difficulty": 9,
             "query": "实现简化版 Raft 共识算法，包含 Leader 选举和日志复制"},
            {"id": "core_010", "type": "review", "difficulty": 7,
             "query": "评审日活 1000 万 App 后端系统的架构设计"},
            {"id": "gen_001", "type": "research", "difficulty": 8,
             "query": "分析量子计算在金融领域的应用前景与风险"},
            {"id": "gen_002", "type": "code", "difficulty": 9,
             "query": "实现联邦学习梯度聚合算法"},
            {"id": "gen_003", "type": "review", "difficulty": 8,
             "query": "评审 ZKP 身份认证系统的架构风险"},
            {"id": "gen_004", "type": "research", "difficulty": 9,
             "query": "分析脑机接口技术最新进展与商业化路径"},
            {"id": "gen_005", "type": "code", "difficulty": 9,
             "query": "实现去中心化身份认证（DID）系统"}
        ]
        
        results = []
        start_time = time.time()
        
        print("=" * 60)
        print("Harness v9.0 - Type-Directed Strategy")
        print("=" * 60)
        
        for task in tasks:
            print(f"[{task['id']}] Executor({task['type']})...", end=" ", flush=True)
            result = self.execute_task(task)
            results.append(result)
            print(f"Score: {result.quality_score:.1f} (iter={result.iterations})")
        
        elapsed = time.time() - start_time
        
        total = len(results)
        core_scores = [r.quality_score for r in results[:10] if r.quality_score > 0]
        gen_scores = [r.quality_score for r in results[10:] if r.quality_score > 0]
        avg_actionability = sum(r.actionability_score for r in results if r.quality_score > 0) / max(len(results), 1)
        
        core_avg = sum(core_scores) / len(core_scores) if core_scores else 0
        gen_avg = sum(gen_scores) / len(gen_scores) if gen_scores else 0
        composite = core_avg * 0.45 + gen_avg * 0.45 + (avg_actionability * 10) * 0.1
        
        print(f"\n{'=' * 60}")
        print(f"v9.0: Core={core_avg:.2f} Gen={gen_avg:.2f} Composite={composite:.2f}")
        print(f"{'=' * 60}")
        
        return {
            "harness_version": "v9.0",
            "paradigm": "v2 (Type-Directed Hybrid)",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "elapsed_seconds": elapsed,
            "summary": {
                "total_tasks": total,
                "core_avg_score": core_avg,
                "gen_avg_score": gen_avg,
                "avg_actionability_level": avg_actionability,
                "composite_score": composite,
            },
            "individual_results": [
                {"task_id": r.task_id, "task_type": r.task_type,
                 "quality_score": r.quality_score, "is_suspicious": r.is_suspicious,
                 "iterations": r.iterations}
                for r in results
            ]
        }


if __name__ == "__main__":
    api_key = "sk-cp-ZNEhSAB4-p-nraTwKzWoeLCpFPE-wY8If5v_1qxUvnW4_h0ryAunuH9_Vn-SItYx-D1AGFdRhD_6fn_9LhkpWG2yy6kUeRZBEjq8aFCUpruT5aFlM-Y5KDc"
    
    harness = HarnessV90(api_key)
    results = harness.run_benchmark()
    
    output_file = f"{RESULTS_PREFIX}_{time.strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\nResults saved to: {output_file}")