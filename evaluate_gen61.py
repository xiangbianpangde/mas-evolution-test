#!/usr/bin/env python3
"""
MAS Evaluator - Generation 61 Benchmark
PARADIGM SHIFT: Computational Complexity-Aware Architecture

⚠️ CONVERGENCE BROKEN - NEW PARADIGM EXPLORATION ⚠️

New metrics focus:
- Token + Latency cost modeling
- Quality per computational unit
- Realistic resource allocation
"""

import sys
import json
import time
from datetime import datetime

sys.path.insert(0, '/root/.openclaw/workspace/mas_repo')

from benchmark.tasks import BenchmarkSuite, get_baseline_single_agent
from mas.core_gen61 import create_mas_system, QualityCalculator
from dataclasses import asdict

def run_evaluation():
    """运行完整评估"""
    print("=" * 60)
    print("MAS Evolution Engine - Gen61 Benchmark")
    print("⚠️ PARADIGM SHIFT: Computational Complexity-Aware")
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
    
    # Calculate cost efficiency for each task
    cost_efficiencies = []
    for r in results:
        ce = QualityCalculator.calculate_cost_efficiency(r.score, r.tokens, r.latency_ms)
        cost_efficiencies.append(ce)
    
    avg_cost_efficiency = sum(cost_efficiencies) / len(cost_efficiencies) if cost_efficiencies else 0
    
    print(f"\n[结果汇总]")
    print(f"  - 任务完成率: {summary['success_rate']*100:.1f}%")
    print(f"  - 平均得分: {summary['avg_score']:.1f}/100")
    print(f"  - Token开销: {summary['avg_tokens']:.0f}/task")
    print(f"  - 平均延迟: {summary['avg_latency_ms']:.1f}ms")
    print(f"  - 效率指数: {summary['efficiency']:.2f}")
    print(f"  - ⚡ 成本效率: {avg_cost_efficiency:.2f}")
    
    # Compare with Gen38 (previous champion)
    gen38_score = 81.0
    gen38_tokens = 5.1
    gen38_efficiency = 15882
    gen38_cost_efficiency = None  # Not calculated before
    
    print(f"\n[对比Gen38 (旧冠军)]")
    score_diff = summary['avg_score'] - gen38_score
    token_diff = (summary['avg_tokens'] - gen38_tokens) / gen38_tokens * 100
    print(f"  - 得分差异: {score_diff:+.1f}")
    print(f"  - Token变化: {token_diff:+.1f}%")
    print(f"  - 注意: 新架构使用不同优化目标")
    
    # Composite score with new metric
    completion_weight = 0.35
    score_weight = 0.30
    efficiency_weight = 0.25
    cost_efficiency_weight = 0.10
    latency_weight = 0.0  # Already in cost_efficiency
    
    latency_score = max(0, 100 - summary['avg_latency_ms'] / 1000)
    
    composite = (
        summary['success_rate'] * 100 * completion_weight +
        summary['avg_score'] * score_weight +
        summary['efficiency'] * 0.1 * efficiency_weight +
        avg_cost_efficiency * 100 * cost_efficiency_weight
    )
    
    print(f"\n[综合评分] {composite:.2f}/100")
    
    # Check if this new paradigm achieved its goals
    new_paradigm_targets = []
    if summary['avg_score'] >= 81:
        new_paradigm_targets.append("Score>=81")
    if summary['avg_latency_ms'] < 50:
        new_paradigm_targets.append("Latency<50ms")
    if avg_cost_efficiency > 50:
        new_paradigm_targets.append("CostEfficiency>50")
    
    print(f"[新范式目标] {', '.join(new_paradigm_targets) if new_paradigm_targets else 'None met'}")
    
    if summary['avg_score'] >= 81 and avg_cost_efficiency > 50:
        verdict = "✅ 新范式成功! Quality + Cost Efficiency 平衡"
    elif summary['avg_score'] >= 81:
        verdict = "✅ 新范式: Score保持, Cost Efficiency待优化"
    else:
        verdict = "⚠️ 新范式: Score下降, 需要调整"
    
    print(f"[判定] {verdict}")
    
    return {
        "timestamp": datetime.now().isoformat(),
        "generation": 61,
        "paradigm": "Computational Complexity-Aware",
        "paradigm_shift": True,
        "summary": summary,
        "baseline": baseline,
        "cost_efficiency": {
            "avg": avg_cost_efficiency,
            "per_task": cost_efficiencies
        },
        "gen38_baseline": {
            "avg_score": gen38_score,
            "avg_tokens": gen38_tokens,
            "efficiency": gen38_efficiency
        },
        "composite_score": composite,
        "verdict": verdict,
        "targets_met": new_paradigm_targets,
        "individual_results": [asdict(r) for r in results]
    }

if __name__ == "__main__":
    result = run_evaluation()
    
    output_file = "/root/.openclaw/workspace/mas_repo/benchmark_results_gen61.json"
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"\n结果已保存至: {output_file}")