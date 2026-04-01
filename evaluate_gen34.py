#!/usr/bin/env python3
"""
MAS Evaluator - Generation 34 Benchmark
测试 Quantum Token Reduction 架构
"""

import sys
import json
import time
from datetime import datetime

sys.path.insert(0, '/root/.openclaw/workspace/mas_repo')

from benchmark.tasks import BenchmarkSuite, get_baseline_single_agent
from mas.core_gen34 import create_mas_system
from dataclasses import asdict

def run_evaluation():
    """运行完整评估"""
    print("=" * 60)
    print("MAS Evolution Engine - Gen34 Benchmark")
    print("Quantum Token Reduction")
    print("=" * 60)
    
    mas = create_mas_system()
    benchmark = BenchmarkSuite()
    baseline = get_baseline_single_agent()
    
    print(f"\n[基线] 单Agent系统:")
    print(f"  - 任务完成率: {baseline['success_rate']*100:.1f}%")
    print(f"  - 平均得分: {baseline['avg_score']:.1f}")
    print(f"  - Token效率: {baseline['avg_tokens']:.0f}/task")
    
    print(f"\n[测试] 开始运行 {len(benchmark.tasks)} 个任务...")
    results, summary = benchmark.run_all(mas)
    
    print(f"\n[结果汇总]")
    print(f"  - 任务完成率: {summary['success_rate']*100:.1f}%")
    print(f"  - 平均得分: {summary['avg_score']:.1f}/100")
    print(f"  - Token开销: {summary['avg_tokens']:.0f}/task")
    print(f"  - 平均延迟: {summary['avg_latency_ms']:.0f}ms")
    print(f"  - 效率指数: {summary['efficiency']:.4f}")
    
    stats = mas.get_stats()
    print(f"\n[Gen34 统计]")
    print(f"  - 版本: {stats['version']}")
    
    # 对比Gen33
    gen33_score = 81.0
    gen33_tokens = 12.0
    gen33_efficiency = 6480.0
    
    print(f"\n[对比Gen33]")
    score_diff = summary['avg_score'] - gen33_score
    token_diff = (summary['avg_tokens'] - gen33_tokens) / gen33_tokens * 100
    efficiency_diff = (summary['efficiency'] - gen33_efficiency) / gen33_efficiency * 100
    print(f"  - 得分差异: {score_diff:+.1f}")
    print(f"  - Token变化: {token_diff:+.1f}%")
    print(f"  - Efficiency变化: {efficiency_diff:+.1f}%")
    
    # 计算综合评分
    composite = (
        summary['success_rate'] * 100 * 0.4 +
        summary['avg_score'] * 0.3 +
        summary['efficiency'] * 10 * 0.2 +
        max(0, 100 - summary['avg_latency_ms'] / 1000) * 0.1
    )
    
    print(f"\n[综合评分] {composite:.2f}/100")
    
    # 目标达成检查
    targets_met = []
    if summary['avg_score'] >= 81:
        targets_met.append("Score>=81")
    if summary['avg_tokens'] < 12:
        targets_met.append("Token<12")
    if summary['efficiency'] > 6480:
        targets_met.append("Efficiency>6480")
    
    if all([summary['avg_score'] >= 81, summary['avg_tokens'] < 12, summary['efficiency'] > 6480]):
        verdict = "✅✅✅ 新冠军! 完美达成所有目标"
    elif summary['avg_score'] >= 81 and summary['efficiency'] > gen33_efficiency:
        verdict = "✅✅ 新冠军! Efficiency提升"
    elif summary['efficiency'] > gen33_efficiency:
        verdict = "✅ 新冠军! Efficiency提升"
    elif summary['avg_tokens'] < gen33_tokens:
        verdict = "✅ 新冠军! Token降低"
    else:
        verdict = "⚠️ 待优化 - 未能超越Gen33"
    
    print(f"[判定] {verdict}")
    if targets_met:
        print(f"[目标达成] {', '.join(targets_met)}")
    
    return {
        "timestamp": datetime.now().isoformat(),
        "generation": 34,
        "architecture": "Quantum Token Reduction",
        "summary": summary,
        "baseline": baseline,
        "gen33_baseline": {
            "avg_score": gen33_score,
            "avg_tokens": gen33_tokens,
            "efficiency": gen33_efficiency
        },
        "composite_score": composite,
        "verdict": verdict,
        "targets_met": targets_met,
        "individual_results": [asdict(r) for r in results]
    }

if __name__ == "__main__":
    result = run_evaluation()
    output_file = "/root/.openclaw/workspace/mas_repo/benchmark_results_gen34.json"
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"\n结果已保存至: {output_file}")