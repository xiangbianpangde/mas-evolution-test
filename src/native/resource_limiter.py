#!/usr/bin/env python3
"""
Resource Limiter - 资源限制模块

在所有 harness 启动前调用 apply_all() 来限制资源使用
"""

import resource
import signal
import sys
import os

# 默认限制
DEFAULT_CPU_TIME = 300  # 5分钟 CPU 时间
DEFAULT_MEM_LIMIT = 512 * 1024 * 1024  # 512MB
DEFAULT_FILE_LIMIT = 50 * 1024 * 1024  # 50MB

class WallClockGuard:
    """墙上时钟超时保护"""
    def __init__(self, timeout_seconds):
        self.timeout = timeout_seconds
        self.start_time = None
    
    def start(self):
        self.start_time = os.times().elapsed
    
    def check(self):
        if self.start_time is None:
            return True
        elapsed = os.times().elapsed - self.start_time
        if elapsed > self.timeout:
            print(f"Wall clock timeout: {elapsed:.1f}s > {self.timeout}s")
            return False
        return True
    
    def remaining(self):
        if self.start_time is None:
            return self.timeout
        return max(0, self.timeout - (os.times().elapsed - self.start_time))

_guard = None

def timeout_handler(signum, frame):
    """超时信号处理"""
    print(f"Process timed out after {DEFAULT_CPU_TIME}s")
    sys.exit(1)

def set_cpu_limit(seconds=DEFAULT_CPU_TIME):
    """设置 CPU 时间限制"""
    try:
        resource.setrlimit(resource.RLIMIT_CPU, (seconds, seconds))
        print(f"CPU limit set: {seconds}s")
    except Exception as e:
        print(f"Failed to set CPU limit: {e}")

def set_mem_limit(bytes_limit=DEFAULT_MEM_LIMIT):
    """设置内存限制"""
    try:
        resource.setrlimit(resource.RLIMIT_AS, (bytes_limit, bytes_limit))
        print(f"Memory limit set: {bytes_limit // (1024*1024)}MB")
    except Exception as e:
        print(f"Failed to set memory limit: {e}")

def set_proc_limit(max_procs=64):
    """设置子进程数限制"""
    try:
        resource.setrlimit(resource.RLIMIT_NPROC, (max_procs, max_procs))
        print(f"Process limit set: {max_procs}")
    except Exception as e:
        print(f"Failed to set process limit: {e}")

def set_file_limit(bytes_limit=DEFAULT_FILE_LIMIT):
    """设置文件写入限制"""
    try:
        resource.setrlimit(resource.RLIMIT_FSIZE, (bytes_limit, bytes_limit))
        print(f"File size limit set: {bytes_limit // (1024*1024)}MB")
    except Exception as e:
        print(f"Failed to set file limit: {e}")

def apply_all():
    """应用所有资源限制"""
    set_cpu_limit()
    set_mem_limit()
    set_proc_limit()
    set_file_limit()
    
    # 设置 SIGALRM 用于超时检测
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(DEFAULT_CPU_TIME)
    
    print("All resource limits applied")

def get_usage():
    """获取当前资源使用"""
    usage = resource.getrusage(resource.RUSAGE_SELF)
    return {
        "utime": usage.ru_utime,
        "stime": usage.ru_stime,
        "maxrss": usage.ru_maxrss,
        "nvcsw": usage.ru_nvcsw,
        "nivcsw": usage.ru_nivcsw
    }

if __name__ == "__main__":
    print("Testing resource limiter...")
    apply_all()
    print(f"Current usage: {get_usage()}")
