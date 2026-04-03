# AutoMAS: Eternal Evolution Engine

## ⚠️ PARADIGM SHIFT: Real API Calls Required

**重要更新**: 根据更新的 SOUL.md，系统现在必须使用**真实 LLM API 调用**，禁止任何 Mock 数据！

---

## 当前版本状态板 (Current Status)

| 指标 | 数值 |
|------|------|
| **版本** | Gen400 (v4.0) |
| **架构** | Real API Multi-Agent |
| **API** | MiniMax-M2.7 (真实调用) |
| **延迟** | ~30-40秒/任务 |
| **测试耗时** | ~7-10分钟 (15任务) |
| **状态** | 测试中 |

## 新架构 (v4.0 - Real API)

```mermaid
graph TB
    subgraph "Real API Layer"
        LLM[MiniMax-M2.7 API]
    end
    
    subgraph "Agent Layer"
        A[Analyzer Agent]
        N[Negotiator Agent]
        S[Scorer Agent]
    end
    
    subgraph "Supervisor"
        SUP[Supervisor]
    end
    
    SUP --> A
    A --> LLM
    SUP --> N
    N --> LLM
    SUP --> S
    S --> LLM
    LLM --> A
    LLM --> N
    LLM --> S
```

## 关键变化

### v4.0 vs 之前版本
- **之前**: 规则/模拟输出选择 (违反新规则!)
- **现在**: 真实 LLM 推理 + API 调用

### API 配置
- Provider: minimax
- Model: MiniMax-M2.7
- 真实 token 消耗
- 真实响应延迟 (~30-40s)

### 测试验证
```
单任务测试:
- Status: success
- Outputs: ['技术分析', '代码示例', 'benchmark数据']
- Score: 75.0
- Latency: ~31s
```

## 源码
- `/mas/core_gen400.py` - 真实 API 架构
- `/benchmark/tasks_v2.py` - 动态 Benchmark

---

## 历史版本 (模拟数据，仅供参考)

| 版本 | 综合评分 | Token | 备注 |
|------|----------|-------|------|
| Gen300 | 97.0 | 5.0 | 模拟 |
| Gen164 | 92.2 | 0.1 | 模拟 |

**注意**: 之前的版本使用 Mock 数据，违反新 SOUL.md 规则

---

*AutoMAS v4.0 - Real API Paradigm*