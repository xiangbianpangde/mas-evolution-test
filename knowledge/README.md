# 📚 AutoMAS 知识库索引

> 入口 · 导航 · 快速定位

---

## 🎯 快速入口

| 我想... | 去哪里 |
|---------|--------|
| 🔍 了解项目是什么 | [`TREE.md`](TREE.md) · 顶层总览 |
| 🗺️ 找到具体文件位置 | [`TREE.md`](TREE.md) · 目录树 |
| 📐 理解系统架构 | [`ARCHITECTURE.md`](ARCHITECTURE.md) · 架构图 |
| 🚀 快速上手 | [`QUICKSTART.md`](QUICKSTART.md) · 5分钟指南 |
| 🏆 了解冠军版本 | [`src/native/harness/harness_v31_0.py`](src/native/harness/harness_v31_0.py) |
| 📊 查看评测结果 | [`results/`](results/) |

---

## 📂 知识库结构图

```
knowledge/
│
├── 🧭 导航文件
│   ├── README.md          ← 📍 你在这里 · 索引入口
│   ├── TREE.md            ← 完整目录树可视化
│   ├── ARCHITECTURE.md    ← 系统架构图
│   └── QUICKSTART.md      ← 快速上手指南
│
├── 📖 sources/            ← ⭐ 第一手 · 外部资源原文
│   ├── OpenAI_Harness_Engineering.md
│   ├── Anthropic_Effective_Harnesses.md
│   ├── Martin_Fowler_Harness_Engineering.md
│   └── Google_Cloud_Agent_Patterns.md
│
├── 📚 reference/          ← 第二手 · 综合参考资料
│   ├── Harness_Engineering_Deep.md
│   └── Multi_Agent_Patterns.md
│
├── 📝 patterns/           ← 精华提炼 · 模式库
│   └── patterns_index.md
│
├── 📊 benchmark/          ← 评测任务说明
│   └── Benchmark_Tasks.md
│
├── 📈 trends/             ← 已验证有效策略
│   └── Known_Trends.md
│
├── 📝 lessons/            ← 失败教训总结
│   └── Lessons_Learned.md
│
├── 🧠 prompts/             ← Prompt 模板库
│   └── Prompt_Library.md
│
├── 🎨 design/              ← 人机交互设计
│   └── Human_Centric_Design.md
│
└── 📚 learning/            ← 学习与发现
    ├── discoveries/
    ├── experiments/
    │   ├── v38_analysis.md
    │   ├── v40_strategy.md
    │   └── v41_adaptive_reflection.md
    └── patterns/
```

---

## 🔑 按目的查找

| 目的 | 推荐文件 |
|------|----------|
| **第一次接触项目** | `QUICKSTART.md` + `TREE.md` |
| **理解系统架构** | `ARCHITECTURE.md` |
| **找到源码文件** | `TREE.md` → `src/` |
| **了解评测任务** | `benchmark/Benchmark_Tasks.md` |
| **查看有效策略** | `trends/Known_Trends.md` |
| **避免重复失败** | `lessons/Lessons_Learned.md` |
| **找 Prompt 模板** | `prompts/Prompt_Library.md` |
| **学习外部资源** | `sources/` 目录 |
| **引用架构模式** | `reference/Multi_Agent_Patterns.md` |
| **了解演进历史** | `papers/` 目录 |

---

## 🏆 核心发现速查

### ✅ 有效策略
| 发现 | 详情 |
|------|------|
| **Token 临界点** | 5000 tokens 突破 Gen 能力 (68.6→81.0) |
| **MAX 策略** | 运行 2 次取最优，可提升 13+ 分 |
| **Research 自反射** | 有利，提升深度 |
| **Code 禁止自反射** | 必须！自反射会破坏代码结构 |

### ❌ 失败教训
| 教训 | 详情 |
|------|------|
| **Gen code 自反射** | gen_002 从 65→15，灾难性失败 |
| **MAX-3** | 3次运行反而增加方差，diminishing returns |
| **扩展自评审到全部** | v37: 76.22→69.07，失败 |

### 📊 评分标准
| 维度 | L4 (良好) 标准 |
|------|----------------|
| Depth | 3-4层分析深度 |
| Completeness | 覆盖 80%+ 维度 |
| Actionability | 步骤清晰可直接执行 |

---

## 📊 版本排行榜

| 版本 | Composite | Core | Gen | 备注 |
|------|-----------|------|-----|------|
| **v31.0** | **76.22** | **79.2** | **81.0** | 🏆 冠军 |
| v38 | 72.16 | - | - | 低于冠军 |
| v37 | 69.07 | - | - | 失败 |
| v33 | 73.44 | 79.4 | 75.2 | - |
| v30 | 67.19 | 73.0 | 68.6 | 前冠军 |

---

## 🔗 相关链接

- **GitHub**: https://github.com/xiangbianpangde/mas-evolution-test
- **源码**: [`src/`](src/)
- **评测结果**: [`results/`](results/)
- **论文**: [`papers/`](papers/)
- **文档**: [`docs/`](docs/)

---

## 📝 更新日志

| 日期 | 更新内容 |
|------|----------|
| 2026-04-08 | 新增 TREE.md, ARCHITECTURE.md, QUICKSTART.md |
| 2026-04-07 | 初始化知识库 |

---

*最后更新: 2026-04-08*
