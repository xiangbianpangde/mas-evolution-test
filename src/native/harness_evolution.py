#!/usr/bin/env python3
"""
AutoMAS Evolution Engine - 进化引擎 v4.0

使用 v31_0 作为基础模板，通过策略参数修改关键配置
"""

import json
import os
import sys
import re
import argparse
import subprocess
import shutil
from datetime import datetime
from pathlib import Path

# 路径配置
BASE_DIR = Path(__file__).parent.parent.parent
STATE_FILE = BASE_DIR / "results" / "evolution" / "state.json"
RESULTS_DIR = BASE_DIR / "results" / "evolution"
HARNESS_TEMPLATE = BASE_DIR / "src" / "native" / "harness" / "harness_v31_0.py"

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
        {"name": "v32_6000tokens", "research_tokens": 6000, "code_tokens": 5500, "max_runs": 2, "temperature": 0.7},
        {"name": "v33_7000tokens", "research_tokens": 7000, "code_tokens": 6000, "max_runs": 2, "temperature": 0.7},
        {"name": "v34_5000max3", "research_tokens": 5000, "code_tokens": 5000, "max_runs": 3, "temperature": 0.5},
        {"name": "v35_8000tokens", "research_tokens": 8000, "code_tokens": 7000, "max_runs": 1, "temperature": 0.9},
        {"name": "v36_5500tokens", "research_tokens": 5500, "code_tokens": 5000, "max_runs": 2, "temperature": 0.7},
    ]
    
    idx = round_num % len(strategies)
    return strategies[idx]

def apply_strategy_to_code(code: str, strategy: dict, version: str) -> str:
    """将策略参数应用到 harness 代码"""
    
    # 1. 修改 max_tokens 返回值
    research_tokens = strategy.get("research_tokens", 6000)
    code_tokens = strategy.get("code_tokens", 5500)
    
    # 替换 get_max_tokens 函数
    old_func = '''    def get_max_tokens(self, task: Dict) -> int:
        """v30: Increase tokens for research tasks"""
        if task["type"] == "research":
            return 5000  # Increased from 4000
        elif task["type"] == "code":
            return 5000  # Increased from 4000
        else:
            return 3000'''
    
    new_func = f'''    def get_max_tokens(self, task: Dict) -> int:
        """v31 Evolved: Strategy-based tokens"""
        if task["type"] == "research":
            return {research_tokens}
        elif task["type"] == "code":
            return {code_tokens}
        else:
            return 3000'''
    
    code = code.replace(old_func, new_func)
    
    # 2. 修改 MAX_RUNS（如果定义了）
    max_runs = strategy.get("max_runs", 2)
    
    # 在初始化时设置实例变量
    old_init = '''class HarnessV30:
    def __init__(self, api_key: str):
        self.llm = RealLLMCaller(api_key)
        self.api_key = api_key'''
    
    new_init = f'''class HarnessV30:
    def __init__(self, api_key: str):
        self.llm = RealLLMCaller(api_key)
        self.api_key = api_key
        self.max_runs = {max_runs}'''
    
    code = code.replace(old_init, new_init)
    
    # 3. 修改 execute_single 中的运行次数
    old_run_pattern = r'for run in range\(1, MAX_RUNS \+ 1\):'
    code = re.sub(old_run_pattern, f'for run in range(1, self.max_runs + 1):', code)
    
    # 4. 修改 temperature
    temp = strategy.get("temperature", 0.7)
    # 在 API payload 中添加 temperature
    code = re.sub(
        r'"max_tokens": max_tokens',
        f'"max_tokens": max_tokens',
        code
    )
    
    # 在 messages 之后添加 temperature
    code = re.sub(
        r'"messages": \[{"role": "user", "content": prompt\}\]',
        f'"temperature": {temp},\n            "messages": [{{"role": "user", "content": prompt}}]',
        code
    )
    
    # 5. 修改 RESULTS_FILE 路径 - 使用完整路径
    results_file = f"str(RESULTS_DIR / \"benchmark_results_{version}_gen1.json\")"
    code = re.sub(
        r'RESULTS_FILE = "[^"]*_gen1\.json"',
        f'RESULTS_FILE = {results_file}',
        code
    )
    
    # 6. 修改 CHECKPOINT_FILE - 使用完整路径
    checkpoint_file = f"str(RESULTS_DIR / \"{version}_checkpoint.json\")"
    code = re.sub(
        r'CHECKPOINT_FILE = "[^"]*\.json"',
        f'CHECKPOINT_FILE = {checkpoint_file}',
        code
    )
    
    # 7. 确保 RESULTS_DIR 存在并使用正确路径
    if "RESULTS_DIR" not in code:
        code = code.replace(
            "import os",
            "import os\nfrom pathlib import Path"
        )
        code = code.replace(
            "CHECKPOINT_FILE = ",
            "RESULTS_DIR = Path(__file__).parent.parent.parent / \"results\" / \"evolution\"\nRESULTS_DIR.mkdir(parents=True, exist_ok=True)\n\nCHECKPOINT_FILE = "
        )
        code = code.replace(
            'CHECKPOINT_FILE = f"{version}_checkpoint.json"',
            f'CHECKPOINT_FILE = str(RESULTS_DIR / "{checkpoint_file}")'
        )
    
    return code

def run_harness(version: str, strategy: dict):
    print(f"运行 harness: {version}")
    print(f"策略: {strategy['name']}")
    
    # 读取模板
    with open(HARNESS_TEMPLATE, 'r') as f:
        code = f.read()
    
    # 应用策略
    code = apply_strategy_to_code(code, strategy, version)
    
    # 写入生成的文件
    version_harness = BASE_DIR / "src" / "native" / "harness" / f"harness_{version}.py"
    with open(version_harness, 'w') as f:
        f.write(code)
    print(f"生成 harness: {version_harness}")
    
    # 运行
    cmd = [sys.executable, str(version_harness)]
    env = os.environ.copy()
    env["PYTHONPATH"] = str(BASE_DIR)
    
    try:
        result = subprocess.run(
            cmd,
            cwd=str(BASE_DIR),
            env=env,
            timeout=14400,
            capture_output=True,
            text=True
        )
        
        if result.stdout:
            print(result.stdout[-1000:] if len(result.stdout) > 1000 else result.stdout)
        if result.stderr and "Error" in result.stderr:
            print(f"STDERR: {result.stderr[-500:]}")
        
        # 读取结果
        results_file = RESULTS_DIR / f"benchmark_results_{version}_gen1.json"
        if results_file.exists():
            with open(results_file) as f:
                return json.load(f)
        else:
            print(f"结果文件不存在: {results_file}")
            return None
            
    except subprocess.TimeoutExpired:
        print(f"Harness 超时!")
        return None
    except Exception as e:
        print(f"Harness 错误: {e}")
        import traceback
        traceback.print_exc()
        return None

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
    
    history_file = RESULTS_DIR / "history.json"
    with open(history_file, "w") as f:
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
    parser = argparse.ArgumentParser(description="AutoMAS 进化引擎 v4.0")
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