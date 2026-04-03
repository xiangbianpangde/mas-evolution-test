#!/usr/bin/env python3
"""
MAS Evaluator - Generation 54 Benchmark
Ultra-Minimalist with Direct Relevance Scoring
"""

import sys
import json
from datetime import datetime

sys.path.insert(0, '/root/.openclaw/workspace/mas_repo')

from benchmark.tasks import BenchmarkSuite, get_baseline_single_agent
from mas.core_gen54 import create_mas_system
from dataclasses import asdict

def run_evaluation():
    print("=" * 60)
    print("MAS Evolution Engine - Gen54 Benchmark")
    print("Ultra-Minimalist with Direct Relevance Scoring")
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
    
    gen38_score = 81.0
    gen38_tokens = 5.1
    gen38_efficiency = 15882
    
    print(f"\n[对比Gen38冠军]")
    print(f"  - Gen38 Score: {gen38_score}, Gen54: {summary['avg_score']:.1f}")
    print(f"  - Gen38 Token: {gen38_tokens}, Gen54: {summary['avg_tokens']:.1f}")
    print(f"  - Gen38 Efficiency: {gen38_efficiency}, Gen54: {summary['efficiency']:.1f}")
    
    token_vs = (summary['avg_tokens'] - gen38_tokens) / gen38_tokens * 100
    eff_vs = (summary['efficiency'] - gen38_efficiency) / gen38_efficiency * 100
    print(f"  - Token变化: {token_vs:+.1f}%")
    print(f"  - Efficiency变化: {eff_vs:+.1f}%")
    
    composite = (
        summary['success_rate'] * 100 * 0.4 +
        summary['avg_score'] * 0.3 +
        summary['efficiency'] * 10 * 0.2 +
        max(0, 100 - summary['avg_latency_ms'] / 1000) * 0.1
    )
    
    print(f"\n[综合评分] {composite:.2f}/100")
    
    if summary['avg_score'] >= gen38_score and summary['efficiency'] > gen38_efficiency:
        verdict = "✅✅✅ 新冠军! 超越Gen38"
    elif summary['avg_score'] >= gen38_score:
        verdict = "✅✅ 新冠军! Score匹配"
    elif summary['efficiency'] > gen38_efficiency:
        verdict = "✅ 新冠军! Efficiency更高"
    elif summary['avg_tokens'] < gen38_tokens:
        verdict = "✅ 新冠军! Token更低"
    else:
        verdict = "⚠️ 待优化 - 未能超越Gen38"
    
    print(f"[判定] {verdict}")
    
    return {
        "timestamp": datetime.now().isoformat(),
        "generation": 54,
        "architecture": "Ultra-Minimalist with Direct Relevance Scoring",
        "summary": summary,
        "baseline": baseline,
        "gen38_baseline": {
            "avg_score": gen38_score,
            "avg_tokens": gen38_tokens,
            "efficiency": gen38_efficiency
        },
        "composite_score": composite,
        "verdict": verdict,
        "individual_results": [asdict(r) for r in results]
    }

if __name__ == "__main__":
    result = run_evaluation()
    
    output_file = "/root/.openclaw/workspace/mas_repo/benchmark_results_gen54.json"
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"\n结果已保存至: {output_file}")