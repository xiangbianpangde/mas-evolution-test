# 🌳 AutoMAS 项目目录树

> 可视化导航 · 一目了然 · 快速定位

---

## 🗺️ 顶层总览

```
mas_repo/
├── 📄 README.md              ← 项目入口 · 快速概览
├── 📄 SUMMARY.md             ← 项目导航索引
│
├── 📁 src/                   ← 核心源码
│   ├── benchmark/           ← 评测任务定义
│   ├── native/              ← OpenClaw Native MAS
│   └── legacy/              ← Python MAS 历史代码
│
├── 📁 knowledge/             ← 知识库 ← YOU ARE HERE
│   ├── architecture/        ← 系统架构图
│   ├── benchmark/           ← 评测任务说明
│   ├── design/              ← 人机设计原则
│   ├── learning/            ← 学习与发现
│   │   ├── discoveries/     ← 核心发现
│   │   ├── experiments/     ← 实验记录
│   │   └── patterns/        ← 模式库
│   ├── lessons/             ← 失败教训
│   ├── prompts/             ← Prompt 模板库
│   ├── reference/           ← 参考资料
│   ├── sources/             ← 外部资源原文
│   ├── trends/              ← 已验证策略
│   └── TREE.md              ← 本文件
│
├── 📁 results/              ← 评测结果存档
├── 📁 papers/               ← 论文与研究资料
├── 📁 docs/                 ← 项目文档
├── 📁 archive/              ← 历史归档
└── 📁 datasets/             ← 数据集
```

---

## 📁 src/ — 核心源码

```
src/
├── 📂 benchmark/             ← 评测任务定义
│   ├── tasks_v2.py           ← 15个标准任务 (gen1基准)
│   ├── gen006_scorer.py      ← 第6代评分器
│   └── gen007_scorer.py      ← 第7代评分器
│
├── 📂 native/               ← OpenClaw Native MAS (当前主流)
│   ├── README.md
│   ├── base_harness.py      ← Harness 基类
│   ├── run_benchmark.py     ← 基准测试入口
│   ├── evolution_loop.py    ← 演进循环引擎
│   ├── evolution_state.json ← 演进状态
│   │
│   ├── 📂 harness/          ← 各版本 Harness
│   │   ├── harness_v31_0.py     ← 🏆 冠军版本 (76.22分)
│   │   ├── harness_v37.py       ← 扩展自评审 (失败)
│   │   ├── harness_v38.py       ← 增强 review prompts
│   │   ├── harness_v39.py       ← 2轮自我反思 (崩溃)
│   │   ├── harness_v40.py       ← 最新版本
│   │   ├── harness_evo_001.py   ← 演进引擎 v1
│   │   ├── harness_evo_002.py   ← 演进引擎 v2
│   │   ├── harness_evo_genesis.py ← 创世纪引擎
│   │   └── harness_template.py  ← Harness 模板
│   │
│   ├── 📂 harness_old/      ← 历史 Harness 归档
│   │   ├── v2-v9/            ← 早期版本
│   │   ├── v10-v19/          ← 发展阶段
│   │   ├── v20-v29/          ← 成熟阶段
│   │   └── v30-v39/          ← 近代版本
│   │
│   └── 📂 soul/              ← Agent SOUL 定义
│       └── SOUL.md
│
├── 📂 agents/                ← Genesis 团队 Agent
│   ├── prometheus/SOUL.md    ← 基础设施架构师
│   ├── athena/SOUL.md        ← 数据分析 Agent
│   ├── helios/SOUL.md        ← 全知监控 Agent
│   ├── hermes/SOUL.md        ← 通信总线
│   ├── archaeus/SOUL.md     ← 档案管理员
│   └── TEAM_SOUL.md          ← 团队灵魂
│
└── 📂 legacy/               ← Python MAS 历史代码
    ├── core.py               ← 树形 Supervisor-Worker
    ├── core_gen10.py         ← Gen10
    ├── core_gen100.py        ← Gen100
    ├── core_gen164.py        ← Gen164
    ├── core_gen300.py        ← Gen300
    └── core_gen404.py        ← Gen404 (94.90分)
```

