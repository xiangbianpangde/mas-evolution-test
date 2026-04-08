# Google Cloud: Agentic AI Design Patterns

> 来源: [Google Cloud Architecture Center](https://docs.cloud.google.com/architecture/choose-design-pattern-agentic-ai-system)
> 日期: 2025-10

---

## 单 Agent 系统

使用 AI 模型 + 工具集 + 系统提示词自主处理请求。

**适用场景**:
- 多步骤任务
- 需要访问外部数据
- 早期开发推荐从单 Agent 开始

**问题**:
- 工具过多时性能下降
- 任务复杂度增加时延迟上升

---

## 多 Agent 系统

核心原则：分解大目标为小子任务，分配给专用 Agent。

---

## 5+1 种多 Agent 模式

### 1. Sequential Pattern (顺序模式)

**结构**: Agent A → Agent B → Agent C → ...

**特点**:
- 预定义线性顺序
- 输出直接传递给下一个
- 无需 AI 模型参与编排

**适用**: 固定流程，如数据处理管道

**缺点**: 缺乏灵活性

---

### 2. Parallel Pattern (并行模式)

**结构**: 
```
        → Agent A ──┐
Task ──→        ├──→ Synthesizer
        → Agent B ──┘
```

**特点**:
- 多个 Agent 同时执行
- Fan-out 到多个专家
- 收集结果进行综合

**适用**: 多源数据收集、多角度分析

**缺点**: 成本增加、结果综合复杂

---

### 3. Loop Pattern (循环模式)

**结构**: Agent A → Agent B → [检查退出条件] → 循环/退出

**特点**:
- 迭代直到满足终止条件
- 最大迭代次数或状态检测
- 预定义逻辑，无 AI 模型编排

**适用**: 迭代改进、自纠正

**缺点**: 可能有死循环风险

---

### 4. Review & Critique Pattern (评审模式)

**结构**: Generator → Critic → [通过? 否→Generator]

**特点**:
- 两个专用 Agent
- Generator 产生内容
- Critic 评估是否符合标准
- 可以多轮迭代

**适用**: 代码审核、内容质量保证

**缺点**: 延迟增加、成本上升

---

### 5. Iterative Refinement Pattern (迭代优化模式)

**结构**: Agent → 评审 → 修改 → [未达标?] → 循环

**特点**:
- 逐步改进输出
- 存储在 session state
- 直到达到质量阈值或最大迭代

**适用**: 复杂生成任务、代码调试、创意写作

**缺点**: 延迟和成本累积、需精心设计退出条件

---

### 6. Coordinator Pattern (协调器模式)

**结构**: Coordinator → 分解任务 → 分发给专门 Agent

**特点**:
- 使用 AI 模型动态路由
- 自适应编排
- 运行时决定执行顺序

**适用**: 自动化结构化业务流程

**缺点**: 比单 Agent 更多模型调用

---

### 7. Hierarchical Task Decomposition Pattern (层级任务分解)

**结构**: Root Agent → Level 1 Agent → Level 2 Agent → ... → Worker Agent

**特点**:
- 多级层次结构
- 顶层分解任务
- 层层下发直到可执行

**适用**: 模糊开放问题、需要多步推理

**缺点**: 架构复杂、需要精心设计层级

---

## 模式选择指南

| 模式 | 复杂度 | 成本 | 灵活性 | 适用场景 |
|------|--------|------|--------|---------|
| Sequential | 低 | 低 | 低 | 固定流程 |
| Parallel | 中 | 中 | 低 | 多源收集 |
| Loop | 中 | 中 | 中 | 自纠正 |
| Review & Critique | 中 | 中高 | 中 | 质量保证 |
| Iterative Refinement | 中 | 中高 | 中 | 渐进改进 |
| Coordinator | 高 | 高 | 高 | 动态路由 |
| Hierarchical | 高 | 高 | 高 | 复杂分解 |

---

## Context Engineering

多 Agent 系统需要专门管理信息流：
- 隔离特定 Agent 的上下文
- 跨多步持久化信息
- 压缩大量数据提高效率

---

## 对 AutoMAS 的启示

### 当前使用的模式

| 模式 | 我们的实现 |
|------|----------|
| Review & Critique | Gen 任务：Generator → Evaluator |
| Loop | 自反射机制 |
| Coordinator | Supervisor 分解任务 |

### 可改进的方向

1. **Parallel Pattern**: Core 任务可以并行执行
2. **Hierarchical**: 更清晰的层级分解
3. **Coordinator**: 更好的动态路由

---

## 原文关键原则

> "If you're early in your agent development, we recommend that you start with a single agent."

> "Multi-agent patterns provide a modular design that can improve the scalability, reliability, and maintainability of the overall system."

---

*最后更新: 2026-04-07*
