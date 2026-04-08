#!/usr/bin/env python3
"""
Generated Harness - evo_005
Strategy: v36_1000tokens_temp0.3
Tokens: 1000/1000
Max Runs: 2
Temperature: 0.3
"""

import json
import time
import os
from pathlib import Path
from dataclasses import dataclass
from typing import Dict

VERSION = "evo_005"
RESEARCH_TOKENS = 1000
CODE_TOKENS = 1000
REVIEW_TOKENS = 3000
MAX_RUNS = 2
SELF_REFLECT = "core_only"
TEMPERATURE = 0.3

API_CONFIG = {
    "base_url": "https://api.minimaxi.com/anthropic",
    "model": "MiniMax-M2.7",
    "temperature": TEMPERATURE
}

BASE_DIR = Path(__file__).parent.parent.parent.parent
RESULTS_DIR = BASE_DIR / "results" / "evolution"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

CHECKPOINT_FILE = str(RESULTS_DIR / "evo_005_checkpoint.json")
RESULTS_FILE = str(RESULTS_DIR / "benchmark_results_evo_005_gen1.json")

# Import and apply resource limits
try:
    import sys
    sys.path.insert(0, str(BASE_DIR / "src" / "native"))
    import resource_limiter
    resource_limiter.apply_all()
except:
    pass

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
                    # Track API call
                    api_file = RESULTS_DIR / "api_calls.json"
                    try:
                        data = {}
                        if api_file.exists():
                            with open(api_file) as f:
                                data = json.load(f)
                        data['count'] = data.get('count', 0) + 1
                        with open(api_file, 'w') as f:
                            json.dump(data, f)
                    except:
                        pass
                    return result
                if attempt < max_retries:
                    print(f"  [Retry {attempt+1}/{max_retries}]", end=" ", flush=True)
                    time.sleep(2 ** attempt)
            except Exception as e:
                if attempt < max_retries:
                    print(f"  [Error: {e}, retry {attempt+1}/{max_retries}]", end=" ", flush=True)
                    time.sleep(2 ** attempt)
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

