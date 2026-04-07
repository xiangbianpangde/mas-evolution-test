# 🔬 OpenClaw Native MAS

> 使用 OpenClaw 原生架构的真实 API 测试系统

---

## 目录结构

```
src/native/
├── README.md              # 本文件
├── SOUL.md               # Agent SOUL 定义
├── base_harness.py       # 基础 harness 框架
├── run_benchmark.py      # 基准测试运行器
├── compare_results.py    # 结果比较工具
│
├── harness/              # 当前活跃版本
│   ├── harness_v31_0.py  # 🏆 冠军版本 (76.22)
│   ├── harness_v37.py   # 实验版本
│   └── harness_v38.py   # 实验版本
│
└── harness_old/          # 历史版本存档
    ├── harness_v2_0.py ~ harness_v36.py
    └── (73个旧版本)
```

---

## 版本说明

### 🏆 冠军版本: v31.0
- **分数**: Composite 76.22 | Core 79.2 | Gen 81.0
- **关键配置**: 5000 tokens, MAX-2, 选择性自反射
- **位置**: `harness/harness_v31_0.py`

### 实验版本
| 版本 | 分数 | 状态 |
|------|------|------|
| v38 | - | 运行中 |
| v37 | 69.07 | 失败 (extended critique) |
| v36 | 69.xx | 待评估 |
| v35 | - | 待评估 |

---

## 核心组件

### SOUL.md
定义 Supervisor 和 Worker Agent 的角色、指令和工具。

### base_harness.py
基础测试框架：
- 任务加载
- 评分计算
- 结果输出

### run_benchmark.py
基准测试运行器：
- 加载任务
- 运行 harness
- 收集结果

---

## 运行测试

```bash
cd /root/.openclaw/workspace/mas_repo
python src/native/run_benchmark.py --version v31_0
```

---

## 版本命名规范

- `harness_vXX.py`: 主版本
- `harness_vXX_0.py`: 同一版本的第一次运行
- `harness_vXX_X.py`: 同一版本的不同配置

---

## 未来改进

1. **保存答案**: 每个版本保存生成的答案，不只是分数
2. **标准化**: 统一 harness 接口
3. **模块化**: 抽取通用组件

---

*最后更新: 2026-04-07*
