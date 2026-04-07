# 📚 AutoMAS Knowledge Base

> 人类视角：视觉层级 + 关联感知  
> AI 视角：文件名搜索 + 内容语义

---

## 🗺️ 知识地图

```
┌─────────────────────────────────────────────────────────┐
│                    HOW TO NAVIGATE                       │
├─────────────────────────────────────────────────────────┤
│                                                         │
│   想快速查找?  →  搜索文件名 (AI 优先)                   │
│   想了解结构?  →  看下面的视觉地图                        │
│   想学习主题?  →  按目录浏览                             │
│   想引用原文?  →  去 sources/ 目录                       │
│   想看精炼模式? →  去 patterns/ 目录                     │
│                                                         │
└─────────────────────────────────────────────────────────┘

┌──────────────────┐    ┌──────────────────┐
│   📖 sources     │    │   📝 patterns    │
│   外部资源原文    │    │   模式库         │
│                   │    │                  │
│  • OpenAI       │    │  • 14 patterns   │
│  • Anthropic    │    │  • 来源索引       │
│  • Martin Fowler│    └──────────────────┘
│  • Google Cloud  │
└──────────────────┘

┌──────────────────┐    ┌──────────────────┐
│   📚 reference   │    │   📈 trends      │
│   参考资料       │    │   已验证策略      │
│                   │    │                  │
│  • Deep Research │    │  • Known Trends  │
└──────────────────┘    └──────────────────┘

┌──────────────────┐    ┌──────────────────┐
│   📝 lessons     │    │   🧠 prompts    │
│   失败教训       │    │   Prompt模板    │
│                   │    │                  │
│  • Learned.md    │    │  • Library.md   │
└──────────────────┘    └──────────────────┘

┌──────────────────┐    ┌──────────────────┐
│   📊 benchmark   │    │   🎨 design     │
│   评测任务       │    │   人机设计       │
│                   │    │                  │
│  • Tasks.md      │    │  • Human_Centric│
└──────────────────┘    └──────────────────┘
```

---

## 📂 完整目录结构

```
knowledge/
├── README.md              # 本文件
│
├── 📖 sources/           # 外部资源原文归档 ⭐ 第一手
│   ├── README.md
│   ├── OpenAI_Harness_Engineering.md
│   ├── Anthropic_Effective_Harnesses.md
│   ├── Martin_Fowler_Harness_Engineering.md
│   └── Google_Cloud_Agent_Patterns.md
│
├── 📝 patterns/          # 模式库 ⭐ 精华提炼
│   ├── README.md
│   └── patterns_index.md
│
├── 📚 reference/          # 参考资料（二手整理）
│   ├── README.md
│   ├── Harness_Engineering_Deep.md
│   └── Multi_Agent_Patterns.md
│
├── 📊 benchmark/          # 评测任务定义
│   ├── README.md
│   └── Tasks.md
│
├── 📈 trends/            # 已验证的有效策略
│   ├── README.md
│   └── Known_Trends.md
│
├── 📝 lessons/            # 失败教训总结
│   ├── README.md
│   └── Learned.md
│
├── 🧠 prompts/            # Prompt 模板库
│   ├── README.md
│   └── Library.md
│
└── 🎨 design/             # 人机交互设计
    ├── README.md
    └── Human_Centric_Design.md
```

---

## 🎯 按目的查找

| 目的 | 去哪里 |
|------|--------|
| 引用原文原文 | `sources/` ⭐ |
| 查找模式 | `patterns/` |
| 综合研究 | `reference/` |
| 了解测试任务 | `benchmark/Tasks.md` |
| 找 Prompt 模板 | `prompts/Library.md` |
| 了解什么策略有效 | `trends/Known_Trends.md` |
| 避免重复失败 | `lessons/Learned.md` |
| 学习人机设计原则 | `design/Human_Centric_Design.md` |

---

## 📐 目录职责定义

| 目录 | 职责 | 内容性质 | 更新频率 |
|------|------|---------|---------|
| `sources/` | 外部资源归档 | 第一手原文 | 偶尔新增 |
| `patterns/` | 模式提炼 | 从sources提取 | 逐步完善 |
| `reference/` | 综合整理 | 第二手综合 | 偶尔更新 |
| `trends/` | 验证有效策略 | 来自实验 | 实验后更新 |
| `lessons/` | 失败教训 | 来自实验 | 实验后更新 |
| `prompts/` | Prompt模板 | 模板 | 偶尔调整 |

---

## 🔑 核心发现 (快速摘要)

### ✅ 有效策略
- **Core research**: 需要自反射
- **Token budget**: 5000 最佳
- **评估器**: code 从宽，research 从严

### ❌ 失败教训
- **Gen research**: 禁止自反射 (破坏结构)
- **Python harness**: 非真实 API，作弊
- **MAX-3**: 3次运行反而增加方差

### 🏗️ 架构模式
- **Review & Critique**: Generator → Critic → 迭代
- **Depth-first**: 一次一个功能
- **Keep Quality Left**: 尽早发现问题

---

*最后更新: 2026-04-07*