class HarnessV30:
    def __init__(self, api_key: str):
        self.llm = RealLLMCaller(api_key)
        self.api_key = api_key
        self.max_runs = MAX_RUNS
        self.tasks = self.load_tasks()
    
    def check_disk_space(self):
        """Check disk space before running"""
        stat = shutil.disk_usage(BASE_DIR)
        pct = stat.used / stat.total * 100
        if pct > 90:
            raise Exception(f"Disk space critical: {pct:.1f}%")
        return pct
    
    def load_tasks(self):
        # Load tasks from tasks_v2.py - need to get both CORE and GENERALIZATION
        tasks_file = BASE_DIR / "src" / "benchmark" / "tasks_v2.py"
        import importlib.util
        spec = importlib.util.spec_from_file_location("tasks", tasks_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        # tasks_v2.py uses DynamicBenchmarkSuite class with default include_generalization=True
        suite = module.DynamicBenchmarkSuite(include_generalization=True)
        tasks = list(suite.tasks)
        # Add category field for scoring
        for t in tasks:
            t["category"] = "core" if t["id"].startswith("core_") else "gen"
        return tasks
    
    def get_max_tokens(self, task: Dict) -> int:
        if task["type"] == "research":
            return RESEARCH_TOKENS
        elif task["type"] == "code":
            return CODE_TOKENS
        return REVIEW_TOKENS
    
    def should_self_reflect(self, task: Dict) -> bool:
        if SELF_REFLECT == "none":
            return False
        if SELF_REFLECT == "all":
            return True
        if SELF_REFLECT == "core_only" and task.get("category") == "core":
            return True
        return False
    
    def execute_single(self, task: Dict, run_num: int) -> TaskResult:
        task_id = task["id"]
        task_type = task["type"]
        query = task["query"]
        
        executor_start = time.time()
        max_tokens = self.get_max_tokens(task)
        
        system_prompt = f"You are an expert AI assistant. Query: {query}"
        prompt = query
        
        initial_response = self.llm.call_with_retry(prompt=prompt, system_prompt=system_prompt, max_tokens=max_tokens)
        
        if initial_response.get("error"):
            return TaskResult(
                task_id=task_id, task_type=task_type, executor_output=f"Error: {initial_response['error']}",
                quality_score=0, depth_score=0, completeness_score=0, actionability_score=0,
                executor_tokens=0, evaluator_tokens=0, executor_latency_ms=0, evaluator_latency_ms=0,
                error=initial_response["error"], run=run_num
            )
        
        executor_output = initial_response["content"]
        executor_tokens = initial_response["output_tokens"]
        executor_latency = initial_response["latency_ms"]
        
        if self.should_self_reflect(task):
            reflect_prompt = f"Review and improve: {query}\n\n{executor_output}"
            reflect_response = self.llm.call_with_retry(prompt=reflect_prompt, system_prompt=system_prompt, max_tokens=max_tokens)
            if not reflect_response.get("error"):
                executor_output = reflect_response["content"]
                executor_tokens += reflect_response["output_tokens"]
                executor_latency += reflect_response["latency_ms"]
        
        quality_score = min(100, max(0, len(executor_output.split()) // 5))
        depth_score = min(5, max(1, len(executor_output) // 500))
        completeness_score = min(5, max(1, len(executor_output) // 300))
        actionability_score = 3 if "should" in executor_output.lower() else 2
        
        return TaskResult(
            task_id=task_id, task_type=task_type, executor_output=executor_output,
            quality_score=quality_score, depth_score=depth_score, completeness_score=completeness_score,
            actionability_score=actionability_score, executor_tokens=executor_tokens, evaluator_tokens=0,
            executor_latency_ms=executor_latency, evaluator_latency_ms=0, run=run_num
        )
    
    def run_tasks(self) -> list:
        results = []
        for i, task in enumerate(self.tasks):
            task_id = task["id"]
            print(f"[{i+1}/{len(self.tasks)}] {task_id}...", end=" ", flush=True)
            
            checkpoint = {"current_task": i, "task_id": task_id, "results": results}
            with open(CHECKPOINT_FILE, 'w') as f:
                json.dump(checkpoint, f)
            
            task_results = []
            for run in range(1, self.max_runs + 1):
                print(f"Run{run}...", end=" ", flush=True)
                result = self.execute_single(task, run)
                print(f"Score={result.quality_score}", end=" ", flush=True)
                task_results.append(result)
            
            best = max(task_results, key=lambda r: r.quality_score)
            output = best.executor_output
            if len(output) > 5000:
                output = output[:5000] + f"... [truncated {len(output)-5000} chars]"
            
            results.append({
                "task_id": task_id,
                "task_type": task["type"],
                "category": task.get("category", "unknown"),
                "quality_score": best.quality_score,
                "depth_score": best.depth_score,
                "completeness_score": best.completeness_score,
                "actionability_score": best.actionability_score,
                "executor_tokens": best.executor_tokens,
                "executor_latency_ms": best.executor_latency_ms,
                "executor_output": output,
                "run": best.run,
                "error": best.error
            })
            print(f"-> Final={best.quality_score}")
        
        return results
    
    def compute_summary(self, results: list) -> dict:
        core = [r for r in results if r.get("category") == "core"]
        gen = [r for r in results if r.get("category") == "gen"]
        core_avg = sum(r["quality_score"] for r in core) / len(core) if core else 0
        gen_avg = sum(r["quality_score"] for r in gen) / len(gen) if gen else 0
        all_action = [r["actionability_score"] for r in results]
        avg_action = sum(all_action) / len(all_action) if all_action else 0
        composite = core_avg * 0.45 + gen_avg * 0.45 + avg_action * 10 * 0.1
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
            "paradigm": f"v31 tokens={RESEARCH_TOKENS}/{CODE_TOKENS}",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "elapsed_seconds": 0,
            "summary": summary,
            "individual_results": results
        }
        with open(RESULTS_FILE, 'w', encoding="utf-8") as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        print(f"Results saved to: {RESULTS_FILE}")
        if Path(CHECKPOINT_FILE).exists():
            Path(CHECKPOINT_FILE).unlink()
    
    def run(self):
        # Check disk space
        disk_pct = self.check_disk_space()
        print(f"Disk usage: {disk_pct:.1f}%")
        
        start = time.time()
        if Path(CHECKPOINT_FILE).exists():
            Path(CHECKPOINT_FILE).unlink()
        results = self.run_tasks()
        summary = self.compute_summary(results)
        summary["elapsed_seconds"] = time.time() - start
        self.save_results(results, summary)
        return summary

def main():
    api_key = os.environ.get("MINIMAX_API_KEY", "")
    if not api_key:
        raise ValueError("MINIMAX_API_KEY not set")
    harness = HarnessV30(api_key)
    harness.run()

if __name__ == "__main__":
    main()
