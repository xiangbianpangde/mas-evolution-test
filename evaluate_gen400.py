#!/usr/bin/env python3
"""
MAS Evaluator - Gen400 Benchmark
REAL API CALLS - No More Mock Data!
"""

import sys
import json
from datetime import datetime

sys.path.insert(0, '/root/.openclaw/workspace/mas_repo')

from benchmark.tasks_v2 import DynamicBenchmarkSuite
from mas.core_gen400 import create_mas_system
from dataclasses import asdict

def run_evaluation():
    print("=" * 60)
    print("MAS Evolution Engine - Gen400 Benchmark")
    print("REAL API PARADIGM - Authentic LLM Calls")
    print("=" * 60)
    
    mas = create_mas_system()
    benchmark = DynamicBenchmarkSuite(include_generalization=True)
    
    print("\n[警告] 这将进行真实的 API 调用!")
    print("[测试] 运行 15 个任务 (每次调用约 0.5-2 秒延迟)")
    print()
    
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
    print(f"  - 综合评分(字典序): {summary['composite_score']:.2f}/100")
    
    gen300_composite = 97.0
    gen300_gen = 90.0
    
    print(f"\n[对比Gen300 (模拟)]")
    print(f"  - Gen300: 综合={gen300_composite}, 泛化={gen300_gen} (模拟数据)")
    print(f"  - 当前: 综合={summary['composite_score']:.2f}, 泛化={summary['generalization_avg_score']:.1f} (真实API)")
    
    output_file = "/root/.openclaw/workspace/mas_repo/benchmark_results_gen400.json"
    with open(output_file, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "generation": 400,
            "architecture": "Real API Multi-Agent Architecture",
            "summary": summary,
            "individual_results": [asdict(r) for r in results]
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n结果已保存至: {output_file}")
    return summary

if __name__ == "__main__":
    run_evaluation()