#!/usr/bin/env python3
"""Generate missing generation reports for Gen121-Gen164"""

import json
import os

REPORTS_DIR = "/root/.openclaw/workspace/mas_repo/reports"
MAS_DIR = "/root/.openclaw/workspace/mas_repo/mas"
BENCHMARK_DIR = "/root/.openclaw/workspace/mas_repo"

REPORT_TEMPLATE = """# Generation {gen}: {arch}

**日期**: 2026-04-{day}  
**状态**: {status}  
**范式**: 极简分数优化  
**文件**: `mas/core_gen{gen}.py`

---

## 架构拓扑图

```mermaid
graph TB
    subgraph Input["输入层"]
        Q[Query Input<br/>查询输入]
    end
    
    subgraph Core["核心处理层"]
        CLA[Classifier<br/>任务分类器]
        BGT[Budget Allocator<br/>预算分配器]
        EXE[Executor<br/>执行器]
    end
    
    subgraph Output["输出层"]
        SEL[Selector<br/>选择器]
        FMT[Formatter<br/>格式化器]
    end
    
    Q --> CLA
    CLA --> BGT
    BGT --> EXE
    EXE --> SEL
    SEL --> FMT
    
    style Core fill:#e3f2fd
    style Input fill:#fff3e0
    style Output fill:#e8f5e9
```

---

## 评估结果

| 指标 | Gen{gen} | Gen{prev} | 变化 |
|------|----------|-----------|------|
| **Score** | {score} | {prev_score} | {score_change} |
| **Token** | {token} | {prev_token} | {token_change} |
| **Efficiency** | {eff:,} | {prev_eff:,} | {eff_change} |

### 效率演进

```
Efficiency (log scale)
     │
{eff:,.0f} ─┤ ████████████████████ Gen{gen}
       |
{prev_eff:,.0f} ─┤ ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄ Gen{prev}
       └────────────────────────────────────────▶ 代数
```

---

## 技术规格

```python
# Gen{gen} 核心参数
ARCHITECTURE = "{arch}"

METRICS = {{
    "score": {score},
    "token": {token},
    "efficiency": {eff:,.0f}
}}
```

---

## {status_detail}

{analysis}

---

*架构版本: v{gen}.0*  
*演进代数: {gen}/164*  
*状态: {status}*
"""

def get_prev_gen(gen):
    """Find previous generation with data"""
    for g in range(gen-1, 0, -1):
        f = os.path.join(BENCHMARK_DIR, f"benchmark_results_gen{g}.json")
        if os.path.exists(f):
            return g
    return gen - 1

def main():
    for g in range(121, 165):
        report_file = os.path.join(REPORTS_DIR, f"GEN{g}_REPORT.md")
        
        # Skip if report exists
        if os.path.exists(report_file):
            print(f"Gen{g}: Report exists, skipping")
            continue
        
        # Get benchmark data
        benchmark_file = os.path.join(BENCHMARK_DIR, f"benchmark_results_gen{g}.json")
        if not os.path.exists(benchmark_file):
            print(f"Gen{g}: No benchmark data, skipping")
            continue
            
        with open(benchmark_file) as f:
            data = json.load(f)
            arch = data.get("architecture", "Minimal Surplus Exploration")
            score = data["summary"]["avg_score"]
            token = data["summary"]["avg_tokens"]
            eff = data["summary"]["efficiency"]
            verdict = data.get("verdict", "")
        
        # Get previous generation data
        prev = get_prev_gen(g)
        prev_file = os.path.join(BENCHMARK_DIR, f"benchmark_results_gen{prev}.json")
        with open(prev_file) as f:
            prev_data = json.load(f)
            prev_score = prev_data["summary"]["avg_score"]
            prev_token = prev_data["summary"]["avg_tokens"]
            prev_eff = prev_data["summary"]["efficiency"]
        
        # Determine status
        if "新冠军" in verdict or "CHAMPION" in verdict.upper():
            status = "🏆🏆🏆 新冠军"
        elif eff > 100000:
            status = "🏆🏆 冠军候选"
        elif score >= 81:
            status = "✅ 达标"
        else:
            status = "⚠️ 待优化"
        
        # Calculate changes
        score_change = f"{score - prev_score:+.0f}"
        token_change = f"{token - prev_token:+.1f}"
        if prev_eff > 0:
            eff_change = f"{((eff - prev_eff) / prev_eff * 100):+.1f}%"
        else:
            eff_change = "NEW" if eff > 0 else "0%"
        
        # Generate analysis
        if "新冠军" in verdict or eff > prev_eff * 1.1:
            analysis = f"""### 突破性进展

Gen{g}相比Gen{prev}实现重大突破：
- Token消耗: {prev_token:.1f} → {token:.1f} ({token_change})
- 效率指数: {prev_eff:,.0f} → {eff:,.0f} ({eff_change})
"""
        elif eff == prev_eff:
            analysis = f"""### 稳定分析

Gen{g}匹配Gen{prev}的性能：
- Token消耗: {token:.1f} ≈ {prev_token:.1f}
- 效率指数: {eff:,.0f} ≈ {prev_eff:,.0f}
"""
        else:
            analysis = f"""### 回归分析

Gen{g}未能超越Gen{prev}：
- Token消耗: {token:.1f} vs {prev_token:.1f}
- 效率指数: {eff:,.0f} vs {prev_eff:,.0f}
"""
        
        day = "02"
        content = REPORT_TEMPLATE.format(
            gen=g,
            arch=arch,
            day=day,
            status=status,
            prev=prev,
            prev_score=prev_score,
            prev_token=prev_token,
            prev_eff=prev_eff,
            score=score,
            token=token,
            eff=eff,
            score_change=score_change,
            token_change=token_change,
            eff_change=eff_change,
            status_detail="突破性进展" if "新冠军" in status else "性能分析",
            analysis=analysis
        )
        
        with open(report_file, "w") as f:
            f.write(content)
        
        print(f"Gen{g}: Score={score}, Token={token}, Eff={eff:,.0f} | {status}")

if __name__ == "__main__":
    main()
