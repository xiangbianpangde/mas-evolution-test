#!/usr/bin/env python3
"""Gen193 Benchmark v2"""
import sys
import json
from datetime import datetime
sys.path.insert(0, '/root/.openclaw/workspace/mas_repo')
from benchmark.tasks_v2 import DynamicBenchmarkSuite
from mas.core_gen193 import create_mas_system
from dataclasses import asdict

def run_evaluation():
    print("Gen193 - Higher Relevance Multiplier")
    mas = create_mas_system()
    benchmark = DynamicBenchmarkSuite(include_generalization=True)
    results, summary = benchmark.run_all(mas)
    print(f"核心: {summary['core_avg_score']:.1f} 泛化: {summary['generalization_avg_score']:.1f} 综合: {summary['composite_score']:.2f}")
    gen185 = 95.2
    verdict = "✅新冠军!" if summary['composite_score'] > gen185 else "⚠️待优化"
    print(f"[判定] {verdict}")
    with open("/root/.openclaw/workspace/mas_repo/benchmark_results_gen193.json", 'w') as f:
        json.dump({"generation": 193, "summary": summary}, f, indent=2)
    return summary

if __name__ == "__main__":
    run_evaluation()