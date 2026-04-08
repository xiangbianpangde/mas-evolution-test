# 📚 Sources

有价值的外部资源

---

## 贡献格式

```markdown
## [资源名称]
**类型**: Article / Video / Tool / Paper
**来源**: 来源网站
**链接**: URL
**日期**: YYYY-MM-DD
**摘要**: 简要描述内容
**关键点**:
- 点1
- 点2
```

---

## 资源索引

### Articles

| 资源 | 来源 | 关键主题 |
|------|------|---------|
| [Harness Engineering: leveraging Codex](https://openai.com/index/harness-engineering/) | OpenAI | 深度优先，评估器分离 |
| [Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) | Anthropic | 上下文持久化，初始化器 |
| [Harness Engineering](https://martinfowler.com/articles/harness-engineering.html) | Martin Fowler | Feedforward/Feedback, Keep Quality Left |
| [AI Agent Orchestration Patterns](https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/ai-agent-design-patterns) | Microsoft | Multi-Agent 编排模式 |
| [Agentic AI: Comprehensive Survey (arXiv:2510.25445)](https://arxiv.org/abs/2510.25445) | arXiv 2025 | Dual-paradigm: Symbolic vs Neural |
| [Choose Design Pattern for Agentic AI](https://docs.cloud.google.com/architecture/choose-design-pattern-agentic-ai-system) | Google Cloud 2025 | 5种多Agent模式详细指南 |
| [Agent Harness Evaluation Guide](https://qubittool.com/blog/agent-harness-evaluation-guide) | QubitTool 2026 | Harness 工程完整指南 |
| [What Is Harness Engineering?](https://www.agent-engineering.dev/article/harness-engineering-in-2026-the-discipline-that-makes-ai-agents-production-ready) | Agent Engineering 2026 | 生产级 Harness 构建 |
| [Awesome Harness Engineering](https://github.com/walkinglabs/awesome-harness-engineering) | GitHub | 883实体知识图谱 |

### Videos

| 资源 | 来源 | 关键主题 |
|------|------|---------|
| [Harness Engineering 深度解析](https://www.bilibili.com/video/BV1Zk9FBwELs/) | Bilibili | 中文讲解 |

### Papers

| 资源 | 来源 | 关键主题 |
|------|------|---------|
| [MASEval](https://arxiv.org/html/2603.08835) | Arxiv | Multi-Agent 评测框架 |
| [Agentic AI Survey (Springer)](https://link.springer.com/article/10.1007/s10462-025-11422-4) | Artificial Intelligence Review 2025 | 混合神经符号架构 |

### GitHub

| 资源 | 来源 | 关键主题 |
|------|------|---------|
| [harness-engineering 学习指南](https://github.com/deusyu/harness-engineering) | deusyu | 中文学习资源 |
| [Everything-Claude-Code](https://github.com/aXp-Engineering/Everything-Claude-Code) | aXp-Engineering | Claude Code harness 完整系统 |
| [Harness Engineering Knowledge Graph](https://harness-engineering.ai/) | harness-engineering.ai | 交互式知识图谱 |

---

## 🎯 Google Cloud 5种多Agent模式 (2025)

| 模式 | 描述 | 适用场景 | 关键洞察 |
|------|------|---------|---------|
| **Sequential** | 预定义线性顺序 | 固定流程，数据处理管道 | 低延迟，但缺乏灵活性 |
| **Parallel** | 并发执行，独立子任务 | 多源数据收集，多角度分析 | 降低延迟，但成本增加 |
| **Loop** | 迭代直到终止条件 | 自我修正，质量改进 | 复杂工作流，但有死循环风险 |
| **Review & Critique** | Generator + Critic | 代码审核，内容质量保证 | **我们正在使用的模式！** |
| **Hierarchical** | 多层Orchestrator | 复杂系统分解 | 可扩展，但增加复杂度 |

---

## 🔬 关键发现

### 1. Agentic AI 双范式框架 (arXiv 2025)
- **Symbolic/Classical**: 算法规划 + 持久状态 → 安全关键领域 (医疗)
- **Neural/Generative**: 随机生成 + prompt驱动 → 适应性数据丰富环境 (金融)
- **未来**: 混合架构 = 适应性强 + 可靠

### 2. Google Cloud 设计原则
- **单Agent优先**: 先从单Agent开始，再考虑多Agent
- **多Agent场景**: 任务需要多个不同技能，或需要并行处理
- **Context Engineering**: 多Agent系统需要专门管理信息流

### 3. Review & Critique 模式
- Generator 产生内容
- Critic 评估是否符合标准
- 可迭代直到满足质量标准
- **这正是我们 Gen 任务使用的模式！**

---

*最后更新: 2026-04-07*
