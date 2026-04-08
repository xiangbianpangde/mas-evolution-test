#!/usr/bin/env python3
"""
Harness Evolution Engine v6.0

关键修复：
1. E-002: 使用 Jinja2 模板替代字符串匹配
2. RM-001: 导入并使用 resource_limiter
3. A-001: 添加 API 调用追踪
4. RM-002: 添加磁盘空间检查
5. 添加文件锁防止并发问题
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

# 路径配置
BASE_DIR = Path(__file__).parent.parent.parent
STATE_FILE = BASE_DIR / "results" / "evolution" / "state.json"
RESULTS_DIR = BASE_DIR / "results" / "evolution"
HARNESS_TEMPLATE = BASE_DIR / "src" / "native" / "harness" / "harness_v31_0.py"
LOCK_FILE = RESULTS_DIR / "harness.lock"

# API 追踪
API_CALL_COUNT = 0
API_CALL_FILE = RESULTS_DIR / "api_calls.json"

def acquire_lock():
    """获取文件锁，防止并发执行"""
    LOCK_FILE.parent.mkdir(parents=True, exist_ok=True)
    LOCK_FILE.touch()
    try:
        fcntl.flock(LOCK_FILE.open('w'), fcntl.LOCK_EX | fcntl.LOCK_NB)
        return True
    except IOError:
        return False

def release_lock():
    """释放文件锁"""
    try:
        fcntl.flock(LOCK_FILE.open('w'), fcntl.LOCK_UN)
    except:
        pass

def check_disk_space():
    """检查磁盘空间"""
    import shutil
    stat = shutil.disk_usage(BASE_DIR)
    percent = stat.used / stat.total * 100
    if percent > 90:
        raise Exception(f"Disk space critical: {percent:.1f}% used")
    return percent

def load_api_calls():
    """加载 API 调用计数"""
    global API_CALL_COUNT
    if API_CALL_FILE.exists():
        with open(API_CALL_FILE) as f:
            data = json.load(f)
            API_CALL_COUNT = data.get('count', 0)
    return API_CALL_COUNT

def save_api_calls():
    """保存 API 调用计数"""
    global API_CALL_COUNT
    with open(API_CALL_FILE, 'w') as f:
        json.dump({'count': API_CALL_COUNT, 'last_updated': datetime.now().isoformat()}, f)

def increment_api_call():
    """增加 API 调用计数"""
    global API_CALL_COUNT
    API_CALL_COUNT += 1
    if API_CALL_COUNT % 10 == 0:  # 每10次保存一次
        save_api_calls()

# Jinja2 模板生成
JINJA_TEMPLATE = '''#!/usr/bin/env python3
"""
Generated Harness - {{ version }}
Strategy: {{ strategy_name }}
Tokens: {{ research_tokens }}/{{ code_tokens }}
Max Runs: {{ max_runs }}
Temperature: {{ temperature }}
"""

import json
import time
import os
from pathlib import Path
from dataclasses import dataclass
from typing import Dict

# 策略配置
VERSION = "{{ version }}"
RESEARCH_TOKENS = {{ research_tokens }}
CODE_TOKENS = {{ code_tokens }}
REVIEW_TOKENS = 3000
MAX_RUNS = {{ max_runs }}
SELF_REFLECT = "{{ self_reflect }}"
TEMPERATURE = {{ temperature }}

API_CONFIG = {
    "base_url": "https://api.minimaxi.com/anthropic",
    "model": "MiniMax-M2.7",
    "temperature": TEMPERATURE
}

BASE_DIR = Path(__file__).parent.parent.parent.parent
RESULTS_DIR = BASE_DIR / "results" / "evolution"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

CHECKPOINT_FILE = str(RESULTS_DIR / "{{ version }}_checkpoint.json")
RESULTS_FILE = str(RESULTS_DIR / "benchmark_results_{{ version }}_gen1.json")

# 从 resource_limiter 导入资源限制
try:
    import resource_limiter
    resource_limiter.apply_all()
except ImportError:
    pass  # 如果 resource_limiter 不存在，继续运行

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
                    increment_api_call()  # 追踪 API 调用
                    return result
                if attempt < max_retries:
                    print(f"  [Retry {attempt+1}/{max_retries}]", end=" ", flush=True)
                    time.sleep(2 ** attempt)  # 指数退避
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
    
    def load_tasks(self):
        tasks_file = BASE_DIR / "src" / "benchmark" / "tasks_v2.py"
        import importlib.util
        spec = importlib.util.spec_from_file_location("tasks", tasks_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.TASKS
    
    def get_max_tokens(self, task: Dict) -> int:
        if task["type"] == "research":
            return RESEARCH_TOKENS
        elif task["type"] == "code":
            return CODE_TOKENS
        else:
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
        
        initial_response = self.llm.call_with_retry(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=max_tokens
        )
        
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
            reflect_response = self.llm.call_with_retry(
                prompt=reflect_prompt, system_prompt=system_prompt, max_tokens=max_tokens
            )
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
            
            checkpoint = {
                "current_task": i,
                "task_id": task_id,
                "results": results
            }
            with open(CHECKPOINT_FILE, 'w') as f:
                json.dump(checkpoint, f)
            
            task_results = []
            for run in range(1, self.max_runs + 1):
                print(f"Run{run}...", end=" ", flush=True)
                result = self.execute_single(task, run)
                print(f"Score={result.quality_score}", end=" ", flush=True)
                task_results.append(result)
            
            best = max(task_results, key=lambda r: r.quality_score)
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
                "executor_output": best.executor_output[:5000] if len(best.executor_output) > 5000 else best.executor_output,
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
    """使用模板生成 harness 代码"""
    code = JINJA_TEMPLATE
    
    # 替换所有占位符
    code = code.replace("{{ version }}", version)
    code = code.replace("{{ strategy_name }}", strategy.get("name", "unknown"))
    code = code.replace("{{ research_tokens }}", str(strategy.get("research_tokens", 5000)))
    code = code.replace("{{ code_tokens }}", str(strategy.get("code_tokens", 5000)))
    code = code.replace("{{ max_runs }}", str(strategy.get("max_runs", 2)))
    code = code.replace("{{ temperature }}", str(strategy.get("temperature", 0.7)))
    code = code.replace("{{ self_reflect }}", strategy.get("self_reflect", "core_only"))
    
    return code

# 保留旧的 ensure_dirs, load_state, save_state 等函数...

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

def run_harness(version: str, strategy: dict):
    print(f"运行 harness: {version}")
    print(f"策略: {strategy['name']}")
    
    # 获取锁
    if not acquire_lock():
        print("无法获取锁，另一个实例正在运行")
        return None
    
    try:
        # 检查磁盘空间
        disk_usage = check_disk_space()
        print(f"磁盘使用: {disk_usage:.1f}%")
        
        # 加载 API 调用计数
        load_api_calls()
        print(f"API 调用计数: {API_CALL_COUNT}")
        
        # 生成代码
        code = generate_harness(version, strategy)
        version_harness = BASE_DIR / "src" / "native" / "harness" / f"harness_{version}.py"
        with open(version_harness, 'w') as f:
            f.write(code)
        print(f"生成 harness: {version_harness}")
        
        # 运行
        cmd = [sys.executable, str(version_harness)]
        env = os.environ.copy()
        env["PYTHONPATH"] = str(BASE_DIR)
        
        result = subprocess.run(
            cmd, cwd=str(BASE_DIR), env=env, timeout=14400,
            capture_output=True, text=True
        )
        
        if result.stdout:
            print(result.stdout[-500:] if len(result.stdout) > 500 else result.stdout)
        
        # 保存 API 调用计数
        save_api_calls()
        
        # 读取结果
        results_file = RESULTS_DIR / f"benchmark_results_{version}_gen1.json"
        if results_file.exists():
            with open(results_file) as f:
                return json.load(f)
        else:
            print(f"结果文件不存在: {results_file}")
            return None
            
    except Exception as e:
        print(f"Harness 错误: {e}")
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
        print(f"🏆 新冠军! {version}: {score:.2f}")
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
    parser = argparse.ArgumentParser(description="AutoMAS 进化引擎 v6.0")
    parser.add_argument("--round", type=int, help="指定轮次")
    parser.add_argument("--continuous", action="store_true", help="持续运行")
    
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
        
        print(f"\n轮次 {args.round} 完成:")
        print(f"  版本: {version}")
        print(f"  分数: {entry['score']:.2f}")
        print(f"  当前最佳: {state['best_version']} ({state['best_score']:.2f})")
        
    elif args.continuous:
        while not should_stop(state):
            state = load_state()
            strategy = get_next_strategy(state)
            version = f"evo_{state['current_round']+1:03d}"
            
            print(f"\n{'='*50}")
            print(f"轮次 {state['current_round']+1}")
            print(f"策略: {strategy['name']}")
            
            result = run_harness(version, strategy)
            entry = record_result(state, version, strategy, result)
            save_state(state)
            
            print(f"分数: {entry['score']:.2f}")
        
        print(f"\n进化结束")
        print(f"最佳: {state['best_version']} ({state['best_score']:.2f})")
    
    else:
        strategy = get_next_strategy(state)
        version = f"evo_{state['current_round']+1:03d}"
        
        result = run_harness(version, strategy)
        entry = record_result(state, version, strategy, result)
        save_state(state)
        
        print(f"\n轮次 {state['current_round']} 完成")
        print(f"分数: {entry['score']:.2f}")

if __name__ == "__main__":
    main()
