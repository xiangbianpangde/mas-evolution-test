#!/usr/bin/env python3
"""
AutoMAS Continuous Evolution Loop

持续进化引擎 - 自动化运行直到收敛或达到目标

机制：
1. 运行 benchmark
2. 检查是否新冠军
3. 如果更好：继续
4. 如果更差：调整策略重试
5. 如果 N 轮无进步：停止

用法:
    python3 evolution_loop.py [--max-rounds N] [--target-score X] [--no-limit]
"""

import json
import time
import os
import sys
import argparse
from datetime import datetime
from pathlib import Path

# 冠军分数
CHAMPION_SCORE = 76.22
CHAMPION_VERSION = "v31.0"

# 策略参数
TOKEN_CONFIGS = [
    {"name": "5000 tokens", "research": 5000, "code": 5000, "review": 3000},
    {"name": "4500 tokens", "research": 4500, "code": 4500, "review": 2500},
    {"name": "4000 tokens", "research": 4000, "code": 4000, "review": 2000},
    {"name": "5500 tokens", "research": 5500, "code": 5500, "review": 3000},
]

REFLECT_CONFIGS = [
    {"name": "core research only", "core_research": True, "gen_research": False, "code": False},
    {"name": "all research", "core_research": True, "gen_research": True, "code": False},
    {"name": "none", "core_research": False, "gen_research": False, "code": False},
]

MAX_RUNS_CONFIGS = [
    {"name": "MAX-1", "runs": 1},
    {"name": "MAX-2", "runs": 2},
]

class EvolutionLoop:
    def __init__(self, max_rounds=20, target_score=80.0, results_dir="results"):
        self.max_rounds = max_rounds
        self.target_score = target_score
        self.results_dir = Path(results_dir)
        self.current_round = 0
        self.best_score = CHAMPION_SCORE
        self.best_version = CHAMPION_VERSION
        self.no_progress_rounds = 0
        self.strategy_history = []
        
    def log(self, msg):
        """带时间戳的日志"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {msg}", flush=True)
        
    def get_next_strategy(self):
        """根据历史选择下一个策略"""
        # 如果多轮无进步，尝试完全不同的配置
        if self.no_progress_rounds >= 3:
            self.no_progress_rounds = 0
            return {
                "tokens": TOKEN_CONFIGS[self.current_round % len(TOKEN_CONFIGS)],
                "reflect": REFLECT_CONFIGS[(self.current_round // len(TOKEN_CONFIGS)) % len(REFLECT_CONFIGS)],
                "max_runs": MAX_RUNS_CONFIGS[self.current_round % len(MAX_RUNS_CONFIGS)]
            }
        
        # 正常轮转
        idx = self.current_round % len(TOKEN_CONFIGS)
        return {
            "tokens": TOKEN_CONFIGS[idx],
            "reflect": REFLECT_CONFIGS[0],  # 默认 core research only
            "max_runs": MAX_RUNS_CONFIGS[1]  # 默认 MAX-2
        }
    
    def run_benchmark(self, version_name, strategy):
        """运行 benchmark"""
        # 这里调用实际的 harness
        # 由于是模拟，返回一个随机分数
        import random
        base_score = 70 + random.uniform(-5, 10)
        return base_score
    
    def save_result(self, version_name, strategy, score):
        """保存结果"""
        result = {
            "version": version_name,
            "strategy": {
                "tokens": strategy["tokens"]["name"],
                "reflect": strategy["reflect"]["name"],
                "max_runs": strategy["max_runs"]["name"]
            },
            "score": score,
            "timestamp": datetime.now().isoformat(),
            "round": self.current_round
        }
        
        # 保存到结果目录
        result_file = self.results_dir / f"evolution_{version_name}.json"
        with open(result_file, "w") as f:
            json.dump(result, f, indent=2)
        
        return result
    
    def check_champion(self, score):
        """检查是否是新冠军"""
        if score > self.best_score:
            self.best_score = score
            self.no_progress_rounds = 0
            return True
        else:
            self.no_progress_rounds += 1
            return False
    
    def should_stop(self):
        """判断是否应该停止"""
        # 达到目标分数
        if self.best_score >= self.target_score:
            self.log(f"🎉 达到目标分数 {self.target_score}!")
            return True
        
        # 超过最大轮次
        if self.current_round >= self.max_rounds:
            self.log(f"达到最大轮次 {self.max_rounds}")
            return True
        
        # 多轮无进步
        if self.no_progress_rounds >= 5:
            self.log(f"连续 {self.no_progress_rounds} 轮无进步，停止")
            return True
        
        return False
    
    def run(self):
        """主循环"""
        self.log("🚀 启动持续进化引擎")
        self.log(f"目标: {self.target_score}, 当前冠军: {self.best_version} ({self.best_score})")
        
        while not self.should_stop():
            self.current_round += 1
            strategy = self.get_next_strategy()
            version_name = f"evo_{self.current_round:03d}"
            
            self.log(f"\n{'='*50}")
            self.log(f"Round {self.current_round}/{self.max_rounds}")
            self.log(f"策略: {strategy['tokens']['name']}, {strategy['reflect']['name']}, {strategy['max_runs']['name']}")
            
            # 运行 benchmark
            start_time = time.time()
            score = self.run_benchmark(version_name, strategy)
            elapsed = time.time() - start_time
            
            # 保存结果
            result = self.save_result(version_name, strategy, score)
            
            # 检查是否冠军
            is_champion = self.check_champion(score)
            
            self.log(f"分数: {score:.2f} (耗时: {elapsed/60:.1f}分钟)")
            
            if is_champion:
                self.log(f"🏆 新冠军! {version_name}: {score:.2f}")
                self.best_version = version_name
            else:
                self.log(f"当前最佳: {self.best_version}: {self.best_score:.2f}")
            
            # 记录历史
            self.strategy_history.append({
                "round": self.current_round,
                "version": version_name,
                "strategy": strategy,
                "score": score,
                "is_champion": is_champion
            })
            
            # 保存历史
            history_file = self.results_dir / "evolution_history.json"
            with open(history_file, "w") as f:
                json.dump(self.strategy_history, f, indent=2)
        
        self.log("\n" + "="*50)
        self.log("🏁 进化循环结束")
        self.log(f"最佳版本: {self.best_version}, 分数: {self.best_score:.2f}")
        
        return {
            "best_version": self.best_version,
            "best_score": self.best_score,
            "total_rounds": self.current_round,
            "history": self.strategy_history
        }


def main():
    parser = argparse.ArgumentParser(description="AutoMAS 持续进化引擎")
    parser.add_argument("--max-rounds", type=int, default=20, help="最大轮次")
    parser.add_argument("--target-score", type=float, default=80.0, help="目标分数")
    parser.add_argument("--results-dir", type=str, default="results/evolution", help="结果目录")
    parser.add_argument("--no-limit", action="store_true", help="无限运行直到目标")
    
    args = parser.parse_args()
    
    # 创建结果目录
    os.makedirs(args.results_dir, exist_ok=True)
    
    # 创建引擎
    max_rounds = float('inf') if args.no_limit else args.max_rounds
    engine = EvolutionLoop(
        max_rounds=max_rounds,
        target_score=args.target_score,
        results_dir=args.results_dir
    )
    
    # 运行
    result = engine.run()
    
    # 输出最终结果
    print("\n最终结果:")
    print(json.dumps(result, indent=2))
    
    return 0 if result["best_score"] >= args.target_score else 1


if __name__ == "__main__":
    sys.exit(main())
