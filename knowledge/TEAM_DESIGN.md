# TEAM_DESIGN.md - AutoMAS 团队设计文档

> **状态**: 强制前置条件 · 所有实验启动前必须完成
> **版本**: v1.0
> **最后更新**: 2026-04-09

---

## 1. 团队架构图

### 完整拓扑 (ASCII)

```
╔══════════════════════════════════════════════════════════════════════╗
║                           SUPERVISOR (主控)                           ║
║                   任务入口 · 分析分解 · 路由决策                       ║
║                      5000 tokens · 唯一任务入口                        ║
╚═══════════════════════════╤══════════════════════════════════════════╝
                             │ sessions_spawn (并行)
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
╔═══════════════╗   ╔═══════════════╗   ╔═══════════════╗
║   RESEARCH    ║   ║     CODE      ║   ║    REVIEW     ║
║    AGENT      ║   ║    AGENT      ║   ║    AGENT       ║
║               ║   ║               ║   ║               ║
║  3 Workers    ║   ║  3 Workers    ║   ║  3 Workers    ║
║  (并行)       ║   ║  (并行)       ║   ║  (并行)       ║
║               ║   ║  ⚠️ 禁止自反射 ║   ║               ║
╚═══════╤═══════╝   ╚═══════╤═══════╝   ╚═══════╤═══════╝
        │                    │                    │
        └────────────────────┴────────────────────┘
                             │ 所有 Worker 结果汇总
                             ▼
╔══════════════════════════════════════════════════════════════════════╗
║                             EVALUATOR                                  ║
║               三维评分: Depth × Completeness × Actionability           ║
║                      L1-L5 量表 · 独立评分 · 不受 Supervisor 影响       ║
╚══════════════════════════════════════════════════════════════════════╝
                             │ JSON 结果写入文件
                             ▼
                    results/benchmarks/
```

### 层级关系 (简化版)

```
Supervisor (第0层 · 协调)
    │
    ├── Research Agent (第1层 · Worker)
    │       └── Worker-1, Worker-2, Worker-3 (第2层)
    │
    ├── Code Agent (第1层 · Worker)
    │       └── Worker-1, Worker-2, Worker-3 (第2层)
    │
    ├── Review Agent (第1层 · Worker)
    │       └── Worker-1, Worker-2, Worker-3 (第2层)
    │
    └── Evaluator (第1层 · 裁判)
            └── (独立运行，无 Worker)
```

---

## 2. Agent 完整职责

### 2.1 Supervisor (监督者)

| 属性 | 值 |
|------|-----|
| **层级** | 第 0 层（顶层协调） |
| **运行时** | main session |
| **Token 预算** | 5000 tokens（已验证最优） |
| **输入** | 原始用户 query |
| **输出** | 路由决策 + Worker 任务分配 |

#### 说什么 (Say)
- 向 Worker 发送任务描述：`你是一个 Research Agent。任务：{具体任务描述}。请按以下格式输出：...`
- 向 Evaluator 发送评分请求：`请评估以下输出的三维质量：...`

#### 做什么 (Do)
1. 接收原始 query
2. 分析任务类型（research / code / review）
3. 分解为原子子任务
4. 通过 `sessions_spawn` 派发 Worker（并行）
5. 等待所有 Worker 返回
6. 汇总 Worker 输出
7. 调用 Evaluator 评分
8. 写入 benchmark 结果文件

#### 交付什么 (Deliver)
- `benchmark_results_vXX.json` — 包含所有任务分数、配置、Composite Score
- 实验日志（任务完成状态）
- 错误报告（如有 Worker 超时/失败）

#### 禁止事项
- ❌ 禁止自行执行研究/代码/评审任务（必须委托 Worker）
- ❌ 禁止自我评审输出结果（必须通过 Evaluator）
- ❌ 禁止超过 5000 tokens（已验证导致 Core 下降）

---

### 2.2 Research Agent (研究 Agent)

| 属性 | 值 |
|------|-----|
| **层级** | 第 1 层（被 Supervisor 调度） |
| **运行时** | subagent (ACP) |
| **并行度** | 3 Workers |
| **Worker 超时** | 120s / Worker |
| **任务类型** | research 类型任务 |
| **Token 预算** | 5000 tokens / Worker |

