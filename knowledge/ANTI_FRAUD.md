# Anti-Fraud Protocol - 多Agent串通欺诈防御

## 🚨 核心威胁模型

### 攻击向量
```
执行Agent ──(偷懒)──→ 低质量产出
                            ↓
              检查Agent ──(幻觉)──→ 虚假高分
                            ↓
                      主Agent ──(误判)──→ 接受虚假结果
```

### 后果
- 虚假高分 → 误判策略有效 → 继续错误方向
- 系统性欺骗 → 整个演进失效

---

## 🛡️ 防御机制

### 1. 三重验证原则 (Never Trust Single Source)

所有关键结果必须通过**三个独立来源**验证：

| 验证项 | Source 1 | Source 2 | Source 3 |
|--------|----------|----------|----------|
| 分数 | Agent 自报 | 结果 JSON | checkpoint |
| executor_output | 结果文件 | checkpoint | 独立读取 |
| 完成状态 | Agent 自报 | 进程状态 | 文件存在 |

### 2. 关键数据必须存在

```yaml
acceptable_result:
  executor_output: NOT_NULL  # 实际输出必须存在
  quality_score: VALID_RANGE  # 0-100
  composite_score: VALID_RANGE
  timestamp: NOT_OLD  # 不超过2小时

suspicious_result:
  executor_output: NULL  # ❌ 无输出
  quality_score: >95  # ❌ 异常高分
  timestamp: STALE  # ❌ 过时
```

### 3. 随机抽样审计

每10次实验，随机选择1次进行**深度审计**：

```python
def deep_audit(version):
    # 1. 验证文件存在
    assert output_file.exists()
    
    # 2. 验证输出长度 (不能太短)
    output = read_file(output_file)
    assert len(output) > 1000, "Output too short - suspicious"
    
    # 3. 验证内容质量 (抽样检查)
    assert contains_code_blocks(output) or contains_analysis(output)
    
    # 4. 独立重新评分 (如果可能)
    # 不依赖Agent自报的分数
    
    # 5. 与同版本历史对比 (异常检测)
    prev = get_previous_version(version)
    if abs(current_score - prev_score) > 15:
        flag_as_suspicious()
```

### 4. 交叉Agent验证

```python
def cross_validate(result_file):
    """不同Agent独立验证同一结果"""
    
    # Agent A 验证
    validator_a = ValidatorAgent()
    score_a = validator_a.evaluate(result_file)
    
    # Agent B 验证 (不同模型/prompt)
    validator_b = CrossValidatorAgent()
    score_b = validator_b.evaluate(result_file)
    
    # Agent C 独立读取原始输出
    raw_output = read_raw_output(result_file)
    score_c = independent_scorer(raw_output)
    
    # 三者必须一致
    assert abs(score_a - score_b) < 5, "Validator disagreement"
    assert abs(score_a - score_c) < 10, "Cross-scorer mismatch"
```

### 5. 溯源验证

每个结果必须能回答：

- [ ] executor_output 是否来自**真实API调用**？
- [ ] 分数是否来自**真实评估**？
- [ ] 是否存在**时间戳矛盾**？
- [ ] 是否存在**克隆/复制**其他结果的痕迹？

---

## 🔴 红线判定

以下情况立即标记为**高危欺诈嫌疑**：

| 情况 | 风险等级 |
|------|----------|
| 有分数但无 executor_output | 🔴 严重 |
| 分数 > 95 | 🔴 严重 |
| 输出长度 < 500 字符 | 🔴 严重 |
| 三次运行分数完全相同 | 🔴 严重 |
| 与历史版本输出高度重复 | 🟡 可疑 |
| 进程声称完成但文件时间戳矛盾 | 🟡 可疑 |

---

## 📋 主Agent职责

### 永远执行的检查

1. **文件存在性**：声称创建的文件必须存在
2. **内容非空**：输出不能为空或过短
3. **时间戳一致**：文件时间与声称的时间匹配
4. **多源交叉**：不依赖单一agent的汇报

### 决策规则

```
IF 有分数 AND 无输出:
    → 判定: SUSPICIOUS
    → 行动: 独立重新执行

IF 分数 > 95:
    → 判定: NEEDS_AUDIT
    → 行动: 深度审计

IF Agent声称完成 AND 文件不存在:
    → 判定: FRAUD
    → 行动: 记录并警告
```

---

## 🔄 团队欺诈应对

如果检测到欺诈：

1. **立即隔离** - 停止相关agent
2. **独立重做** - 主agent亲自执行
3. **记录欺诈** - 写入审计日志
4. **追究责任** - 标记为不可信
5. **系统性修复** - 堵住漏洞

---

## 📊 审计日志格式

```json
{
  "version": "evo_001",
  "timestamp": "2026-04-09T00:08:00",
  "checks": {
    "file_exists": true,
    "output_length": 5234,
    "score_reasonable": true,
    "cross_validated": true,
    "audit_passed": true
  },
  "risk_level": "LOW",
  "verified_by": "independent_check",
  "notes": []
}
```

---

*Last updated: 2026-04-09*
