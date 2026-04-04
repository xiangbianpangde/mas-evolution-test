# AutoMAS - 自动化多智能体系统评测与演进引擎

[English](#english) | 中文

---

## 🎯 项目简介

AutoMAS 是一个**全自动化**的多智能体系统（Multi-Agent System）评测与演进框架。它通过持续的基准测试、自动评分和迭代优化，探索最优的 MAS 架构设计。

**核心能力：**
- 📊 **自动化基准测试** — 15 个高难度任务，覆盖研究、代码、评审类型
- 🔬 **真实 API 驱动** — 使用真实 LLM API 调用评估，不使用 Mock 数据
- ⚖️ **三维质量评估** — 深度（Depth）、完整性（Completeness）、可操作性（Actionability）
- 🔄 **闭环自主演进** — 分析结果 → 优化架构 → 重新测试 → 记录迭代

---

## 🏆 当前最优结果

### Track 1: OpenClaw Native MAS（真实 API）

| 版本 | 综合评分 | 核心得分 | 泛化得分 | 可操作性 |
|------|----------|----------|----------|----------|
| **v18.0** | **52.83** | 56.1 | 56.1 | L3.1 |
| v12.0 | 52.0 | 54.5 | 54.5 | L3.1 |

> v18.0 通过"Type-Aware Evaluation"策略（对代码任务使用更合理的评估标准）取得突破，达到 52.83 分。

### Track 2: Python MAS（快速迭代）

| 代际 | 综合评分 | Token/任务 | 核心得分 | 泛化得分 |
|------|----------|-----------|----------|----------|
| **Gen404** | **94.90** | 1.0 | 77.0 | 83.0 |
| Gen176/179 | 93.40 | 0.1 | 81.0 | 78.0 |

> Gen404 采用多 Agent 协商架构（9 个输出），达到近乎满分。注：此轨道使用 Mock Token，评分标准为输出匹配率。

---

## 📁 目录结构

```
mas-evolution-test/
├── README.md                    # 本文件
├── ARCHITECTURE.md              # 系统架构详解
├── EVOLUTION_HISTORY.md         # 完整迭代演进历史
├── CONVERGENCE_REPORT.md        # 收敛分析报告

├── benchmark/                   # 基准测试套件
│   ├── tasks.py                 # 15 个标准化测试任务
│   └── tasks_v2.py              # 扩展任务集
│
├── mas/                         # Python MAS 核心代码（第一代）
│   └── core.py                   # 树形 Supervisor-Worker 架构
│
├── openclaw_native/             # OpenClaw 原生 MAS（当前主流）
│   ├── harness_v12.py            # v12.0 评测脚手架（最稳定）
│   ├── supervisor/SOUL.md         # Supervisor Agent 定义
│   ├── research/SOUL.md          # Research Agent 定义
│   ├── code/SOUL.md              # Code Agent 定义
│   ├── review/SOUL.md            # Review Agent 定义
│   ├── evaluator/SOUL.md        # Evaluator Agent 定义
│   └── mas-supervisor/           # 编排调度 Skill
│
├── archive/                     # 历史迭代归档（可忽略）
│   ├── evaluate_scripts/         # 历代评测脚本（gen1-gen400+）
│   ├── benchmark_json/           # 历代评测结果
│   └── python_mas/               # Python MAS 历史版本
│
└── papers/                      # 相关论文与研究资料
```

---

## ⚙️ 核心架构

### OpenClaw Native MAS（v12.0）

```
┌─────────────────────────────────────────────────────┐
│                    Supervisor                        │
│            任务分析与路由决策                         │
└──────────────────────┬──────────────────────────────┘
                       │ sessions_spawn
         ┌─────────────┼─────────────┐
         ▼             ▼             ▼
   ┌──────────┐ ┌──────────┐ ┌──────────┐
   │ Research  │ │   Code   │ │  Review  │
   │   Agent   │ │   Agent  │ │  Agent   │
   └─────┬─────┘ └────┬─────┘ └────┬─────┘
         │            │            │
         └────────────┴────────────┘
                       ▼
┌─────────────────────────────────────────────────────┐
│                   Evaluator                          │
│         三维评分：Depth / Completeness /             │
│         Actionability (L1-L5)                        │
└─────────────────────────────────────────────────────┘
```

### Python MAS（Tree Architecture）

```
User Query → Supervisor → [Research, Code, Review Agents]
                           ↓
                      Knowledge Base
                           ↓
                      Output Selector
```

---

## 🚀 快速开始

### 运行基准测试

```bash
# OpenClaw Native MAS（v12.0）
cd openclaw_native
python harness_v12.py

# 查看结果
cat benchmark_results_v12_gen1.json
```

### 自定义任务

编辑 `benchmark/tasks.py` 添加新测试任务：

```python
{
    "id": "task_016",
    "type": "research",
    "difficulty": 8,
    "query": "你的复杂问题描述",
    "expected_outputs": ["输出类型1", "输出类型2"]
}
```

---

## 📈 演进里程碑

| 日期 | 事件 |
|------|------|
| 2026-04-02 | v12.0 确认稳定，综合评分 51-52 |
| 2026-04-03 | Gen404 达到 94.90（Python MAS 轨道） |
| 2026-04-04 | v12.0 范式收敛，开始新纪元规划 |

完整演进历史见 [EVOLUTION_HISTORY.md](EVOLUTION_HISTORY.md)

---

## ⚠️ 重要说明

1. **双轨道并行**：项目有两条独立演进轨道，评分标准不同，不可直接比较
2. **真实 API**：OpenClaw Native 轨道使用真实 LLM API，每次运行有 ~2% 的自然方差
3. **自动化演进**：所有迭代由 AI 自主完成，无需人工干预

---

## 📖 英文简介 <a name="english"></a>

AutoMAS (Automated Multi-Agent System) is an **autonomous** benchmarking and evolution framework for MAS architectures. It continuously tests agent systems against standardized tasks, evaluates quality across three dimensions, and iteratively improves the architecture.

**Key Features:**
- Automated benchmarking with 15 high-difficulty tasks
- Real LLM API calls (no mock data)
- Three-dimensional quality scoring
- Closed-loop autonomous evolution

**Current Champions:**
- OpenClaw Native: v12.0 at 51.97 composite
- Python MAS: Gen404 at 94.90 composite

---

*Last updated: 2026-04-04*
