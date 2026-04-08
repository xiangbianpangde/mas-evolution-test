# Lessons Learned

## v5.0 Native MAS 失败原因 (Score 19.6)
1. **超时太短**: 60s 超时导致复杂任务失败
2. **无重试**: API 失败后直接放弃
3. **解析脆弱**: JSON 解析无容错
4. **max_tokens 太小**: 2048 不够复杂任务

## Python Harness 作弊问题
- Mock Token: Gen1-400 全是假数据
- 启发式评分: 非真实 LLM 评估
- 不可信: 无法证明真实环境能力

## 自反射规则 (黄金法则)
- **Core research**: 需要自反射
- **Gen research**: 禁止自反射 (破坏结构)
- **Core review**: 可选
- **Gen review**: 禁止自反射
- **Code (所有)**: 禁止自反射 (破坏代码)

## Token Budget 发现
- 5000: v31 验证最佳
- 6000: 略差 (浪费)
- 3000: 仅 review 可用

## 多轮策略
- 2 runs + MAX: v31 成功
- 3 runs + MAX-3: v33 失败 (方差增加)

## 评分维度
- Depth: 技术深度
- Completeness: 完整性
- Actionability: 可操作性
- Overall: 0-100 加权
