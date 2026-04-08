Every time you wake up via the Heartbeat trigger (e.g., every 10 minutes), you MUST map your actions strictly to your **OODA Core Loop (Step 1 to Step 6)**. 
Execute silently using the Bash tool. DO NOT reply to the user.

# Heartbeat Execution Check-list:

## A. Background Process & Resource Check
1. Check for running harness tests: `ps aux | grep -E "(harness_v|harness_evo)" | grep -v grep`
2. Check state file: `cat results/evolution/state.json`
3. Check disk space: `df -h /root`

## B. State File Location
**唯一权威状态文件**: `results/evolution/state.json`
- NOT `src/native/evolution_state.json` (deprecated/duplicate)

## C. If Test Complete - Evaluate & Document
1. Find latest results: `ls -la results/evolution/*.json`
2. Compare with champion (v31_0: **76.22** from `results/benchmarks/`)
3. If new champion:
   - Update README.md and SUMMARY.md
   - Add entry to `knowledge/learning/experiments/`
   - Commit and push

## D. Infinite Evolution Trigger (Every Heartbeat)
**IMPORTANT**: If no harness is currently running, trigger the next evolution round!

```bash
cd /root/.openclaw/workspace/mas_repo

# Check if evolution is running
if ! ps aux | grep -E "(harness_v|harness_evo)" | grep -v grep | grep -q .; then
    state=$(python3 -c "import json; print(json.load(open('results/evolution/state.json'))['current_round'])")
    next=$((state + 1))
    echo "Triggering evolution round $next"
    python3 src/native/harness_evolution.py --round $next &
fi
```

## E. Resources
- Disk: Check `df -h /root` - should have >5GB free
- Memory: `free -h` - should have >1GB available
- No GPU

## Current Status (2026-04-09)

### ⚠️ CRITICAL: Two v31_0 Files (DO NOT CONFUSE!)
| Location | Score | Source |
|----------|-------|--------|
| `results/benchmarks/benchmark_results_v31_0_gen1.json` | **76.22** | 真正的冠军基准 |
| `results/evolution/benchmark_results_v31_0_gen1.json` | 73.73 | 进化系统重跑结果 |

**只有 `results/benchmarks/` 下的 76.22 是真冠军！**

### Champion Baseline
| Version | Composite | Core | Gen | Source |
|---------|-----------|------|-----|--------|
| **v31_0** | **76.22** | **79.2** | **81.0** | `results/benchmarks/` |

### Evolution State
- **State file**: `results/evolution/state.json` (唯一权威)
- **Mode**: `infinite` - 永不停歇
- **Stop condition**: 只有达到 100.0 或 10000 轮才停
- **Current round**: 0 (待启动)

### Bug Fixed: 2026-04-09 01:36
1. **Issue**: state.json 有两个版本 (`results/evolution/` 和 `src/native/`)
2. **Fix**: 统一使用 `results/evolution/state.json`，删除重复
3. **Issue**: evo_001 多次运行产生 0 分和 51.74 分
4. **Fix**: 清理历史记录，正确设置 v31_0 (76.22) 为冠军

### GitHub
- Remote: https://github.com/xiangbianpangde/mas-evolution-test
- Branch: main

## 实验前置条件 (Prerequisites) - 2026-04-09 完善

### ✅ 已修复
1. 状态文件统一为 `results/evolution/state.json`
2. 冠军基线正确设置: v31_0 = 76.22
3. check_and_trigger_evolution.py 添加文件锁防止重复执行
4. 清理了旧的 checkpoint 和日志文件

### ⚠️ 注意事项
- `results/benchmarks/` 下的 v31_0 (76.22) 是真正的历史冠军
- `results/evolution/` 下的文件是进化系统的运行时数据
- 进化系统需要超越 76.22 才能产生新的冠军
