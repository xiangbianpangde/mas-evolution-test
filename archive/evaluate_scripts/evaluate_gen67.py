#!/usr/bin/env python3
"""
MAS Evaluator - Generation 67 Benchmark
测试 Computational Complexity-Aware - Maximum Efficiency
"""

import sys
import json
import time
from datetime import datetime

sys.path.insert(0, '/root/.openclaw/workspace/mas_repo')

from benchmark.tasks import BenchmarkSuite, get_baseline_single_agent
from mas.core_gen67 import create_mas_system
from dataclasses import asdict

def run_evaluation():
    """运行完整评估"""
    print("=" * 60)
    print("MAS Evolution Engine - Gen67 Benchmark")
    print("Computational Complexity-Aware - Maximum Efficiency")
    print("=" * 60)
    
    # 创建MAS系统 (Gen67)
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
    
    # Gen67 特有统计
    stats = mas.get_stats()
    print(f"\n[Gen67 统计]")
    print(f"  - 版本: {stats['version']}")
    
    # 对比Gen66
    gen66_score = 81.0
    gen66_tokens = 11.7
    gen66_efficiency = 6923.0
    
    print(f"\n[对比Gen66]")
    score_diff = summary['avg_score'] - gen66_score
    token_diff = (summary['avg_tokens'] - gen66_tokens) / gen66_tokens * 100
    efficiency_diff = (summary['efficiency'] - gen66_efficiency) / gen66_efficiency * 100
    print(f"  - 得分差异: {score_diff:+.1f}")
    print(f"  - Token变化: {token_diff:+.1f}%")
    print(f"  - Efficiency变化: {efficiency_diff:+.1f}%")
    
    # 计算综合评分
    completion_weight = 0.4
    score_weight = 0.3
    efficiency_weight = 0.2
    latency_weight = 0.1
    
    latency_score = max(0, 100 - summary['avg_latency_ms'] / 1000)
    
    composite = (
        summary['success_rate'] * 100 * completion_weight +
        summary['avg_score'] * score_weight +
        summary['efficiency'] * 10 * efficiency_weight +
        latency_score * latency_weight
    )
    
    print(f"\n[综合评分] {composite:.2f}/100")
    
    # 目标达成检查
    targets_met = []
    if summary['avg_score'] >= 81:
        targets_met.append("Score>=81")
    if summary['avg_tokens'] < 12:
        targets_met.append("Token<12")
    if summary['efficiency'] > 6923:
        targets_met.append("Efficiency>6923")
    
    if all([summary['avg_score'] >= 81, summary['avg_tokens'] < 12, summary['efficiency'] > 6923]):
        verdict = "✅✅✅ 新冠军! 完美达成所有目标"
    elif summary['avg_score'] >= 81 and summary['efficiency'] > gen66_efficiency:
        verdict = "✅✅ 新冠军! Efficiency提升"
    elif summary['avg_score'] > gen66_score:
        verdict = "✅ 新冠军! Score提升"
    elif summary['efficiency'] > gen66_efficiency:
        verdict = "✅ 新冠军! Efficiency提升"
    elif summary['avg_tokens'] < gen66_tokens:
        verdict = "✅ 新冠军! Token降低"
    else:
        verdict = "⚠️ 待优化 - 未能超越Gen66"
    
    print(f"[判定] {verdict}")
    if targets_met:
        print(f"[目标达成] {', '.join(targets_met)}")
    
    return {
        "timestamp": datetime.now().isoformat(),
        "generation": 67,
        "architecture": "Computational Complexity-Aware - Maximum Efficiency",
        "summary": summary,
        "baseline": baseline,
        "gen66_baseline": {
            "avg_score": gen66_score,
            "avg_tokens": gen66_tokens,
            "efficiency": gen66_efficiency
        },
        "composite_score": composite,
        "verdict": verdict,
        "targets_met": targets_met,
        "individual_results": [asdict(r) for r in results]
    }

if __name__ == "__main__":
    result = run_evaluation()
    
    # 保存结果
    output_file = "/root/.openclaw/workspace/mas_repo/benchmark_results_gen67.json"
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"\n结果已保存至: {output_file}")