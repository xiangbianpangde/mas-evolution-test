# Anthropic: Effective Harnesses for Long-Running Agents

> 来源: [Anthropic Engineering Blog](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)
> 日期: 2024-2025

---

## 核心问题

长时间运行的 Agent 面临两个失败模式：

| 失败模式 | 描述 |
|---------|------|
| **One-shot 倾向** | 试图一次完成所有功能，导致中途耗尽 context |
| **提前宣布完成** | 看到已有进展就认为任务完成 |

---

## 两部分解决方案

### 1. Initializer Agent
第一个 session 设置初始环境：
- `init.sh` - 运行脚本
- `claude-progress.txt` - 进度日志
- Feature list JSON - 功能列表

### 2. Coding Agent
每个后续 session：
- 读取进度文件和 git log
- 选择一个 feature 开始工作
- 完成后提交 git + 更新进度文件

---

## Feature List 设计

```json
{
  "category": "functional",
  "description": "New chat button creates a fresh conversation",
  "steps": [
    "Navigate to main interface",
    "Click the 'New Chat' button",
    "Verify a new conversation is created"
  ],
  "passes": false
}
```

**关键设计**：
- JSON 格式 > Markdown（不易被模型随意修改）
- 所有 feature 初始标记为 `passes: false`
- 模型只能改 passes 字段，不能删除或修改测试

---

## 增量进度

> "The key insight was finding a way for agents to quickly understand the state of work when starting with a fresh context window."

每个 session 的步骤：
1. `pwd` - 确认工作目录
2. 读取 `claude-progress.txt` 和 git log
3. 选择最高优先级且 `passes: false` 的 feature
4. 运行 init.sh 启动开发服务器
5. 先做基础测试确保环境正常
6. 开始实现一个 feature

---

## 测试的重要性

Anthropic 发现：
- Claude 倾向于标记功能完成但没有正确测试
- 需要 **end-to-end 测试**（如 Puppeteer 浏览器自动化）
- 截图验证功能正常工作

> "Providing Claude with these kinds of testing tools dramatically improved performance."

---

## Agent 失败模式对照表

| 问题 | Initializer 行为 | Coding Agent 行为 |
|------|-----------------|------------------|
| Claude 过早宣布胜利 | 建立 feature list | 读取 feature list，每次只做一个 |
| 环境有 bug 或无文档 | 建立 git repo + 进度文件 | 读进度文件 + git log，结束时更新 |

---

## 对 AutoMAS 的启示

### ✅ 可借鉴

1. **Feature list 模式**
   - 用 JSON 格式定义任务
   - 任务状态 tracking（pass/fail）
   - 只允许修改状态字段

2. **初始化 + 增量执行**
   - 先建立基准环境
   - 每次只做一个任务

3. **Progress file**
   - 记录进度供后续 session 参考
   - 减少重复推理

4. **Git 提交 + 回滚**
   - 提交保持代码状态
   - 可回滚坏变更

### ❌ 不适用

1. **Browser automation** - 我们的任务不需要
2. **init.sh** - 我们的任务是独立 API 调用

---

## 原文关键引用

> "The key insight was finding a way for agents to quickly understand the state of work when starting with a fresh context window."

> "Once working incrementally, it’s still essential that the model leaves the environment in a clean state after making a code change."

> "Providing Claude with these kinds of testing tools dramatically improved performance."

---

*最后更新: 2026-04-07*
