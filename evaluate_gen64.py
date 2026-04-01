#!/usr/bin/env python3
"""
MAS Evaluator - Generation 64 Benchmark
Ultra-Optimized Cost Efficiency
"""

import sys
import json
import time
from datetime import datetime

sys.path.insert(0, '/root/.openclaw/workspace/mas_repo')

from benchmark.tasks import BenchmarkSuite, get_baseline_single_agent
from mas.core_gen64 import create_mas_system
from dataclasses import asdict

def run_evaluation():
    """运行完整评估"""
    print("=" * 60)
    print("MAS Evolution Engine - Gen64 Benchmark")
    print("Ultra-Optimized Cost Efficiency")
    print("=" * 60)
    
    # 创建MAS系统 (Gen64)
    mas = create_mas_system()
    
    # 创建Benchmark
    benchmark = BenchmarkSuite()
    
    # 获取基线
    baseline = get_baseline_single_agent()
    print(f"\n[基线] 单Agent系统:")
    print(f"  - 任务完成率: {baseline['success_rate']*100:.1f}%")
    print(f"  - 平均得分: {baseline['avg_score']:.1f}")
    print(f"  - Token效率: {baseline['avg_tokens']:.0f}/task")
    
    # 运行测试
    print(f"\n[测试] 开始运行 {len(benchmark.tasks)} 个任务...")
    results, summary = benchmark.run_all(mas)
    
    # 打印结果
    print(f"\n[结果汇总]")
    print(f"  - 任务完成率: {summary['success_rate']*100:.1f}%")
    print(f"  - 平均得分: {summary['avg_score']:.1f}/100")
    print(f"  - Token开销: {summary['avg_tokens']:.0f}/task")
    print(f"  - 平均延迟: {summary['avg_latency_ms']:.0f}ms")
    print(f"  - 效率指数: {summary['efficiency']:.2f}")
    
    # 计算 Cost Efficiency
    cost_efficiency_values = []
    for r in results:
        score = r.score
        tokens = r.tokens
        latency = r.latency_ms
        token_norm = tokens / 35
        latency_norm = latency / 70
        total_cost = 0.35 * token_norm + 0.65 * latency_norm
        if total_cost > 0:
            cost_efficiency_values.append(score / total_cost)
    
    avg_cost_efficiency = sum(cost_efficiency_values) / len(cost_efficiency_values) if cost_efficiency_values else 0
    print(f"  - ⚡ 成本效率: {avg_cost_efficiency:.2f}")
    
    # Gen64 特有统计
    stats = mas.get_stats()
    print(f"\n[Gen64 统计]")
    print(f"  - 版本: {stats['version']}")
    
    # 对比Gen63
    gen63_score = 81.0
    gen63_tokens = 18.5
    gen63_efficiency = 4378.4
    gen63_cost_efficiency = 567.51
    
    print(f"\n[对比Gen63]")
    score_diff = summary['avg_score'] - gen63_score
    token_diff = (summary['avg_tokens'] - gen63_tokens) / gen63_tokens * 100
    efficiency_diff = (summary['efficiency'] - gen63_efficiency) / gen63_efficiency * 100
    cost_efficiency_diff = (avg_cost_efficiency - gen63_cost_efficiency) / gen63_cost_efficiency * 100
    print(f"  - 得分差异: {score_diff:+.1f}")
    print(f"  - Token变化: {token_diff:+.1f}%")
    print(f"  - Efficiency变化: {efficiency_diff:+.1f}%")
    print(f"  - Cost Efficiency变化: {cost_efficiency_diff:+.1f}%")
    
    # 综合评分
    completion_weight = 0.4
    score_weight = 0.3
    efficiency_weight = 0.2
    latency_weight = 0.1
    
    latency_score = max(0, 100 - summary['avg_latency_ms'] / 1000)
    
    composite = (
        summary['success_rate'] * 100 * completion_weight +
        summary['avg_score'] * score_weight +
        summary['efficiency'] / 100 * efficiency_weight +
        latency_score * latency_weight
    )
    
    print(f"\n[综合评分] {composite:.2f}/100")
    
    # 目标达成检查
    targets_met = []
    if summary['avg_score'] >= 81:
        targets_met.append("Score>=81")
    if avg_cost_efficiency > gen63_cost_efficiency:
        targets_met.append(f"CostEff>{gen63_cost_efficiency:.0f}")
    
    if summary['avg_score'] >= 81 and avg_cost_efficiency > gen63_cost_efficiency:
        verdict = "✅✅✅ 新冠军! Cost Efficiency 提升"
    elif summary['avg_score'] >= 81 and avg_cost_efficiency > 560:
        verdict = "✅✅ 新冠军! Cost Efficiency 突破560"
    elif summary['avg_score'] > gen63_score:
        verdict = "✅ 新冠军! Score提升"
    elif avg_cost_efficiency > gen63_cost_efficiency:
        verdict = "✅ 新冠军! Cost Efficiency提升"
    else:
        verdict = "⚠️ 待优化 - 未能超越Gen63"
    
    print(f"[判定] {verdict}")
    if targets_met:
        print(f"[目标达成] {', '.join(targets_met)}")
    
    return {
        "timestamp": datetime.now().isoformat(),
        "generation": 64,
        "paradigm": "Computational Complexity-Aware",
        "summary": summary,
        "baseline": baseline,
        "cost_efficiency": {
            "avg": avg_cost_efficiency,
            "per_task": cost_efficiency_values
        },
        "gen63_baseline": {
            "avg_score": gen63_score,
            "avg_tokens": gen63_tokens,
            "efficiency": gen63_efficiency,
            "cost_efficiency": gen63_cost_efficiency
        },
        "composite_score": composite,
        "verdict": verdict,
        "targets_met": targets_met,
        "individual_results": [asdict(r) for r in results]
    }

if __name__ == "__main__":
    result = run_evaluation()
    
    # 保存结果
    output_file = "/root/.openclaw/workspace/mas_repo/benchmark_results_gen64.json"
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"\n结果已保存至: {output_file}")