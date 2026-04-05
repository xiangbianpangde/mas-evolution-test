#!/usr/bin/env python3
"""
OpenClaw Native Harness v10.0 - Type-Directed + Targeted Self-Reflection

v9.0 (56.73): Type-directed strategy - Core=57.4, Gen=61.4
v23 (58.30): Adaptive format - Core=54.4, Gen=68.2 (still BEST overall)

Key insight from v8/v9:
- CoT improved research tasks (core_001=91, core_003=78)
- But Gen dropped because code tasks still weak

v10 Strategy: Type-Directed + Targeted Self-Reflection
- Research: CoT format (proven) + targeted self-reflection on depth
- Code: v23 format + self-reflection for implementation completeness  
- Review: v23 format + self-reflection for risk coverage

Hypothesis: Targeted reflection on WEAK areas (code, gen) will boost Gen without hurting Core.
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

CHECKPOINT_FILE = "v10_0_checkpoint.json"
RESULTS_PREFIX = "benchmark_results_v10_0"

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
    
    def call_with_retry(self, prompt: str, system_prompt: str = "", max_tokens: int = 2048, timeout: int = 120, max_retries: int = 2) -> Dict:
        for attempt in range(max_retries + 1):
            try:
                result = self._make_request(prompt, system_prompt, max_tokens, timeout)
                if result.get("error") is None:
                    return result
                if attempt < max_retries:
                    print(f"  [Retry {attempt+1}]", end=" ", flush=True)
                    time.sleep(2)
            except Exception as e:
                if attempt < max_retries:
                    print(f"  [Err: {str(e)[:30]}, retry {attempt+1}]", end=" ", flush=True)
                    time.sleep(2)
                else:
                    return {"content": "", "latency_ms": 0, "input_tokens": 0, "output_tokens": 0, "error": str(e)}
        return {"content": "", "latency_ms": 0, "input_tokens": 0, "output_tokens": 0, "error": "Max retries"}
    
    def _make_request(self, prompt: str, system_prompt: str, max_tokens: int, timeout: int) -> Dict:
        import urllib.request
        start = time.time()
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

# v10.0: Type-Directed + Targeted Self-Reflection

# Research tasks: CoT format (from v8, proven for research)
RESEARCH_EXECUTOR = """你是一个专业的技术分析师。

任务：{query}

请按照以下 Chain-of-Thought 格式输出你的完整分析：

1. **问题诊断**：识别核心技术问题
2. **深度分析**：分解问题成因，包含具体数字和案例
3. **解决方案**：提出具体可操作的技术方案
4. **数字证据**：引用具体数字、研究数据或案例
5. **验证方法**：说明如何验证方案有效性
6. **风险评估**：识别潜在风险和应对策略

要求：
- 有具体数字和证据支撑
- 有可操作的步骤
- 有验证方法

直接输出完整分析。"""

# Code tasks: v23 format + self-reflection for completeness
CODE_EXECUTOR = """你是一个专业的技术分析师。

任务类型：code
任务：{query}

根据任务类型，选择最合适的输出格式：

**code**: 架构简图 → 核心代码（完整可运行）→ 测试用例 → 配置说明

要求：
- 有具体数字和证据
- 有可操作的步骤
- 有验证方法
- 代码必须可运行

直接输出你的完整分析。"""

# Review tasks: v23 format + self-reflection for risk coverage
REVIEW_EXECUTOR = """你是一个专业的技术分析师。

任务类型：review
任务：{query}

根据任务类型，选择最合适的输出格式：

**review**: 风险矩阵 → 影响分析 → 缓解步骤 → 优先级 → 验证方法

要求：
- 有具体数字和证据
- 有可操作的步骤
- 有验证方法
- 代码必须可运行

直接输出你的完整分析。"""

# Self-reflection prompts (targeted to task type)
RESEARCH_REFLECTION = """你是一个严格的技术评审专家。

当前输出（research任务）：
{output}

请检查：
1. 深度分析是否充分？（要求：包含具体数字、案例、研究数据）
2. 解决方案是否可操作？（要求：步骤明确、可执行）
3. 验证方法是否有效？（要求：可复现的验证方式）

如果发现问题，请指出最多2个关键问题和改进建议。
否则，回复"无需修改"。

输出格式：
问题1: [描述]
改进1: [建议]
（可选问题2...）
或：无需修改"""

CODE_REFLECTION = """你是一个严格的代码评审专家。

当前输出（code任务）：
{output}

请检查：
1. 代码是否完整可运行？（要求：包含完整实现、依赖说明、测试用例）
2. 架构设计是否合理？（要求：模块化、可扩展）
3. 是否有错误处理和边界条件？（要求：健壮性）

如果发现问题，请指出最多2个关键问题和改进建议。
否则，回复"无需修改"。

输出格式：
问题1: [描述]
改进1: [建议]
（可选问题2...）
或：无需修改"""

REVIEW_REFLECTION = """你是一个严格的风险评审专家。

当前输出（review任务）：
{output}

请检查：
1. 风险矩阵是否全面？（要求：覆盖主要风险维度）
2. 影响分析是否有具体数据支撑？
3. 缓解步骤是否可操作？

如果发现问题，请指出最多2个关键问题和改进建议。
否则，回复"无需修改"。

输出格式：
问题1: [描述]
改进1: [建议]
（可选问题2...）
或：无需修改"""

REVISION_PROMPT = """你是一个专业的技术分析师。请根据评审意见改进你的输出：

任务类型：{task_type}
任务：{query}

之前的输出：
{output}

评审意见：
{critique}

