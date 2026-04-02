#!/usr/bin/env python3
"""
MAS Evaluator - Gen184 Benchmark v2
Specialized Outputs for Generalization
"""

import sys
import json
from datetime import datetime

sys.path.insert(0, '/root/.openclaw/workspace/mas_repo')

from benchmark.tasks_v2 import DynamicBenchmarkSuite
from mas.core_gen184 import create_mas_system
from dataclasses import asdict

def run_evaluation():
    print("=" * 60)
    print("MAS Evolution Engine - Gen184 Benchmark")
    print("Specialized Outputs for Generalization")
    print("=" * 60)
    
    mas = create_mas_system()
    benchmark = DynamicBenchmarkSuite(include_generalization=True)
    
    print(f"\n[测试] 运行 15 个任务...")
    results, summary = benchmark.run_all(mas)
    
    print(f"\n[核心任务]")
    print(f"  成功率: {summary['core_success_rate']*100:.1f}%")
    print(f"  得分: {summary['core_avg_score']:.1f}")
    print(f"  Token: {summary['core_avg_tokens']:.1f}")
    
    print(f"\n[泛化任务]")
    print(f"  成功率: {summary['generalization_success_rate']*100:.1f}%")
    print(f"  得分: {summary['generalization_avg_score']:.1f}")
    print(f"  Token: {summary['generalization_avg_tokens']:.1f}")
    
    print(f"\n[综合评分]")
    print(f"  综合: {summary['composite_score']:.2f}")
    print(f"  Token: {summary['avg_tokens']:.1f}")
    print(f"  效率: {summary['efficiency']:.0f}")
    
    print(f"\n[泛化任务分解]")
    for r in results:
        if r.is_generalization:
            print(f"  {r.task_id}: tokens={r.tokens}, score={r.score}")
    
    gen176_composite = 93.40
    gen176_gen = 78.0
    
    print(f"\n[对比Gen176]")
    print(f"  Gen176 综合: {gen176_composite}, 泛化: {gen176_gen}")
    print(f"  当前 综合: {summary['composite_score']:.2f}, 泛化: {summary['generalization_avg_score']:.1f}")
    
    if summary['composite_score'] > gen176_composite:
        verdict = "✅✅✅ 新冠军!"
    elif summary['generalization_avg_score'] > gen176_gen:
        verdict = "✅✅ 泛化提升"
    else:
        verdict = "⚠️ 待优化"
    
    print(f"[判定] {verdict}")
    
    output_file = "/root/.openclaw/workspace/mas_repo/benchmark_results_gen184.json"
    with open(output_file, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "generation": 184,
            "architecture": "Specialized Outputs for Generalization",
            "summary": summary,
            "individual_results": [asdict(r) for r in results]
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n结果已保存至: {output_file}")

if __name__ == "__main__":
    run_evaluation()