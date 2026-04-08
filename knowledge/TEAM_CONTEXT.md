# TEAM_CONTEXT.md - 团队上下文

## AutoMAS 团队架构

```
┌─────────────────────────────────────────────────────────────────┐
│                     Supervisor (主控)                            │
│            任务分析 · 路由决策 · 结果整合                         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼ sessions_spawn
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│   Research   │      │     Code     │      │    Review    │
│    Agent     │      │    Agent     │      │    Agent     │
└──────────────┘      └──────────────┘      └──────────────┘
        │                     │                     │
        └─────────────────────┴─────────────────────┘
                                │
                                ▼
                    ┌──────────────────────┐
                    │      Evaluator       │
                    │   三维质量评估       │
                    └──────────────────────┘
```

---

## Agent 角色与能力

### 1. Supervisor (监督者)

| 属性 | 说明 |
|------|------|
| **定位** | 任务入口 + 协调者 |
| **核心能力** | 任务分析、路由决策、结果整合 |
| **SOUL** | `src/native/soul/` 中的 Supervisor 定义 |
| **当前配置** | 5000 tokens |

**职责**：
- 接收原始任务 query
- 分析任务类型 (research/code/review)
- 分解为子任务
- 调用对应 Worker Agent
- 整合最终结果

**协作方式**：
- 通过 `sessions_spawn` 派生 Worker
- 收集 Worker 返回结果
- 传递给 Evaluator

---

### 2. Research Agent (研究 Agent)

| 属性 | 说明 |
|------|------|
| **定位** | 深度研究专家 |
| **核心能力** | 信息检索、分析综合、方案生成 |
| **任务类型** | research 类型任务 |
| **并行度** | 3 workers |

**输出格式**：
```
问题诊断 → 深度分析 → 具体方案 → 数字证据 → 验证方法
```

**质量标准**：
- Depth: 诊断准确性、分析深度
- Completeness: 覆盖全面性、细节完整性
- Actionability: 可执行性、实用性

---

### 3. Code Agent (代码 Agent)

| 属性 | 说明 |
|------|------|
| **定位** | 代码工程专家 |
| **核心能力** | 架构设计、代码实现、测试验证 |
| **任务类型** | code 类型任务 |
| **并行度** | 3 workers |
| **禁忌** | ⚠️ 禁止自反射（已验证会导致灾难） |

**输出格式**：
```
架构简图 → 核心代码 → 测试用例 → 配置说明
```

**质量标准**：
- Depth: 架构合理性、代码质量
- Completeness: 功能完整性、边界处理
- Actionability: 可运行性、可测试性

---

### 4. Review Agent (评审 Agent)

| 属性 | 说明 |
|------|------|
| **定位** | 评审改进专家 |
| **核心能力** | 风险识别、影响分析、改进建议 |
| **任务类型** | review 类型任务 |
| **并行度** | 3 workers |

**输出格式**：
```
风险矩阵 → 影响分析 → 缓解步骤 → 优先级 → 验证方法
```

**质量标准**：
- Depth: 风险识别准确性
- Completeness: 影响面覆盖
- Actionability: 缓解方案可行性

---

### 5. Evaluator (评估器)

| 属性 | 说明 |
|------|------|
| **定位** | 质量裁判 |
| **核心能力** | 三维评分、Actionability 判断 |
| **评估维度** | Depth × Completeness × Actionability |
| **评分量表** | L1-L5 |

**评分公式**：
```
Composite = (Core × 0.5 + Gen × 0.5) × ActionabilityMultiplier
```

---

## Agent 间协作机制

### 任务流程

```
1. User Query
       │
       ▼
2. Supervisor 分析任务类型
       │
       ▼
3. sessions_spawn(Research/Code/Review Agent)
       │
       ├──▶ Research Agent (3 workers)
       ├──▶ Code Agent (3 workers)
       └──▶ Review Agent (3 workers)
       │
       ▼
4. 收集所有 Worker 结果
       │
       ▼
5. Supervisor 整合结果
       │
       ▼
6. Evaluator 三维评分
       │
       ▼
7. 输出 benchmark 结果
```

### 通信协议

| 通信路径 | 方式 | 内容 |
|----------|------|------|
| Supervisor → Worker | sessions_spawn | 任务描述 + 上下文 |
| Worker → Supervisor | 返回值 | 任务结果 |
| Supervisor → Evaluator | 函数调用 | 原始输出 |
| Evaluator → 文件 | write | JSON 结果 |

### 状态同步

| 状态类型 | 存储位置 | 更新时机 |
|----------|----------|----------|
| 实验进度 | `results/benchmarks/*.json` | 每次运行后 |
| 演进历史 | `results/evolution/history.json` | 每次演进后 |
| 资源状态 | `src/native/evolution_state.json` | 演进循环中 |

---

## 团队能力矩阵

| 能力 | Supervisor | Research | Code | Review | Evaluator |
|------|------------|----------|------|--------|-----------|
| **任务分析** | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐ |
| **深度研究** | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐ |
| **代码实现** | ⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐ |
| **风险评审** | ⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐ |
| **质量评估** | ⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| **系统协调** | ⭐⭐⭐⭐⭐ | ⭐ | ⭐ | ⭐ | ⭐ |

---

## 子 Agent 派生配置

### sessions_spawn 参数

```python
sessions_spawn(
    runtime="acp",        # OpenClaw 运行时
    timeout=120,          # 2分钟超时
    prompt=f"""
    你是一个 {agent_type} Agent。
    任务: {task_description}
    上下文: {context}
    输出要求: {output_format}
    """,
    agent_type=agent_type
)
```

### 并行度配置

| Agent 类型 | 并行 Worker 数 | 总超时 |
|------------|---------------|--------|
| Research | 3 | 6 分钟 |
| Code | 3 | 6 分钟 |
| Review | 3 | 6 分钟 |

---

## 历史版本团队配置

| 版本 | 团队配置 | Composite |
|------|----------|-----------|
| v31.0 🏆 | 5000 tokens, MAX-2 | 76.22 |
| v33.0 | 5000 tokens, MAX-3 | 73.44 |
| v32.0 | 6000 tokens, MAX | 72.22 |
| v37.0 | 扩展自评审 | 69.07 |
| v29.0 | MAX 策略引入 | 67.01 |

---

## 协作教训

| 教训 | 原因 | 后果 |
|------|------|------|
| **代码自反射** | Code Agent 自我评审 | gen 任务灾难 |
| **6000 tokens** | Supervisor 过度分析 | Core 下降 7.6 分 |
| **扩展自评审** | 增加不必要的 Agent | 分数下降 |

---

## 最佳实践

1. **Supervisor 不要过度分析**：5000 tokens 已验证最优
2. **Code Agent 禁止自反射**：Worker 独立工作
3. **使用 MAX 策略**：取多次运行最大值
4. **Worker 并行执行**：3 workers 是最优并行度
5. **Evaluator 独立评分**：不受 Supervisor 影响

---

*Last updated: 2026-04-08*
