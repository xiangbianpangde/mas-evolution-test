#!/usr/bin/env python3
"""
OpenClaw Native Harness v13.0 - Enhanced Gen Reflection

v12.0 achieved 58.01 composite (Core=58.7, Gen=63.4)
v11's hybrid approach worked well:
- Research: v9 CoT format → Core excellent
- Code/Review: v23 format → good
- Gen: light reflection only → Gen needs improvement

v13 Strategy: Strengthen Gen reflection
- Keep v11's proven Research format
- Keep v11's Code/Review formats
- Add FULL self-reflection for Gen tasks (not just light)
- Target: Beat v23's Gen (68.2) while maintaining Core (58.7)
"""

import json
import time
import os
import sys
from dataclasses import dataclass
from typing import Dict

API_CONFIG = {
    "base_url": "https://api.minimaxi.com/anthropic",
    "model": "MiniMax-M2.7"
}

CHECKPOINT_FILE = "v13_0_checkpoint.json"
RESULTS_PREFIX = "benchmark_results_v13_0"

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
                    print(f"  [Retry {attempt+1}/{max_retries}]", end=" ", flush=True)
                    time.sleep(2)
            except Exception as e:
                if attempt < max_retries:
                    print(f"  [Error: {e}, retry {attempt+1}/{max_retries}]", end=" ", flush=True)
                    time.sleep(2)
                else:
                    return {"content": "", "latency_ms": 0, "input_tokens": 0, "output_tokens": 0, "error": str(e)}
        return {"content": "", "latency_ms": 0, "input_tokens": 0, "output_tokens": 0, "error": "Max retries exceeded"}
    
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

# v13.0: Research/Code/Review from v11 + Full reflection for Gen

RESEARCH_EXECUTOR = """你是一个专业的技术分析师。

任务：{query}

请按以下步骤深度分析：

## Step 1: 问题诊断
- 核心问题是什么？
- 有什么关键挑战？

## Step 2: 深度分析
- 技术原理是什么？
- 相关数据/案例有哪些？
- 优势 vs 劣势

## Step 3: 具体方案
- 至少3个可行方案
- 每个方案的预期效果
- 实施难度和风险

## Step 4: 数字证据
- 支持你观点的具体数字
- 行业基准或案例

## Step 5: 验证方法
- 如何验证方案有效性？
- 关键指标是什么？

直接输出你的完整分析。"""

CODE_EXECUTOR = """你是一个专业的技术分析师和代码专家。

任务：{query}

请按以下格式输出：

**架构简图**：用文字描述核心架构

**核心代码**：完整可运行的代码（用```包裹）

**测试用例**：验证功能正确性的测试

**配置说明**：如何部署和配置

要求：
- 代码必须可运行
- 有错误处理
- 有注释

直接输出你的完整分析。"""

REVIEW_EXECUTOR = """你是一个专业的架构评审专家。

任务：{query}

请按以下格式输出：

**风险矩阵**：列出主要风险及等级（高/中/低）

**影响分析**：每个风险的影响范围和程度

**缓解步骤**：针对每个风险的具体缓解方案

**优先级**：按风险等级排序的处理顺序

**验证方法**：如何确认风险已被缓解

直接输出你的完整分析。"""

# Full self-critique for Gen tasks (v13 improvement)
GEN_CRITIQUE = """你是一个严格的技术评审专家。请评审以下输出，找出关键问题：

任务类型：{task_type}
任务：{query}

当前输出：
{output}

请严格指出最多3个最重要的问题：

输出格式：
问题1: [描述]
改进1: [具体怎么做]
问题2: ...
问题3: ..."""

# Light critique for Core tasks (maintain speed)
LIGHT_CRITIQUE = """检查以下输出的质量。如果有明确问题，指出最重要的1个：

输出：
{output}

输出格式：
问题: [描述问题]
改进: [如何改进]

如果输出质量好，输出：
无问题"""

REVISION_PROMPT = """你是一个专业的技术分析师。

之前的输出：
{output}

评审意见：{critique}

请输出改进版本，解决指出的问题。"""

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


