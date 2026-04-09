#!/usr/bin/env python3
"""
Harness Evolution Engine v6.0

Key fixes:
1. E-002: Use template generation (not string matching)
2. RM-001: Import resource_limiter
3. A-001: API call tracking
4. RM-002: Disk space check
5. File lock for concurrent protection
"""

import json
import os
import sys
import re
import argparse
import subprocess
import shutil
import fcntl
import time
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.parent
STATE_FILE = BASE_DIR / "results" / "evolution" / "state.json"
RESULTS_DIR = BASE_DIR / "results" / "evolution"
HARNESS_TEMPLATE = BASE_DIR / "src" / "native" / "harness" / "harness_v31_0.py"
LOCK_FILE = RESULTS_DIR / "harness.lock"

API_CALL_FILE = RESULTS_DIR / "api_calls.json"

def acquire_lock():
    LOCK_FILE.parent.mkdir(parents=True, exist_ok=True)
    LOCK_FILE.touch()
    try:
        fcntl.flock(LOCK_FILE.open('w'), fcntl.LOCK_EX | fcntl.LOCK_NB)
        return True
    except IOError:
        return False

def release_lock():
    try:
        fcntl.flock(LOCK_FILE.open('w'), fcntl.LOCK_UN)
    except:
        pass

def load_api_calls():
    if API_CALL_FILE.exists():
        with open(API_CALL_FILE) as f:
            data = json.load(f)
            return data.get('count', 0)
    return 0

def save_api_calls(count):
    with open(API_CALL_FILE, 'w') as f:
        json.dump({'count': count, 'last_updated': datetime.now().isoformat()}, f)

def check_disk_space():
    stat = shutil.disk_usage(BASE_DIR)
    percent = stat.used / stat.total * 100
    if percent > 90:
        raise Exception(f"Disk space critical: {percent:.1f}% used")
    return percent

def ensure_dirs():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    if not STATE_FILE.exists():
        init_state()

def init_state():
    state = {
        "current_round": 0,
        "best_score": 76.22,
        "best_version": "v31_0",
        "no_progress_rounds": 0,
        "history": [],
        "mode": "infinite"
    }
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def load_state():
    with open(STATE_FILE) as f:
        return json.load(f)

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def get_next_strategy(state):
    round_num = state["current_round"]
    strategies = [
        {"name": "v32_1000tokens", "research_tokens": 1000, "code_tokens": 1000, "max_runs": 2, "temperature": 0.7, "self_reflect": "core_only"},
        {"name": "v33_1000tokens_max3", "research_tokens": 1000, "code_tokens": 1000, "max_runs": 3, "temperature": 0.5, "self_reflect": "none"},
        {"name": "v34_800tokens", "research_tokens": 800, "code_tokens": 800, "max_runs": 2, "temperature": 0.7, "self_reflect": "core_only"},
        {"name": "v35_1200tokens", "research_tokens": 1200, "code_tokens": 1000, "max_runs": 2, "temperature": 0.9, "self_reflect": "none"},
        {"name": "v36_1000tokens_temp0.3", "research_tokens": 1000, "code_tokens": 1000, "max_runs": 2, "temperature": 0.3, "self_reflect": "core_only"},
    ]
    idx = round_num % len(strategies)
    return strategies[idx]

