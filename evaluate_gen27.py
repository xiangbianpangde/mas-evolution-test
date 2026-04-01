#!/usr/bin/env python3
"""
MAS Evaluator - Generation 27 Benchmark
测试 Ultra-Precise Token Optimization 架构
"""

import sys
import json
import time
from datetime import datetime

sys.path.insert(0, '/root/.openclaw/workspace/mas_repo')

from benchmark.tasks import BenchmarkSuite, get_baseline_single_agent
from mas.core_gen27 import create_mas_system
from dataclasses import asdict

def run_evaluation():
    print("=" * 60)
    print("MAS Evolution Engine - Gen27 Benchmark")
    print("Ultra-Precise Token Optimization")
    print("=" * 60)
    
    mas = create_mas_system()
    benchmark = BenchmarkSuite()
    baseline = get_baseline_single_agent()
    
    print(f"\n[基线] 单Agent系统:")
    print(f"  - 任务完成率: {baseline['success_rate']*100:.1f}%")
    print(f"  - 平均得分: {baseline['avg_score']:.1f}")
    print(f"  - Token效率: {baseline['avg_tokens']:.0f}/task")
    
    print(f"\n[测试] 开始运行 {len(benchmark.tasks)} 个任务...")
    results, summary = benchmark.run_all(mas)
    
    print(f"\n[结果汇总]")
    print(f"  - 任务完成率: {summary['success_rate']*100:.1f}%")
    print(f"  - 平均得分: {summary['avg_score']:.1f}/100")
    print(f"  - Token开销: {summary['avg_tokens']:.0f}/task")
    print(f"  - 平均延迟: {summary['avg_latency_ms']:.0f}ms")
    print(f"  - 效率指数: {summary['efficiency']:.4f}")
    
    # 对比Gen26
    gen26_score = 81.0
    gen26_tokens = 33.4
    gen26_efficiency = 2425
    gen26_completion = 1.0
    
    print(f"\n[对比Gen26]")
    score_diff = summary['avg_score'] - gen26_score
    token_diff = (summary['avg_tokens'] - gen26_tokens) / gen26_tokens * 100
    eff_diff = (summary['efficiency'] - gen26_efficiency) / gen26_efficiency * 100
    print(f"  - 得分差异: {score_diff:+.1f}")
    print(f"  - Token变化: {token_diff:+.1f}%")
    print(f"  - Efficiency变化: {eff_diff:+.1f}%")
    
    # 计算综合评分
    completion_weight = 0.4
    score_weight = 0.3
    efficiency_weight = 0.2
    latency_weight = 0.1
    
    latency_score = max(0, 100 - summary['avg_latency_ms'] / 1000)
    
    composite = (
        summary['success_rate'] * 100 * completion_weight +
        summary['avg_score'] * score_weight +
        summary['efficiency'] * efficiency_weight +
        latency_score * latency_weight
    )
    
    print(f"\n[综合评分] {composite:.2f}/100")
    
    # 判断目标达成
    targets_met = []
    if summary['avg_score'] >= 81:
        targets_met.append("Score>=81")
    if summary['avg_tokens'] < 33:
        targets_met.append("Token<33")
    if summary['efficiency'] > 2450:
        targets_met.append("Efficiency>2450")
    
    if len(targets_met) == 3:
        verdict = "✅✅✅ 新冠军! 达成所有目标"
    elif summary['avg_score'] >= gen26_score and summary['avg_tokens'] < gen26_tokens:
        verdict = "✅ 超越Gen26"
    elif summary['avg_score'] >= gen26_score and summary['efficiency'] > gen26_efficiency:
        verdict = "✅ 超越Gen26"
    else:
        verdict = "⚠️ 未超越Gen26"
    
    print(f"[判定] {verdict}")
    if targets_met:
        print(f"[目标达成] {', '.join(targets_met)}")
    
    return {
        "timestamp": datetime.now().isoformat(),
        "generation": 27,
        "architecture": "Ultra-Precise Token Optimization",
        "summary": summary,
        "baseline": baseline,
        "gen26_baseline": {
            "avg_score": gen26_score,
            "avg_tokens": gen26_tokens,
            "efficiency": gen26_efficiency
        },
        "composite_score": composite,
        "verdict": verdict,
        "targets_met": targets_met,
        "individual_results": [asdict(r) for r in results]
    }

if __name__ == "__main__":
    result = run_evaluation()
    
    output_file = "/root/.openclaw/workspace/mas_repo/benchmark_results_gen27.json"
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"\n结果已保存至: {output_file}")