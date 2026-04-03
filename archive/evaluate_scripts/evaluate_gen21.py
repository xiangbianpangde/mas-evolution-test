#!/usr/bin/env python3
"""MAS Evaluator - Generation 21 Benchmark"""

import sys
import json
from datetime import datetime

sys.path.insert(0, '/root/.openclaw/workspace/mas_repo')

from benchmark.tasks import BenchmarkSuite, get_baseline_single_agent
from mas.core_gen21 import create_mas_system
from dataclasses import asdict

def run_evaluation():
    print("=" * 60)
    print("MAS Evolution Engine - Gen21 Benchmark")
    print("Hybrid: Hierarchical Teams + Quality Enhancement")
    print("=" * 60)
    
    mas = create_mas_system()
    benchmark = BenchmarkSuite()
    baseline = get_baseline_single_agent()
    
    print(f"\n[基线] 单Agent: Score={baseline['avg_score']}, Token={baseline['avg_tokens']}")
    
    print(f"\n[测试] 运行 {len(benchmark.tasks)} 个任务...")
    
    results = []
    for task in benchmark.tasks:
        result = benchmark.run_single(mas, task)
        results.append(result)
    
    summary = benchmark._compute_summary(results)
    
    print(f"\n[结果]")
    print(f"  - 完成率: {summary['success_rate']*100:.1f}%")
    print(f"  - 平均得分: {summary['avg_score']:.1f}")
    print(f"  - Token开销: {summary['avg_tokens']:.1f}/task")
    print(f"  - 效率指数: {summary['efficiency']:.2f}")
    
    stats = mas.get_stats()
    print(f"\n[Gen21] 专业:{stats['specialized_tasks']} 协作:{stats['collaboration_tasks']}")
    
    # 对比
    gen18 = {"score": 81, "tokens": 41, "efficiency": 1961}
    gen20 = {"score": 79, "tokens": 39, "efficiency": 2005}
    
    print(f"\n[对比Gen18] Score {summary['avg_score']-gen18['score']:+.1f}, Token {(summary['avg_tokens']-gen18['tokens'])/gen18['tokens']*100:+.1f}%, Eff {(summary['efficiency']-gen18['efficiency'])/gen18['efficiency']*100:+.1f}%")
    print(f"[对比Gen20] Score {summary['avg_score']-gen20['score']:+.1f}, Token {(summary['avg_tokens']-gen20['tokens'])/gen20['tokens']*100:+.1f}%, Eff {(summary['efficiency']-gen20['efficiency'])/gen20['efficiency']*100:+.1f}%")
    
    composite = (
        summary['success_rate'] * 100 * 0.4 +
        summary['avg_score'] * 0.3 +
        summary['efficiency'] * 1000 * 0.2 +
        max(0, 100 - summary['avg_latency_ms'] / 1000) * 0.1
    )
    
    print(f"\n[综合评分] {composite:.2f}/100")
    
    # 目标: Score>=81 AND Token<41 AND Efficiency>2005
    if summary['avg_score'] >= 81 and summary['avg_tokens'] < 41 and summary['efficiency'] > 2005:
        verdict = "🏆 新冠军! 达成所有目标!"
    elif summary['avg_score'] >= 80 and summary['avg_tokens'] < 42:
        verdict = "✅ 优秀"
    else:
        verdict = "⚠️ 待优化"
    
    print(f"[判定] {verdict}")
    
    return {
        "timestamp": datetime.now().isoformat(),
        "generation": 21,
        "architecture": "Hybrid Hierarchical + Quality Enhancement",
        "summary": summary,
        "baseline": baseline,
        "composite_score": composite,
        "verdict": verdict,
        "stats": stats,
        "individual_results": [asdict(r) for r in results]
    }

if __name__ == "__main__":
    result = run_evaluation()
    with open("/root/.openclaw/workspace/mas_repo/benchmark_results_gen21.json", 'w') as f:
        json.dump(result, f, indent=2)
    print(f"\n结果已保存")