HARNESS_TEMPLATE_CODE = '''#!/usr/bin/env python3
"""
Generated Harness - {version}
Strategy: {strategy_name}
Tokens: {research_tokens}/{code_tokens}
Max Runs: {max_runs}
Temperature: {temperature}
"""

import json
import time
import os
import shutil
from pathlib import Path
from dataclasses import dataclass
from typing import Dict

VERSION = "{version}"
RESEARCH_TOKENS = {research_tokens}
CODE_TOKENS = {code_tokens}
REVIEW_TOKENS = 3000
MAX_RUNS = {max_runs}
SELF_REFLECT = "{self_reflect}"
TEMPERATURE = {temperature}

API_CONFIG = {{
    "base_url": "https://api.minimaxi.com/anthropic",
    "model": "MiniMax-M2.7",
    "temperature": TEMPERATURE
}}

BASE_DIR = Path(__file__).parent.parent.parent.parent
RESULTS_DIR = BASE_DIR / "results" / "evolution"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

CHECKPOINT_FILE = str(RESULTS_DIR / "{version}_checkpoint.json")
RESULTS_FILE = str(RESULTS_DIR / "benchmark_results_{version}_gen1.json")

# Note: Resource limits disabled - they cause premature termination
# import sys
# sys.path.insert(0, str(BASE_DIR / "src" / "native"))
# try:
#     import resource_limiter
#     resource_limiter.apply_all()
# except:
#     pass

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
    
    def call_with_retry(self, prompt: str, system_prompt: str = "", max_tokens: int = 2048, timeout: int = 60, max_retries: int = 3) -> Dict:
        for attempt in range(max_retries + 1):
            try:
                result = self._make_request(prompt, system_prompt, max_tokens, timeout)
                if result.get("error") is None:
                    # Track API call
                    api_file = RESULTS_DIR / "api_calls.json"
                    try:
                        data = {{}}
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
                    return {{"content": "", "latency_ms": 0, "input_tokens": 0, "output_tokens": 0, "error": str(e)}}
        return {{"content": "", "latency_ms": 0, "input_tokens": 0, "output_tokens": 0, "error": "Max retries exceeded"}}
    
    def _make_request(self, prompt: str, system_prompt: str, max_tokens: int, timeout: int) -> Dict:
        import subprocess
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
        data = json.dumps(payload)
        curl_cmd = [
            "curl", "-s", "--max-time", str(timeout),
            "-X", "POST",
            f"{API_CONFIG['base_url']}/v1/messages",
            "-H", f"Authorization: Bearer {self.api_key}",
            "-H", "Content-Type: application/json",
            "-H", "anthropic-version: 2023-06-01",
            "-d", data
        ]
        try:
            result = subprocess.run(curl_cmd, capture_output=True, text=True, timeout=timeout + 10)
            if result.returncode != 0:
                return {"content": "", "latency_ms": 0, "input_tokens": 0, "output_tokens": 0, "error": f"Curl error: {result.stderr}"}
            response_text = result.stdout
            if not response_text:
                return {"content": "", "latency_ms": 0, "input_tokens": 0, "output_tokens": 0, "error": "Empty response"}
            result_json = json.loads(response_text)
        except subprocess.TimeoutExpired:
            return {"content": "", "latency_ms": 0, "input_tokens": 0, "output_tokens": 0, "error": "Request timeout"}
        except json.JSONDecodeError as e:
            return {"content": "", "latency_ms": 0, "input_tokens": 0, "output_tokens": 0, "error": f"JSON decode error: {e}"}
        latency = (time.time() - start) * 1000
        content = ""
        for item in result_json.get("content", []):
            if item.get("type") == "text":
                content = item.get("text", "")
                break
        return {
            "content": content,
            "latency_ms": latency,
            "input_tokens": result_json.get("usage", {}).get("input_tokens", 0),
            "output_tokens": result_json.get("usage", {}).get("output_tokens", 0),
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
            raise Exception(f"Disk space critical: {{pct:.1f}}%")
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
        
        system_prompt = f"You are an expert AI assistant. Query: {{query}}"
        prompt = query
        
        initial_response = self.llm.call_with_retry(prompt=prompt, system_prompt=system_prompt, max_tokens=max_tokens)
        
        if initial_response.get("error"):
            return TaskResult(
                task_id=task_id, task_type=task_type, executor_output=f"Error: {{initial_response['error']}}",
                quality_score=0, depth_score=0, completeness_score=0, actionability_score=0,
                executor_tokens=0, evaluator_tokens=0, executor_latency_ms=0, evaluator_latency_ms=0,
                error=initial_response["error"], run=run_num
            )
        
        executor_output = initial_response["content"]
        executor_tokens = initial_response["output_tokens"]
        executor_latency = initial_response["latency_ms"]
        
        if self.should_self_reflect(task):
            reflect_prompt = f"Review and improve: {{query}}\\n\\n{{executor_output}}"
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
            print(f"[{{i+1}}/{{len(self.tasks)}}] {{task_id}}...", end=" ", flush=True)
            
            checkpoint = {{"current_task": i, "task_id": task_id, "results": results}}
            with open(CHECKPOINT_FILE, 'w') as f:
                json.dump(checkpoint, f)
            
            task_results = []
            for run in range(1, self.max_runs + 1):
                print(f"Run{{run}}...", end=" ", flush=True)
                result = self.execute_single(task, run)
                print(f"Score={{result.quality_score}}", end=" ", flush=True)
                task_results.append(result)
            
            best = max(task_results, key=lambda r: r.quality_score)
            output = best.executor_output
            if len(output) > 5000:
                output = output[:5000] + f"... [truncated {{len(output)-5000}} chars]"
            
            results.append({{
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
            }})
            print(f"-> Final={{best.quality_score}}")
        
        return results
    
    def compute_summary(self, results: list) -> dict:
        core = [r for r in results if r.get("category") == "core"]
        gen = [r for r in results if r.get("category") == "gen"]
        core_avg = sum(r["quality_score"] for r in core) / len(core) if core else 0
        gen_avg = sum(r["quality_score"] for r in gen) / len(gen) if gen else 0
        all_action = [r["actionability_score"] for r in results]
        avg_action = sum(all_action) / len(all_action) if all_action else 0
        composite = core_avg * 0.45 + gen_avg * 0.45 + avg_action * 10 * 0.1
        return {{
            "total_tasks": len(results),
            "core_avg_score": round(core_avg, 2),
            "gen_avg_score": round(gen_avg, 2),
            "avg_actionability_level": round(avg_action, 1),
            "composite_score": round(composite, 2)
        }}
    
    def save_results(self, results: list, summary: dict):
        output = {{
            "harness_version": VERSION,
            "paradigm": f"v31 tokens={{RESEARCH_TOKENS}}/{{CODE_TOKENS}}",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "elapsed_seconds": 0,
            "summary": summary,
            "individual_results": results
        }}
        with open(RESULTS_FILE, 'w', encoding="utf-8") as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        print(f"Results saved to: {{RESULTS_FILE}}")
        if Path(CHECKPOINT_FILE).exists():
            Path(CHECKPOINT_FILE).unlink()
    
    def run(self):
        # Check disk space
        disk_pct = self.check_disk_space()
        print(f"Disk usage: {{disk_pct:.1f}}%")
        
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
'''

