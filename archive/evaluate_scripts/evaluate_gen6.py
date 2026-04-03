#!/usr/bin/env python3
"""
MAS Evaluator - Generation 6 Benchmark
测试 Token Budget + Early Exit 架构
"""

import sys
import json
import time
from datetime import datetime

sys.path.insert(0, '/root/.openclaw/workspace/mas_repo')

from benchmark.tasks import BenchmarkSuite, get_baseline_single_agent
from mas.core_gen6 import create_mas_system
from dataclasses import asdict

def run_evaluation():
    """运行完整评估"""
    print("=" * 60)
    print("MAS Evolution Engine - Gen6 Benchmark")
    print("Token Budget + Early Exit Strategy")
    print("=" * 60)
    
    # 创建MAS系统 (Gen6)
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
    
    # Gen6 特有统计
    stats = mas.get_stats()
    print(f"\n[Gen6 统计]")
    print(f"  - 总任务数: {stats['total_tasks']}")
    print(f"  - 缓存命中: {stats['cache_hits']}")
    print(f"  - 直接执行: {stats['direct_exec']}")
    print(f"  - 提前退出: {stats['early_exits']}")
    print(f"  - 总预算: {stats['total_budget']}")
    print(f"  - 总Token: {stats['total_tokens']}")
    if stats.get('avg_efficiency'):
        print(f"  - 预算效率: {stats['avg_efficiency']:.2%}")
    
    # 改进对比
    print(f"\n[对比基线]")
    score_improvement = (summary['avg_score'] - baseline['avg_score']) / baseline['avg_score'] * 100
    token_change = (summary['avg_tokens'] - baseline['avg_tokens']) / baseline['avg_tokens'] * 100
    print(f"  - 得分提升: {score_improvement:+.1f}%")
    print(f"  - Token变化: {token_change:+.1f}%")
    
    # 对比Gen5
    gen5_score = 80.0
    gen5_tokens = 199
    
    print(f"\n[对比Gen5]")
    gen5_token_diff = (summary['avg_tokens'] - gen5_tokens) / gen5_tokens * 100
    print(f"  - Token变化: {gen5_token_diff:+.1f}%")
    
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
    
    if composite > 70000:
        verdict = "✅ NEW BEST - 显著优于Gen5"
    elif composite > 60000:
        verdict = "✅ 通过 - 优于基线"
    elif composite > 50000:
        verdict = "⚠️ 待优化 - 接近基线"
    else:
        verdict = "❌ 不合格 - 显著低于基线"
    
    print(f"[判定] {verdict}")
    
    return {
        "timestamp": datetime.now().isoformat(),
        "generation": 6,
        "architecture": "Token Budget + Early Exit",
        "summary": summary,
        "baseline": baseline,
        "gen5_baseline": {
            "avg_score": gen5_score,
            "avg_tokens": gen5_tokens,
        },
        "composite_score": composite,
        "verdict": verdict,
        "stats": stats,
        "individual_results": [asdict(r) for r in results]
    }

if __name__ == "__main__":
    result = run_evaluation()
    
    # 保存结果
    output_file = "/root/.openclaw/workspace/mas_repo/benchmark_results_gen6.json"
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"\n结果已保存至: {output_file}")