#### 说什么 (Say)
- 研究报告输出格式：

```
## 研究报告: {任务ID}

### 1. 问题诊断
{清晰描述核心问题}

### 2. 深度分析
{多角度分析，包括原因、影响、上下文}

### 3. 具体方案
{可执行的解决方案 1, 2, 3...}

### 4. 数字证据
{支撑数据、引用、案例}

### 5. 验证方法
{如何验证方案有效性}
```

#### 做什么 (Do)
1. 接收 Supervisor 的任务描述
2. 执行深度研究（网络搜索、文档分析等）
3. 按标准格式输出研究报告
4. 返回结构化结果给 Supervisor

#### 交付什么 (Deliver)
- **结构化研究报告**（符合上述格式）
- **Worker 级别日志**（任务开始/完成时间、token 消耗）
- **异常状态码**（如遇 API 错误、超时）

#### 质量标准
| 维度 | 要求 |
|------|------|
| Depth | 诊断准确性、分析深度 |
| Completeness | 覆盖全面性、细节完整性 |
| Actionability | 可执行性、实用性 |

---

### 2.3 Code Agent (代码 Agent)

| 属性 | 值 |
|------|-----|
| **层级** | 第 1 层（被 Supervisor 调度） |
| **运行时** | subagent (ACP) |
| **并行度** | 3 Workers |
| **Worker 超时** | 120s / Worker |
| **任务类型** | code 类型任务 |
| **Token 预算** | 5000 tokens / Worker |

#### 说什么 (Say)
- 代码输出格式：

```
## 代码实现: {任务ID}

### 架构简图
{ASCII 架构图或简短说明}

### 核心代码
```{language}
{完整可运行代码}
```

### 测试用例
```python
def test_{功能}():
    # 测试逻辑
    pass
```

### 配置说明
{必要的环境配置、依赖说明}
```

#### 做什么 (Do)
1. 接收 Supervisor 的任务描述
2. 分析需求，设计架构
3. 编写完整可运行代码
4. 编写对应测试用例
5. 提供配置说明

#### 交付什么 (Deliver)
- **完整可运行代码**（含注释）
- **测试用例**（至少覆盖核心路径）
- **配置说明**（依赖、环境变量）
- **架构简图**（ASCII 或简短文字说明）

#### ⚠️ 强制禁止
- ❌ **禁止自我评审**（Code Agent 评审自己的代码）
- ❌ **禁止输出不完整的代码片段**
- ❌ **禁止假设运行环境**（必须提供配置说明）

---

### 2.4 Review Agent (评审 Agent)

| 属性 | 值 |
|------|-----|
| **层级** | 第 1 层（被 Supervisor 调度） |
| **运行时** | subagent (ACP) |
| **并行度** | 3 Workers |
| **Worker 超时** | 120s / Worker |
| **任务类型** | review 类型任务 |
| **Token 预算** | 3500 tokens / Worker |

#### 说什么 (Say)
- 评审报告格式：

```
## 评审报告: {任务ID}

### 风险矩阵
| 风险项 | 严重程度 | 概率 | 影响面 |
|--------|----------|------|--------|
| ...    | 高/中/低 | 高/中/低 | 宽/中/窄 |

### 影响分析
{各风险项的详细影响评估}

### 缓解步骤
1. {具体缓解措施}
2. ...
3. ...

### 优先级
- P0: {必须立即处理}
- P1: {本周内处理}
- P2: {后续迭代处理}

### 验证方法
{如何验证风险已被缓解}
```

#### 做什么 (Do)
1. 接收 Supervisor 的任务描述
2. 识别潜在风险（技术、安全、性能等）
3. 评估影响面和严重程度
4. 提出缓解方案
5. 确定优先级

#### 交付什么 (Deliver)
- **风险矩阵**（结构化风险列表）
- **影响分析**（风险间的关联和级联效应）
- **缓解方案**（具体、可执行的步骤）
- **优先级排序**（P0/P1/P2 分级）

---

### 2.5 Evaluator (评估器)

| 属性 | 值 |
|------|-----|
| **层级** | 第 1 层（独立运行） |
| **运行时** | 函数调用（非 Agent） |
| **输入** | Supervisor 汇总的所有 Worker 输出 |
| **输出** | 三维评分 JSON |

