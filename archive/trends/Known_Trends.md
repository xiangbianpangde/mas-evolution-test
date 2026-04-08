# MAS Architecture - Known Trends

## Self-Reflection Impact
| Task Type | Self-Reflection | Effect |
|-----------|---------------|--------|
| Core Research | ✅ Yes | +10-20 score |
| Gen Research | ❌ No | Gen=72.6 vs 53.2 (with) |
| Gen Review | ❌ No | 禁止! 破坏结构 |
| Code | ❌ No | 禁止! 破坏代码结构 |
| Gen Code | ❌ No | gen_002=65 without, 15 with |

## Token Budget
- 5000 tokens: 最佳平衡点 (v31 验证)
- 6000 tokens: v32 略低
- 3000 tokens: review 专用

## Prompt Strategy
- Core research: 详细结构化 (CORE_RESEARCH_PROMPT)
- Gen research: V15_GEN_RESEARCH_PROMPT (轻量)
- Code: CODE_PROMPT (完整可运行要求)
- Review: 风险矩阵格式

## Evaluator Choice
- research/review: STRICT_EVALUATOR
- code: LENIENT_CODE_EVALUATOR (给分从宽)

## MAX Strategy
- 2 runs (v31): 最佳
- 3 runs (v33): 反而增加方差

## Failed Experiments
- v37: 扩展自评审到所有任务 → 69.07 (FAIL)
- v33: MAX-3 → 73.44 < 76.22 (FAIL)
