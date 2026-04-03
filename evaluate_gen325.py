#!/usr/bin/env python3
import sys
sys.path.insert(0, '/root/.openclaw/workspace/mas_repo')
from benchmark.tasks_v2 import DynamicBenchmarkSuite
from mas.core_gen325 import create_mas_system
from dataclasses import asdict
import json
from datetime import datetime

mas = create_mas_system()
benchmark = DynamicBenchmarkSuite(include_generalization=True)
results, summary = benchmark.run_all(mas)

print(f"[Gen325 Results]")
print(f"  Core: {summary['core_avg_score']:.1f} @ {summary['core_avg_tokens']:.1f} tokens")
print(f"  Gen: {summary['generalization_avg_score']:.1f} @ {summary['generalization_avg_tokens']:.1f} tokens")
print(f"  Composite: {summary['composite_score']:.2f}")

with open('/root/.openclaw/workspace/mas_repo/benchmark_results_gen325.json', 'w') as f:
    json.dump({"generation": 325, "summary": summary, "results": [asdict(r) for r in results]}, f)
