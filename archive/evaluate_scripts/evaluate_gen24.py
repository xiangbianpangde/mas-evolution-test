#!/usr/bin/env python3
"""
MAS Evaluator - Generation 24 Benchmark
测试 Ultra-Precision Token Optimization
目标: Score>=81 AND Token<38 AND Efficiency>2100
"""

import sys
import json
import time
from datetime import datetime

sys.path.insert(0, '/root/.openclaw/workspace/mas_repo')

from benchmark.tasks import BenchmarkSuite, get_baseline_single_agent
from mas.core_gen24 import create_mas_system
from dataclasses import asdict

def run_evaluation():
    """运行完整评估"""
    print("=" * 60)
    print("MAS Evolution Engine - Gen24 Benchmark")
    print("Ultra-Precision Token Optimization")
    print("=" * 60)
    
    # 创建MAS系统 (Gen24)
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
    
    # 对比Gen23
    gen23_score = 81.0
    gen23_tokens = 39.7
    gen23_efficiency = 2040
    
    print(f"\n[对比Gen23 (当前冠军)]")
    print(f"  - Score: {summary['avg_score']:.1f} vs {gen23_score}")
    print(f"  - Token: {summary['avg_tokens']:.1f} vs {gen23_tokens}")
    print(f"  - Efficiency: {summary['efficiency']:.1f} vs {gen23_efficiency}")
    
    score_diff = summary['avg_score'] - gen23_score
    token_diff = gen23_tokens - summary['avg_tokens']
    eff_diff = summary['efficiency'] - gen23_efficiency
    
    print(f"\n[差异]")
    print(f"  - Score: {score_diff:+.1f}")
    print(f"  - Token节省: {token_diff:+.1f}")
    print(f"  - Efficiency变化: {eff_diff:+.1f}")
    
    # 目标检查
    print(f"\n[目标检查]")
    target_score = 81
    target_token = 38
    target_efficiency = 2100
    
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
        summary['efficiency'] * 50 * efficiency_weight +  # 调整权重
        latency_score * latency_weight
    )
    
    print(f"\n[综合评分] {composite:.2f}/100")
    
    if all_targets_met:
        verdict = "🏆🏆 新冠军! 完美达成所有目标"
    elif summary['avg_score'] >= target_score and summary['avg_tokens'] < target_token:
        verdict = "✅ 超越Gen23 - 效率提升"
    elif composite > 408134:
        verdict = "✅ 超越Gen23 - 综合评分提升"
    else:
        verdict = "⚠️ 未超越Gen23"
    
    print(f"[判定] {verdict}")
    
    return {
        "timestamp": datetime.now().isoformat(),
        "generation": 24,
        "architecture": "Ultra-Precision Token Optimization",
        "summary": summary,
        "baseline": baseline,
        "gen23_baseline": {
            "avg_score": gen23_score,
            "avg_tokens": gen23_tokens,
            "efficiency": gen23_efficiency
        },
        "composite_score": composite,
        "verdict": verdict,
        "targets_met": {
            "score": score_ok,
            "token": token_ok,
            "efficiency": eff_ok
        },
        "individual_results": [asdict(r) for r in results]
    }

if __name__ == "__main__":
    result = run_evaluation()
    
    # 保存结果
    output_file = "/root/.openclaw/workspace/mas_repo/benchmark_results_gen24.json"
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"\n结果已保存至: {output_file}")