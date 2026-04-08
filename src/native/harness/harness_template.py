#!/usr/bin/env python3
"""
OpenClaw Native Harness Template - 可配置的进化模板

策略参数:
- RESEARCH_TOKENS: research 任务的 max_tokens
- CODE_TOKENS: code 任务的 max_tokens
- REVIEW_TOKENS: review 任务的 max_tokens
- MAX_RUNS: 每个任务运行次数（取最高分）
- SELF_REFLECT: 是否启用自反射 ("none", "core_only", "all")
- TEMPERATURE: LLM temperature
"""

import json
import time
import os
from pathlib import Path
from dataclasses import dataclass
from typing import Dict

# ========== 策略配置 (会被 evolution engine 修改) ==========
VERSION = "template"
RESEARCH_TOKENS = 5000
CODE_TOKENS = 5000
REVIEW_TOKENS = 3000
MAX_RUNS = 2
SELF_REFLECT = "core_only"  # none, core_only, all
TEMPERATURE = 0.7
# =========================================================

API_CONFIG = {
    "base_url": "https://api.minimaxi.com/anthropic",
    "model": "MiniMax-M2.7",
    "temperature": TEMPERATURE
}

BASE_DIR = Path(__file__).parent.parent.parent.parent
RESULTS_DIR = BASE_DIR / "results" / "evolution"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

CHECKPOINT_FILE = str(RESULTS_DIR / "checkpoint.json")
RESULTS_FILE = str(RESULTS_DIR / "results.json")

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
    run: int = 1

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
            "temperature": API_CONFIG.get("temperature", 0.7),
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

