# 📋 AutoMAS 项目导航索引

> 一站式了解项目结构和快速定位资源

---

## 🎯 我想...

| 需求 | 快速链接 |
|------|----------|
| **了解项目是什么** | [`README.md`](README.md) |
| **快速上手** | [`knowledge/QUICKSTART.md`](knowledge/QUICKSTART.md) |
| **理解系统架构** | [`knowledge/ARCHITECTURE.md`](knowledge/ARCHITECTURE.md) |
| **查找目录结构** | [`knowledge/TREE.md`](knowledge/TREE.md) |
| **浏览知识库** | [`knowledge/README.md`](knowledge/README.md) |
| **查看评测任务** | [`knowledge/benchmark/Benchmark_Tasks.md`](knowledge/benchmark/Benchmark_Tasks.md) |
| **了解有效策略** | [`knowledge/trends/Known_Trends.md`](knowledge/trends/Known_Trends.md) |
| **避免重复失败** | [`knowledge/lessons/Lessons_Learned.md`](knowledge/lessons/Lessons_Learned.md) |
| **找 Prompt 模板** | [`knowledge/prompts/Prompt_Library.md`](knowledge/prompts/Prompt_Library.md) |

---

## 🏆 当前冠军

**v31.0** — Composite **76.22**

| 维度 | 得分 |
|------|------|
| Core | 79.2 |
| Gen | 81.0 |
| Actionability | L4.13 |

关键发现: **5000 tokens** 是临界点，突破后 Gen 能力从 68.6 飙升到 81.0

---

## 📂 项目结构速览

```
mas_repo/
├── 📄 README.md              ← 项目入口
├── 📋 SUMMARY.md             ← 本文件 · 导航索引
│
├── 📁 src/                   ← 核心源码
│   ├── benchmark/           ← 15 个评测任务
│   ├── native/              ← OpenClaw Native MAS
│   │   ├── harness/         ← 各版本 harness (v31-v40+)
│   │   └── ...
│   └── legacy/              ← Python MAS 历史
│
├── 📁 knowledge/             ← 知识库
│   ├── README.md            ← 知识库索引
│   ├── TREE.md              ← 目录树可视化
│   ├── ARCHITECTURE.md      ← 系统架构图
│   ├── QUICKSTART.md        ← 快速上手指南
│   └── ...
│
├── 📁 results/              ← 评测结果
├── 📁 papers/               ← 论文资料
├── 📁 docs/                 ← 项目文档
├── 📁 archive/              ← 历史归档
└── 📁 datasets/             ← 数据集
```

---

## 🚀 快速开始

### 1. 运行基准测试

```bash
cd /root/.openclaw/workspace/mas_repo/src/native
python run_benchmark.py --version v31_0
```

### 2. 查看结果

```bash
cat results/*.json | python -m json.tool | less
```

### 3. 创建新版本

```bash
# 复制冠军版本
cp harness_v31_0.py harness_v42.py

# 修改策略参数
# 运行测试
python run_benchmark.py --version v42
```

---

## 📊 版本演进

```
v10 ──▶ v20 ──▶ v25 ──▶ v30 ──▶ v31 ──▶ v38
 │       │       │       │       │       │
48      58      57      67      76      72
                              🏆    冠军
```

里程碑:
- **v23**: 自适应格式选择 (58.30)
- **v29**: MAX 策略 (+13.85)
- **v31**: 5000 tokens 临界点 (**76.22** 🏆)
- **v37**: 扩展自评审失败 (69.07)

---

## 🔑 核心资源

| 资源 | 说明 |
|------|------|
| [`knowledge/QUICKSTART.md`](knowledge/QUICKSTART.md) | 5分钟快速上手 |
| [`knowledge/ARCHITECTURE.md`](knowledge/ARCHITECTURE.md) | 系统架构详解 |
| [`knowledge/trends/Known_Trends.md`](knowledge/trends/Known_Trends.md) | 已验证策略 |
| [`knowledge/lessons/Lessons_Learned.md`](knowledge/lessons/Lessons_Learned.md) | 失败教训 |
| [`papers/`](papers/) | 6篇研究论文 |

---

## 📞 联系

- **GitHub**: https://github.com/xiangbianpangde/mas-evolution-test

---

*最后更新: 2026-04-08*
