#!/usr/bin/env python3
"""
MAS Evaluator - Gen300 Benchmark v3.0
Multi-Agent Negotiation Architecture
"""
import sys
sys.path.insert(0, '/root/.openclaw/workspace/mas_repo')
from benchmark.tasks_v2 import DynamicBenchmarkSuite
from mas.core_gen300 import create_mas_system
import json

def run():
    print("=" * 60)
    print("MAS Evolution Engine - Gen300 Benchmark v3.0")
    print("Multi-Agent Negotiation Architecture")
    print("=" * 60)
    
    mas = create_mas_system()
    benchmark = DynamicBenchmarkSuite(include_generalization=True)
    results, summary = benchmark.run_all(mas)
    
    print(f"\n[核心任务结果]")
    print(f"  成功率: {summary['core_success_rate']*100:.1f}%")
    print(f"  得分: {summary['core_avg_score']:.1f}/100")
    print(f"  Token: {summary['core_avg_tokens']:.1f}/task")
    
    print(f"\n[泛化任务结果]")
    print(f"  成功率: {summary['generalization_success_rate']*100:.1f}%")
    print(f"  得分: {summary['generalization_avg_score']:.1f}/100")
    print(f"  Token: {summary['generalization_avg_tokens']:.1f}/task")
    
    print(f"\n[综合评分]")
    print(f"  综合评分: {summary['composite_score']:.2f}/100")
    print(f"  效率: {summary['efficiency']:.0f}")
    
    gen196_composite = 96.40
    print(f"\n[对比Gen196]")
    print(f"  Gen196: {gen196_composite}")
    print(f"  当前: {summary['composite_score']:.2f}")
    
    if summary['composite_score'] > gen196_composite:
        print(f"  ✅ 新冠军! (+{summary['composite_score']-gen196_composite:.2f})")
    else:
        print(f"  ⚠️ 待优化")
    
    return summary

if __name__ == "__main__":
    result = run()
    with open('/root/.openclaw/workspace/mas_repo/benchmark_results_gen300.json', 'w') as f:
        json.dump({"generation": 300, "summary": result}, f, indent=2, default=str)