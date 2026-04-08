# 🔁 Patterns

反复出现的模式

---

## 贡献格式

```markdown
## [模式名称]

### 描述
这个模式是什么？

### 观察到的地方
在哪些地方观察到这个模式？

### 原则
它遵循什么原则？

### 变体
有什么已知变体？
```

---

## 已识别的模式

### 1. 评估器分离模式 (Generator-Evaluator)
**描述**: Generator 不评自己，由独立 Evaluator 评分
**来源**: OpenAI, Anthropic, Martin Fowler, 我们的实验
**原则**: Agent 总是高估自己的工作
**变体**: 
- 独立 Evaluator Agent
- 人类评审
- 自动评测脚本

### 2. 深度优先模式 (Depth-First)
**描述**: 大目标分解为小构建块，一次只做一个
**来源**: OpenAI, Martin Fowler
**原则**: 避免"一次搞定"导致的质量下降
**变体**:
- 串行深度优先
- 带检查点的深度优先

### 3. 渐进式披露模式 (Progressive Disclosure)
**描述**: 先展示摘要，需要时再深入细节
**来源**: OpenAI, Anthropic, 人类认知研究
**原则**: 人类处理信息的方式
**变体**:
- 分层摘要
- 按需展开
- AGENTS.md as TOC

### 4. MAX 策略模式
**描述**: 运行多次取最优分数
**来源**: 我们的实验 (v29-v33)
**原则**: 单次运行有方差，多次运行降低方差（但不是越多越好）
**变体**:
- MAX-1: 1次运行
- MAX-2: 2次运行 (v31 使用)
- MAX-3: 3次运行 (v33 失败)

### 5. 黄金Token Budget 模式
**描述**: 存在一个最优 token 数量
**来源**: 我们的实验 (v31)
**原则**: 太少不够深度，太多边际递减
**变体**:
- 3000 tokens: 基本足够
- 5000 tokens: v31 最佳 (76.22)
- 6000 tokens: v32 边际递减 (72.22)

### 6. Review & Critique 模式 ⭐
**描述**: Generator 产生内容 → Critic 评估 → 迭代直到达标
**来源**: Google Cloud, Anthropic, 我们的 Gen 任务
**原则**: 独立评审者能发现作者忽略的问题
**变体**:
- 单轮评审
- 多轮迭代 (我们的 gen_review 模式)
- 分层评审 (先快速筛选，再深度评审)

### 7. Sequential 模式
**描述**: 预定义线性顺序执行子任务
**来源**: Google Cloud
**原则**: 固定流程不需要动态调度
**变体**:
- 纯顺序
- 带条件跳过

### 8. Parallel 模式
**描述**: 多个子任务同时执行
**来源**: Google Cloud, Specialist Panel 模式
**原则**: 并行可以降低延迟但增加成本
**变体**:
- 扇出-收集 (Fan-out-Gather)
- 独立并行

### 9. Loop 模式
**描述**: 迭代直到满足终止条件
**来源**: Google Cloud, Anthropic, 我们的自反射机制
**原则**: 重复直到质量达标
**变体**:
- 固定次数循环
- 条件终止循环

### 10. Context Engineering 模式
**描述**: 多Agent系统需要专门管理信息流
**来源**: Google Cloud, Martin Fowler
**原则**: 每个Agent需要特定上下文才能有效工作
**变体**:
- 上下文隔离
- 上下文持久化
- 上下文压缩

### 11. Initializer + Worker 模式
**描述**: 初始化 Agent 设置环境，后续 Worker 增量执行
**来源**: Anthropic
**原则**: 跨 session 保持状态和进度
**变体**:
- Initializer 建立基准
- Worker 增量工作
- Progress file 跨 session 传递

### 12. Feedforward + Feedback 模式
**描述**: 预防问题 + 观察后自纠正
**来源**: Martin Fowler
**原则**: 单独用任一方都会失败
**变体**:
- Guides (Feedforward): 预防
- Sensors (Feedback): 观察纠正

### 13. Keep Quality Left 模式
**描述**: 尽早发现问题
**来源**: Martin Fowler
**原则**: 发现越早，修复越便宜

### 14. Computational vs Inferential 模式
**描述**: 确定性快速检查 vs 语义分析
**来源**: Martin Fowler
**原则**: 两者结合使用
**变体**:
- Computational: linter, tests, type checker
- Inferential: AI review, LLM as judge

---

## 🔗 模式关系图

```
单Agent系统
├── 深度优先 (一次一个功能)
├── 渐进式披露 (先摘要后细节)
└── 黄金Token Budget (最优token数)

多Agent系统
├── Sequential (线性流程)
├── Parallel (并行执行)
├── Loop (迭代优化)
├── Review & Critique (评审迭代) ⭐ 核心模式
├── Coordinator (动态路由)
└── Hierarchical (层级分解)

评测策略
├── 评估器分离 ⭐ 核心原则
├── MAX 策略 (多次运行取最优)
└── Keep Quality Left (尽早发现)

上下文管理
├── Context Engineering (信息流管理)
├── Initializer + Worker (跨session)
└── Feedforward + Feedback (预防+纠正)
```

---

## 📊 模式成功率

| 模式 | 成功率 | 备注 |
|------|--------|------|
| 评估器分离 | ✅ 100% | 始终有效 |
| 深度优先 | ✅ 100% | 始终有效 |
| 黄金Token Budget | ✅ 100% | 5000 是最优 |
| Review & Critique | ✅ 100% | Gen 任务核心 |
| MAX-2 | ✅ 100% | v31 最佳 |
| MAX-3 | ❌ 0% | v33 失败 |
| Sequential | ✅ 100% | 固定流程 |
| Parallel | ⚠️ 50% | 需要场景匹配 |
| Loop | ⚠️ 50% | 需要正确终止条件 |
| Keep Quality Left | ✅ 100% | 通用原则 |

---

## 📚 来源

| 来源 | 关键模式 |
|------|---------|
| OpenAI | AGENTS.md as TOC, Depth-First, 等待是昂贵的 |
| Anthropic | Initializer+Worker, Feature List, 增量进度 |
| Martin Fowler | Feedforward/Feedback, Keep Quality Left, Computational/Inferential |
| Google Cloud | 7种多Agent模式, Context Engineering |
| 我们的实验 | MAX策略, Token Budget, 选择性自反射 |

---

*最后更新: 2026-04-07*
