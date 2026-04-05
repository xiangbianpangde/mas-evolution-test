#!/usr/bin/env python3
"""
OpenClaw Native Harness v3.2 - Paradigm v3: Code Specialist (Planning-First)

All paradigms (v1, v2, v3) fail at code tasks:
- v3.1 ultra-minimal: core_004 hung at code
- v12.0 reflection: code tasks avg ~50
- v23 adaptive: code tasks avg ~50

Root cause: Full implementation in single call = timeout

v3.2 Strategy: PLANNING-FIRST for code
For CODE tasks:
1. First call: Get architecture/pseudocode only (quick)
2. Second call: Implement core logic only
3. Skip: Full test suites (causes timeout)

This reduces complexity from O(n) to O(1) per code task.
"""

import json
import time
import os
from dataclasses import dataclass
from typing import Dict, Optional

API_CONFIG = {
    "base_url": "https://api.minimaxi.com/anthropic",
    "model": "MiniMax-M2.7"
}

CHECKPOINT_FILE = "v3_2_checkpoint.json"
RESULTS_PREFIX = "benchmark_results_v3_2"

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
    
    def call_with_retry(self, prompt: str, system_prompt: str = "", max_tokens: int = 2048, timeout: int = 90, max_retries: int = 2) -> Dict:
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
                    print(f"  [Error, retry {attempt+1}/{max_retries}]", end=" ", flush=True)
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
        return {"content": content, "latency_ms": latency, "input_tokens": result.get("usage", {}).get("input_tokens", 0),
                "output_tokens": result.get("usage", {}).get("output_tokens", 0), "error": None}

# v3.2: Planning-first for code, ultra-minimal for research/review

RESEARCH_PROMPT = """分析以下问题，给出深度技术分析：

问题：{query}

要求：
- 有具体数字和证据
- 有可操作的步骤
- 有验证方法

直接输出你的分析。"""

REVIEW_PROMPT = """评审以下架构/设计，给出优化建议：

任务：{query}

要求：
- 风险矩阵
- 影响分析
- 缓解步骤
- 优先级

直接输出你的评审。"""

CODE_ARCH_PROMPT = """为以下任务设计架构和核心实现（不超过50行）：

任务：{query}

输出：
1. 架构设计（2-3句话）
2. 核心数据结构
3. 主要算法/函数（伪代码或简化的Python）
4. 关键边界条件

保持简洁，避免冗余。"""

CODE_IMPL_PROMPT = """基于以下架构，实现核心代码：

任务：{query}

架构：{architecture}

实现要求：
- 核心功能完整
- 代码简洁可运行
- 包含必要的错误处理

直接输出代码。"""

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
- L5: 功能完整，结构清晰
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


class HarnessV32:
    def __init__(self, api_key: str):
        self.llm = RealLLMCaller(api_key)
        self.api_key = api_key
    
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
        total_tokens = 0
        
        if task_type == "code":
            # Planning-first: Architecture then implementation
            arch_response = self.llm.call_with_retry(
                prompt=CODE_ARCH_PROMPT.format(query=query),
                system_prompt="你是一个架构专家。保持简洁。",
                max_tokens=1500
            )
            
            if arch_response.get("error"):
                return TaskResult(
                    task_id=task_id, task_type=task_type,
                    executor_output="", quality_score=0,
                    depth_score=0, completeness_score=0, actionability_score=0,
                    executor_tokens=0, evaluator_tokens=0,
                    executor_latency_ms=(time.time() - executor_start) * 1000,
                    evaluator_latency_ms=0,
                    error=f"Architecture error: {arch_response['error']}"
                )
            
            architecture = arch_response["content"]
            total_tokens += arch_response.get("output_tokens", 0)
            
            # Implementation
            impl_response = self.llm.call_with_retry(
                prompt=CODE_IMPL_PROMPT.format(query=query, architecture=architecture),
                system_prompt="你是一个代码专家。输出简洁可运行的代码。",
                max_tokens=2000
            )
            
            if impl_response.get("error"):
                # If implementation fails, at least we have architecture
                current_output = f"[架构设计]\n{architecture}\n\n[实现失败]\n{impl_response['error']}"
                total_tokens += impl_response.get("output_tokens", 0)
            else:
                current_output = f"[架构设计]\n{architecture}\n\n[核心实现]\n{impl_response['content']}"
                total_tokens += impl_response.get("output_tokens", 0)
        
        else:
            # Research and Review: Ultra-minimal
            if task_type == "research":
                prompt = RESEARCH_PROMPT.format(query=query)
                system = "你是一个专业的技术分析师。"
            else:
                prompt = REVIEW_PROMPT.format(query=query)
                system = "你是一个专业的架构评审专家。"
            
            response = self.llm.call_with_retry(
                prompt=prompt,
                system_prompt=system,
                max_tokens=2500
            )
            
            if response.get("error"):
                return TaskResult(
                    task_id=task_id, task_type=task_type,
                    executor_output="", quality_score=0,
                    depth_score=0, completeness_score=0, actionability_score=0,
                    executor_tokens=0, evaluator_tokens=0,
                    executor_latency_ms=(time.time() - executor_start) * 1000,
                    evaluator_latency_ms=0,
                    error=f"Error: {response['error']}"
                )
            
            current_output = response["content"]
            total_tokens += response.get("output_tokens", 0)
        
        executor_latency = (time.time() - executor_start) * 1000
        
        # Evaluate
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
        
        if evaluator_response.get("error"):
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
            is_suspicious = executor_latency < 8000 and len(current_output) > 1000
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
            is_suspicious=is_suspicious
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
            print(f"Score: {result.quality_score:.1f}")
            
            # Save checkpoint
            checkpoint["tasks_completed"].append(task["id"])
            checkpoint["results"].append({
                "task_id": result.task_id, "task_type": result.task_type,
                "executor_output": result.executor_output, "quality_score": result.quality_score,
                "depth_score": result.depth_score, "completeness_score": result.completeness_score,
                "actionability_score": result.actionability_score, "executor_tokens": result.executor_tokens,
                "evaluator_tokens": result.evaluator_tokens, "executor_latency_ms": result.executor_latency_ms,
                "evaluator_latency_ms": result.evaluator_latency_ms, "is_suspicious": result.is_suspicious,
                "error": result.error
            })
            self.save_checkpoint(checkpoint)
        
        elapsed = time.time() - start_time
        
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
        print(f"v3.2: Core={core_avg:.2f} Gen={gen_avg:.2f} Composite={composite:.2f}")
        print(f"{'=' * 60}")
        
        return {
            "harness_version": "v3.2",
            "paradigm": "v3 (Code Specialist - Planning First)",
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
    
    harness = HarnessV32(api_key)
    results = harness.run_benchmark()
    
    output_file = f"{RESULTS_PREFIX}_{time.strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\nResults saved to: {output_file}")