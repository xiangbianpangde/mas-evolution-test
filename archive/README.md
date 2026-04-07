# 📦 Archive

> 历史归档 - 不再活跃使用但保留用于参考

---

## 目录结构

```
archive/
├── README.md                    # 本文件
│
├── python_mas/                   # Python MAS 版本历史
│   ├── core_gen1.py ~ core_gen404.py
│   └── (旧的 Python 实现)
│
├── evaluate_scripts/             # 旧版评测脚本
│   ├── evaluate_gen10.py ~ evaluate_gen400.py
│   └── (自动化评测脚本)
│
├── reports/                     # 历史报告
│   ├── GEN01_REPORT.md ~ GEN200+_REPORT.md
│   └── (各版本的详细报告)
│
├── logs/                        # 运行日志
│   ├── harness_v10_0_run.log
│   ├── harness_v12_0_rerun.log
│   └── ... (各种运行日志)
│
├── benchmark_json/              # 基准测试 JSON
├── benchmark_results_v29_gen1.json
├── evaluate.py                  # 旧评测脚本
├── generate_reports.py          # 报告生成
├── generate_reports_gen121_164.py
├── harness_results_v26.md
├── run_v7_0_tool.sh
├── run_v8_0_standard.sh
└── run_v9_0_ext.sh
```

---

## 内容说明

### python_mas/
Python 实现的多智能体系统版本。
**状态**: 已废弃 (OpenClaw Native 更好)

### evaluate_scripts/
自动化评测脚本，用于批量运行和评分。
**状态**: 保留参考

### reports/
各版本的详细评测报告。
**状态**: 历史记录

### logs/
运行日志，用于调试和复盘。
**状态**: 历史记录

---

## 为什么保留

- **历史追踪**: 了解演进过程
- **调试参考**: 出现问题时可以回溯
- **趋势分析**: 查看分数变化

---

## 清理计划

如果磁盘空间不足，可以清理：
1. `reports/` 中的旧报告 (保留 gen100, 200, 300 等关键节点)
2. `logs/` 中的所有日志
3. `benchmark_json/` 如果不再需要

---

*最后更新: 2026-04-07*
