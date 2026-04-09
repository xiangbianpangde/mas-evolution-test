#!/usr/bin/env python3
"""
Check if evolution should run and trigger if needed

Called by heartbeat mechanism (every ~10 min)
"""

import json
import os
import subprocess
import sys
import fcntl
import time
from pathlib import Path

# 路径
BASE_DIR = Path(__file__).parent.parent.parent
STATE_FILE = BASE_DIR / "results" / "evolution" / "state.json"
LOCK_FILE = BASE_DIR / "results" / "evolution" / "check.lock"

def acquire_lock():
    """获取锁防止重复执行"""
    LOCK_FILE.parent.mkdir(parents=True, exist_ok=True)
    LOCK_FILE.touch()
    try:
        fcntl.flock(LOCK_FILE.open('w'), fcntl.LOCK_EX | fcntl.LOCK_NB)
        return True
    except IOError:
        return False

def is_harness_running():
    """检查是否有 harness 正在运行"""
    try:
        result = subprocess.run(
            ["ps", "aux"],
            capture_output=True,
            text=True
        )
        # 检查是否有 python 进程正在运行 harness
        # 包括: harness_v*, harness_evo*, harness_evolution
        for line in result.stdout.split("\n"):
            if "python" in line.lower():
                # 排除 grep 自身和 check_and_trigger_evolution
                if "check_and_trigger" in line:
                    continue
                # 检查是否是 harness 相关进程
                if any(x in line for x in ["harness_v", "harness_evo", "harness_evolution"]):
                    return True
        return False
    except:
        return False

def should_trigger_evolution(state):
    """检查是否应该触发进化"""
    if state.get("mode") != "infinite":
        return False
    
    if state.get("best_score", 0) >= state.get("target_score", 100.0):
        return False
    
    if state.get("current_round", 0) >= state.get("max_rounds", 10000):
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
        stdout=open(BASE_DIR / "results" / "evolution" / "evo_run.log", "w"),
        stderr=open(BASE_DIR / "results" / "evolution" / "evo_err.log", "w")
    )

def main():
    # 获取锁防止重复执行
    if not acquire_lock():
        print("Another check is running, skipping")
        sys.exit(0)
    
    try:
        # 检查 API Key 是否设置 (关键！)
        if not os.environ.get("MINIMAX_API_KEY"):
            print("ERROR: MINIMAX_API_KEY not set - evolution cannot run")
            sys.exit(1)
        
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
                "no_progress_rounds": 0,
                "mode": "infinite",
                "target_score": 100.0,
                "max_rounds": 10000,
                "history": []
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
    finally:
        # 释放锁
        try:
            fcntl.flock(LOCK_FILE.open('w'), fcntl.LOCK_UN)
        except:
            pass

if __name__ == "__main__":
    main()