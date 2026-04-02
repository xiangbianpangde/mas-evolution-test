#!/usr/bin/env python3
"""
MAS Evaluator - Gen180 Benchmark v2
Higher Base Score for Better Generalization
"""

import sys
import json
from datetime import datetime

sys.path.insert(0, '/root/.openclaw/workspace/mas_repo')

from benchmark.tasks_v2 import DynamicBenchmarkSuite, get_baseline_single_agent
from mas.core_gen180 import create_mas_system
from dataclasses import asdict

def run_evaluation():
    print("=" * 60)
    print("MAS Evolution Engine - Gen180 Benchmark")
    print("Higher Base Score for Better Generalization")
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
    print(f"  - 综合评分(字典序): {summary['composite_score']:.2f}/100")
    print(f"  - Token: {summary['avg_tokens']:.2f}/task")
    print(f"  - 效率: {summary['efficiency']:.0f}")
    
    gen176_composite = 93.40
    gen176_gen = 78.0
    gen176_core = 81.0
    
    print(f"\n[对比Gen176]")
    print(f"  - Gen176 综合: {gen176_composite}, 泛化: {gen176_gen}, 核心: {gen176_core}")
    print(f"  - 当前 综合: {summary['composite_score']:.2f}, 泛化: {summary['generalization_avg_score']:.1f}, 核心: {summary['core_avg_score']:.1f}")
    
    if summary['generalization_avg_score'] > gen176_gen and summary['composite_score'] >= gen176_composite:
        verdict = "✅✅✅ 新冠军! 泛化性提升"
    elif summary['composite_score'] > gen176_composite:
        verdict = "✅✅ 新冠军! 综合评分提升"
    elif summary['generalization_avg_score'] > gen176_gen:
        verdict = "✅ 新冠军! 泛化提升"
    else:
        verdict = "⚠️ 待优化"
    
    print(f"[判定] {verdict}")
    
    output_file = "/root/.openclaw/workspace/mas_repo/benchmark_results_gen180.json"
    with open(output_file, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "generation": 180,
            "architecture": "Higher Base Score for Better Generalization",
            "summary": summary,
            "individual_results": [asdict(r) for r in results]
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n结果已保存至: {output_file}")

if __name__ == "__main__":
    run_evaluation()