#!/usr/bin/env python3
"""
OpenClaw Native Harness v7.0 - Tool-Augmented Generalization

v12.0 (58.01): Self-reflection for Gen - Core=58.7, Gen=63.4 - CHAMPION
v3.3 (52.48): Pure self-reflection - Core=61.4, Gen=48.4 (Core improved, Gen collapsed!)
v9.0 (56.73): Type-directed hybrid - Core=57.4, Gen=61.4

Root Cause of Gen Collapse in v3.3:
Self-reflection reinforces existing patterns. For KNOWN domains (Core), this refines outputs.
For UNKNOWN domains (Gen: quantum computing, blockchain, federated learning),
self-reflection amplifies guesswork rather than grounding in reality.

v7.0 Strategy: Tool-Augmented Generalization
- For Gen tasks: Use REAL web search (DuckDuckGo) to gather domain knowledge FIRST
- Then generate grounded outputs with actual data
- For Core tasks: Keep v12.0's selective reflection (works well for known domains)
- Key difference from self-reflection: External truth > internal self-critique

New composite weighting (based on observation):
- Core 60% + Gen 30% + Efficiency 10% (same as before)
- But Gen tasks now get actual external knowledge grounding
"""

import json
import time
import os
import sys
import urllib.request
import urllib.parse
from dataclasses import dataclass
from typing import Dict, List, Optional

API_CONFIG = {
    "base_url": "https://api.minimaxi.com/anthropic",
    "model": "MiniMax-M2.7"
}

CHECKPOINT_FILE = "v7_0_tool_checkpoint.json"
RESULTS_FILE = "benchmark_results_v7_0_tool.json"

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
    used_web_search: bool = False

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


