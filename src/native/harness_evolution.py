#!/usr/bin/env python3
"""
AutoMAS Evolution Engine - 进化引擎 v5.0

使用 v31_0 作为基础模板,通过策略参数修改关键配置
修复: RESULTS_DIR 必须在 CHECKPOINT_FILE/RESULTS_FILE 之前定义
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
    """策略生成:基于已知最优 v31.0 (5000 tokens) 进行有方向性探索。

    已知事实:
    - 5000 tokens 是最优(v31.0 验证)
    - 选择性自评审(仅 core research)有效
    - MAX-2 策略最优(v31.0)

    探索方向(不在已验证区间内搜索):
    """
    round_num = state["current_round"]

    # 策略:以 v31.0 (5000 tokens) 为中心,向外探索未验证方向
    strategies = [
        # 基线:完全复制 v31.0(验证可复现性)
        {"name": "v32_v31_clone", "research_tokens": 5000, "code_tokens": 5000, "max_runs": 2, "temperature": 0.7},

        # 方向1:增加 token 上限(探索更长上下文是否有用)
        {"name": "v33_6000tokens", "research_tokens": 6000, "code_tokens": 6000, "max_runs": 2, "temperature": 0.7},

        # 方向2:降低 temperature(更确定性输出)
        {"name": "v34_5000tokens_temp0.3", "research_tokens": 5000, "code_tokens": 5000, "max_runs": 2, "temperature": 0.3},

        # 方向3:提高 temperature(更多样化输出)
        {"name": "v35_5000tokens_temp0.9", "research_tokens": 5000, "code_tokens": 5000, "max_runs": 2, "temperature": 0.9},

        # 方向4:延长 review tokens(review 任务可能需要更多上下文)
        {"name": "v36_review3500", "research_tokens": 5000, "code_tokens": 5000, "review_tokens": 3500, "max_runs": 2, "temperature": 0.7},
    ]

    idx = round_num % len(strategies)
    return strategies[idx]

def apply_strategy_to_code(code: str, strategy: dict, version: str) -> str:
    """将策略参数应用到 harness 代码"""

    # 0. 首先添加 RESULTS_DIR 定义(如果不存在)
    if "RESULTS_DIR" not in code:
        # 在 import os 之后插入 RESULTS_DIR
        code = code.replace(
            "import os",
            "import os\nfrom pathlib import Path\n\nRESULTS_DIR = Path(__file__).parent.parent.parent.parent / \"results\" / \"evolution\"\nRESULTS_DIR.mkdir(parents=True, exist_ok=True)"
        )

    # 1. 修改 RESULTS_FILE - 使用 RESULTS_DIR
    results_file = f"str(RESULTS_DIR / \"benchmark_results_{version}_gen1.json\")"
    code = re.sub(
        r'RESULTS_FILE = "[^"]*"',
        f'RESULTS_FILE = {results_file}',
        code
    )

    # 2. 修改 CHECKPOINT_FILE - 使用 RESULTS_DIR
    checkpoint_file = f"str(RESULTS_DIR / \"{version}_checkpoint.json\")"
    code = re.sub(
        r'CHECKPOINT_FILE = "[^"]*"',
        f'CHECKPOINT_FILE = {checkpoint_file}',
        code
    )

    # 3. 修改 max_tokens 返回值
    research_tokens = strategy.get("research_tokens", 5000)
    code_tokens = strategy.get("code_tokens", 5000)
    review_tokens = strategy.get("review_tokens", 3000)

    old_func = '''    def get_max_tokens(self, task: Dict) -> int:
        """v30: Increase tokens for research tasks"""
        if task["type"] == "research":
            return 5000  # Increased from 4000
        elif task["type"] == "code":
            return 5000  # Increased from 4000
        else:
            return 3000'''

    new_func = f'''    def get_max_tokens(self, task: Dict) -> int:
        """v31 Evolved: Strategy={strategy['name']}"""
        if task["type"] == "research":
            return {research_tokens}
        elif task["type"] == "code":
            return {code_tokens}
        else:
            return {review_tokens}'''

    code = code.replace(old_func, new_func)

    # 4. 修改 max_runs
    max_runs = strategy.get("max_runs", 2)

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

    # 5. 修改运行次数引用 - v31_0 使用硬编码的双运行模式,需要替换为循环
    # 查找并替换硬编码的双运行模式
    old_run_pattern = '''            result1 = self.execute_single(task, run_num=1)
            print(f"  Run1: {result1.quality_score:.1f}")

            result2 = self.execute_single(task, run_num=2)
            print(f"  Run2: {result2.quality_score:.1f}")

            best = result1 if result1.quality_score >= result2.quality_score else result2
            print(f"  BEST: {best.quality_score:.1f}")'''

    new_run_pattern = f'''            # 使用 self.max_runs ({max_runs}) 进行多次运行,选择最佳结果
            results = []
            for run_i in range(1, self.max_runs + 1):
                result = self.execute_single(task, run_num=run_i)
                print(f"  Run{{run_i}}: {{result.quality_score:.1f}}")
                results.append(result)

            best = max(results, key=lambda r: r.quality_score)
            print(f"  BEST: {{best.quality_score:.1f}}")'''

    code = code.replace(old_run_pattern, new_run_pattern)

    # 5.1 修复 checkpoint 字典中的 run1_score/run2_score 引用
    # 原来硬编码 result1/result2，现在使用 results 列表
    old_checkpoint_scores = '''                "run1_score": result1.quality_score,
                "run2_score": result2.quality_score'''
    
    new_checkpoint_scores = '''                "run1_score": results[0].quality_score if len(results) > 0 else 0,
                "run2_score": results[1].quality_score if len(results) > 1 else 0'''
    
    code = code.replace(old_checkpoint_scores, new_checkpoint_scores)

    # 6. 修改 temperature
    temp = strategy.get("temperature", 0.7)
    # 在 messages 之后添加 temperature
    code = re.sub(
        r'"messages": \[{"role": "user", "content": prompt\}]',
        f'"temperature": {temp},\n            "messages": [{{"role": "user", "content": prompt}}]',
        code
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
    parser = argparse.ArgumentParser(description="AutoMAS 进化引擎 v5.0")
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