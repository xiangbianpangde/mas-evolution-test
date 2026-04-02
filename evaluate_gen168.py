#!/usr/bin/env python3
"""
MAS Evaluator - Gen168 Benchmark v2
Extended Output Selection
"""

import sys
import json
from datetime import datetime

sys.path.insert(0, '/root/.openclaw/workspace/mas_repo')

from benchmark.tasks_v2 import DynamicBenchmarkSuite
from mas.core_gen168 import create_mas_system
from dataclasses import asdict

def run_evaluation():
    print("=" * 60)
    print("MAS Evolution Engine - Gen168 Benchmark")
    print("Extended Output Selection")
    print("=" * 60)
    
    mas = create_mas_system()
    benchmark = DynamicBenchmarkSuite(include_generalization=True)
    
    print(f"\n[测试] 运行 15 个任务...")
    results, summary = benchmark.run_all(mas)
    
    print(f"\n[核心任务]")
    print(f"  - 成功率: {summary['core_success_rate']*100:.1f}%")
    print(f"  - 得分: {summary['core_avg_score']:.1f}/100")
    print(f"  - Token: {summary['core_avg_tokens']:.1f}/task")
    
    print(f"\n[泛化任务]")
    print(f"  - 成功率: {summary['generalization_success_rate']*100:.1f}%")
    print(f"  - 得分: {summary['generalization_avg_score']:.1f}/100")
    print(f"  - Token: {summary['generalization_avg_tokens']:.1f}/task")
    
    print(f"\n[综合]")
    print(f"  - 综合评分: {summary['composite_score']:.2f}/100")
    print(f"  - Token: {summary['avg_tokens']:.1f}/task")
    
    print(f"\n[任务分解]")
    for r in results:
        print(f"  {r.task_id}: tokens={r.tokens}, score={r.score}")
    
    gen164_composite = 92.20
    gen164_gen = 74.0
    
    print(f"\n[对比Gen164]")
    if summary['composite_score'] > gen164_composite and summary['generalization_avg_score'] >= gen164_gen:
        verdict = "✅✅✅ 新冠军!"
    elif summary['generalization_avg_score'] > gen164_gen:
        verdict = "✅✅ 泛化提升!"
    elif summary['composite_score'] > gen164_composite:
        verdict = "✅✅ 综合提升!"
    else:
        verdict = "⚠️ 待优化"
    
    print(f"[判定] {verdict}")
    
    output_file = "/root/.openclaw/workspace/mas_repo/benchmark_results_gen168.json"
    with open(output_file, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "generation": 168,
            "architecture": "Extended Output Selection",
            "summary": summary,
            "individual_results": [asdict(r) for r in results]
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n结果已保存至: {output_file}")

if __name__ == "__main__":
    run_evaluation()