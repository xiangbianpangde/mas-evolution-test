#!/usr/bin/env python3
"""
MAS Evaluator - Generation 52 Benchmark
NEW PARADIGM: Hierarchical Two-Level Supervisor Architecture

这是全新纪元的开始 - 不再追求极致Token压缩，
而是探索真正的多Agent协作架构。
"""

import sys
import json
import time
from datetime import datetime

sys.path.insert(0, '/root/.openclaw/workspace/mas_repo')

from benchmark.tasks import BenchmarkSuite, get_baseline_single_agent
from mas.core_gen52 import create_mas_system
from dataclasses import asdict

def run_evaluation():
    print("=" * 60)
    print("MAS Evolution Engine - Gen52 Benchmark")
    print("NEW PARADIGM: Hierarchical Two-Level Supervisor")
    print("=" * 60)
    
    mas = create_mas_system()
    benchmark = BenchmarkSuite()
    baseline = get_baseline_single_agent()
    
    print(f"\n[基线] 单Agent系统:")
    print(f"  - 任务完成率: {baseline['success_rate']*100:.1f}%")
    print(f"  - 平均得分: {baseline['avg_score']:.1f}")
    print(f"  - Token效率: {baseline['avg_tokens']:.0f}/task")
    
    print(f"\n[测试] 运行 {len(benchmark.tasks)} 个任务...")
    results, summary = benchmark.run_all(mas)
    
    print(f"\n[结果汇总]")
    print(f"  - 任务完成率: {summary['success_rate']*100:.1f}%")
    print(f"  - 平均得分: {summary['avg_score']:.1f}/100")
    print(f"  - Token开销: {summary['avg_tokens']:.0f}/task")
    print(f"  - 平均延迟: {summary['avg_latency_ms']:.0f}ms")
    print(f"  - 效率指数: {summary['efficiency']:.4f}")
    
    # Gen52 stats
    stats = mas.get_stats()
    print(f"\n[Gen52 统计]")
    print(f"  - 版本: {stats['version']}")
    print(f"  - 范式: {stats['paradigm']}")
    print(f"  - 域统计: {stats['domain_stats']}")
    
    # 对比Gen38
    gen38_score = 81.0
    gen38_tokens = 5.1
    gen38_efficiency = 15882
    
    print(f"\n[对比Gen38冠军 (Token优化范式)]")
    print(f"  - Gen52得分: {summary['avg_score']:.1f} vs Gen38: {gen38_score}")
    print(f"  - Gen52 Token: {summary['avg_tokens']:.1f} vs Gen38: {gen38_tokens}")
    print(f"  - Gen52 Efficiency: {summary['efficiency']:.1f} vs Gen38: {gen38_efficiency}")
    
    # 判断
    efficiency_ratio = summary['efficiency'] / gen38_efficiency * 100
    print(f"\n[效率比] Gen52 is {efficiency_ratio:.1f}% of Gen38's efficiency")
    
    if summary['avg_score'] > gen38_score:
        verdict = "✅ 新冠军! Score超越"
    elif summary['efficiency'] > gen38_efficiency:
        verdict = "✅ 新冠军! Efficiency超越"
    else:
        verdict = "⚠️ 新范式探索 - 效率低于Gen38但可能有其他优势"
    
    print(f"[判定] {verdict}")
    print(f"\n[注意] Gen52采用全新双层Supervisor范式，")
    print(f"        不与Gen38在Token效率上直接竞争。")
    
    return {
        "timestamp": datetime.now().isoformat(),
        "generation": 52,
        "architecture": "Hierarchical Two-Level Supervisor",
        "paradigm": "NEW_ERA",
        "summary": summary,
        "baseline": baseline,
        "gen38_baseline": {
            "avg_score": gen38_score,
            "avg_tokens": gen38_tokens,
            "efficiency": gen38_efficiency
        },
        "composite_score": summary['efficiency'] * 0.1 + summary['avg_score'] * 10,
        "verdict": verdict,
        "stats": stats,
        "individual_results": [asdict(r) for r in results]
    }

if __name__ == "__main__":
    result = run_evaluation()
    
    output_file = "/root/.openclaw/workspace/mas_repo/benchmark_results_gen52.json"
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"\n结果已保存至: {output_file}")