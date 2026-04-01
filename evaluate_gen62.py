#!/usr/bin/env python3
"""
MAS Evaluator - Generation 62 Benchmark
Computational Complexity-Aware - Refined Cost Efficiency
"""

import sys
import json
import time
from datetime import datetime

sys.path.insert(0, '/root/.openclaw/workspace/mas_repo')

from benchmark.tasks import BenchmarkSuite, get_baseline_single_agent
from mas.core_gen62 import create_mas_system
from dataclasses import asdict

def run_evaluation():
    print("=" * 60)
    print("MAS Evolution Engine - Gen62 Benchmark")
    print("Computational Complexity-Aware - Refined Cost Efficiency")
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
    print(f"  - 平均延迟: {summary['avg_latency_ms']:.2f}ms")
    print(f"  - 效率指数: {summary['efficiency']:.2f}")
    
    # Calculate cost efficiency
    cost_efficiencies = []
    for r in results:
        ce = r.score / (0.4 * (r.tokens / 40) + 0.6 * (r.latency_ms / 80)) if r.tokens > 0 else 0
        cost_efficiencies.append(ce)
    avg_cost_efficiency = sum(cost_efficiencies) / len(cost_efficiencies) if cost_efficiencies else 0
    
    print(f"  - ⚡ 成本效率: {avg_cost_efficiency:.2f}")
    
    # Gen62 stats
    stats = mas.get_stats()
    print(f"\n[Gen62 统计]")
    print(f"  - 版本: {stats['version']}")
    
    # 对比Gen61
    gen61_score = 81.0
    gen61_tokens = 22.7
    gen61_efficiency = 3568
    gen61_cost_eff = 441.0
    
    print(f"\n[对比Gen61]")
    score_diff = summary['avg_score'] - gen61_score
    token_diff = (summary['avg_tokens'] - gen61_tokens) / gen61_tokens * 100
    eff_diff = (summary['efficiency'] - gen61_efficiency) / gen61_efficiency * 100
    cost_eff_diff = (avg_cost_efficiency - gen61_cost_eff) / gen61_cost_eff * 100
    print(f"  - 得分差异: {score_diff:+.1f}")
    print(f"  - Token变化: {token_diff:+.1f}%")
    print(f"  - Efficiency变化: {eff_diff:+.1f}%")
    print(f"  - Cost Efficiency变化: {cost_eff_diff:+.1f}%")
    
    # 综合评分
    composite = (
        summary['success_rate'] * 100 * 0.3 +
        summary['avg_score'] * 0.3 +
        summary['efficiency'] / 100 * 0.2 +
        avg_cost_efficiency / 10 * 0.2
    )
    
    print(f"\n[综合评分] {composite:.2f}/100")
    
    # 判定
    targets_met = []
    if summary['avg_score'] >= 81:
        targets_met.append("Score>=81")
    if avg_cost_efficiency > gen61_cost_eff:
        targets_met.append(f"CostEff>{gen61_cost_eff:.0f}")
    
    if all([summary['avg_score'] >= 81, avg_cost_efficiency > gen61_cost_eff]):
        verdict = "✅✅✅ 新冠军! Cost Efficiency 提升"
    elif summary['avg_score'] >= 81 and avg_cost_efficiency > gen61_cost_eff * 0.95:
        verdict = "✅✅ 接近冠军, Cost Efficiency 提升"
    elif summary['avg_score'] > gen61_score:
        verdict = "✅ 新冠军! Score 提升"
    elif avg_cost_efficiency > gen61_cost_eff:
        verdict = "✅ 新冠军! Cost Efficiency 提升"
    else:
        verdict = "⚠️ 待优化 - 未能超越Gen61"
    
    print(f"[判定] {verdict}")
    if targets_met:
        print(f"[目标达成] {', '.join(targets_met)}")
    
    return {
        "timestamp": datetime.now().isoformat(),
        "generation": 62,
        "paradigm": "Computational Complexity-Aware",
        "summary": summary,
        "baseline": baseline,
        "cost_efficiency": {
            "avg": avg_cost_efficiency,
            "per_task": cost_efficiencies
        },
        "gen61_baseline": {
            "avg_score": gen61_score,
            "avg_tokens": gen61_tokens,
            "efficiency": gen61_efficiency,
            "cost_efficiency": gen61_cost_eff
        },
        "composite_score": composite,
        "verdict": verdict,
        "targets_met": targets_met,
        "individual_results": [asdict(r) for r in results]
    }

if __name__ == "__main__":
    result = run_evaluation()
    
    output_file = "/root/.openclaw/workspace/mas_repo/benchmark_results_gen62.json"
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"\n结果已保存至: {output_file}")