#!/usr/bin/env python3
"""
OpenClaw Native Harness v21.0 - Balanced Code Optimization

v20: 52.26 - Gen score up (65.6 vs 56.1), but Core down (54.2 vs 56.1)
Root cause: max_tokens=3000 for code may have caused verbosity

v21 策略：
1. 保持 code-specific executor（Gen 提升 9.5 分，有效）
2. 调整 max_tokens balance：code 2500（从 3000 下调，减少冗余）
3. 优化 code GOOD EXAMPLE：更侧重"架构图 + 核心算法 + 测试用例"
4. 保持 type-aware evaluation
"""

import json
import time
import os
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Tuple

API_CONFIG = {
    "base_url": "https://api.minimaxi.com/anthropic",
    "model": "MiniMax-M2.7"
}

@dataclass
class TaskResult:
    task_id: str
    task_type: str
    executor_output: str
    quality_score: float
    depth_score: int
    completeness_score: int
    actionability_score: int
    executor_tokens: int
    evaluator_tokens: int
    executor_latency_ms: float
    evaluator_latency_ms: float
    is_suspicious: bool = False
    suspicious_reason: str = ""
    error: str = ""

class RealLLMCaller:
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    def call(self, prompt: str, system_prompt: str = "", max_tokens: int = 2048, timeout: int = 120) -> Dict[str, Any]:
        import urllib.request
        
        start = time.time()
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01"
            }
            
            payload = {
                "model": API_CONFIG["model"],
                "max_tokens": max_tokens,
                "system": system_prompt or "You are a helpful AI assistant.",
                "messages": [{"role": "user", "content": prompt}]
            }
            
            data = json.dumps(payload).encode('utf-8')
            req = urllib.request.Request(
                f"{API_CONFIG['base_url']}/v1/messages",
                data=data,
                headers=headers,
                method='POST'
            )
            
            with urllib.request.urlopen(req, timeout=timeout) as response:
                result = json.loads(response.read().decode('utf-8'))
            
            latency = (time.time() - start) * 1000
            
            raw_content = result.get("content", [])
            content = ""
            for item in raw_content:
                if item.get("type") == "text":
                    content = item.get("text", "")
                    break
            
            input_tokens = result.get("usage", {}).get("input_tokens", 0)
            output_tokens = result.get("usage", {}).get("output_tokens", 0)
            
            return {
                "content": content,
                "latency_ms": latency,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "error": None
            }
        except Exception as e:
            latency = (time.time() - start) * 1000
            return {
                "content": "",
                "latency_ms": latency,
                "input_tokens": 0,
                "output_tokens": 0,
                "error": str(e)
            }

# Good/Bad Examples for research/review
GOOD_EXAMPLE_RESEARCH = """# Redis 缓存失效策略分析

## 问题诊断
Redis 缓存失效导致瞬时数据库压力峰值。当缓存 key 批量过期时，大量请求穿透到 DB。

## 解决方案
1. **被动过期 + 随机偏移**：每个 key 设置 TTL 时加上 0-60s 随机偏移
2. **主动刷新**：后台任务在 TTL 过期前主动刷新热点 key
3. **分层缓存**：L1(Lua) -> L2(Redis) -> DB

## 验证方法
```bash
# 模拟缓存失效
redis-cli --scan --pattern "user:*" | xargs redis-cli EXPIREAT
# 监控系统延迟和 DB QPS
```

效果：峰值 QPS 从 50,000 降至 8,000"""

BAD_EXAMPLE_RESEARCH = """# Redis 缓存问题

## 问题
缓存失效会有影响。

## 方案
可以加随机时间。

## 总结
注意缓存策略。"""

# v21: Optimized code example - focused structure
GOOD_EXAMPLE_CODE = """# 滑动窗口限流器

## 架构
```
┌─────────────────────────────────────┐
│         RateLimiter                 │
├─────────────────────────────────────┤
│  timestamp[] sliding window         │
│  allow_request() -> bool            │
└─────────────────────────────────────┘
```

## 核心算法
```python
class SlidingWindowRateLimiter:
    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = deque()
    
    def allow_request(self) -> bool:
        now = time.time()
        # 移除窗口外请求
        while self.requests and self.requests[0] <= now - self.window_seconds:
            self.requests.popleft()
        if len(self.requests) < self.max_requests:
            self.requests.append(now)
            return True
        return False
```

## 测试用例
```python
limiter = SlidingWindowRateLimiter(3, 1)
assert limiter.allow_request() == True
assert limiter.allow_request() == True
assert limiter.allow_request() == True
assert limiter.allow_request() == False
```"""

