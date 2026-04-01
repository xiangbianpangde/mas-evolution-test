#!/usr/bin/env python3
"""
MAS Evaluator - Generation 78 Benchmark
PARADIGM SHIFT: Pareto-Optimal Multi-Objective Architecture
"""

import sys
import json
from datetime import datetime

sys.path.insert(0, '/root/.openclaw/workspace/mas_repo')

from benchmark.tasks import BenchmarkSuite, get_baseline_single_agent
from mas.core_gen78 import create_mas_system
from dataclasses import asdict

def run_evaluation():
    print("=" * 60)
    print("MAS Evolution Engine - Gen78 Benchmark")
    print("PARADIGM SHIFT: Multi-Objective Pareto Optimization")
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
    
    # Gen69 baseline
    gen69_efficiency = 13064.5
    gen69_tokens = 6.2
    gen69_score = 81.0
    
    print(f"\n[对比Gen69 (Paradigm 1 Champion)]")
    score_diff = summary['avg_score'] - gen69_score
    token_diff = (summary['avg_tokens'] - gen69_tokens) / gen69_tokens * 100
    efficiency_diff = (summary['efficiency'] - gen69_efficiency) / gen69_efficiency * 100
    print(f"  - 得分差异: {score_diff:+.1f}")
    print(f"  - Token变化: {token_diff:+.1f}%")
    print(f"  - Efficiency变化: {efficiency_diff:+.1f}%")
    
    # 判断
    targets_met = []
    if summary['avg_score'] >= 81:
        targets_met.append("Score>=81")
    if summary['avg_tokens'] < gen69_tokens:
        targets_met.append("Token<6.2")
    if summary['efficiency'] > gen69_efficiency:
        targets_met.append("Efficiency>13064")
    
    # Multi-objective verdict
    if summary['efficiency'] > gen69_efficiency and summary['avg_score'] >= 81:
        verdict = "✅✅✅ 新冠军! 多目标优化成功!"
    elif summary['avg_score'] > gen69_score:
        verdict = "✅✅ 新冠军! Score突破"
    elif summary['efficiency'] > gen69_efficiency:
        verdict = "✅✅ 新冠军! Efficiency提升"
    elif token_diff < 0:
        verdict = "✅ 新冠军! Token降低"
    else:
        verdict = "⚠️ 新范式 - 探索中"
    
    print(f"\n[判定] {verdict}")
    if targets_met:
        print(f"[目标达成] {', '.join(targets_met)}")
    print(f"[注意] 这是新范式的首次测试，与旧范式不可直接比较")
    
    return {
        "timestamp": datetime.now().isoformat(),
        "generation": 78,
        "architecture": "Pareto-Optimal Multi-Objective",
        "paradigm": "Multi-Objective Pareto Optimization",
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
    output_file = "/root/.openclaw/workspace/mas_repo/benchmark_results_gen78.json"
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"\n结果已保存至: {output_file}")