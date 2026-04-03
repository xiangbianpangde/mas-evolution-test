#!/usr/bin/env python3
"""
MAS Evaluator - Generation 18 Benchmark
Fusion: Gen16 Token Precision + Gen17 Quality Enhancement
目标: Score>=80 AND Token<45 AND Efficiency>1946
"""

import sys
import json
import time
from datetime import datetime

sys.path.insert(0, '/root/.openclaw/workspace/mas_repo')

from benchmark.tasks import BenchmarkSuite, get_baseline_single_agent
from mas.core_gen18 import create_mas_system
from dataclasses import asdict

def run_evaluation():
    """运行完整评估"""
    print("=" * 60)
    print("MAS Evolution Engine - Gen18 Benchmark")
    print("Fusion: Gen16 Token Precision + Gen17 Quality")
    print("目标: Score>=80 AND Token<45 AND Efficiency>1946")
    print("=" * 60)
    
    # 创建MAS系统 (Gen18)
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
    
    # Gen18 特有统计
    stats = mas.get_stats()
    print(f"\n[Gen18 统计]")
    print(f"  - 版本: {stats['version']}")
    print(f"  - 总任务数: {stats['total_tasks']}")
    print(f"  - 缓存命中: {stats['cache_hits']}")
    print(f"  - 直接执行: {stats['direct_exec']}")
    print(f"  - 复杂度分布: {dict(stats['complexity_counts'])}")
    print(f"  - 缓存命中率: {stats['cache']['hit_rate']:.2%}")
    
    # 对比目标
    print(f"\n[目标检查]")
    score_ok = summary['avg_score'] >= 80
    token_ok = summary['avg_tokens'] < 45
    efficiency_ok = summary['efficiency'] > 1946
    print(f"  - Score >= 80: {summary['avg_score']:.1f} {'✅' if score_ok else '❌'}")
    print(f"  - Token < 45: {summary['avg_tokens']:.0f} {'✅' if token_ok else '❌'}")
    print(f"  - Efficiency > 1946: {summary['efficiency']:.1f} {'✅' if efficiency_ok else '❌'}")
    
    # 对比Gen16和Gen17
    gen16_score = 79
    gen16_tokens = 41
    gen16_efficiency = 1946
    
    gen17_score = 81
    gen17_tokens = 47
    gen17_efficiency = 1738
    
    print(f"\n[对比Gen16]")
    print(f"  - Score: {summary['avg_score']:.1f} vs {gen16_score} ({summary['avg_score']-gen16_score:+.1f})")
    print(f"  - Token: {summary['avg_tokens']:.0f} vs {gen16_tokens} ({summary['avg_tokens']-gen16_tokens:+.0f})")
    print(f"  - Efficiency: {summary['efficiency']:.1f} vs {gen16_efficiency} ({summary['efficiency']-gen16_efficiency:+.1f})")
    
    print(f"\n[对比Gen17]")
    print(f"  - Score: {summary['avg_score']:.1f} vs {gen17_score} ({summary['avg_score']-gen17_score:+.1f})")
    print(f"  - Token: {summary['avg_tokens']:.0f} vs {gen17_tokens} ({summary['avg_tokens']-gen17_tokens:+.0f})")
    print(f"  - Efficiency: {summary['efficiency']:.1f} vs {gen17_efficiency} ({summary['efficiency']-gen17_efficiency:+.1f})")
    
    # 计算综合评分
    completion_weight = 0.4
    score_weight = 0.3
    efficiency_weight = 0.2
    latency_weight = 0.1
    
    latency_score = max(0, 100 - summary['avg_latency_ms'] / 1000)
    
    composite = (
        summary['success_rate'] * 100 * completion_weight +
        summary['avg_score'] * score_weight +
        summary['efficiency'] * 1000 * efficiency_weight +
        latency_score * latency_weight
    )
    
    print(f"\n[综合评分] {composite:.2f}/100")
    
    # 判定
    all_goals_met = score_ok and token_ok and efficiency_ok
    if all_goals_met:
        verdict = "🏆 完美! 达成所有目标"
    elif composite > 70000:
        verdict = "✅ 优秀 - 大幅超越基线"
    elif composite > 60000:
        verdict = "✅ 良好 - 超越基线"
    elif composite > 50000:
        verdict = "⚠️ 一般 - 接近基线"
    else:
        verdict = "❌ 不合格 - 显著低于基线"
    
    print(f"[判定] {verdict}")
    
    return {
        "timestamp": datetime.now().isoformat(),
        "generation": 18,
        "architecture": "Fusion: Gen16 Token Precision + Gen17 Quality",
        "goals": {
            "score_target": 80,
            "token_target": 45,
            "efficiency_target": 1946
        },
        "goals_met": {
            "score": score_ok,
            "token": token_ok,
            "efficiency": efficiency_ok
        },
        "summary": summary,
        "baseline": baseline,
        "gen16_baseline": {
            "avg_score": gen16_score,
            "avg_tokens": gen16_tokens,
            "efficiency": gen16_efficiency
        },
        "gen17_baseline": {
            "avg_score": gen17_score,
            "avg_tokens": gen17_tokens,
            "efficiency": gen17_efficiency
        },
        "composite_score": composite,
        "verdict": verdict,
        "stats": stats,
        "individual_results": [asdict(r) for r in results]
    }

if __name__ == "__main__":
    result = run_evaluation()
    
    # 保存结果
    output_file = "/root/.openclaw/workspace/mas_repo/benchmark_results_gen18.json"
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"\n结果已保存至: {output_file}")