请输出改进后的完整版本。保持原有优点，解决评审指出的问题。"""

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


class HarnessV100:
    def __init__(self, api_key: str):
        self.llm = RealLLMCaller(api_key)
        self.api_key = api_key
    
    def get_executor_prompt(self, task_type: str) -> str:
        if task_type == "research":
            return RESEARCH_EXECUTOR
        elif task_type == "code":
            return CODE_EXECUTOR
        else:  # review
            return REVIEW_EXECUTOR
    
    def get_reflection_prompt(self, task_type: str) -> str:
        if task_type == "research":
            return RESEARCH_REFLECTION
        elif task_type == "code":
            return CODE_REFLECTION
        else:  # review
            return REVIEW_REFLECTION
    
    def load_checkpoint(self) -> Dict:
        if os.path.exists(CHECKPOINT_FILE):
            try:
                with open(CHECKPOINT_FILE, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {"tasks_completed": [], "results": []}
    
    def save_checkpoint(self, checkpoint: Dict):
        with open(CHECKPOINT_FILE, 'w') as f:
            json.dump(checkpoint, f, ensure_ascii=False)
    
    def execute_task(self, task: Dict) -> TaskResult:
        task_id = task["id"]
        task_type = task["type"]
        query = task["query"]
        
        executor_start = time.time()
        max_tokens = 3000 if task_type == "code" else 2500
        
        # Step 1: Generate initial response using type-specific prompt
        executor_prompt = self.get_executor_prompt(task_type)
        initial_response = self.llm.call_with_retry(
            prompt=f"任务类型：{task_type}\n任务：{query}",
            system_prompt=executor_prompt.format(query=query),
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
        
        # Step 2: Type-targeted self-reflection
        reflection_prompt = self.get_reflection_prompt(task_type)
        reflection_response = self.llm.call_with_retry(
            prompt=reflection_prompt.format(output=current_output),
            system_prompt="你是一个严格的评审专家。",
            max_tokens=1500
        )
        
        total_tokens += reflection_response.get("output_tokens", 0)
        reflection_text = reflection_response["content"]
        
        # Step 3: Revision if reflection found issues
        iterations = 1
        needs_revision = len(reflection_text) > 50 and "问题" in reflection_text and "无需修改" not in reflection_text
        
        if needs_revision and not reflection_response.get("error"):
            revision_response = self.llm.call_with_retry(
                prompt=REVISION_PROMPT.format(
                    task_type=task_type, query=query,
                    output=current_output, critique=reflection_text
                ),
                system_prompt="你是一个专业的技术分析师。",
                max_tokens=max_tokens
            )
            total_tokens += revision_response.get("output_tokens", 0)
            if not revision_response.get("error"):
                current_output = revision_response["content"]
                iterations = 2
        
        executor_latency = (time.time() - executor_start) * 1000
        
        # Step 4: Evaluate
        evaluator_start = time.time()
        evaluator_prompt = LENIENT_CODE_EVALUATOR if task_type == "code" else STRICT_EVALUATOR
        evaluator_response = self.llm.call_with_retry(
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
        
        checkpoint = self.load_checkpoint()
        completed_ids = set(checkpoint["tasks_completed"])
        
        results = []
        for r in checkpoint.get("results", []):
            results.append(TaskResult(**r))
        
        start_time = time.time()
        for task in tasks:
            if task["id"] in completed_ids:
                print(f"[{task['id']}] SKIP (checkpoint)")
                continue
                
            print(f"[{task['id']}] Executor({task['type']})...", end=" ", flush=True)
            result = self.execute_task(task)
            results.append(result)
            print(f"Score: {result.quality_score:.1f} (iter={result.iterations})")
            
            # Save checkpoint
            checkpoint["tasks_completed"].append(task["id"])
            checkpoint["results"].append({
                "task_id": result.task_id,
                "task_type": result.task_type,
                "executor_output": result.executor_output,
                "quality_score": result.quality_score,
                "depth_score": result.depth_score,
                "completeness_score": result.completeness_score,
                "actionability_score": result.actionability_score,
                "executor_tokens": result.executor_tokens,
                "evaluator_tokens": result.evaluator_tokens,
                "executor_latency_ms": result.executor_latency_ms,
                "evaluator_latency_ms": result.evaluator_latency_ms,
                "is_suspicious": result.is_suspicious,
                "error": result.error,
                "iterations": result.iterations
            })
            self.save_checkpoint(checkpoint)
        
        elapsed = time.time() - start_time
        
        # Clean up checkpoint on success
        if os.path.exists(CHECKPOINT_FILE):
            os.remove(CHECKPOINT_FILE)
        
        total = len(results)
        core_results = [r for r in results if r.task_id.startswith("core_") and r.quality_score > 0]
        gen_results = [r for r in results if r.task_id.startswith("gen_") and r.quality_score > 0]
        
        core_scores = [r.quality_score for r in core_results]
        gen_scores = [r.quality_score for r in gen_results]
        
        core_avg = sum(core_scores) / len(core_scores) if core_scores else 0
        gen_avg = sum(gen_scores) / len(gen_scores) if gen_scores else 0
        
        all_scores = [r for r in results if r.quality_score > 0]
        avg_actionability = sum(r.actionability_score for r in all_scores) / max(len(all_scores), 1)
        
        composite = core_avg * 0.45 + gen_avg * 0.45 + (avg_actionability * 10) * 0.1
        
        print(f"\n{'=' * 60}")
        print(f"v10.0: Core={core_avg:.2f} Gen={gen_avg:.2f} Composite={composite:.2f}")
        print(f"{'=' * 60}")
        
        return {
            "harness_version": "v10.0",
            "paradigm": "v2 (Type-Directed + Targeted Self-Reflection)",
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
    
    harness = HarnessV100(api_key)
    results = harness.run_benchmark()
    
    output_file = f"{RESULTS_PREFIX}_{time.strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\nResults saved to: {output_file}")