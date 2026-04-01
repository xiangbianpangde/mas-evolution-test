#!/usr/bin/env python3
"""
MAS Evaluator - Generation 65 Benchmark
"""

import sys
import json
import time
from datetime import datetime

sys.path.insert(0, '/root/.openclaw/workspace/mas_repo')

from benchmark.tasks import BenchmarkSuite, get_baseline_single_agent
from mas.core_gen65 import create_mas_system
from dataclasses import asdict

def run_evaluation():
    """运行完整评估"""
    print("=" * 60)
    print("MAS Evolution Engine - Gen65 Benchmark")
    print("Computational Complexity-Aware - Further Optimized")
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
    
    # Gen65 特有统计
    stats = mas.get_stats()
    print(f"\n[Gen65 统计]")
    print(f"  - 版本: {stats['version']}")
    
    # 对比Gen64
    gen64_score = 81.0
    gen64_tokens = 15.0
    gen64_efficiency = 5294.12
    gen64_cost_efficiency = 690.24
    
    print(f"\n[对比Gen64]")
    score_diff = summary['avg_score'] - gen64_score
    token_diff = (summary['avg_tokens'] - gen64_tokens) / gen64_tokens * 100
    efficiency_diff = (summary['efficiency'] - gen64_efficiency) / gen64_efficiency * 100
    print(f"  - 得分差异: {score_diff:+.1f}")
    print(f"  - Token变化: {token_diff:+.1f}%")
    print(f"  - Efficiency变化: {efficiency_diff:+.1f}%")
    
    # 计算成本效率 (手动计算)
    # Cost Efficiency = Score / (Tokens * 0.4 + Latency_ms/1000 * 0.6)
    cost_efficiencies = []
    for r in results:
        token_cost = r.tokens * 0.4
        latency_cost = (r.latency_ms / 1000) * 0.6
        total_cost = token_cost + latency_cost
        if total_cost > 0:
            cost_eff = r.score / total_cost
            cost_efficiencies.append(cost_eff)
    avg_cost_eff = sum(cost_efficiencies) / len(cost_efficiencies) if cost_efficiencies else 0
    print(f"  - Cost Efficiency: {avg_cost_eff:.2f}")
    
    # 综合评分
    latency_score = max(0, 100 - summary['avg_latency_ms'] / 1000)
    composite = (
        summary['success_rate'] * 100 * 0.4 +
        summary['avg_score'] * 0.3 +
        summary['efficiency'] * 0.2 +
        latency_score * 0.1
    )
    
    print(f"\n[综合评分] {composite:.2f}/100")
    
    # 目标达成检查
    targets_met = []
    if summary['avg_score'] >= 81:
        targets_met.append("Score>=81")
    if avg_cost_eff > gen64_cost_efficiency:
        targets_met.append(f"CostEff>{gen64_cost_efficiency:.0f}")
    
    if summary['avg_score'] >= 81 and avg_cost_eff > gen64_cost_efficiency:
        verdict = "✅✅✅ 新冠军! Cost Efficiency 提升"
    elif summary['avg_score'] >= 81:
        verdict = "✅ 新冠军候选"
    else:
        verdict = "⚠️ 待优化"
    
    print(f"[判定] {verdict}")
    if targets_met:
        print(f"[目标达成] {', '.join(targets_met)}")
    
    return {
        "timestamp": datetime.now().isoformat(),
        "generation": 65,
        "architecture": "Computational Complexity-Aware - Further Optimized",
        "summary": summary,
        "baseline": baseline,
        "gen64_baseline": {
            "avg_score": gen64_score,
            "avg_tokens": gen64_tokens,
            "efficiency": gen64_efficiency,
            "cost_efficiency": gen64_cost_efficiency
        },
        "composite_score": composite,
        "verdict": verdict,
        "targets_met": targets_met,
        "cost_efficiency": avg_cost_eff,
        "individual_results": [asdict(r) for r in results]
    }

if __name__ == "__main__":
    result = run_evaluation()
    
    output_file = "/root/.openclaw/workspace/mas_repo/benchmark_results_gen65.json"
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"\n结果已保存至: {output_file}")