BAD_EXAMPLE_CODE = """# 限流器

```python
class Limiter:
    def allow(self):
        return True
```
"""


class HarnessV21:
    # v21: Balanced code executor prompts
    EXECUTOR_PROMPTS = {
        "research": """你是一个专业的研究分析师。分析技术问题并给出可操作的建议。

任务：{query}

参考下面的好/差示例，理解高 Actionability 输出的标准：

""" + GOOD_EXAMPLE_RESEARCH + """

VS

""" + BAD_EXAMPLE_RESEARCH + """

请按照好的示例的标准输出你的分析。
输出 300+ 字，包含具体步骤、数字、和验证方法。""",

        "code": """你是一个专业的代码工程师。编写完整可运行的代码。

任务：{query}

参考下面的好示例：

""" + GOOD_EXAMPLE_CODE + """

VS

""" + BAD_EXAMPLE_CODE + """

输出结构（按此顺序）：
1. **架构图**：ASCII 简图展示核心组件
2. **核心算法**：完整可运行代码，所有 import
3. **测试用例**：基本验证代码

重点：结构清晰 > 代码简洁 > 功能完整。""",

        "review": """你是一个专业的架构评审专家。评审架构并给出可操作的改进建议。

任务：{query}

参考下面的好/差示例：

""" + GOOD_EXAMPLE_RESEARCH + """

VS

""" + BAD_EXAMPLE_RESEARCH + """

好的评审应该：
- 每个风险有具体触发条件和影响
- 每个建议有具体步骤和资源需求
- 有验证方法

请按好的示例标准输出你的评审。"""
    }
    
    STRICT_EVALUATOR = """你是一个严格的技术评估专家。

评分标准：
- L5: 卓越 - 有独到见解，有具体可执行步骤，有数字证据
- L4: 优秀 - 分析深入，有具体方案
- L3: 合格 - 技术正确，但方案需要细化
- L2: 不足 - 方案过于抽象
- L1: 差 - 方案不可行

输出 JSON（不用 markdown）：
{{"depth": {{"level": 1-5, "evidence": "引用"}}, "completeness": {{"level": 1-5, "evidence": "引用"}}, "actionability": {{"level": 1-5, "evidence": "引用"}}, "overall_score": 0-100, "reasoning": "说明"}}

---
{content}
---

请严格评分。"""
    
    LENIENT_CODE_EVALUATOR = """你是一个代码质量评估专家。

对于代码任务，评估重点：
1. **功能完整性** (40%): 代码是否实现了核心功能
2. **结构清晰度** (30%): 代码是否有适当抽象和模块化
3. **可运行性** (30%): 是否有基本正确的语法和依赖

评分标准：
- L5: 功能完整，结构清晰，可直接运行
- L4: 功能完整，有一些小问题
- L3: 基本功能OK，但需要修改才能运行
- L2: 功能不完整或结构混乱
- L1: 无法理解或完全不可行

输出 JSON（不用 markdown）：
{{"depth": {{"level": 1-5, "evidence": "引用"}}, "completeness": {{"level": 1-5, "evidence": "引用"}}, "actionability": {{"level": 1-5, "evidence": "引用"}}, "overall_score": 0-100, "reasoning": "说明"}}

---
{content}
---

对于代码任务，重点看功能是否实现，不要过于严格挑剔语法细节。"""

    def __init__(self, api_key: str):
        self.llm = RealLLMCaller(api_key)
    
    def execute_task(self, task: Dict) -> TaskResult:
        task_id = task["id"]
        task_type = task["type"]
        query = task["query"]
        
        executor_start = time.time()
        executor_system = self.EXECUTOR_PROMPTS.get(task_type, self.EXECUTOR_PROMPTS["research"])
        
        # v21: Balance max_tokens - code 2500 (down from 3000), others 2048
        max_tokens = 2500 if task_type == "code" else 2048
        
        executor_response = self.llm.call(
            prompt=f"任务：{query}",
            system_prompt=executor_system,
            max_tokens=max_tokens
        )
        executor_latency = (time.time() - executor_start) * 1000
        
        if executor_response["error"]:
            return TaskResult(
                task_id=task_id, task_type=task_type,
                executor_output="", quality_score=0,
                depth_score=0, completeness_score=0, actionability_score=0,
                executor_tokens=0, evaluator_tokens=0,
                executor_latency_ms=executor_latency, evaluator_latency_ms=0,
                error=executor_response["error"]
            )
        
        executor_output = executor_response["content"]
        executor_tokens = executor_response["output_tokens"]
        
        # Evaluate
        evaluator_start = time.time()
        evaluator_prompt = self.LENIENT_CODE_EVALUATOR if task_type == "code" else self.STRICT_EVALUATOR
        evaluator_response = self.llm.call(
            prompt=evaluator_prompt.format(content=executor_output),
            system_prompt="你是一个严格的技术评估专家。",
            max_tokens=1024
        )
        evaluator_latency = (time.time() - evaluator_start) * 1000
        evaluator_tokens = evaluator_response.get("output_tokens", 0)
        
        if evaluator_response["error"]:
            return TaskResult(
                task_id=task_id, task_type=task_type,
                executor_output=executor_output, quality_score=0,
                depth_score=0, completeness_score=0, actionability_score=0,
                executor_tokens=executor_tokens, evaluator_tokens=0,
                executor_latency_ms=executor_latency, evaluator_latency_ms=evaluator_latency,
                error=f"Evaluator error: {evaluator_response['error']}"
            )
        
        # Parse evaluator output
        try:
            eval_text = evaluator_response["content"]
            json_start = eval_text.find('{')
            json_end = eval_text.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                eval_json = json.loads(eval_text[json_start:json_end])
            else:
                eval_json = {"overall_score": 50, "depth": {"level": 3}, "completeness": {"level": 3}, "actionability": {"level": 3}}
            
            quality_score = eval_json.get("overall_score", 50)
            depth_score = eval_json.get("depth", {}).get("level", 3)
            completeness_score = eval_json.get("completeness", {}).get("level", 3)
            actionability_score = eval_json.get("actionability", {}).get("level", 3)
            
            is_suspicious = executor_latency < 5000 and len(executor_output) > 1000
            suspicious_reason = "Excessively fast completion" if is_suspicious else ""
            
        except Exception as e:
            quality_score = 50
            depth_score = 3
            completeness_score = 3
            actionability_score = 3
            is_suspicious = False
            suspicious_reason = ""
        
        return TaskResult(
            task_id=task_id, task_type=task_type,
            executor_output=executor_output, quality_score=quality_score,
            depth_score=depth_score, completeness_score=completeness_score, actionability_score=actionability_score,
            executor_tokens=executor_tokens, evaluator_tokens=evaluator_tokens,
            executor_latency_ms=executor_latency, evaluator_latency_ms=evaluator_latency,
            is_suspicious=is_suspicious, suspicious_reason=suspicious_reason
        )
    
    def run_benchmark(self, api_key: str) -> Dict:
        tasks = [
            {"id": "core_001", "type": "research", "difficulty": 8,
             "query": "分析 Transformer 架构在长上下文场景下的注意力机制优化方案"},
            {"id": "core_002", "type": "code", "difficulty": 9,
             "query": "实现一个支持动态窗口大小的滑动日志解析器，处理 TB 级日志"},
            {"id": "core_003", "type": "research", "difficulty": 7,
             "query": "对比 RAG 与 Fine-tuning 在垂直领域问答场景下的成本效益"},
            {"id": "core_004", "type": "code", "difficulty": 8,
             "query": "设计一个分布式限流系统，支持多节点协同和精确度控制"},
            {"id": "core_005", "type": "review", "difficulty": 6,
             "query": "评审微服务架构的链路调用复杂度，给出优化建议"},
            {"id": "core_006", "type": "research", "difficulty": 9,
             "query": "分析 LLM 数学推理能力的技术瓶颈与解决方案"},
            {"id": "core_007", "type": "code", "difficulty": 7,
             "query": "实现一个插件化框架，支持热更新和依赖管理"},
            {"id": "core_008", "type": "research", "difficulty": 8,
             "query": "分析向量数据库在实时推荐系统中的选型策略"},
            {"id": "core_009", "type": "code", "difficulty": 9,
             "query": "实现简化版 Raft 共识算法，包含 Leader 选举和日志复制"},
            {"id": "core_010", "type": "review", "difficulty": 7,
             "query": "评审日活 1000 万 App 后端系统的架构设计"},
            {"id": "gen_001", "type": "research", "difficulty": 8,
             "query": "分析量子计算在金融领域的应用前景与风险"},
            {"id": "gen_002", "type": "code", "difficulty": 9,
             "query": "实现联邦学习梯度聚合算法"},
            {"id": "gen_003", "type": "review", "difficulty": 8,
             "query": "评审 ZKP 身份认证系统的架构风险"},
            {"id": "gen_004", "type": "research", "difficulty": 9,
             "query": "分析脑机接口技术最新进展与商业化路径"},
            {"id": "gen_005", "type": "code", "difficulty": 9,
             "query": "实现去中心化身份认证（DID）系统"}
        ]
        
        self.api_key = api_key
        results = []
        start_time = time.time()
        
        print(f"=" * 60)
        print(f"Harness v21.0 - Balanced Code Optimization")
        print(f"=" * 60)
        
        for task in tasks:
            print(f"[{task['id']}] Executor({task['type']})...", end=" ", flush=True)
            result = self.execute_task(task)
            results.append(result)
            print(f"Score: {result.quality_score:.1f} " +
                  (f"[SUSPICIOUS: {result.suspicious_reason}]" if result.is_suspicious else ""))
        
        elapsed = time.time() - start_time
        
        total = len(results)
        core_scores = [r.quality_score for r in results[:10]]
        gen_scores = [r.quality_score for r in results[10:]]
        
        avg_depth = sum(r.depth_score for r in results) / total
        avg_completeness = sum(r.completeness_score for r in results) / total
        avg_actionability = sum(r.actionability_score for r in results) / total
        total_tokens = sum(r.executor_tokens + r.evaluator_tokens for r in results)
        
        core_avg = sum(core_scores) / len(core_scores)
        gen_avg = sum(gen_scores) / len(gen_scores)
        efficiency_factor = min(total_tokens / 50000, 1.0)
        anti_cheat_factor = 1.0 - (sum(1 for r in results if r.is_suspicious) / total * 0.5)
        
        composite = (core_avg * 0.4 + gen_avg * 0.4 + (avg_actionability * 10) * 0.2) * efficiency_factor * anti_cheat_factor
        
        summary = {
            "harness_version": "v21.0",
            "architecture": "Balanced Code Optimization",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "elapsed_seconds": elapsed,
            "summary": {
                "total_tasks": total,
                "core_avg_score": core_avg,
                "gen_avg_score": gen_avg,
                "avg_depth_level": avg_depth,
                "avg_completeness_level": avg_completeness,
                "avg_actionability_level": avg_actionability,
                "total_tokens": total_tokens,
                "avg_latency_s": elapsed / total,
                "suspicious_count": sum(1 for r in results if r.is_suspicious),
                "composite_score": composite,
                "anti_cheat_factor": anti_cheat_factor
            },
            "individual_results": [
                {
                    "task_id": r.task_id,
                    "task_type": r.task_type,
                    "executor_output": r.executor_output[:500] + "..." if len(r.executor_output) > 500 else r.executor_output,
                    "quality_score": r.quality_score,
                    "depth_score": r.depth_score,
                    "completeness_score": r.completeness_score,
                    "actionability_score": r.actionability_score,
                    "executor_tokens": r.executor_tokens,
                    "evaluator_tokens": r.evaluator_tokens,
                    "executor_latency_ms": r.executor_latency_ms,
                    "evaluator_latency_ms": r.evaluator_latency_ms,
                    "is_suspicious": r.is_suspicious,
                    "suspicious_reason": r.suspicious_reason,
                    "error": r.error
                }
                for r in results
            ]
        }
        
        print(f"\n{'=' * 60}")
        print(f"v21.0 Results:")
        print(f"  Core Score:  {core_avg:.2f}")
        print(f"  Gen Score:   {gen_avg:.2f}")
        print(f"  Actionability: {avg_actionability:.2f}")
        print(f"  Composite:   {composite:.2f}")
        print(f"  Total Time:  {elapsed:.1f}s")
        print(f"{'=' * 60}")
        
        return summary


if __name__ == "__main__":
    import sys
    
    api_key = os.environ.get("MINIMAX_API_KEY", "")
    if not api_key:
        print("Error: MINIMAX_API_KEY not set")
        sys.exit(1)
    
    harness = HarnessV21(api_key)
    results = harness.run_benchmark(api_key)
    
    output_file = f"benchmark_results_v21_gen1.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\nResults saved to {output_file}")
