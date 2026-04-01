#!/usr/bin/env python3
"""
MAS Evaluator - Generation 46 Benchmark
Minimalist Collaboration + Token Floor
融合Gen38效率和Gen45协作概念
"""

import sys
import json
from datetime import datetime

sys.path.insert(0, '/root/.openclaw/workspace/mas_repo')

from benchmark.tasks import BenchmarkSuite, get_baseline_single_agent
from mas.core_gen46 import create_mas_system
from dataclasses import asdict

def run_evaluation():
    print("=" * 60)
    print("MAS Evolution Engine - Gen46 Benchmark")
    print("Minimalist Collaboration + Token Floor")
    print("=" * 60)
    
    mas = create_mas_system()
    benchmark = BenchmarkSuite()
    baseline = get_baseline_single_agent()
    
    print(f"\n[基线] 单Agent: {baseline['success_rate']*100:.0f}%完成, {baseline['avg_score']}分")
    print(f"[参考] Gen38冠军: Score 81, Token 5.1, Efficiency 15882")
    
    print(f"\n[测试] 运行 {len(benchmark.tasks)} 个任务...")
    results, summary = benchmark.run_all(mas)
    
    print(f"\n[结果]")
    print(f"  - 完成率: {summary['success_rate']*100:.0f}%")
    print(f"  - 平均得分: {summary['avg_score']:.1f}/100")
    print(f"  - Token开销: {summary['avg_tokens']:.1f}/task")
    print(f"  - 效率指数: {summary['efficiency']:.1f}")
    
    # 对比Gen38
    gen38_score, gen38_tokens, gen38_eff = 81.0, 5.1, 15882
    score_diff = summary['avg_score'] - gen38_score
    token_ratio = summary['avg_tokens'] / gen38_tokens if gen38_tokens > 0 else float('inf')
    eff_diff = (summary['efficiency'] - gen38_eff) / gen38_eff * 100
    
    print(f"\n[对比Gen38]")
    print(f"  - 得分差异: {score_diff:+.1f}")
    print(f"  - Token比例: {token_ratio:.1f}x")
    print(f"  - Efficiency变化: {eff_diff:+.1f}%")
    
    # 判定
    targets_met = []
    if summary['avg_score'] >= 81:
        targets_met.append("Score>=81")
    if summary['avg_tokens'] < 10:
        targets_met.append("Token<10")
    if summary['efficiency'] > 8000:
        targets_met.append("Eff>8000")
    
    if summary['avg_score'] >= 81 and summary['avg_tokens'] <= 6:
        verdict = "✅✅✅ 新冠军! 完美达成目标"
    elif summary['avg_score'] >= 81 and summary['efficiency'] > gen38_eff:
        verdict = "✅✅ 新冠军! Efficiency提升"
    elif score_diff >= 0 and token_ratio < 2:
        verdict = "✅ 新冠军候选! Score持平, Token可接受"
    elif score_diff >= -2:
        verdict = "⚠️ 待优化 - Score略低"
    else:
        verdict = "❌ 回归 - 未能超越Gen38"
    
    print(f"\n[判定] {verdict}")
    if targets_met:
        print(f"[目标达成] {', '.join(targets_met)}")
    
    return {
        "generation": 46,
        "architecture": "Minimalist Collaboration + Token Floor",
        "summary": summary,
        "gen38_reference": {"score": gen38_score, "tokens": gen38_tokens, "efficiency": gen38_eff},
        "verdict": verdict,
        "targets_met": targets_met,
        "individual_results": [asdict(r) for r in results]
    }

if __name__ == "__main__":
    result = run_evaluation()
    
    output_file = "/root/.openclaw/workspace/mas_repo/benchmark_results_gen46.json"
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"\n结果已保存至: {output_file}")