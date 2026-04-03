#!/usr/bin/env python3
"""
MAS Evaluator - Generation 42 Benchmark
测试 Precision Output Excellence 架构
目标: Score>=82 AND Token<6 AND Efficiency>14000
"""

import sys
import json
import time
from datetime import datetime

sys.path.insert(0, '/root/.openclaw/workspace/mas_repo')

from benchmark.tasks import BenchmarkSuite, get_baseline_single_agent
from mas.core_gen42 import create_mas_system
from dataclasses import asdict

def run_evaluation():
    print("=" * 60)
    print("MAS Evolution Engine - Gen42 Benchmark")
    print("Precision Output Excellence")
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
    
    stats = mas.get_stats()
    print(f"\n[Gen42 统计]")
    print(f"  - 版本: {stats['version']}")
    
    # 对比Gen38
    gen38_score = 81.0
    gen38_tokens = 5.1
    gen38_efficiency = 15882.0
    
    print(f"\n[对比Gen38 (效率冠军)]")
    score_diff = summary['avg_score'] - gen38_score
    token_diff = (summary['avg_tokens'] - gen38_tokens) / gen38_tokens * 100
    efficiency_diff = (summary['efficiency'] - gen38_efficiency) / gen38_efficiency * 100
    print(f"  - 得分差异: {score_diff:+.1f}")
    print(f"  - Token变化: {token_diff:+.1f}%")
    print(f"  - Efficiency变化: {efficiency_diff:+.1f}%")
    
    completion_weight = 0.4
    score_weight = 0.3
    efficiency_weight = 0.2
    latency_weight = 0.1
    
    latency_score = max(0, 100 - summary['avg_latency_ms'] / 1000)
    
    composite = (
        summary['success_rate'] * 100 * completion_weight +
        summary['avg_score'] * score_weight +
        summary['efficiency'] * 10 * efficiency_weight +
        latency_score * latency_weight
    )
    
    print(f"\n[综合评分] {composite:.2f}/100")
    
    targets_met = []
    if summary['avg_score'] >= 82:
        targets_met.append("Score>=82")
    if summary['avg_tokens'] < 6:
        targets_met.append("Token<6")
    if summary['efficiency'] > 14000:
        targets_met.append("Efficiency>14000")
    
    if all([summary['avg_score'] >= 82, summary['avg_tokens'] < 6, summary['efficiency'] > 14000]):
        verdict = "✅✅✅ 新冠军! 完美达成所有目标"
    elif summary['avg_score'] > gen38_score:
        verdict = "✅ 新冠军! Score提升"
    elif summary['efficiency'] > gen38_efficiency:
        verdict = "✅✅ 新冠军! Efficiency提升"
    elif summary['avg_tokens'] < gen38_tokens:
        verdict = "✅ 新冠军! Token降低"
    else:
        verdict = "⚠️ 待优化 - 未能超越Gen38"
    
    print(f"[判定] {verdict}")
    if targets_met:
        print(f"[目标达成] {', '.join(targets_met)}")
    
    return {
        "timestamp": datetime.now().isoformat(),
        "generation": 42,
        "architecture": "Precision Output Excellence",
        "summary": summary,
        "baseline": baseline,
        "gen38_baseline": {
            "avg_score": gen38_score,
            "avg_tokens": gen38_tokens,
            "efficiency": gen38_efficiency
        },
        "composite_score": composite,
        "verdict": verdict,
        "targets_met": targets_met,
        "individual_results": [asdict(r) for r in results]
    }

if __name__ == "__main__":
    result = run_evaluation()
    output_file = "/root/.openclaw/workspace/mas_repo/benchmark_results_gen42.json"
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"\n结果已保存至: {output_file}")