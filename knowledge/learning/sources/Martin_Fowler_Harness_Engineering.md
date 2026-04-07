# Martin Fowler: Harness Engineering for Coding Agent Users

> 来源: [Martin Fowler](https://martinfowler.com/articles/harness-engineering.html)
> 日期: 2025

---

## 核心框架

```
Agent = Model + Harness
```

**Harness** = 除了模型本身之外的一切

---

## Feedforward vs Feedback

| 类型 | 作用 | 例子 |
|------|------|------|
| **Guides (Feedforward)** | 预防，在行动前引导 | AGENTS.md, linter rules |
| **Sensors (Feedback)** | 观察，帮助自纠正 | 测试，代码审查 |

> "Separately, you get either an agent that keeps repeating the same mistakes (feedback-only) or an agent that encodes rules but never finds out whether they worked (feedforward-only)."

---

## Computational vs Inferential

| 类型 | 执行方式 | 速度 | 确定性 |
|------|---------|------|--------|
| **Computational** | CPU | 快 (ms-s) | 可靠 |
| **Inferential** | GPU/NPU | 慢且贵 | 非确定 |

**例子**:
- Computational: Tests, linters, type checkers, structural analysis
- Inferential: AI code review, "LLM as judge"

---

## Timing: Keep Quality Left

> "The earlier you find issues, the cheaper they are to fix."

### 生命周期分布

| 阶段 | 控制类型 |
|------|---------|
| Commit 前 | Linters, fast tests, basic code review agent |
| Post-integration | Mutation testing, broader code review |
| 持续监控 | Dead code detection, coverage analysis, SLO monitoring |

---

## 三种 Harness 类型

### 1. Maintainability Harness (最简单)
调节内部代码质量和可维护性

**Computational sensors catch**:
- Duplicate code
- Cyclomatic complexity
- Missing test coverage
- Architectural drift
- Style violations

**LLMs can partially address**:
- Semantically duplicate code
- Redundant tests
- Over-engineered solutions

**Neither catches reliably**:
- Misdiagnosis of issues
- Overengineering
- Misunderstood instructions

### 2. Architecture Fitness Harness
定义和检查应用架构特性

- Performance tests
- Observability standards (logging)
- Architectural constraint rules

### 3. Behaviour Harness (最难)
功能行为是否符合预期

**当前方法**:
- Feedforward: Functional specification
- Feedback: AI-generated test suite

**问题**: "This approach puts a lot of faith into the AI-generated tests, that's not good enough yet."

---

## Harness Templates

企业常见模式 → 未来的 Harness Templates：
- 一组 guides 和 sensors
- 绑定 coding agent 到拓扑的结构、惯例、技术栈
- 团队可以根据已有 harness 选择技术栈

---

## Human 的角色

人类带来的是**隐式 Harness**：
- Absorbed conventions
- Felt cognitive pain of complexity
- Social accountability
- Organisational memory

> "A coding agent has none of this."

**Harness 的目标**: 不是消除人类输入，而是把人类输入引导到最重要的地方。

---

## OpenAI 的案例

OpenAI 的 harness 包括：
- Layered architecture enforced by custom linters
- Structural tests
- Recurring "garbage collection" scanning for drift

**结论**: "Our most difficult challenges now center on designing environments, feedback loops, and control systems."

---

## 对 AutoMAS 的启示

### ✅ 可借鉴

1. **Feedforward + Feedback 组合**
   - 我们的 harness 需要 Guides (instructions) + Sensors (evaluators)
   - 不能只有一方面

2. **Keep Quality Left**
   - 尽早发现问题
   - 评测要在 context window 耗尽前完成

3. **Maintainability Harness 模式**
   - 结构测试最可靠
   - AI 评测是非确定性的，需要结合使用

4. **Harness Templates**
   - 标准化评测框架
   - 可复用的评测组件

### ❌ 不适用

1. **Behavioral Harness** - 我们是评测框架，不是代码生成
2. **Mutation testing** - 不直接适用于我们的场景

---

## 原文关键引用

> "A well-built outer harness serves two goals: it increases the probability that the agent gets it right in the first place, and it provides a feedback loop that self-corrects as many issues as possible before they even reach human eyes."

> "The earlier you find issues, the cheaper they are to fix."

> "A good harness should not necessarily aim to fully eliminate human input, but to direct it to where our input is most important."

---

*最后更新: 2026-04-07*
