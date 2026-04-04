#!/usr/bin/env python3
"""
OpenClaw Native Harness v5.1 - Single task test with retries

Testing if API calls work properly with retry logic.
"""

import json
import time
import os
import urllib.request
from dataclasses import dataclass
from typing import Dict

API_CONFIG = {
    "base_url": "https://api.minimaxi.com/anthropic",
    "model": "MiniMax-M2.7"
}

@dataclass
class TaskResult:
    task_id: str
    quality_score: float
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
                print(f"  [Attempt {attempt+1} failed: {result.get('error')}]", end=" ", flush=True)
                if attempt < max_retries:
                    time.sleep(2)
            except Exception as e:
                print(f"  [Exception: {e}]", end=" ", flush=True)
                if attempt < max_retries:
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


EXECUTOR_PROMPT = """你是一个专业的技术分析师。

任务类型：{task_type}
任务：{query}

根据任务类型输出：
**research**: 问题诊断 → 深度分析 → 具体方案 → 验证方法
**code**: 架构 → 核心代码 → 测试
**review**: 风险矩阵 → 影响分析 → 缓解方案

要求：具体数字、可操作步骤、代码可运行。"""

SELF_CRITIQUE = """评审以下输出，找出最多3个问题：

任务：{query}
输出：
{output}

格式：
问题1: [描述]
改进1: [怎么做]"""

REVISION = """根据评审改进输出：

任务：{query}
输出：{output}
评审：{critique}

输出改进版本。"""

EVALUATOR = """评分以下输出（0-100）：
{content}

输出JSON：{{"overall_score": 数字}}"""


class HarnessV51:
    def __init__(self, api_key: str):
        self.llm = RealLLMCaller(api_key)
        self.api_key = api_key
    
    def execute_single_task(self, task: Dict) -> TaskResult:
        task_id = task["id"]
        task_type = task["type"]
        query = task["query"]
        
        print(f"  Step 1: Initial response...", end=" ", flush=True)
        initial = self.llm.call_with_retry(
            prompt=f"任务类型：{task_type}\n任务：{query}",
            system_prompt=EXECUTOR_PROMPT.format(task_type=task_type, query=query),
            max_tokens=2500
        )
        
        if initial["error"]:
            return TaskResult(task_id=task_id, quality_score=0, error=f"Initial: {initial['error']}")
        
        output = initial["content"]
        print(f"OK ({len(output)} chars)", end=" ", flush=True)
        
        print(f"\n  Step 2: Self-critique...", end=" ", flush=True)
        critique = self.llm.call_with_retry(
            prompt=SELF_CRITIQUE.format(query=query, output=output),
            system_prompt="你是评审专家。",
            max_tokens=1500
        )
        
        has_issues = not critique["error"] and len(critique.get("content", "")) > 100
        print(f"{'Found issues' if has_issues else 'No major issues'}", end=" ", flush=True)
        
        if has_issues:
            print(f"\n  Step 3: Revision...", end=" ", flush=True)
            revision = self.llm.call_with_retry(
                prompt=REVISION.format(query=query, output=output, critique=critique["content"]),
                system_prompt="你是技术分析师。",
                max_tokens=2500
            )
            if not revision["error"]:
                output = revision["content"]
                print(f"OK ({len(output)} chars)")
        
        print(f"\n  Step 4: Evaluate...", end=" ", flush=True)
        evaluator = self.llm.call_with_retry(
            prompt=EVALUATOR.format(content=output[:2000]),
            system_prompt="你是评估专家。",
            max_tokens=500
        )
        
        if evaluator["error"]:
            return TaskResult(task_id=task_id, quality_score=0, error=f"Eval: {evaluator['error']}")
        
        try:
            text = evaluator["content"]
            json_start = text.find('{')
            json_end = text.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                score = json.loads(text[json_start:json_end]).get("overall_score", 50)
            else:
                score = 50
        except:
            score = 50
        
        print(f"Score: {score}")
        return TaskResult(task_id=task_id, quality_score=score)
    
    def run_test(self) -> Dict:
        task = {"id": "test_001", "type": "research",
                "query": "分析 Transformer 架构在长上下文场景下的注意力机制优化方案"}
        
        print("=" * 60)
        print("Harness v5.1 - Single Task Test")
        print("=" * 60)
        
        start = time.time()
        result = self.execute_single_task(task)
        elapsed = time.time() - start
        
        print(f"\nResult: {result.task_id} = {result.quality_score} ({elapsed:.1f}s)")
        if result.error:
            print(f"Error: {result.error}")
        
        return {
            "harness_version": "v5.1",
            "task_id": result.task_id,
            "quality_score": result.quality_score,
            "error": result.error,
            "elapsed_seconds": elapsed
        }


if __name__ == "__main__":
    api_key = "sk-cp-ZNEhSAB4-p-nraTwKzWoeLCpFPE-wY8If5v_1qxUvnW4_h0ryAunuH9_Vn-SItYx-D1AGFdRhD_6fn_9LhkpWG2yy6kUeRZBEjq8aFCUpruT5aFlM-Y5KDc"
    
    harness = HarnessV51(api_key)
    result = harness.run_test()
    
    with open("test_v5_1_result.json", "w") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)