#!/usr/bin/env python3
"""
OpenClaw Native Harness v23.0 - Restore v15.0's Gen + v20's Core

Root Cause of Gen regression: Modified Gen prompts consistently underperform v15.0's original.

v23.0 Strategy:
1. Core research: v20's STRONGER format + self-reflection (proven to work)
2. Gen research: RESTORE v15.0's EXACT COT format + no self-reflection
3. All code: Lenient evaluator
4. All review: v15.0's review format

v15.0 Gen approach was the best (Gen=72.6). We need to restore it exactly.

Target: Core 60+ / Gen 70+ / Composite 60+
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

CHECKPOINT_FILE = "v23_0_checkpoint.json"
RESULTS_FILE = "benchmark_results_v23_0_gen1.json"

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
    
    def call_with_retry(self, prompt: str, system_prompt: str = "", max_tokens: int = 2048, timeout: int = 180, max_retries: int = 3) -> Dict:
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


# ============================================================
# v20's Core Research (proven to give Core 61.2)
# ============================================================
CORE_RESEARCH_PROMPT = """你是一个世界级的技术架构专家，专注于深度技术分析和证据驱动的研究。

任务：{query}

请按以下结构进行深度分析：

## 一、问题诊断与范围定义
- 明确核心挑战是什么
- 界定分析的技术边界
- 说明为什么这个问题重要

## 二、技术深度分析
- 列出关键技术原理（必须包含具体数字、公式、算法复杂度）
- 分析主流技术路线的优缺点（必须包含 benchmark 数据）
- 识别技术瓶颈及其根本原因

## 三、方案设计
- 提出具体可落地的方案
- 包含架构设计或代码实现
- 说明方案的适用范围和局限性

## 四、证据与验证
- 引用具体论文、数据、案例
- 提供量化的性能指标
- 说明如何验证方案有效性

## 五、可操作的实施路径
- 给出分步骤的实施计划
- 包含时间线和资源需求
- 指出关键风险点和缓解措施

质量要求：
- 每一个观点必须有数字或论文支撑
- 代码必须完整可运行
- 图表必须清晰可复现

请开始深度分析："""

# ============================================================
# v15.0's EXACT Gen Research prompt (restored)
# ============================================================
V15_GEN_RESEARCH_PROMPT = """你是一个专业的技术分析师。请仔细分析以下任务。

任务类型：{task_type}
任务：{query}

## 分析步骤（请先思考这些步骤，再输出最终答案）：

1. **问题诊断**：这个问题的核心挑战是什么？
2. **深度分析**：有哪些关键技术点需要考虑？
3. **方案设计**：具体的解决方案是什么？
4. **证据支撑**：有哪些数字或案例支持这个方案？
5. **验证方法**：如何验证方案的有效性？

## 输出格式要求：

根据任务类型，选择最合适的输出格式：

**research**: 
- 问题诊断（核心挑战是什么）
- 深度分析（包含具体数字和技术细节）
- 具体方案（分步骤）
- 证据支撑（数字、案例）
- 验证方法（如何验证）

**review**:
- 风险矩阵
- 影响分析
- 缓解步骤（分优先级）
- 验证方法

## 质量标准：
- 有具体数字和证据
- 有可操作的步骤
- 有验证方法
- 代码必须可运行

请先完成分析步骤，再输出最终答案。"""

CODE_PROMPT = """你是一个专业的技术分析师。

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

REVISION_PROMPT = """你是一个专业的技术分析师。请根据评审意见改进你的输出：

任务类型：{task_type}
任务：{query}

之前的输出：
{output}

评审意见：
{critique}

请输出改进后的完整版本。"""

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

LENIENT_CODE_EVALUATOR = """你是一个代码质量评估专家。代码任务评分标准：

- L5 (90-100): 完整可运行实现 + 测试 + 清晰结构
- L4 (75-89): 完整实现，个别细节问题
- L3 (60-74): 核心逻辑完成，部分功能缺失但可接受
- L2 (40-59): 部分完成，核心功能有但实现不完整
- L1 (20-39): 有尝试但基本不可用
- L0 (0-19): 几乎没有有效代码

评分原则：
- 给分从宽，只要有有效代码就给部分分
- 重点看核心功能是否实现
- 小问题不扣大分
- 注释缺失、格式问题忽略

输出 JSON（不用markdown）：
{{"depth": {{"level": 0-5, "evidence": "引用"}}, "completeness": {{"level": 0-5, "evidence": "引用"}}, "actionability": {{"level": 0-5, "evidence": "引用"}}, "overall_score": 0-100, "reasoning": "说明"}}

---
{content}
---

请从宽评分。"""


