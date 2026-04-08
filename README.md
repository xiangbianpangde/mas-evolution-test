# AutoMAS: Automated Multi-Agent System Harness Evolution

> Endless evolution engine for benchmarking and optimizing AI agent architectures.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Model: MiniMax-M2.7](https://img.shields.io/badge/Model-MiniMax--M2.7-blue)](https://minimax.io)

## 🎯 What is AutoMAS?

AutoMAS is an automated benchmarking and evolution system for AI agent architectures. It runs 15 standardized tasks (10 core + 5 generalization) against different harness configurations, measures performance, and evolves better strategies over time.

## 📊 Current Champion

| Version | Composite | Core | Gen | Status |
|---------|----------|------|-----|--------|
| **v31.0** | **76.22** | 79.2 | 81.0 | 🏆 Current Best |

## 🚀 Quick Start

```bash
# 1. Set API key
export MINIMAX_API_KEY="your-api-key"

# 2. Run single evolution round
python src/native/harness_evolution.py --round 1

# 3. Run continuous evolution
python src/native/harness_evolution.py --continuous
```

## 📁 Project Structure

```
.
├── src/
│   ├── native/
│   │   ├── harness_evolution.py    # Evolution engine
│   │   ├── self_verifier.py         # Self-verification
│   │   ├── strategy_registry.py      # Strategy registry
│   │   └── harness/                # Harness versions
│   └── benchmark/
│       └── tasks_v2.py             # 15 benchmark tasks
├── knowledge/                        # System documentation
├── experiments/                      # Experiment tracking
├── results/
│   ├── benchmarks/                  # Benchmark results
│   ├── checkpoints/                 # Checkpoint files
│   └── evolution/                   # Evolution state
└── memory/                          # Session memory
```

## 🔬 Benchmark Tasks

### Core Tasks (10)
Research and code tasks covering:
- Transformer attention optimization
- Distributed cache systems
- RAG retrieval enhancement
- Microservice rate limiting
- Multimodal RAG
- Vector database optimization
- Graph database queries
- Real-time data streaming
- Knowledge graph construction
- Security authentication

### Generalization Tasks (5)
Harder tasks testing generalization:
- Quantum computing
- Federated learning
- Zero-knowledge proofs
- Neural architecture search
- Edge deployment

## 📈 Evolution Strategies

| Strategy | Tokens | Runs | Temp | Reflect | Score |
|----------|--------|------|------|---------|-------|
| v31.0 🏆 | 5000/5000 | 2 | 0.7 | core_only | **76.22** |
| v33 | 5000/5000 | 3 | 0.5 | none | 73.44 |
| v32 | 6000/5500 | 2 | 0.7 | core_only | 72.22 |

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [ARCHITECTURE.md](knowledge/ARCHITECTURE.md) | System architecture overview |
| [TEAM_DESIGN.md](knowledge/TEAM_DESIGN.md) | Multi-agent team design |
| [EXPERIMENT_DESIGN.md](knowledge/EXPERIMENT_DESIGN.md) | Benchmark design |
| [LESSONS.md](knowledge/LESSONS.md) | Lessons learned |
| [HARNESS_KNOWLEDGE.md](knowledge/HARNESS_KNOWLEDGE.md) | Industry best practices |

## 🔒 Anti-Fraud Mechanisms

- **Self-verification**: Each task output is validated before acceptance
- **Triple verification**: File existence + content + cross-validation
- **Resource limits**: CPU, memory, disk space enforced
- **API tracking**: All API calls logged

## 📝 License

MIT License - see [LICENSE](LICENSE) for details.

---

**AutoMAS** is maintained by the Genesis Team.
