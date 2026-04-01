#!/usr/bin/env python3
"""
MAS Evaluator - Generation 68 Benchmark
"""

import sys
import json
from datetime import datetime

sys.path.insert(0, '/root/.openclaw/workspace/mas_repo')

from benchmark.tasks import BenchmarkSuite, get_baseline_single_agent
from mas.core_gen68 import create_mas_system
from dataclasses import asdict

def run_evaluation():
    print("=" * 60)
    print("MAS Evolution Engine - Gen68 Benchmark")
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
    print(f"  - Token开销: {summary['avg_tokens']:.1f}/task")
    print(f"  - 平均延迟: {summary['avg_latency_ms']:.0f}ms")
    print(f"  - 效率指数: {summary['efficiency']:.1f}")
    
    stats = mas.get_stats()
    print(f"\n[Gen68 统计]")
    print(f"  - 版本: {stats['version']}")
    
    # 对比Gen67
    gen67_score = 81.0
    gen67_tokens = 9.3
    gen67_efficiency = 8709.7
    
    print(f"\n[对比Gen67]")
    score_diff = summary['avg_score'] - gen67_score
    token_diff = (summary['avg_tokens'] - gen67_tokens) / gen67_tokens * 100
    efficiency_diff = (summary['efficiency'] - gen67_efficiency) / gen67_efficiency * 100
    print(f"  - 得分差异: {score_diff:+.1f}")
    print(f"  - Token变化: {token_diff:+.1f}%")
    print(f"  - Efficiency变化: {efficiency_diff:+.1f}%")
    
    # 综合评分
    composite = (
        summary['success_rate'] * 100 * 0.4 +
        summary['avg_score'] * 0.3 +
        summary['efficiency'] * 0.2 +
        max(0, 100 - summary['avg_latency_ms'] / 1000) * 0.1
    )
    
    print(f"\n[综合评分] {composite:.2f}/100")
    
    # 判定
    if summary['avg_score'] >= 81 and summary['avg_tokens'] < 9 and summary['efficiency'] > gen67_efficiency:
        verdict = "✅✅✅ 新冠军! 完美达成所有目标"
    elif summary['avg_score'] >= 81 and summary['efficiency'] > gen67_efficiency:
        verdict = "✅✅ 新冠军! Efficiency提升"
    elif summary['avg_score'] > gen67_score:
        verdict = "✅ 新冠军! Score提升"
    elif summary['efficiency'] > gen67_efficiency:
        verdict = "✅ 新冠军! Efficiency提升"
    elif summary['avg_tokens'] < gen67_tokens:
        verdict = "✅ 新冠军! Token降低"
    else:
        verdict = "⚠️ 待优化"
    
    print(f"[判定] {verdict}")
    
    return {
        "timestamp": datetime.now().isoformat(),
        "generation": 68,
        "architecture": "Computational Complexity-Aware - Maximum Efficiency v2",
        "summary": summary,
        "baseline": baseline,
        "gen67_baseline": {
            "avg_score": gen67_score,
            "avg_tokens": gen67_tokens,
            "efficiency": gen67_efficiency
        },
        "composite_score": composite,
        "verdict": verdict,
        "individual_results": [asdict(r) for r in results]
    }

if __name__ == "__main__":
    result = run_evaluation()
    output_file = "/root/.openclaw/workspace/mas_repo/benchmark_results_gen68.json"
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"\n结果已保存至: {output_file}")