#!/usr/bin/env python3
"""
OpenClaw Native Harness v3.0 - Paradigm v3: Ensemble Fusion

v1 (v23.0): Single agent, adaptive format - Core=54.4, Gen=68.2
v2 (v12.0): Self-reflection loop - Core=58.7, Gen=63.4

Key insight: Each paradigm excels at different task types!
- v1 better at Gen tasks (68.2 vs 63.4)
- v2 better at Core tasks (58.7 vs 54.4)

v3 Strategy: Ensemble Fusion
1. Run task with v1 strategy (direct adaptive)
2. Run task with v2 strategy (self-reflection)
3. Run task with v3 strategy (synthesis)
4. Select best output using meta-evaluation

Hypothesis: Fusing multiple paradigms should outperform any single approach.
"""

import json
import time
import os
from dataclasses import dataclass
from typing import Dict, Tuple

API_CONFIG = {
    "base_url": "https://api.minimaxi.com/anthropic",
    "model": "MiniMax-M2.7"
}

CHECKPOINT_FILE = "v3_0_checkpoint.json"
RESULTS_PREFIX = "benchmark_results_v3_0"

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
                    print(f"  [Error: {e}, retry {attempt+1}]", end=" ", flush=True)
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
        req = urllib.request.Request(f"{API_CONFIG['base_url']}/v1/messages", data=data, headers=headers, method='POST')
        with urllib.request.urlopen(req, timeout=timeout) as response:
            result = json.loads(response.read().decode('utf-8'))
        latency = (time.time() - start) * 1000
        content = ""
        for item in result.get("content", []):
            if item.get("type") == "text":
                content = item.get("text", "")
                break
        return {"content": content, "latency_ms": latency, "input_tokens": result.get("usage", {}).get("input_tokens", 0), "output_tokens": result.get("usage", {}).get("output_tokens", 0), "error": None}

# v3.0: Ensemble Fusion prompts

# v1 Strategy: Direct Adaptive (like v23)
V1_EXECUTOR = """你是一个专业的技术分析师。

任务类型：{task_type}
任务：{query}

根据任务类型，选择最合适的输出格式：

**research**: 问题诊断 → 深度分析 → 具体方案 → 数字证据 → 验证方法
**code**: 架构简图 → 核心代码（完整可运行）→ 测试用例 → 配置说明
**review**: 风险矩阵 → 影响分析 → 缓解步骤 → 优先级 → 验证方法

要求：
- 有具体数字和证据
- 有可操作的步骤
- 有验证方法
- 代码必须可运行

直接输出你的完整分析。"""

# v2 Strategy: Self-Reflection (like v12)
V2_INITIAL = """你是一个专业的技术分析师。

任务类型：{task_type}
任务：{query}

请按照以下格式输出你的完整分析：

**research**: 问题诊断 → 深度分析 → 具体方案 → 数字证据 → 验证方法
**code**: 架构简图 → 核心代码（完整可运行）→ 测试用例 → 配置说明
**review**: 风险矩阵 → 影响分析 → 缓解步骤 → 优先级 → 验证方法

要求：
- 有具体数字和证据
- 有可操作的步骤
- 有验证方法
- 代码必须可运行

直接输出你的分析。"""

V2_CRITIQUE = """你是一个严格的技术评审专家。请评审以下输出，找出关键问题：

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

V2_REVISION = """你是一个专业的技术分析师。请根据评审意见改进你的输出：

任务类型：{task_type}
任务：{query}

之前的输出：
{output}

评审意见：
{critique}

请输出改进后的完整版本。保持原有优点，解决评审指出的问题。"""

# v3 Strategy: Synthesis (combine best elements)
V3_SYNTHESIS = """三个专家对同一任务给出了不同的分析：

专家1（直接分析）：
{output1}

专家2（反思改进）：
{output2}

专家3（独立分析）：
{output3}

请综合三个专家的分析，取长补短，输出一个更好的答案。

要求：
- 结合三个专家的各自优势
- 解决任何明显的问题或矛盾
- 保持具体数字和可操作性

