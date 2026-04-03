#!/usr/bin/env python3
"""Gen204 Benchmark Evaluator - Fixed missing keywords"""
import sys
sys.path.insert(0, '/root/.openclaw/workspace/mas_repo')
from benchmark.tasks_v2 import DynamicBenchmarkSuite
from mas.core_gen204 import create_mas_system
import json

def run():
    mas = create_mas_system()
    benchmark = DynamicBenchmarkSuite(include_generalization=True)
    results, summary = benchmark.run_all(mas)
    
    print(f"Gen204 Results:")
    print(f"  Core: {summary['core_avg_score']:.1f} ({summary['core_avg_tokens']:.1f} tok)")
    print(f"  Gen: {summary['generalization_avg_score']:.1f} ({summary['generalization_avg_tokens']:.1f} tok)")
    print(f"  Composite: {summary['composite_score']:.2f}")
    
    print(f"\n[Task breakdown]")
    for r in results:
        gen_tag = "[G]" if r.is_generalization else "[C]"
        print(f"  {gen_tag} {r.task_id}: score={r.score}, tokens={r.tokens}")
    
    gen196_composite = 96.40
    if summary['composite_score'] > gen196_composite:
        print(f"\n  ✅ NEW CHAMPION! (+{summary['composite_score']-gen196_composite:.2f})")
    
    return summary

if __name__ == "__main__":
    result = run()
    with open('/root/.openclaw/workspace/mas_repo/benchmark_results_gen204.json', 'w') as f:
        json.dump({"generation": 204, "summary": result}, f, indent=2, default=str)