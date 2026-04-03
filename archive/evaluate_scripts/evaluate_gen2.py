#!/usr/bin/env python3
"""
MAS Evaluator - Generation 2 Benchmark
测试 Mesh-based Collaborative 架构
"""

import sys
import json
import time
from datetime import datetime

sys.path.insert(0, '/root/.openclaw/workspace/mas_repo')

from benchmark.tasks import BenchmarkSuite, get_baseline_single_agent
from mas.core_gen2 import create_mas_system
from dataclasses import asdict

def run_evaluation():
    """运行完整评估"""
    print("=" * 60)
    print("MAS Evolution Engine - Gen2 Benchmark")
    print("Mesh-based Collaborative Supervisor-Worker")
    print("=" * 60)
    
    # 创建MAS系统 (Gen2)
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
    
    # Gen2 特有统计
    stats = mas.get_stats()
    print(f"\n[Gen2 统计]")
    print(f"  - 总任务数: {stats['total_tasks']}")
    print(f"  - 并行任务: {stats['parallel_tasks']}")
    print(f"  - 协作次数: {stats['collaborations']}")
    
    # 改进对比
    print(f"\n[对比基线]")
    score_improvement = (summary['avg_score'] - baseline['avg_score']) / baseline['avg_score'] * 100
    token_change = (summary['avg_tokens'] - baseline['avg_tokens']) / baseline['avg_tokens'] * 100
    print(f"  - 得分提升: {score_improvement:+.1f}%")
    print(f"  - Token变化: {token_change:+.1f}%")
    
    # 对比Gen1
    gen1_score = 80.0
    gen1_tokens = 303
    gen1_completion = 1.0
    
    print(f"\n[对比Gen1]")
    gen1_score_diff = summary['avg_score'] - gen1_score
    gen1_token_diff = (summary['avg_tokens'] - gen1_tokens) / gen1_tokens * 100
    print(f"  - 得分差异: {gen1_score_diff:+.1f}")
    print(f"  - Token变化: {gen1_token_diff:+.1f}%")
    
    # 计算综合评分
    # 加权: 完成率40% + 得分30% + 效率20% + 延迟10%
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
    
    if composite > 70:
        verdict = "✅ 通过 - 优于基线"
    elif composite > 50:
        verdict = "⚠️ 待优化 - 接近基线"
    else:
        verdict = "❌ 不合格 - 显著低于基线"
    
    print(f"[判定] {verdict}")
    
    return {
        "timestamp": datetime.now().isoformat(),
        "generation": 2,
        "architecture": "Mesh-based Collaborative",
        "summary": summary,
        "baseline": baseline,
        "gen1_baseline": {
            "avg_score": gen1_score,
            "avg_tokens": gen1_tokens,
            "success_rate": gen1_completion
        },
        "composite_score": composite,
        "verdict": verdict,
        "stats": stats,
        "individual_results": [asdict(r) for r in results]
    }

if __name__ == "__main__":
    result = run_evaluation()
    
    # 保存结果
    output_file = "/root/.openclaw/workspace/mas_repo/benchmark_results_gen2.json"
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"\n结果已保存至: {output_file}")