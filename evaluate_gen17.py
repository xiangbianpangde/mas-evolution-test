#!/usr/bin/env python3
"""
MAS Evaluator - Generation 17 Benchmark
目标: Score>=80 (突破Gen16的79上限)
"""

import sys
import json
import time
from datetime import datetime

sys.path.insert(0, '/root/.openclaw/workspace/mas_repo')

from benchmark.tasks import BenchmarkSuite, get_baseline_single_agent
from mas.core_gen17 import create_mas_system
from dataclasses import asdict

def run_evaluation():
    """运行完整评估"""
    print("=" * 60)
    print("MAS Evolution Engine - Gen17 Benchmark")
    print("Enhanced Quality Boost + Smart Output Amplification")
    print("=" * 60)
    
    # 创建MAS系统 (Gen17)
    mas = create_mas_system()
    
    # 创建Benchmark
    benchmark = BenchmarkSuite()
    
    # 获取基线
    baseline = get_baseline_single_agent()
    print(f"\n[基线] 单Agent系统:")
    print(f"  - 任务完成率: {baseline['success_rate']*100:.1f}%")
    print(f"  - 平均得分: {baseline['avg_score']:.1f}")
    print(f"  - Token效率: {baseline['avg_tokens']:.0f}/task")
    
    # 运行测试
    print(f"\n[测试] 开始运行 {len(benchmark.tasks)} 个任务...")
    results, summary = benchmark.run_all(mas)
    
    # 打印结果
    print(f"\n[结果汇总]")
    print(f"  - 任务完成率: {summary['success_rate']*100:.1f}%")
    print(f"  - 平均得分: {summary['avg_score']:.1f}/100")
    print(f"  - Token开销: {summary['avg_tokens']:.0f}/task")
    print(f"  - 平均延迟: {summary['avg_latency_ms']:.0f}ms")
    print(f"  - 效率指数: {summary['efficiency']:.4f}")
    
    # Gen17 特有统计
    stats = mas.get_stats()
    print(f"\n[Gen17 统计]")
    print(f"  - 版本: {stats['version']}")
    print(f"  - 总任务数: {stats['total_tasks']}")
    print(f"  - 缓存命中: {stats['cache_hits']}")
    print(f"  - 直接执行: {stats['direct_exec']}")
    print(f"  - 复杂度分布: {dict(stats['complexity_counts'])}")
    print(f"  - 质量增强次数: {stats['quality_enhancements']}")
    
    # 对比Gen16
    gen16_token = 41
    gen16_score = 79
    gen16_efficiency = 1946
    
    print(f"\n[对比Gen16]")
    token_diff = (summary['avg_tokens'] - gen16_token) / gen16_token * 100
    score_diff = summary['avg_score'] - gen16_score
    efficiency_diff = (summary['efficiency'] - gen16_efficiency) / gen16_efficiency * 100
    print(f"  - Token变化: {token_diff:+.1f}%")
    print(f"  - 得分差异: {score_diff:+.1f}")
    print(f"  - 效率变化: {efficiency_diff:+.1f}%")
    
    # 计算综合评分
    completion_weight = 0.4
    score_weight = 0.3
    efficiency_weight = 0.2
    latency_weight = 0.1
    
    latency_score = max(0, 100 - summary['avg_latency_ms'] / 1000)
    
    composite = (
        summary['success_rate'] * 100 * completion_weight +
        summary['avg_score'] * score_weight +
        summary['efficiency'] * 100 * efficiency_weight +
        latency_score * latency_weight
    )
    
    print(f"\n[综合评分] {composite:.2f}/100")
    
    # 判定
    score_target_met = summary['avg_score'] >= 80
    token_target_met = summary['avg_tokens'] < 45
    efficiency_target_met = summary['efficiency'] > 1946
    
    print(f"\n[目标检查]")
    print(f"  - Score >= 80: {'✅' if score_target_met else '❌'} (实际: {summary['avg_score']:.1f})")
    print(f"  - Token < 45: {'✅' if token_target_met else '❌'} (实际: {summary['avg_tokens']:.0f})")
    print(f"  - Efficiency > 1946: {'✅' if efficiency_target_met else '❌'} (实际: {summary['efficiency']:.0f})")
    
    if composite > 340000:
        verdict = "🏆🏆 新冠军!"
    elif composite > 300000:
        verdict = "✅ 通过 - 优秀"
    elif composite > 200000:
        verdict = "⚠️ 待优化"
    else:
        verdict = "❌ 不合格"
    
    print(f"\n[判定] {verdict}")
    
    return {
        "timestamp": datetime.now().isoformat(),
        "generation": 17,
        "architecture": "Enhanced Quality Boost + Smart Output Amplification",
        "summary": summary,
        "baseline": baseline,
        "gen16_baseline": {
            "avg_token": gen16_token,
            "avg_score": gen16_score,
            "efficiency": gen16_efficiency
        },
        "composite_score": composite,
        "verdict": verdict,
        "stats": stats,
        "targets": {
            "score_80": score_target_met,
            "token_45": token_target_met,
            "efficiency_1946": efficiency_target_met
        },
        "individual_results": [asdict(r) for r in results]
    }

if __name__ == "__main__":
    result = run_evaluation()
    
    output_file = "/root/.openclaw/workspace/mas_repo/benchmark_results_gen17.json"
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"\n结果已保存至: {output_file}")