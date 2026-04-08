# Team SOUL - Harness Evolution Engine Coordination

## Overview
This document defines how the 5-agent team coordinates to achieve endless harness evolution.

## Agent Hierarchy
```
Hermes (Communication Bus) - State Manager & Trigger
    ↓ coordinates
Prometheus (Infrastructure) ←→ Athena (Analysis)
    ↓ execution support         ↓ pattern detection
Helios (Monitor) → Archaeus (Archivist) → GitHub
```

## Coordination Flow

### Evolution Round Lifecycle
1. **Hermes** checks state → determines if evolution should run
2. **Prometheus** executes harness benchmark
3. **Helios** monitors execution for anomalies
4. **Athena** analyzes results post-completion
5. **Archaeus** commits results and updates knowledge base
6. Loop back to Hermes

### State File Protocol
`results/evolution/state.json` is the single source of truth:
```json
{
  "current_round": 0,
  "best_score": 76.22,
  "best_version": "v31_0",
  "no_progress_rounds": 0,
  "history": [],
  "mode": "infinite"
}
```

### Anomaly Response Flow
```
Helios detects anomaly
    → Alert Hermes
    → Hermes updates state
    → If critical: Prometheus executes rollback
    → Archaeus logs incident
```

## Team Meeting Protocol
No actual meetings. Instead:
- **State file** is the shared workspace
- **GitHub commits** serve as announcements
- **Anomaly alerts** are written to `results/evolution/anomalies.log`

## Execution Priorities
1. Never let a benchmark run die without completion
2. Always commit after a round completes
3. Update README after champion changes
4. Preserve knowledge before system changes
