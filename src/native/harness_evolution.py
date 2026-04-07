#!/usr/bin/env python3
"""
AutoMAS Evolution Engine - 进化引擎

设计原则:
1. 无状态 - 所有状态存储在 JSON 文件
2. 可中断 - 每轮独立，可安全中断
3. 可触发 - 支持 cron 或手动触发

用法:
    python3 harness_evolution.py --round 1 --strategy '{"tokens":5000,"reflect":"core_only","max_runs":2}'
"""

import json
import os
import sys
import argparse
import subprocess
import shutil
from datetime import datetime
from pathlib import Path

# 路径配置
BASE_DIR = Path(__file__).parent.parent.parent
STATE_FILE = BASE_DIR / "results" / "evolution" / "state.json"
RESULTS_DIR = BASE_DIR / "results" / "evolution"
HARNESS_TEMPLATE = BASE_DIR / "src" / "native" / "harness" / "harness_v{version}.py"

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
        "history": []
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
    """获取下一个策略"""
    round_num = state["current_round"]
    
    # 策略池
    strategies = [
        {"name": "5000tokens_core_reflect", "tokens": 5000, "reflect": "core_only", "max_runs": 2},
        {"name": "5000tokens_all_reflect", "tokens": 5000, "reflect": "all", "max_runs": 2},
        {"name": "4500tokens", "tokens": 4500, "reflect": "core_only", "max_runs": 2},
        {"name": "5500tokens", "tokens": 5500, "reflect": "core_only", "max_runs": 2},
        {"name": "MAX1_6000tokens", "tokens": 6000, "reflect": "none", "max_runs": 1},
    ]
    
    idx = round_num % len(strategies)
    return strategies[idx]

def run_harness(version, strategy):
    """运行 harness"""
    print(f"运行 harness: {version}")
    print(f"策略: {strategy}")
    
    # 创建版本特定的 harness
    version_harness = BASE_DIR / "src" / "native" / "harness" / f"harness_{version}.py"
    
    if not version_harness.exists():
        # 复制模板并修改
        shutil.copy(BASE_DIR / "src" / "native" / "harness" / "harness_v31_0.py", version_harness)
    
    # 运行
    cmd = [sys.executable, str(version_harness)]
    env = os.environ.copy()
    env["PYTHONPATH"] = str(BASE_DIR)
    
    try:
        result = subprocess.run(
            cmd,
            cwd=str(BASE_DIR),
            env=env,
            timeout=86400,  # 24小时超时
            capture_output=True,
            text=True
        )
        
        # 读取结果
        results_file = RESULTS_DIR / f"benchmark_results_{version}_gen1.json"
        if results_file.exists():
            with open(results_file) as f:
                return json.load(f)
        else:
            return None
            
    except subprocess.TimeoutExpired:
        print(f"Harness 超时!")
        return None
    except Exception as e:
        print(f"Harness 错误: {e}")
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
        "strategy": strategy,
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
    """判断是否应该停止 - 无限进化，永不停止"""
    # 无限模式：永不自动停止
    # 仅当达到极端情况时停止
    if state["best_score"] >= 100.0:
        print(f"🎉 达到满分 100.0!")
        return True
    
    if state["current_round"] >= 10000:
        print(f"达到安全上限 10000 轮，停止")
        return True
    
    return False

def main():
    parser = argparse.ArgumentParser(description="AutoMAS 进化引擎")
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
        # 指定轮次模式
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
        # 持续运行模式
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
        # 单轮模式
        strategy = get_next_strategy(state)
        version = f"evo_{state['current_round']+1:03d}"
        
        result = run_harness(version, strategy)
        entry = record_result(state, version, strategy, result)
        save_state(state)
        
        print(f"\n轮次 {state['current_round']} 完成")
        print(f"分数: {entry['score']:.2f}")

if __name__ == "__main__":
    main()
