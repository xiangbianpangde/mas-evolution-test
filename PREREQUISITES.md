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
| 6 | `src/native/harness_evolution.py` 存在 | ✅ | 进化主脚本 |

### 🟡 重要项 (Should-Have)

| # | 前置条件 | 当前状态 | 说明 |
|---|---------|---------|------|
| 7 | disk space > 5GB | ✅ 69GB | 当前剩余空间 |
| 8 | memory > 1GB | ✅ 6.5GB | 当前可用内存 |
| 9 | `results/benchmarks/` 有历史基准数据 | ✅ | 用于对比 |
| 10 | Git 仓库状态 clean | ⚠️ | 需提交当前修改 |
| 11 | 无过期锁文件 | ✅ | 已清理 harness.lock |

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
│   │   ├── resource_limiter.py       ✅ 必须
│   │   ├── self_verifier.py          ✅ 必须
│   │   └── harness/
│   │       └── harness_v31_0.py     ✅ 参考基线
│   └── benchmark/
│       └── tasks_v2.py              ✅ 必须 (15任务)
├── results/
│   ├── evolution/
│   │   └── state.json               ✅ 必须 (唯一权威)
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
Current Round: 1
Mode: infinite (需手动触发)
Stop Condition: 100.0 或 10000 轮

API Key: ❌ 未设置
Disk Space: ✅ 69GB 充足
Memory: ✅ 6.5GB 充足
Git Status: ⚠️ 有未提交修改
```

---

## 🔄 状态文件格式

`results/evolution/state.json` 结构：

```json
{
  "current_round": 1,
  "best_score": 76.22,
  "best_version": "v31_0",
  "best_source": "benchmark",
  "no_progress_rounds": 1,
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
  "history": [
    {
      "round": 0,
      "version": "v31_0",
      "strategy": "5000 tokens + 选择性反射 (MAX策略)",
      "score": 76.22,
      "core_score": 79.2,
      "gen_score": 81.0,
      "timestamp": "2026-04-04T00:00:00",
      "is_champion": true,
      "note": "真冠军 - 标准 tasks_v2.py 基准测试"
    },
    {
      "round": 0,
      "version": "evo_001",
      "strategy": "v32_1000tokens",
      "score": 51.74,
      "timestamp": "2026-04-09T01:38:42.189830",
      "is_champion": false
    },
    {
      "round": 0,
      "version": "evo_001",
      "strategy": "v32_1000tokens",
      "score": 0,
      "timestamp": "2026-04-09T03:46:39.957159",
      "is_champion": false
    }
  ]
}
```

---

## 🧹 清理记录

### 2026-04-09 清理
1. 删除孤立的 `evo_001_checkpoint.json` - 该文件与历史记录不匹配
2. 删除过期的 `harness.lock` - 无进程运行时不应存在
3. 删除无效的 `benchmark_results_evo_001_gen1.json` - 重复/无效数据
4. 删除测试日志 `evo_round_new.log` - 临时文件

---

*最后更新: 2026-04-09 14:50*
