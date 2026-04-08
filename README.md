# AutoMAS - Harness Endless Evolution Engine

Automated Multi-Agent System for benchmarking and evolving AI agent architectures.

## Status

| | |
|---|---|
| **Champion** | v31.0 (76.22) |
| **Framework** | OpenClaw + MiniMax-M2.7 |
| **Tasks** | 15 (10 Core + 5 Gen) |
| **License** | MIT |

## Quick Start

```bash
# Set API key
export MINIMAX_API_KEY="your-key"

# Run evolution
python src/native/harness_evolution.py --round 1
```

## Benchmark Tasks

| Category | Count | Description |
|----------|-------|-------------|
| Core | 10 | Research + Code (Transformer, RAG, etc.) |
| Gen | 5 | Generalization (Quantum, ZKP, etc.) |

## Architecture

```
src/
├── native/
│   ├── harness_evolution.py  # Evolution engine
│   ├── harness/              # Harness versions
│   ├── self_verifier.py      # Self-verification
│   └── strategy_registry.py   # Strategy registry
└── benchmark/
    └── tasks_v2.py          # Task definitions

knowledge/     # Team & experiment docs
experiments/    # Experiment tracking
results/        # Benchmark results
```

## Evolution Strategy

| Strategy | Tokens | Runs | Temp | Score |
|----------|--------|------|------|-------|
| v31.0 🏆 | 5000/5000 | 2 | 0.7 | **76.22** |
| v33 | 5000/5000 | 3 | 0.5 | 73.44 |
| v32 | 6000/5500 | 2 | 0.7 | 72.22 |

## Documentation

| Doc | Purpose |
|-----|---------|
| `knowledge/ARCHITECTURE.md` | System architecture |
| `knowledge/TEAM_DESIGN.md` | Agent team design |
| `knowledge/EXPERIMENT_DESIGN.md` | Benchmark design |
| `knowledge/LESSONS.md` | Lessons learned |
| `knowledge/HARNESS_KNOWLEDGE.md` | Industry best practices |

## License

MIT
