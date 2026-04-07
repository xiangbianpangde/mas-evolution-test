# v31.1 Results

> 基于 v31.0 冠军版本，新增答案保存功能

---

## 版本信息

| 属性 | 值 |
|------|-----|
| 版本 | v31.1 |
| 基础 | v31.0 (Composite 76.22) |
| 新增 | 答案保存功能 |
| 目标 | 验证保存机制，同时保持分数 |

---

## 目录结构

```
v31_1/
├── README.md              # 本文件
├── scores.json           # 最终分数摘要
├── detailed_results.json # 详细结果（含所有分数和元数据）
└── answers/              # 各任务答案 ⭐
    ├── core_001/
    │   ├── question.md    # 原始问题
    │   ├── answer.md      # 生成的答案
    │   └── evaluation.json # 评估详情
    ├── core_002/
    │   └── ...
    └── gen_001/
        └── ...
```

---

## 文件说明

### scores.json
最终分数摘要，包含：
- core_avg_score
- gen_avg_score  
- composite_score
- 任务级分数列表

### detailed_results.json
完整结果数据，包含：
- 所有分数
- 运行时间
- token 消耗
- 原始问题 (question)
- 评估理由 (evaluation_reasoning)

### answers/
每个任务的完整答案：
- **question.md**: 原始任务描述
- **answer.md**: 生成的完整答案
- **evaluation.json**: 评估详情（分数、理由等）

---

## 评估维度

| 维度 | 说明 | 评分范围 |
|------|------|---------|
| depth | 深度和分析水平 | 1-5 |
| completeness | 完整性和全面性 | 1-5 |
| actionability | 可操作性 | 1-5 |
| overall_score | 综合分数 | 0-100 |

---

## 运行 harness

```bash
cd /root/.openclaw/workspace/mas_repo
python src/native/harness/harness_v31_1.py
```

---

## 与 v31.0 的区别

| 功能 | v31.0 | v31.1 |
|------|-------|-------|
| 分数保存 | ✅ | ✅ |
| 答案保存 | ❌ | ✅ |
| 问题保存 | ❌ | ✅ |
| 评估理由保存 | ❌ | ✅ |

---

*创建: 2026-04-07*
