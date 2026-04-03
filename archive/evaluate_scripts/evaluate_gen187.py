#!/usr/bin/env python3
"""Gen187 Benchmark"""
import sys
import json
from datetime import datetime
sys.path.insert(0, '/root/.openclaw/workspace/mas_repo')
from benchmark.tasks_v2 import DynamicBenchmarkSuite
from mas.core_gen187 import create_mas_system
from dataclasses import asdict

def run_evaluation():
    mas = create_mas_system()
    benchmark = DynamicBenchmarkSuite(include_generalization=True)
    results, summary = benchmark.run_all(mas)
    
    print(f"\n[核心] 成功率: {summary['core_success_rate']*100:.1f}% 得分: {summary['core_avg_score']:.1f} Token: {summary['core_avg_tokens']:.1f}")
    print(f"[泛化] 成功率: {summary['generalization_success_rate']*100:.1f}% 得分: {summary['generalization_avg_score']:.1f} Token: {summary['generalization_avg_tokens']:.1f}")
    print(f"[综合] {summary['composite_score']:.2f} Token: {summary['avg_tokens']:.1f}")
    
    gen185_composite = 95.20
    gen185_gen = 84.0
    
    if summary['composite_score'] > gen185_composite:
        print(f"[判定] ✅✅✅ 新冠军!")
    elif summary['generalization_avg_score'] > gen185_gen:
        print(f"[判定] ✅✅ 泛化提升")
    else:
        print(f"[判定] ⚠️ 待优化")
    
    with open('/root/.openclaw/workspace/mas_repo/benchmark_results_gen187.json', 'w') as f:
        json.dump({"generation": 187, "summary": summary, "results": [asdict(r) for r in results]}, f, indent=2)

if __name__ == "__main__":
    run_evaluation()