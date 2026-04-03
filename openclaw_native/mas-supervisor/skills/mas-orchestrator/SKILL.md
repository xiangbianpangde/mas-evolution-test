---
name: mas-orchestrator
description: OpenClaw Native MAS Orchestrator - 调度多 Agent 协作系统。当需要执行复杂任务、跨领域分析、代码生成、架构评审等任务时，使用此 Skill 进行多 Agent 协作。Supervisor 会分析任务类型，通过 sessions_spawn 唤起专业 Worker Agent，聚合结果并评估质量。
---

# MAS Orchestrator Skill

## 概述

这是 OpenClaw 原生 MAS（多智能体系统）编排器。通过 SOUL.md 定义的 Agent 角色，Supervisor 协调多个专业 Worker 完成复杂任务。

## 核心架构

```
User Query → Supervisor → sessions_spawn → Research/Code/Review Agent
                ↓                              ↓
            Quality Check ← ← ← ← ← ← ← Results
                ↓
        Final Output + Score
```

## Agent 角色

| Agent | SOUL | 职责 | 输出类型 |
|-------|------|------|---------|
| supervisor | mas_agents/supervisor/SOUL.md | 任务调度+结果聚合 | 调度决策 |
| research | mas_agents/research/SOUL.md | 技术调研分析 | 技术分析/代码示例/benchmark |
| code | mas_agents/code/SOUL.md | 代码实现 | 完整代码/测试用例/架构图 |
| review | mas_agents/review/SOUL.md | 架构评审 | 风险列表/缓解方案/优先级 |

## 执行流程

### Step 1: 任务分析

分析 query，识别：
- `task_type`: research | code | review
- `complexity`: simple | medium | complex
- `required_outputs`: 需要的输出类型

### Step 2: Agent 调度

根据 task_type 选择 Agent：

```python
if task_type == "research":
    target = "research_agent"
elif task_type == "code":
    target = "code_agent"  
elif task_type == "review":
    target = "review_agent"
else:
    # 复杂任务：并行调度多个 Agent
    targets = ["research_agent", "code_agent"]
```

使用 `sessions_spawn(runtime="subagent")` 唤起 Worker：

```json
{
  "task": "执行任务: {query}",
  "runtime": "subagent",
  "agentId": "research_agent",
  "mode": "run",
  "sandbox": "inherit"
}
```

### Step 3: 结果聚合

收集所有 Worker 响应，整合为统一输出。

### Step 4: 质量评估

调用 Evaluator Agent 进行真实 Benchmark 评分。

## Benchmark 任务集

### 核心任务 (10个)

| ID | 类型 | 难度 | Query |
|----|------|------|-------|
| core_001 | research | 8 | 分析 Transformer 注意力机制优化方案 |
| core_002 | code | 9 | 实现 TB 级日志解析器 |
| core_003 | research | 7 | 对比 RAG 与 Fine-tuning 成本效益 |
| core_004 | code | 8 | 设计分布式限流系统 |
| core_005 | review | 6 | 审查微服务架构风险 |
| core_006 | research | 9 | 调研 LLM 数学推理最新进展 |
| core_007 | code | 7 | 实现热更新插件框架 |
| core_008 | research | 8 | 分析向量数据库选型策略 |
| core_009 | code | 9 | 实现简化版 Raft 算法 |
| core_010 | review | 7 | 架构评估与优化建议 |

### 泛化任务 (5个)

| ID | 类型 | Query |
|----|------|-------|
| gen_001 | research | 分析量子计算在金融领域的应用 |
| gen_002 | code | 实现联邦学习梯度聚合 |
| gen_003 | review | 评估零知识证明系统风险 |
| gen_004 | research | 调研脑机接口最新进展 |
| gen_005 | code | 设计去中心化身份认证系统 |

## 评分体系

### 字典序评估权重

1. **复杂任务解决率** (60%): 核心任务平均得分
2. **泛化性跨度** (30%): 泛化任务平均得分
3. **Token 效率** (10%): 质量 / Token 消耗

### 评分公式

```
composite_score = 0.6 * core_score + 0.3 * gen_score + 0.1 * efficiency_score
```

### 防作弊规则

- Token 统计必须来自 API 真实响应
- 质量评估必须基于实际输出内容
- 禁止 Mock 数据或硬编码分数

## 会话管理

### 短任务 (one-shot)

```json
{
  "task": "任务描述",
  "runtime": "subagent",
  "mode": "run"
}
```

### 长任务 (persistent)

```json
{
  "task": "任务描述",
  "runtime": "subagent",
  "mode": "session",
  "sandbox": "inherit"
}
```

## 错误处理

- Worker 超时 → 最多重试 2 次
- 质量分数 < 70 → 重新调度
- API 失败 → 记录错误，返回部分结果

## 输出规范

最终输出必须包含：

```json
{
  "task_id": "core_001",
  "task_type": "research",
  "outputs": ["技术分析", "代码示例"],
  "quality_score": 85,
  "tokens_used": 1234,
  "latency_ms": 2341,
  "agents_invoked": ["research_agent"],
  "success": true
}
```
