# 📋 AutoMAS 项目导航

> 快速了解项目结构和找到你需要的内容

---

## 🏠 项目首页
- **[README.md](README.md)** - 项目介绍、快速开始

---

## 📚 知识库 (knowledge/)
探索和学习的地方

| 目录 | 内容 |
|------|------|
| [knowledge/](knowledge/README.md) | 完整知识库索引 |
| [architecture/](knowledge/architecture/README.md) | 系统架构与设计模式 |
| [learning/](knowledge/learning/README.md) | 持续学习 (实验/发现/模式) |
| [trends/](knowledge/trends/README.md) | 已验证的有效策略 |
| [lessons/](knowledge/lessons/README.md) | 失败教训 |
| [prompts/](knowledge/prompts/README.md) | Prompt 模板库 |
| [benchmark/](knowledge/benchmark/README.md) | 评测任务说明 |

---

## 🔬 源码 (src/)
开发和测试的地方

| 目录 | 内容 |
|------|------|
| [src/benchmark/](src/benchmark/) | 评测任务定义 (tasks_v2.py) |
| [src/native/harness/](src/native/harness/) | 当前 harness (v31, v37, v38) |
| [src/native/soul/](src/native/soul/) | Agent SOUL 定义 |
| [src/legacy/](src/legacy/) | Python MAS 历史代码 |

---

## 📊 评测结果 (results/)

| 最新结果 | 分数 |
|---------|------|
| v31.0 | Composite 76.22 (冠军) |
| v37.0 | Composite 69.07 (失败) |

查看所有结果: [results/](results/)

---

## 📰 文档 (docs/)

| 文档 | 内容 |
|------|------|
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | 系统架构详解 |
| [EVOLUTION_HISTORY.md](docs/EVOLUTION_HISTORY.md) | 完整演进历史 |
| [CONVERGENCE_REPORT.md](docs/CONVERGENCE_REPORT.md) | 收敛分析 |

---

## 📦 历史归档 (archive/)

- `archive/evaluate_scripts/` - 旧版评测脚本 (gen1-gen400+)
- `archive/python_mas/` - Python MAS 版本历史
- `archive/reports/` - 历史报告

---

## 📖 论文 (papers/)

- 6篇 AutoMAS 相关论文

---

## 🚀 快速开始

### 1. 想了解项目是什么？
→ [README.md](README.md)

### 2. 想了解当前最优策略？
→ [knowledge/trends/Known_Trends.md](knowledge/trends/Known_Trends.md)

### 3. 想看最新实验结果？
→ [results/](results/)

### 4. 想开发新 harness？
→ [src/native/harness/](src/native/harness/)

### 5. 想学习相关知识？
→ [knowledge/learning/](knowledge/learning/)

---

## 🔑 当前状态

| 指标 | 值 |
|------|-----|
| 冠军版本 | v31.0 |
| 最高分数 | 76.22 |
| 演进状态 | 暂停 (等待 Native MAS 重启) |
| 知识库 | 已建立 |

---

*最后更新: 2026-04-07*
