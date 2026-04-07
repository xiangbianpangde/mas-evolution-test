# Multi-Agent Orchestration Patterns

## 复杂度层级

| Level | Description | When to use |
|-------|-------------|-------------|
| **L0** | Direct model call | 分类/总结/翻译，单步任务 |
| **L1** | Single agent + tools | 同域多态请求，需要动态工具 |
| **L2** | Multi-agent orchestration | 跨域/跨功能/需要并行专业化 |

> 先评估是否需要多 Agent，避免过度设计

---

## 核心编排模式

### 1. 顺序编排 (Sequential)
```
Input → Agent1 → Agent2 → ... → AgentN → Result
```
**用途**: 阶段有依赖，逐步细化 (draft→review→polish)
**注意**: 不适合并行任务

### 2. 编排器-工作者模式 (Orchestrator-Worker)
```
Orchestrator
├── 分解任务
├── 分发给 Worker
├── 收集结果
└── 合成输出

Worker (专业化)
├── Research Agent
├── Code Agent
├── Review Agent
└── 只执行，不做战略决策
```
**优点**: 分离关注点，单一控制点
**风险**: Orchestrator 是瓶颈和单点故障

### 3. 专家小组模式 (Specialist Panel - 并行)
```
 Dispatcher → [Agent1] ─┐
              → [Agent2]─┼→ Synthesiser → Result
              → [Agent3]─┘
```
**用途**: 同时处理多维度 (价格分析+情感分析+新闻监控)
**优点**: 延迟 = 最长步骤，而非累加
**风险**: 综合比看起来难，需要处理矛盾

### 4. 评审链模式 (Review Chain)
```
AgentA → [Review AgentB] → 通过? → AgentA 重做 : 继续
                              ↓
                         人工审核 (必要时)
```
**用途**: 高风险输出 (客户-facing/财务/法律/生产代码)
**注意**: 不是每个步骤都需要评审

### 5. 共享黑板模式 (Shared Blackboard)
```
Agent1 ─┐
Agent2 ─┼─→ 共享结构化状态 ──→ AgentN
Agent3 ─┘        ↓
           所有 Agent 可读写
```
**用途**: 复杂工作流中多个 Agent 需要访问同一信息
**vs 消息队列**: 是持久化结构化文档，不是队列

### 6. 共识投票模式 (Consensus Voting)
```
同一任务 → Agent1 ─┐
                 ├─→ 投票/共识 → 结果
同一任务 → Agent2 ─┘
```
**用途**: 关键决策需要多个视角验证

### 7. 故障转移模式 (Fault-Tolerant Handoffs)
```
Agent1 → 失败? → 转移给 Agent2
              → 失败? → 转移给 Agent3
```
**用途**: 关键任务不能失败

---

## Agent 协作失败模式

| 失败模式 | 表现 | 解决方案 |
|---------|------|---------|
| **协调混乱** | Agent 互相打断/重复/矛盾 | 明确 handoff 协议 |
| **上下文污染** | Agent A 的错误悄悄影响 Agent B | 隔离 + 验证 |
| **调试噩梦** | 无法追踪谁做了什么决策 | 完整执行 trace |
| **脆弱交接** | Agent 间的接缝是最常见故障点 | 明确接口 + 测试 |

---

## 编排层职责

> "编排层将自主组件转化为有凝聚力、目标导向的集体。没有编排，高度capable的agents有重复努力、逻辑不一致或偏离系统目标的无界自主权风险。"

---

## 适用本项目的模式

**当前**: Orchestrator-Worker (Supervisor 分解任务 → Workers 执行)
**改进方向**:
- Review Chain 用于评审任务
- Specialist Panel 用于 Gen tasks (research/code 并行)
- Shared Blackboard 用于状态管理
