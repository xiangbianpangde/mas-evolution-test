# 🚀 AutoMAS 快速上手指南

> 5 分钟了解 AutoMAS · 10 分钟跑通基准测试

---

## 📋 目录

1. [项目是什么？](#1-项目是什么)
2. [核心概念](#2-核心概念)
3. [快速开始](#3-快速开始)
4. [运行基准测试](#4-运行基准测试)
5. [理解评测结果](#5-理解评测结果)
6. [常见任务](#6-常见任务)
7. [故障排除](#7-故障排除)

---

## 1. 项目是什么？

**AutoMAS** 是一个全自动化多智能体系统（Multi-Agent System）评测与演进框架。

简单说：
- 🤖 有 15 个标准测试任务
- 📊 自动评估 Agent 输出质量（深度、完整性、可操作性）
- 🔄 根据结果自动改进 Agent 架构
- 🏆 目标是让 AI 自主进化到满分

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  15 个任务   │ ──▶ │   评测运行   │ ──▶ │   得分输出   │
└─────────────┘    └─────────────┘    └─────────────┘
                                            │
                                            ▼
                   ┌─────────────┐    ┌─────────────┐
                   │  版本迭代    │ ◀──│  分析结果   │
                   └─────────────┘    └─────────────┘
```

---

## 2. 核心概念

### 2.1 三维评分系统

每个任务输出从 3 个维度评分：

| 维度 | 说明 | 评分 |
|------|------|------|
| **Depth** | 分析有多深？ | L1-L5 |
| **Completeness** | 覆盖完整吗？ | L1-L5 |
| **Actionability** | 能落地执行吗？ | L1-L5 |

### 2.2 任务类型

| 类型 | 数量 | 例子 |
|------|------|------|
| **research** | 7 个 | 分析 Transformer 优化方案 |
| **code** | 5 个 | 实现滑动日志解析器 |
| **review** | 3 个 | 评审系统架构设计 |

### 2.3 关键术语

| 术语 | 含义 |
|------|------|
| **Harness** | Agent 评测脚手架/框架 |
| **Champion** | 当前最优版本 |
| **MAX 策略** | 运行多次取最优 |
| **Self-reflect** | Agent 自我反思 |
| **Composite** | 综合评分 |

---

## 3. 快速开始

### 3.1 查看项目结构

```bash
cd /root/.openclaw/workspace/mas_repo

# 查看目录结构
ls -la

# 查看源码
ls src/native/harness/
```

### 3.2 查看当前冠军

```bash
# 冠军版本是 v31.0，得分 76.22
cat src/native/harness/harness_v31_0.py | head -50
```

### 3.3 查看评测任务

```bash
# 15 个标准任务
cat src/benchmark/tasks_v2.py | grep -A3 '"id":'
```

---

## 4. 运行基准测试

### 4.1 运行冠军版本 (v31.0)

```bash
cd /root/.openclaw/workspace/mas_repo

# 运行基准测试
python src/native/run_benchmark.py --version v31_0

# 或者直接运行 harness
cd src/native
python -m harness.harness_v31_0
```

### 4.2 运行自定义版本

```bash
# 如果你修改了代码，想测试新版本
cd src/native
python -m harness.harness_v38

# 运行演进引擎
python harness_evolution.py
```

### 4.3 查看结果

```bash
# 查看最新结果
cat results/*.json | python -m json.tool | less

# 对比两个版本
python compare_results.py --v1 v31 --v2 v38
```

---

## 5. 理解评测结果

### 5.1 评分结构

```json
{
  "version": "v31.0",
  "composite": 76.22,
  "core_score": 79.2,
  "gen_score": 81.0,
  "tasks": {
    "core_001": {"depth": 4, "completeness": 4, "actionability": 4},
    "core_002": {"depth": 4, "completeness": 5, "actionability": 4},
    ...
  }
}
```

### 5.2 评分等级

| 等级 | 含义 | 典型表现 |
|------|------|----------|
| L5 | 极佳 | 面面俱到，可直接落地 |
| L4 | 良好 | 有深度，基本可用 |
| L3 | 中等 | 有覆盖但不深入 |
| L2 | 较差 | 缺失较多 |
| L1 | 差 | 几乎无用 |

### 5.3 分数计算

```
Composite = (Core_Score × 0.5) + (Gen_Score × 0.3) + (Actionability × 0.2)
```

---

## 6. 常见任务

### 6.1 添加新测试任务

编辑 `src/benchmark/tasks_v2.py`:

```python
{
    "id": "core_011",
    "type": "research",      # research / code / review
    "difficulty": 8,         # 1-10 难度
    "query": "你的新问题",
    "expected_outputs": ["输出类型1", "输出类型2"]
}
```

### 6.2 创建新 Agent 版本

```bash
# 复制冠军版本作为模板
cd src/native/harness
cp harness_v31_0.py harness_v42.py

# 修改策略参数
# 然后运行测试
cd ../..
python run_benchmark.py --version v42
```

### 6.3 分析失败任务

```bash
# 查看失败任务详情
python -c "
import json
with open('results/benchmark_results_v38_gen1.json') as f:
    r = json.load(f)
    for t in r['tasks']:
        if t['score'] < 50:
            print(f'{t[\"id\"]}: {t[\"score\"]} - {t[\"error\"]}')"
```

---

## 7. 故障排除

### 7.1 API 错误

```
症状: HTTP 500 errors
解决: API 不稳定，使用内置重试机制
```

### 7.2 OOM (内存不足)

```
症状: 进程被 killed
解决: 减少 MAX_RUNS 或降低 token 数量
```

### 7.3 版本路径错误

```
症状: Results directory not found
解决: 检查 RESULTS_DIR 配置是否指向 4 层父目录
```

---

## 🗺️ 知识库导航

| 需求 | 去哪里 |
|------|--------|
| 想看完整架构图 | `knowledge/ARCHITECTURE.md` |
| 想看目录树 | `knowledge/TREE.md` |
| 想找 Prompt 模板 | `knowledge/prompts/Prompt_Library.md` |
| 想了解有效策略 | `knowledge/trends/Known_Trends.md` |
| 想看失败教训 | `knowledge/lessons/Lessons_Learned.md` |
| 想学习外部资源 | `knowledge/sources/` |

---

## 📞 快速命令参考

```bash
# 列出所有 harness 版本
ls src/native/harness/harness_v*.py

# 查看演进状态
cat src/native/evolution_state.json

# 查看知识库
ls knowledge/

# 运行基准测试
cd src/native && python run_benchmark.py

# 查看帮助
python run_benchmark.py --help
```

---

**下一步:**
1. 📖 阅读 `ARCHITECTURE.md` 理解系统架构
2. 📊 查看 `results/` 目录了解历史得分
3. 🔬 修改 `harness_v31_0.py` 开始你的实验

---

*最后更新: 2026-04-08*
