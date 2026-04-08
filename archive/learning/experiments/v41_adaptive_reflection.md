# v41: Adaptive Reflection Strategy

## 核心问题
v39 使用的 2-pass 反思策略会增加 LLM 调用次数和 token 消耗：
- 对于简单任务（第一轮质量 >= 85），反思是浪费
- 对于困难任务（第一轮质量 < 70），多轮反思有价值

## v41 策略：自适应阈值

```python
def should_reflect_more(self, quality_so_far: float, pass_num: int) -> bool:
    """根据当前质量决定是否继续反思"""
    if pass_num == 1:
        # 第一轮反思后，质量 >= 80 就不需要第二轮
        return quality_so_far < 80
    elif pass_num == 2:
        # 第二轮反思后，质量 >= 70 就接受
        return quality_so_far < 70
    return False
```

## 预期效果
- 简单任务：1 次 LLM 调用（无反思）→ 节省 tokens
- 困难任务：最多 3 次 LLM 调用（2 轮反思）→ 提高质量
- 整体：平衡质量和效率

## 等待 v38/v39 结果后再决定是否实施
