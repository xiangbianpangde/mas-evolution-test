#!/usr/bin/env python3
"""
AutoMAS Evolution Engine - 进化引擎 v3.0

设计原则:
1. 无状态 - 所有状态存储在 JSON 文件
2. 可中断 - 每轮独立，可安全中断
3. 可触发 - 支持 cron 或手动触发
4. 策略驱动 - 根据策略动态生成 harness 代码

v3.0: 使用专用模板，正确应用所有策略参数
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
HARNESS_TEMPLATE = BASE_DIR / "src" / "native" / "harness" / "harness_template.py"

def ensure_dirs():
    """确保目录存在"""
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    if not STATE_FILE.exists():
        init_state()

def init_state():
    """初始化状态"""
    state = {
        "current_round": 0,
        "best_score": 76.22,
        "best_version": "v31_0",
        "no_progress_rounds": 0,
        "target_score": 80.0,
        "max_rounds": 50,
        "history": [],
        "mode": "infinite"
    }
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def load_state():
    """加载状态"""
    with open(STATE_FILE) as f:
        return json.load(f)

def save_state(state):
    """保存状态"""
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def get_next_strategy(state):
    """获取下一个策略 - 真正多样化的策略"""
    round_num = state["current_round"]
    
    strategies = [
        {"name": "high_tokens_dual_reflect", "research_tokens": 6000, "code_tokens": 5500, "review_tokens": 3000, "max_runs": 2, "self_reflect": "core_only", "temperature": 0.7},
        {"name": "ultra_high_all_reflect", "research_tokens": 7000, "code_tokens": 6000, "review_tokens": 4000, "max_runs": 2, "self_reflect": "all", "temperature": 0.7},
        {"name": "balanced_max3", "research_tokens": 5000, "code_tokens": 5000, "review_tokens": 3000, "max_runs": 3, "self_reflect": "none", "temperature": 0.5},
        {"name": "very_high_no_reflect", "research_tokens": 8000, "code_tokens": 7000, "review_tokens": 4000, "max_runs": 1, "self_reflect": "none", "temperature": 0.9},
        {"name": "medium_enhanced_reflect", "research_tokens": 5500, "code_tokens": 5000, "review_tokens": 3000, "max_runs": 2, "self_reflect": "enhanced", "temperature": 0.7},
    ]
    
    idx = round_num % len(strategies)
    return strategies[idx]

def generate_harness_from_template(version: str, strategy: dict) -> str:
    """根据策略生成新的 harness 代码"""
    with open(HARNESS_TEMPLATE, 'r') as f:
        code = f.read()
    
    # 替换版本号
    code = code.replace('VERSION = "template"', f'VERSION = "{version}"')
    
    # 替换 token 配置
    code = code.replace('RESEARCH_TOKENS = 5000', f'RESEARCH_TOKENS = {strategy.get("research_tokens", 5000)}')
    code = code.replace('CODE_TOKENS = 5000', f'CODE_TOKENS = {strategy.get("code_tokens", 5000)}')
    code = code.replace('REVIEW_TOKENS = 3000', f'REVIEW_TOKENS = {strategy.get("review_tokens", 3000)}')
    
    # 替换策略配置
    code = code.replace('MAX_RUNS = 2', f'MAX_RUNS = {strategy.get("max_runs", 2)}')
    code = code.replace('SELF_REFLECT = "core_only"', f'SELF_REFLECT = "{strategy.get("self_reflect", "core_only")}"')
    code = code.replace('TEMPERATURE = 0.7', f'TEMPERATURE = {strategy.get("temperature", 0.7)}')
    
    return code

def run_harness(version: str, strategy: dict):
    """运行 harness - 根据策略生成并运行"""
    print(f"运行 harness: {version}")
    print(f"策略: {strategy['name']}")
    
    # 生成 harness 代码
    harness_code = generate_harness_from_template(version, strategy)
    version_harness = BASE_DIR / "src" / "native" / "harness" / f"harness_{version}.py"
    with open(version_harness, 'w') as f:
        f.write(harness_code)
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
            timeout=14400,  # 4小时超时
            capture_output=True,
            text=True
        )
        
        # 打印输出便于调试
        if result.stdout:
            print(result.stdout[-1000:] if len(result.stdout) > 1000 else result.stdout)
        if result.stderr:
            print(f"STDERR: {result.stderr[-500:]}")
        
        # 读取结果
        results_file = RESULTS_DIR / f"benchmark_results_{version}_gen1.json"
        if results_file.exists():
            with open(results_file) as f:
                return json.load(f)
        else:
            # 尝试其他可能的路径
            alt_results = RESULTS_DIR / "results.json"
            if alt_results.exists():
                shutil.move(alt_results, results_file)
                with open(results_file) as f:
                    return json.load(f)
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
    """记录结果"""
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
    
    # 检查是否新冠军
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
    
    # 保存历史
    history_file = RESULTS_DIR / "history.json"
    with open(history_file, "w") as f:
        json.dump(state["history"], f, indent=2)
    
    return entry

def should_stop(state):
    """判断是否应该停止"""
    if state.get("mode") == "infinite":
        if state["best_score"] >= 100.0:
            print(f"🎉 达到满分 100.0!")
            return True
        if state["current_round"] >= 10000:
            print(f"达到安全上限 10000 轮，停止")
            return True
        return False
    
    if state["no_progress_rounds"] >= 10 and len(state["history"]) >= 10:
        recent = state["history"][-10:]
        avg = sum(h["score"] for h in recent) / 10
        first = recent[0]["score"]
        if abs(avg - first) < 1.0:
            print(f"📊 范式收敛: 连续10轮提升<1%")
            return True
    return False

def main():
    parser = argparse.ArgumentParser(description="AutoMAS 进化引擎 v3.0")
    parser.add_argument("--round", type=int, help="指定轮次")
    parser.add_argument("--strategy", type=str, help="指定策略 (JSON)")
    parser.add_argument("--continuous", action="store_true", help="持续运行")
    parser.add_argument("--max-rounds", type=int, help="最大轮次")
    
    args = parser.parse_args()
    
    ensure_dirs()
    state = load_state()
    
    if args.max_rounds:
        state["max_rounds"] = args.max_rounds
        save_state(state)
    
    if args.round is not None:
        state["current_round"] = args.round - 1
        save_state(state)
        
        if args.strategy:
            strategy = json.loads(args.strategy)
        else:
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