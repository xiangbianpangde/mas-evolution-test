# Team Design - 完整团队架构

## 1. 团队架构图

```
                    ┌─────────────────────────────────────────────────────────────┐
                    │                         LEADER (Me)                          │
                    │                  最终决策者 + 监督者 + 协调者                  │
                    └─────────────────────────────────────────────────────────────┘
                                              │
          ┌───────────────────────────────────┼───────────────────────────────────┐
          │                                   │                                   │
          ▼                                   ▼                                   ▼
    ┌──────────┐                       ┌──────────┐                       ┌──────────┐
    │ EXECUTOR │                       │ CHECKER  │                       │ LOGGER   │
    │  执行Agent │                       │ 检查Agent │                       │ 记录Agent │
    └──────────┘                       └──────────┘                       └──────────┘
          │                                   │                                   │
          └───────────────────────────────────┼───────────────────────────────────┘
                                              ▼
                              ┌───────────────────────────────┐
                              │        SHARED CONTEXT         │
                              │   (state.json, checkpoints)   │
                              └───────────────────────────────┘
```

## 2. Agent 职责定义

### Leader (主Agent)
| 属性 | 说明 |
|------|------|
| **角色** | 决策者、监督者、协调者 |
| **职责** | 制定计划、分配任务、验证结果、做出最终决定 |
| **汇报对象** | 无（自主运行） |
| **决策权限** | 最终决定权 |
| **交付物** | 决策记录、任务分配、结果验证 |

### EXECUTOR Agent
| 属性 | 说明 |
|------|------|
| **角色** | 执行者 |
| **职责** | 按照指令执行实验、运行 harness、生成结果 |
| **汇报对象** | Leader |
| **决策权限** | 无（只执行） |
| **交付物** | executor_output, quality_score, checkpoint |

### CHECKER Agent
| 属性 | 说明 |
|------|------|
| **角色** | 验证者 |
| **职责** | 独立验证 Executor 结果、检查异常、标记可疑结果 |
| **汇报对象** | Leader |
| **决策权限** | 建议权（可标记可疑但不能推翻） |
| **交付物** | 验证报告、异常标记、is_suspicious |

### LOGGER Agent
| 属性 | 说明 |
|------|------|
| **角色** | 记录者 |
| **职责** | 记录所有实验、维持知识库、更新记忆 |
| **汇报对象** | Leader |
| **决策权限** | 无（只记录） |
| **交付物** | 实验日志、知识库更新、记忆写入 |

## 3. 通信协议

### 任务分配 (Leader → Agent)
```json
{
  "type": "TASK",
  "task_id": "task_001",
  "agent": "EXECUTOR",
  "instruction": "具体指令",
  "expected_output": {
    "file": "path/to/output.json",
    "fields": ["executor_output", "quality_score"]
  },
  "verification": "如何验证完成",
  "timeout": 7200
}
```

### 结果汇报 (Agent → Leader)
```json
{
  "type": "RESULT",
  "task_id": "task_001",
  "agent": "EXECUTOR",
  "status": "success|failed|suspicious",
  "output": {
    "file": "path/to/output.json",
    "verified": true
  },
  "evidence": {
    "file_exists": true,
    "output_length": 5234,
    "timestamp": "2026-04-09T00:14:00"
  }
}
```

### 异常上报 (Agent → Leader)
```json
{
  "type": "ALERT",
  "alert_type": "suspicious_result|error|timeout",
  "severity": "high|medium|low",
  "details": "具体描述",
  "evidence": ["证据1", "证据2"]
}
```

## 4. 监督链

```
EXECUTOR ──(结果)──→ CHECKER ──(验证)──→ LEADER ──(决策)──→ 执行/拒绝
                              ↑
                              │
                     LOGGER ───┘
                      (记录异常)
```

**关键规则**：
1. EXECUTOR 不能直接向 LEADER 报告结果，必须经过 CHECKER
2. CHECKER 必须独立验证，不能只相信 EXECUTOR 的说法
3. LOGGER 记录所有交互，包括异常

## 5. 决策机制

### 决策流程
```
收到结果 → CHECKER 验证 → 三重检查 → LEADER 决策
```

### 决策类型

| 决策 | 条件 | 行动 |
|------|------|------|
| **接受** | 三重验证通过 + 无异常 | 记录并继续 |
| **拒绝** | 验证失败 + 证据确凿 | 重新执行 |
| **审计** | 可疑但不确定 | 深度审计 |
| **升级** | 无法判断 | 标记待处理 + 继续 |

## 6. 冲突解决

| 冲突类型 | 解决方法 |
|----------|----------|
| CHECKER vs EXECUTOR | 以 CHECKER 为准 |
| 多个 CHECKER 不一致 | 以多数意见为准 |
| LEADER vs 所有Agent | LEADER 最终决定 |

## 7. 验证清单

每个任务完成后，LEADER 必须验证：

- [ ] 文件存在
- [ ] 内容非空 (>500 chars)
- [ ] 分数在合理范围 (0-100)
- [ ] 时间戳合理
- [ ] 与历史版本无矛盾
- [ ] CHECKER 已验证

---

*Last updated: 2026-04-09*
