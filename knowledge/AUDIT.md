# Deep System Audit Report

**Auditor:** Deep Auditor Agent  
**Date:** 2026-04-09  
**Scope:** Full system review across 7 dimensions  
**Status:** ⚠️ CRITICAL GAPS FOUND — Block experiments until resolved

---

## Executive Summary

The system has **37 identified gaps**, of which **12 are critical** that can cause silent data corruption, incorrect evolution decisions, or resource exhaustion. The evolution loop has a **brittle code-generation mechanism**, the **state management is fragmented**, and the **scoring formula is inconsistently applied**.

---

## 1. Evolution Loop Integrity

### 🔴 Critical

**[E-001] DUAL STATE UPDATE PATHS — Race Condition**
- `harness_evolution.py` writes to `results/evolution/state.json` via `record_result()` → `save_state()`
- `harness_v31_0.py` also calls `self._update_state()` which writes to the SAME file
- In continuous mode, two processes can write simultaneously → **state corruption**
- **Fix:** Unify state writes to one authoritative location; use file locking

**[E-002] CODE GENERATION VIA STRING REPLACEMENT — Brittle**
- `apply_strategy_to_code()` in `harness_evolution.py` uses hardcoded string patterns to inject strategy parameters
- Example: `old_func = '''...'''` match expects exact whitespace/format
- Template formatting changes → **silent failure** → strategy parameters NOT applied → experiments produce v31_0 clones
- Evidence: `evolution/history.json` shows `evo_001` and `evo_002` scored 0 — likely strategy was not applied
- **Fix:** Use AST manipulation or template engine (Jinja2), not string matching

**[E-003] `evolution_loop.py` IS A SIMULATION — Not Connected**
- `run_benchmark()` returns `random.uniform(-5, 10)` — **fake scores**
- The "real" evolution loop is `harness_evolution.py` with `--continuous` flag
- These are two completely separate codebases with different logic
- **Fix:** Remove `evolution_loop.py` or clearly mark it as a simulation mock

### 🟡 Medium

**[E-004] HARDCODED CHAMPION SCORE IN TWO PLACES**
- `CHAMPION_SCORE = 76.22` in `evolution_loop.py`
- `best_score: 76.22` in `evolution_state.json`
- No single source of truth; changing one doesn't update the other
- **Fix:** Read from `state.json` only; remove `CHAMPION_SCORE` constant

**[E-005] TEMPLATE DEPENDENCY — `harness_v31_0.py` Is The Only Template**
- All generated harnesses derive from `harness_v31_0.py` via `apply_strategy_to_code()`
- Any v31_0 bugs get propagated to ALL generated versions
- **Fix:** Extract template into a dedicated `harness_template.py` with versioned snapshots

**[E-006] `self.max_runs` INJECTION UNVERIFIED**
- `apply_strategy_to_code` adds `self.max_runs = {max_runs}` to `__init__`
- But v31_0 already has a hardcoded double-run pattern; the injection creates `self.max_runs` but the existing hardcoded `for run_i in range(1, self.max_runs + 1)` loop depends on it being set
- If the replacement fails silently, `self.max_runs` is undefined → NameError
- **Fix:** Add validation that `self.max_runs` is set before use

---

## 2. Error Handling

### 🔴 Critical

**[EH-001] API KEY IN SOURCE CODE — Security Risk**
- `harness_v31_0.py` line: `api_key = "sk-cp-ZNEhSAB4..."` (hardcoded)
- `harness_v40.py` same pattern
- Key appears in git history forever
- **Fix:** Use environment variable `MINIMAX_API_KEY` only; remove all hardcoded keys

**[EH-002] NO SIGNAL HANDLING — Graceful Termination Impossible**
- No `signal.SIGTERM` / `signal.SIGINT` handlers in any harness
- `WallClockGuard` exists in `resource_limiter.py` but is **never imported or used** by any harness
- If harness is killed mid-run, checkpoint may be partially written → **corrupt state**
- **Fix:** Add signal handlers; use `WallClockGuard` in all harness runs

**[EH-003] `subprocess.run(timeout=14400)` IN `harness_evolution.py` — No Child Process Cleanup**
- If harness subprocess times out, `subprocess.run` kills it but **no cleanup** of orphaned child processes
- The spawned harness may have spawned its own subprocesses
- **Fix:** Use process group killing (`os.killpg`) on timeout

### 🟡 Medium

