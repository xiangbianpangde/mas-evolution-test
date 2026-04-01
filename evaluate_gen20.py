#!/usr/bin/env python3
"""
MAS Evaluator - Generation 20 Benchmark
测试 Optimized Hierarchical Teams v2
"""

import sys
import json
from datetime import datetime

sys.path.insert(0, '/root/.openclaw/workspace/mas_repo')

from benchmark.tasks import BenchmarkSuite, get_baseline_single_agent
from mas.core_gen20 import create_mas_system
from dataclasses import asdict

def run_evaluation():
    print("=" * 60)
    print("MAS Evolution Engine - Gen20 Benchmark")
    print("Optimized Hierarchical Teams v2")
    print("=" * 60)
    
    mas = create_mas_system()
    benchmark = BenchmarkSuite()
    baseline = get_baseline_single_agent()
    
    print(f"\n[基线] 单Agent系统:")
    print(f"  - 任务完成率: {baseline['success_rate']*100:.1f}%")
    print(f"  - 平均得分: {baseline['avg_score']:.1f}")
    print(f"  - Token效率: {baseline['avg_tokens']:.0f}/task")
    
    print(f"\n[测试] 开始运行 {len(benchmark.tasks)} 个任务...")
    
    results = []
    for task in benchmark.tasks:
        result = benchmark.run_single(mas, task)
        results.append(result)
    
    summary = benchmark._compute_summary(results)
    
    print(f"\n[结果汇总]")
    print(f"  - 任务完成率: {summary['success_rate']*100:.1f}%")
    print(f"  - 平均得分: {summary['avg_score']:.1f}/100")
    print(f"  - Token开销: {summary['avg_tokens']:.0f}/task")
    print(f"  - 平均延迟: {summary['avg_latency_ms']:.0f}ms")
    print(f"  - 效率指数: {summary['efficiency']:.4f}")
    
    stats = mas.get_stats()
    print(f"\n[Gen20 统计]")
    print(f"  - 总任务数: {stats['total_tasks']}")
    print(f"  - 专业团队任务: {stats['specialized_tasks']}")
    print(f"  - 协作任务: {stats['collaboration_tasks']}")
    print(f"  - 团队使用: {stats['team_usage']}")
    
    # 对比
    gen18_score = 81
    gen18_tokens = 41
    gen18_efficiency = 1961
    gen19_score = 80
    gen19_tokens = 43
    gen19_efficiency = 1852
    
    print(f"\n[对比Gen18]")
    print(f"  - 得分: {summary['avg_score'] - gen18_score:+.1f}")
    print(f"  - Token: {(summary['avg_tokens'] - gen18_tokens) / gen18_tokens * 100:+.1f}%")
    print(f"  - 效率: {(summary['efficiency'] - gen18_efficiency) / gen18_efficiency * 100:+.1f}%")
    
    print(f"\n[对比Gen19]")
    print(f"  - 得分: {summary['avg_score'] - gen19_score:+.1f}")
    print(f"  - Token: {(summary['avg_tokens'] - gen19_tokens) / gen19_tokens * 100:+.1f}%")
    print(f"  - 效率: {(summary['efficiency'] - gen19_efficiency) / gen19_efficiency * 100:+.1f}%")
    
    # 综合评分
    composite = (
        summary['success_rate'] * 100 * 0.4 +
        summary['avg_score'] * 0.3 +
        summary['efficiency'] * 1000 * 0.2 +
        max(0, 100 - summary['avg_latency_ms'] / 1000) * 0.1
    )
    
    print(f"\n[综合评分] {composite:.2f}/100")
    
    if summary['avg_score'] >= 81 and summary['avg_tokens'] <= 41 and summary['efficiency'] >= 1961:
        verdict = "🏆 超越Gen18! 新冠军!"
    elif summary['avg_score'] >= 80 and summary['avg_tokens'] < 45 and summary['efficiency'] > 1800:
        verdict = "✅ 优秀 - 达标"
    else:
        verdict = "⚠️ 待优化"
    
    print(f"[判定] {verdict}")
    
    return {
        "timestamp": datetime.now().isoformat(),
        "generation": 20,
        "architecture": "Optimized Hierarchical Teams v2",
        "summary": summary,
        "baseline": baseline,
        "gen18_baseline": {"avg_score": gen18_score, "avg_tokens": gen18_tokens, "efficiency": gen18_efficiency},
        "gen19_baseline": {"avg_score": gen19_score, "avg_tokens": gen19_tokens, "efficiency": gen19_efficiency},
        "composite_score": composite,
        "verdict": verdict,
        "stats": stats,
        "individual_results": [asdict(r) for r in results]
    }

if __name__ == "__main__":
    result = run_evaluation()
    output_file = "/root/.openclaw/workspace/mas_repo/benchmark_results_gen20.json"
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"\n结果已保存至: {output_file}")