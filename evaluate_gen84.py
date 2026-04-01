#!/usr/bin/env python3
"""
MAS Evaluator - Generation 84 Benchmark
Multi-Objective v7: Ultra-Optimized Pareto
"""

import sys
import json
import time
from datetime import datetime

sys.path.insert(0, '/root/.openclaw/workspace/mas_repo')

from benchmark.tasks import BenchmarkSuite, get_baseline_single_agent
from mas.core_gen84 import create_mas_system
from dataclasses import asdict

def run_evaluation():
    """运行完整评估"""
    print("=" * 60)
    print("MAS Evolution Engine - Gen84 Benchmark")
    print("Multi-Objective v7: Ultra-Optimized Pareto")
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
    
    # 对比Gen83
    gen83_score = 81.0
    gen83_tokens = 9.2
    gen83_efficiency = 8804.3
    
    print(f"\n[对比Gen83]")
    score_diff = summary['avg_score'] - gen83_score
    token_diff = (summary['avg_tokens'] - gen83_tokens) / gen83_tokens * 100
    efficiency_diff = (summary['efficiency'] - gen83_efficiency) / gen83_efficiency * 100
    print(f"  - 得分差异: {score_diff:+.1f}")
    print(f"  - Token变化: {token_diff:+.1f}%")
    print(f"  - Efficiency变化: {efficiency_diff:+.1f}%")
    
    # 判定
    if summary['avg_score'] > gen83_score:
        verdict = "✅✅✅ 新冠军! Score提升"
    elif summary['avg_score'] == gen83_score and summary['efficiency'] > gen83_efficiency:
        verdict = "✅✅ 新冠军! Efficiency提升"
    elif summary['avg_score'] == gen83_score and summary['avg_tokens'] < gen83_tokens:
        verdict = "✅ 新冠军! Token降低"
    else:
        verdict = "⚠️ 待优化 - 未能超越Gen83"
    
    print(f"\n[判定] {verdict}")
    
    return {
        "timestamp": datetime.now().isoformat(),
        "generation": 84,
        "architecture": "Multi-Objective v7: Ultra-Optimized Pareto",
        "summary": summary,
        "baseline": baseline,
        "gen83_baseline": {
            "avg_score": gen83_score,
            "avg_tokens": gen83_tokens,
            "efficiency": gen83_efficiency
        },
        "verdict": verdict,
        "individual_results": [asdict(r) for r in results]
    }

if __name__ == "__main__":
    result = run_evaluation()
    output_file = "/root/.openclaw/workspace/mas_repo/benchmark_results_gen84.json"
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"\n结果已保存至: {output_file}")