**[EH-004] CHECKPOINT INCOMPLETE — Cannot Resume Full State**
- `checkpoint["results"]` stores only the `best` result per task (after MAX comparison)
- Individual run scores (`run1_score`, `run2_score`) are stored in checkpoint dict but NOT used for recovery
- If crashed after run1 but before run2 completes, the MAX comparison is不公平
- **Fix:** Store all individual runs in checkpoint; on resume, re-run only missing runs

**[EH-005] API RETRY WITHOUT EXPONENTIAL BACKOFF**
- `BaseHarness.call_api()`: `time.sleep(2)` (constant, not exponential)
- `RealLLMCaller.call_with_retry()`: `time.sleep(2 ** attempt)` — correct
- `RealLLMCaller` is used by v31+, but `BaseHarness.call_api` is the documented standard
- Inconsistency: some code paths use backoff, some don't
- **Fix:** Standardize on exponential backoff everywhere

**[EH-006] JSON PARSE FAILURE SILENTLY DEFAULTS TO 50 SCORE**
- `parse_evaluator_response()` returns `{"overall_score": 50, ...}` on any parse failure
- No logging, no flagging as suspicious
- A completely broken evaluator response is indistinguishable from a 50-score response
- **Fix:** Log parse failures; flag result as `is_suspicious=True`

---

## 3. Resource Management

### 🔴 Critical

**[RM-001] `resource_limiter.py` EXISTS BUT IS NEVER USED**
- All limits (CPU, memory, process count, file size) are defined but **no harness imports it**
- `apply_all()` is defined but no caller
- Memory limit of 512MB may be easily exceeded with multiple concurrent API calls
- **Fix:** Import and call `apply_all()` at harness startup

**[RM-002] NO DISK SPACE MONITORING**
- `results/benchmarks/` has 80+ JSON result files
- `archive/` directory is 32MB
- No disk space check before running; could fill disk mid-benchmark
- **Fix:** Add pre-run disk space check; set alert threshold at 90% capacity

**[RM-003] NO MEMORY MONITORING DURING RUN**
- No RSS monitoring, no OOM prediction
- `get_usage()` in `resource_limiter.py` exists but is never called
- **Fix:** Call `get_usage()` every N tasks; log warning if RSS > 400MB

### 🟡 Medium

**[RM-004] NO CONCURRENT PROCESS LIMIT**
- `harness_evolution.py --continuous` could spawn multiple harness processes
- `check_and_trigger_evolution.py` only checks for "any harness running" but doesn't enforce exclusive access
- Two triggers in quick succession → two harnesses running simultaneously → **state file race**
- **Fix:** Use a lock file (`harness.lock`) for exclusive execution

**[RM-005] PROCESS ORPHANING ON PARENT CRASH**
- `trigger_evolution()` uses `subprocess.Popen` with no `start_new_session=True`
- If parent (OpenClaw agent) dies, child harness continues running orphaned
- **Fix:** Use `start_new_session=True` in Popen, or use a systemd service

---

## 4. Experiment Tracking

### 🔴 Critical

**[T-001] MULTIPLE, INCONSISTENT RESULT STORAGE**
- `results/benchmarks/benchmark_results_v*.json` (one per version)
- `results/benchmarks/checkpoint/v*_checkpoint.json` (intermediate)
- `results/evolution/history.json` (aggregated)
- `results/evolution/state.json` (current state)
- `src/native/evolution_state.json` (also exists — is this a third copy?)
- **NO unified experiment registry** — impossible to answer "what experiments have run?"
- **Fix:** Create `experiments/registry.json` as single source of truth for all experiment metadata

**[T-002] NO REPRODUCIBILITY — API VARIANCE UNMANAGED**
- README states "~8% natural variance" but there's **no seed control**
- No `random.seed()` or API temperature control beyond `strategy.get("temperature")`
- v31_0 uses `temperature=0.7` (default) — not explicitly set in v31_0, only in generated versions
- **Fix:** Explicitly set `temperature` in all harness versions; log actual temperature used

### 🟡 Medium

**[T-003] `harness_version` STRING INCONSISTENCY**
- `harness_v40.py` class is `HarnessV40` but `"harness_version": "v31.0"` in output
- `harness_v31_0.py` class is `HarnessV30` (not HarnessV31!) but outputs `"harness_version": "v31.0"`
- Makes benchmark comparison tools produce misleading output
- **Fix:** Class name should match harness version string exactly

