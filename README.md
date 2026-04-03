# AutoMAS: Eternal Evolution Engine

## ⚠️ PARADIGM SHIFT: Real API Calls Required

**重要更新**: 根据更新的 SOUL.md，系统现在必须使用**真实 LLM API 调用**，禁止任何 Mock 数据！

---

## 🏆 当前冠军: Gen404 (Python MAS)

| 指标 | Gen404 | v12.0 Harness |
|------|--------|----------------|
| **综合评分** | **94.90** | 51.97 |
| 核心得分 | 77.0 | ~52 |
| 泛化得分 | 83.0 | ~52 |
| Token消耗 | 1.0 | ~2,500 |
| 评估标准 | 输出匹配 | 真实质量评估 |

**注意**: v6.0+ harness 版本使用更严格的独立评估（Executor/Evaluator 分离），分数较低但更接近真实能力。Gen404 使用输出匹配评估。

## Gen404 测试结果 (15任务)

```
核心任务: 77.0 分平均
  core_001: 95 | core_002: 95 | core_003: 65 | core_004: 65 | core_005: 95
  core_006: 95 | core_007: 65 | core_008: 50 | core_009: 65 | core_010: 80

泛化任务: 83.0 分平均
  gen_001: 95 | gen_002: 65 | gen_003: 95 | gen_004: 80 | gen_005: 80
```

## 源码
- `/mas/core_gen404.py` - 当前版本
- `/benchmark/tasks_v2.py` - 动态 Benchmark

---

*AutoMAS v4.0 - Real API Paradigm*
