#!/usr/bin/env python3
"""
OpenClaw Native Harness v9.0 - Extended Self-Reflection for ALL Gen Tasks

v8.0 问题发现：
- Gen code 任务（gen_002, gen_005）没有获得自反射优化
- gen_005 multimodal RAG 仅得 32 分
- Gen research/review 有自反射（72/68分）

v9.0 策略：
- 对 ALL Gen 任务应用自反射（包括 code）
- 使用代码专用 critique prompt（不同于 research/review）
- Hypothesis：代码任务在陌生领域同样需要自反射来提升完整性

变化：
- should_reflect(): 对所有 Gen 任务应用自反射（不仅是 research/review）
- 添加代码专用的 SELF_CRITIQUE_PROMPT_CODE
"""

import json
import time
import os
import sys
import urllib.request
from dataclasses import dataclass
from typing import Dict, List

API_CONFIG = {
    "base_url": "https://api.minimaxi.com/anthropic",
    "model": "MiniMax-M2.7"
}

CHECKPOINT_FILE = "v9_0_ext_checkpoint.json"
RESULTS_FILE = "benchmark_results_v9_0_ext.json"

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


# Prompts
COT_RESEARCH_PROMPT = """你是一个专业的技术分析师。请深入分析以下研究任务。

任务：{query}

请按以下Chain-of-Thought格式输出：
1. 问题诊断：先明确核心问题
2. 深度分析：分解问题，包含具体数字和案例
3. 技术方案：给出可操作的解决方案
4. 数字证据：引用具体数据支持分析
5. 验证方法：说明如何验证方案有效性

要求：有深度，有具体数字，有可操作性。"""

V23_CODE_PROMPT = """你是一个专业的技术分析师。

任务类型：{task_type}
任务：{query}

根据任务类型，选择最合适的输出格式：

**code**: 架构简图 → 核心代码（完整可运行）→ 测试用例 → 配置说明
**review**: 风险矩阵 → 影响分析 → 缓解步骤 → 优先级 → 验证方法

要求：
- 有具体数字和证据
- 有可操作的步骤
- 有验证方法
- 代码必须可运行

直接输出你的完整分析。"""

# Research/Review 用的 critique prompt
SELF_CRITIQUE_PROMPT = """你是一个严格的技术评审专家。请评审以下输出，找出关键问题：

任务类型：{task_type}
任务：{query}

当前输出：
{output}

请严格指出最多2个最重要的问题：

输出格式：
问题1: [描述]
改进1: [具体怎么做]
问题2: ...
"""

# Code 专用的 critique prompt - 更注重完整性和可运行性
SELF_CRITIQUE_PROMPT_CODE = """你是一个严格的代码评审专家。请评审以下代码输出，找出关键问题：

任务：{query}

当前输出：
{output}

请严格指出最多2个最重要的问题（重点关注代码完整性和可运行性）：

输出格式：
问题1: [描述]
改进1: [具体怎么做]
问题2: ...
"""

REVISION_PROMPT = """你是一个专业的技术分析师。请根据评审意见改进你的输出：

任务类型：{task_type}
任务：{query}

之前的输出：
{output}

评审意见：
{critique}

请输出改进后的完整版本。"""

REVISION_PROMPT_CODE = """你是一个专业的技术分析师。请根据评审意见改进你的代码输出：

任务：{query}

之前的输出：
{output}

评审意见：
{critique}

请输出改进后的完整代码版本。"""

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


