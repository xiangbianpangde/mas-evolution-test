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
│   想积累新知?  →  去 learning/ 目录                      │
│                                                         │
└─────────────────────────────────────────────────────────┘

┌──────────────────┐    ┌──────────────────┐
│   🏗️ architecture │    │   🧠 prompts     │
│   系统架构        │    │   Prompt 模板    │
│                   │    │                  │
│  • Multi-Agent   │    │  • Library.md    │
│  • Harness Deep  │    └──────────────────┘
└──────────────────┘

┌──────────────────┐    ┌──────────────────┐
│   📈 trends       │    │   📝 lessons     │
│   已验证趋势      │    │   失败教训       │
│                   │    │                  │
│  • Known_Trends  │    │  • Learned.md    │
└──────────────────┘    └──────────────────┘

┌──────────────────┐    ┌──────────────────┐
│   🔬 research     │    │   🎨 design      │
│   网络研究        │    │   人机设计       │
│                   │    │                  │
│  • Harness_Eng   │    │  • Human_Centric │
└──────────────────┘    └──────────────────┘

┌──────────────────┐    ┌──────────────────┐
│   📊 benchmark   │    │   📖 learning ⭐  │
│   评测任务        │    │   持续学习       │
│                   │    │                  │
│  • Tasks.md      │    │  • experiments   │
└──────────────────┘    │  • discoveries   │
                        │  • patterns      │
                        │  • sources       │
                        └──────────────────┘
```

---

## 📂 完整目录结构

```
knowledge/
├── 🏗️ architecture/      - 系统架构与设计模式
│   ├── README.md
│   ├── Multi_Agent_Patterns.md      - 编排模式
│   └── Harness_Engineering_Deep.md   - 深度研究
├── 🧠 prompts/           - Prompt 模板库
│   ├── README.md
│   └── Library.md
├── 📈 trends/            - 已验证的有效策略
│   ├── README.md
│   └── Known_Trends.md
├── 📝 lessons/           - 失败教训总结
│   ├── README.md
│   └── Learned.md
├── 🔬 research/          - 网络研究成果
│   ├── README.md
│   └── Harness_Engineering.md
├── 🎨 design/            - 人机交互设计
│   ├── README.md
│   └── Human_Centric_Design.md
└── 📖 learning/          - 持续学习库 ⭐
    ├── README.md
    ├── experiments/       - 实验知识
    │   └── README.md
    ├── discoveries/      - 新发现
    │   └── README.md
    ├── patterns/         - 反复出现的模式
    │   └── README.md
    └── sources/          - 外部资源
        └── README.md
```

---

## 🎯 按目的查找

| 目的 | 去哪里 |
|------|--------|
| 了解 Multi-Agent 编排模式 | `architecture/Multi_Agent_Patterns.md` |
| 学习 Harness Engineering | `architecture/Harness_Engineering_Deep.md` |
| 查看有哪些测试任务 | `benchmark/Tasks.md` |
| 找 Prompt 模板 | `prompts/Library.md` |
| 了解什么策略有效 | `trends/Known_Trends.md` |
| 避免重复失败 | `lessons/Learned.md` |
| 学习人机设计原则 | `design/Human_Centric_Design.md` |
| **积累新知识** | `learning/` ⭐ |

---

## 🔑 核心发现 (快速摘要)

### ✅ 有效策略
- **Core research**: 需要自反射
- **Token budget**: 5000 最佳
- **评估器**: code 从宽，research 从严

### ❌ 失败教训
- **Gen research**: 禁止自反射 (破坏结构)
- **Python harness**: 非真实 API，作弊
- **v5.0 Native**: 超时/解析问题

### 🏗️ 架构模式
- **Orchestrator-Worker**: Supervisor 分解 → Workers 执行
- **Review Chain**: 高风险输出需要评审
- **深度优先**: 一次一个功能

### 🎨 设计原则
- **渐进式披露**: 先摘要后细节
- **视觉分组**: 相关信息放一起
- **及时反馈**: 操作后立即显示结果

---

## 📖 持续学习 (learning/)

这是新增的专门用于**不断积累知识**的目录：

- `experiments/` - 实验中获得的知识
- `discoveries/` - 新发现和洞察
- `patterns/` - 反复出现的模式
- `sources/` - 有价值的外部资源

**使用方式**: 每次实验或研究后，将有价值的发现添加到相应文件中。
