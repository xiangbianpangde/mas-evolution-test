# AutoMAS: Eternal Harness Evolution Engine

## 🚨 PARADIGM SHIFT: Anti-Cheat Harness

**v6.0-v8.0 架构**: 防作弊评测底座，Executor/Evaluator 完全分离

---

## 📊 当前状态 (v8.0 Running)

| 架构版本 | Composite | Core | Gen | Token | 备注 |
|---------|-----------|------|-----|-------|------|
| **v8.0** | TBD | TBD | TBD | TBD | Running - Improved Executor |
| v7.0 | 47.78 | 53.09 | 53.09 | 36.5k | Multi-dim scoring |
| v6.0 | 45.00 | 50.0 | 50.0 | 38.2k | Anti-cheat separation |

## 🎯 v8.0 改进

- Chain-of-Thought reasoning
- 任务结构化指导（Research/Code/Review 各有框架）
- 更详细的输出模板

## 🔬 防作弊架构

```
┌─────────────────────────────────────────────────────────────┐
│                      Harness v6.0+                           │
│                                                             │
│  Task Query                                                 │
│      │                                                      │
│      ▼                                                      │
│  ┌─────────────────────────────────────────────────────┐     │
│  │              EXECUTOR AGENT                         │     │
│  │  - 看不到 expected outputs（防透题）                 │     │
│  │  - 输出真实解答                                      │     │
│  │  - Chain-of-Thought reasoning                       │     │
│  └─────────────────────────────────────────────────────┘     │
│      │                                                      │
│      │  executor_output (only)                           │
│      ▼                                                      │
│  ┌─────────────────────────────────────────────────────┐     │
│  │              EVALUATOR AGENT                         │     │
│  │  - 独立评分，不知道正确答案                           │     │
│  │  - 技术深度/完整性/可操作性                          │     │
│  └─────────────────────────────────────────────────────┘     │
│      │                                                      │
│      ▼                                                      │
│  Quality Score (Anti-Cheat)                                 │
└─────────────────────────────────────────────────────────────┘
```

## 📈 进化历史

| 版本 | 分数 | 改进 |
|------|------|------|
| v5.0 | 75.4 | OpenClaw Native MAS + Real API |
| v6.0 | 45.0 | 防作弊分离 (但评分异常) |
| v7.0 | 47.8 | 多维度评分修复 |
| v8.0 | TBD | Executor 质量提升 |

## 🔍 防作弊规则

1. **Executor 绝不接收 expected outputs**
2. **Evaluator 独立评分，不知道正确答案**
3. **异常秒解(<5s)+长输出 → 标记可疑**
4. **禁止正则匹配/硬编码答案**

## 📁 核心文件

```
openclaw_native/
├── harness_v8.py              # 最新 Harness
├── benchmark_results_v8_*.json # Benchmark 结果
├── supervisor/SOUL.md         # Supervisor Agent
├── research/SOUL.md          # Research Agent
├── code/SOUL.md              # Code Agent
└── review/SOUL.md            # Review Agent
```

---

*AutoMAS v8.0 - Anti-Cheat Harness Architecture*
