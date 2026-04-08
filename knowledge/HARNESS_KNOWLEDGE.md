# Harness Knowledge - 行业最佳实践

## Anthropic 官方指南 (2024)

### Self-Verification 最佳实践

**关键发现**：Self-verification（自我验证）比让另一个 Agent 检查更有效。

**原因**：
- 同一个 Agent 理解自己的推理过程
- 可以交叉验证自己的推理
- 避免了 Agent 间沟通损耗

**实现方法**：
1. 将复杂任务分解为子任务
2. 每个子任务完成后立即自我验证
3. 如果验证失败，尝试修正

### 构建评估测试用例

**核心原则**：
1. **聚焦最重要** - 测试应该衡量对你最重要的东西
2. **覆盖边缘** - 应该覆盖边缘情况和常见错误
3. **可操作** - 结果应该指导具体改进

**评分维度** (Anthropic 推荐)：
- **Correctness** - 答案是否正确？
- **Conciseness** - 是否简洁？
- **Style** - 风格是否合适？
- **Completeness** - 是否完整？

### 我的实验的对应

| Anthropic 原则 | 我的实现 | 状态 |
|----------------|----------|------|
| Self-verification | 对 Gen research 应用自反射 | ✅ |
| 任务分解 | 15 个独立任务 | ✅ |
| 多维度评分 | Depth/Completeness/Actionability | ✅ |
| 边缘覆盖 | Gen 任务包括高难度场景 | ⚠️ |

## OpenAI Evals 框架

### 核心概念

**Registry 模式**：
- 评估方法注册表
- 标准化接口
- 便于扩展

**我的借鉴**：
- 应该有一个策略注册表
- 标准化策略接口
- 便于比较不同策略

### Record-and-Play

**概念**：
- 记录评估过程
- 可回放调试
- 便于复现问题

**我的借鉴**：
- checkpoint 应该包含完整执行状态
- 便于复现失败案例

## 关键教训

### 1. 自我验证 > 交叉验证

```
错误：Executor → Checker → Leader
正确：Executor (执行+自我验证) → Leader
```

### 2. 多维度评分 > 单分数

```
单一分数不足以描述质量
需要 Depth + Completeness + Actionability
```

### 3. 边缘案例覆盖

```
测试不应该只测"正常"情况
应该有意测试边缘和错误情况
```

### 4. 可操作的反馈

```
"答案不正确" 不够
应该是"答案在 X 方面不正确，原因是 Y"
```

## 改进建议

### 立即改进

1. **添加自我验证**：
   - 每个任务执行后添加自我检查步骤
   - 不是外部 Checker，是执行者自己检查

2. **改进评分维度**：
   - 当前：Depth/Completeness/Actionability
   - 可添加：Correctness/Conciseness/Style

3. **增强错误分析**：
   - 不仅记录分数
   - 记录具体的错误类型和原因

### 中期改进

1. **策略 Registry**：
   - 建立标准化策略接口
   - 便于比较和复用

2. **执行回放**：
   - checkpoint 包含完整状态
   - 便于复现和调试

---

*Last updated: 2026-04-09*
*Sources: Anthropic Evals docs, OpenAI Evals GitHub*
