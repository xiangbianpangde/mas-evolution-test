"""
Resource Limiter - CPU & Memory constraints for experiment sandbox.
Prevents runaway processes from consuming host resources.
"""
import os
import sys
import resource
import signal
import time
from typing import Optional, Tuple

# ── Configuration ────────────────────────────────────────────────────────────
DEFAULT_CPU_LIMIT_SEC   = 300   # Max CPU seconds per experiment
DEFAULT_MEM_LIMIT_BYTES = 512 * 1024 * 1024  # 512 MB
DEFAULT_PROC_LIMIT      = 64    # Max child processes

# ── CPU Limit ─────────────────────────────────────────────────────────────────
def set_cpu_limit(seconds: int = DEFAULT_CPU_LIMIT_SEC) -> None:
    """Limit max CPU time (both user + sys) for the current process tree."""
    def _handler(signum, frame):
        raise SystemExit(f"[RESOURCE] CPU time limit ({seconds}s) exceeded")
    signal.signal(signal.SIGXCPU, _handler)
    # Soft limit → SIGXCPU; hard limit → SIGKILL
    resource.setrlimit(resource.RLIMIT_CPU, (seconds, seconds))

# ── Memory Limit ──────────────────────────────────────────────────────────────
def set_mem_limit(bytes_limit: int = DEFAULT_MEM_LIMIT_BYTES) -> None:
    """Cap addressable virtual memory (RSS will be smaller due to overcommit)."""
    # Set both AS (address space) and DATA segments
    for rl_type in (resource.RLIMIT_AS, resource.RLIMIT_DATA):
        resource.setrlimit(rl_type, (bytes_limit, bytes_limit))

# ── Process Count Limit ───────────────────────────────────────────────────────
def set_proc_limit(n: int = DEFAULT_PROC_LIMIT) -> None:
    """Restrict number of concurrent child processes."""
    resource.setrlimit(resource.RLIMIT_NPROC, (n, n))

# ── File Size Limit ───────────────────────────────────────────────────────────
def set_file_limit(bytes_limit: int = 50 * 1024 * 1024) -> None:
    """Prevent writing files larger than limit."""
    resource.setrlimit(resource.RLIMIT_FSIZE, (bytes_limit, bytes_limit))

# ── Wall Clock Timeout ────────────────────────────────────────────────────────
class WallClockGuard:
    """SIGKILL after N seconds elapsed (not CPU time)."""
    def __init__(self, seconds: int):
        self.seconds = seconds
        self._timer = None

    def start(self) -> None:
        def _fire():
            print(f"[RESOURCE] Wall clock limit ({self.seconds}s) exceeded — killing process", file=sys.stderr)
            os.kill(os.getpid(), signal.SIGKILL)
        import threading
        self._timer = threading.Timer(self.seconds, _fire)
        self._timer.daemon = True
        self._timer.start()

    def cancel(self) -> None:
        if self._timer:
            self._timer.cancel()

# ── Composite Apply ───────────────────────────────────────────────────────────
def apply_all(
    cpu_sec: int = DEFAULT_CPU_LIMIT_SEC,
    mem_bytes: int = DEFAULT_MEM_LIMIT_BYTES,
    proc_n: int = DEFAULT_PROC_LIMIT,
    wall_sec: Optional[int] = None,
) -> Optional[WallClockGuard]:
    """Apply all resource limits. Returns WallClockGuard if wall_sec set."""
    set_cpu_limit(cpu_sec)
    set_mem_limit(mem_bytes)
    set_proc_limit(proc_n)
    set_file_limit()
    guard = WallClockGuard(wall_sec) if wall_sec else None
    if guard:
        guard.start()
    return guard

# ── Query Current Usage ───────────────────────────────────────────────────────
def get_usage() -> Tuple[int, int, int]:
    """Return (ru_utime_ms, ru_stime_ms, max_rss_kb) for current process."""
    usage = resource.getrusage(resource.RUSAGE_SELF)
    return (
        int(usage.ru_utime * 1000),
        int(usage.ru_stime * 1000),
        usage.ru_maxrss,
    )

if __name__ == "__main__":
    print(f"PID={os.getpid()}, applying limits...")
    apply_all(wall_sec=10)
    print("Limits applied. Try: python3 -c 'x=1' (should work)")
    print(f"Usage so far: {get_usage()}")
