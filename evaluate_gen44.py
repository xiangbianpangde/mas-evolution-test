#!/usr/bin/env python3
"""MAS Evaluator - Generation 44 Benchmark"""

import sys
import json
from datetime import datetime

sys.path.insert(0, '/root/.openclaw/workspace/mas_repo')

from benchmark.tasks import BenchmarkSuite, get_baseline_single_agent
from mas.core_gen44 import create_mas_system
from dataclasses import asdict

def run_evaluation():
    print("=" * 60)
    print("MAS Evolution Engine - Gen44 Benchmark")
    print("Gen38精确复制 + query cost 0.01")
    print("=" * 60)
    
    mas = create_mas_system()
    benchmark = BenchmarkSuite()
    baseline = get_baseline_single_agent()
    
    print(f"\n[基线] 单Agent: {baseline['success_rate']*100:.0f}%完成, {baseline['avg_score']:.1f}分")
    
    print(f"\n[测试] 运行 {len(benchmark.tasks)} 个任务...")
    results, summary = benchmark.run_all(mas)
    
    print(f"\n[结果]")
    print(f"  - 完成率: {summary['success_rate']*100:.0f}%")
    print(f"  - 平均得分: {summary['avg_score']:.1f}/100")
    print(f"  - Token开销: {summary['avg_tokens']:.1f}/task")
    print(f"  - 效率指数: {summary['efficiency']:.1f}")
    
    gen38_tokens = 5.1
    gen38_efficiency = 15882.0
    
    print(f"\n[对比Gen38]")
    token_diff = (summary['avg_tokens'] - gen38_tokens) / gen38_tokens * 100
    efficiency_diff = (summary['efficiency'] - gen38_efficiency) / gen38_efficiency * 100
    print(f"  - Token变化: {token_diff:+.1f}%")
    print(f"  - Efficiency变化: {efficiency_diff:+.1f}%")
    
    if summary['efficiency'] > gen38_efficiency:
        verdict = "✅✅ 新冠军! Efficiency提升"
    elif summary['avg_tokens'] < gen38_tokens:
        verdict = "✅ 新冠军! Token降低"
    else:
        verdict = "⚠️ 待优化"
    
    print(f"\n[判定] {verdict}")
    
    return {
        "timestamp": datetime.now().isoformat(),
        "generation": 44,
        "summary": summary,
        "verdict": verdict,
        "individual_results": [asdict(r) for r in results]
    }

if __name__ == "__main__":
    result = run_evaluation()
    with open("/root/.openclaw/workspace/mas_repo/benchmark_results_gen44.json", 'w') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print("\n结果已保存.")