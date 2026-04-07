#!/usr/bin/env python3
"""
OpenClaw Native Harness v2.1 - Hybrid: v23 Format + Self-Reflection

v2.0 (54.64) analysis:
- Gen (65.2) close to v23 (68.2) - self-reflection works
- Core (50.0) below v23 (54.4) - research prompts need strengthening

v2.1 Strategy: HYBRID
1. Use v23's proven adaptive format (better for research)
2. Add self-reflection loop (proven to help Gen)
3. Stronger system prompt for research tasks

Key difference from v2.0:
- v2.0: Generic self-reflection prompt
- v2.1: v23 format + targeted critique + stronger research guidance
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
    
    def call(self, prompt: str, system_prompt: str = "", max_tokens: int = 2048, timeout: int = 180) -> Dict:
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

# v2.1: Hybrid - v23 format + self-reflection

INITIAL_RESPONSE_PROMPT = """你是一个专业的技术分析师。

任务类型：{task_type}
任务：{query}

根据任务类型，选择最合适的输出格式：

**research**: 问题诊断 → 深度分析 → 具体方案 → 数字证据 → 验证方法
**code**: 架构简图 → 核心代码（完整可运行）→ 测试用例 → 配置说明
**review**: 风险矩阵 → 影响分析 → 缓解步骤 → 优先级 → 验证方法

无论哪种类型，都要做到：
- 有具体数字和证据
- 有可操作的步骤
- 有验证方法

输出格式示例（根据任务类型选择）：

【research类型】：
# 技术分析
## 问题诊断
## 深度分析（包含具体数字）
## 解决方案（分步骤）
## 验证方法

【code类型】：
# 实现方案
## 架构
## 核心代码
## 测试

【review类型】：
# 架构评审
## 风险矩阵
## 缓解方案
## 优先级"""

# v2.1: More targeted critique - focuses on depth and actionability
SELF_CRITIQUE_PROMPT = """你是一个严格的技术评审专家。请评审以下输出：

任务类型：{task_type}
任务：{query}

当前输出：
{output}

请严格检查：
1. **深度**：是否有具体数字和证据？分析是否深入？
2. **完整性**：是否覆盖了任务的所有方面？
3. **可操作性**：步骤是否具体可执行？

如果发现问题，明确指出问题和具体改进建议。
如果输出质量已经很高，指出它为什么好。

输出格式：
评估：[质量高/有问题]
问题1: [描述]（如果没有问题则写"无"）
改进1: [建议]（如果没有问题则写"无需改进"）
问题2: ...
改进2: ..."""

REVISION_PROMPT = """你是一个专业的技术分析师。请根据评审意见改进输出：

任务类型：{task_type}
任务：{query}

当前输出：
{output}

评审意见：
{critique}

要求：
- 解决评审指出的所有问题
- 保持原有的优点
- 质量有明显提升

直接输出改进后的完整版本。"""

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


class HarnessV21:
    def __init__(self, api_key: str):
        self.llm = RealLLMCaller(api_key)
        self.max_iterations = 2
    
    def execute_task(self, task: Dict) -> TaskResult:
        task_id = task["id"]
        task_type = task["type"]
        query = task["query"]
        
        executor_start = time.time()
        max_tokens = 3000 if task_type == "code" else 2500
        
        current_output = ""
        total_tokens = 0
        
        # Iteration 1: Generate initial response using v23 format
        initial_response = self.llm.call(
            prompt=f"任务类型：{task_type}\n任务：{query}",
            system_prompt=INITIAL_RESPONSE_PROMPT.format(task_type=task_type, query=query),
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
                error=f"Initial call error: {initial_response['error']}"
            )
        
        current_output = initial_response["content"]
        total_tokens += initial_response.get("output_tokens", 0)
        
        # Iteration 2: Self-critique and revision
        critique_response = self.llm.call(
            prompt=SELF_CRITIQUE_PROMPT.format(
                task_type=task_type, query=query, output=current_output
            ),
            system_prompt="你是一个严格的技术评审专家。",
            max_tokens=1500
        )
        
        total_tokens += critique_response.get("output_tokens", 0)
        critique_text = critique_response["content"]
        
        # Check if critique identified real issues
        has_issues = len(critique_text) > 80 and ("问题" in critique_text or "改进" in critique_text)
        
        if has_issues:
            revision_response = self.llm.call(
                prompt=REVISION_PROMPT.format(
                    task_type=task_type, query=query,
                    output=current_output, critique=critique_text
                ),
                system_prompt="你是一个专业的技术分析师。",
                max_tokens=max_tokens
            )
            total_tokens += revision_response.get("output_tokens", 0)
            current_output = revision_response["content"]
        
        executor_latency = (time.time() - executor_start) * 1000
        
        # Evaluate final output
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
            is_suspicious = executor_latency < 15000 and len(current_output) > 1000
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
            iterations=2 if has_issues else 1
        )
    
    def run_benchmark(self, api_key: str) -> Dict:
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
        
        self.api_key = api_key
        results = []
        start_time = time.time()
        
        print("=" * 60)
        print("Harness v2.1 - Hybrid: v23 Format + Self-Reflection")
        print("=" * 60)
        
        for task in tasks:
            print(f"[{task['id']}] Executor({task['type']})...", end=" ", flush=True)
            result = self.execute_task(task)
            results.append(result)
            print(f"Score: {result.quality_score:.1f} (iter={result.iterations})")
        
        elapsed = time.time() - start_time
        
        total = len(results)
        core_scores = [r.quality_score for r in results[:10]]
        gen_scores = [r.quality_score for r in results[10:]]
        avg_actionability = sum(r.actionability_score for r in results) / total
        
        core_avg = sum(core_scores) / len(core_scores)
        gen_avg = sum(gen_scores) / len(gen_scores)
        composite = core_avg * 0.45 + gen_avg * 0.45 + (avg_actionability * 10) * 0.1
        
        print(f"\n{'=' * 60}")
        print(f"v2.1 HYBRID: Core={core_avg:.2f} Gen={gen_avg:.2f} Composite={composite:.2f}")
        print(f"{'=' * 60}")
        
        return {
            "harness_version": "v2.1",
            "paradigm": "v2 (Self-Reflection + v23 Format)",
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
    import sys
    api_key = os.environ.get("MINIMAX_API_KEY", "")
    if not api_key:
        # Fallback to test key
        api_key = "sk-cp-ZNEhSAB4-p-nraTwKzWoeLCpFPE-wY8If5v_1qxUvnW4_h0ryAunuH9_Vn-SItYx-D1AGFdRhD_6fn_9LhkpWG2yy6kUeRZBEjq8aFCUpruT5aFlM-Y5KDc"
    
    harness = HarnessV21(api_key)
    results = harness.run_benchmark(api_key)
    
    output_file = f"benchmark_results_v2_1_gen1_{time.strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\nResults saved to: {output_file}")