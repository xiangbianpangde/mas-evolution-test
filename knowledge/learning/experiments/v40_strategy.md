# v40 策略设计

## v39 vs v31 对比分析

v39 改进了自我反思深度（2轮 vs 1轮），但代价是：
- 每次 research 任务最多 3 次 LLM 调用（初始 + 2次反思）
- Token 消耗增加约 50%
- 如果第一轮已经很好，第二轮反思可能是浪费

## v40 候选策略

### 候选 A: Adaptive Reflection（自适应反思）
只在第一轮输出质量低于阈值时才触发反思
- 如果 Run1 质量 >= 80，不反思（直接进入 MAX 对比）
- 如果 Run1 质量 < 80，触发 2 轮反思
- 优点：避免浪费，对于简单任务直接给出高质量
- 缺点：增加了判断逻辑

### 候选 B: Different Temperature for Different Runs（分温度策略）
MAX-2 已经取最优。但可以探索：
- Run1: temperature=0.3（确定性）
- Run2: temperature=0.9（多样性）
- 两者取最优
- 优点：覆盖不同的输出空间

### 候选 C: Extended Review Tokens（延长 Review）
v31.0 弱项：core_005=65 (review), core_010=58 (review)
当前 review tokens: 3000
v40 探索: 4000-5000 tokens for review tasks

### 候选 D: Task-Specific Evaluator Prompts（任务专用评估 prompt）
每个任务类型用不同的 evaluator prompt
- Research: 强调深度、技术准确性、可执行性
- Code: 强调正确性、可运行性、代码质量
- Review: 强调风险识别、影响分析、可操作性

## 推荐 v40 策略

选择 **候选 C（延长 Review Tokens）+ 候选 D（任务专用评估）**

理由：
- v38 正在测试增强 review prompts（候选 D 的一部分）
- 如果 v38 不如 v31，说明 prompt 改进方向不对
- v40 应该尝试增加 review tokens 到 4000

## 实施计划

```python
# get_max_tokens 改动
def get_max_tokens(self, task: Dict) -> int:
    if task["type"] == "research":
        return 5000  # 不变
    elif task["type"] == "code":
        return 5000  # 不变
    else:  # review
        return 4500  # 从 3000 提高到 4500
```

等待 v38 结果后再决定是否实施。
