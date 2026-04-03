#!/usr/bin/env python3
"""
MAS Evaluator - Gen169 Benchmark v2
Score Enhancement without Token Increase
"""

import sys
import json
from datetime import datetime

sys.path.insert(0, '/root/.openclaw/workspace/mas_repo')

from benchmark.tasks_v2 import DynamicBenchmarkSuite, get_baseline_single_agent
from mas.core_gen169 import create_mas_system
from dataclasses import asdict

def run_evaluation():
    print("=" * 60)
    print("MAS Evolution Engine - Gen169 Benchmark")
    print("Score Enhancement without Token Increase")
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
    
    # New champion conditions
    if (summary['core_avg_score'] > gen164_core and 
        summary['composite_score'] >= gen164_composite and
        summary['avg_tokens'] <= gen164_tokens):
        verdict = "✅✅✅ 新冠军! 分数提升且Token不增"
    elif summary['composite_score'] > gen164_composite:
        verdict = "✅✅ 新冠军! 综合评分提升"
    elif summary['core_avg_score'] > gen164_core:
        verdict = "✅ 新冠军! 核心分数提升"
    else:
        verdict = "⚠️ 待优化"
    
    print(f"[判定] {verdict}")
    
    output_file = "/root/.openclaw/workspace/mas_repo/benchmark_results_gen169.json"
    with open(output_file, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "generation": 169,
            "architecture": "Score Enhancement without Token Increase",
            "summary": summary,
            "individual_results": [asdict(r) for r in results]
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n结果已保存至: {output_file}")

if __name__ == "__main__":
    run_evaluation()