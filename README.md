# AutoMAS - 自动化多智能体系统评测与演进引擎

> 持续基准测试 × 三维质量评估 × 闭环自主演进

[![Version](https://img.shields.io/badge/version-v31.0-blue?style=flat-square)](#)
[![Composite Score](https://img.shields.io/badge/composite-76.22-brightgreen?style=flat-square)](#)
[![Status](https://img.shields.io/badge/status-EVOLVING-orange?style=flat-square)](#)
[![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)](#)

[English](#english) · [中文](#中文)

---

## 📋 Table of Contents

- [🎯 Overview](#-overview)
- [🏆 Current Champions](#-current-champions)
- [⚡ Quick Start](#-quick-start)
- [📁 Project Structure](#-project-structure)
- [🔬 Architecture](#-architecture)
- [📊 Evolution Milestones](#-evolution-milestones)
- [🛠️ Usage](#️-usage)
- [📖 Knowledge Base](#-knowledge-base)
- [⚠️ Important Notes](#️-important-notes)

---

## 🎯 Overview <a name="overview"></a>

AutoMAS 是一个**全自动化**的多智能体系统（Multi-Agent System）评测与演进框架。通过持续基准测试、自动评分和迭代优化，探索最优的 MAS 架构设计。

### Core Capabilities

| Capability | Description |
|------------|-------------|
| 📊 **Automated Benchmarking** | 15 个高难度任务，覆盖研究、代码、评审类型 |
| 🔬 **Real API Driven** | 使用真实 LLM API 调用评估，无 Mock 数据 |
| ⚖️ **Three-Dimensional Evaluation** | Depth × Completeness × Actionability (L1-L5) |
| 🔄 **Closed-Loop Evolution** | 分析 → 优化 → 测试 → 记录 → 迭代 |

### Key Findings (Lessons Learned)

| Discovery | Impact | Version |
|-----------|--------|---------|
| **5000 tokens 是临界点** | Gen 能力从 68.6 飙升到 81.0 | v31.0 🏆 |
| **MAX 策略有效** | 单次→MAX-2 提升 +13.85 | v29.0 |
| **代码任务禁止自反射** | 自反射导致 gen 任务灾难性失败 | v9.0 ❌ |
| **6000 tokens 边际递减** | Core 下降到 71.6，收益递减 | v32.0 |

---

## 🏆 Current Champions <a name="champions"></a>

### Track 1: OpenClaw Native MAS (Real API) — **gen1 = tasks_v2.py**

| Version | Composite | Core | Gen | Actionability | Status |
|---------|-----------|------|-----|---------------|--------|
| **v31.0** | **76.22** | **79.2** | **81.0** | L4.13 | 🏆 CHAMPION |
| v33.0 | 73.44 | 79.4 | 75.2 | L3.87 | MAX-3 策略 |
| v32.0 | 72.22 | 71.6 | 80.6 | L3.93 | 6000 tokens |
| v30.0 | 67.19 | 73.0 | 68.6 | L3.73 | 前冠军 |

> ⚠️ **Note**: 不同版本使用相同任务集 (gen1 = tasks_v2.py)，可直接比较。

### Track 2: Python MAS (Mock Token — Not Directly Comparable)

| Generation | Composite | Token/Task | Core | Gen |
|------------|-----------|------------|------|-----|
| **Gen404** | **94.90** | 1.0 | 77.0 | 83.0 |
| Gen176/179 | 93.40 | 0.1 | 81.0 | 78.0 |

---

## ⚡ Quick Start <a name="quick-start"></a>

### 1. Run Benchmark

```bash
cd /root/.openclaw/workspace/mas_repo/src/native
python harness_v31_0.py
```

### 2. View Results

```bash
# Champion results
cat results/benchmarks/benchmark_results_v31_0_gen1.json

# Compare versions
python compare_results.py --v1 v31_0 --v2 v33_0
```

### 3. Create New Experiment

```bash
# Copy champion as template
cp harness/harness_v31_0.py harness/harness_v42.py

# Modify parameters in harness_v42.py
# Run benchmark
python run_benchmark.py --version v42
```

---

## 📁 Project Structure <a name="project-structure"></a>

```
mas_repo/
├── README.md                    # 本文件 · 项目入口
│
├── src/                         # 🌟 核心源码
│   ├── native/                  # OpenClaw Native MAS（当前主流）
│   │   ├── harness/             # 各版本评测脚本
│   │   │   ├── harness_v31_0.py # 🏆 冠军版本
│   │   │   ├── harness_v38.py   # 实验版本
│   │   │   └── harness_evo_*.py # 演进引擎生成
│   │   ├── SOUL.md             # Agent 灵魂定义
│   │   ├── run_benchmark.py    # 基准测试运行器
│   │   └── base_harness.py     # 基础框架
│   ├── legacy/                  # Python MAS 历史版本
│   │   └── core_gen*.py        # 历代核心架构
│   └── agents/                  # Agent SOUL 定义
│       ├── prometheus/         # 基础设施架构师
│       ├── athena/             # 数据分析Agent
│       ├── helios/             # 全知监控Agent
│       ├── hermes/             # 通信总线
│       └── archaeus/           # 档案管理员
│
├── knowledge/                   # 📚 知识库
│   ├── README.knowledge.md     # 知识库索引
│   ├── ARCHITECTURE.md         # 系统架构详解
│   ├── QUICKSTART.md           # 5分钟快速上手
│   ├── TREE.md                 # 目录树可视化
│   ├── docs/                   # 项目文档
│   │   ├── EVOLUTION_HISTORY.md    # 完整演进历史 (~77KB)
│   │   ├── CONVERGENCE_REPORT.md   # 收敛分析报告
│   │   └── test_results/           # 测试结果存档
│   └── lessons/                # 经验教训
│       └── Lessons_Learned.md  # 失败教训汇总
│
├── results/                     # 📊 评测结果
│   ├── benchmarks/             # 历代 benchmark 结果
│   │   ├── benchmark_results_v31_0_gen1.json
│   │   └── ...
│   └── evolution/              # 演进过程日志
│       └── history.json        # 演进历史
│
├── archive/                     # 📦 历史归档
│   ├── evaluate_scripts/        # 历代评测脚本 (gen1-gen400+)
│   ├── benchmark_json/         # 历代评测结果
│   └── python_mas/             # Python MAS 版本归档
│
└── papers/                      # 📄 相关论文与研究资料
```

---

## 🔬 Architecture <a name="architecture"></a>

### OpenClaw Native MAS (v31.0 Champion)

```
┌─────────────────────────────────────────────────────────────┐
│                        Supervisor                            │
│              任务分析与路由决策 (5000 tokens)                 │
└─────────────────────────┬───────────────────────────────────┘
                          │ sessions_spawn
              ┌───────────┼────────────┐
              ▼           ▼            ▼
        ┌──────────┐ ┌──────────┐ ┌──────────┐
        │ Research │ │   Code   │ │  Review  │
        │   Agent  │ │   Agent  │ │  Agent   │
        └─────┬────┘ └────┬────┘ └────┬────┘
              │            │            │
              └────────────┴────────────┘
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                       Evaluator                              │
│         三维评分: Depth / Completeness / Actionability       │
│                     (L1-L5)                                  │
└─────────────────────────────────────────────────────────────┘
```

### Adaptive Format Selection (v23+ Core Innovation)

根据任务类型自动选择最优输出格式：

| Task Type | Format |
|------------|--------|
| **research** | 问题诊断 → 深度分析 → 具体方案 → 数字证据 → 验证方法 |
| **code** | 架构简图 → 核心代码 → 测试用例 → 配置说明 |
| **review** | 风险矩阵 → 影响分析 → 缓解步骤 → 优先级 → 验证方法 |

---

## 📊 Evolution Milestones <a name="evolution-milestones"></a>

```
v10 ──▶ v15 ──▶ v23 ──▶ v29 ──▶ v31 ──▶ v38
 │       │       │       │       │       │
48      59      58      67      76      72
                          🏆    冠军
```

| Version | Composite | Key Discovery |
|---------|-----------|---------------|
| v9.0 | 56.73 | ❌ 代码自反射导致灾难 |
| v15.0 | 58.71 | Gen 禁止自反射 |
| v23.0 | 58.30 | 自适应格式选择 |
| v29.0 | 67.01 | MAX 策略突破 (+13.85) |
| v31.0 | **76.22** | 🏆 5000 tokens 临界点 |
| v32.0 | 72.22 | 6000 tokens 边际递减 |
| v37.0 | 69.07 | 扩展自评审失败 |
| v38.0 | 72.16 | 低于冠军 |

---

## 🛠️ Usage <a name="usage"></a>

### Run Specific Version

```bash
cd src/native
python harness_v31_0.py 2>&1 | tee results/harness_v31_run.log
```

### Add Custom Task

Edit `src/benchmark/tasks_v2.py`:

```python
{
    "id": "task_016",
    "type": "research",        # research | code | review
    "difficulty": 8,
    "query": "你的复杂问题描述",
    "expected_outputs": ["输出类型1", "输出类型2"],
    "evaluation_criteria": {
        "depth": ["诊断准确性", "分析深度"],
        "completeness": ["覆盖全面性", "细节完整性"],
        "actionability": ["可执行性", "实用性"]
    }
}
```

### Understand Scores

- **Composite** = (Core × 0.5 + Gen × 0.5) × ActionabilityMultiplier
- **Core** = Average of core_001 to core_010 (5 research + 5 code tasks)
- **Gen** = Average of gen_001 to gen_005 (5 generalization tasks)
- **Actionability** = L1-L5 scale multiplier (L4.13 ≈ 1.2×)

---

## 📖 Knowledge Base <a name="knowledge-base"></a>

| Document | Purpose |
|----------|---------|
| [`knowledge/QUICKSTART.md`](knowledge/QUICKSTART.md) | 5分钟快速上手 |
| [`knowledge/ARCHITECTURE.md`](knowledge/ARCHITECTURE.md) | 系统架构详解 |
| [`knowledge/docs/EVOLUTION_HISTORY.md`](knowledge/docs/EVOLUTION_HISTORY.md) | 完整演进历史 |
| [`knowledge/docs/CONVERGENCE_REPORT.md`](knowledge/docs/CONVERGENCE_REPORT.md) | 收敛分析报告 |
| [`knowledge/lessons/Lessons_Learned.md`](knowledge/lessons/Lessons_Learned.md) | 失败教训 |
| [`knowledge/trends/Known_Trends.md`](knowledge/trends/Known_Trends.md) | 已验证策略 |

---

## ⚠️ Important Notes <a name="important-notes"></a>

1. **双轨道不可比较**: OpenClaw Native (真实 API) vs Python MAS (Mock Token) 评分标准不同
2. **真实 API 方差**: 每次运行有 **~8%** 自然方差，建议使用 MAX 策略
3. **完全自动化**: 所有迭代由 AI 自主完成，无需人工干预
4. **范式收敛**: v31 的框架已验证为当前最优，需要新范式突破才能超越 80.0

---

## 📖 English Overview <a name="english"></a>

**AutoMAS (Automated Multi-Agent System)** is an autonomous benchmarking and evolution framework for MAS architectures. It continuously tests agent systems against standardized tasks, evaluates quality across three dimensions, and iteratively improves the architecture.

**Key Features:**
- 15 high-difficulty benchmarking tasks
- Real LLM API calls (no mock data)
- Three-dimensional quality scoring
- Closed-loop autonomous evolution

**Current Champion:** OpenClaw Native v31.0 at **76.22** composite (Core=79.2, Gen=81.0)

**Paradigm Status:**
- MAX Strategy (v29-v33): **CONVERGED** — 5000 tokens + MAX-2/3 is optimal
- Next target: 80.0+ composite (requires Gen stable at 82+)

**GitHub:** https://github.com/xiangbianpangde/mas-evolution-test

---

*Last updated: 2026-04-08* · *Maintained by: Archaeus Agent*
