# AutoMAS: Eternal Evolution Engine

## 🏆 STABLE VERSION: v12.0 (Tagged & Released)

### v12.0 Benchmark Results

| 指标 | v12.0 | v12_rerun | Notes |
|------|-------|-----------|-------|
| **综合评分** | 51.97 | 51.26 | ✅ Confirmed stable |
| 核心得分 | 54.5 | 54.4 | Consistent |
| 泛化得分 | 54.5 | 54.4 | Consistent |
| Actionability | L3.1 | L3.1 | Stable |
| Token消耗 | 42,823 | 42,323 | ~600 variance |

### Architecture: 1 Good + 1 Bad Example

```
┌─────────────────────────────────────────────────────┐
│                  Executor (v12)                     │
│  Prompt: 1 Good Example + 1 Bad Example            │
│  Goal: Teach actionability via contrast            │
└──────────────────────┬──────────────────────────────┘
                      │ Real LLM API Call
                      ▼
┌─────────────────────────────────────────────────────┐
│                  Evaluator (v12)                   │
│  Strict 3-dim scoring: depth, completeness,        │
│  actionability (L1-L5 each)                        │
│  Output: JSON with scores + reasoning              │
└─────────────────────────────────────────────────────┘
```

### Key Findings (v10-v15 iterations)

| Version | Score | Actionability | Changes |
|---------|-------|---------------|---------|
| v10 | 49.8 | - | Concise executor |
| v11 | 41.7 | - | Structured output (REGRESSION) |
| **v12** | **52.0** | **L3.1** | 🏆 BEST - 1 good + 1 bad example |
| v13 | 49.1 | L2.3 | 4 examples + ensemble (regression) |
| v14 | 39.7 | L2.2 | STAR framework (worse regression) |
| v15 | 48.4 | L2.7 | Back to v12 design |

**Lesson**: Simple is better. 1 good + 1 bad example is the sweet spot.

---

## ⚠️ PARADIGM SHIFT: Real API Calls Required

**重要更新**: 根据更新的 SOUL.md，系统现在必须使用**真实 LLM API 调用**，禁止任何 Mock 数据！

---

## Gen404 (Python MAS - Different Track)

| 指标 | Gen404 | v12.0 Harness |
|------|--------|----------------|
| **综合评分** | **94.90** | 51.26 |
| 核心得分 | 77.0 | ~52 |
| 泛化得分 | 83.0 | ~52 |
| Token消耗 | 1.0 | ~43,000 |
| 评估标准 | 输出匹配 | 真实质量评估 |

**Note**: Gen404 uses mock tokens (1.0 per task) and output-matching evaluation. v12.0 uses real API and strict quality evaluation. They're different tracks.

---

## v12.0 Source

- `openclaw_native/harness_v12.py` - Stable baseline
- `openclaw_native/benchmark_results_v12_gen1.json` - Full results

---

*AutoMAS v12.0 - Stable Real API Harness*