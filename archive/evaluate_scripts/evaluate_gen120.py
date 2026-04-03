#!/usr/bin/env python3
"""MAS Evaluator - Gen120"""

import sys
import json
from datetime import datetime

sys.path.insert(0, '/root/.openclaw/workspace/mas_repo')

from benchmark.tasks import BenchmarkSuite
from mas.core_gen120 import create_mas_system
from dataclasses import asdict

mas = create_mas_system()
benchmark = BenchmarkSuite()
results, summary = benchmark.run_all(mas)

print(f"[结果] Score: {summary['avg_score']:.1f}, Token: {summary['avg_tokens']:.1f}, Eff: {summary['efficiency']:.0f}")
for r in results:
    print(f"  {r.task_id}: tokens={r.tokens}, score={r.score}")

gen108_tokens = 1.9
gen108_efficiency = 42632.0

token_diff = (summary['avg_tokens'] - gen108_tokens) / gen108_tokens * 100
efficiency_diff = (summary['efficiency'] - gen108_efficiency) / gen108_efficiency * 100
print(f"[对比Gen108] Token: {token_diff:+.1f}%, Eff: {efficiency_diff:+.1f}%")

if summary['avg_score'] >= 81 and summary['avg_tokens'] < gen108_tokens:
    verdict = "✅✅✅ 新冠军!"
elif summary['avg_score'] >= 81:
    verdict = "✅ 匹配Gen108"
else:
    verdict = "⚠️ 待优化"

print(f"[判定] {verdict}")

with open(f"/root/.openclaw/workspace/mas_repo/benchmark_results_gen120.json", 'w') as f:
    json.dump({"generation": 120, "summary": summary, "verdict": verdict, "results": [asdict(r) for r in results]}, f)