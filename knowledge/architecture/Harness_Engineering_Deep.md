# Harness Engineering 深度研究

## 核心公式
```
Agent = Model + Harness
Harness = 缰绳 + 马鞍 + 跑道护栏 + 反馈镜子
```

## Anthropic: 长时间运行 Agent 的有效 Harness

### 核心问题
- Context 窗口有限
- 跨多窗口工作时需要桥接
- Agent 在新 session 开始时没有记忆

### 解决方案: 双层结构

#### 1. Initializer Agent (首次)
设置初始环境：
- `init.sh` - 初始化脚本
- `claude-progress.txt` - 进度日志
- 初始 git commit

#### 2. Coding Agent (后续每次)
- 每次只做一个功能
- 完成后留下清晰状态
- commit + 进度更新

### Feature List 设计
```json
{
  "category": "functional",
  "description": "New chat button creates a fresh conversation",
  "steps": ["Navigate to main", "Click button", "Verify..."],
  "passes": false
}
```
- JSON 格式 > Markdown (不易被破坏)
- 只改变 `passes` 字段
- 不可删除/编辑测试

### Session 流程
```
1. Run pwd (确认目录)
2. Read git logs + progress files (了解状态)
3. Read features list (选择最高优先级)
4. Implement one feature
5. Test (end-to-end, not just unit tests)
6. Update progress + git commit
```

---

## Martin Fowler: Harness 工程分类

### Feedforward vs Feedback

| 类型 | 作用 | 示例 |
|------|------|------|
| **Guides (前馈)** | 预测行为，行动前引导 | AGENTS.md, Skills, 规则 |
| **Sensors (反馈)** | 观察行为，帮助自我修正 | Linter, 测试, AI review |

### Computational vs Inferential

| 类型 | 特点 | 速度 | 可靠性 |
|------|------|------|--------|
| **Computational** | 确定性，CPU 运行 | 毫秒级 | 高 |
| **Inferential** | 语义分析，GPU 运行 | 秒级 | 概率性 |

### 三种 Regulation Categories

#### 1. Maintainability Harness
控制代码质量和可维护性
- Computational sensors: 重复代码、复杂度、测试覆盖
- Inferential: 语义重复、过度工程

#### 2. Architecture Fitness Harness
定义和检查架构特性
- Fitness Functions
- 性能测试
- 可观测性标准

#### 3. Behavior Harness
功能行为是否如预期
- 功能规格 (feedforward)
- 测试套件 (feedback)
- AI-generated tests 还不完美

### Timing Principle: Keep Quality Left
```
左边 (早): Linter, 快测试, 基础 review
右边 (晚): 慢测试, 全面 review, 变异测试
```

---

## OpenAI: 深度优先原则

### 核心经验
- 大目标 → 小构建块
- 构建块: design, code, review, test
- 用构建块解锁更复杂任务

### 失败时问
> "缺什么能力？如何让 agent 可见可执行？"

不是"try harder"，而是"what capability is missing"

---

## Azure: Multi-Agent 编排模式

### 何时用 Multi-Agent
- 跨域/跨功能问题
- 需要不同安全边界
- 需要并行专业化

### 不要过早优化
```
Direct call → Single agent → Multi-agent
     ↑                  ↑
   够用就不要加复杂度
```

---

## 关键原则总结

| 原则 | 来源 | 应用 |
|------|------|------|
| 深度优先 | OpenAI | 一次做一个功能 |
| 评估器分离 | OpenAI/Anthropic | Generator 不评自己 |
| 上下文磁盘化 | Anthropic | Session 间持久化 |
| 快速反馈 | Martin Fowler | 验证延迟决定迭代 |
| 目录替代巨册 | OpenAI | 渐进式披露 |
| JSON > Markdown | Anthropic | 状态文件不易损坏 |
| Keep Quality Left | Martin Fowler | 早发现问题成本低 |

---

## 本项目适用

**当前问题**:
- Python harness 是作弊 (非真实 API)
- v5.0 Native MAS 失败 (超时/解析问题)

**改进方向**:
1. 真实 API 调用 (已启动 native_evolution)
2. 深度优先: 一次一个任务
3. 状态持久化: JSON feature list
4. 评估器分离: Generator 不评自己
5. 快速反馈: Computational sensors