#### 做什么 (Do)
1. 接收 Supervisor 汇总的 Worker 输出
2. 对每个输出进行三维评分：
   - **Depth**（深度）：诊断准确、分析透彻
   - **Completeness**（完整）：覆盖全面、细节完整
   - **Actionability**（可执行）：方案可行、实用有效
3. 评定 Actionability 等级（L1-L5）
4. 计算 Composite Score
5. 将结果写入 JSON 文件

#### 交付什么 (Deliver)
- `benchmark_results_vXX.json`：

```json
{
  "version": "vXX",
  "composite": 76.22,
  "core": {
    "score": 79.2,
    "core_001": 82.0,
    ...
  },
  "gen": {
    "score": 81.0,
    "gen_001": 85.0,
    ...
  },
  "actionability": {
    "score": "L4.13",
    "level": 4.13
  },
  "config": {
    "tokens": 5000,
    "max_strategy": "MAX-2",
    "temperature": 0.7
  }
}
```

#### 强制规则
- ✅ **独立评分**：不受 Supervisor 偏好影响
- ✅ **基于客观标准**：使用 L1-L5 量表
- ✅ **结果写入文件**：不仅返回字符串，必须写 JSON

---

## 3. Agent 间通信协议

### 3.1 任务传递协议

```
协议名称: TASK_DISPATCH_PROTOCOL
触发条件: Supervisor 接收到实验任务
```

#### 步骤

```
Step 1: Supervisor 解析 query
        │
        ▼
Step 2: 判断任务类型 (research | code | review)
        │
        ▼
Step 3: 构建 Worker prompt
        {
          "task_id": "core_001",
          "task_type": "research",
          "query": "分析为什么...",
          "output_format": "见各 Agent 输出格式",
          "context": "相关上下文",
          "max_tokens": 5000,
          "timeout": 120
        }
        │
        ▼
Step 4: sessions_spawn(worker_type, prompt, timeout=120)
        │
        ▼
Step 5: Worker 执行并返回结果
        │
        ▼
Step 6: Supervisor 验证结果存在且非空
        ├── 失败 → 记录错误，继续其他 Worker
        └── 成功 → 汇总到 result_list
```

### 3.2 结果汇报协议

```
协议名称: RESULT_REPORT_PROTOCOL
触发条件: Worker 完成执行
```

#### Worker → Supervisor

所有 Worker 返回必须包含：

```json
{
  "worker_id": "research_worker_1",
  "task_id": "core_001",
  "status": "success|failed|timeout",
  "output": "...",
  "token_used": 3500,
  "execution_time_ms": 45000,
  "error": null  // 仅失败时填写
}
```

#### Supervisor → Evaluator

汇总后发送：

```json
{
  "version": "vXX",
  "tasks": [
    {
      "task_id": "core_001",
      "type": "research",
      "outputs": ["worker_1_output", "worker_2_output", "worker_3_output"],
      "best_output": "...",  // MAX 策略选择
      "all_scores": [82.0, 78.0, 80.0]
    },
    ...
  ],
  "config": {
    "max_strategy": "MAX-2",
    "temperature": 0.7
  }
}
```

### 3.3 验证协议

```
协议名称: VERIFICATION_PROTOCOL
触发条件: 每次 Worker 返回、每次 Evaluator 评分后
```

#### Worker 结果验证

| 检查项 | 通过条件 | 失败处理 |
|--------|----------|----------|
| 输出存在 | `output` != null 且 != "" | 标记 failed |
| 长度合理 | `len(output)` > 500 chars | 警告，记录但不失败 |
| 格式正确 | 包含关键 section header | 记录格式偏差 |
| 无 API 错误 | `status` == "success" | 记录错误信息 |

#### Evaluator 结果验证

| 检查项 | 通过条件 | 失败处理 |
|--------|----------|----------|
| Composite 有效 | 0 <= score <= 100 | 重新评分 |
| 各维度有效 | 0 <= 每个维度 <= 100 | 重新评分 |
| JSON 写入成功 | 文件存在且可读 | 重新写入 |

---

## 4. 监督链 (Supervision Chain)

