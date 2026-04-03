# Harness Evolution History

## v6.0 - Anti-Cheat Separated Executor/Evaluator (2026-04-04)

**架构特点:**
- Executor/Evaluator 完全分离
- expected outputs 永不泄漏给 Executor
- 独立 Evaluator 评分（不知道正确答案）
- 行为审计：异常短延迟检测

**Benchmark 结果:**
```
[核心任务] 平均质量分: 50.0
[泛化任务] 平均质量分: 50.0
[Token消耗] Executor: 30582 | Evaluator: 7680
[平均延迟] 41.2秒/任务
[可疑检测] 0 个
[综合评分] 45.00/100
```

**问题识别:**
- Evaluator 评分过于统一（全是 50.0）
- 多维度评分缺失
- prompt 需要优化减少 LLM 评分随机性

**Root Cause:**
Evaluator prompt 太简单，LLM 默认给中等分。需要更细致的评分标准和多维度评估。

---

## v7.0 - Multi-Dimensional Scoring (2026-04-04)

**改进:**
1. 引入多维度评分（technical_depth, completeness, actionability）
2. 每个维度独立打分，最终加权平均
3. 优化 prompt 减少评分随机性
4. 去除 task_type hint 避免评分偏见

**运行状态:** 进行中

---

## 进化趋势

| 版本 | 评分机制 | 综合分 | 关键改进 |
|------|---------|--------|---------|
| v5 | 类型匹配 | 72.0 | 真实 API |
| v6 | 分离 Evaluator | 45.0 | 防作弊架构 |
| v7 | 多维度评分 | TBD | 更细致的评估 |
