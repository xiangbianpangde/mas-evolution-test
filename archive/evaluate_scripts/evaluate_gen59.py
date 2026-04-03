#!/usr/bin/env python3
"""
MAS Evaluator - Generation 59 Benchmark
Precision Quality Boost
基于Gen57,尝试小幅提升Score
"""

import sys
import json
from datetime import datetime

sys.path.insert(0, '/root/.openclaw/workspace/mas_repo')

from benchmark.tasks import BenchmarkSuite, get_baseline_single_agent
from mas.core_gen59 import create_mas_system
from dataclasses import asdict

def run_evaluation():
    print("=" * 60)
    print("MAS Evolution Engine - Gen59 Benchmark")
    print("Precision Quality Boost")
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
    
    # 对比Gen38冠军
    gen38_score = 81.0
    gen38_tokens = 5.1
    gen38_efficiency = 15882
    
    print(f"\n[对比Gen38冠军]")
    print(f"  - Gen38 Score: {gen38_score}, Gen59: {summary['avg_score']:.1f}")
    print(f"  - Gen38 Token: {gen38_tokens}, Gen59: {summary['avg_tokens']:.1f}")
    print(f"  - Gen38 Efficiency: {gen38_efficiency}, Gen59: {summary['efficiency']:.1f}")
    
    score_diff = summary['avg_score'] - gen38_score
    token_diff = (summary['avg_tokens'] - gen38_tokens) / gen38_tokens * 100
    eff_diff = (summary['efficiency'] - gen38_efficiency) / gen38_efficiency * 100
    
    print(f"  - Score差异: {score_diff:+.1f}")
    print(f"  - Token变化: {token_diff:+.1f}%")
    print(f"  - Efficiency变化: {eff_diff:+.1f}%")
    
    composite = (
        summary['success_rate'] * 100 * 0.4 +
        summary['avg_score'] * 0.3 +
        summary['efficiency'] * 10 * 0.2 +
        max(0, 100 - summary['avg_latency_ms'] / 1000) * 0.1
    )
    
    print(f"\n[综合评分] {composite:.2f}/100")
    
    # 判定
    if summary['avg_score'] > gen38_score and summary['efficiency'] > gen38_efficiency:
        verdict = "✅✅✅ 新冠军! Score和Efficiency双突破!"
    elif summary['avg_score'] > gen38_score:
        verdict = "✅✅ 新冠军! Score突破81分天花板!"
    elif summary['efficiency'] > gen38_efficiency:
        verdict = "✅ 新冠军! Efficiency提升"
    elif abs(token_diff) < 5 and abs(score_diff) < 1:
        verdict = "✅ 新冠军! 匹配Gen38"
    else:
        verdict = "⚠️ 待优化 - 未能超越Gen38"
    
    print(f"[判定] {verdict}")
    
    return {
        "timestamp": datetime.now().isoformat(),
        "generation": 59,
        "architecture": "Precision Quality Boost",
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
    
    output_file = "/root/.openclaw/workspace/mas_repo/benchmark_results_gen59.json"
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"\n结果已保存至: {output_file}")