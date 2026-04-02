#!/usr/bin/env python3
"""
MAS Evaluator - Generation 156 Benchmark
Reduced Query Cost Multiplier
"""

import sys
import json
from datetime import datetime

sys.path.insert(0, '/root/.openclaw/workspace/mas_repo')

from benchmark.tasks import BenchmarkSuite, get_baseline_single_agent
from mas.core_gen156 import create_mas_system
from dataclasses import asdict

def run_evaluation():
    print("=" * 60)
    print("MAS Evolution Engine - Gen156 Benchmark")
    print("Reduced Query Cost Multiplier")
    print("=" * 60)
    
    mas = create_mas_system()
    benchmark = BenchmarkSuite()
    baseline = get_baseline_single_agent()
    
    print(f"\n[测试] 开始运行 {len(benchmark.tasks)} 个任务...")
    results, summary = benchmark.run_all(mas)
    
    print(f"\n[结果汇总]")
    print(f"  - 任务完成率: {summary['success_rate']*100:.1f}%")
    print(f"  - 平均得分: {summary['avg_score']:.1f}/100")
    print(f"  - Token开销: {summary['avg_tokens']:.1f}/task")
    print(f"  - 效率指数: {summary['efficiency']:.0f}")
    
    print(f"\n[任务分解]")
    for r in results:
        print(f"  {r.task_id}: tokens={r.tokens}, score={r.score}")
    
    gen150_tokens = 0.3
    gen150_efficiency = 250000.0
    gen145_score = 81.0
    
    print(f"\n[对比Gen150 (Efficiency Champion)]")
    if summary['efficiency'] > 0:
        token_diff = (summary['avg_tokens'] - gen150_tokens) / gen150_tokens * 100
        efficiency_diff = (summary['efficiency'] - gen150_efficiency) / gen150_efficiency * 100
        print(f"  - Token变化: {token_diff:+.1f}%")
        print(f"  - Efficiency变化: {efficiency_diff:+.1f}%")
    else:
        print(f"  - Efficiency: 0 (degenerate case)")
    
    print(f"\n[对比Gen145 (Quality Champion)]")
    print(f"  - Score差异: {summary['avg_score'] - gen145_score:+.1f}")
    
    composite = (
        summary['success_rate'] * 100 * 0.4 +
        summary['avg_score'] * 0.3 +
        (summary['efficiency'] / 100 if summary['efficiency'] > 0 else 0) * 0.2 +
        max(0, 100 - summary['avg_latency_ms'] / 1000) * 0.1
    )
    
    print(f"\n[综合评分] {composite:.2f}/100")
    
    if summary['efficiency'] == 0:
        verdict = "⚠️ 退化: 0效率 (所有任务0 token)"
    elif summary['avg_score'] >= 81 and (summary['avg_tokens'] < gen150_tokens or summary['efficiency'] > gen150_efficiency):
        verdict = "✅✅✅ 新冠军! Quality + Efficiency同时提升!"
    elif summary['avg_score'] >= 81:
        verdict = "✅✅ 新冠军! Quality Champion!"
    elif summary['efficiency'] > gen150_efficiency * 1.1:
        verdict = "✅✅ 新冠军! Efficiency大幅提升!"
    elif summary['avg_tokens'] < gen150_tokens and summary['avg_score'] >= 75:
        verdict = "✅ 新冠军! Token降低!"
    else:
        verdict = "⚠️ 待优化"
    
    print(f"[判定] {verdict}")
    
    return {
        "timestamp": datetime.now().isoformat(),
        "generation": 156,
        "architecture": "Reduced Query Cost Multiplier",
        "summary": summary,
        "baseline": baseline,
        "gen150_baseline": {"avg_tokens": gen150_tokens, "efficiency": gen150_efficiency},
        "gen145_baseline": {"avg_score": gen145_score},
        "composite_score": composite,
        "verdict": verdict,
        "individual_results": [asdict(r) for r in results]
    }

if __name__ == "__main__":
    result = run_evaluation()
    output_file = "/root/.openclaw/workspace/mas_repo/benchmark_results_gen156.json"
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"\n结果已保存至: {output_file}")