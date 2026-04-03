#!/usr/bin/env python3
"""
MAS Evaluator - Generation 10 Benchmark
Adaptive Token Budget + Performance-Based Scoring
"""

import sys
import json
from datetime import datetime

sys.path.insert(0, '/root/.openclaw/workspace/mas_repo')

from benchmark.tasks import BenchmarkSuite, get_baseline_single_agent
from mas.core_gen10 import create_mas_system
from dataclasses import asdict

def run_evaluation():
    print("=" * 60)
    print("MAS Evolution Engine - Gen10 Benchmark")
    print("Adaptive Token Budget + Performance-Based Scoring")
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
    print(f"\n[Gen10 统计]")
    print(f"  - 总任务数: {stats['total_tasks']}")
    print(f"  - 缓存命中: {stats['cache_hits']}")
    print(f"  - 直接执行: {stats['direct_exec']}")
    
    # 对比Gen7
    gen7_tokens = 101
    gen7_efficiency = 783.7
    gen7_score = 79.0
    
    print(f"\n[对比Gen7 (当前最优)]")
    token_diff = (summary['avg_tokens'] - gen7_tokens) / gen7_tokens * 100
    eff_diff = (summary['efficiency'] - gen7_efficiency) / gen7_efficiency * 100
    score_diff = summary['avg_score'] - gen7_score
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
    
    # 收敛检查
    if eff_diff > 1.0:
        verdict = "🏆 新纪录! 显著超越Gen7"
    elif eff_diff > 0:
        verdict = "✅ 小幅改进"
    elif token_diff < -1.0:
        verdict = "✅ Token优化显著"
    elif eff_diff >= -1.0:
        verdict = "⚡ 匹配Gen7 (收敛边缘)"
    else:
        verdict = "❌ 回归"
    
    print(f"[判定] {verdict}")
    
    # 收敛判定
    is_converged = abs(token_diff) < 1.0 and abs(eff_diff) < 1.0
    if is_converged:
        print(f"\n[收敛警告] Gen10 ≈ Gen7")
        print(f"  连续改进 < 1%，接近收敛阈值")
        print(f"  如Gen11仍无显著改进，应触发范式转换")
    
    return {
        "timestamp": datetime.now().isoformat(),
        "generation": 10,
        "architecture": "Adaptive Token Budget + Performance-Based Scoring",
        "summary": summary,
        "baseline": baseline,
        "gen7_baseline": {"avg_tokens": gen7_tokens, "efficiency": gen7_efficiency, "avg_score": gen7_score},
        "composite_score": composite,
        "verdict": verdict,
        "converged": is_converged,
        "stats": stats,
        "individual_results": [asdict(r) for r in results]
    }

if __name__ == "__main__":
    result = run_evaluation()
    output_file = "/root/.openclaw/workspace/mas_repo/benchmark_results_gen10.json"
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"\n结果已保存至: {output_file}")