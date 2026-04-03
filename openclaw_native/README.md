# OpenClaw Native MAS 架构

## 架构概述

这是基于 OpenClaw 原生框架的多智能体系统（MAS），完全兼容 OpenClaw 的 Agent 生命周期管理。

## 目录结构

```
/root/.openclaw/workspace/mas_agents/
├── supervisor/          # Supervisor Agent SOUL
├── research/             # Research Agent SOUL
├── code/                # Code Agent SOUL
├── review/              # Review Agent SOUL
├── evaluator/           # Evaluator Agent SOUL
└── benchmark_results_native.json  # Benchmark 结果

/root/.openclaw/extensions/mas-supervisor/
└── skills/mas-orchestrator/
    ├── SKILL.md         # 编排器 Skill
    └── scripts/
        └── benchmark_runner.py  # Benchmark 执行器
```

## Agent 角色

| Agent | 职责 | 触发条件 |
|-------|------|---------|
| **Supervisor** | 任务调度+结果聚合 | 主入口 |
| **Research** | 技术调研分析 | task_type=research |
| **Code** | 代码实现生成 | task_type=code |
| **Review** | 架构评审风险分析 | task_type=review |
| **Evaluator** | 性能评估 Benchmark | 定期评估 |

## 执行方式

### 方式 1: 通过 Skill 调用（推荐）

当收到复杂任务时，触发 `mas-orchestrator` Skill：
- Skill 分析任务类型
- 通过 `sessions_spawn` 唤起对应 Worker Agent
- 聚合结果并评分

### 方式 2: 直接运行 Benchmark

```bash
cd /root/.openclaw/extensions/mas-supervisor/skills/mas-orchestrator/scripts
MINIMAX_API_KEY=your_key python3 benchmark_runner.py
```

## 进化机制

### OODA Loop

```
Observe  → 读取 sessions_history / memory
Orient   → 分析当前 SOUL 配置
Decide   → 修改 Agent SOUL / SKILL
Act      → sessions_spawn 新配置
```

### 进化触发条件

- 连续 10 轮提升 < 1%
- 某个维度得分 < 60
- 发现新的架构范式

### 进化操作

1. **修改 SOUL.md**: 调整 Agent 行为指令
2. **修改 SKILL.md**: 调整编排策略
3. **更新 Benchmark**: 增加任务难度
4. **添加新 Agent**: 扩展角色

## 与 Python MAS 的区别

| 维度 | Python MAS | OpenClaw Native MAS |
|------|-----------|---------------------|
| 架构定义 | Python 类 | SOUL.md + SKILL.md |
| 运行环境 | 独立进程 | OpenClaw 运行时 |
| 工具调用 | urllib 硬编码 | OpenClaw 统一工具池 |
| 会话管理 | 自己实现 | sessions_* 原语 |
| 进化粒度 | 类级别 | 配置级别（细粒度） |
| Benchmark | Mock 数据 | 真实 API |
| 评分体系 | 硬编码 | LLM 评估 |

## 下一步

1. 配置 `openclaw.json` 添加 `agents.list[]`
2. 启用 `acp` 配置
3. 运行首次真实 Benchmark
4. 根据结果进化 Agent SOUL
