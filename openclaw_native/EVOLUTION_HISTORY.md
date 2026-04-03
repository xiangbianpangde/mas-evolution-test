# AutoMAS Evolution History

## v6.0 - Anti-Cheat Harness Architecture (2026-04-04)

### 架构变更
- **核心创新**: Executor/Evaluator 完全分离
- **防作弊**: Executor 永不接收 expected outputs
- **评分机制**: Evaluator 独立评分（不知道正确答案）

### Benchmark 结果
| 指标 | 数值 |
|------|------|
| 综合评分 | 45.00 |
| 核心任务质量分 | 50.0 |
| 泛化任务质量分 | 50.0 |
| Executor Token | 30,582 |
| Evaluator Token | 7,680 |
| 平均延迟 | 41.2秒/任务 |
| 可疑检测 | 0 |

### 发现的问题
- Evaluator 对所有任务给出统一的 50 分，区分度不足
- 需要改进 Evaluator 的评分标准

### 根因分析
- 当前 Evaluator prompt 过于简单，没有精细化评分维度
- 需要引入多维度评分（技术深度、完整性、可执行性）

---

## v5.0 - OpenClaw Native MAS (2026-04-03)

### 架构变更
- 从 Python MAS 迁移到 OpenClaw 原生 SOUL-driven 架构
- 创建了 Supervisor/Research/Code/Review/Evaluator Agent SOUL
- 实现了真实 API Benchmark runner

### Benchmark 结果
- 综合评分: 75.4
- 但存在 expected 泄漏问题（不是真正的防作弊评测）

---

## v4.0 - Real API Paradigm (2026-04-03)

### 架构变更
- 从 Mock 数据切换到真实 MiniMax API
- Gen400: 真实 API 调用，86.2 分
- Gen402: 退回 Mock，86.8 分

---

## 收敛检查
- v6.0 是首次防作弊架构测试
- 评分 45.0 有较大提升空间
- 下一步：改进 Evaluator 评分精细度
