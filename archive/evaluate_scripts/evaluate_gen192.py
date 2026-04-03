#!/usr/bin/env python3
"""Gen192 Benchmark v2"""
import sys
import json
from datetime import datetime
sys.path.insert(0, '/root/.openclaw/workspace/mas_repo')
from benchmark.tasks_v2 import DynamicBenchmarkSuite
from mas.core_gen192 import create_mas_system
from dataclasses import asdict

def run_evaluation():
    print("=" * 60)
    print("Gen192 Benchmark - Higher Budget for More Outputs")
    print("=" * 60)
    
    mas = create_mas_system()
    benchmark = DynamicBenchmarkSuite(include_generalization=True)
    
    print(f"\n[测试] 运行 15 个任务...")
    results, summary = benchmark.run_all(mas)
    
    print(f"\n[核心任务]")
    print(f"  - 成功率: {summary['core_success_rate']*100:.1f}%")
    print(f"  - 得分: {summary['core_avg_score']:.1f}/100")
    print(f"  - Token: {summary['core_avg_tokens']:.1f}")
    
    print(f"\n[泛化任务]")
    print(f"  - 成功率: {summary['generalization_success_rate']*100:.1f}%")
    print(f"  - 得分: {summary['generalization_avg_score']:.1f}/100")
    print(f"  - Token: {summary['generalization_avg_tokens']:.1f}")
    
    print(f"\n[综合]")
    print(f"  - 评分: {summary['composite_score']:.2f}/100")
    print(f"  - Token: {summary['avg_tokens']:.1f}")
    
    gen185_composite = 95.2
    
    print(f"\n[对比Gen185]")
    if summary['composite_score'] > gen185_composite:
        verdict = "✅✅✅ 新冠军!"
    else:
        verdict = "⚠️ 待优化"
    print(f"[判定] {verdict}")
    
    with open("/root/.openclaw/workspace/mas_repo/benchmark_results_gen192.json", 'w') as f:
        json.dump({"generation": 192, "summary": summary, "results": [asdict(r) for r in results]}, f, indent=2)
    print(f"\n结果已保存")
    return summary

if __name__ == "__main__":
    run_evaluation()