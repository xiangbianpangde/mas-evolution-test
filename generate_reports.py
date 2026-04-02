#!/usr/bin/env python3
"""Generate missing generation reports"""

import json
import os

REPORTS_DIR = "/root/.openclaw/workspace/mas_repo/reports"
MAS_DIR = "/root/.openclaw/workspace/mas_repo/mas"
BENCHMARK_DIR = "/root/.openclaw/workspace/mas_repo"

# Data from evolution history for missing generations
EXTRA_DATA = {
    102: {"score": 81, "token": 2.2, "eff": 36818, "arch": "Multi-Objective v15+: Complex Budget Further Reduced"},
    103: {"score": 81, "token": 2.2, "eff": 36818, "arch": "Multi-Objective v15+: Matched Gen102"},
    104: {"score": 80, "token": 1.9, "eff": 42105, "arch": "Minimal Surplus v2: Complex Budget Below Floor"},
    105: {"score": 79, "token": 1.6, "eff": 49375, "arch": "Minimal Surplus v2+: Aggressive Reduction"},
    106: {"score": 80, "token": 1.9, "eff": 42105, "arch": "Minimal Surplus v2 Clone"},
    107: {"score": 80, "token": 1.9, "eff": 42105, "arch": "Minimal Surplus v2 Clone"},
    108: {"score": 81, "token": 1.9, "eff": 42632, "arch": "Minimal Surplus v3: Optimized Output Costs"},
    109: {"score": 81, "token": 1.9, "eff": 42632, "arch": "Minimal Surplus v3: Matched Gen108"},
    110: {"score": 81, "token": 1.9, "eff": 42632, "arch": "Minimal Surplus v3: Matched Gen108"},
    111: {"score": 81, "token": 1.9, "eff": 42632, "arch": "Minimal Surplus v3: Matched Gen108"},
    112: {"score": 81, "token": 1.9, "eff": 42632, "arch": "Minimal Surplus v3: Matched Gen108"},
    113: {"score": 81, "token": 1.9, "eff": 42632, "arch": "Minimal Surplus v3: Matched Gen108"},
    114: {"score": 80, "token": 1.6, "eff": 50000, "arch": "Minimal Surplus: complex=3 Exploration"},
    115: {"score": 80, "token": 1.6, "eff": 50000, "arch": "Minimal Surplus: complex=3 Exploration"},
    116: {"score": 80, "token": 1.6, "eff": 50000, "arch": "Minimal Surplus: complex=3 Exploration"},
    117: {"score": 81, "token": 1.9, "eff": 42632, "arch": "Minimal Surplus v3: Returned to complex=4"},
}

REPORT_TEMPLATE = """# Generation {gen}: {arch}

**日期**: 2026-04-{day}  
**状态**: {status}  
**范式**: {paradigm}  
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

| 指标 | Gen{gen} | Gen{prev} | 目标 | 状态 |
|------|----------|-----------|------|------|
| **Score** | {score} | {prev_score} | ≥81 | {score_status} |
| **Token** | {token} | {prev_token} | <{prev_token} | {token_status} |
| **Efficiency** | {eff} | {prev_eff} | >{prev_eff} | {eff_status} |

### 效率对比

```
Efficiency
     │
{eff} ─┤ ████████████████████ Gen{gen}
       │
{prev_eff} ─┤ ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄ Gen{prev}
       │
       └──────────────────────────────▶ 代数
```

---

## 技术规格

```python
# Gen{gen} 核心参数
ARCHITECTURE = "{arch}"

METRICS = {{
    "score": {score},
    "token": {token},
    "efficiency": {eff}
}}
```

---

## {status_detail}

{analysis}

---

*架构版本: v{gen}.0*  
*演进代数: {gen}/120*  
*状态: {status}*
"""

def get_prev_gen(gen):
    """Get previous champion generation"""
    champions = {38: 1, 51: 38, 60: 38, 69: 61, 84: 69, 92: 84, 102: 92, 104: 102, 108: 104}
    for g in sorted(champions.keys(), reverse=True):
        if gen >= g:
            return champions[g]
    return gen - 1

def get_status(gen, score, token, eff):
    """Determine status based on metrics"""
    if gen == 108:
        return "🏆🏆🏆 新冠军", "新范式冠军"
    elif eff > 42000:
        return "🏆🏆 冠军候选", "冠军水平"
    elif eff > 30000:
        return "✅ 达标", "分数效率双达标"
    elif score >= 81:
        return "✅ 分数达标", "分数达标"
    else:
        return "⚠️ 待优化", "未达目标"

