#!/usr/bin/env python3
"""Gen179 Benchmark - Higher score base"""
import sys
sys.path.insert(0, '/root/.openclaw/workspace/mas_repo')
from benchmark.tasks_v2 import DynamicBenchmarkSuite
from mas.core_gen179 import create_mas_system
from dataclasses import asdict
import json

mas = create_mas_system()
benchmark = DynamicBenchmarkSuite(include_generalization=True)
results, summary = benchmark.run_all(mas)

print(f"[Gen179 Results]")
print(f"  核心: {summary['core_avg_score']:.1f}, Token: {summary['core_avg_tokens']:.1f}")
print(f"  泛化: {summary['generalization_avg_score']:.1f}, Token: {summary['generalization_avg_tokens']:.1f}")
print(f"  综合: {summary['composite_score']:.2f}")

for r in results:
    if r.is_generalization:
        print(f"  [泛化] {r.task_id}: tokens={r.tokens}, score={r.score}")

gen176_composite = 93.40
if summary['composite_score'] > gen176_composite and summary['generalization_avg_score'] >= 78.0:
    print(f"  判定: ✅✅✅ 新冠军!")
elif summary['generalization_avg_score'] > 78.0:
    print(f"  判定: ✅✅ 泛化提升")
elif summary['composite_score'] > gen176_composite:
    print(f"  判定: ✅ 综合提升")
else:
    print(f"  判定: ⚠️ 待优化")

with open(f'/root/.openclaw/workspace/mas_repo/benchmark_results_gen179.json', 'w') as f:
    json.dump({"generation": 179, "summary": summary, "results": [asdict(r) for r in results]}, f, indent=2)