#!/usr/bin/env python3
"""
MAS Evaluator - Generation 118 Benchmark
"""

import sys
import json
from datetime import datetime

sys.path.insert(0, '/root/.openclaw/workspace/mas_repo')

from benchmark.tasks import BenchmarkSuite, get_baseline_single_agent
from mas.core_gen118 import create_mas_system
from dataclasses import asdict

def run_evaluation():
    print("=" * 60)
    print("MAS Evolution Engine - Gen118 Benchmark")
    print("=" * 60)
    
    mas = create_mas_system()
    benchmark = BenchmarkSuite()
    baseline = get_baseline_single_agent()
    
    print(f"\n[测试] 运行 {len(benchmark.tasks)} 个任务...")
    results, summary = benchmark.run_all(mas)
    
    print(f"\n[结果] Score: {summary['avg_score']:.1f}, Token: {summary['avg_tokens']:.1f}, Eff: {summary['efficiency']:.0f}")
    
    print(f"\n[任务分解]")
    for r in results:
        print(f"  {r.task_id}: tokens={r.tokens}, score={r.score}")
    
    # Compare with Gen108
    gen108_tokens = 1.9
    gen108_efficiency = 42632.0
    gen108_score = 81.0
    
    print(f"\n[对比Gen108]")
    token_diff = (summary['avg_tokens'] - gen108_tokens) / gen108_tokens * 100
    efficiency_diff = (summary['efficiency'] - gen108_efficiency) / gen108_efficiency * 100
    print(f"  - Token变化: {token_diff:+.1f}%")
    print(f"  - Efficiency变化: {efficiency_diff:+.1f}%")
    
    composite = (
        summary['success_rate'] * 100 * 0.4 +
        summary['avg_score'] * 0.3 +
        summary['efficiency'] / 100 * 0.2 +
        max(0, 100 - summary['avg_latency_ms'] / 1000) * 0.1
    )
    
    print(f"\n[综合评分] {composite:.2f}/100")
    
    if summary['avg_tokens'] < gen108_tokens and summary['avg_score'] >= 81:
        verdict = "✅✅✅ 新冠军! Token更低!"
    elif summary['efficiency'] > gen108_efficiency:
        verdict = "✅✅ 新冠军! Efficiency提升"
    elif summary['avg_score'] > gen108_score:
        verdict = "✅ 新冠军! Score提升"
    else:
        verdict = "⚠️ 待优化"
    
    print(f"[判定] {verdict}")
    
    return {
        "timestamp": datetime.now().isoformat(),
        "generation": 118,
        "summary": summary,
        "composite_score": composite,
        "verdict": verdict,
        "individual_results": [asdict(r) for r in results]
    }

if __name__ == "__main__":
    result = run_evaluation()
    output_file = f"/root/.openclaw/workspace/mas_repo/benchmark_results_gen118.json"
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"\n结果已保存至: {output_file}")