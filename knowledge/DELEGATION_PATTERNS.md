# Delegation Patterns - Leader 必须掌握的知识

## 核心发现

> "Task decomposition is the linchpin of effective delegation -- getting decomposition wrong cascades failures across the entire agent team."
> — Zylos AI Research

> "41-87% of multi-agent LLM systems fail in production, with 79% of failures rooted in specification and coordination issues rather than technical bugs."

## 三种协调拓扑

### 1. Hierarchical ( Supervisor-Worker )
```
        Supervisor
       /    |    \
   Worker  Worker  Worker
```
**适用**: 复杂、多域任务，需要清晰的责任链
**优点**: 明确的汇报链，易调试，易 specialization
**风险**: 单点故障，瓶颈

### 2. Flat / Peer-to-Peer
```
Agent A <---> Agent B
   ^           ^
   |           |
Agent C <---> Agent D
```
**适用**: 对等协作，无单一权威
**优点**: 无单点故障，弹性好
**风险**: 协调复杂，难以预测

### 3. Supervisor Pattern (推荐)
```
Orchestrator (Supervisor)
  - 接收任务
  - 分解为子任务
  - 分派给专业 Agent
  - 监控进度
  - 验证输出
  - 合成最终响应
```

## 任务分解是关键

### 正确分解 vs 错误分解

**正确分解**:
```
任务 → 子任务A → 子任务B → 子任务C
         ↓           ↓           ↓
       执行        执行        执行
         ↓           ↓           ↓
       验证        验证        验证
         └───────────┴───────────┘
                    ↓
              结果聚合 + 验证
```

**错误分解** (我的问题):
```
任务 → 模糊指令 → 假设完成
```

### 任务分解检查清单

- [ ] 任务是否可独立验证？
- [ ] 子任务是否有清晰的交付标准？
- [ ] 子任务是否有明确的验收条件？
- [ ] 是否有失败处理机制？

## CrewAI 模式参考

### Sequential Process
```
Task A → Task B → Task C
```
适用于：简单、可预测、有依赖的任务

### Hierarchical Process
```
Manager
  ├── Agent A (执行)
  ├── Agent B (执行)
  └── Agent C (验证)
```
适用于：复杂任务，需要协调和验证

## 验证机制设计

### 三层验证

1. **执行时验证** - Agent 自我检查
2. **执行后验证** - Supervisor 验证输出
3. **聚合时验证** - 交叉检查一致性

### 验证方法

| 验证类型 | 方法 |
|----------|------|
| 存在性 | 文件是否存在 |
| 格式 | JSON/YAML schema 验证 |
| 内容 | 关键词、长度、结构 |
| 一致性 | 与历史版本对比 |
| 可审计 | 是否有执行痕迹 |

## 失败模式

### 常见失败

1. **分解错误** - 任务太模糊
2. **上下文泄露** - 信息共享不当
3. **验证缺失** - 假设成功
4. **单点故障** - Supervisor 崩溃

### 缓解措施

- 红undant supervisors
- 超时 fallback 到直接执行
- 明确的错误边界

## 正确的 Leader 模式

### 我应该做的

1. **设计任务分解** - 不是执行任务
2. **设计验证机制** - 不是亲自验证
3. **评估结果** - 不是假设成功
4. **调整分解** - 从失败中学习

### 我不应该做的

1. ~~亲自执行所有任务~~
2. ~~假设 Agent 完成 = 成功~~
3. ~~等用户指出问题~~
4. ~~不做任务分解设计~~

---

*Last updated: 2026-04-09*