### 4.1 监督拓扑

```
┌─────────────────────────────────────────────────────────┐
│                    人类 (最终监督者)                       │
│            所有结果可见 · 可终止实验 · 可干预               │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│               Supervisor (主动监督者)                      │
│  · 监督所有 Worker 的执行状态                              │
│  · 检测 Worker 超时/失败                                   │
│  · 控制实验开始/暂停/终止                                  │
│  · 汇报进度给人类                                          │
└─────────────────────────────────────────────────────────┘
                            │
          ┌─────────────────┼─────────────────┐
          ▼                 ▼                 ▼
   Research Agent      Code Agent        Review Agent
   (无下属监督)        (监督自己的        (无下属监督)
                       3个Worker)
                            │
                     ┌──────┼──────┐
                     ▼      ▼      ▼
                  Worker-1 Worker-2 Worker-3
               (被 Code Agent 监督，但禁止自反射)
```

### 4.2 单点失败防护

| 风险点 | 防护机制 | 恢复方式 |
|--------|----------|----------|
| **Worker 超时** | 每个 Worker 独立超时（120s） | Supervisor 记录失败，继续其他 Worker |
| **Worker 失败** | 3 Workers 并行任一成功即可 | 使用其他 Worker 结果 |
| **Agent 类型全部失败** | 该类型所有 Worker 失败 | 标记任务失败，不阻塞其他任务 |
| **Supervisor 崩溃** | 实验状态写入 checkpoint | 从 checkpoint 恢复 |
| **Evaluator 失败** | JSON 写入验证 | 重新调用 Evaluator |

### 4.3 Supervisor 自监督

Supervisor 必须记录以下状态：

```json
{
  "experiment_id": "vXX_genY",
  "start_time": "2026-04-09T00:00:00",
  "tasks_completed": 10,
  "tasks_total": 15,
  "workers_active": {
    "research": 3,
    "code": 2,
    "review": 3
  },
  "failures": [
    {"task_id": "core_003", "worker": "code_worker_1", "reason": "timeout"}
  ],
  "checkpoint": true
}
```

---

## 5. 决策机制

### 5.1 决策层级

```
层级 1: 实验级决策 ( Supervisor 独立决定 )
    ├── 使用哪个任务集 (tasks.py vs tasks_v2.py)
    ├── Worker 并行度 (3 Workers 已验证最优)
    └── MAX 策略 (MAX-2 已验证最优)

层级 2: 任务级决策 ( Supervisor 独立决定 )
    ├── 选择哪个 Agent 类型处理任务
    ├── Worker 超时时间 (120s)
    └── 输出格式验证标准

层级 3: 结果级决策 ( Supervisor + Evaluator 协作 )
    ├── 选择 MAX 分数 (MAX-2 取2次运行最大值)
    ├── 分数是否达到基准线
    └── 是否触发新实验

层级 4: 架构级决策 ( 人类授权 Supervisor )
    ├── 改变 Agent 类型数量
    ├── 改变 token 预算
    └── 引入新 Agent 类型
```

### 5.2 最终决定权

| 决策类型 | 最终决定权 | 说明 |
|----------|------------|------|
| 实验配置 | Supervisor | 遵循已验证的最佳实践 |
| 分数计算 | Evaluator | Supervisor 无权修改 |
| 实验是否继续 | Supervisor + 人类 | Supervisor 建议，人类批准 |
| 架构变更 | 人类 | 需要人类明确授权 |
| 实验终止 | 人类 | 人类可随时终止实验 |

### 5.3 决策流程

```
决策请求
    │
    ▼
判断决策类型 (层级 1-4)
    │
    ├── 层级 1-2 → Supervisor 立即决定
    │                   │
    │                   ▼
    │              记录到日志
    │
    ├── 层级 3 → Supervisor 提议，Evaluator 验证
    │                   │
    │                   ▼
    │              验证通过 → 执行
    │              验证失败 → Supervisor 重审
    │
    └── 层级 4 → 暂停，等待人类授权
                    │
                    ▼
              人类批准 → 执行
              人类拒绝 → 记录拒绝原因
```

---

## 6. 冲突解决

### 6.1 冲突类型与解决策略

