#!/usr/bin/env python3
"""
MAS Evaluator - Generation 73 Benchmark
"""

import sys
import json
import time
from datetime import datetime

sys.path.insert(0, '/root/.openclaw/workspace/mas_repo')

from benchmark.tasks import BenchmarkSuite, get_baseline_single_agent
from mas.core_gen73 import create_mas_system
from dataclasses import asdict

def run_evaluation():
    print("=" * 60)
    print("MAS Evolution Engine - Gen73 Benchmark")
    print("Maximum Efficiency v5 (Further Budget Reduction)")
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
    print(f"\n[Gen73 统计]")
    print(f"  - 版本: {stats['version']}")
    
    # 对比Gen69
    gen69_score = 81.0
    gen69_tokens = 6.2
    gen69_efficiency = 13064.5
    
    print(f"\n[对比Gen69]")
    score_diff = summary['avg_score'] - gen69_score
    token_diff = (summary['avg_tokens'] - gen69_tokens) / gen69_tokens * 100
    efficiency_diff = (summary['efficiency'] - gen69_efficiency) / gen69_efficiency * 100
    print(f"  - 得分差异: {score_diff:+.1f}")
    print(f"  - Token变化: {token_diff:+.1f}%")
    print(f"  - Efficiency变化: {efficiency_diff:+.1f}%")
    
    # 目标达成检查
    targets_met = []
    if summary['avg_score'] >= 81:
        targets_met.append("Score>=81")
    if summary['avg_tokens'] < 6.2:
        targets_met.append("Token<6.2")
    if summary['efficiency'] > 13065:
        targets_met.append("Efficiency>13065")
    
    if all([summary['avg_score'] >= 81, summary['avg_tokens'] < 6.2, summary['efficiency'] > 13065]):
        verdict = "✅✅✅ 新冠军! 完美达成所有目标"
    elif summary['avg_score'] >= 81 and summary['efficiency'] > gen69_efficiency:
        verdict = "✅✅ 新冠军! Efficiency提升"
    elif summary['avg_score'] > gen69_score:
        verdict = "✅ 新冠军! Score提升"
    elif summary['efficiency'] > gen69_efficiency:
        verdict = "✅ 新冠军! Efficiency提升"
    elif summary['avg_tokens'] < gen69_tokens:
        verdict = "✅ 新冠军! Token降低"
    else:
        verdict = "⚠️ 待优化"
    
    print(f"\n[判定] {verdict}")
    if targets_met:
        print(f"[目标达成] {', '.join(targets_met)}")
    
    return {
        "timestamp": datetime.now().isoformat(),
        "generation": 73,
        "architecture": "Maximum Efficiency v5",
        "summary": summary,
        "baseline": baseline,
        "gen69_baseline": {
            "avg_score": gen69_score,
            "avg_tokens": gen69_tokens,
            "efficiency": gen69_efficiency
        },
        "verdict": verdict,
        "targets_met": targets_met,
        "individual_results": [asdict(r) for r in results]
    }

if __name__ == "__main__":
    result = run_evaluation()
    
    output_file = "/root/.openclaw/workspace/mas_repo/benchmark_results_gen73.json"
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"\n结果已保存至: {output_file}")