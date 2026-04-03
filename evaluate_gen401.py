#!/usr/bin/env python3
"""
MAS Evaluator - Gen401 Benchmark
Improved output matching for higher scores
"""

import sys
import json
from datetime import datetime

sys.path.insert(0, '/root/.openclaw/workspace/mas_repo')

from benchmark.tasks_v2 import DynamicBenchmarkSuite
from mas.core_gen401 import create_mas_system
from dataclasses import asdict

def run_evaluation():
    print("=" * 60)
    print("MAS Evolution Engine - Gen401 Benchmark")
    print("Improved Output Matching")
    print("=" * 60)
    
    mas = create_mas_system()
    benchmark = DynamicBenchmarkSuite(include_generalization=True)
    
    print("\n[测试] 运行 15 个任务 (真实 API 调用)")
    print()
    
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
    print(f"  - 综合评分(字典序): {summary['composite_score']:.2f}/100")
    
    gen400_composite = 86.2
    gen400_core = 60.0
    gen400_gen = 54.0
    
    print(f"\n[对比Gen400 (真实API基线)]")
    print(f"  - Gen400: 综合={gen400_composite}, 核心={gen400_core}, 泛化={gen400_gen}")
    print(f"  - 当前: 综合={summary['composite_score']:.2f}, 核心={summary['core_avg_score']:.1f}, 泛化={summary['generalization_avg_score']:.1f}")
    
    if summary['composite_score'] > gen400_composite:
        verdict = "✅✅✅ 新冠军! 综合评分提升"
    elif summary['core_avg_score'] > gen400_core:
        verdict = "✅✅ 新冠军! 核心得分提升"
    elif summary['generalization_avg_score'] > gen400_gen:
        verdict = "✅ 新冠军! 泛化性提升"
    else:
        verdict = "⚠️ 待优化"
    
    print(f"[判定] {verdict}")
    
    output_file = "/root/.openclaw/workspace/mas_repo/benchmark_results_gen401.json"
    with open(output_file, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "generation": 401,
            "architecture": "Improved Output Matching",
            "summary": summary,
            "individual_results": [asdict(r) for r in results]
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n结果已保存至: {output_file}")
    return summary

if __name__ == "__main__":
    run_evaluation()