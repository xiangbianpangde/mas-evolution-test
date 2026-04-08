# Harness Engineering - 网络知识库

## OpenAI 官方经验 (2025年8月-2026年1月)

**核心成果**: 5个月，100万行代码，0行手写代码
- 3.5 PRs/工程师/天
- 人类只做：设计环境、指定意图、构建反馈循环
- Codex 执行

### 关键原则

**1. 深度优先 (Depth-First)**
- 大目标分解为小构建块 (design, code, review, test)
- 用构建块解锁更复杂任务
- 失败时问："缺什么能力？如何让 agent 可见可执行？"

**2. 评估器是关键**
- Agent 总是对自己的工作评分过高
- 分离生成与评估 = 诚实反馈循环
- 调优一个怀疑性的独立评估器比让生成器自我批评容易得多

**3. 上下文管理**
- 不要"一本巨册 AGENTS.md"
- 100行 AGENTS.md = 目录
- 知识存在 structured docs/ 目录
- 上下文窗口是短暂资源，所有必须存在磁盘

**4. Session 流程**
```
Orient → Setup → Verify baseline → Select one task → Implement → Test → Update state → Clean exit
```

**5. 反馈循环要快**
- 类型检查、linter、测试、安全扫描
- 慢验证减少迭代次数

### 最佳实践 (Anthropic + OpenAI)

**Agent 角色分工**
- Planner: 扩展短提示为完整规格
- Generator: 一次实现一个功能
- Evaluator/QA: 测试运行中的应用程序

**多 Agent 决策**
- 先单 Agent，再多 Agent
- 多 Agent 引入复杂度如同微服务 + 非确定性
- 只有单 Agent 遇到天花板才添加

**Context 管理**
- 每个 session 创建新 client/context
- 压缩保留连续性但不消除"上下文焦虑"
- 完全重置给干净 slate

**JSON > Markdown**
- 任务列表用 JSON（抵抗模型腐败）
- 永远不删除/重排序，只翻转完成状态

## 中文资源

### 视频
- [哔哩哔哩: Harness Engineering 深度解析](https://www.bilibili.com/video/BV1Zk9FBwELs/)

### 文章
- [知乎: Harness Engineering 深度解读](https://zhuanlan.zhihu.com/p/2016495809307374819)
- [博客园: Harness Engineering 从零理解到动手实践](https://www.cnblogs.com/aquester/p/19791985)
- [郝源的完全指南](https://www.heyuan110.com/zh/posts/ai/2026-03-30-harness-engineering-guide/)

### GitHub 学习指南
- [deusyu/harness-engineering](https://github.com/deusyu/harness-engineering)

## 评测基准 (Multi-Agent Evaluation)

### 关键资源
- [MASEval](https://github.com/parameterlab/MASEval) - 统一评测库
- [MASEval arxiv](https://arxiv.org/html/2603.08835) - 多 Agent 评测框架
- [LangChain: Multi-Agent Benchmarking](https://blog.langchain.com/benchmarking-multi-agent-architectures/)
- [Microsoft: Multi-Agent Reference Architecture](https://microsoft.github.io/multi-agent-reference-architecture/docs/evaluation/Evaluation.html)
- [GitHub: multi-agent-benchmarks](https://github.com/Viewer-HX/multi-agent-benchmarks)

### YouTube
- [Evaluating Multi Agent Systems](https://www.youtube.com/watch?v=PvdaIqIUpnQ)

## 核心公式
```
Agent = Model + Harness
Harness = 缰绳 + 马鞍 + 跑道护栏 + 反馈镜子
```

## 适用本项目的原则
1. **Evaluator 分离**: Generator 不评自己
2. **深度优先**: 小块构建 → 大任务
3. **上下文磁盘化**: Session 间持久化
4. **反馈快速**: 验证延迟决定迭代次数
5. **避免巨册**: 用目录结构替代
