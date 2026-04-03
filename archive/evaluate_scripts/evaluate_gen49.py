#!/usr/bin/env python3
"""
MAS Evaluator - Generation 49 Benchmark
Task-Specific Micro-Optimization
"""

import sys
import json
import time
from datetime import datetime

sys.path.insert(0, '/root/.openclaw/workspace/mas_repo')

from benchmark.tasks import BenchmarkSuite, get_baseline_single_agent
from mas.core_gen49 import create_mas_system
from dataclasses import asdict

def run_evaluation():
    print("=" * 60)
    print("MAS Evolution Engine - Gen49 Benchmark")
    print("Task-Specific Micro-Optimization")
    print("=" * 60)
    
    mas = create_mas_system()
    benchmark = BenchmarkSuite()
    baseline = get_baseline_single_agent()
    
    print(f"\n[基线] 单Agent系统:")
    print(f"  - 任务完成率: {baseline['success_rate']*100:.1f}%")
    print(f"  - 平均得分: {baseline['avg_score']:.1f}")
    print(f"  - Token效率: {baseline['avg_tokens']:.0f}/task")
    
    # Gen38 reference
    gen38_score = 81.0
    gen38_tokens = 5.1
    gen38_efficiency = 15882
    
    print(f"\n[冠军参考] Gen38:")
    print(f"  - Score: {gen38_score}, Token: {gen38_tokens}, Efficiency: {gen38_efficiency}")
    
    print(f"\n[测试] 开始运行 {len(benchmark.tasks)} 个任务...")
    results, summary = benchmark.run_all(mas)
    
    print(f"\n[结果汇总]")
    print(f"  - 任务完成率: {summary['success_rate']*100:.1f}%")
    print(f"  - 平均得分: {summary['avg_score']:.1f}/100")
    print(f"  - Token开销: {summary['avg_tokens']:.1f}/task")
    print(f"  - 平均延迟: {summary['avg_latency_ms']:.1f}ms")
    print(f"  - 效率指数: {summary['efficiency']:.1f}")
    
    print(f"\n[对比Gen38]")
    score_diff = summary['avg_score'] - gen38_score
    token_ratio = summary['avg_tokens'] / gen38_tokens
    efficiency_ratio = summary['efficiency'] / gen38_efficiency
    print(f"  - 得分差异: {score_diff:+.1f}")
    print(f"  - Token倍率: {token_ratio:.2f}x")
    print(f"  - Efficiency倍率: {efficiency_ratio:.2f}x")
    
    # 综合评分
    composite = (
        summary['success_rate'] * 100 * 0.4 +
        summary['avg_score'] * 0.3 +
        summary['efficiency'] * 10 * 0.2 +
        max(0, 100 - summary['avg_latency_ms']) * 0.1
    )
    
    print(f"\n[综合评分] {composite:.2f}/100")
    
    # 判定
    if summary['avg_score'] >= 81 and summary['avg_tokens'] < 5 and summary['efficiency'] > 15882:
        verdict = "🏆🏆🏆 新冠军! 完美超越Gen38"
    elif summary['efficiency'] > gen38_efficiency and summary['avg_score'] >= gen38_score:
        verdict = "🏆🏆 新冠军! Efficiency提升"
    elif summary['avg_score'] > gen38_score:
        verdict = "🏆 新冠军! Score提升"
    elif summary['efficiency'] > gen38_efficiency:
        verdict = "✅ 新冠军! Efficiency提升"
    elif summary['avg_tokens'] < gen38_tokens and summary['avg_score'] >= 80:
        verdict = "✅ 进步! Token降低"
    else:
        verdict = "⚠️ 待优化"
    
    print(f"[判定] {verdict}")
    
    return {
        "timestamp": datetime.now().isoformat(),
        "generation": 49,
        "architecture": "Task-Specific Micro-Optimization",
        "summary": summary,
        "baseline": baseline,
        "gen38_reference": {
            "score": gen38_score,
            "tokens": gen38_tokens,
            "efficiency": gen38_efficiency
        },
        "composite_score": composite,
        "verdict": verdict,
        "individual_results": [asdict(r) for r in results]
    }

if __name__ == "__main__":
    result = run_evaluation()
    
    output_file = "/root/.openclaw/workspace/mas_repo/benchmark_results_gen49.json"
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"\n结果已保存至: {output_file}")