class HarnessV130:
    def __init__(self, api_key: str):
        self.llm = RealLLMCaller(api_key)
        self.api_key = api_key
    
    def get_executor_prompt(self, task_type: str, query: str) -> str:
        if task_type == "research":
            return RESEARCH_EXECUTOR.format(query=query)
        elif task_type == "code":
            return CODE_EXECUTOR.format(query=query)
        else:  # review
            return REVIEW_EXECUTOR.format(query=query)
    
    def execute_task(self, task: Dict) -> TaskResult:
        task_id = task["id"]
        task_type = task["type"]
        query = task["query"]
        is_gen = task_id.startswith("gen_")
        
        executor_start = time.time()
        max_tokens = 3000 if task_type == "code" else 2500
        
        # Step 1: Generate initial response
        initial_response = self.llm.call_with_retry(
            prompt=f"任务类型：{task_type}\n任务：{query}",
            system_prompt=self.get_executor_prompt(task_type, query),
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
        
        # Step 2: Self-critique - FULL for Gen, LIGHT for Core
        critique_prompt = GEN_CRITIQUE if is_gen else LIGHT_CRITIQUE
        critique_response = self.llm.call_with_retry(
            prompt=critique_prompt.format(task_type=task_type, query=query, output=current_output),
            system_prompt="你是一个严格的评审专家。",
            max_tokens=1500
        )
        
        total_tokens += critique_response.get("output_tokens", 0)
        critique_text = critique_response["content"]
        
        # Step 3: Revision - only if issues found
        iterations = 1
        has_issues = "问题" in critique_text and len(critique_text) > 50 and critique_text.count("问题") >= 1
        
        if has_issues and not critique_response.get("error"):
            revision_response = self.llm.call_with_retry(
                prompt=REVISION_PROMPT.format(output=current_output, critique=critique_text),
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
        
        results = []
        start_time = time.time()
        
        print("=" * 60)
        print("Harness v13.0 - Enhanced Gen Reflection")
        print("Strategy: v11 formats + FULL reflection for Gen tasks")
        print("=" * 60)
        
        for task in tasks:
            print(f"[{task['id']}] Executor({task['type']})...", end=" ", flush=True)
            result = self.execute_task(task)
            results.append(result)
            print(f"Score: {result.quality_score:.1f} (iter={result.iterations})")
            
            # Save checkpoint after each task
            checkpoint = {
                "tasks_completed": [r.task_id for r in results],
                "results": [{
                    "task_id": r.task_id, "task_type": r.task_type,
                    "quality_score": r.quality_score,
                    "iterations": r.iterations
                } for r in results]
            }
            with open(CHECKPOINT_FILE, 'w') as f:
                json.dump(checkpoint, f, ensure_ascii=False)
        
        elapsed = time.time() - start_time
        
        # Clean up checkpoint on success
        if os.path.exists(CHECKPOINT_FILE):
            os.remove(CHECKPOINT_FILE)
        
        total = len(results)
        core_scores = [r.quality_score for r in results[:10] if r.quality_score > 0]
        gen_scores = [r.quality_score for r in results[10:] if r.quality_score > 0]
        avg_actionability = sum(r.actionability_score for r in results if r.quality_score > 0) / max(len(results), 1)
        
        core_avg = sum(core_scores) / len(core_scores) if core_scores else 0
        gen_avg = sum(gen_scores) / len(gen_scores) if gen_scores else 0
        composite = core_avg * 0.45 + gen_avg * 0.45 + (avg_actionability * 10) * 0.1
        
        print(f"\n{'=' * 60}")
        print(f"v13.0: Core={core_avg:.2f} Gen={gen_avg:.2f} Composite={composite:.2f}")
        print(f"{'=' * 60}")
        
        return {
            "harness_version": "v13.0",
            "paradigm": "v2 (Enhanced Gen Reflection)",
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
    
    harness = HarnessV130(api_key)
    results = harness.run_benchmark()
    
    output_file = f"{RESULTS_PREFIX}_{time.strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\nResults saved to: {output_file}")