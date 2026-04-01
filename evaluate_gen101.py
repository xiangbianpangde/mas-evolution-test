#!/usr/bin/env python3
import sys
import json
from datetime import datetime

sys.path.insert(0, '/root/.openclaw/workspace/mas_repo')

from benchmark.tasks import BenchmarkSuite, get_baseline_single_agent
from mas.core_gen101 import create_mas_system
from dataclasses import asdict

def run_evaluation():
    mas = create_mas_system()
    benchmark = BenchmarkSuite()
    
    print(f"[测试] 运行 {len(benchmark.tasks)} 个任务...")
    results, summary = benchmark.run_all(mas)
    
    print(f"[结果] Score: {summary['avg_score']:.1f}, Token: {summary['avg_tokens']:.1f}, Eff: {summary['efficiency']:.0f}")
    for r in results:
        print(f"  {r.task_id}: tokens={r.tokens}, score={r.score}")
    
    gen92_tokens, gen92_efficiency = 2.5, 32400.0
    token_diff = (summary['avg_tokens'] - gen92_tokens) / gen92_tokens * 100
    efficiency_diff = (summary['efficiency'] - gen92_efficiency) / gen92_efficiency * 100
    print(f"[对比Gen92] Token变化: {token_diff:+.1f}%, Efficiency变化: {efficiency_diff:+.1f}%")
    
    verdict = "✅✅✅ 新冠军!" if summary['avg_tokens'] < gen92_tokens and summary['avg_score'] >= 81 else "⚠️ 待优化"
    print(f"[判定] {verdict}")
    
    return {"generation": 101, "summary": summary, "verdict": verdict, "individual_results": [asdict(r) for r in results]}

if __name__ == "__main__":
    result = run_evaluation()
    with open('/root/.openclaw/workspace/mas_repo/benchmark_results_gen101.json', 'w') as f:
        json.dump(result, f, indent=2)
