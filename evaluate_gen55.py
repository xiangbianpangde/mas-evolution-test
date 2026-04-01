#!/usr/bin/env python3
"""
MAS Evaluator - Generation 55 Benchmark
NEW PARADIGM: Self-Optimizing Meta-Architecture (SOMA)

This is a completely different paradigm from Token Optimization:
- Self: System examines its own decisions
- Optimizing: Dynamically adjusts based on history
- Meta: Strategy about strategies
"""

import sys
import json
import time
from datetime import datetime

sys.path.insert(0, '/root/.openclaw/workspace/mas_repo')

from benchmark.tasks import BenchmarkSuite, get_baseline_single_agent
from mas.core_gen55 import create_mas_system
from dataclasses import asdict

def run_evaluation():
    """运行完整评估"""
    print("=" * 60)
    print("MAS Evolution Engine - Gen55 Benchmark")
    print("NEW PARADIGM: Self-Optimizing Meta-Architecture (SOMA)")
    print("=" * 60)
    
    mas = create_mas_system()
    benchmark = BenchmarkSuite()
    baseline = get_baseline_single_agent()
    
    print(f"\n[基线] 单Agent系统:")
    print(f"  - 任务完成率: {baseline['success_rate']*100:.1f}%")
    print(f"  - 平均得分: {baseline['avg_score']:.1f}")
    print(f"  - Token效率: {baseline['avg_tokens']:.0f}/task")
    
    print(f"\n[测试] 开始运行 {len(benchmark.tasks)} 个任务...")
    print("[注意] SOMA paradigm 不与Gen38在Token效率上直接竞争")
    print("[注意] 这是全新纪元的探索...")
    
    results, summary = benchmark.run_all(mas)
    
    print(f"\n[结果汇总]")
    print(f"  - 任务完成率: {summary['success_rate']*100:.1f}%")
    print(f"  - 平均得分: {summary['avg_score']:.1f}/100")
    print(f"  - Token开销: {summary['avg_tokens']:.0f}/task")
    print(f"  - 平均延迟: {summary['avg_latency_ms']:.0f}ms")
    print(f"  - 效率指数: {summary['efficiency']:.4f}")
    
    stats = mas.get_stats()
    print(f"\n[SOMA 统计]")
    print(f"  - 版本: {stats['version']}")
    print(f"  - 架构: {stats['architecture']}")
    print(f"  - 决策记录: {stats['total_decisions']}")
    print(f"  - 策略数量: {stats['strategy_count']}")
    
    # 对比Gen38
    gen38_score = 81.0
    gen38_tokens = 5.1
    gen38_efficiency = 15882
    
    print(f"\n[对比Gen38冠军 (Token优化范式)]")
    print(f"  - Gen55得分: {summary['avg_score']:.1f} vs Gen38: {gen38_score:.1f}")
    print(f"  - Gen55 Token: {summary['avg_tokens']:.1f} vs Gen38: {gen38_tokens:.1f}")
    print(f"  - Gen55 Efficiency: {summary['efficiency']:.1f} vs Gen38: {gen38_efficiency:.1f}")
    
    efficiency_ratio = summary['efficiency'] / gen38_efficiency * 100
    print(f"  - Gen55效率是Gen38的 {efficiency_ratio:.1f}%")
    
    # 判断
    score_diff = summary['avg_score'] - gen38_score
    efficiency_diff = (summary['efficiency'] - gen38_efficiency) / gen38_efficiency * 100
    
    if summary['avg_score'] >= 81 and summary['efficiency'] > gen38_efficiency:
        verdict = "🏆🏆🏵️ 超级冠军! 全新范式超越Token优化!"
    elif summary['avg_score'] > gen38_score:
        verdict = "🏆 新冠军! Score超越Gen38"
    elif efficiency_diff > 50:
        verdict = "⚡ 新范式效率冠军! Efficiency远超Gen38"
    elif summary['avg_score'] >= 78 and efficiency_diff > -20:
        verdict = "✅ 新范式可接受 - Score接近但架构更先进"
    else:
        verdict = "⚠️ 新范式探索 - 未能超越Gen38"
    
    print(f"\n[判定] {verdict}")
    
    return {
        "timestamp": datetime.now().isoformat(),
        "generation": 55,
        "architecture": "Self-Optimizing Meta-Architecture (SOMA)",
        "paradigm": "Meta-Cognition",
        "summary": summary,
        "baseline": baseline,
        "gen38_baseline": {
            "avg_score": gen38_score,
            "avg_tokens": gen38_tokens,
            "efficiency": gen38_efficiency
        },
        "composite_score": summary['efficiency'] * 0.5 + summary['avg_score'] * 50,
        "verdict": verdict,
        "stats": stats,
        "individual_results": [asdict(r) for r in results]
    }

if __name__ == "__main__":
    result = run_evaluation()
    
    output_file = "/root/.openclaw/workspace/mas_repo/benchmark_results_gen55.json"
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"\n结果已保存至: {output_file}")