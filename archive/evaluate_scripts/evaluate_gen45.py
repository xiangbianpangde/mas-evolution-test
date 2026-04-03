#!/usr/bin/env python3
"""
MAS Evaluator - Generation 45 Benchmark
测试 Swarm Orchestration Architecture
新范式探索: 从Token优化转向动态协作拓扑
"""

import sys
import json
from datetime import datetime

sys.path.insert(0, '/root/.openclaw/workspace/mas_repo')

from benchmark.tasks import BenchmarkSuite, get_baseline_single_agent
from mas.core_gen45 import create_mas_system
from dataclasses import asdict

def run_evaluation():
    print("=" * 60)
    print("MAS Evolution Engine - Gen45 Benchmark")
    print("Swarm Orchestration Architecture")
    print("范式转变: 动态协作拓扑 vs Token优化")
    print("=" * 60)
    
    mas = create_mas_system()
    benchmark = BenchmarkSuite()
    baseline = get_baseline_single_agent()
    
    print(f"\n[基线] 单Agent系统:")
    print(f"  - 任务完成率: {baseline['success_rate']*100:.1f}%")
    print(f"  - 平均得分: {baseline['avg_score']:.1f}")
    print(f"  - Token效率: {baseline['avg_tokens']:.0f}/task")
    
    print(f"\n[参考] Gen38冠军 (Token优化极限):")
    print(f"  - 任务完成率: 100%")
    print(f"  - 平均得分: 81.0")
    print(f"  - Token开销: 5.1/task")
    print(f"  - 效率指数: 15882")
    
    print(f"\n[测试] 开始运行 {len(benchmark.tasks)} 个任务...")
    results, summary = benchmark.run_all(mas)
    
    print(f"\n[结果汇总]")
    print(f"  - 任务完成率: {summary['success_rate']*100:.1f}%")
    print(f"  - 平均得分: {summary['avg_score']:.1f}/100")
    print(f"  - Token开销: {summary['avg_tokens']:.0f}/task")
    print(f"  - 平均延迟: {summary['avg_latency_ms']:.0f}ms")
    print(f"  - 效率指数: {summary['efficiency']:.4f}")
    
    stats = mas.get_stats()
    print(f"\n[Gen45 统计]")
    print(f"  - 版本: {stats['version']}")
    print(f"  - 总执行次数: {stats['total_executions']}")
    
    # 对比Gen38
    gen38_score = 81.0
    gen38_tokens = 5.1
    gen38_efficiency = 15882
    
    print(f"\n[对比Gen38 (Token优化冠军)]")
    score_diff = summary['avg_score'] - gen38_score
    token_ratio = summary['avg_tokens'] / gen38_tokens if gen38_tokens > 0 else float('inf')
    efficiency_diff = (summary['efficiency'] - gen38_efficiency) / gen38_efficiency * 100
    
    print(f"  - 得分差异: {score_diff:+.1f}")
    print(f"  - Token比例: {token_ratio:.1f}x")
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
    
    # 新范式评估
    if summary['avg_score'] > gen38_score:
        verdict = "✅✅✅ 新冠军! Score突破"
        new_paradigm_success = True
    elif summary['avg_score'] == gen38_score and summary['efficiency'] > gen38_efficiency:
        verdict = "✅✅ 新冠军! Efficiency提升"
        new_paradigm_success = True
    elif summary['avg_score'] == gen38_score and summary['tokens'] <= gen38_tokens * 1.5:
        verdict = "✅ 新范式可行! Token可接受"
        new_paradigm_success = True
    elif score_diff >= -3 and efficiency_diff > -30:
        verdict = "⚠️ 新范式探索 - Score略低但可接受"
        new_paradigm_success = True
    else:
        verdict = "❌ 新范式回归 - 需要继续优化"
        new_paradigm_success = False
    
    print(f"[判定] {verdict}")
    
    return {
        "timestamp": datetime.now().isoformat(),
        "generation": 45,
        "architecture": "Swarm Orchestration",
        "paradigm": "Dynamic Collaboration vs Token Optimization",
        "summary": summary,
        "baseline": baseline,
        "gen38_reference": {
            "avg_score": gen38_score,
            "avg_tokens": gen38_tokens,
            "efficiency": gen38_efficiency
        },
        "composite_score": composite,
        "verdict": verdict,
        "new_paradigm_success": new_paradigm_success,
        "individual_results": [asdict(r) for r in results]
    }

if __name__ == "__main__":
    result = run_evaluation()
    
    output_file = "/root/.openclaw/workspace/mas_repo/benchmark_results_gen45.json"
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"\n结果已保存至: {output_file}")