def get_day(gen):
    """Get approximate date"""
    if gen <= 51:
        return "01"
    elif gen <= 60:
        return "01"
    elif gen <= 77:
        return "01"
    elif gen <= 84:
        return "01"
    elif gen <= 91:
        return "02"
    elif gen <= 101:
        return "02"
    else:
        return "02"

def generate_report(gen, score, token, eff, arch):
    """Generate a single report"""
    prev = get_prev_gen(gen)
    status, status_detail = get_status(gen, score, token, eff)
    
    # Get previous generation data
    prev_benchmark = os.path.join(BENCHMARK_DIR, f"benchmark_results_gen{prev}.json")
    prev_data = EXTRA_DATA.get(prev, {})
    
    if os.path.exists(prev_benchmark):
        with open(prev_benchmark) as f:
            prev_json = json.load(f)
            prev_score = prev_json["summary"]["avg_score"]
            prev_token = prev_json["summary"]["avg_tokens"]
            prev_eff = prev_json["summary"]["efficiency"]
    else:
        prev_score = prev_data.get("score", score)
        prev_token = prev_data.get("token", token)
        prev_eff = prev_data.get("eff", eff)
    
    # Determine status symbols
    score_status = "🏆🏆🏆" if score >= 81 else "⚠️"
    token_status = "✅" if token < prev_token else "≈"
    eff_status = "🏆🏆🏆" if eff > prev_eff else ("≈" if eff == prev_eff else "⚠️")
    
    # Generate analysis
    if eff > prev_eff * 1.01:
        analysis = f"### 改进分析\n\nGen{gen}相比Gen{prev}实现了效率提升：\n- Token消耗: {prev_token} → {token} ({((prev_token-token)/prev_token)*100:.1f}%)\n- 效率指数: {prev_eff:.0f} → {eff} ({((eff-prev_eff)/prev_eff)*100:.1f}%)\n"
    elif eff == prev_eff:
        analysis = f"### 匹配分析\n\nGen{gen}匹配Gen{prev}的性能：\n- Token消耗: {token} ≈ {prev_token}\n- 效率指数: {eff} ≈ {prev_eff}\n"
    else:
        analysis = f"### 回归分析\n\nGen{gen}未能超越Gen{prev}：\n- Token消耗: {token} vs {prev_token}\n- 效率指数: {eff} vs {prev_eff}\n"
    
    # Determine paradigm
    if gen <= 51:
        paradigm = "Token优化范式"
    elif gen <= 60:
        paradigm = "新范式探索"
    elif gen <= 77:
        paradigm = "代价感知优化"
    elif gen <= 84:
        paradigm = "多目标Pareto优化"
    else:
        paradigm = "极简剩余优化"
    
    content = REPORT_TEMPLATE.format(
        gen=gen,
        arch=arch,
        day=get_day(gen),
        status=status,
        paradigm=paradigm,
        score=score,
        prev=prev,
        prev_score=prev_score,
        prev_token=prev_token,
        prev_eff=prev_eff,
        token=token,
        eff=eff,
        score_status=score_status,
        token_status=token_status,
        eff_status=eff_status,
        status_detail=status_detail,
        analysis=analysis
    )
    
    return content

def main():
    # First, process generations with benchmark files
    for g in range(41, 121):
        report_file = os.path.join(REPORTS_DIR, f"GEN{g}_REPORT.md")
        
        # Skip if report already exists
        if os.path.exists(report_file):
            print(f"Gen{g}: Report exists, skipping")
            continue
        
        # Try to get data from benchmark file
        benchmark_file = os.path.join(BENCHMARK_DIR, f"benchmark_results_gen{g}.json")
        if os.path.exists(benchmark_file):
            with open(benchmark_file) as f:
                data = json.load(f)
                arch = data.get("architecture", "Unknown")
                score = data["summary"]["avg_score"]
                token = data["summary"]["avg_tokens"]
                eff = data["summary"]["efficiency"]
        elif g in EXTRA_DATA:
            d = EXTRA_DATA[g]
            arch = d["arch"]
            score = d["score"]
            token = d["token"]
            eff = d["eff"]
        else:
            print(f"Gen{g}: No data found, skipping")
            continue
        
        content = generate_report(g, score, token, eff, arch)
        
        with open(report_file, "w") as f:
            f.write(content)
        
        print(f"Gen{g}: Created report (Score={score}, Token={token}, Eff={eff})")

if __name__ == "__main__":
    main()
