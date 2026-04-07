# OpenClaw Native MAS - v6.0 Native Agent Orchestration

## Architecture

This implementation uses **sessions_spawn** to coordinate real Agent subagents instead of Python harness code.

```
User/Orchestrator → Supervisor Agent → sessions_spawn → Worker Agents
                                    ↓
                            Result Aggregation
                                    ↓
                            Quality Evaluation
```

## Key Improvements over v5.0

| Issue | v5.0 | v6.0 Fix |
|-------|------|----------|
| Timeout too short | 60s | 180s |
| No retry | ✗ | 3x retry with exponential backoff |
| JSON parsing | Fragile | Fault-tolerant with multiple extraction strategies |

## Supervisor Agent Role

The Supervisor analyzes each task and spawns appropriate Worker agents:
- **research** query → spawn research_agent
- **code** query → spawn code_agent  
- **review** query → spawn review_agent

## sessions_spawn Protocol

Workers are spawned via sessions_spawn with:

```json
{
  "task": "<task_query>",
  "runtime": "subagent",
  "agentId": "<worker_type>_agent",
  "mode": "run",
  "sandbox": "inherit"
}
```

## Implementation

The Supervisor Agent (defined in mas_agents/supervisor/SOUL.md) coordinates the benchmark by:

1. Loading tasks from tasks_v2.py
2. For each task, spawning the appropriate Worker via sessions_spawn
3. Collecting Worker outputs
4. Aggregating results and computing scores

## Execution

To run the Native MAS benchmark:

```bash
cd /root/.openclaw/workspace/mas_repo
python3 -c "
from openclaw_native.native_supervisor import NativeSupervisor
supervisor = NativeSupervisor()
results = supervisor.run_benchmark()
print(results)
"
```

Or via CLI:

```bash
openclaw agent --agent supervisor --message "run_benchmark"
```