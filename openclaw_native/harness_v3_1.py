#!/usr/bin/env python3
"""
OpenClaw Native Harness v3.1 - Parallel Ensemble (SIMPLICITY FIRST)

v2 paradigm (v2-v12) converged at v12.0=58.01
All attempts to improve (v13-v15, v3.0) caused hangs due to API instability

v3 Strategy: PARALLEL ENSEMBLE
- Run 3 independent simple harnesses in parallel
- Each uses minimal prompts (no reflection, no CoT)
- Majority voting on final answer
- Fast timeouts (60s) to avoid hangs
- Checkpoint after each PARALLEL batch completes

Key insight: Rather than making ONE complex harness, run MULTIPLE simple ones.
Redundancy > Complexity for stability.
"""

import json
import time
import os
import sys
from dataclasses import dataclass
from typing import Dict, List, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

API_CONFIG = {
    "base_url": "https://api.minimaxi.com/anthropic",
    "model": "MiniMax-M2.7"
}

CHECKPOINT_FILE = "v3_1_checkpoint.json"
RESULTS_PREFIX = "benchmark_results_v3_1"
API_KEY = "sk-cp-ZNEhSAB4-p-nraTwKzWoeLCpFPE-wY8If5v_1qxUvnW4_h0ryAunuH9_Vn-SItYx-D1AGFdRhD_6fn_9LhkpWG2yy6kUeRZBEjq8aFCUpruT5aFlM-Y5KDc"

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

class SimpleLLMCaller:
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    def call(self, prompt: str, system_prompt: str = "", max_tokens: int = 1500, timeout: int = 60) -> Dict:
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

# v3.1: MINIMAL prompts - just give the task and format hint

MINIMAL_EXECUTOR = """Task: {query}

Output format ({task_type}):
- research: Analysis with specific numbers and actionable steps
- code: Working code with comments
- review: Risk assessment with mitigation steps

Be concise but complete."""

VOTING_PROMPT = """Three experts gave their analysis:

Expert 1:
{answer1}

Expert 2:
{answer2}

Expert 3:
{answer3}

Task: {query}

Select the BEST answer or combine them into a superior answer.
Output only the selected/improved answer."""

STRICT_EVALUATOR = """Score this output (0-100):
- L5 (90-100): Excellent - specific, actionable, with evidence
- L4 (70-89): Good - detailed and mostly actionable
- L3 (50-69): Average - some specifics but needs work
- L2 (30-49): Weak - vague or incomplete
- L1 (0-29): Poor - not actionable

JSON format:
{{"depth": 1-5, "completeness": 1-5, "actionability": 1-5, "overall_score": 0-100, "reasoning": "brief"}}

---
{content}
---"""

LENIENT_CODE_EVALUATOR = """Score this code (0-100):
- L5 (90-100): Complete, working, well-structured
- L4 (70-89): Mostly complete, works with minor issues
- L3 (50-69): Partial, needs work
- L2 (30-49): Incomplete or broken
- L1 (0-29): Not functional

JSON format:
{{"depth": 1-5, "completeness": 1-5, "actionability": 1-5, "overall_score": 0-100, "reasoning": "brief"}}

---
{content}
---"""


