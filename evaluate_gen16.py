#!/usr/bin/env python3
"""
MAS Evaluator - Generation 16 Benchmark
测试 Semantic-Gradient Cache + Precision Output Budgeting
目标: Token<45, Score>=80, Efficiency>1703
"""

import sys
import json
import time
from datetime import datetime

sys.path.insert(0, '/root/.openclaw/workspace/mas_repo')

from benchmark.tasks import BenchmarkSuite, get_baseline_single_agent
from mas.core_gen16 import create_mas_system
from dataclasses import asdict

def run_evaluation():
    print("=" * 60)
    print("MAS Evolution Engine - Gen16 Benchmark")
    print("Semantic-Gradient Cache + Precision Output Budgeting")
    print("=" * 60)
    
    mas = create_mas_system()
    benchmark = BenchmarkSuite()
    baseline = get_baseline_single_agent()
    
    print(f"\n[基线] 单Agent系统:")
    print(f"  - 任务完成率: {baseline['success_rate']*100:.1f}%")
    print(f"  - 平均得分: {baseline['avg_score']:.1f}")
    print(f"  - Token效率: {baseline['avg_tokens']:.0f}/task")
    
    # Gen15基准
    gen15_tokens = 46
    gen15_score = 79
    gen15_efficiency = 1703
    print(f"\n[Gen15 基准]")
    print(f"  - Token: {gen15_tokens}")
    print(f"  - Score: {gen15_score}")
    print(f"  - Efficiency: {gen15_efficiency}")
    
    print(f"\n[测试] 开始运行 {len(benchmark.tasks)} 个任务...")
    results, summary = benchmark.run_all(mas)
    
    print(f"\n[结果汇总]")
    print(f"  - 任务完成率: {summary['success_rate']*100:.1f}%")
    print(f"  - 平均得分: {summary['avg_score']:.1f}/100")
    print(f"  - Token开销: {summary['avg_tokens']:.0f}/task")
    print(f"  - 平均延迟: {summary['avg_latency_ms']:.0f}ms")
    print(f"  - 效率指数: {summary['efficiency']:.4f}")
    
    stats = mas.get_stats()
    print(f"\n[Gen16 统计]")
    print(f"  - 总任务数: {stats['total_tasks']}")
    print(f"  - 缓存命中: {stats['cache_hits']}")
    print(f"  - 直接执行: {stats['direct_exec']}")
    print(f"  - 复杂度分布: {dict(stats['complexity_counts'])}")
    
    cache_stats = stats.get('cache', {})
    print(f"\n[缓存统计]")
    print(f"  - L1命中: {cache_stats.get('L1_hits', 0)}")
    print(f"  - L2命中: {cache_stats.get('L2_hits', 0)}")
    print(f"  - L3命中: {cache_stats.get('L3_hits', 0)}")
    print(f"  - 缓存命中率: {cache_stats.get('hit_rate', 0)*100:.1f}%")
    
    # 目标检查
    token_target = 45
    score_target = 80
    efficiency_target = 1703
    
    print(f"\n[目标检查]")
    token_ok = summary['avg_tokens'] < token_target
    score_ok = summary['avg_score'] >= score_target
    efficiency_ok = summary['efficiency'] > efficiency_target
    
    print(f"  - Token < {token_target}: {summary['avg_tokens']:.1f} {'✅' if token_ok else '❌'}")
    print(f"  - Score >= {score_target}: {summary['avg_score']:.1f} {'✅' if score_ok else '❌'}")
    print(f"  - Efficiency > {efficiency_target}: {summary['efficiency']:.1f} {'✅' if efficiency_ok else '❌'}")
    
    # 对比Gen15
    print(f"\n[对比Gen15]")
    token_diff = (summary['avg_tokens'] - gen15_tokens) / gen15_tokens * 100
    score_diff = summary['avg_score'] - gen15_score
    efficiency_diff = (summary['efficiency'] - gen15_efficiency) / gen15_efficiency * 100
    print(f"  - Token变化: {token_diff:+.1f}%")
    print(f"  - Score变化: {score_diff:+.1f}")
    print(f"  - Efficiency变化: {efficiency_diff:+.1f}%")
    
    # 综合评分
    completion_weight = 0.4
    score_weight = 0.3
    efficiency_weight = 0.2
    latency_weight = 0.1
    
    latency_score = max(0, 100 - summary['avg_latency_ms'] / 1000)
    
    composite = (
        summary['success_rate'] * 100 * completion_weight +
        summary['avg_score'] * score_weight +
        summary['efficiency'] * 1000 * efficiency_weight +
        latency_score * latency_weight
    )
    
    print(f"\n[综合评分] {composite:.2f}/100")
    
    # 判断
    all_targets_met = token_ok and score_ok and efficiency_ok
    if all_targets_met:
        verdict = "🏆🏆🏆 全部目标达成! 超越Gen15!"
    elif composite > 340737:
        verdict = "✅ 超越Gen15综合评分"
    else:
        verdict = "⚠️ 未超越Gen15"
    
    print(f"[判定] {verdict}")
    
    return {
        "timestamp": datetime.now().isoformat(),
        "generation": 16,
        "architecture": "Semantic-Gradient Cache + Precision Output Budgeting",
        "summary": summary,
        "baseline": baseline,
        "gen15_baseline": {
            "avg_tokens": gen15_tokens,
            "avg_score": gen15_score,
            "efficiency": gen15_efficiency
        },
        "targets": {
            "token": {"target": token_target, "actual": summary['avg_tokens'], "met": token_ok},
            "score": {"target": score_target, "actual": summary['avg_score'], "met": score_ok},
            "efficiency": {"target": efficiency_target, "actual": summary['efficiency'], "met": efficiency_ok}
        },
        "composite_score": composite,
        "verdict": verdict,
        "stats": stats,
        "individual_results": [asdict(r) for r in results]
    }

if __name__ == "__main__":
    result = run_evaluation()
    
    output_file = "/root/.openclaw/workspace/mas_repo/benchmark_results_gen16.json"
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"\n结果已保存至: {output_file}")