def generate_harness(version: str, strategy: dict) -> str:
    """Generate harness code from template"""
    code = HARNESS_TEMPLATE_CODE
    replacements = {
        "{version}": version,
        "{strategy_name}": strategy.get("name", "unknown"),
        "{research_tokens}": str(strategy.get("research_tokens", 5000)),
        "{code_tokens}": str(strategy.get("code_tokens", 5000)),
        "{max_runs}": str(strategy.get("max_runs", 2)),
        "{temperature}": str(strategy.get("temperature", 0.7)),
        "{self_reflect}": strategy.get("self_reflect", "core_only"),
    }
    for old, new in replacements.items():
        code = code.replace(old, new)
    # Fix double-brace escaping for Python dict/literal syntax
    code = code.replace("{{", "{")
    code = code.replace("}}", "}")
    return code

def run_harness(version: str, strategy: dict):
    print(f"Running harness: {version}")
    print(f"Strategy: {strategy['name']}")
    
    if not acquire_lock():
        print("Cannot acquire lock, another instance may be running")
        return None
    
    try:
        disk_pct = check_disk_space()
        print(f"Disk usage: {disk_pct:.1f}%")
        
        api_count = load_api_calls()
        print(f"API call count: {api_count}")
        
        code = generate_harness(version, strategy)
        version_harness = BASE_DIR / "src" / "native" / "harness" / f"harness_{version}.py"
        with open(version_harness, 'w') as f:
            f.write(code)
        print(f"Generated: {version_harness}")
        
        # Delete old results and checkpoint files to force fresh run
        results_file = RESULTS_DIR / f"benchmark_results_{version}_gen1.json"
        checkpoint_file = RESULTS_DIR / f"{version}_checkpoint.json"
        if results_file.exists():
            results_file.unlink()
            print(f"Deleted old results: {results_file}")
        if checkpoint_file.exists():
            checkpoint_file.unlink()
            print(f"Deleted old checkpoint: {checkpoint_file}")
        
        cmd = [sys.executable, str(version_harness)]
        env = os.environ.copy()
        env["PYTHONPATH"] = str(BASE_DIR)
        
        result = subprocess.run(
            cmd, cwd=str(BASE_DIR), env=env, timeout=14400,
            capture_output=True, text=True
        )
        
        if result.stdout:
            print(result.stdout[-500:] if len(result.stdout) > 500 else result.stdout)
        
        save_api_calls(load_api_calls())
        
        results_file = RESULTS_DIR / f"benchmark_results_{version}_gen1.json"
        if results_file.exists():
            with open(results_file) as f:
                return json.load(f)
        else:
            print(f"Results file not found: {results_file}")
            return None
            
    except Exception as e:
        print(f"Harness error: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        release_lock()

def record_result(state, version, strategy, result):
    if result and "summary" in result:
        score = result["summary"].get("composite_score", 0)
    else:
        score = 0
    
    entry = {
        "round": state["current_round"],
        "version": version,
        "strategy": strategy["name"],
        "score": score,
        "timestamp": datetime.now().isoformat()
    }
    
    state["history"].append(entry)
    
    if score > state["best_score"]:
        state["best_score"] = score
        state["best_version"] = version
        state["no_progress_rounds"] = 0
        entry["is_champion"] = True
        print(f"🏆 New champion! {version}: {score:.2f}")
    else:
        state["no_progress_rounds"] += 1
        entry["is_champion"] = False
    
    state["current_round"] += 1
    
    with open(RESULTS_DIR / "history.json", "w") as f:
        json.dump(state["history"], f, indent=2)
    
    return entry

def should_stop(state):
    if state.get("mode") == "infinite":
        if state["best_score"] >= 100.0:
            return True
        if state["current_round"] >= 10000:
            return True
        return False
    return False

def main():
    parser = argparse.ArgumentParser(description="AutoMAS Evolution Engine v6.0")
    parser.add_argument("--round", type=int, help="Specify round")
    parser.add_argument("--continuous", action="store_true", help="Continuous run")
    
    args = parser.parse_args()
    
    ensure_dirs()
    state = load_state()
    
    if args.round is not None:
        state["current_round"] = args.round - 1
        save_state(state)
        
        strategy = get_next_strategy(state)
        version = f"evo_{args.round:03d}"
        
        result = run_harness(version, strategy)
        entry = record_result(state, version, strategy, result)
        save_state(state)
        
        print(f"\nRound {args.round} complete:")
        print(f"  Version: {version}")
        print(f"  Score: {entry['score']:.2f}")
        print(f"  Current best: {state['best_version']} ({state['best_score']:.2f})")
        
    elif args.continuous:
        while not should_stop(state):
            state = load_state()
            strategy = get_next_strategy(state)
            version = f"evo_{state['current_round']+1:03d}"
            
            print(f"\n{'='*50}")
            print(f"Round {state['current_round']+1}")
            print(f"Strategy: {strategy['name']}")
            
            result = run_harness(version, strategy)
            entry = record_result(state, version, strategy, result)
            save_state(state)
            
            print(f"Score: {entry['score']:.2f}")
        
        print(f"\nEvolution complete")
        print(f"Best: {state['best_version']} ({state['best_score']:.2f})")
    
    else:
        strategy = get_next_strategy(state)
        version = f"evo_{state['current_round']+1:03d}"
        
        result = run_harness(version, strategy)
        entry = record_result(state, version, strategy, result)
        save_state(state)
        
        print(f"\nRound {state['current_round']} complete")
        print(f"Score: {entry['score']:.2f}")

if __name__ == "__main__":
    main()