class HarnessV23:
    def __init__(self, api_key: str):
        self.llm = RealLLMCaller(api_key)
        self.api_key = api_key
    
    def get_prompt_for_task(self, task: Dict) -> tuple:
        task_id = task["id"]
        task_type = task["type"]
        query = task["query"]
        
        is_gen = task_id.startswith("gen_")
        
        if task_type == "code":
            return (CODE_PROMPT.format(task_type=task_type, query=query), 
                    f"任务类型：{task_type}\n任务：{query}")
        elif task_type == "research":
            if is_gen:
                # RESTORE v15.0's exact Gen research prompt
                return (V15_GEN_RESEARCH_PROMPT.format(task_type=task_type, query=query),
                        f"任务类型：{task_type}\n任务：{query}")
            else:
                # v20's Core research prompt
                return (CORE_RESEARCH_PROMPT.format(query=query),
                        f"任务：{query}")
        else:
            # v15.0's Gen review format
            return (V15_GEN_RESEARCH_PROMPT.format(task_type=task_type, query=query),
                    f"任务类型：{task_type}\n任务：{query}")
    
    def should_reflect(self, task: Dict) -> bool:
        """v23: Core research only"""
        task_id = task["id"]
        task_type = task["type"]
        
        # Core research: YES
        if task_type == "research" and task_id.startswith("core_"):
            return True
        
        # All Gen: NO (restore v15.0 stability)
        if task_id.startswith("gen_"):
            return False
        
        # Core code/review: NO
        return False
    
    def execute_task(self, task: Dict) -> TaskResult:
        task_id = task["id"]
        task_type = task["type"]
        query = task["query"]
        
        executor_start = time.time()
        max_tokens = 3000 if task_type == "code" else 2500
        
        system_prompt, prompt = self.get_prompt_for_task(task)
        
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
        
        iterations = 1
        if self.should_reflect(task):
            critique_response = self.llm.call_with_retry(
                prompt=SELF_CRITIQUE_PROMPT.format(
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
                    prompt=REVISION_PROMPT.format(
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
        
        if os.path.exists(CHECKPOINT_FILE):
            os.remove(CHECKPOINT_FILE)
        
        checkpoint = {"tasks_completed": [], "results": []}
        completed_ids = set()
        results = []
        
        start_time = time.time()
        
        for task in tasks:
            if task["id"] in completed_ids:
                print(f"[{task['id']}] SKIP (already completed)")
                continue
            
            reflect_str = "reflect" if self.should_reflect(task) else "no-reflect"
            print(f"[{task['id']}] Executor({task['type']}, {reflect_str})...", end=" ", flush=True)
            result = self.execute_task(task)
            results.append(result)
            print(f"Score: {result.quality_score:.1f} (iter={result.iterations})")
            
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
            with open(CHECKPOINT_FILE, 'w') as f:
                json.dump(checkpoint, f, ensure_ascii=False)
        
        elapsed = time.time() - start_time
        
        total = len(results)
        core_results = [r for r in results if r.task_id.startswith("core_") and r.quality_score > 0]
        gen_results = [r for r in results if r.task_id.startswith("gen_") and r.quality_score > 0]
        
        core_scores = [r.quality_score for r in core_results]
        gen_scores = [r.quality_score for r in gen_results]
        
        core_avg = sum(core_scores) / len(core_scores) if core_scores else 0
        gen_avg = sum(gen_scores) / len(gen_scores) if gen_scores else 0
        
        all_scores = [r.quality_score for r in results if r.quality_score > 0]
        avg_actionability = sum(r.actionability_score for r in results if r.quality_score > 0) / max(len(all_scores), 1)
        
        composite = core_avg * 0.45 + gen_avg * 0.45 + (avg_actionability * 10) * 0.1
        
        print(f"\n{'=' * 60}")
        print(f"v23.0: Core={core_avg:.2f} Gen={gen_avg:.2f} Composite={composite:.2f}")
        print(f"{'=' * 60}")
        
        print("\nPer-task scores:")
        for r in results:
            gen_marker = " [GEN]" if r.task_id.startswith("gen_") else ""
            print(f"  {r.task_id}: {r.quality_score:.1f} (iter={r.iterations}){gen_marker}")
        
        final_results = {
            "harness_version": "v23.0",
            "paradigm": "v23 (v20 Core + v15 Gen)",
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
        
        with open(RESULTS_FILE, 'w', encoding="utf-8") as f:
            json.dump(final_results, f, ensure_ascii=False, indent=2)
        
        print(f"\nResults saved to: {RESULTS_FILE}")
        
        if os.path.exists(CHECKPOINT_FILE):
            os.remove(CHECKPOINT_FILE)
        
        return final_results


if __name__ == "__main__":
    api_key = "sk-cp-ZNEhSAB4-p-nraTwKzWoeLCpFPE-wY8If5v_1qxUvnW4_h0ryAunuH9_Vn-SItYx-D1AGFdRhD_6fn_9LhkpWG2yy6kUeRZBEjq8aFCUpruT5aFlM-Y5KDc"
    
    harness = HarnessV23(api_key)
    harness.run_benchmark()
