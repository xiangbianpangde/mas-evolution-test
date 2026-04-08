# AutoMAS 实验前置条件 (Prerequisites)

> 确保所有前置条件满足后再启动实验。未满足前置条件时禁止运行实验。

## 📋 前置条件检查清单

### 🔴 必须项 (Must-Have)

| # | 前置条件 | 当前状态 | 说明 |
|---|---------|---------|------|
| 1 | `MINIMAX_API_KEY` 环境变量已设置 | ❌ **缺失** | API 调用必需 |
| 2 | `results/evolution/state.json` 存在 | ✅ | 状态追踪文件 |
| 3 | `src/benchmark/tasks_v2.py` 存在 | ✅ | 15 个基准测试任务 |
| 4 | `src/native/resource_limiter.py` 存在 | ✅ | 资源限制模块 |
| 5 | `src/native/harness/harness_v31_0.py` 存在 | ✅ | 参考 harness |

### 🟡 重要项 (Should-Have)

| # | 前置条件 | 当前状态 | 说明 |
|---|---------|---------|------|
| 6 | disk space > 5GB | ✅ | 需检查当前剩余空间 |
| 7 | memory > 1GB | ✅ | 需检查当前可用内存 |
| 8 | `results/benchmarks/` 有历史基准数据 | ✅ | 用于对比 |
| 9 | Git 仓库状态 clean | ⚠️ | 需确认无未提交更改 |

---

## 🚨 关键问题：API Key 未设置

### 问题
`MINIMAX_API_KEY` 环境变量当前为空，导致：
- harness 无法调用 MiniMax API
- 所有任务返回 0 分
- 实验无效

### 解决方案
在运行实验前，必须设置环境变量：

```bash
# 方法 1: 临时设置 (仅当前终端)
export MINIMAX_API_KEY="your-api-key-here"

# 方法 2: 永久设置
echo 'export MINIMAX_API_KEY="your-api-key-here"' >> ~/.bashrc
source ~/.bashrc
```

### 验证
```bash
python3 -c "import os; print('API Key set:', bool(os.environ.get('MINIMAX_API_KEY')))"
```

---

## 📁 目录结构要求

```
mas_repo/
├── src/
│   ├── native/
│   │   ├── harness_evolution.py      ✅ 必须
│   │   ├── check_and_trigger_evolution.py  ✅ 必须
│   │   ├── resource_limiter.py      ✅ 必须
│   │   ├── self_verifier.py         ✅ 必须
│   │   └── harness/
│   │       └── harness_v31_0.py     ✅ 参考基线
│   └── benchmark/
│       └── tasks_v2.py              ✅ 必须 (15任务)
├── results/
│   ├── evolution/
│   │   └── state.json               ✅ 必须
│   └── benchmarks/
│       └── benchmark_results_v31_0_gen1.json  ✅ 历史冠军
└── knowledge/                       ✅ 文档
```

---

## 🔧 运行实验的完整流程

### 步骤 1: 验证前置条件
```bash
cd /root/.openclaw/workspace/mas_repo

# 检查 API Key
python3 -c "import os; assert os.environ.get('MINIMAX_API_KEY'), 'API Key not set!'"

# 检查磁盘空间
df -h /root

# 检查状态文件
cat results/evolution/state.json | python3 -c "import json,sys; d=json.load(sys.stdin); print(f\"Best: {d['best_version']}={d['best_score']}, Round: {d['current_round']}\")"
```

### 步骤 2: 启动实验
```bash
# 单轮实验
python3 src/native/harness_evolution.py --round 1

# 或持续实验 (心跳触发)
nohup python3 src/native/check_and_trigger_evolution.py &
```

### 步骤 3: 监控实验
```bash
# 检查状态
cat results/evolution/state.json

# 检查日志
tail -f results/evolution/evo_round*.log

# 检查 API 调用次数
cat results/evolution/api_calls.json
```

---

## ⚠️ 禁止事项

1. **禁止在 API Key 未设置时运行实验** - 产生无效数据
2. **禁止在磁盘空间 < 5GB 时运行实验** - 可能导致系统故障
3. **禁止在状态文件损坏时运行实验** - 导致状态丢失
4. **禁止运行多个并发实验** - 使用文件锁保护

---

## 📊 当前系统状态

```
Best Score:  v31_0 = 76.22
Current Round: 0
Mode: infinite (需手动触发)
Stop Condition: 100.0 或 10000 轮

API Key: ❌ 未设置
Disk Space: ✅ 充足
Memory: ✅ 充足
```

---

## 🔄 状态文件格式

`results/evolution/state.json` 结构：

```json
{
  "current_round": 0,
  "best_score": 76.22,
  "best_version": "v31_0",
  "best_source": "benchmark",
  "no_progress_rounds": 0,
  "mode": "infinite",
  "target_score": 100.0,
  "max_rounds": 10000,
  "baseline": {
    "version": "v31_0",
    "score": 76.22,
    "core": 79.2,
    "gen": 81.0,
    "source": "results/benchmarks/benchmark_results_v31_0_gen1.json"
  },
  "history": []
}
```

---

*最后更新: 2026-04-09 01:46*
