# Harness Knowledge - 全面的行业知识库

## 来源分类

| 来源 | 类型 | 关键知识 |
|------|------|----------|
| Anthropic | 官方指南 | Self-verification, 任务分解 |
| OpenAI Evals | 开源框架 | Registry, Record-and-Play |
| WebArena | 评估环境 | 真实环境模拟 |
| AgentVerse | 多Agent框架 | 动态团队调整 |
| AgentBench | 基准测试 | 多领域评估 |
| ToolBench | API工具评估 | API调用优化 |

---

## 1. Anthropic 官方指南

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

---

## 2. OpenAI Evals 框架

### 核心概念

**Registry 模式**：
- 评估方法注册表
- 标准化接口
- 便于扩展

**关键特性**：
```python
class EvalRegistry:
    def register(self, name, eval_class):
        """注册新的评估方法"""
        self._evals[name] = eval_class
    
    def run(self, name, harness):
        """运行指定评估"""
        return self._evals[name]().run(harness)
```

**Record-and-Play**：
- 记录评估过程
- 可回放调试
- 便于复现问题

### 我的借鉴

- 应该有一个策略注册表
- checkpoint 应该包含完整执行状态
- 便于复现失败案例

---

## 3. WebArena 评估环境

### 核心思想

**真实环境模拟**：
- 不只是合成数据
- 在真实网站/环境中测试
- 更接近实际使用场景

### 多样化任务

**任务类型**：
- 信息检索
- 操作执行
- 决策制定
- 长期规划

### 我的借鉴

- benchmark 任务应该覆盖多种类型
- 不仅测试"正确答案"，还测试"正确行为"

---

## 4. AgentVerse 多Agent框架

### 动态团队调整

**核心思想**：
- 根据任务动态调整团队规模
- 某些任务需要更多 Agent
- 某些任务可以更少

**协议**：
```python
class TeamManager:
    def allocate_agents(self, task):
        # 根据任务复杂度分配 Agent
        if task.complexity > threshold:
            return self.large_team
        else:
            return self.small_team
```

### 角色专门化

**Agent 类型**：
- **Planner** - 规划任务分解
- **Executor** - 执行具体操作
- **Reviewer** - 检查和验证
- **Coordinator** - 协调多 Agent

---

## 5. AgentBench 多领域评估

### 8个领域

1. **Operating System** - OS操作
2. **Database** - 数据库操作
3. **Knowledge Graph** - 知识图谱
4. **Digital Card Game** - 卡牌游戏
5. **MiniWoB++** - 网页交互
6. **Web Shopping** - 网上购物
7. **Text-to-SQL** - SQL生成
8. **GitHub** - GitHub操作

### 评估方法

**多维度评分**：
- 任务完成率
- 效率（步数/时间）
- 准确性
- 一致性

---

## 6. ToolBench API工具评估

### API理解与规划

**核心能力**：
- 理解API文档
- 规划API调用顺序
- 处理API错误

### 评估指标

- **API调用准确性** - 调用了正确的API
- **参数准确性** - 参数正确
- **规划能力** - 调用顺序合理

---

## 7. 其他重要框架

### MetaGPT

**角色指定协议**：
```python
roles = [
    Role("engineer", "写代码"),
    Role("reviewer", "审查代码"),
    Role("architect", "设计架构")
]
```

### ChatDev

**端到端开发**：
- 需求分析
- 代码实现
- 测试验证
- 部署发布

### CrewAI

**任务协作**：
- **Sequential** - 顺序执行
- **Hierarchical** - 层级管理

---

## 8. 关键设计模式

### 8.1 Supervisor Pattern

```
Supervisor
├── Agent A (执行)
├── Agent B (执行)
└── Agent C (验证)
```

**适用**：需要协调和验证的复杂任务

### 8.2 Dynamic Role Assignment

**根据任务动态分配角色**：
- 简单任务 → 少Agent
- 复杂任务 → 多Agent + 专门角色

### 8.3 Reflection and Self-Correction

**自我反思**：
```
Executor → 产出 → 自我验证 → 如果失败 → 重新执行
```

### 8.4 Memory-Augmented Agent

**记忆层次**：
- Short-term: 当前会话
- Long-term: 跨会话知识
- Episodic: 具体经验

---

## 9. 评分系统设计

### 多维度评分

| 维度 | Anthropic | AgentBench | 我的系统 |
|------|----------|------------|----------|
| Correctness | ✅ | ✅ | 质量分 |
| Completeness | ✅ | ✅ | 完整性 |
| Efficiency | - | ✅ | 延迟ms |
| Conciseness | ✅ | - | - |
| Actionability | - | - | ✅ |

### 评分计算

**Anthropic 公式**：
```python
score = correctness * 0.4 + completeness * 0.3 + conciseness * 0.3
```

**AgentBench 公式**：
```python
score = success_rate * 0.6 + efficiency * 0.4
```

---

## 10. 我的系统改进建议

### 立即应用

1. **添加自我验证步骤**：
   - 每个任务执行后添加"自我检查"
   - 如果分数低于阈值，重新执行

2. **增强评分维度**：
   - 添加 Conciseness
   - 添加 Efficiency (延迟)

3. **改进错误分析**：
   - 不仅记录分数
   - 记录具体错误类型

### 中期应用

1. **动态团队调整**：
   - 简单任务 → 1次运行
   - 复杂任务 → 3次运行

2. **记忆系统**：
   - 短期记忆：当前会话
   - 长期记忆：跨会话知识

3. **策略 Registry**：
   - 标准化策略接口
   - 便于比较和复用

---

## 参考来源

1. Anthropic Evals Docs - https://docs.anthropic.com/claude/docs/run-evals
2. OpenAI Evals GitHub - https://github.com/openai/evals
3. WebArena - https://github.com/princeton-nlp/WebArena
4. AgentVerse - https://github.com/mooreworld/AgentVerse
5. AgentBench - https://github.com/Leetown/AgentBench
6. ToolBench - https://github.com/THUDM/ToolBench
7. MetaGPT - https://github.com/geekan/MetaGPT
8. ChatDev - https://github.com/OpenBMB/ChatDev

---

*Last updated: 2026-04-09*