class HarnessV31:
    def __init__(self, api_key: str = None):
        if api_key is None:
            api_key = os.environ.get("MINIMAX_API_KEY", "")
        if not api_key:
            raise ValueError("MINIMAX_API_KEY not set")
        self.llm = RealLLMCaller(api_key)
        self.tasks = self.load_tasks()
    
    def load_tasks(self):
        tasks_file = BASE_DIR / "src" / "benchmark" / "tasks_v2.py"
        import importlib.util
        spec = importlib.util.spec_from_file_location("tasks", tasks_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.TASKS
    
    def get_max_tokens(self, task: Dict) -> int:
        """根据任务类型返回 max_tokens"""
        if task["type"] == "research":
            return RESEARCH_TOKENS
        elif task["type"] == "code":
            return CODE_TOKENS
        else:
            return REVIEW_TOKENS
    
    def should_self_reflect(self, task: Dict) -> bool:
        """根据策略决定是否自反射"""
        if SELF_REFLECT == "none":
            return False
        if SELF_REFLECT == "all":
            return True
        # core_only: 只对 core 任务自反射
        if SELF_REFLECT == "core_only" and task.get("category") == "core":
            return True
        return False
    
    def get_prompt_for_task(self, task: Dict) -> tuple:
        """构建 prompt"""
        query = task["query"]
        
        system_prompt = f"""You are an expert AI assistant tasked at answering the user's query accurately and thoroughly.

Query: {query}

Your response should be:
1. Accurate and factual
2. Well-structured with clear sections if needed
3. Actionable if the query requires action
4. Comprehensive covering all aspects of the query"""
        
        return system_prompt, query
    
    def execute_single(self, task: Dict, run_num: int) -> TaskResult:
        task_id = task["id"]
        task_type = task["type"]
        query = task["query"]
        
        executor_start = time.time()
        max_tokens = self.get_max_tokens(task)
        
        system_prompt, prompt = self.get_prompt_for_task(task)
        
        initial_response = self.llm.call_with_retry(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=max_tokens
        )
        
        if initial_response.get("error"):
            return TaskResult(
                task_id=task_id,
                task_type=task_type,
                executor_output=f"Error: {initial_response['error']}",
                quality_score=0,
                depth_score=0,
                completeness_score=0,
                actionability_score=0,
                executor_tokens=0,
                evaluator_tokens=0,
                executor_latency_ms=0,
                evaluator_latency_ms=0,
                error=initial_response["error"],
                run=run_num
            )
        
        executor_output = initial_response["content"]
        executor_tokens = initial_response["output_tokens"]
        executor_latency = initial_response["latency_ms"]
        
        # 自反射
        if self.should_self_reflect(task):
            reflect_prompt = f"""Review your previous response and improve it:

Original Query: {query}

Your Previous Response:
{executor_output}

Please provide an improved response that:
1. Addresses any gaps or inaccuracies
2. Is more comprehensive and detailed
3. Is better structured

Improved Response:"""
            
            reflect_response = self.llm.call_with_retry(
                prompt=reflect_prompt,
                system_prompt=system_prompt,
                max_tokens=max_tokens
            )
            
            if not reflect_response.get("error"):
                executor_output = reflect_response["content"]
                executor_tokens += reflect_response["output_tokens"]
                executor_latency += reflect_response["latency_ms"]
        
        # 评估
        eval_start = time.time()
        quality_score, depth_score, completeness_score, actionability_score = self.evaluate_task(task_id, query, executor_output)
        eval_latency = (time.time() - eval_start) * 1000
        eval_tokens = 0  # 简化，不追踪
        
        return TaskResult(
            task_id=task_id,
            task_type=task_type,
            executor_output=executor_output,
            quality_score=quality_score,
            depth_score=depth_score,
            completeness_score=completeness_score,
            actionability_score=actionability_score,
            executor_tokens=executor_tokens,
            evaluator_tokens=eval_tokens,
            executor_latency_ms=executor_latency,
            evaluator_latency_ms=eval_latency,
            run=run_num
        )
    
    def evaluate_task(self, task_id: str, query: str, response: str) -> tuple:
        """评估任务结果"""
        scorer_module = None
        
        # 动态加载对应 scorer
        scorer_file = BASE_DIR / "src" / "native" / "scorers" / f"{task_id}.py"
        if scorer_file.exists():
            import importlib.util
            spec = importlib.util.spec_from_file_location(f"scorer_{task_id}", scorer_file)
            scorer_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(scorer_module)
        
        if scorer_module and hasattr(scorer_module, 'score'):
            try:
                scores = scorer_module.score(query, response)
                return scores.get("quality", 50), scores.get("depth", 3), scores.get("completeness", 3), scores.get("actionability", 3)
            except Exception as e:
                print(f"Scorer error for {task_id}: {e}")
        
        # 默认评分逻辑
        word_count = len(response.split())
        has_structure = any(marker in response for marker in ["##", "1.", "2.", "- ", "* "])
        has_numbers = any(c.isdigit() for c in response)
        
        quality = min(100, max(0, word_count // 10))
        if has_structure:
            quality = min(100, quality + 10)
        if has_numbers:
            quality = min(100, quality + 5)
        
        depth = min(5, max(1, word_count // 200))
        completeness = min(5, max(1, len(response) // 500))
        actionability = 3 if "action" in response.lower() or "should" in response.lower() else 2
        
        return quality, depth, completeness, actionability
    
    def run_tasks(self) -> list:
        results = []
        
        print(f"\n{'='*60}")
        print(f"Harness {VERSION} 开始执行")
        print(f"策略: tokens=({RESEARCH_TOKENS}/{CODE_TOKENS}/{REVIEW_TOKENS}), max_runs={MAX_RUNS}, reflect={SELF_REFLECT}")
        print(f"{'='*60}\n")
        
        for i, task in enumerate(self.tasks):
            task_id = task["id"]
            task_type = task["type"]
            category = task.get("category", "unknown")
            
            print(f"[{i+1}/{len(self.tasks)}] {task_id} ({task_type}/{category})...", end=" ", flush=True)
            
            # 保存检查点
            checkpoint = {
                "current_task": i,
                "task_id": task_id,
                "results": results
            }
            with open(CHECKPOINT_FILE, 'w') as f:
                json.dump(checkpoint, f)
            
            # 执行多次取最高
            best_result = None
            for run in range(1, MAX_RUNS + 1):
                print(f"\n  Run {run}/{MAX_RUNS}...", end=" ", flush=True)
                result = self.execute_single(task, run)
                print(f"Score={result.quality_score}", end=" ", flush=True)
                
                if best_result is None or result.quality_score > best_result.quality_score:
                    best_result = result
            
            # Truncate long outputs to save space (keep first 5000 chars)
            output = best_result.executor_output
            if len(output) > 5000:
                output = output[:5000] + f"\n... [truncated {len(output)-5000} chars]"
            
            results.append({
                "task_id": task_id,
                "task_type": task_type,
                "category": category,
                "quality_score": best_result.quality_score,
                "depth_score": best_result.depth_score,
                "completeness_score": best_result.completeness_score,
                "actionability_score": best_result.actionability_score,
                "executor_tokens": best_result.executor_tokens,
                "executor_latency_ms": best_result.executor_latency_ms,
                "is_suspicious": best_result.is_suspicious,
                "error": best_result.error,
                "run": best_result.run,
                "iterations": best_result.iterations,
                "executor_output": output
            })
            
            print(f" -> Final={best_result.quality_score}")
        
        return results
    
    def compute_summary(self, results: list) -> dict:
        core_tasks = [r for r in results if r.get("category") == "core"]
        gen_tasks = [r for r in results if r.get("category") == "gen"]
        
        core_avg = sum(r["quality_score"] for r in core_tasks) / len(core_tasks) if core_tasks else 0
        gen_avg = sum(r["quality_score"] for r in gen_tasks) / len(gen_tasks) if gen_tasks else 0
        
        all_actionability = [r["actionability_score"] for r in results]
        avg_action = sum(all_actionability) / len(all_actionability) if all_actionability else 0
        
        composite = (core_avg * 0.6 + gen_avg * 0.4)
        
        return {
            "total_tasks": len(results),
            "core_avg_score": round(core_avg, 2),
            "gen_avg_score": round(gen_avg, 2),
            "avg_actionability_level": round(avg_action, 1),
            "composite_score": round(composite, 2)
        }
    
    def save_results(self, results: list, summary: dict):
        output = {
            "harness_version": VERSION,
            "paradigm": f"v31 (tokens={RESEARCH_TOKENS}/{CODE_TOKENS}/{REVIEW_TOKENS}, reflect={SELF_REFLECT})",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "elapsed_seconds": 0,
            "summary": summary,
            "individual_results": results
        }
        
        with open(RESULTS_FILE, 'w', encoding="utf-8") as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        print(f"\nResults saved to: {RESULTS_FILE}")
        
        if os.path.exists(CHECKPOINT_FILE):
            os.remove(CHECKPOINT_FILE)
    
    def run(self):
        start_time = time.time()
        
        if os.path.exists(CHECKPOINT_FILE):
            os.remove(CHECKPOINT_FILE)
        
        results = self.run_tasks()
        summary = self.compute_summary(results)
        
        elapsed = time.time() - start_time
        summary["elapsed_seconds"] = elapsed
        
        self.save_results(results, summary)
        
        print(f"\n{'='*60}")
        print(f"评分汇总:")
        print(f"  Core 平均: {summary['core_avg_score']}")
        print(f"  Gen 平均: {summary['gen_avg_score']}")
        print(f"  综合得分: {summary['composite_score']}")
        print(f"  平均可操作性: {summary['avg_actionability_level']}")
        print(f"  总任务数: {summary['total_tasks']}")
        print(f"  总耗时: {elapsed:.1f}秒")
        print(f"{'='*60}")

def get_api_key():
    """获取 API key - 支持多种方式"""
    # 1. 环境变量
    key = os.environ.get("MINIMAX_API_KEY", "")
    if key:
        return key
    # 2. 环境变量 (alternative name)
    key = os.environ.get("API_KEY", "")
    if key:
        return key
    # 3. 从配置文件读取
    key_file = Path.home() / ".openclaw" / "secrets" / "minimax_api_key.txt"
    if key_file.exists():
        return key_file.read_text().strip()
    # 4. 默认值 (仅用于兼容旧代码)
    return "sk-cp-ZNEhSAB4-p-nraTwKzWoeLCpFPE-wY8If5v_1qxUvnW4_h0ryAunuH9_Vn-SItYx-D1AGFdRhD_6fn_9LhkpWG2yy6kUeRZBEjq8aFCUpruT5aFlM-Y5KDc"

def main():
    api_key = get_api_key()
    harness = HarnessV31(api_key)
    harness.run()

if __name__ == "__main__":
    main()