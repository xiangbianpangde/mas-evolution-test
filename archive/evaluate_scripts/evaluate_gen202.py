#!/usr/bin/env python3
"""Gen202 Benchmark Evaluator"""
import sys
sys.path.insert(0, '/root/.openclaw/workspace/mas_repo')
from benchmark.tasks_v2 import DynamicBenchmarkSuite
from mas.core_gen202 import create_mas_system
from dataclasses import asdict
import json

def run():
    mas = create_mas_system()
    benchmark = DynamicBenchmarkSuite(include_generalization=True)
    results, summary = benchmark.run_all(mas)
    
    print(f"Gen202 Results:")
    print(f"  Core: {summary['core_avg_score']:.1f} ({summary['core_avg_tokens']:.1f} tok)")
    print(f"  Gen: {summary['generalization_avg_score']:.1f} ({summary['generalization_avg_tokens']:.1f} tok)")
    print(f"  Composite: {summary['composite_score']:.2f}")
    
    gen196_composite = 96.40
    if summary['composite_score'] > gen196_composite:
        print(f"  ✅ NEW CHAMPION! (+{summary['composite_score']-gen196_composite:.2f})")
    
    return summary

if __name__ == "__main__":
    result = run()
    with open('/root/.openclaw/workspace/mas_repo/benchmark_results_gen202.json', 'w') as f:
        json.dump({"generation": 202, "summary": result}, f, indent=2, default=str)