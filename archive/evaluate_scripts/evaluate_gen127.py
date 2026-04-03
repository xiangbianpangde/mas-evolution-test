#!/usr/bin/env python3
"""Gen127"""
import sys; sys.path.insert(0, '/root/.openclaw/workspace/mas_repo')
from benchmark.tasks import BenchmarkSuite
from mas.core_gen127 import create_mas_system
from dataclasses import asdict
import json
from datetime import datetime

mas = create_mas_system()
benchmark = BenchmarkSuite()
results, summary = benchmark.run_all(mas)

print(f"[Gen127] Score: {summary['avg_score']:.1f}, Token: {summary['avg_tokens']:.1f}, Eff: {summary['efficiency']:.0f}")
for r in results:
    print(f"  {r.task_id}: tokens={r.tokens}, score={r.score}")

gen125_tokens = 1.6
gen125_efficiency = 50625

token_diff = (summary['avg_tokens'] - gen125_tokens) / gen125_tokens * 100
efficiency_diff = (summary['efficiency'] - gen125_efficiency) / gen125_efficiency * 100
print(f"[对比Gen125] Token: {token_diff:+.1f}%, Eff: {efficiency_diff:+.1f}%")

composite = summary['success_rate'] * 100 * 0.4 + summary['avg_score'] * 0.3 + summary['efficiency'] / 100 * 0.2 + max(0, 100 - summary['avg_latency_ms'] / 1000) * 0.1
print(f"[综合评分] {composite:.2f}/100")

if summary['avg_score'] >= 81 and summary['avg_tokens'] < gen125_tokens:
    verdict = "✅✅✅ 新冠军!"
elif summary['avg_score'] >= 81:
    verdict = "✅ 得分达标"
else:
    verdict = "⚠️ 待优化"
print(f"[判定] {verdict}")

with open(f"/root/.openclaw/workspace/mas_repo/benchmark_results_gen127.json", 'w') as f:
    json.dump({"generation": 127, "summary": summary, "verdict": verdict, "individual_results": [asdict(r) for r in results]}, f)