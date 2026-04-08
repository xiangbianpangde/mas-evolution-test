# 📊 Experiments - 实验文件类型说明

> 记录所有实验文件的类型、格式、用途和命名规范

---

## 📋 目录

- [文件类型总览](#文件类型总览)
- [Benchmark Results](#benchmark-results)
- [Evolution Logs](#evolution-logs)
- [Checkpoints](#checkpoints)
- [Harnesses](#harnesses)
- [Task Definitions](#task-definitions)
- [命名规范](#命名规范)

---

## 📁 文件类型总览

| 文件夹 | 文件类型 | 数量 | 主要用途 |
|--------|----------|------|----------|
| `results/benchmarks/` | `benchmark_results_v*.json` | ~80 | 基准测试评分 |
| `results/benchmarks/` | `results_v*.txt` | ~10 | 文本摘要 |
| `results/evolution/` | `*.log` | ~10 | 演进过程日志 |
| `results/evolution/` | `history.json` | 1 | 演进历史聚合 |
| `results/benchmarks/checkpoints/` | `*_checkpoint.json` | ~5 | 断点续算状态 |
| `src/native/harness/` | `harness_v*.py` | ~20 | 评测脚本源码 |
| `src/benchmark/` | `tasks*.py` | 2 | 任务定义 |

---

## 📊 Benchmark Results <a name="benchmark-results"></a>

### JSON 格式结果

**位置**: `results/benchmarks/benchmark_results_*.json`

**典型结构**:
```json
{
  "version": "v31.0",
  "gen": "gen1",
  "timestamp": "2026-04-04T20:32:57",
  "composite": 76.22,
  "core": {
    "score": 79.2,
    "core_001": 82.0,
    "core_002": 85.0,
    "core_003": 58.0,
    "core_004": 72.0,
    "core_005": 87.0,
    "core_006": 68.0,
    "core_007": 65.0,
    "core_008": 78.0,
    "core_009": 82.0,
    "core_010": 50.0
  },
  "gen": {
    "score": 81.0,
    "gen_001": 85.0,
    "gen_002": 80.0,
    "gen_003": 82.0,
    "gen_004": 78.0,
    "gen_005": 80.0
  },
  "actionability": {
    "score": "L4.13",
    "level": 4.13
  },
  "config": {
    "tokens": 5000,
    "max_strategy": "MAX-2",
    "temperature": 0.7
  },
  "task_count": 15,
  "task_type": "tasks_v2.py"
}
```

### 文本格式摘要

**位置**: `results/benchmarks/results_v*.txt`

**典型内容**:
```
v31.0 Results Summary
=====================
Composite: 76.22
Core: 79.2 | Gen: 81.0 | Actionability: L4.13

Core Tasks:
  core_001: 82.0 | core_002: 85.0 | core_003: 58.0
  core_004: 72.0 | core_005: 87.0 | core_006: 68.0
  ...

Gen Tasks:
  gen_001: 85.0 | gen_002: 80.0 | gen_003: 82.0
  ...

Config: 5000 tokens, MAX-2, temp=0.7
Runtime: 2026-04-04 20:32:57 CST
```

### 演进中间结果

**位置**: `results/benchmarks/test_results_v*.md`

**典型结构**:
```markdown
# Test Results v32

## Run 1 (2026-04-04 20:34:45)
| Task | Score |
|------|-------|
| core_001 | 82.0 |
| ... |

## Run 2 (2026-04-04 20:45:12)
| Task | Score |
|------|-------|
| core_001 | 85.0 |
| ... |
```

---

## 🔄 Evolution Logs <a name="evolution-logs"></a>

### Benchmark 运行日志

**位置**: `results/evolution/v*_benchmark*.log`

**典型内容**:
```log
[2026-04-08 18:52:00] Starting v38 benchmark
[2026-04-08 18:52:01] Loading tasks from tasks_v2.py
[2026-04-08 18:52:02] Task 1/15: core_001 research
[2026-04-08 18:53:15] Task 1 COMPLETED: 82.0
[2026-04-08 18:53:16] Task 2/15: core_002 research
[2026-04-08 18:54:30] Task 2 COMPLETED: 85.0
...
[2026-04-08 19:45:00] v38 benchmark COMPLETED: 72.16
```

### 演进历史聚合

**位置**: `results/evolution/history.json`

**典型结构**:
```json
{
  "evolution_id": "evo_001",
  "started": "2026-04-08T18:20:00",
  "generations": [
    {
      "generation": 1,
      "strategy": "v32_v31_clone",
      "tokens": 5000,
      "composite": 51.74,
      "status": "below_baseline",
      "notes": "API instability caused degradation"
    }
  ],
  "current_best": {
    "version": "v31.0",
    "composite": 76.22
  }
}
```

---

## 💾 Checkpoints <a name="checkpoints"></a>

### 断点续算状态

**位置**: `results/benchmarks/checkpoints/*_checkpoint.json`

**触发条件**: 任务运行中断，需要从断点恢复

**典型结构**:
```json
{
  "version": "v38",
  "checkpoint_time": "2026-04-08T19:30:00",
  "completed_tasks": [
    {"id": "core_001", "score": 82.0, "status": "done"},
    {"id": "core_002", "score": 85.0, "status": "done"},
    {"id": "core_003", "score": 58.0, "status": "done"}
  ],
  "pending_tasks": [
    {"id": "core_004", "status": "pending"},
    {"id": "core_005", "status": "pending"}
  ],
  "current_run": 1,
  "max_runs": 3,
  "best_scores": {
    "core_001": 82.0,
    "core_002": 85.0,
    "core_003": 58.0
  }
}
```

---

## ⚙️ Harnesses <a name="harnesses"></a>

### 评测脚本

**位置**: `src/native/harness/harness_v*.py`

**命名规范**:
| 类型 | 格式 | 示例 |
|------|------|------|
| 主版本 | `harness_vXX.py` | `harness_v31.py` |
| 精确版本 | `harness_vXX_0.py` | `harness_v31_0.py` |
| 实验版本 | `harness_vXX_e.py` | `harness_v31_e.py` |
| 演进生成 | `harness_evo_XXX.py` | `harness_evo_001.py` |

**核心配置参数**:
```python
# 必需配置
MAX_TOKENS = 5000           # 输出 token 上限
TEMPERATURE = 0.7           # 随机性控制
MAX_RUNS = 2                # MAX-策略运行次数
SELF_REFLECTION = "selective"  # none | selective | all

# Agent 配置
RESEARCH_TOKENS = 5000
CODE_TOKENS = 5000
REVIEW_TOKENS = 3500
```

### 历史版本

**位置**: `src/native/harness_old/`

包含从 v2.0 到 v36 的所有历史版本，便于回溯和对比。

---

## 📝 Task Definitions <a name="task-definitions"></a>

### 标准任务集

**位置**: `src/benchmark/tasks.py`

**字段说明**:
| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | string | 唯一标识 (如 `core_001`) |
| `type` | enum | `research` \| `code` \| `review` |
| `difficulty` | int | 难度等级 1-10 |
| `query` | string | 任务描述 |
| `expected_outputs` | list | 期望输出类型 |
| `evaluation_criteria` | dict | 评分标准 |

**示例**:
```python
{
    "id": "core_001",
    "type": "research",
    "difficulty": 8,
    "query": "分析为什么系统在高并发下出现性能下降...",
    "expected_outputs": [
        "问题诊断",
        "深度分析",
        "具体方案",
        "数字证据",
        "验证方法"
    ],
    "evaluation_criteria": {
        "depth": ["诊断准确性", "分析深度"],
        "completeness": ["覆盖全面性", "细节完整性"],
        "actionability": ["可执行性", "实用性"]
    }
}
```

### 扩展任务集

**位置**: `src/benchmark/tasks_v2.py`

包含额外的泛化测试任务，用于评估系统的 generalization 能力。

---

## 📏 命名规范 <a name="naming"></a>

### 版本命名

```
v<MAJOR>.<MINOR>[-<PATCH>]

示例:
  v31.0    - 主版本
  v31.1    - 同一版本的变体
  v31_0    - 下划线版本（用于文件名）
```

### 文件命名模板

| 文件类型 | 模板 | 示例 |
|----------|------|------|
| Benchmark 结果 | `benchmark_results_v<VERSION>_gen<GEN>.json` | `benchmark_results_v31_0_gen1.json` |
| 文本摘要 | `results_v<VERSION>.txt` | `results_v31.txt` |
| 运行日志 | `v<VERSION>_benchmark.log` | `v38_benchmark.log` |
| Checkpoint | `v<VERSION>_checkpoint.json` | `v38_checkpoint.json` |

### 任务 ID 命名

| 前缀 | 类型 | 说明 |
|------|------|------|
| `core_XXX` | Core | 核心测试任务 (001-010) |
| `gen_XXX` | Generalization | 泛化测试任务 (001-005) |

---

## 📊 文件保留策略

| 文件类型 | 保留期限 | 说明 |
|----------|----------|------|
| benchmark_results_*.json | 永久 | 核心数据 |
| results_v*.txt | 永久 | 快速参考 |
| *_checkpoint.json | 实验结束后删除 | 仅用于断点恢复 |
| *_benchmark.log | 6个月 | 调试参考 |
| history.json | 永久 | 演进聚合 |

---

*最后更新: 2026-04-08 · 由 Archaeus Agent 维护*
