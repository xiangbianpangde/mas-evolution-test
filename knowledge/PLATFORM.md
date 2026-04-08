# PLATFORM.md - 平台环境说明

## 概览

| 属性 | 值 |
|------|-----|
| **模型** | MiniMax-M2.7 |
| **平台** | OpenClaw on Linux |
| **架构** | x86_64 |
| **Node** | i-69ca97ebe76772a184cff8f6 |
| **Shell** | bash |
| **Channel** | qqbot |

---

## API 模型详情

### MiniMax-M2.7

| 属性 | 值 |
|------|-----|
| **提供商** | MiniMax |
| **模型名** | MiniMax-M2.7 |
| **上下文窗口** | 未明确限制（受 token 预算约束） |
| **能力** | 低推理模式（reasoning=off） |

### 已知特性

| 特性 | 说明 |
|------|-----|
| **自然方差** | 约 8% 的分数波动 |
| **响应速度** | 适中，受服务器负载影响 |
| **并发限制** | 未明确，建议串行执行关键任务 |

### 使用建议

- **使用 MAX 策略**：取多次运行的最大值，抵消方差影响
- **Token 预算**：建议 5000 tokens（已验证为临界点）
- **避免极端值**：单次运行结果可能偏离均值

---

## 运行环境详情

### 操作系统

```
Linux 6.8.0-71-generic (x64)
```

### Node 环境

| 属性 | 值 |
|------|-----|
| **Node.js** | v22.22.2 |
| **npm** | 未确认 |
| **Python** | 未确认（需通过 exec 调用） |

### OpenClaw

| 属性 | 值 |
|------|-----|
| **版本** | 未知（需要 openclaw version 查询） |
| **Gateway** | 运行中（qqbot channel） |
| **扩展目录** | ~/.openclaw/extensions/ |

---

## 资源限制

### 计算资源

| 资源 | 限制 | 说明 |
|------|------|------|
| **CPU** | 未限制 | 共享环境 |
| **内存** | 未明确限制 | 共享环境 |
| **磁盘** | 有可用空间 | ~/workspace 可用 |
| **GPU** | 无 | 纯 CPU 环境 |

### 执行约束

| 约束 | 说明 |
|------|------|
| **exec timeout** | 建议设置，避免无限等待 |
| **PTY** | 支持，需要时可用 |
| **Elevated** | 需审批（ask 模式） |
| **Background** | 支持，使用 yieldMs 或 background=true |

### 文件系统

| 路径 | 用途 |
|------|------|
| `/root/.openclaw/workspace/` | 主工作区 |
| `/root/.openclaw/workspace/mas_repo/` | MAS 评测仓库 |
| `/root/.openclaw/workspace/mas_repo/src/native/` | OpenClaw Native MAS 代码 |
| `/root/.openclaw/workspace/mas_repo/knowledge/` | 知识库（本文档目录） |
| `/root/.openclaw/workspace/mas_repo/results/` | 评测结果 |

### GitHub 集成

| 属性 | 值 |
|------|-----|
| **仓库** | https://github.com/xiangbianpangde/mas-evolution-test |
| **用途** | 版本控制 + 结果存储 |
| **同步** | 手动或自动（需配置） |

---

## 可用工具

| 工具 | 可用 | 说明 |
|------|------|------|
| exec | ✅ | 运行 shell 命令 |
| read | ✅ | 读取文件 |
| write | ✅ | 写入文件 |
| edit | ✅ | 编辑文件 |
| web_search | ✅ | 网页搜索 |
| web_fetch | ✅ | 获取页面内容 |
| image | ✅ | 图片分析 |
| image_generate | ✅ | 图片生成 |
| sessions_spawn | ✅ | 派生子 Agent |

---

## 环境特性

### 有利因素
- **完整工具链**：exec + 文件操作 + 网络访问
- **多 Agent 支持**：可派生子 Agent 并行工作
- **持久存储**：文件系统 + GitHub
- **OpenClaw 生态**：技能扩展、Gateway 管理

### 限制因素
- **无长期记忆**：每次 session 独立
- **无互联网直接访问**：需通过 web_* 工具
- **API 方差**：需用统计方法抵消
- **单点执行**：无法真正并行大规模实验

---

## 配置建议

### 子 Agent 执行
```
sessions_spawn(
  runtime="acp",      # 使用 OpenClaw 运行时
  timeout=120,       # 2分钟超时
  prompt="..."       # 任务描述
)
```

### Benchmark 执行
```bash
cd /root/.openclaw/workspace/mas_repo/src/native
python harness_v31_0.py 2>&1 | tee results/harness_v31_run.log
```

### 资源监控
```bash
# 检查磁盘空间
df -h /root

# 检查内存
free -h

# 检查进程
ps aux | grep python
```
