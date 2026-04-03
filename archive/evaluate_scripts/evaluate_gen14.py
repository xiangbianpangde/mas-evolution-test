#!/usr/bin/env python3
"""
MAS Evaluator - Generation 14 Benchmark
Precision-Cached Minimal Processing
"""

import sys
import json
import time
from datetime import datetime

sys.path.insert(0, '/root/.openclaw/workspace/mas_repo')

from benchmark.tasks import BenchmarkSuite, get_baseline_single_agent
from mas.core_gen14 import create_mas_system
from dataclasses import asdict

def run_evaluation():
    """运行完整评估"""
    print("=" * 60)
    print("MAS Evolution Engine - Gen14 Benchmark")
    print("Precision-Cached Minimal Processing")
    print("=" * 60)
    
    # 创建MAS系统 (Gen14)
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
    
    # Gen14 特有统计
    stats = mas.get_stats()
    print(f"\n[Gen14 统计]")
    print(f"  - 总任务数: {stats['total_tasks']}")
    print(f"  - 缓存命中: {stats['cache_hits']}")
    print(f"  - 直接执行: {stats['direct_exec']}")
    print(f"  - 缓存命中率: {stats['cache']['hit_rate']:.1%}")
    print(f"  - 缓存大小: {stats['cache']['size']}")
    
    # 对比Gen13
    gen13_score = 77.0
    gen13_tokens = 59.1
    gen13_efficiency = 1302.9
    
    print(f"\n[对比Gen13]")
    score_diff = summary['avg_score'] - gen13_score
    token_diff = (summary['avg_tokens'] - gen13_tokens) / gen13_tokens * 100
    eff_diff = (summary['efficiency'] - gen13_efficiency) / gen13_efficiency * 100
    print(f"  - 得分差异: {score_diff:+.1f}")
    print(f"  - Token变化: {token_diff:+.1f}%")
    print(f"  - 效率变化: {eff_diff:+.1f}%")
    
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
    
    if composite > 260000:
        verdict = "🏆🏆 新冠军! 超越Gen13!"
    elif composite > 250000:
        verdict = "✅ 显著提升"
    elif composite > 200000:
        verdict = "✅ 通过 - 优于基线"
    elif composite > 100000:
        verdict = "⚠️ 待优化"
    else:
        verdict = "❌ 不合格"
    
    print(f"[判定] {verdict}")
    
    return {
        "timestamp": datetime.now().isoformat(),
        "generation": 14,
        "architecture": "Precision-Cached Minimal Processing",
        "summary": summary,
        "baseline": baseline,
        "gen13_baseline": {
            "avg_score": gen13_score,
            "avg_tokens": gen13_tokens,
            "efficiency": gen13_efficiency
        },
        "composite_score": composite,
        "verdict": verdict,
        "stats": stats,
        "individual_results": [asdict(r) for r in results]
    }

if __name__ == "__main__":
    result = run_evaluation()
    
    # 保存结果
    output_file = "/root/.openclaw/workspace/mas_repo/benchmark_results_gen14.json"
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"\n结果已保存至: {output_file}")