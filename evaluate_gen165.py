#!/usr/bin/env python3
"""
MAS Evaluator - Gen165 Benchmark v2
Generalization-Focused Optimization
"""

import sys
import json
from datetime import datetime

sys.path.insert(0, '/root/.openclaw/workspace/mas_repo')

from benchmark.tasks_v2 import DynamicBenchmarkSuite, get_baseline_single_agent
from mas.core_gen165 import create_mas_system
from dataclasses import asdict

def run_evaluation():
    print("=" * 60)
    print("MAS Evolution Engine - Gen165 Benchmark")
    print("Generalization-Focused Optimization")
    print("=" * 60)
    
    mas = create_mas_system()
    benchmark = DynamicBenchmarkSuite(include_generalization=True)
    baseline = get_baseline_single_agent()
    
    print(f"\n[测试] 运行 15 个任务 (10核心 + 5泛化)...")
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
    print(f"  - Token: {summary['avg_tokens']:.1f}/task")
    print(f"  - 效率: {summary['efficiency']:.0f}")
    
    if summary['degradation_detected']:
        print(f"\n[警告] ⚠️ 检测到退化!")
    
    gen164_composite = 92.20
    gen164_gen_score = 74.0
    
    print(f"\n[对比Gen164]")
    print(f"  - Gen164 综合评分: {gen164_composite}")
    print(f"  - 当前综合评分: {summary['composite_score']:.2f}")
    print(f"  - Gen164 泛化得分: {gen164_gen_score}")
    print(f"  - 当前泛化得分: {summary['generalization_avg_score']:.1f}")
    
    if summary['composite_score'] > gen164_composite and summary['generalization_avg_score'] >= gen164_gen_score:
        verdict = "✅✅✅ 新冠军! 泛化性提升且综合评分增加"
    elif summary['generalization_avg_score'] > gen164_gen_score:
        verdict = "✅✅ 新冠军! 泛化性显著提升"
    elif summary['composite_score'] > gen164_composite:
        verdict = "✅ 新冠军! 综合评分提升"
    else:
        verdict = "⚠️ 待优化"
    
    print(f"[判定] {verdict}")
    
    output_file = f"/root/.openclaw/workspace/mas_repo/benchmark_results_gen165.json"
    with open(output_file, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "generation": 165,
            "architecture": "Generalization-Focused Optimization",
            "summary": summary,
            "baseline": baseline,
            "individual_results": [asdict(r) for r in results]
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n结果已保存至: {output_file}")
    return summary

if __name__ == "__main__":
    run_evaluation()