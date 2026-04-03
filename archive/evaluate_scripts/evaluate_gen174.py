#!/usr/bin/env python3
"""Gen174 Benchmark"""
import sys
sys.path.insert(0, '/root/.openclaw/workspace/mas_repo')
from benchmark.tasks_v2 import DynamicBenchmarkSuite
from mas.core_gen174 import create_mas_system
from dataclasses import asdict
import json
from datetime import datetime

mas = create_mas_system()
benchmark = DynamicBenchmarkSuite(include_generalization=True)
results, summary = benchmark.run_all(mas)

print(f"[Gen174 Results]")
print(f"  核心: {summary['core_avg_score']:.1f}/81, Token: {summary['core_avg_tokens']:.1f}")
print(f"  泛化: {summary['generalization_avg_score']:.1f}, Token: {summary['generalization_avg_tokens']:.1f}")
print(f"  综合: {summary['composite_score']:.2f}")

gen171_composite = 92.80
if summary['composite_score'] > gen171_composite:
    print(f"  判定: ✅ 新冠军!")
else:
    print(f"  判定: ⚠️ 待优化")

with open(f'/root/.openclaw/workspace/mas_repo/benchmark_results_gen174.json', 'w') as f:
    json.dump({"generation": 174, "summary": summary, "results": [asdict(r) for r in results]}, f)