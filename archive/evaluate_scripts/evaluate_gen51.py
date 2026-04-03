#!/usr/bin/env python3
"""
MAS Evaluator - Generation 51 Benchmark
Gen38 冠军复制 + 最后一次突破尝试
"""

import sys
import json
import time
from datetime import datetime

sys.path.insert(0, '/root/.openclaw/workspace/mas_repo')

from benchmark.tasks import BenchmarkSuite, get_baseline_single_agent
from mas.core_gen51 import create_mas_system
from dataclasses import asdict

def run_evaluation():
    print("=" * 60)
    print("MAS Evolution Engine - Gen51 Benchmark")
    print("Final Attempt: Gen38 Clone + Micro-Tuning")
    print("=" * 60)
    
    mas = create_mas_system()
    benchmark = BenchmarkSuite()
    baseline = get_baseline_single_agent()
    
    print(f"\n[基线] 单Agent: 完成率 {baseline['success_rate']*100:.1f}%, 得分 {baseline['avg_score']:.1f}, Token {baseline['avg_tokens']}")
    
    print(f"\n[测试] 运行 {len(benchmark.tasks)} 个任务...")
    results, summary = benchmark.run_all(mas)
    
    print(f"\n[结果]")
    print(f"  - 完成率: {summary['success_rate']*100:.1f}%")
    print(f"  - 平均得分: {summary['avg_score']:.1f}")
    print(f"  - Token开销: {summary['avg_tokens']:.1f}/task")
    print(f"  - 效率指数: {summary['efficiency']:.1f}")
    
    # 对比Gen38
    gen38_score = 81.0
    gen38_tokens = 5.1
    gen38_efficiency = 15882
    
    print(f"\n[对比Gen38冠军]")
    score_diff = summary['avg_score'] - gen38_score
    token_diff = (summary['avg_tokens'] - gen38_tokens) / gen38_tokens * 100
    efficiency_diff = (summary['efficiency'] - gen38_efficiency) / gen38_efficiency * 100
    print(f"  - 得分差异: {score_diff:+.1f}")
    print(f"  - Token变化: {token_diff:+.1f}%")
    print(f"  - Efficiency变化: {efficiency_diff:+.1f}%")
    
    # 判断
    if summary['avg_score'] > gen38_score and summary['efficiency'] > gen38_efficiency:
        verdict = "🏆🏆🏆 新冠军! 得分和效率双突破!"
    elif summary['avg_score'] >= gen38_score and summary['avg_tokens'] < gen38_tokens:
        verdict = "🏆🏆 新冠军! Token效率提升"
    elif summary['efficiency'] > gen38_efficiency * 1.01:
        verdict = "🏆 新冠军! Efficiency提升"
    else:
        verdict = "⚠️ 未超越Gen38 - 系统已收敛"
    
    print(f"\n[判定] {verdict}")
    
    return {
        "timestamp": datetime.now().isoformat(),
        "generation": 51,
        "summary": summary,
        "gen38_reference": {
            "score": gen38_score,
            "tokens": gen38_tokens,
            "efficiency": gen38_efficiency
        },
        "verdict": verdict,
        "individual_results": [asdict(r) for r in results]
    }

if __name__ == "__main__":
    result = run_evaluation()
    output_file = "/root/.openclaw/workspace/mas_repo/benchmark_results_gen51.json"
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"\n结果已保存至: {output_file}")