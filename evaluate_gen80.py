#!/usr/bin/env python3
"""
MAS Evaluator - Generation 80 Benchmark
Multi-Objective v3: Latency-Optimized Pareto
"""

import sys
import json
import time
from datetime import datetime

sys.path.insert(0, '/root/.openclaw/workspace/mas_repo')

from benchmark.tasks import BenchmarkSuite, get_baseline_single_agent
from mas.core_gen80 import create_mas_system
from dataclasses import asdict

def run_evaluation():
    """运行完整评估"""
    print("=" * 60)
    print("MAS Evolution Engine - Gen80 Benchmark")
    print("Multi-Objective v3: Latency-Optimized Pareto")
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
    
    # 对比Gen79
    gen79_score = 81.0
    gen79_tokens = 9.5
    gen79_efficiency = 8526.0
    
    print(f"\n[对比Gen79]")
    score_diff = summary['avg_score'] - gen79_score
    token_diff = (summary['avg_tokens'] - gen79_tokens) / gen79_tokens * 100
    efficiency_diff = (summary['efficiency'] - gen79_efficiency) / gen79_efficiency * 100
    print(f"  - 得分差异: {score_diff:+.1f}")
    print(f"  - Token变化: {token_diff:+.1f}%")
    print(f"  - Efficiency变化: {efficiency_diff:+.1f}%")
    
    # 对比Gen69 (efficiency champion)
    gen69_efficiency = 13065
    print(f"\n[对比Gen69 (efficiency champion)]")
    print(f"  - Efficiency差距: {(summary['efficiency'] - gen69_efficiency) / gen69_efficiency * 100:+.1f}%")
    
    # 综合评分
    composite = (
        summary['success_rate'] * 100 * 0.4 +
        summary['avg_score'] * 0.3 +
        summary['efficiency'] * 0.002 * 0.2 +
        max(0, 100 - summary['avg_latency_ms'] / 100) * 0.1
    )
    
    print(f"\n[综合评分] {composite:.2f}/100")
    
    # 判定
    if summary['avg_score'] >= 81 and summary['efficiency'] > gen79_efficiency:
        verdict = "✅✅✅ 新冠军! Multi-Objective新纪录"
    elif summary['efficiency'] > gen79_efficiency:
        verdict = "✅ 新冠军! Efficiency提升"
    elif summary['avg_tokens'] < gen79_tokens:
        verdict = "✅ 新冠军! Token降低"
    else:
        verdict = "⚠️ 待优化"
    
    print(f"[判定] {verdict}")
    
    return {
        "timestamp": datetime.now().isoformat(),
        "generation": 80,
        "architecture": "Multi-Objective v3: Latency-Optimized Pareto",
        "summary": summary,
        "baseline": baseline,
        "gen79_baseline": {
            "avg_score": gen79_score,
            "avg_tokens": gen79_tokens,
            "efficiency": gen79_efficiency
        },
        "composite_score": composite,
        "verdict": verdict,
        "individual_results": [asdict(r) for r in results]
    }

if __name__ == "__main__":
    result = run_evaluation()
    
    output_file = "/root/.openclaw/workspace/mas_repo/benchmark_results_gen80.json"
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"\n结果已保存至: {output_file}")