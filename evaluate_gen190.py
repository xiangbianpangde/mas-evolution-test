#!/usr/bin/env python3
"""Gen190 Benchmark v2"""
import sys
import json
from datetime import datetime
sys.path.insert(0, '/root/.openclaw/workspace/mas_repo')
from benchmark.tasks_v2 import DynamicBenchmarkSuite
from mas.core_gen190 import create_mas_system
from dataclasses import asdict

def run_evaluation():
    print("=" * 60)
    print("Gen190 Benchmark - Higher Relevance Weight")
    print("=" * 60)
    
    mas = create_mas_system()
    benchmark = DynamicBenchmarkSuite(include_generalization=True)
    
    print(f"\n[测试] 运行 15 个任务...")
    results, summary = benchmark.run_all(mas)
    
    print(f"\n[核心任务]")
    print(f"  - 成功率: {summary['core_success_rate']*100:.1f}%")
    print(f"  - 得分: {summary['core_avg_score']:.1f}/100")
    print(f"  - Token: {summary['core_avg_tokens']:.1f}")
    
    print(f"\n[泛化任务]")
    print(f"  - 成功率: {summary['generalization_success_rate']*100:.1f}%")
    print(f"  - 得分: {summary['generalization_avg_score']:.1f}/100")
    print(f"  - Token: {summary['generalization_avg_tokens']:.1f}")
    
    print(f"\n[综合]")
    print(f"  - 评分: {summary['composite_score']:.2f}/100")
    print(f"  - Token: {summary['avg_tokens']:.1f}")
    
    gen185_composite = 95.2
    gen185_gen = 84.0
    gen185_core = 75.0
    
    print(f"\n[对比Gen185]")
    print(f"  - Gen185: 核心={gen185_core}, 泛化={gen185_gen}, 综合={gen185_composite}")
    print(f"  - 当前: 核心={summary['core_avg_score']:.1f}, 泛化={summary['generalization_avg_score']:.1f}, 综合={summary['composite_score']:.2f}")
    
    if (summary['core_avg_score'] >= gen185_core and 
        summary['generalization_avg_score'] >= gen185_gen and
        summary['composite_score'] > gen185_composite):
        verdict = "✅✅✅ 新冠军! 全面超越!"
    elif summary['composite_score'] > gen185_composite:
        verdict = "✅✅ 新冠军! 综合评分提升"
    elif summary['generalization_avg_score'] > gen185_gen:
        verdict = "✅ 新冠军! 泛化提升"
    else:
        verdict = "⚠️ 待优化"
    
    print(f"[判定] {verdict}")
    
    output_file = "/root/.openclaw/workspace/mas_repo/benchmark_results_gen190.json"
    with open(output_file, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "generation": 190,
            "architecture": "Higher Relevance Weight",
            "summary": summary,
            "individual_results": [asdict(r) for r in results]
        }, f, indent=2, ensure_ascii=False)
    print(f"\n结果已保存至: {output_file}")
    return summary

if __name__ == "__main__":
    run_evaluation()