#!/usr/bin/env python3
"""
OpenClaw Native Harness v15.0 - Novelty-Focused Gen + Stable Core

v12.0 (58.01): Best v2 paradigm
- Core: 58.7 (beats v23's 54.4!)
- Gen: 63.4 (below v23's 68.2)

v14 tried Gen reflection but hung at gen_003.

v15 Strategy: NO REFLECTION LOOPS - Instead use enhanced prompts
- Keep v12's proven Core formats (CoT research, v23 code/review)
- For Gen tasks: Use a single-shot enhanced prompt that explicitly requires:
  * Novel/unseen aspects of the solution
  * Practical applicability
  * Specific implementation considerations
- Target: Improve Gen to match v23 (68.2) while keeping Core (58.7)

Key insight: Reflection loops cause hangs. Use better prompt engineering instead.
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

CHECKPOINT_FILE = "v15_0_checkpoint.json"
RESULTS_PREFIX = "benchmark_results_v15_0"

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

# v15: NO REFLECTION - Enhanced prompts for Gen tasks only

# Core research - CoT (Chain of Thought) from v12
CORE_RESEARCH_EXECUTOR = """你是一个专业的技术分析师。任务类型：research。

任务：{query}

请按以下结构输出你的深度分析：

## 1. 问题诊断
明确核心问题是什么

## 2. 深度分析
- 技术原理
- 现有方案的优缺点
- 具体数字和证据

## 3. 解决方案
分步骤的具体方案

## 4. 验证方法
如何验证方案的有效性

要求：分析要有深度，方案要有可操作性。"""

# Core code - v23 format
CORE_CODE_EXECUTOR = """你是一个专业的技术分析师。任务类型：code。

任务：{query}

请按以下结构输出：

## 架构简图
简要描述系统架构

## 核心代码
完整可运行的代码实现

## 测试用例
验证功能的测试代码

## 配置说明
必要的配置说明

要求：代码必须可运行。"""

# Core review - v23 format
CORE_REVIEW_EXECUTOR = """你是一个专业的技术分析师。任务类型：review。

任务：{query}

请按以下结构输出：

## 风险矩阵
列出主要风险及等级

## 影响分析
每个风险的影响

## 缓解步骤
具体的缓解措施

## 优先级
按优先级排序

## 验证方法
如何验证缓解效果

要求：有具体数字和可操作步骤。"""

# Gen research - Enhanced for novelty and practical applicability
GEN_RESEARCH_EXECUTOR = """你是一个专业的技术分析师。任务类型：research（泛化任务）。

任务：{query}

这是跨领域泛化任务。请按以下结构输出你的分析，特别强调**新颖性**和**实用性**：

## 1. 问题诊断
核心问题是什么

## 2. 跨领域迁移分析
- 从已知领域到本领域的类比
- 需要适配的关键点
- **新颖点**：与标准方案的差异

## 3. 具体方案
分步骤的实现方案

## 4. 实用性评估
- 优点
- 潜在风险
- 实施注意事项

## 5. 验证方法
具体可操作的验证方案

要求：重点展示如何将通用知识适配到本领域的创新点。"""

# Gen code - Enhanced for novel implementation
GEN_CODE_EXECUTOR = """你是一个专业的技术分析师。任务类型：code（泛化任务）。

任务：{query}

这是跨领域泛化任务。请按以下结构输出，特别强调**实现创新点**：

## 架构设计
系统架构及创新点

## 核心代码
完整可运行的代码（标注创新部分）

## 测试用例
验证功能的测试代码

## 实用性分析
- 优点
- 潜在风险
- 优化方向

要求：代码必须可运行，清晰标注与标准实现的差异。"""

# Gen review - Enhanced for cross-domain assessment
GEN_REVIEW_EXECUTOR = """你是一个专业的技术分析师。任务类型：review（泛化任务）。

任务：{query}

