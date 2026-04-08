# OpenAI Harness Engineering 原文

> 来源: [Harness engineering: leveraging Codex in an agent-first world](https://openai.com/index/harness-engineering/)
> 日期: 2025年 (5个月实验)

---

## 核心原则

| 原则 | 说明 |
|------|------|
| **人类 steering，Agent execute** | 人类设计环境，Agent 执行代码 |
| **Depth-first** | 大目标分解为小构建块 |
| **AGENTS.md 是目录** | ~100行作为入口，细节在 docs/ |
| **渐进式披露** | 给地图，不给千页手册 |
| **机械 enforced invariant** | linter 检查，非人工审批 |

---

## 关键洞见

### 1. Context 管理是最大挑战

**失败的方案**: "One big AGENTS.md"
- Context 是稀缺资源
- 巨册式指令挤占了任务、代码、文档
- 当一切都是"重要"时，什么都不重要
- 文档会腐烂，变成过时规则

**成功的方案**: Treat AGENTS.md as table of contents
- ~100 行作为入口和地图
- 详细内容在 docs/ 目录
- 强制机械检查 (linter, CI)

### 2. 环境比指令更重要

> "Early progress was slower than we expected, not because Codex was incapable, but because the environment was underspecified."

人类工程师的工作变成"给 agent 赋能"：
- 什么能力缺失？
- 如何让它可理解且可执行？

### 3. 刚性架构 = Agent 高效的前提

```
每业务域 → 固定层数
Types → Config → Repo → Service → Runtime → UI
```

- 约束被机械 enforced
- 自定义 linter 生成 error message 包含修复指令
- 一旦编码，应用到所有地方

### 4. 等待是昂贵的，纠正是便宜的

- PR 短命
- 测试 flake 用后续运行解决
- 不blocking进度

---

## 对 AutoMAS 的启示

### ✅ 可借鉴

1. **AGENTS.md 作为目录**
   - 我们的 `knowledge/` 结构正是这个思路
   - 但需要机械检查确保不腐烂

2. **Depth-first 策略**
   - OpenAI 验证有效
   - 我们在 v31 实验中也在用

3. **渐进式披露**
   - 先摘要后细节
   - 我们的 SUMMARY.md 符合这个原则

### ❌ 不适用

1. **Agent 生成所有代码** - 我们的评测需要 ground truth
2. **短命 PR** - 评测结果需要可复现
3. **等待 vs 纠正** - 评测需要确定性结果

---

## 原文关键引用

> "Humans steer. Agents execute."

> "The primary job of our engineering team became enabling the agents to do useful work."

> "Give Codex a map, not a 1,000-page instruction manual."

> "Agents are most effective in environments with strict boundaries and predictable structure."

---

*最后更新: 2026-04-07*
