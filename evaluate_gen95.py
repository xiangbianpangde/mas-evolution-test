#!/usr/bin/env python3
"""
MAS Evaluator - Generation 95 Benchmark
Token Budget Tuning
"""

import sys
import json
from datetime import datetime

sys.path.insert(0, '/root/.openclaw/workspace/mas_repo')

from benchmark.tasks import BenchmarkSuite, get_baseline_single_agent
from mas.core_gen95 import create_mas_system
from dataclasses import asdict

def run_evaluation():
    print("=" * 60)
    print("MAS Evolution Engine - Gen95 Benchmark")
    print("Token Budget Tuning")
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
    print(f"  - 效率指数: {summary['efficiency']:.0f}")
    
    print(f"\n[任务分解]")
    for r in results:
        print(f"  {r.task_id}: tokens={r.tokens}, score={r.score}")
    
    gen92_score = 81.0
    gen92_tokens = 2.5
    gen92_efficiency = 32400.0
    
    print(f"\n[对比Gen92]")
    score_diff = summary['avg_score'] - gen92_score
    token_diff = (summary['avg_tokens'] - gen92_tokens) / gen92_tokens * 100
    efficiency_diff = (summary['efficiency'] - gen92_efficiency) / gen92_efficiency * 100
    print(f"  - 得分差异: {score_diff:+.1f}")
    print(f"  - Token变化: {token_diff:+.1f}%")
    print(f"  - Efficiency变化: {efficiency_diff:+.1f}%")
    
    composite = (
        summary['success_rate'] * 100 * 0.4 +
        summary['avg_score'] * 0.3 +
        summary['efficiency'] / 100 * 0.2 +
        max(0, 100 - summary['avg_latency_ms'] / 1000) * 0.1
    )
    
    print(f"\n[综合评分] {composite:.2f}/100")
    
    if summary['avg_tokens'] < gen92_tokens and summary['avg_score'] >= gen92_score:
        verdict = "✅✅✅ 新冠军! Token更低!"
    elif summary['efficiency'] > gen92_efficiency:
        verdict = "✅✅ 新冠军! Efficiency提升"
    elif summary['avg_score'] > gen92_score:
        verdict = "✅ 新冠军! Score提升"
    elif summary['avg_tokens'] < gen92_tokens:
        verdict = "✅ 新冠军! Token降低"
    else:
        verdict = "⚠️ 待优化"
    
    print(f"[判定] {verdict}")
    
    return {
        "timestamp": datetime.now().isoformat(),
        "generation": 95,
        "architecture": "Token Budget Tuning",
        "summary": summary,
        "baseline": baseline,
        "gen92_baseline": {"avg_score": gen92_score, "avg_tokens": gen92_tokens, "efficiency": gen92_efficiency},
        "composite_score": composite,
        "verdict": verdict,
        "individual_results": [asdict(r) for r in results]
    }

if __name__ == "__main__":
    result = run_evaluation()
    output_file = "/root/.openclaw/workspace/mas_repo/benchmark_results_gen95.json"
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"\n结果已保存至: {output_file}")