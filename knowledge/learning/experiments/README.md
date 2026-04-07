# 🔬 Experiments

实验中获得的知识

## 目录
- [v31_Success_Factors.md](v31_Success_Factors.md) - v31.0 成功因素分析

---

## 贡献格式

```markdown
## [实验名称] - YYYY-MM-DD

### 问题
我们要解决什么问题？

### 假设
我们假设什么会有效？

### 方法
我们怎么测试的？

### 结果
发生了什么？

### 洞察
我们学到了什么？
```

---

## 按时间索引

| 日期 | 实验 | 关键发现 |
|------|------|---------|
| 2026-04-07 | v31.0 Token Budget | 5000 tokens 是最佳点 |
| 2026-04-07 | v33.0 MAX-3 | 3次运行反而增加方差 |
| 2026-04-07 | v37.0 Extended Critique | 扩展到所有任务 → 失败 |

## v31.1 - Answer Saving Capability Test - 2026-04-07

### Configuration
- Based on: v31.0 (76.22)
- New feature: Save answers to results/v31.1/answers/
- MAX-2 strategy, 5000 tokens

### Results
| Metric | v31.1 | v31.0 | Change |
|--------|-------|-------|--------|
| Composite | **69.25** | 76.22 | **-6.97** |
| Core | 65.2 | 79.2 | -14.0 |
| Gen | 80.4 | 81.0 | -0.6 |

### Analysis
- **Regression**: Score dropped from 76.22 to 69.25
- Core tasks regressed significantly (65.2 vs 79.2)
- Gen tasks similar (80.4 vs 81.0)
- **Possible causes**: API variance (MAX-2 should reduce this), or slight prompt differences

### Answers Saved
- 15 tasks × 3 files each = 45 files
- Location: results/v31.1/answers/

### Conclusion
- v31.0 remains champion
- v31.1 demonstrated answer saving works
- Next: Re-run v31.1 to confirm if regression is variance or systematic
