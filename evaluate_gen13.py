#!/usr/bin/env python3
"""
MAS Evaluator - Generation 13 Benchmark
Ultra-Light Efficiency + Quality Floor
Goal: Token < 60, Score >= 75, Efficiency > 1296
"""

import sys
import json
from datetime import datetime

sys.path.insert(0, '/root/.openclaw/workspace/mas_repo')

from benchmark.tasks import BenchmarkSuite, get_baseline_single_agent
from mas.core_gen13 import create_mas_system
from dataclasses import asdict

def run_evaluation():
    print("=" * 60)
    print("MAS Evolution Engine - Gen13 Benchmark")
    print("Ultra-Light Efficiency + Quality Floor")
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
    print(f"\n[Gen13 统计]")
    print(f"  - 总任务数: {stats['total_tasks']}")
    print(f"  - 缓存命中: {stats['cache_hits']}")
    print(f"  - 直接执行: {stats['direct_exec']}")
    
    # 对比Gen10
    gen10_tokens = 57
    gen10_efficiency = 1296
    gen10_score = 74.0
    
    print(f"\n[对比Gen10 (当前最优)]")
    token_diff = (summary['avg_tokens'] - gen10_tokens) / gen10_tokens * 100
    eff_diff = (summary['efficiency'] - gen10_efficiency) / gen10_efficiency * 100
    score_diff = summary['avg_score'] - gen10_score
    print(f"  - Token变化: {token_diff:+.1f}%")
    print(f"  - 效率变化: {eff_diff:+.1f}%")
    print(f"  - 得分差异: {score_diff:+.1f}")
    
    # 综合评分
    latency_score = max(0, 100 - summary['avg_latency_ms'] / 1000)
    composite = (
        summary['success_rate'] * 100 * 0.4 +
        summary['avg_score'] * 0.3 +
        summary['efficiency'] * 1000 * 0.2 +
        latency_score * 0.1
    )
    
    print(f"\n[综合评分] {composite:.2f}/100")
    
    # 判定
    target_met = summary['avg_tokens'] < 60 and summary['avg_score'] >= 75 and summary['efficiency'] > 1296
    
    if composite > 259267 and target_met:
        verdict = "🏆🏆 完美! 达成所有目标并超越Gen10"
    elif composite > 259267:
        verdict = "🏆 新纪录! 超越Gen10"
    elif eff_diff > 5.0 and score_diff >= -1.0:
        verdict = "✅ 显著改进 - 效率大幅提升"
    elif target_met:
        verdict = "🎯 目标达成! Token<60, Score>=75, Eff>1296"
    elif score_diff > 3.0 and token_diff < 10.0:
        verdict = "⚡ 分数提升且保持效率"
    else:
        verdict = "❌ 未能超越Gen10"
    
    print(f"[判定] {verdict}")
    
    # 收敛检查
    if eff_diff < 1.0 and score_diff < 1.0:
        print(f"\n[收敛检查] 性能变化 < 1%")
        print(f"  Gen13 ≈ Gen10, 考虑触发收敛")
    
    return {
        "timestamp": datetime.now().isoformat(),
        "generation": 13,
        "architecture": "Ultra-Light Efficiency + Quality Floor",
        "summary": summary,
        "baseline": baseline,
        "gen10_baseline": {"avg_tokens": gen10_tokens, "efficiency": gen10_efficiency, "avg_score": gen10_score},
        "composite_score": composite,
        "verdict": verdict,
        "target_achieved": target_met,
        "stats": stats,
        "individual_results": [asdict(r) for r in results]
    }

if __name__ == "__main__":
    result = run_evaluation()
    output_file = "/root/.openclaw/workspace/mas_repo/benchmark_results_gen13.json"
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"\n结果已保存至: {output_file}")