#!/usr/bin/env python3
"""
MAS Evaluator - Generation 38 Benchmark
测试 Zero-Point Token Energy 架构
"""

import sys
import json
import time
from datetime import datetime

sys.path.insert(0, '/root/.openclaw/workspace/mas_repo')

from benchmark.tasks import BenchmarkSuite, get_baseline_single_agent
from mas.core_gen38 import create_mas_system
from dataclasses import asdict

def run_evaluation():
    """运行完整评估"""
    print("=" * 60)
    print("MAS Evolution Engine - Gen38 Benchmark")
    print("Zero-Point Token Energy")
    print("=" * 60)
    
    # 创建MAS系统 (Gen38)
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
    
    # Gen38 特有统计
    stats = mas.get_stats()
    print(f"\n[Gen38 统计]")
    print(f"  - 版本: {stats['version']}")
    
    # 对比Gen37
    gen37_score = 81.0
    gen37_tokens = 5.0
    gen37_efficiency = 15882.0
    
    print(f"\n[对比Gen37]")
    score_diff = summary['avg_score'] - gen37_score
    token_diff = (summary['avg_tokens'] - gen37_tokens) / gen37_tokens * 100
    efficiency_diff = (summary['efficiency'] - gen37_efficiency) / gen37_efficiency * 100
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
    if summary['avg_tokens'] < 5:
        targets_met.append("Token<5")
    if summary['efficiency'] > 16000:
        targets_met.append("Efficiency>16000")
    
    if all([summary['avg_score'] >= 81, summary['avg_tokens'] < 5, summary['efficiency'] > 16000]):
        verdict = "✅✅✅ 新冠军! 完美达成所有目标"
    elif summary['avg_score'] >= 81 and summary['efficiency'] > gen37_efficiency:
        verdict = "✅✅ 新冠军! Efficiency提升"
    elif summary['avg_score'] > gen37_score:
        verdict = "✅ 新冠军! Score提升"
    elif summary['efficiency'] > gen37_efficiency:
        verdict = "✅ 新冠军! Efficiency提升"
    elif summary['avg_tokens'] < gen37_tokens:
        verdict = "✅ 新冠军! Token降低"
    else:
        verdict = "⚠️ 待优化 - 未能超越Gen37"
    
    print(f"[判定] {verdict}")
    if targets_met:
        print(f"[目标达成] {', '.join(targets_met)}")
    
    return {
        "timestamp": datetime.now().isoformat(),
        "generation": 38,
        "architecture": "Zero-Point Token Energy",
        "summary": summary,
        "baseline": baseline,
        "gen37_baseline": {
            "avg_score": gen37_score,
            "avg_tokens": gen37_tokens,
            "efficiency": gen37_efficiency
        },
        "composite_score": composite,
        "verdict": verdict,
        "targets_met": targets_met,
        "individual_results": [asdict(r) for r in results]
    }

if __name__ == "__main__":
    result = run_evaluation()
    
    # 保存结果
    output_file = "/root/.openclaw/workspace/mas_repo/benchmark_results_gen38.json"
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"\n结果已保存至: {output_file}")