# OpenClaw Native Harness - v6.0 防作弊架构

## 核心架构

```
┌─────────────────────────────────────────────────────────┐
│                    Harness v6.0                          │
│                   防作弊评测架构                          │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Task → [Executor Agent] → 真实输出（无 expected 泄漏）  │
│                    ↓                                    │
│          [Evaluator Agent] → 独立评分                    │
│          （不知道 expected，仅评估内容质量）               │
│                    ↓                                    │
│           Quality Score + Token 统计                     │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## 防作弊机制

| 机制 | 说明 |
|------|------|
| **分离执行** | Executor 和 Evaluator 完全分离 |
| **信息隔离** | Executor 看不到 expected outputs |
| **行为审计** | 检测异常短延迟（<5秒）+长输出 |
| **独立评分** | Evaluator 不知道正确答案 |

## Benchmark 结果 v6.0

| 指标 | 数值 |
|------|------|
| **综合评分** | 45.00 |
| 核心任务质量分 | 50.0 |
| 泛化任务质量分 | 50.0 |
| Executor Token | 30,582 |
| Evaluator Token | 7,680 |
| 平均延迟 | 41.2秒/任务 |
| 可疑检测 | 0 个 |

## 发现的问题

1. **Evaluator 区分度不足**: 所有任务统一给 50 分
2. **评分维度单一**: 只有整体质量分
3. **需要多维度评估**: 技术深度/完整性/可执行性分离

## 下一步进化方向

- 改进 Evaluator prompt，引入多维度评分
- 添加更细粒度的子评分（技术准确性、完整性、可操作性）
- 考虑引入外部知识库进行事实核查

## 文件结构

```
openclaw_native/
├── SOUL.md                    # Agent 定义
├── evaluator/SOUL.md          # Evaluator Agent
├── research/SOUL.md          # Research Agent
├── code/SOUL.md             # Code Agent
├── review/SOUL.md           # Review Agent
├── mas-supervisor/
│   └── skills/mas-orchestrator/
│       ├── SKILL.md
│       └── scripts/
│           └── harness_v6.py  # 防作弊 Harness
└── benchmark_results_v6_gen1.json
```

---

*Harness v6.0 - Anti-Cheat Architecture*
