#!/usr/bin/env python3
"""
MAS Evaluator - Gen170 Benchmark v2
Specialized Outputs for Generalization Tasks
"""

import sys
import json
from datetime import datetime

sys.path.insert(0, '/root/.openclaw/workspace/mas_repo')

from benchmark.tasks_v2 import DynamicBenchmarkSuite, get_baseline_single_agent
from mas.core_gen170 import create_mas_system
from dataclasses import asdict

def run_evaluation():
    print("=" * 60)
    print("MAS Evolution Engine - Gen170 Benchmark")
    print("Specialized Outputs for Generalization Tasks")
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
    
    gen164_composite = 92.20
    gen164_core = 81.0
    gen164_gen = 74.0
    gen164_tokens = 0.1
    
    print(f"\n[对比Gen164]")
    print(f"  - Gen164: 核心{gen164_core}, 泛化{gen164_gen}, Token{gen164_tokens}")
    print(f"  - 当前: 核心{summary['core_avg_score']:.1f}, 泛化{summary['generalization_avg_score']:.1f}, Token{summary['avg_tokens']:.1f}")
    
    if summary['generalization_avg_score'] > gen164_gen:
        if summary['composite_score'] >= gen164_composite:
            verdict = "✅✅✅ 新冠军! 泛化得分显著提升"
        else:
            verdict = "✅✅ 新冠军! 泛化提升"
    elif summary['composite_score'] > gen164_composite:
        verdict = "✅✅ 新冠军! 综合评分提升"
    elif summary['core_avg_score'] > gen164_core:
        verdict = "✅ 新冠军! 核心分数提升"
    else:
        verdict = "⚠️ 待优化"
    
    print(f"[判定] {verdict}")
    
    print(f"\n[任务分解]")
    for r in results:
        gen_tag = "[泛化]" if r.is_generalization else "[核心]"
        print(f"  {gen_tag} {r.task_id}: tokens={r.tokens}, score={r.score}")
    
    output_file = "/root/.openclaw/workspace/mas_repo/benchmark_results_gen170.json"
    with open(output_file, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "generation": 170,
            "architecture": "Specialized Outputs for Generalization",
            "summary": summary,
            "individual_results": [asdict(r) for r in results]
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n结果已保存至: {output_file}")

if __name__ == "__main__":
    run_evaluation()