#!/bin/bash
# AutoMAS Continuous Evolution Trigger
# 
# 用法:
#   ./run_evolution.sh          # 运行一轮
#   ./run_evolution.sh --watch  # 持续运行直到完成
#   ./run_evolution.sh --daemon # 后台运行

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STATE_FILE="$SCRIPT_DIR/evolution_state.json"
RESULTS_DIR="$SCRIPT_DIR/../../results/evolution"

mkdir -p "$RESULTS_DIR"

# 读取当前状态
get_state() {
    cat "$STATE_FILE"
}

# 更新状态
update_state() {
    local new_state="$1"
    echo "$new_state" > "$STATE_FILE"
}

# 获取下一个策略
get_next_strategy() {
    local state=$(get_state)
    local current_round=$(echo "$state" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['current_round'])" 2>/dev/null || echo "0")
    local queue=$(echo "$state" | python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d['strategy_queue']))" 2>/dev/null || echo "5")
    local idx=$((current_round % queue))
    
    echo "$state" | python3 -c "
import sys,json
d=json.load(sys.stdin)
idx=$idx
if idx < len(d['strategy_queue']):
    s=d['strategy_queue'][idx]
    print(json.dumps(s))
else:
    print('{}')
"
}

# 运行一轮
run_round() {
    local strategy=$(get_next_strategy)
    if [ -z "$strategy" ] || [ "$strategy" = "{}" ]; then
        echo "没有更多策略，停止"
        return 1
    fi
    
    echo "策略: $strategy"
    
    # 生成版本名
    local state=$(get_state)
    local round=$(echo "$state" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['current_round'])" 2>/dev/null || echo "0")
    local version="evo_$(printf '%03d' $((round + 1)))"
    
    echo "运行 $version..."
    
    # 调用 harness
    cd "$SCRIPT_DIR"
    python3 harness_evolution.py --version "$version" --strategy "$strategy"
    
    # 等待完成
    # TODO: 实际应该等待 harness 完成并读取结果
}

# 主逻辑
case "${1:-}" in
    --watch)
        echo "持续运行模式..."
        while true; do
            run_round || break
            sleep 5
        done
        ;;
    --daemon)
        echo "后台运行..."
        nohup "$0" --watch > "$RESULTS_DIR/evolution.log" 2>&1 &
        echo "PID: $!"
        ;;
    *)
        run_round
        ;;
esac