class HarnessV90Extended:
    def __init__(self, api_key: str):
        self.llm = RealLLMCaller(api_key)
        self.api_key = api_key
    
    def get_prompt_for_task(self, task: Dict) -> tuple:
        """Return (system_prompt, prompt) based on task type"""
        task_type = task["type"]
        query = task["query"]
        
        if task_type == "research":
            return (COT_RESEARCH_PROMPT.format(query=query), f"任务类型：{task_type}\n任务：{query}")
        else:
            return (V23_CODE_PROMPT.format(task_type=task_type, query=query), f"任务类型：{task_type}\n任务：{query}")
    
    def should_reflect(self, task_type: str, is_gen: bool) -> bool:
        """
        v9.0 关键变化：对 ALL Gen 任务应用自反射（包括 code）
        
        v8.0 策略：只对 Gen research/review 应用自反射
        v9.0 策略：对所有 Gen 任务应用自反射
        
        Hypothesis：代码任务在陌生领域（Gen）同样需要自反射来提升完整性
        """
        return is_gen  # All Gen tasks get reflection now
    
    def get_critique_prompt(self, task_type: str) -> str:
        """Get appropriate critique prompt based on task type"""
        if task_type == "code":
            return SELF_CRITIQUE_PROMPT_CODE
        return SELF_CRITIQUE_PROMPT
    
    def get_revision_prompt(self, task_type: str) -> str:
        """Get appropriate revision prompt based on task type"""
        if task_type == "code":
            return REVISION_PROMPT_CODE
        return REVISION_PROMPT
    
    def execute_task(self, task: Dict) -> TaskResult:
        task_id = task["id"]
        task_type = task["type"]
        query = task["query"]
        is_gen = task_id.startswith("gen_")
        
        executor_start = time.time()
        max_tokens = 3000 if task_type == "code" else 2500
        
        system_prompt, prompt = self.get_prompt_for_task(task)
        
        # Step 1: Initial response
        initial_response = self.llm.call_with_retry(
            prompt=prompt,
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
        
        # Step 2: Self-reflection for ALL Gen tasks (including code)
        iterations = 1
        if self.should_reflect(task_type, is_gen):
            critique_prompt = self.get_critique_prompt(task_type)
            revision_prompt = self.get_revision_prompt(task_type)
            
            critique_response = self.llm.call_with_retry(
                prompt=critique_prompt.format(
                    task_type=task_type, query=query, output=current_output
                ),
                system_prompt="你是一个严格的评审专家。",
                max_tokens=1000
            )
            total_tokens += critique_response.get("output_tokens", 0)
            critique_text = critique_response["content"]
            
            has_issues = len(critique_text) > 80 and "问题" in critique_text
            if has_issues and not critique_response.get("error"):
                revision_response = self.llm.call_with_retry(
                    prompt=revision_prompt.format(
                        task_type=task_type, query=query,
                        output=current_output, critique=critique_text
                    ),
                    system_prompt="你是一个专业的技术分析师。",
                    max_tokens=max_tokens
                )
                total_tokens += revision_response.get("output_tokens", 0)
                if not revision_response.get("error"):
                    current_output = revision_response["content"]
                    iterations = 2
        
        executor_latency = (time.time() - executor_start) * 1000
        
        # Step 3: Evaluate
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
        except:
            quality_score = 50
            depth_score = completeness_score = actionability_score = 3
        
        return TaskResult(
            task_id=task_id, task_type=task_type,
            executor_output=current_output, quality_score=quality_score,
            depth_score=depth_score, completeness_score=completeness_score,
            actionability_score=actionability_score,
            executor_tokens=total_tokens, evaluator_tokens=evaluator_tokens,
            executor_latency_ms=executor_latency, evaluator_latency_ms=evaluator_latency,
            iterations=iterations
        )
    
    def run_benchmark(self) -> Dict:
        # STANDARD tasks - Core from tasks_v2.py
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
            # STANDARD Gen tasks from tasks_v2.py
            {"id": "gen_001", "type": "research", "difficulty": 8,
             "query": "分析量子计算在组合优化问题中的实际应用前景与挑战"},
            {"id": "gen_002", "type": "code", "difficulty": 9,
             "query": "实现一个自适应调度的线程池，支持基于负载的动态扩容和缩容"},
            {"id": "gen_003", "type": "review", "difficulty": 8,
             "query": "评估区块链技术在供应链溯源场景中的适用性和潜在风险"},
            {"id": "gen_004", "type": "research", "difficulty": 9,
             "query": "调研联邦学习在医疗数据隐私保护中的最新进展"},
            {"id": "gen_005", "type": "code", "difficulty": 8,
             "query": "设计一个多模态 RAG 系统，融合文本、图像和表格进行智能问答"},
        ]
        
        results = []
        start_time = time.time()
        
        # Load checkpoint if exists
        checkpoint = self.load_checkpoint()
        completed = set(checkpoint.get("tasks_completed", []))
        
        for task in tasks:
            task_id = task["id"]
            if task_id in completed:
                print(f"[{task_id}] Already completed, skipping")
                continue
            
            print(f"[{task_id}] Running ({task['type']})...", end=" ", flush=True)
            result = self.execute_task(task)
            results.append(result)
            
            # Save checkpoint after each task
            completed.add(task_id)
            checkpoint["tasks_completed"] = list(completed)
            checkpoint["results"] = [self.result_to_dict(r) for r in results]
            self.save_checkpoint(checkpoint)
            
            reflect_mark = " [REFLECT]" if result.iterations > 1 else ""
            print(f"Score: {result.quality_score}{reflect_mark}")
        
        elapsed = time.time() - start_time
        
        # Compute summary
        summary = self.compute_summary(results, elapsed)
        
        return {
            "harness_version": "v9.0-extended",
            "paradigm": "Extended Self-Reflection for ALL Gen Tasks",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "elapsed_seconds": elapsed,
            "summary": summary,
            "individual_results": [self.result_to_dict(r) for r in results]
        }
    
    def result_to_dict(self, r: TaskResult) -> Dict:
        return {
            "task_id": r.task_id,
            "task_type": r.task_type,
            "executor_output": r.executor_output[:500] if r.executor_output else "",
            "quality_score": r.quality_score,
            "depth_score": r.depth_score,
            "completeness_score": r.completeness_score,
            "actionability_score": r.actionability_score,
            "executor_tokens": r.executor_tokens,
            "evaluator_tokens": r.evaluator_tokens,
            "executor_latency_ms": r.executor_latency_ms,
            "evaluator_latency_ms": r.evaluator_latency_ms,
            "is_suspicious": r.is_suspicious,
            "error": r.error,
            "iterations": r.iterations
        }
    
    def compute_summary(self, results: List[TaskResult], elapsed: float) -> Dict:
        total = len(results)
        core_results = [r for r in results if not r.task_id.startswith("gen_")]
        gen_results = [r for r in results if r.task_id.startswith("gen_")]
        
        core_avg = sum(r.quality_score for r in core_results) / len(core_results) if core_results else 0
        gen_avg = sum(r.quality_score for r in gen_results) / len(gen_results) if gen_results else 0
        
        # Gen code specific
        gen_code = [r for r in gen_results if r.task_type == "code"]
        gen_research = [r for r in gen_results if r.task_type == "research"]
        gen_review = [r for r in gen_results if r.task_type == "review"]
        
        gen_code_avg = sum(r.quality_score for r in gen_code) / len(gen_code) if gen_code else 0
        gen_research_avg = sum(r.quality_score for r in gen_research) / len(gen_research) if gen_research else 0
        
        total_tokens = sum(r.executor_tokens for r in results)
        avg_latency = sum(r.executor_latency_ms + r.evaluator_latency_ms for r in results) / total if total > 0 else 0
        
        avg_actionability = sum(r.actionability_score for r in results) / total if total > 0 else 0
        
        # Composite: same formula as v8.0
        composite = core_avg * 0.45 + gen_avg * 0.45 + (avg_actionability * 10) * 0.1
        
        return {
            "total_tasks": total,
            "core_avg_score": core_avg,
            "gen_avg_score": gen_avg,
            "gen_code_avg_score": gen_code_avg,
            "gen_research_avg_score": gen_research_avg,
            "avg_actionability_level": avg_actionability,
            "total_executor_tokens": total_tokens,
            "avg_latency_ms": avg_latency,
            "composite_score": composite,
            "gen_tasks_with_reflection": sum(1 for r in gen_results if r.iterations > 1)
        }
    
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