| 冲突类型 | 冲突描述 | 解决策略 | 执行者 |
|----------|----------|----------|--------|
| **Worker 间冲突** | 3 个 Worker 输出差异大 | MAX 策略：取最高分 | Supervisor |
| **Agent 类型冲突** | 不同类型 Agent 对同一任务有矛盾结论 | 以 Research Agent 结论为准 | Supervisor |
| **质量与速度冲突** | 高质量 = 高耗时 | 遵循质量优先，超时则记录 | Supervisor |
| **Supervisor vs Evaluator** | 分数计算不一致 | 以 Evaluator 为准 | Evaluator |
| **架构建议冲突** | 多个实验建议矛盾 | 提交人类决策 | 人类 |

### 6.2 冲突升级流程

```
冲突发生
    │
    ▼
尝试自动解决 (根据冲突类型选择策略)
    │
    ├── 可自动解决 → 应用策略 → 记录到日志
    │                     │
    │                     ▼
    │                 解决完成
    │
    └── 无法自动解决 → 升级到人类
                          │
                          ▼
                    人类做出决定
                          │
                          ▼
                    记录决策原因 → 执行
```

### 6.3 冲突记录格式

当冲突无法自动解决时，Supervisor 必须记录：

```json
{
  "conflict_id": "CONF_001",
  "timestamp": "2026-04-09T00:00:00",
  "conflict_type": "worker_output_divergence",
  "involved_agents": ["research_worker_1", "research_worker_2", "research_worker_3"],
  "task_id": "core_003",
  "divergence_details": {
    "worker_1_score": 85.0,
    "worker_2_score": 62.0,
    "worker_3_score": 78.0,
    "max_diff": 23.0
  },
  "attempted_resolution": "MAX_strategy_applied",
  "resolution_result": "used_worker_1_output",
  "escalation_needed": false,
  "human_notes": null
}
```

---

## 7. 交付物总表

| 角色 | 交付物 | 文件位置 | 触发时机 |
|------|--------|----------|----------|
| **Supervisor** | 实验配置 | `src/native/harness/harness_vXX.py` | 实验开始 |
| **Supervisor** | Benchmark 结果 | `results/benchmarks/benchmark_results_vXX.json` | 实验完成 |
| **Supervisor** | Checkpoint | `results/benchmarks/checkpoint/vXX_checkpoint.json` | 每个任务完成后 |
| **Supervisor** | 实验日志 | `results/evolution/vXX_benchmark.log` | 实验运行中 |
| **Research Agent** | 研究报告 | 汇总后写入 JSON | 任务完成 |
| **Code Agent** | 代码 + 测试 | 汇总后写入 JSON | 任务完成 |
| **Review Agent** | 评审报告 | 汇总后写入 JSON | 任务完成 |
| **Evaluator** | 评分结果 | `results/benchmarks/benchmark_results_vXX.json` | 所有 Worker 完成后 |

---

## 8. 快速参考卡

```
╔══════════════════════════════════════════════════════════╗
║                    团队角色速查                            ║
╠══════════════════════════════════════════════════════════╣
║ Supervisor:  入口 · 协调 · 路由 · 汇总 (5000 tokens)      ║
║ Research:    研究分析 (3 Workers, 5000 tokens/Worker)     ║
║ Code:        代码实现 (3 Workers, 5000 tokens/Worker)     ║
║ Review:      风险评审 (3 Workers, 3500 tokens/Worker)     ║
║ Evaluator:   独立评分 (L1-L5, JSON 写出)                  ║
╠══════════════════════════════════════════════════════════╣
║ 决策层级:                                                   ║
║   L1-2: Supervisor 独立决定                               ║
║   L3:   Supervisor + Evaluator 协作                       ║
║   L4:   人类授权                                           ║
╠══════════════════════════════════════════════════════════╣
║ 冲突解决:                                                   ║
║   Worker 分歧 → MAX 策略                                  ║
║   Agent 分歧 → Research 结论优先                          ║
║   无法解决 → 升级人类                                      ║
╚══════════════════════════════════════════════════════════╝
```

---

*此文档是实验启动前的强制前置条件。所有 Agent 必须遵循本设计运行。*
*如需修改任何角色职责或协议，请先更新本文档并获得人类批准。*
