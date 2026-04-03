#!/usr/bin/env python3
"""
MAS Evaluator - Generation 43 Benchmark
Gen38精确复制 + query cost微调 (0.018)
"""

import sys
import json
from datetime import datetime

sys.path.insert(0, '/root/.openclaw/workspace/mas_repo')

from benchmark.tasks import BenchmarkSuite, get_baseline_single_agent
from mas.core_gen43 import create_mas_system
from dataclasses import asdict

def run_evaluation():
    print("=" * 60)
    print("MAS Evolution Engine - Gen43 Benchmark")
    print("Micro-Query Cost Optimization (on Gen38)")
    print("=" * 60)
    
    mas = create_mas_system()
    benchmark = BenchmarkSuite()
    baseline = get_baseline_single_agent()
    
    print(f"\n[基线] 单Agent系统:")
    print(f"  - 任务完成率: {baseline['success_rate']*100:.1f}%")
    print(f"  - 平均得分: {baseline['avg_score']:.1f}")
    
    print(f"\n[测试] 开始运行 {len(benchmark.tasks)} 个任务...")
    results, summary = benchmark.run_all(mas)
    
    print(f"\n[结果汇总]")
    print(f"  - 任务完成率: {summary['success_rate']*100:.1f}%")
    print(f"  - 平均得分: {summary['avg_score']:.1f}/100")
    print(f"  - Token开销: {summary['avg_tokens']:.1f}/task")
    print(f"  - 效率指数: {summary['efficiency']:.1f}")
    
    # 对比Gen38
    gen38_score = 81.0
    gen38_tokens = 5.1
    gen38_efficiency = 15882.0
    
    print(f"\n[对比Gen38]")
    score_diff = summary['avg_score'] - gen38_score
    token_diff = (summary['avg_tokens'] - gen38_tokens) / gen38_tokens * 100
    efficiency_diff = (summary['efficiency'] - gen38_efficiency) / gen38_efficiency * 100
    print(f"  - 得分差异: {score_diff:+.1f}")
    print(f"  - Token变化: {token_diff:+.1f}%")
    print(f"  - Efficiency变化: {efficiency_diff:+.1f}%")
    
    targets_met = []
    if summary['avg_score'] >= 81:
        targets_met.append("Score>=81")
    if summary['avg_tokens'] < 5:
        targets_met.append("Token<5")
    if summary['efficiency'] > 16000:
        targets_met.append("Efficiency>16000")
    
    if all([summary['avg_score'] >= 81, summary['avg_tokens'] < 5.1, summary['efficiency'] > 15882]):
        verdict = "✅✅✅ 新冠军! 完美超越Gen38"
    elif summary['efficiency'] > gen38_efficiency:
        verdict = "✅✅ 新冠军! Efficiency提升"
    elif summary['avg_tokens'] < gen38_tokens:
        verdict = "✅ 新冠军! Token降低"
    else:
        verdict = "⚠️ 待优化"
    
    print(f"\n[判定] {verdict}")
    
    return {
        "timestamp": datetime.now().isoformat(),
        "generation": 43,
        "architecture": "Micro-Query Cost Optimization",
        "summary": summary,
        "gen38_baseline": {
            "avg_score": gen38_score,
            "avg_tokens": gen38_tokens,
            "efficiency": gen38_efficiency
        },
        "verdict": verdict,
        "targets_met": targets_met,
        "individual_results": [asdict(r) for r in results]
    }

if __name__ == "__main__":
    result = run_evaluation()
    output_file = "/root/.openclaw/workspace/mas_repo/benchmark_results_gen43.json"
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"\n结果已保存至: {output_file}")