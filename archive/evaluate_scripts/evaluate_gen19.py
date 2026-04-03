#!/usr/bin/env python3
"""
MAS Evaluator - Generation 19 Benchmark
测试 Hierarchical Team-of-Agents with Predictive Routing
"""

import sys
import json
import time
from datetime import datetime

sys.path.insert(0, '/root/.openclaw/workspace/mas_repo')

from benchmark.tasks import BenchmarkSuite, get_baseline_single_agent
from mas.core_gen19 import create_mas_system
from dataclasses import asdict

def run_evaluation():
    """运行完整评估"""
    print("=" * 60)
    print("MAS Evolution Engine - Gen19 Benchmark")
    print("Hierarchical Team-of-Agents with Predictive Routing")
    print("=" * 60)
    
    # 创建MAS系统 (Gen19)
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
    
    results = []
    for task in benchmark.tasks:
        result = benchmark.run_single(mas, task)
        results.append(result)
    
    summary = benchmark._compute_summary(results)
    
    # 打印结果
    print(f"\n[结果汇总]")
    print(f"  - 任务完成率: {summary['success_rate']*100:.1f}%")
    print(f"  - 平均得分: {summary['avg_score']:.1f}/100")
    print(f"  - Token开销: {summary['avg_tokens']:.0f}/task")
    print(f"  - 平均延迟: {summary['avg_latency_ms']:.0f}ms")
    print(f"  - 效率指数: {summary['efficiency']:.4f}")
    
    # Gen19 特有统计
    stats = mas.get_stats()
    print(f"\n[Gen19 统计]")
    print(f"  - 总任务数: {stats['total_tasks']}")
    print(f"  - 多团队任务: {stats['multi_team_tasks']}")
    print(f"  - 单团队任务: {stats['single_team_tasks']}")
    print(f"  - 团队使用统计: {stats['team_usage']}")
    
    # 对比Gen18
    gen18_score = 81
    gen18_tokens = 41
    gen18_efficiency = 1961
    
    print(f"\n[对比Gen18 (v1.0)]")
    score_diff = summary['avg_score'] - gen18_score
    token_diff = (summary['avg_tokens'] - gen18_tokens) / gen18_tokens * 100
    efficiency_diff = (summary['efficiency'] - gen18_efficiency) / gen18_efficiency * 100
    print(f"  - 得分差异: {score_diff:+.1f}")
    print(f"  - Token变化: {token_diff:+.1f}%")
    print(f"  - 效率变化: {efficiency_diff:+.1f}%")
    
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
    
    # 判定
    if summary['avg_score'] >= 80 and summary['avg_tokens'] < 45 and summary['efficiency'] > 1961:
        verdict = "🏆 完美! 超越Gen18"
    elif summary['avg_score'] >= 80 and summary['avg_tokens'] < 45:
        verdict = "✅ 达标 - Score>=80, Token<45"
    elif summary['avg_score'] >= 80:
        verdict = "✅ 分数达标 - Score>=80"
    elif composite > 300000:
        verdict = "✅ 优秀 - 大幅超越基线"
    elif composite > 200000:
        verdict = "⚠️ 良好 - 超越基线"
    else:
        verdict = "❌ 不合格 - 低于预期"
    
    print(f"[判定] {verdict}")
    
    return {
        "timestamp": datetime.now().isoformat(),
        "generation": 19,
        "architecture": "Hierarchical Team-of-Agents + Predictive Routing",
        "summary": summary,
        "baseline": baseline,
        "gen18_baseline": {
            "avg_score": gen18_score,
            "avg_tokens": gen18_tokens,
            "efficiency": gen18_efficiency
        },
        "composite_score": composite,
        "verdict": verdict,
        "stats": stats,
        "individual_results": [asdict(r) for r in results]
    }

if __name__ == "__main__":
    result = run_evaluation()
    
    # 保存结果
    output_file = "/root/.openclaw/workspace/mas_repo/benchmark_results_gen19.json"
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"\n结果已保存至: {output_file}")