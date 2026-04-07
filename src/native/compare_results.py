#!/usr/bin/env python3
"""
Benchmark 结果对比工具

用法:
    python compare_results.py
    python compare_results.py v8_0_standard_checkpoint.json benchmark_results_v9_0_ext.json
"""

import os
import sys
import json
import glob

def load_result_file(filepath):
    """加载结果文件"""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except Exception as e:
        return None

def get_summary(result):
    """从结果中提取 summary"""
    if isinstance(result, dict):
        if "summary" in result:
            return result["summary"]
        return result
    return None

def format_row(name, composite, core, gen, action, gen_code=None, errors=0):
    """格式化表格行"""
    if gen_code is not None:
        return f"{name:<40} {composite:>10.2f} {core:>8.2f} {gen:>8.2f} {action:>8.2f} {gen_code:>8.2f} {errors:>6}"
    return f"{name:<40} {composite:>10.2f} {core:>8.2f} {gen:>8.2f} {action:>8.2f} {'':>8} {errors:>6}"

def compare_results(filepaths):
    """对比多个结果文件"""
    print("=" * 100)
    print("BENCHMARK RESULTS COMPARISON")
    print("=" * 100)
    
    results = []
    for filepath in filepaths:
        if not os.path.exists(filepath):
            print(f"\n⚠️  File not found: {filepath}")
            continue
        
        data = load_result_file(filepath)
        if data is None:
            print(f"\n⚠️  Could not load: {filepath}")
            continue
        
        summary = get_summary(data)
        if summary is None:
            print(f"\n⚠️  No summary in: {filepath}")
            continue
        
        results.append({
            "name": os.path.basename(filepath),
            "full_path": filepath,
            "summary": summary
        })
    
    if not results:
        print("\n❌ No valid results found")
        return
    
    # 按 composite score 排序
    results.sort(key=lambda x: x["summary"].get("composite_score", 0), reverse=True)
    
    print(f"\n{'Version':<40} {'Composite':>10} {'Core':>8} {'Gen':>8} {'Action':>8} {'GenCode':>8} {'Errors':>6}")
    print("-" * 100)
    
    best_composite = results[0]["summary"].get("composite_score", 0) if results else 0
    
    for r in results:
        s = r["summary"]
        composite = s.get("composite_score", 0)
        core = s.get("core_avg_score", 0)
        gen = s.get("gen_avg_score", 0)
        action = s.get("avg_actionability_level", 0)
        gen_code = s.get("gen_code_avg_score", 0) or s.get("gen_code", 0) or None
        errors = s.get("errors_count", 0)
        
        marker = " 🏆" if composite == best_composite else ""
        print(f"{r['name']:<40} {composite:>10.2f} {core:>8.2f} {gen:>8.2f} {action:>8.2f} {(gen_code if gen_code else 0):>8.2f} {errors:>6}{marker}")
    
    # 差异分析
    if len(results) >= 2:
        print("\n" + "=" * 100)
        print("DIFFERENCE ANALYSIS (vs best)")
        print("=" * 100)
        
        best = results[0]
        print(f"\n{'Version':<40} {'ΔComposite':>12} {'ΔCore':>10} {'ΔGen':>10}")
        print("-" * 80)
        
        for r in results[1:]:
            s = r["summary"]
            b = best["summary"]
            
            delta_comp = s.get("composite_score", 0) - b.get("composite_score", 0)
            delta_core = s.get("core_avg_score", 0) - b.get("core_avg_score", 0)
            delta_gen = s.get("gen_avg_score", 0) - b.get("gen_avg_score", 0)
            
            print(f"{r['name']:<40} {delta_comp:>+12.2f} {delta_core:>+10.2f} {delta_gen:>+10.2f}")
    
    # 详细结果
    print("\n" + "=" * 100)
    print("INDIVIDUAL TASK SCORES")
    print("=" * 100)
    
    for r in results[:5]:  # 最多显示前5个
        print(f"\n--- {r['name']} ---")
        data = load_result_file(r['full_path'])
        if data and "individual_results" in data:
            for task in data["individual_results"]:
                task_id = task.get("task_id", "?")
                score = task.get("quality_score", 0)
                iterations = task.get("iterations", 1)
                error = task.get("error", "")
                
                error_mark = " ❌" if error else ""
                reflect_mark = f" (iter={iterations})" if iterations > 1 else ""
                
                print(f"  {task_id:<12} {score:>5}{reflect_mark}{error_mark}")


def auto_discover_results():
    """自动发现结果文件"""
    patterns = [
        "benchmark_results_v*.json",
        "*checkpoint.json",
        "results*.json"
    ]
    
    found = []
    for pattern in patterns:
        found.extend(glob.glob(pattern))
    
    # 去重并排序
    seen = set()
    unique = []
    for f in found:
        if f not in seen:
            seen.add(f)
            unique.append(f)
    
    return sorted(unique)


def main():
    if len(sys.argv) > 1:
        # 使用命令行指定文件
        filepaths = sys.argv[1:]
    else:
        # 自动发现
        print("No files specified, auto-discovering...")
        filepaths = auto_discover_results()
        
        if not filepaths:
            print("No result files found!")
            print("\nUsage:")
            print("  python compare_results.py                          # auto-discover")
            print("  python compare_results.py file1.json file2.json   # specify files")
            return
        
        print(f"Found {len(filepaths)} result files:")
        for f in filepaths:
            print(f"  - {f}")
    
    compare_results(filepaths)


if __name__ == "__main__":
    main()