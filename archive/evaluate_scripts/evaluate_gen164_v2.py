#!/usr/bin/env python3
"""
MAS Evaluator - Gen164 with Dynamic Benchmark v2
测试泛化能力
"""

import sys
import json
from datetime import datetime

sys.path.insert(0, '/root/.openclaw/workspace/mas_repo')

from benchmark.tasks_v2 import DynamicBenchmarkSuite, get_baseline_single_agent
from mas.core_gen164 import create_mas_system
from dataclasses import asdict

def run_evaluation():
    print("=" * 60)
    print("MAS Evolution Engine - Gen164 Benchmark v2")
    print("Dynamic Benchmark with Generalization Test")
    print("=" * 60)
    
    mas = create_mas_system()
    benchmark = DynamicBenchmarkSuite(include_generalization=True)
    baseline = get_baseline_single_agent()
    
    print(f"\n[基线] 单Agent系统:")
    print(f"  - 成功率: {baseline['success_rate']*100:.1f}%")
    print(f"  - 泛化得分: {baseline['generalization_score']:.1f}")
    
    print(f"\n[测试] 运行 15 个任务 (10核心 + 5泛化)...")
    results, summary = benchmark.run_all(mas)
    
    print(f"\n[核心任务结果汇总]")
    print(f"  - 核心任务成功率: {summary['core_success_rate']*100:.1f}%")
    print(f"  - 核心任务得分: {summary['core_avg_score']:.1f}/100")
    print(f"  - 核心任务Token: {summary['core_avg_tokens']:.1f}/task")
    
    print(f"\n[泛化任务结果汇总]")
    print(f"  - 泛化任务成功率: {summary['generalization_success_rate']*100:.1f}%")
    print(f"  - 泛化任务得分: {summary['generalization_avg_score']:.1f}/100")
    print(f"  - 泛化任务Token: {summary['generalization_avg_tokens']:.1f}/task")
    
    print(f"\n[综合评分]")
    print(f"  - 成功率: {summary['success_rate']*100:.1f}%")
    print(f"  - 平均得分: {summary['avg_score']:.1f}/100")
    print(f"  - Token开销: {summary['avg_tokens']:.1f}/task")
    print(f"  - 效率指数: {summary['efficiency']:.0f}")
    print(f"  - 综合评分(字典序): {summary['composite_score']:.2f}/100")
    
    print(f"\n[防退化检查]")
    if summary['degradation_detected']:
        print(f"  ⚠️ 警告: 检测到可能的过拟合! 泛化得分显著低于核心得分")
    else:
        print(f"  ✅ 未检测到退化")
    
    print(f"\n[任务分解]")
    for r in results:
        gen_tag = "[泛化]" if r.is_generalization else "[核心]"
        print(f"  {gen_tag} {r.task_id}: tokens={r.tokens}, score={r.score}")
    
    # 保存结果
    output_file = "/root/.openclaw/workspace/mas_repo/benchmark_results_gen164_v2.json"
    with open(output_file, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "generation": 164,
            "architecture": "Selective Code Cost Reduction (v2 Benchmark)",
            "summary": summary,
            "baseline": baseline,
            "individual_results": [asdict(r) for r in results]
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n结果已保存至: {output_file}")
    return summary

if __name__ == "__main__":
    run_evaluation()