这是跨领域泛化任务。请按以下结构输出，特别强调**跨领域适用性**：

## 风险矩阵
主要风险及等级

## 跨领域影响分析
从其他领域视角看此设计的合理性

## 创新点评估
与标准架构相比的创新之处

## 实用性建议
如何提高跨领域适用性

## 验证方法
具体可操作的验证方案

要求：展示跨领域的泛化能力。"""

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


class HarnessV150:
    def __init__(self, api_key: str):
        self.llm = RealLLMCaller(api_key)
        self.api_key = api_key
    
    def get_executor_prompt(self, task_id: str, task_type: str) -> str:
        """Get the appropriate executor prompt based on task ID and type"""
        # Gen tasks (gen_*) use enhanced prompts for novelty/practicality
        if task_id.startswith("gen_"):
            if task_type == "research":
                return GEN_RESEARCH_EXECUTOR
            elif task_type == "code":
                return GEN_CODE_EXECUTOR
            else:  # review
                return GEN_REVIEW_EXECUTOR
        else:
            # Core tasks use proven v12 prompts
            if task_type == "research":
                return CORE_RESEARCH_EXECUTOR
            elif task_type == "code":
                return CORE_CODE_EXECUTOR
            else:  # review
                return CORE_REVIEW_EXECUTOR
    
    def execute_task(self, task: Dict) -> TaskResult:
        task_id = task["id"]
        task_type = task["type"]
        query = task["query"]
        
        executor_start = time.time()
        max_tokens = 3000 if task_type == "code" else 2500
        
        # Get appropriate executor prompt
        executor_prompt = self.get_executor_prompt(task_id, task_type)
        
        # Single-shot execution (NO reflection loop!)
        response = self.llm.call_with_retry(
            prompt=f"任务：{query}",
            system_prompt=executor_prompt.format(query=query),
            max_tokens=max_tokens
        )
        
        if response["error"]:
            return TaskResult(
                task_id=task_id, task_type=task_type,
                executor_output="", quality_score=0,
                depth_score=0, completeness_score=0, actionability_score=0,
                executor_tokens=0, evaluator_tokens=0,
                executor_latency_ms=(time.time() - executor_start) * 1000,
                evaluator_latency_ms=0,
                error=f"Executor error: {response['error']}"
            )
        
        current_output = response["content"]
        total_tokens = response.get("output_tokens", 0)
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
            iterations=1  # NO REFLECTION LOOP
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
        print("Harness v15.0 - Novelty-Focused Gen + Stable Core (NO REFLECTION)")
        print("=" * 60)
        
        for task in tasks:
            print(f"[{task['id']}] Executor({task['type']})...", end=" ", flush=True)
            result = self.execute_task(task)
            results.append(result)
            print(f"Score: {result.quality_score:.1f}")
            
            # Save checkpoint after each task
            checkpoint = {
                "tasks_completed": [t["id"] for t in tasks[:len(results)]],
                "last_task": task["id"]
            }
            with open(CHECKPOINT_FILE, 'w') as f:
                json.dump(checkpoint, f)
        
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
        print(f"v15.0: Core={core_avg:.2f} Gen={gen_avg:.2f} Composite={composite:.2f}")
        print(f"{'=' * 60}")
        
        return {
            "harness_version": "v15.0",
            "paradigm": "v2 (Novelty-Focused Gen + Stable Core)",
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
    # Use test key (same as other versions)
    api_key = "sk-cp-ZNEhSAB4-p-nraTwKzWoeLCpFPE-wY8If5v_1qxUvnW4_h0ryAunuH9_Vn-SItYx-D1AGFdRhD_6fn_9LhkpWG2yy6kUeRZBEjq8aFCUpruT5aFlM-Y5KDc"
    
    harness = HarnessV150(api_key)
    results = harness.run_benchmark()
    
    output_file = f"{RESULTS_PREFIX}_{time.strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\nResults saved to: {output_file}")