**[T-004] LONG-TERM MEMORY NOT SYSTEMATICALLY UPDATED**
- `knowledge/lessons/Lessons_Learned.md` exists but is not referenced in evolution decisions
- No pre-experiment checklist that queries past lessons
- The system repeats known mistakes (e.g., v32 "6000 tokens边际递减" was predictable from v31 trend)
- **Fix:** Before each `run_harness()`, read relevant lessons and log whether they're being heeded

**[T-005] evo_001 SCORED 0 — DEAD END IN HISTORY**
- `history.json` shows `evo_001` and `evo_002` with `score: 0`
- No error recorded, no explanation
- Dead experiments pollute the history and confuse analysis
- **Fix:** On harness failure, record error type and actual exception message

---

## 5. Scoring Mechanism

### 🔴 Critical

**[S-001] COMPOSITE FORMULA INCONSISTENCY — README vs CODE**
- README states: `(Core × 0.5 + Gen × 0.5) × ActionabilityMultiplier`
- `base_harness.py` uses: `core_avg * 0.45 + gen_avg * 0.45 + (avg_actionability * 10) * 0.1`
- `harness_v31_0.py` uses: `core_avg * 0.45 + gen_avg * 0.45 + (avg_actionability * 10) * 0.1`
- These are **not equivalent** — 0.45+0.45+0.1=1.0 weights vs 0.5+0.5=1.0 with a multiplier
- At actionability=4.13: code formula gives `0.45*core + 0.45*gen + 4.13` vs README's `(0.5*core + 0.5*gen) * 4.13`
- **Impact:** Reported composite scores may not mean what README says they mean
- **Fix:** Choose ONE formula; document it precisely; update all code and README

**[S-002] ACTIONABILITY IS INTEGER L1-L5, NOT CONTINUOUS**
- `TaskResult.actionability_score: int  # 3` — stored as integer 1-5
- But `avg_actionability * 10` in composite → 30 to 50 range
- The "L4.13" notation in README is misleading — it's a float average of integer levels
- L4.13 means average level is between 4 and 5, but the actual levels are discrete
- **Fix:** Either use continuous 0-100 scale, or document clearly as discrete levels

### 🟡 Medium

**[S-003] GEN006_SCORER IS NEVER USED**
- `src/benchmark/gen006_scorer.py` defines a complete learning system scorer
- But actual benchmark evaluation uses `STRICT_EVALUATOR` / `LENIENT_CODE_EVALUATOR` prompts
- The gen006 scorer has different dimensions and weights — appears abandoned
- **Fix:** Either integrate it into the benchmark or remove it to avoid confusion

**[S-004] ACTIONABILITY CALCULATION EXCLUDES ZERO-SCORE TASKS**
- `avg_actionability = sum(r.actionability_score for r in clean_results if r.quality_score > 0) / max(len(all_scores), 1)`
- Tasks with `quality_score=0` (errors) are excluded from actionability denominator but included in the `max()` floor
- This biases actionability upward when errors occur
- **Fix:** Use consistent denominator (all tasks, including zero-score)

---

## 6. API Limits

### 🔴 Critical

**[A-001] NO API RATE LIMIT TRACKING**
- No tracking of calls per day, per hour
- No prevention of hitting daily limits mid-benchmark
- MiniMax API limit unknown and unmonitored
- **Fix:** Track API call count; estimate token usage; pause when approaching limits

**[A-002] NO TOKEN BUDGET TRACKING**
- `executor_tokens` and `evaluator_tokens` are tracked per task but never aggregated for budget control
- No pre-run estimate of total tokens needed
- No abort decision based on projected overspend
- **Fix:** Add token budget tracking; set `MAX_TOKENS_PER_DAY`; abort early if projected to exceed

### 🟡 Medium

**[A-003] NO CONCURRENCY LIMIT**
- In theory `MAX_RUNS_CONFIGS` could run tasks in parallel
- In practice v31_0 runs sequentially; but nothing enforces this
- No guard against accidentally parallelizing API calls beyond rate limits
- **Fix:** Define `MAX_CONCURRENT_API_CALLS` and enforce it

**[A-004] API TIMEOUT ONLY 180s BUT NO NETWORK ERROR HANDLING**
- `timeout=180` for individual calls
- Network partitions, DNS failures, proxy issues — not handled specifically
- `BaseHarness.call_api()` catches generic `Exception`
- **Fix:** Specific handling for `urllib.error.URLError`, `socket.timeout`, HTTP 429/500/503

---

## 7. GitHub Protocol

### 🟡 Medium