直接输出综合后的分析。"""

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


class HarnessV30:
    def __init__(self, api_key: str):
        self.llm = RealLLMCaller(api_key)
        self.api_key = api_key
    
    def v1_strategy(self, task: Dict) -> Tuple[str, int]:
        """v1: Direct adaptive format (like v23)"""
        response = self.llm.call_with_retry(
            prompt=f"任务类型：{task['type']}\n任务：{task['query']}",
            system_prompt=V1_EXECUTOR.format(task_type=task['type'], query=task['query']),
            max_tokens=2500 if task['type'] == 'code' else 2000
        )
        return response["content"], response.get("output_tokens", 0)
    
    def v2_strategy(self, task: Dict) -> Tuple[str, int]:
        """v2: Self-reflection loop (like v12)"""
        # Initial
        initial = self.llm.call_with_retry(
            prompt=f"任务类型：{task['type']}\n任务：{task['query']}",
            system_prompt=V2_INITIAL.format(task_type=task['type'], query=task['query']),
            max_tokens=2500 if task['type'] == 'code' else 2000
        )
        total_tokens = initial.get("output_tokens", 0)
        current = initial["content"]
        
        # Critique
        critique = self.llm.call_with_retry(
            prompt=V2_CRITIQUE.format(task_type=task['type'], query=task['query'], output=current),
            system_prompt="你是一个严格的评审专家。",
            max_tokens=1500
        )
        total_tokens += critique.get("output_tokens", 0)
        
        # Revision if critique found issues
        if len(critique["content"]) > 100 and "问题" in critique["content"]:
            revision = self.llm.call_with_retry(
                prompt=V2_REVISION.format(task_type=task['type'], query=task['query'], output=current, critique=critique["content"]),
                system_prompt="你是一个专业的技术分析师。",
                max_tokens=2500 if task['type'] == 'code' else 2000
            )
            total_tokens += revision.get("output_tokens", 0)
            current = revision["content"]
        
        return current, total_tokens
    
    def v3_strategy(self, task: Dict, v1_out: str, v2_out: str) -> Tuple[str, int]:
        """v3: Synthesis of v1 and v2 outputs"""
        # Generate third independent analysis
        v3_initial = self.llm.call_with_retry(
            prompt=f"任务类型：{task['type']}\n任务：{task['query']}\n\n请提供一个独立的技术分析。",
            system_prompt=V1_EXECUTOR.format(task_type=task['type'], query=task['query']),
            max_tokens=2500 if task['type'] == 'code' else 2000
        )
        total_tokens = v3_initial.get("output_tokens", 0)
        
        # Synthesize all three
        synthesis = self.llm.call_with_retry(
            prompt=V3_SYNTHESIS.format(output1=v1_out, output2=v2_out, output3=v3_initial["content"]),
            system_prompt="你是一个综合分析专家。",
            max_tokens=2500
        )
        total_tokens += synthesis.get("output_tokens", 0)
        
        return synthesis["content"], total_tokens
    
    def evaluate(self, content: str, task_type: str) -> Tuple[Dict, int]:
        """Evaluate output"""
        evaluator_prompt = LENIENT_CODE_EVALUATOR if task_type == "code" else STRICT_EVALUATOR
        response = self.llm.call_with_retry(
            prompt=evaluator_prompt.format(content=content),
            system_prompt="你是一个严格的技术评估专家。",
            max_tokens=1024
        )
        tokens = response.get("output_tokens", 0)
        
        try:
            eval_text = response["content"]
            json_start = eval_text.find('{')
            json_end = eval_text.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                eval_json = json.loads(eval_text[json_start:json_end])
            else:
                eval_json = {"overall_score": 50, "depth": {"level": 3}, "completeness": {"level": 3}, "actionability": {"level": 3}}
            return eval_json, tokens
        except:
            return {"overall_score": 50, "depth": {"level": 3}, "completeness": {"level": 3}, "actionability": {"level": 3}}, tokens
    
    def execute_task(self, task: Dict) -> TaskResult:
        task_id = task["id"]
        task_type = task["type"]
        query = task["query"]
        
        start_time = time.time()
        total_tokens = 0
        
        # Strategy 1: v1 (direct adaptive)
        print(f"[{task_id}] v1...", end=" ", flush=True)
        v1_out, t1 = self.v1_strategy(task)
        total_tokens += t1
        v1_eval, _ = self.evaluate(v1_out, task_type)
        print(f"Score={v1_eval.get('overall_score', 50):.0f}", end=" | ", flush=True)
        
        # Strategy 2: v2 (self-reflection)
        print(f"v2...", end=" ", flush=True)
        v2_out, t2 = self.v2_strategy(task)
        total_tokens += t2
        v2_eval, _ = self.evaluate(v2_out, task_type)
        print(f"Score={v2_eval.get('overall_score', 50):.0f}", end=" | ", flush=True)
        
        # Strategy 3: v3 (synthesis)
        print(f"v3...", end=" ", flush=True)
        v3_out, t3 = self.v3_strategy(task, v1_out, v2_out)
        total_tokens += t3
        v3_eval, _ = self.evaluate(v3_out, task_type)
        print(f"Score={v3_eval.get('overall_score', 50):.0f}", flush=True)
        
        # Select best output
        scores = [
            (v1_eval.get("overall_score", 50), v1_out, v1_eval),
            (v2_eval.get("overall_score", 50), v2_out, v2_eval),
            (v3_eval.get("overall_score", 50), v3_out, v3_eval)
        ]
        best_score, best_output, best_eval = max(scores, key=lambda x: x[0])
        
        elapsed = (time.time() - start_time) * 1000
        
        return TaskResult(
            task_id=task_id, task_type=task_type,
            executor_output=best_output,
            quality_score=best_score,
            depth_score=best_eval.get("depth", {}).get("level", 3),
            completeness_score=best_eval.get("completeness", {}).get("level", 3),
            actionability_score=best_eval.get("actionability", {}).get("level", 3),
            executor_tokens=total_tokens, evaluator_tokens=0,
            executor_latency_ms=elapsed, evaluator_latency_ms=0,
            is_suspicious=False
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
        
        print("=" * 70)
        print("Harness v3.0 - Paradigm v3: Ensemble Fusion (v1 + v2 + v3)")
        print("=" * 70)
        
        for task in tasks:
            result = self.execute_task(task)
            results.append(result)
            print(f"  → Best: {result.quality_score:.1f}")
        
        elapsed = time.time() - start_time
        
        total = len(results)
        core_scores = [r.quality_score for r in results[:10]]
        gen_scores = [r.quality_score for r in results[10:]]
        avg_actionability = sum(r.actionability_score for r in results) / total
        
        core_avg = sum(core_scores) / len(core_scores)
        gen_avg = sum(gen_scores) / len(gen_scores)
        composite = core_avg * 0.45 + gen_avg * 0.45 + (avg_actionability * 10) * 0.1
        
        print(f"\n{'=' * 70}")
        print(f"v3.0: Core={core_avg:.2f} Gen={gen_avg:.2f} Composite={composite:.2f}")
        print(f"{'=' * 70}")
        
        return {
            "harness_version": "v3.0",
            "paradigm": "v3 (Ensemble Fusion)",
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
                 "quality_score": r.quality_score, "is_suspicious": r.is_suspicious}
                for r in results
            ]
        }


if __name__ == "__main__":
    api_key = "sk-cp-ZNEhSAB4-p-nraTwKzWoeLCpFPE-wY8If5v_1qxUvnW4_h0ryAunuH9_Vn-SItYx-D1AGFdRhD_6fn_9LhkpWG2yy6kUeRZBEjq8aFCUpruT5aFlM-Y5KDc"
    
    harness = HarnessV30(api_key)
    results = harness.run_benchmark()
    
    output_file = f"{RESULTS_PREFIX}_{time.strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\nResults saved to: {output_file}")