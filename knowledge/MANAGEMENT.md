# 📋 MANAGEMENT - 文件管理与记录方式

> 项目文件的组织、管理和维护规范

---

## 📋 目录

- [文件组织原则](#文件组织原则)
- [目录结构说明](#目录结构说明)
- [版本控制策略](#版本控制策略)
- [GitHub 同步规范](#github-同步规范)
- [长时记忆机制](#长时记忆机制)
- [知识归档流程](#知识归档流程)

---

## 🔑 文件组织原则 <a name="文件组织原则"></a>

### 核心原则

1. **语义清晰**: 目录和文件名反映内容用途
2. **层级扁平**: 避免过深嵌套，重要文件靠前
3. **单一真相**: 每个信息只有一处权威存储
4. **可追溯**: 所有变更通过 Git 记录

### 命名最佳实践

```
✅ good:  benchmark_results_v31_0_gen1.json
❌ bad:   result_v31_final_real.json
✅ good:  harness_v31_0.py
❌ bad:   harness_new.py
```

### 文件类型分组

| 类型 | 存储位置 | 说明 |
|------|----------|------|
| 源码 | `src/` | 可执行代码 |
| 结果 | `results/` | 只读数据 |
| 知识 | `knowledge/` | 文档和经验 |
| 归档 | `archive/` | 历史版本 |

---

## 📁 目录结构说明 <a name="目录结构说明"></a>

```
mas_repo/
├── src/                         # 🌟 核心源码（可执行）
│   ├── native/                   # OpenClaw Native MAS
│   │   ├── harness/              # 评测脚本（活跃版本）
│   │   ├── harness_old/          # 历史版本（已归档）
│   │   └── SOUL.md              # Agent 灵魂定义
│   ├── legacy/                   # Python MAS 历史
│   └── agents/                   # Agent 团队定义
│
├── results/                      # 📊 评测结果（只读数据）
│   ├── benchmarks/               # 基准测试结果
│   │   ├── checkpoint/          # 断点续算状态
│   │   └── benchmark_results_*.json
│   └── evolution/               # 演进过程日志
│
├── knowledge/                    # 📚 知识库（文档）
│   ├── docs/                     # 核心文档
│   ├── lessons/                 # 经验教训
│   └── trends/                  # 趋势分析
│
├── archive/                      # 📦 历史归档（压缩/冻结）
│   ├── evaluate_scripts/        # 旧评测脚本
│   └── python_mas/              # Python MAS 版本
│
└── papers/                      # 📄 研究资料
```

---

## 🔢 版本控制策略 <a name="版本控制策略"></a>

### Git 分支模型

```
main (稳定版本)
 ├── v31_0 (冠军版本)
 ├── v38 (实验版本)
 └── ...

feature/* (实验分支)
 └── ...
```

### Commit 规范

**格式**: `<type>(<scope>): <description>`

**Type 类型**:
| Type | 说明 | 示例 |
|------|------|------|
| `feat` | 新功能 | `feat(harness): add MAX-3 strategy` |
| `fix` | Bug 修复 | `fix(benchmark): token calculation` |
| `docs` | 文档更新 | `docs: update README structure` |
| `test` | 测试相关 | `test: add benchmark for v42` |
| `refactor` | 重构 | `refactor: split supervisor logic` |
| `chore` | 杂项 | `chore: cleanup old files` |

**示例**:
```bash
git commit -m "feat(harness_v31): add 5000 tokens as default

- Token count increased from 2500 to 5000
- Gen score improved from 68.6 to 81.0
- BREAKING: runtime increased by 40%

Closes #31"
```

### Tag 规范

```bash
# 版本 Tag
git tag -a v31.0 -m "Champion: 5000 tokens breakthrough"
git push origin v31.0

# 里程碑 Tag
git tag -a v3.0-paradigm-converged -m "MAX strategy confirmed optimal"
```

---

## 🔄 GitHub 同步规范 <a name="github-同步规范"></a>

### 仓库信息

- **URL**: https://github.com/xiangbianpangde/mas-evolution-test
- **主要用途**: 外部观察者查看实验状态

### 同步策略

| 文件类型 | 同步优先级 | 说明 |
|----------|------------|------|
| README.md | 最高 | 永远保持最新 |
| results/benchmarks/*.json | 高 | 评测结果必须同步 |
| knowledge/docs/*.md | 高 | 重要文档同步 |
| src/native/harness/*.py | 中 | 源码同步 |
| archive/* | 低 | 可选同步 |

### 同步频率

| 场景 | 触发条件 | 频率 |
|------|----------|------|
| 基准测试完成 | 每次完整运行后 | 立即 |
| 版本更新 | commit 后 | 批量 |
| 文档更新 | 重要变更后 | 批量 |

### 不同步的内容

```gitignore
# 本地临时文件
*.pyc
__pycache__/
*.log.local

# 大型数据文件
*.json.bak
results/benchmarks/checkpoint/

# 个人配置
.env
config/local_*.yaml
```

---

## 🧠 长时记忆机制 <a name="长时记忆机制"></a>

### 记忆层次结构

```
┌─────────────────────────────────────────────┐
│  MEMORY.md (工作区根目录)                      │
│  ├── 长期记忆：重要决策、洞见、偏好              │
│  └── 跨会话上下文：当前项目状态                 │
├─────────────────────────────────────────────┤
│  memory/YYYY-MM-DD.md (每日笔记)               │
│  ├── 当日工作记录                             │
│  ├── 遇到的问题和解决方案                      │
│  └── 临时想法和待办                           │
├─────────────────────────────────────────────┤
│  mas_repo/knowledge/ (项目知识库)              │
│  ├── lessons/Lessons_Learned.md              │
│  │   └── 永久经验：失败教训、成功模式           │
│  ├── trends/Known_Trends.md                   │
│  │   └── 已验证策略和趋势                      │
│  └── docs/EVOLUTION_HISTORY.md                │
│      └── 完整演进历史                          │
└─────────────────────────────────────────────┘
```

### 记忆更新规则

| 场景 | 记忆位置 | 更新时机 |
|------|----------|----------|
| 重要决策 | `MEMORY.md` | 决策时 |
| 每日工作 | `memory/YYYY-MM-DD.md` | 每日结束时 |
| 实验失败教训 | `knowledge/lessons/` | 复盘时 |
| 版本策略洞见 | `knowledge/trends/` | 发现时 |
| 完整演进记录 | `knowledge/docs/` | 每次运行后 |

### 记忆检索

**问题 → 记忆位置映射**:

| 问题类型 | 先查哪里 |
|----------|----------|
| 项目是什么 | `README.md` |
| 如何运行测试 | `knowledge/QUICKSTART.md` |
| 为什么 v31 是冠军 | `knowledge/docs/EVOLUTION_HISTORY.md` |
| 代码任务注意什么 | `knowledge/lessons/Lessons_Learned.md` |
| 当前最佳策略是什么 | `knowledge/trends/Known_Trends.md` |
| 最近发生了什么 | `memory/YYYY-MM-DD.md` |

---

## 📚 知识归档流程 <a name="知识归档流程"></a>

### 实验完成后的归档步骤

```
1. 保存原始结果
   results/benchmarks/benchmark_results_v38_gen1.json
   
2. 提取关键信息到摘要
   results/benchmarks/results_v38.txt
   
3. 记录到演进历史
   knowledge/docs/EVOLUTION_HISTORY.md
   
4. 更新已知趋势
   knowledge/trends/Known_Trends.md
   
5. 如果失败，记录教训
   knowledge/lessons/Lessons_Learned.md
   
6. 归档源码（如果是新版本）
   src/native/harness/harness_v38.py → harness_old/
   
7. 清理临时文件
   __pycache__/, *.pyc, *_checkpoint.json
```

### 归档清单 (Pre-Experiment Checklist)

在启动实验前，确认以下文件就位：

```markdown
- [ ] 任务定义: src/benchmark/tasks_v2.py
- [ ] Harness 脚本: src/native/harness/harness_vNN.py
- [ ] 结果目录: results/benchmarks/
- [ ] 日志目录: results/evolution/
- [ ] Checkpoint 目录: results/benchmarks/checkpoint/
- [ ] Git 工作区: 无未提交更改
```

### 归档验证

```bash
# 检查必要文件
ls results/benchmarks/benchmark_results_v<VERSION>_gen1.json

# 检查 Git 状态
git status

# 检查知识库更新
git diff knowledge/
```

---

## 📊 容量管理

### 大文件处理

| 文件类型 | 大小 | 处理方式 |
|----------|------|----------|
| benchmark_results_*.json | ~50KB | Git 追踪 |
| *_benchmark.log | ~1MB | 本地保留 |
| __pycache__/*.pyc | ~100KB | .gitignore |
| archive/* | ~10MB | 压缩归档 |

### 清理规则

| 文件类型 | 何时清理 | 清理方式 |
|----------|----------|----------|
| `*_checkpoint.json` | 实验完全结束 | 删除 |
| `*.pyc` | 任何时候 | 删除 |
| `__pycache__/` | 任何时候 | 删除整个目录 |
| 超过 6 个月的 .log | 6 个月后 | 压缩或删除 |

### 备份策略

- **本地**: Git 仓库本身
- **远程**: GitHub (手动 push)
- **频率**: 重要结果立即 push

---

*最后更新: 2026-04-08 · 由 Archaeus Agent 维护*