**[G-001] COMMIT CONVENTION NOT ENFORCED**
- `MANAGEMENT.md` defines `feat/fix/docs/test/refactor/chore` convention
- Git log shows commits like `Complete pre-experiment documentation` (not convention-compliant)
- No pre-commit hook or CI check
- **Fix:** Add `.commitlintrc` or pre-commit hook; document exception process

**[G-002] BRANCH STRATEGY UNDEFINED**
- `MANAGEMENT.md` shows `main` and `feature/*` but no actual branches exist in git
- All work happens on `main`
- `README.md` GitHub link points to external repo but no branch protection
- **Fix:** Define branch model; protect `main`; use PRs for harness changes

**[G-003] RELEASE PROCESS NOT DEFINED**
- No changelog generation
- No version tagging discipline (only 1 tag visible)
- No release branch or tag review process
- **Fix:** Add `CHANGELOG.md` auto-generation; tag every champion version

**[G-004] `.gitignore` INCOMPLETE**
- `results/` files are tracked in git (intentional) but `results/benchmarks/checkpoint/` should not be
- `__pycache__/` is properly ignored
- But `src/native/__pycache__/` is inside `src/native/` and may leak .pyc files
- **Fix:** Verify all cache files are ignored; add `*.log` local ignores

---

## Gap Summary Table

| ID | Area | Severity | Impact |
|----|------|----------|--------|
| E-001 | Evolution | 🔴 Critical | State race condition |
| E-002 | Evolution | 🔴 Critical | Silent strategy failure |
| E-003 | Evolution | 🔴 Critical | Fake evolution loop |
| EH-001 | Errors | 🔴 Critical | API key exposure |
| EH-002 | Errors | 🔴 Critical | No graceful shutdown |
| EH-003 | Errors | 🔴 Critical | Orphaned processes |
| RM-001 | Resources | 🔴 Critical | Limits not enforced |
| RM-002 | Resources | 🔴 Critical | Disk exhaustion |
| T-001 | Tracking | 🔴 Critical | Fragmented state |
| S-001 | Scoring | 🔴 Critical | Wrong formula |
| A-001 | API | 🔴 Critical | No rate limit tracking |
| A-002 | API | 🔴 Critical | No token budget |
| E-004 | Evolution | 🟡 Medium | Hardcoded constants |
| E-005 | Evolution | 🟡 Medium | Template single point |
| E-006 | Evolution | 🟡 Medium | Unverified injection |
| EH-004 | Errors | 🟡 Medium | Checkpoint gaps |
| EH-005 | Errors | 🟡 Medium | Inconsistent backoff |
| EH-006 | Errors | 🟡 Medium | Silent JSON failures |
| RM-003 | Resources | 🟡 Medium | No memory monitoring |
| RM-004 | Resources | 🟡 Medium | No exclusive lock |
| RM-005 | Resources | 🟡 Medium | Orphaned on crash |
| T-002 | Tracking | 🟡 Medium | Unreproducible runs |
| T-003 | Tracking | 🟡 Medium | Version string mismatch |
| T-004 | Tracking | 🟡 Medium | Lessons not consulted |
| T-005 | Tracking | 🟡 Medium | Dead experiments |
| S-002 | Scoring | 🟡 Medium | Actionability discrete |
| S-003 | Scoring | 🟡 Medium | Unused scorer |
| S-004 | Scoring | 🟡 Medium | Biased actionability |
| A-003 | API | 🟡 Medium | No concurrency limit |
| A-004 | API | 🟡 Medium | Poor network handling |
| G-001 | GitHub | 🟡 Medium | No convention enforcement |
| G-002 | GitHub | 🟡 Medium | No branch model |
| G-003 | GitHub | 🟡 Medium | No release process |
| G-004 | GitHub | 🟡 Medium | Incomplete gitignore |

---

## Priority Fixes (Before Next Experiment)

1. **[E-002]** Replace `apply_strategy_to_code` string matching with AST/template approach
2. **[E-001]** Add file locking to `state.json` writes
3. **[EH-001]** Move API key to environment variable immediately
4. **[S-001]** Unify composite score formula — pick one and document
5. **[RM-001]** Import `resource_limiter.apply_all()` in harness startup
6. **[T-001]** Create unified `experiments/registry.json`
7. **[A-001]** Add API call counter and daily limit tracking
8. **[EH-002]** Add SIGTERM/SIGINT handlers to all harness scripts

---

*Audit completed by Deep Auditor Agent — 2026-04-09*
