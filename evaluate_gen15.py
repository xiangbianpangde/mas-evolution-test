#!/usr/bin/env python3
"""
MAS Evaluator - Generation 15 Benchmark
测试 Pattern-Inference + Dynamic Quality Gating 架构
"""

import sys
import json
import time
from datetime import datetime

sys.path.insert(0, '/root/.openclaw/workspace/mas_repo')

from benchmark.tasks import BenchmarkSuite, get_baseline_single_agent
from mas.core_gen15 import create_mas_system
from dataclasses import asdict

def run_evaluation():
    """运行完整评估"""
    print("=" * 60)
    print("MAS Evolution Engine - Gen15 Benchmark")
    print("Pattern-Inference + Dynamic Quality Gating")
    print("=" * 60)
    
    # 创建MAS系统 (Gen15)
    mas = create_mas_system()
    
    # 创建Benchmark
    benchmark = BenchmarkSuite()
    
    # 获取基线
    baseline = get_baseline_single_agent()
    print(f"\n[基线] 单Agent系统:")
    print(f"  - 任务完成率: {baseline['success_rate']*100:.1f}%")
    print(f"  - 平均得分: {baseline['avg_score']:.1f}")
    print(f"  - Token效率: {baseline['avg_tokens']:.0f}/task")
    
    # 运行测试
    print(f"\n[测试] 开始运行 {len(benchmark.tasks)} 个任务...")
    results, summary = benchmark.run_all(mas)
    
    # 打印结果
    print(f"\n[结果汇总]")
    print(f"  - 任务完成率: {summary['success_rate']*100:.1f}%")
    print(f"  - 平均得分: {summary['avg_score']:.1f}/100")
    print(f"  - Token开销: {summary['avg_tokens']:.0f}/task")
    print(f"  - 平均延迟: {summary['avg_latency_ms']:.0f}ms")
    print(f"  - 效率指数: {summary['efficiency']:.4f}")
    
    # Gen15 特有统计
    stats = mas.get_stats()
    print(f"\n[Gen15 统计]")
    print(f"  - 版本: {stats['version']}")
    print(f"  - 总任务数: {stats['total_tasks']}")
    print(f"  - 缓存命中: {stats['cache_hits']}")
    print(f"  - 直接执行: {stats['direct_exec']}")
    print(f"  - 复杂度分布: {dict(stats['complexity_counts'])}")
    print(f"  - 缓存统计: {stats['cache']}")
    
    # 对比Gen14
    gen14_tokens = 47
    gen14_score = 78
    gen14_efficiency = 1646
    
    print(f"\n[对比Gen14 (当前冠军)]")
    token_diff = (summary['avg_tokens'] - gen14_tokens) / gen14_tokens * 100
    score_diff = summary['avg_score'] - gen14_score
    eff_diff = (summary['efficiency'] - gen14_efficiency) / gen14_efficiency * 100
    print(f"  - Token: {summary['avg_tokens']:.0f} vs {gen14_tokens} ({token_diff:+.1f}%)")
    print(f"  - Score: {summary['avg_score']:.1f} vs {gen14_score} ({score_diff:+.1f})")
    print(f"  - Efficiency: {summary['efficiency']:.1f} vs {gen14_efficiency} ({eff_diff:+.1f}%)")
    
    # 计算综合评分
    completion_weight = 0.4
    score_weight = 0.3
    efficiency_weight = 0.2
    latency_weight = 0.1
    
    latency_score = max(0, 100 - summary['avg_latency_ms'] / 1000)
    
    composite = (
        summary['success_rate'] * 100 * completion_weight +
        summary['avg_score'] * score_weight +
        summary['efficiency'] * 1000 * efficiency_weight +
        latency_score * latency_weight
    )
    
    print(f"\n[综合评分] {composite:.2f}/100")
    
    if composite > 329187:  # Gen14's composite
        verdict = "🏆🏆 新冠军! 超越Gen14!"
    elif composite > 260648:  # Gen13's composite
        verdict = "🏆 超越Gen13!"
    elif composite > 70:
        verdict = "✅ 通过 - 优于基线"
    else:
        verdict = "⚠️ 待优化"
    
    print(f"[判定] {verdict}")
    
    return {
        "timestamp": datetime.now().isoformat(),
        "generation": 15,
        "architecture": "Pattern-Inference + Dynamic Quality Gating",
        "summary": summary,
        "baseline": baseline,
        "gen14_baseline": {
            "avg_tokens": gen14_tokens,
            "avg_score": gen14_score,
            "efficiency": gen14_efficiency
        },
        "composite_score": composite,
        "verdict": verdict,
        "stats": stats,
        "individual_results": [asdict(r) for r in results]
    }

if __name__ == "__main__":
    result = run_evaluation()
    
    # 保存结果
    output_file = "/root/.openclaw/workspace/mas_repo/benchmark_results_gen15.json"
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"\n结果已保存至: {output_file}")