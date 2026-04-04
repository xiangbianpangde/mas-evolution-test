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
| **v23.0** | **58.30** | 54.4 | 68.2 | L3.1 |
| v33.0 | 56.57 | 57.3 | 61.6 | L3.2 |
| v26.0 | 56.91 | 53.0 | 66.8 | L3.1 |

> v23.0 通过"自适应格式选择"策略（根据任务类型自适应输出格式）取得突破，达到 58.30 分。
> **注意**：真实 API 存在约 8% 的自然方差。

### 🆕 PARADIGM v2: Self-Reflection Architecture (2026-04-05)

| 版本 | 综合评分 | 核心得分 | 泛化得分 | 状态 |
|------|----------|----------|----------|------|
| v2.0 | **54.64** | 50.0 | 65.2 | ✅ Completed |
| v3.0 | TBD | TBD | TBD | 🚀 Running... |

> v2 范式核心创新：**自我批判循环**。单个智能体生成初稿 → 自我批判弱点 → 改进输出。
> 对比 v1 的多智能体投票（v36: 43.60），自我反思在 Gen 任务上提升显著（44.8→65.2）。

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
├── EVOLUTION_HISTORY.md         # 完整迭代演进历史（v20-v35）
├── CONVERGENCE_REPORT.md        # 收敛分析报告

├── benchmark/                   # 基准测试套件
│   ├── tasks.py                 # 15 个标准化测试任务
│   └── tasks_v2.py              # 扩展任务集
│
├── mas/                         # Python MAS 核心代码（第一代）
│   └── core.py                   # 树形 Supervisor-Worker 架构
│
├── openclaw_native/             # OpenClaw 原生 MAS（当前主流）
│   ├── harness_v23.py            # v23.0 评测脚手架（最稳定/最佳）
│   ├── harness_v33.py            # v33.0 评测脚手架
│   └── ...
│
├── archive/                     # 历史迭代归档
│   ├── evaluate_scripts/         # 历代评测脚本（gen1-gen400+）
│   ├── benchmark_json/           # 历代评测结果
│   └── python_mas/              # Python MAS 历史版本
│
└── papers/                      # 相关论文与研究资料
```

---

## ⚙️ 核心架构

### OpenClaw Native MAS（v23.0）

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

### 自适应格式选择（v23 核心创新）

根据任务类型自动选择最优输出格式：
- **research**: 问题诊断 → 深度分析 → 具体方案 → 数字证据 → 验证方法
- **code**: 架构简图 → 核心代码 → 测试用例 → 配置说明
- **review**: 风险矩阵 → 影响分析 → 缓解步骤 → 优先级 → 验证方法

---

## 🚀 快速开始

### 运行基准测试

```bash
# OpenClaw Native MAS（v23.0 - 最佳版本）
cd openclaw_native
python harness_v23.py

# 查看结果
cat benchmark_results_v23_gen1.json
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

## 📈 演进里程碑（v20-v35）

| 日期 | 版本 | 综合评分 | 策略 |
|------|------|----------|------|
| 2026-04-04 | v23.0 | **58.30** | 自适应格式选择 |
| 2026-04-04 | v26.0 | 56.91 | 回退到 v23 框架 |
| 2026-04-04 | v33.0 | 56.57 | 极简 prompt |
| 2026-04-04 | v35.0 | 53.40 | 改进的极简 prompt |

---

## ⚠️ 重要说明

1. **双轨道并行**：项目有两条独立演进轨道，评分标准不同，不可直接比较
2. **真实 API 方差**：OpenClaw Native 轨道使用真实 LLM API，每次运行有 **~8%** 的自然方差
3. **自动化演进**：所有迭代由 AI 自主完成，无需人工干预
4. **范式收敛**：v23 的框架已验证为当前最优，需要新范式突破

---

## 📖 英文简介 <a name="english"></a>

AutoMAS (Automated Multi-Agent System) is an **autonomous** benchmarking and evolution framework for MAS architectures. It continuously tests agent systems against standardized tasks, evaluates quality across three dimensions, and iteratively improves the architecture.

**Key Features:**
- Automated benchmarking with 15 high-difficulty tasks
- Real LLM API calls (no mock data)
- Three-dimensional quality scoring
- Closed-loop autonomous evolution

**Current Champions:**
- OpenClaw Native: v23.0 at **58.30** composite (v1 paradigm)
- OpenClaw Native: v2.0 at **54.64** composite (v2 paradigm - testing)

**Paradigm Status:**
- **v1 (v6-v36)**: CONVERGED at v36 (43.60) - multi-agent voting failed
- **v2 (Self-Reflection)**: IN TESTING - v2.1 hybrid running now

---

*Last updated: 2026-04-04*
