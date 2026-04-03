#!/usr/bin/env python3
"""MAS Evaluator - Generation 22"""

import sys
import json
from datetime import datetime

sys.path.insert(0, '/root/.openclaw/workspace/mas_repo')

from benchmark.tasks import BenchmarkSuite, get_baseline_single_agent
from mas.core_gen22 import create_mas_system
from dataclasses import asdict

def run_evaluation():
    print("=" * 60)
    print("Gen22: Enhanced Hierarchical + Semantic Cache")
    print("=" * 60)
    
    mas = create_mas_system()
    benchmark = BenchmarkSuite()
    
    print(f"\n运行 {len(benchmark.tasks)} 个任务...")
    
    results = []
    for task in benchmark.tasks:
        result = benchmark.run_single(mas, task)
        results.append(result)
    
    summary = benchmark._compute_summary(results)
    
    print(f"\n[结果]")
    print(f"  Score: {summary['avg_score']:.1f}")
    print(f"  Token: {summary['avg_tokens']:.1f}/task")
    print(f"  Efficiency: {summary['efficiency']:.2f}")
    
    stats = mas.get_stats()
    print(f"\n[统计]")
    print(f"  Cache hits: {stats['cache_hits']}")
    print(f"  Direct exec: {stats['direct_exec']}")
    print(f"  Team usage: {stats['team_usage']}")
    
    # 对比
    gen18 = (81, 41, 1961)
    gen20 = (79, 39, 2005)
    
    s, t, e = summary['avg_score'], summary['avg_tokens'], summary['efficiency']
    print(f"\n[对比 Gen18] Score {s-gen18[0]:+.1f}, Token {(t-gen18[1])/gen18[1]*100:+.1f}%, Eff {(e-gen18[2])/gen18[2]*100:+.1f}%")
    print(f"[对比 Gen20] Score {s-gen20[0]:+.1f}, Token {(t-gen20[1])/gen20[1]*100:+.1f}%, Eff {(e-gen20[2])/gen20[2]*100:+.1f}%")
    
    composite = (
        summary['success_rate'] * 100 * 0.4 +
        summary['avg_score'] * 0.3 +
        summary['efficiency'] * 1000 * 0.2 +
        max(0, 100 - summary['avg_latency_ms'] / 1000) * 0.1
    )
    
    print(f"\n[综合评分] {composite:.2f}/100")
    
    if s >= 81 and t < 40 and e > 2000:
        verdict = "🏆 新冠军!"
    elif s >= 80 and t < 42:
        verdict = "✅ 达标"
    else:
        verdict = "⚠️ 待优化"
    
    print(f"[判定] {verdict}")
    
    return {
        "generation": 22,
        "architecture": "Enhanced Hierarchical + Semantic Cache",
        "summary": summary,
        "composite_score": composite,
        "verdict": verdict,
        "stats": stats,
        "individual_results": [asdict(r) for r in results]
    }

if __name__ == "__main__":
    result = run_evaluation()
    with open("/root/.openclaw/workspace/mas_repo/benchmark_results_gen22.json", 'w') as f:
        json.dump(result, f, indent=2)
    print(f"\n已保存到 benchmark_results_gen22.json")