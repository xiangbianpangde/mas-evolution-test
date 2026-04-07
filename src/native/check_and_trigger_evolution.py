#!/usr/bin/env python3
"""
Check if evolution should run and trigger if needed

 Called by heartbeat mechanism
"""

import json
import os
import subprocess
import sys
from pathlib import Path

# 路径
BASE_DIR = Path(__file__).parent.parent.parent
STATE_FILE = BASE_DIR / "results" / "evolution" / "state.json"

def is_harness_running():
    """检查是否有 harness 正在运行"""
    try:
        result = subprocess.run(
            ["ps", "aux"],
            capture_output=True,
            text=True
        )
        # 检查是否有 python3 进程正在运行 harness (包括 harness_v* 和 harness_evo*)
        for line in result.stdout.split("\n"):
            if ("harness_v" in line or "harness_evo" in line) and "python" in line.lower():
                return True
        return False
    except:
        return False

def should_trigger_evolution(state):
    """检查是否应该触发进化"""
    if state.get("mode") != "infinite":
        return False
    
    if state.get("best_score", 0) >= 100.0:
        return False
    
    if state.get("current_round", 0) >= 10000:
        return False
    
    return True

def trigger_evolution(round_num):
    """触发一轮进化"""
    print(f"Triggering evolution round {round_num}")
    
    cmd = [
        sys.executable,
        str(BASE_DIR / "src" / "native" / "harness_evolution.py"),
        "--round", str(round_num)
    ]
    
    # 后台运行
    subprocess.Popen(
        cmd,
        cwd=str(BASE_DIR),
        stdout=open("/dev/null", "w"),
        stderr=open("/dev/null", "w")
    )

def main():
    # 检查是否有 harness 运行
    if is_harness_running():
        print("Harness is running, skipping trigger")
        sys.exit(0)
    
    # 读取状态
    if not STATE_FILE.exists():
        print("No state file, initializing...")
        state = {
            "current_round": 0,
            "best_score": 76.22,
            "best_version": "v31_0",
            "mode": "infinite"
        }
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(STATE_FILE, "w") as f:
            json.dump(state, f, indent=2)
    
    with open(STATE_FILE) as f:
        state = json.load(f)
    
    # 检查是否应该触发
    if should_trigger_evolution(state):
        next_round = state.get("current_round", 0) + 1
        trigger_evolution(next_round)
        print(f"Triggered round {next_round}")
    else:
        print(f"Should not trigger: mode={state.get('mode')}, score={state.get('best_score')}, round={state.get('current_round')}")

if __name__ == "__main__":
    main()
