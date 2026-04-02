#!/usr/bin/env python3
"""
MAS Evaluator - Gen199 Benchmark v2
Extended Output Coverage for Quantum Tasks
"""

import sys
import json
from datetime import datetime

sys.path.insert(0, '/root/.openclaw/workspace/mas_repo')

from benchmark.tasks_v2 import DynamicBenchmarkSuite, get_baseline_single_agent
from mas.core_gen199 import create_mas_system
from dataclasses import asdict

def run_evaluation():
    print("=" * 60)
    print("MAS Evolution Engine - Gen199 Benchmark")
    print("Extended Output Coverage for Quantum Tasks")
    print("=" * 60)
    
    mas = create_mas_system()
    benchmark = DynamicBenchmarkSuite(include_generalization=True)
    
    print(f"\n[测试] 运行 15 个任务...")
    results, summary = benchmark.run_all(mas)
    
    print(f"\n[核心任务结果]")
    print(f"  - 成功率: {summary['core_success_rate']*100:.1f}%")
    print(f"  - 得分: {summary['core_avg_score']:.1f}/100")
    print(f"  - Token: {summary['core_avg_tokens']:.1f}/task")
    
    print(f"\n[泛化任务结果]")
    print(f"  - 成功率: {summary['generalization_success_rate']*100:.1f}%")
    print(f"  - 得分: {summary['generalization_avg_score']:.1f}/100")
    print(f"  - Token: {summary['generalization_avg_tokens']:.1f}/task")
    
    print(f"\n[综合评分]")
    print(f"  - 综合评分: {summary['composite_score']:.2f}/100")
    print(f"  - Token: {summary['avg_tokens']:.1f}/task")
    print(f"  - 效率: {summary['efficiency']:.0f}")
    
    gen196_composite = 96.40
    gen196_gen = 88.0
    
    print(f"\n[对比Gen196]")
    print(f"  - Gen196 综合: {gen196_composite}, 泛化: {gen196_gen}")
    print(f"  - 当前 综合: {summary['composite_score']:.2f}, 泛化: {summary['generalization_avg_score']:.1f}")
    
    if summary['generalization_avg_score'] > gen196_gen and summary['composite_score'] >= gen196_composite:
        verdict = "✅✅✅ 新冠军! 泛化得分显著提升"
    elif summary['composite_score'] > gen196_composite:
        verdict = "✅✅ 新冠军! 综合评分提升"
    elif summary['generalization_avg_score'] > gen196_gen:
        verdict = "✅ 新冠军! 泛化提升"
    else:
        verdict = "⚠️ 待优化"
    
    print(f"[判定] {verdict}")
    
    output_file = "/root/.openclaw/workspace/mas_repo/benchmark_results_gen199.json"
    with open(output_file, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "generation": 199,
            "architecture": "Extended Output Coverage for Quantum Tasks",
            "summary": summary,
            "individual_results": [asdict(r) for r in results]
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n结果已保存至: {output_file}")
    return summary

if __name__ == "__main__":
    run_evaluation()