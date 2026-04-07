# 📝 Patterns

> 从 sources/ 原文提取的精华模式库

---

## 核心原则

| 原则 | 来源 | 说明 |
|------|------|------|
| **评估器分离** | OpenAI, Anthropic, Martin Fowler | Generator 不评自己 |
| **深度优先** | OpenAI | 一次一个功能 |
| **渐进式披露** | OpenAI, Anthropic | 先摘要后细节 |
| **Keep Quality Left** | Martin Fowler | 尽早发现问题 |

---

## 14种已识别模式

### 评测策略
| 模式 | 成功率 | 说明 |
|------|--------|------|
| 评估器分离 | ✅ 100% | Generator + 独立Evaluator |
| MAX-2 | ✅ 100% | 2次运行取最优 |
| MAX-3 | ❌ 0% | 3次运行反而增加方差 |

### Agent 执行
| 模式 | 来源 | 说明 |
|------|------|------|
| 深度优先 | OpenAI | 大目标分解为小构建块 |
| Review & Critique | Google Cloud | Generator → Critic → 迭代 |
| Sequential | Google Cloud | 预定义线性顺序 |
| Parallel | Google Cloud | 多个子任务同时执行 |
| Loop | Google Cloud | 迭代直到终止条件 |

### 上下文管理
| 模式 | 来源 | 说明 |
|------|------|------|
| 渐进式披露 | OpenAI, Anthropic | 先入口，再深入 |
| Initializer + Worker | Anthropic | 跨session状态传递 |
| Context Engineering | Google Cloud | 多Agent信息流管理 |

### 质量控制
| 模式 | 来源 | 说明 |
|------|------|------|
| Feedforward + Feedback | Martin Fowler | 预防 + 观察纠正 |
| Keep Quality Left | Martin Fowler | 尽早发现问题 |
| Computational vs Inferential | Martin Fowler | 确定性检查 + AI评审 |

---

## 模式关系图

```
单Agent系统
├── 深度优先
├── 渐进式披露
└── 黄金Token Budget

多Agent系统
├── Sequential (线性流程)
├── Parallel (并行执行)
├── Loop (迭代优化)
├── Review & Critique (评审迭代) ⭐
├── Coordinator (动态路由)
└── Hierarchical (层级分解)

评测策略
├── 评估器分离 ⭐ 核心原则
├── MAX 策略 (多次运行取最优)
└── Keep Quality Left (尽早发现)

上下文管理
├── Context Engineering
├── Initializer + Worker
└── Feedforward + Feedback
```

---

## 来源索引

| 模式 | 主要来源 |
|------|---------|
| 评估器分离 | OpenAI, Martin Fowler |
| 深度优先 | OpenAI |
| Review & Critique | Google Cloud |
| Initializer + Worker | Anthropic |
| Feedforward + Feedback | Martin Fowler |
| Keep Quality Left | Martin Fowler |

---

*最后更新: 2026-04-07*