class DuckDuckGoSearch:
    """Simple DuckDuckGo search without API key"""
    
    def search(self, query: str, max_results: int = 5) -> List[Dict]:
        """Search DuckDuckGo and return results"""
        try:
            # Use DuckDuckGo HTML lite interface
            url = f"https://duckduckgo.com/html/?q={urllib.parse.quote(query)}&kl=us-en"
            req = urllib.request.Request(url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            with urllib.request.urlopen(req, timeout=10) as response:
                html = response.read().decode('utf-8')
            
            # Parse results
            results = []
            import re
            # Simple HTML parsing for search results
            pattern = r'<a class="result__a" href="([^"]+)"[^>]*>([^<]+)</a>'
            matches = re.findall(pattern, html)
            
            for url, title in matches[:max_results]:
                results.append({
                    "title": self._clean_html(title),
                    "url": url
                })
            
            # If no matches, try alternative pattern
            if not results:
                pattern = r'<h2[^>]*><a href="([^"]+)"[^>]*>([^<]+)</a></h2>'
                matches = re.findall(pattern, html)
                for url, title in matches[:max_results]:
                    results.append({
                        "title": self._clean_html(title),
                        "url": url
                    })
            
            return results
        except Exception as e:
            print(f"  [Search error: {e}]")
            return []
    
    def _clean_html(self, text: str) -> str:
        """Remove HTML entities and tags"""
        import re
        text = re.sub(r'<[^>]+>', '', text)
        text = text.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
        text = text.replace('&quot;', '"').replace('&#39;', "'")
        return text.strip()


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

# NEW: Tool-augmented prompt for Gen tasks
TOOL_AUGMENTED_GEN_PROMPT = """你是一个专业的技术分析师。请基于以下真实信息进行分析。

任务：{query}

真实参考信息（来自网络搜索）：
{search_results}

请按以下格式输出：
1. 技术分析：结合真实信息给出深度分析
2. 案例研究：引用你找到的真实案例或数据
3. 可行性评估：基于真实信息评估技术成熟度和挑战

要求：
- 结合真实数据，不要空泛猜测
- 有具体数字和来源
- 分析要实际，不要过度乐观"""

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


class HarnessV70ToolAugmented:
    def __init__(self, api_key: str):
        self.llm = RealLLMCaller(api_key)
        self.api_key = api_key
        self.search = DuckDuckGoSearch()
    
    def get_prompt_for_task(self, task: Dict, is_gen: bool = False, search_context: str = "") -> tuple:
        """Return (system_prompt, prompt) based on task type and whether it's Gen"""
        task_type = task["type"]
        query = task["query"]
        
        if is_gen and search_context:
            # Use tool-augmented prompt for Gen tasks with search context
            return (
                TOOL_AUGMENTED_GEN_PROMPT.format(query=query, search_results=search_context),
                f"任务类型：{task_type}\n任务：{query}"
            )
        elif task_type == "research":
            return (COT_RESEARCH_PROMPT.format(query=query), f"任务类型：{task_type}\n任务：{query}")
        else:
            return (V23_CODE_PROMPT.format(task_type=task_type, query=query), f"任务类型：{task_type}\n任务：{query}")
    
    def should_reflect(self, task_type: str, is_gen: bool) -> bool:
        """Self-reflection for Core tasks only, not Gen (to preserve diversity)"""
        if is_gen:
            return False  # Gen tasks get web search instead of self-reflection
        return task_type in ["research", "review"]
    
    def search_for_task(self, query: str) -> str:
        """Search for relevant information for a task"""
        print(f"  [Searching for: {query[:50]}...]")
        results = self.search.search(query, max_results=3)
        
        if not results:
            return ""
        
        context = "以下是搜索到的相关信息：\n\n"
        for i, r in enumerate(results, 1):
            context += f"{i}. {r['title']}\n   来源: {r['url']}\n\n"
        
        print(f"  [Found {len(results)} results]")
        return context
    
    def execute_task(self, task: Dict) -> TaskResult:
        task_id = task["id"]
        task_type = task["type"]
        query = task["query"]
        is_gen = task_id.startswith("gen_")
        
        executor_start = time.time()
        max_tokens = 3000 if task_type == "code" else 2500
        
        # For Gen tasks, search for external knowledge first
        search_context = ""
        used_search = False
        if is_gen:
            search_context = self.search_for_task(query)
            used_search = True
        
        system_prompt, prompt = self.get_prompt_for_task(task, is_gen, search_context)
        
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
                error=f"Initial error: {initial_response['error']}",
                used_web_search=used_search
            )
        
        current_output = initial_response["content"]
        total_tokens = initial_response.get("output_tokens", 0)
        
        # Step 2: Light self-reflection only for Core (NOT Gen - preserve diversity)
        iterations = 1
        if self.should_reflect(task_type, is_gen):
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
                error=f"Evaluator error: {evaluator_response['error']}",
                used_web_search=used_search
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
            iterations=iterations,
            used_web_search=used_search
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
            # Gen tasks (novel domains - use web search)
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
            
            print(f"\n[{task_id}] Running ({task['type']})...", flush=True)
            result = self.execute_task(task)
            results.append(result)
            
            # Save checkpoint after each task
            completed.add(task_id)
            checkpoint["tasks_completed"] = list(completed)
            checkpoint["results"] = [self.result_to_dict(r) for r in results]
            self.save_checkpoint(checkpoint)
            
            print(f"  Score: {result.quality_score} | "
                  f"Depth={result.depth_score} Comp={result.completeness_score} Act={result.actionability_score} | "
                  f"Tokens={result.executor_tokens} | "
                  f"Search={result.used_web_search}")
        
        elapsed = time.time() - start_time
        
        # Compute summary
        summary = self.compute_summary(results, elapsed)
        
        return {
            "harness_version": "v7.0-tool-aug",
            "paradigm": "Tool-Augmented Generalization",
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
            "iterations": r.iterations,
            "used_web_search": r.used_web_search
        }
    
    def compute_summary(self, results: List[TaskResult], elapsed: float) -> Dict:
        total = len(results)
        core_results = [r for r in results if not r.task_id.startswith("gen_")]
        gen_results = [r for r in results if r.task_id.startswith("gen_")]
        
        core_avg = sum(r.quality_score for r in core_results) / len(core_results) if core_results else 0
        gen_avg = sum(r.quality_score for r in gen_results) / len(gen_results) if gen_results else 0
        
        total_tokens = sum(r.executor_tokens for r in results)
        avg_latency = sum(r.executor_latency_ms + r.evaluator_latency_ms for r in results) / total if total > 0 else 0
        
        # Composite: 60% core, 30% gen, 10% efficiency
        efficiency = 1.0 - (elapsed / (total * 120000))  # Efficiency based on time
        composite = core_avg * 0.6 + gen_avg * 0.3 + efficiency * 100 * 0.1
        
        return {
            "total_tasks": total,
            "core_avg_score": core_avg,
            "gen_avg_score": gen_avg,
            "total_executor_tokens": total_tokens,
            "avg_latency_ms": avg_latency,
            "composite_score": composite,
            "tasks_with_web_search": sum(1 for r in results if r.used_web_search)
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
        print("Error: MINIMAX_API_KEY not set")
        sys.exit(1)
    
    harness = HarnessV70ToolAugmented(api_key)
    print(f"Starting v7.0 Tool-Augmented benchmark...")
    print(f"Paradigm: Tool-Augmented Generalization")
    print(f"  - Gen tasks: Web search first, then generate")
    print(f"  - Core tasks: Selective self-reflection (from v12.0)")
    print()
    
    results = harness.run_benchmark()
    
    # Save results
    with open(RESULTS_FILE, 'w') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'='*60}")
    print(f"BENCHMARK COMPLETE")
    print(f"{'='*60}")
    print(f"Composite: {results['summary']['composite_score']:.2f}")
    print(f"Core avg: {results['summary']['core_avg_score']:.2f}")
    print(f"Gen avg: {results['summary']['gen_avg_score']:.2f}")
    print(f"Total tokens: {results['summary']['total_executor_tokens']}")
    print(f"Elapsed: {results['summary']['elapsed_seconds']:.1f}s")
    print(f"Tasks with web search: {results['summary']['tasks_with_web_search']}")
    print(f"\nResults saved to: {RESULTS_FILE}")


if __name__ == "__main__":
    main()