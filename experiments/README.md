# Experiment Log - 实验追踪模板

## 实验 #001

**日期**: 2026-04-07
**版本**: v31_0
**状态**: 🏆 CHAMPION

### 假设
5000 tokens + MAX-2 + self-reflect on core 是最佳平衡

### 变量

| 参数 | 值 |
|------|-----|
| research_tokens | 5000 |
| code_tokens | 5000 |
| max_runs | 2 |
| temperature | 0.7 |
| self_reflect | core_only |

### Baseline
N/A (first comprehensive test)

### 结果

| 指标 | 分数 |
|------|------|
| Core | 79.2 |
| Gen | 81.0 |
| Actionability | 4.13 |
| **Composite** | **76.22** |

### 分析
这是一个强有力的基线。5000 tokens提供了足够的生成空间，MAX-2策略在质量和成本之间取得了平衡。self-reflect只在core任务上应用，避免了对代码任务的负面影响。

### 结论
✅ 验证了假设。这是新的基线。

### 下一步
探索是否可以通过以下方式改进：
1. 增加 tokens 到 6000
2. 增加 max_runs 到 3
3. 调整 temperature

---

## 实验 #002

**日期**: 2026-04-07
**版本**: v31_1
**状态**: ❌ REGRESSION

### 假设
(未记录 - 问题！)

### 变量

| 参数 | 值 |
|------|-----|
| research_tokens | ? |
| code_tokens | ? |
| max_runs | ? |
| temperature | ? |
| self_reflect | ? |

### Baseline
v31_0 (76.22)

### 结果

| 指标 | v31_0 | v31_1 | 变化 |
|------|--------|--------|------|
| Core | 79.2 | 70.0 | -9.2 |
| Gen | 81.0 | 72.0 | -9.0 |
| **Composite** | **76.22** | **69.25** | **-6.97** |

### 分析
(未完成 - 需要调查具体参数变化)

### 教训
⚠️ 每次实验必须记录假设和变量！

### 下一步
撤销所有变更，回到 v31_0

---

## 模板使用说明

### 创建新实验

1. 复制以下模板到新文件：`experiments/exp_XXX.md`
2. 填写所有字段
3. 提交到 Git

### 模板

```markdown
## 实验 #XXX

**日期**: YYYY-MM-DD
**版本**: vXX
**状态**: ⏳ RUNNING / ✅ SUCCESS / ❌ FAILED

### 假设
[描述这次实验要验证什么]

### 变量

| 参数 | 值 |
|------|-----|
| research_tokens | X |
| code_tokens | X |
| max_runs | X |
| temperature | X |
| self_reflect | X |

### Baseline
[对比版本和分数]

### 结果

| 指标 | Baseline | 实验 | 变化 |
|------|----------|------|------|
| Core | A | B | ±X |
| Gen | A | B | ±X |
| **Composite** | **X** | **X** | **±X** |

### 分析
[分析结果]

### 结论
[是否验证了假设]

### 下一步
[基于这个结果，下一步实验是什么]
```

---

## 快速参考

### 分数变化判断
- **> 5% 提升**：✅ 成功
- **± 2-5%**：需更多数据
- **< -5%**：❌ 回退
- **< -10%**：🚨 严重问题

### 参数调整规则
- **只调一个**：每次只改一个参数
- **记录基线**：改动前先记录当前分数
- **对比版本**：始终与 v31_0 对比

---

*Last updated: 2026-04-09*
