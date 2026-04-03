# Harness Evolution History

## v5.0 - First Real API Benchmark (2026-04-03)

**Benchmark 结果:** 75.4/100
- First real API test, type-matching based scoring

---

## v6.0 - Anti-Cheat Separated Executor/Evaluator (2026-04-04)

**Benchmark 结果:** 45.00/100
- Executor/Evaluator 完全分离
- expected outputs 永不泄漏

---

## v7.0 - Multi-Dimensional Scoring (2026-04-04)

**Benchmark 结果:** 47.78/100

---

## v8.0 - Simplified Prompts (2026-04-04)

**Benchmark 结果:** 46.80/100

---

## v9.0 - Consistency Fix (2026-04-04)

**Benchmark 结果:** 47.03/100

---

## v10.0 - Concise Executor (2026-04-04)

**Benchmark 结果:** 49.84/100

---

## v11.0 - Structured Output (2026-04-04)

**Benchmark 结果:** 41.73/100 (regression!)

---

## v12.0 - Few-Shot Actionability Examples (2026-04-04)

**Benchmark 结果:** 51.97/100 🏆 BEST
- 核心任务: 54.5, 泛化任务: 54.5
- Actionability: L3.1
- Token消耗: 42823
- 2 examples (1 good + 1 bad)

---

## v13.0 - Multi-Example + Ensemble Eval (2026-04-04)

**Benchmark 结果:** 49.10/100 ❌ REGRESSION
- 核心任务: 51.7, 泛化任务: 51.7
- Actionability: L2.3 (↓0.8 from v12)
- Token消耗: 53437 (+25%)
- 4 examples + 2x ensemble eval

**Root Cause:**
- 4 examples 太多，导致 Executor 信息过载
- 更多的 examples 反而干扰了输出质量
- 简单胜复杂 - 回归 v12 风格

**Lesson:** 2 examples > 4 examples

---

## v14.0 - Actionability-Focused (FAILED)

**Benchmark 结果:** 39.74/100 ❌ WORST
- 2 good only, no bad example (regression from v12)
- Actionability: L2.2

---

## v15.0 - Back to v12 Foundation

**Benchmark 结果:** 48.35/100
- 核心任务: 51.1, 泛化任务: 51.1
- Actionability: L2.7 (回稳)
- Token消耗: 43160

**结论:**
- 回归 v12 结构有效果，但未完全恢复
- v12 的 52.0 仍是最优
- 问题是 executor 输出的稳定性

---

## 版本对比总结

| Version | Score | Actionability | Token | 备注 |
|---------|-------|---------------|-------|------|
| v5 | 75.4 | N/A | - | First real API |
| v12 | 52.0 | L3.1 | 42823 | 🏆 BEST |
| v13 | 49.1 | L2.3 | 53437 | Regression |
| v14 | 39.7 | L2.2 | 43894 | Worst |
| v15 | 48.4 | L2.7 | 43160 | Partial recovery |

## 关键发现

1. **Bad example 很重要** - 单独用 good example 会降低 actionability
2. **2 examples 优于 4 examples** - v12 > v13
3. **v12 的结构最优** - 回归后分数回稳但未完全恢复

## 下一步

需要找出 v12 和 v15 之间差异的真正原因：
- 可能问题：API 调用变化？
- 可能问题：评分随机性？
- 需要做 A/B 测试验证