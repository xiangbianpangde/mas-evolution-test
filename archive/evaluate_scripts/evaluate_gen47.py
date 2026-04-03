#!/usr/bin/env python3
"""
MAS Evaluator - Generation 47 Benchmark
Pipeline Parallel Processing Architecture
范式转变: Supervisor-Worker → Pipeline
"""

import sys
import json
import time
from datetime import datetime

sys.path.insert(0, '/root/.openclaw/workspace/mas_repo')

from benchmark.tasks import BenchmarkSuite, get_baseline_single_agent
from mas.core_gen47 import create_mas_system
from dataclasses import asdict

def run_evaluation():
    """运行完整评估"""
    print("=" * 60)
    print("MAS Evolution Engine - Gen47 Benchmark")
    print("Pipeline Parallel Processing Architecture")
    print("范式转变: Supervisor-Worker → Pipeline")
    print("=" * 60)
    
    mas = create_mas_system()
    benchmark = BenchmarkSuite()
    baseline = get_baseline_single_agent()
    
    print(f"\n[基线] 单Agent系统:")
    print(f"  - 任务完成率: {baseline['success_rate']*100:.1f}%")
    print(f"  - 平均得分: {baseline['avg_score']:.1f}")
    print(f"  - Token效率: {baseline['avg_tokens']:.0f}/task")
    
    print(f"\n[Champions] Gen38 (v3.0):")
    print(f"  - Score: 81, Token: 5.1, Efficiency: 15882")
    
    print(f"\n[测试] 开始运行 {len(benchmark.tasks)} 个任务...")
    results, summary = benchmark.run_all(mas)
    
    print(f"\n[结果汇总]")
    print(f"  - 任务完成率: {summary['success_rate']*100:.1f}%")
    print(f"  - 平均得分: {summary['avg_score']:.1f}/100")
    print(f"  - Token开销: {summary['avg_tokens']:.1f}/task")
    print(f"  - 平均延迟: {summary['avg_latency_ms']:.1f}ms")
    print(f"  - 效率指数: {summary['efficiency']:.1f}")
    
    # 对比Gen38
    gen38_score = 81.0
    gen38_tokens = 5.1
    gen38_efficiency = 15882
    
    print(f"\n[对比Gen38 (v3.0冠军)]")
    score_diff = summary['avg_score'] - gen38_score
    token_ratio = summary['avg_tokens'] / gen38_tokens
    efficiency_ratio = summary['efficiency'] / gen38_efficiency
    print(f"  - 得分差异: {score_diff:+.1f}")
    print(f"  - Token倍率: {token_ratio:.2f}x")
    print(f"  - Efficiency倍率: {efficiency_ratio:.2f}x")
    
    # 判定
    if summary['avg_score'] >= 81 and summary['efficiency'] > gen38_efficiency:
        verdict = "🏆🏆🏆 新冠军! 超越Gen38"
    elif summary['avg_score'] >= 81:
        verdict = "✅ Score达标"
    elif summary['efficiency'] > gen38_efficiency:
        verdict = "✅ Efficiency提升"
    else:
        verdict = "⚠️ 待优化"
    
    print(f"\n[判定] {verdict}")
    
    return {
        "timestamp": datetime.now().isoformat(),
        "generation": 47,
        "architecture": "Pipeline Parallel Processing",
        "summary": summary,
        "baseline": baseline,
        "gen38_reference": {
            "score": gen38_score,
            "tokens": gen38_tokens,
            "efficiency": gen38_efficiency
        },
        "composite_score": summary['efficiency'] / 10,
        "verdict": verdict,
        "individual_results": [asdict(r) for r in results]
    }

if __name__ == "__main__":
    result = run_evaluation()
    output_file = "/root/.openclaw/workspace/mas_repo/benchmark_results_gen47.json"
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"\n结果已保存至: {output_file}")