def main():
    api_key = os.environ.get("MINIMAX_API_KEY", "")
    if not api_key:
        import re
        with open('harness_v12_0.py', 'r') as f:
            content = f.read()
        match = re.search(r'api_key = "([^"]+)"', content)
        if match:
            api_key = match.group(1)
        else:
            print("Error: MINIMAX_API_KEY not set and could not find backup")
            sys.exit(1)
    
    harness = HarnessV90Extended(api_key)
    print(f"Starting v9.0 (Extended Self-Reflection for ALL Gen Tasks)...")
    print(f"Strategy: All Gen tasks (including code) get self-reflection")
    print()
    
    results = harness.run_benchmark()
    
    with open(RESULTS_FILE, 'w') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'='*60}")
    print(f"BENCHMARK COMPLETE")
    print(f"{'='*60}")
    print(f"Composite: {results['summary']['composite_score']:.2f}")
    print(f"Core avg: {results['summary']['core_avg_score']:.2f}")
    print(f"Gen avg: {results['summary']['gen_avg_score']:.2f}")
    print(f"Gen code avg: {results['summary']['gen_code_avg_score']:.2f}")
    print(f"Gen research avg: {results['summary']['gen_research_avg_score']:.2f}")
    print(f"Actionability: {results['summary']['avg_actionability_level']:.2f}")
    print(f"Gen tasks with reflection: {results['summary']['gen_tasks_with_reflection']}")
    print(f"\nResults saved to: {RESULTS_FILE}")
    
    # Compare with v8.0
    print(f"\n--- Comparison with v8.0 ---")
    print(f"v8.0: Composite=55.58, Gen=57.4, Gen_code=49.5")
    print(f"v9.0: Composite={results['summary']['composite_score']:.2f}, Gen={results['summary']['gen_avg_score']:.2f}, Gen_code={results['summary']['gen_code_avg_score']:.2f}")


if __name__ == "__main__":
    main()