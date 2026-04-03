#!/usr/bin/env python3
"""
MAS Evaluator - Generation 5 Benchmark
测试 Minimalist Pipeline with Experience-Guided Skipping
"""

import sys
import json
from datetime import datetime

sys.path.insert(0, '/root/.openclaw/workspace/mas_repo')

from benchmark.tasks import BenchmarkSuite, get_baseline_single_agent
from mas.core_gen5 import create_mas_system
from dataclasses import asdict

def run_evaluation():
    print("=" * 60)
    print("MAS Evolution Engine - Gen5 Benchmark")
    print("Minimalist Pipeline + Experience-Guided Skipping")
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
    print(f"\n[Gen5 统计]")
    print(f"  - 总任务数: {stats['total_tasks']}")
    print(f"  - 缓存命中: {stats['cache_hits']}")
    print(f"  - 直接执行: {stats['direct_exec']}")
    
    # 对比
    gen3_tokens = 242
    gen3_efficiency = 330.0
    gen1_tokens = 303
    
    print(f"\n[对比Gen3 (当前最优)]")
    gen3_token_diff = (summary['avg_tokens'] - gen3_tokens) / gen3_tokens * 100
    gen3_eff_diff = (summary['efficiency'] - gen3_efficiency) / gen3_efficiency * 100
    print(f"  - Token变化: {gen3_token_diff:+.1f}%")
    print(f"  - 效率变化: {gen3_eff_diff:+.1f}%")
    
    print(f"\n[对比Gen1]")
    gen1_token_diff = (summary['avg_tokens'] - gen1_tokens) / gen1_tokens * 100
    print(f"  - Token变化: {gen1_token_diff:+.1f}%")
    
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
    
    if composite > 70:
        verdict = "✅ 通过 - 优于基线"
    elif composite > 50:
        verdict = "⚠️ 待优化 - 接近基线"
    else:
        verdict = "❌ 不合格 - 显著低于基线"
    
    print(f"[判定] {verdict}")
    
    return {
        "timestamp": datetime.now().isoformat(),
        "generation": 5,
        "architecture": "Minimalist Pipeline + Experience-Guided Skipping",
        "summary": summary,
        "baseline": baseline,
        "gen3_baseline": {"avg_tokens": gen3_tokens, "efficiency": gen3_efficiency},
        "composite_score": composite,
        "verdict": verdict,
        "stats": stats,
        "individual_results": [asdict(r) for r in results]
    }

if __name__ == "__main__":
    result = run_evaluation()
    
    output_file = "/root/.openclaw/workspace/mas_repo/benchmark_results_gen5.json"
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"\n结果已保存至: {output_file}")