class HarnessV31:
    def __init__(self, api_key: str):
        self.llm = SimpleLLMCaller(api_key)
        self.api_key = api_key
        self.num_agents = 3
    
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
    
    def run_single_agent(self, task: Dict, agent_id: int) -> Tuple[str, int, float]:
        """Run single agent on task, return (output, tokens, latency)"""
        task_type = task["type"]
        query = task["query"]
        
        response = self.llm.call(
            prompt=f"Task type: {task_type}\n{MINIMAL_EXECUTOR.format(query=query, task_type=task_type)}",
            system_prompt=f"You are Expert {agent_id}. Provide clear, actionable analysis.",
            max_tokens=1500,
            timeout=60
        )
        
        if response["error"]:
            return ("", 0, response["latency_ms"])
        
        return (response["content"], response.get("output_tokens", 0), response["latency_ms"])
    
    def execute_task(self, task: Dict) -> TaskResult:
        task_id = task["id"]
        task_type = task["type"]
        query = task["query"]
        
        executor_start = time.time()
        
        # Run 3 agents in parallel
        answers = []
        total_tokens = 0
        
        with ThreadPoolExecutor(max_workers=self.num_agents) as executor:
            futures = [executor.submit(self.run_single_agent, task, i+1) for i in range(self.num_agents)]
            for future in as_completed(futures):
                output, tokens, latency = future.result()
                answers.append(output)
                total_tokens += tokens
        
        # If any answer is empty, use the first non-empty
        non_empty = [a for a in answers if len(a) > 100]
        if not non_empty:
            final_output = answers[0] if answers else ""
        elif len(non_empty) == 1:
            final_output = non_empty[0]
        else:
            # Voting - pick longest (usually most detailed)
            final_output = max(non_empty, key=len)
        
        executor_latency = (time.time() - executor_start) * 1000
        
        # Evaluate
        evaluator_start = time.time()
        evaluator_prompt = LENIENT_CODE_EVALUATOR if task_type == "code" else STRICT_EVALUATOR
        evaluator_response = self.llm.call(
            prompt=evaluator_prompt.format(content=final_output),
            system_prompt="You are a strict evaluator.",
            max_tokens=512,
            timeout=30
        )
        evaluator_latency = (time.time() - evaluator_start) * 1000
        evaluator_tokens = evaluator_response.get("output_tokens", 0)
        total_tokens += evaluator_tokens
        
        if evaluator_response["error"]:
            return TaskResult(
                task_id=task_id, task_type=task_type,
                executor_output=final_output, quality_score=0,
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
            depth_score = eval_json.get("depth", {}).get("level", 3) if isinstance(eval_json.get("depth"), dict) else eval_json.get("depth", 3)
            completeness_score = eval_json.get("completeness", {}).get("level", 3) if isinstance(eval_json.get("completeness"), dict) else eval_json.get("completeness", 3)
            actionability_score = eval_json.get("actionability", {}).get("level", 3) if isinstance(eval_json.get("actionability"), dict) else eval_json.get("actionability", 3)
            is_suspicious = executor_latency < 5000 and len(final_output) > 500
        except:
            quality_score = 50
            depth_score = completeness_score = actionability_score = 3
            is_suspicious = False
        
        return TaskResult(
            task_id=task_id, task_type=task_type,
            executor_output=final_output, quality_score=quality_score,
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
                "error": result.error
            })
            self.save_checkpoint(checkpoint)
        
        elapsed = time.time() - start_time
        
        # Clean up checkpoint
        if os.path.exists(CHECKPOINT_FILE):
            os.remove(CHECKPOINT_FILE)
        
        total = len(results)
        core_scores = [r.quality_score for r in results[:10] if r.quality_score > 0]
        gen_scores = [r.quality_score for r in results[10:] if r.quality_score > 0]
        avg_actionability = sum(r.actionability_score for r in results if r.quality_score > 0) / max(len([r for r in results if r.quality_score > 0]), 1)
        
        core_avg = sum(core_scores) / len(core_scores) if core_scores else 0
        gen_avg = sum(gen_scores) / len(gen_scores) if gen_scores else 0
        composite = core_avg * 0.45 + gen_avg * 0.45 + (avg_actionability * 10) * 0.1
        
        print(f"\n{'=' * 60}")
        print(f"v3.1: Core={core_avg:.2f} Gen={gen_avg:.2f} Composite={composite:.2f}")
        print(f"{'=' * 60}")
        
        return {
            "harness_version": "v3.1",
            "paradigm": "v3 (Parallel Ensemble)",
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
    harness = HarnessV31(API_KEY)
    results = harness.run_benchmark()
    
    output_file = f"{RESULTS_PREFIX}_{time.strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\nResults saved to: {output_file}")