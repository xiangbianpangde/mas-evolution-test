#!/usr/bin/env python3
"""
自动生成人类可读的测试结果报告

每次运行完 benchmark 后调用此脚本，生成人类友好的 README.md
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime

def load_results(version):
    """加载结果"""
    base_dir = Path(__file__).parent.parent.parent
    results_dir = base_dir / "results" / version
    
    scores_file = results_dir / "scores.json"
    if not scores_file.exists():
        return None
    
    with open(scores_file) as f:
        return json.load(f)

def generate_task_table(results):
    """生成任务表格"""
    tasks = results.get("individual_results", [])
    
    lines = []
    lines.append("| 任务 | 类型 | 分数 |")
    lines.append("|------|------|------|")
    
    for task in tasks:
        task_id = task.get("task_id", "")
        task_type = task.get("task_type", "")
        score = task.get("quality_score", 0)
        lines.append(f"| {task_id} | {task_type} | {score:.1f} |")
    
    return "\n".join(lines)

def generate_readme(results, version):
    """生成 README.md"""
    summary = results.get("summary", {})
    timestamp = results.get("timestamp", datetime.now().isoformat())
    
    readme = f"""# {version} 结果

> 生成时间: {timestamp}

## 📊 分数概览

| 指标 | 值 |
|------|-----|
| **综合评分** | {summary.get('composite_score', 0):.2f} |
| Core 平均 | {summary.get('core_avg_score', 0):.2f} |
| Gen 平均 | {summary.get('gen_avg_score', 0):.2f} |
| 可操作性 | {summary.get('avg_actionability_level', 0):.2f} |

## 📋 任务详情

| 任务 | 类型 | 分数 |
|------|------|------|

"""
    return readme

def main():
    if len(sys.argv) < 2:
        print("用法: python3 generate_result_report.py <version>")
        sys.exit(1)
    
    version = sys.argv[1]
    results = load_results(version)
    
    if not results:
        print(f"未找到 {version} 的结果")
        sys.exit(1)
    
    # 生成 README
    readme = generate_readme(results, version)
    
    # 保存
    base_dir = Path(__file__).parent.parent.parent
    results_dir = base_dir / "results" / version
    readme_file = results_dir / "README.md"
    
    with open(readme_file, "w") as f:
        f.write(readme)
    
    print(f"已生成: {readme_file}")

if __name__ == "__main__":
    main()
