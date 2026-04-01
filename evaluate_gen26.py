#!/usr/bin/env python3
"""
MAS Evaluator - Generation 26 Benchmark
测试 Task-Specific Output Weighting + Adaptive Quality Threshold
"""

import sys
import json
import time
from datetime import datetime

sys.path.insert(0, '/root/.openclaw/workspace/mas_repo')

from benchmark.tasks import BenchmarkSuite, get_baseline_single_agent
from mas.core_gen26 import create_mas_system
from dataclasses import asdict

def run_evaluation():
    """运行完整评估"""
    print("=" * 60)
    print("MAS Evolution Engine - Gen26 Benchmark")
    print("Task-Specific Output Weighting + Adaptive Quality Threshold")
    print("=" * 60)
    
    # 创建MAS系统 (Gen26)
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
    print(f"  - Token开销: {summary['avg_tokens']:.1f}/task")
    print(f"  - 平均延迟: {summary['avg_latency_ms']:.1f}ms")
    print(f"  - 效率指数: {summary['efficiency']:.1f}")
    
    # Gen26 特有信息
    print(f"\n[Gen26 架构]")
    print(f"  - 版本: {mas.version}")
    
    # 改进对比
    print(f"\n[对比基线]")
    score_improvement = (summary['avg_score'] - baseline['avg_score']) / baseline['avg_score'] * 100
    token_change = (summary['avg_tokens'] - baseline['avg_tokens']) / baseline['avg_tokens'] * 100
    print(f"  - 得分提升: {score_improvement:+.1f}%")
    print(f"  - Token变化: {token_change:+.1f}%")
    
    # 对比Gen25
    gen25_score = 81.0
    gen25_tokens = 35.6
    gen25_efficiency = 2275
    
    print(f"\n[对比Gen25 (当前冠军)]")
    gen25_score_diff = summary['avg_score'] - gen25_score
    gen25_token_diff = summary['avg_tokens'] - gen25_tokens
    gen25_eff_diff = summary['efficiency'] - gen25_efficiency
    print(f"  - 得分差异: {gen25_score_diff:+.1f}")
    print(f"  - Token差异: {gen25_token_diff:+.1f}")
    print(f"  - Efficiency差异: {gen25_eff_diff:+.1f}")
    
    # 目标检查
    target_score = 81
    target_token = 36
    target_efficiency = 2300
    
    print(f"\n[目标检查]")
    score_ok = summary['avg_score'] >= target_score
    token_ok = summary['avg_tokens'] < target_token
    eff_ok = summary['efficiency'] > target_efficiency
    print(f"  - Score >= {target_score}: {'✅' if score_ok else '❌'} ({summary['avg_score']:.1f})")
    print(f"  - Token < {target_token}: {'✅' if token_ok else '❌'} ({summary['avg_tokens']:.1f})")
    print(f"  - Efficiency > {target_efficiency}: {'✅' if eff_ok else '❌'} ({summary['efficiency']:.1f})")
    
    all_targets_met = score_ok and token_ok and eff_ok
    
    # 计算综合评分
    completion_weight = 0.4
    score_weight = 0.3
    efficiency_weight = 0.2
    latency_weight = 0.1
    
    latency_score = max(0, 100 - summary['avg_latency_ms'] / 1000)
    
    composite = (
        summary['success_rate'] * 100 * completion_weight +
        summary['avg_score'] * score_weight +
        summary['efficiency'] * efficiency_weight +
        latency_score * latency_weight
    )
    
    print(f"\n[综合评分] {composite:.2f}")
    
    if all_targets_met:
        verdict = "🏆🏆 新冠军! 完美达成所有目标"
    elif summary['avg_score'] >= gen25_score and summary['avg_tokens'] < gen25_tokens:
        verdict = "✅ 改进 - Token优化"
    elif summary['avg_score'] > gen25_score:
        verdict = "✅ 改进 - Score提升"
    elif composite > 1000:
        verdict = "✅ 通过 - 优于基线"
    else:
        verdict = "❌ 未超越冠军"
    
    print(f"[判定] {verdict}")
    
    return {
        "timestamp": datetime.now().isoformat(),
        "generation": 26,
        "architecture": "Task-Specific Output Weighting + Adaptive Quality Threshold",
        "summary": summary,
        "baseline": baseline,
        "gen25_baseline": {
            "avg_score": gen25_score,
            "avg_tokens": gen25_tokens,
            "efficiency": gen25_efficiency
        },
        "composite_score": composite,
        "verdict": verdict,
        "targets_met": {
            "score": score_ok,
            "token": token_ok,
            "efficiency": eff_ok,
            "all": all_targets_met
        },
        "individual_results": [asdict(r) for r in results]
    }

if __name__ == "__main__":
    result = run_evaluation()
    
    # 保存结果
    output_file = "/root/.openclaw/workspace/mas_repo/benchmark_results_gen26.json"
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"\n结果已保存至: {output_file}")