---

## 📁 knowledge/ — 知识库

```
knowledge/
├── README.md                 ← 知识库总入口
├── TREE.md                   ← 本文件 · 目录树可视化
├── ARCHITECTURE.md           ← 系统架构图
├── QUICKSTART.md             ← 快速上手指南
│
├── 📂 sources/               ← ⭐ 第一手外部资源原文
│   ├── README.md
│   ├── OpenAI_Harness_Engineering.md
│   ├── Anthropic_Effective_Harnesses.md
│   ├── Martin_Fowler_Harness_Engineering.md
│   └── Google_Cloud_Agent_Patterns.md
│
├── 📂 reference/             ← 第二手参考资料
│   ├── README.md
│   ├── Harness_Engineering_Deep.md
│   └── Multi_Agent_Patterns.md
│
├── 📂 patterns/              ← 模式库 · 精华提炼
│   ├── README.md
│   └── patterns_index.md
│
├── 📂 benchmark/             ← 评测任务说明
│   ├── README.md
│   └── Benchmark_Tasks.md
│
├── 📂 trends/                ← 已验证的有效策略
│   ├── README.md
│   └── Known_Trends.md
│
├── 📂 lessons/               ← 失败教训总结
│   ├── README.md
│   └── Lessons_Learned.md
│
├── 📂 prompts/               ← Prompt 模板库
│   ├── README.md
│   └── Prompt_Library.md
│
├── 📂 design/                ← 人机交互设计
│   ├── README.md
│   └── Human_Centric_Design.md
│
└── 📂 learning/              ← 学习与发现
    ├── README.md
    ├── discoveries/         ← 核心发现
    │   └── README.md
    ├── experiments/          ← 实验记录
    │   ├── README.md
    │   ├── v38_analysis.md
    │   ├── v40_strategy.md
    │   └── v41_adaptive_reflection.md
    └── patterns/             ← 学习模式
        └── README.md
```

---

## 📁 results/ — 评测结果

```
results/
├── README.md
└── evolution/                    ← 演进实验结果
    └── benchmark_results_evo_001_gen1.json
```

---

## 📁 papers/ — 论文与研究资料

```
papers/
├── README.md
├── PAPER_01_TransPlanck_Convergence.md
├── PAPER_02_Evolution_Paradigm.md
├── PAPER_03_Convergence_Methodology.md
├── PAPER_04_Cost_Aware_Multi_Objective_Convergence.md
├── PAPER_05_Fractional_Paradigm_Convergence.md
├── PAPER_06_v2_Convergence_Report.md
└── RESEARCH_REPORT_GENERATIONS.md
```

---

## 📁 docs/ — 项目文档

```
docs/
├── ARCHITECTURE.md           ← 系统架构详解
├── EVOLUTION_HISTORY.md      ← 完整演进历史 (v20-v35)
└── CONVERGENCE_REPORT.md     ← 收敛分析报告
```

---

## 📁 archive/ — 历史归档

```
archive/
├── README.md
├── README_STRUCTURE.md
├── harness_results_v26.md
├── evaluate_scripts/         ← 历代评测脚本 (gen1-gen400+)
├── benchmark_json/           ← 历代评测结果
└── python_mas/              ← Python MAS 历史版本
```

---

## 🔍 快速定位索引

| 需求 | 路径 |
|------|------|
| 想看项目是什么 | `README.md` |
| 想找源码 | `src/native/harness/` |
| 想找评测任务 | `src/benchmark/tasks_v2.py` |
| 想找冠军版本代码 | `src/native/harness/harness_v31_0.py` |
| 想找 Prompt 模板 | `knowledge/prompts/Prompt_Library.md` |
| 想了解有效策略 | `knowledge/trends/Known_Trends.md` |
| 想看评测任务说明 | `knowledge/benchmark/Benchmark_Tasks.md` |
| 想学习外部资源 | `knowledge/sources/` |
| 想看实验记录 | `knowledge/learning/experiments/` |
| 想找论文资料 | `papers/` |
| 想看历史演进 | `docs/EVOLUTION_HISTORY.md` |

---

*最后更新: 2026-04-08*
