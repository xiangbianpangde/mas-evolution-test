#!/usr/bin/env python3
"""
MAS Evaluator - Gen307 Benchmark
Reduced max_outputs=4 to lower tokens
"""

import sys
import json
from datetime import datetime

sys.path.insert(0, '/root/.openclaw/workspace/mas_repo')

from benchmark.tasks_v2 import DynamicBenchmarkSuite
from mas.core_gen307 import create_mas_system
from dataclasses import asdict

def run_evaluation():
    print("=" * 60)
    print("MAS Evolution Engine - Gen307 Benchmark")
    print("Reduced max_outputs=4 for lower tokens")
    print("=" * 60)
    
    mas = create_mas_system()
    benchmark = DynamicBenchmarkSuite(include_generalization=True)
    
    print(f"\n[测试] 运行 15 个任务...")
    results, summary = benchmark.run_all(mas)
    
    print(f"\n[核心任务结果]")
    print(f"  - 成功率: {summary['core_success_rate']*100:.1f}%")
    print(f"  - 得分: {summary['core_avg_score']:.1f}/100")
    print(f"  - Token: {summary['core_avg_tokens']:.1f}/task")
    
    print(f"\n[泛化任务结果]")
    print(f"  - 成功率: {summary['generalization_success_rate']*100:.1f}%")
    print(f"  - 得分: {summary['generalization_avg_score']:.1f}/100")
    print(f"  - Token: {summary['generalization_avg_tokens']:.1f}/task")
    
    print(f"\n[综合评分]")
    print(f"  - 综合评分: {summary['composite_score']:.2f}/100")
    print(f"  - Token: {summary['avg_tokens']:.1f}/task")
    
    gen300_composite = 97.0
    gen300_gen = 90.0
    gen300_tokens = 5.0
    
    print(f"\n[对比Gen300]")
    print(f"  - Gen300: 综合={gen300_composite}, 泛化={gen300_gen}, Token={gen300_tokens}")
    print(f"  - 当前: 综合={summary['composite_score']:.2f}, 泛化={summary['generalization_avg_score']:.1f}, Token={summary['avg_tokens']:.1f}")
    
    if summary['composite_score'] > gen300_composite:
        verdict = "✅✅✅ 新冠军!"
    elif summary['generalization_avg_score'] > gen300_gen:
        verdict = "✅✅ 泛化提升"
    elif summary['avg_tokens'] < gen300_tokens and summary['generalization_avg_score'] >= gen300_gen * 0.95:
        verdict = "✅ Token优化"
    else:
        verdict = "⚠️ 待优化"
    
    print(f"[判定] {verdict}")
    
    output_file = "/root/.openclaw/workspace/mas_repo/benchmark_results_gen307.json"
    with open(output_file, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "generation": 307,
            "architecture": "Negotiation with max_outputs=4",
            "summary": summary,
            "individual_results": [asdict(r) for r in results]
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n结果已保存至: {output_file}")

if __name__ == "__main__":
    run_evaluation()