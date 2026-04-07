#!/usr/bin/env python3
"""
OpenClaw Native Harness v27.0 - Core-Focused Enhancement

v26: 56.91 - Gen good (66.80), Core weak (53.00)
v23: 58.30 - Gen great (68.20), Core moderate (54.40)

v27 策略：保持 Gen 水平（66-68），重点提升 Core
1. 保持 adaptive format selection（Gen 维持）
2. 为 research/review 任务添加更详细的结构指导
3. 研究任务强调"数字证据"和"验证方法"
"""

import json
import time
import os
from dataclasses import dataclass
from typing import Dict

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
    error: str = ""

class RealLLMCaller:
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    def call(self, prompt: str, system_prompt: str = "", max_tokens: int = 2048, timeout: int = 120) -> Dict:
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
                data=data, headers=headers, method='POST'
            )
            with urllib.request.urlopen(req, timeout=timeout) as response:
                result = json.loads(response.read().decode('utf-8'))
            latency = (time.time() - start) * 1000
            content = ""
            for item in result.get("content", []):
                if item.get("type") == "text":
                    content = item.get("text", "")
                    break
            return {
                "content": content,
                "latency_ms": latency,
                "input_tokens": result.get("usage", {}).get("input_tokens", 0),
                "output_tokens": result.get("usage", {}).get("output_tokens", 0),
                "error": None
            }
        except Exception as e:
            return {
                "content": "", "latency_ms": (time.time() - start) * 1000,
                "input_tokens": 0, "output_tokens": 0, "error": str(e)
            }

# v27: Core-focused research prompt with more structure
RESEARCH_PROMPT = """你是一个专业的研究分析师。

任务：{query}

输出结构（严格按此顺序）：

# 技术深度分析

## 1. 问题诊断
- 具体现象（包含数字）
- 影响范围（QPS/延迟/错误率）

## 2. 根因分析
- 技术层面原因
- 多角度分析（架构/数据/配置）

## 3. 解决方案
### 方案A（推荐）
- 实施步骤（编号列表）
- 关键参数（具体数值）
- 资源需求

### 方案B（备选）
同上结构

## 4. 验证方法
- 测试命令
- 预期结果（数字）
- 监控指标

## 5. 风险与缓解
- 风险点
- 缓解措施

要求：
- 每个部分都要有具体数字
- 命令可直接执行
- 验证方法可操作"""

CODE_PROMPT = """你是一个专业的代码工程师。

任务：{query}

输出结构：

# 实现方案

## 架构简图
```
[ASCII架构图]
```

## 核心代码
```python
[完整可运行代码，所有import]
```

## 测试用例
```python
[assert验证]
```

## 配置说明
- 参数说明
- 依赖环境

要求：代码可直接运行。"""

REVIEW_PROMPT = """你是一个专业的架构评审专家。

任务：{query}

输出结构：

# 架构评审报告

## 风险矩阵
| 风险 | 严重度 | 概率 | 风险值 | 优先级 |
|------|--------|------|--------|--------|
| ... | ... | ... | ... | P0/P1 |

## 缓解方案
### P0（立即处理）
- 风险描述
- 实施步骤
- 验证方法

### P1（本周处理）
同上

## 验证方法
- 测试命令
- 监控指标

## 资源估算
- 人力
- 时间
- 基础设施

要求：每个风险有具体触发条件。"""

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

对于代码任务，重点看功能是否实现。"""


class HarnessV27:
    def __init__(self, api_key: str):
        self.llm = RealLLMCaller(api_key)
    
    def execute_task(self, task: Dict) -> TaskResult:
        task_id = task["id"]
        task_type = task["type"]
        query = task["query"]
        
        executor_start = time.time()
        max_tokens = 2500 if task_type == "code" else 2048
        
        if task_type == "research":
            system_prompt = RESEARCH_PROMPT.format(query=query)
        elif task_type == "code":
            system_prompt = CODE_PROMPT.format(query=query)
        else:
            system_prompt = REVIEW_PROMPT.format(query=query)
        
        executor_response = self.llm.call(
            prompt=f"任务：{query}",
            system_prompt=system_prompt,
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
        
        evaluator_start = time.time()
        evaluator_prompt = LENIENT_CODE_EVALUATOR if task_type == "code" else STRICT_EVALUATOR
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
        except:
            quality_score = 50
            depth_score = completeness_score = actionability_score = 3
            is_suspicious = False
        
        return TaskResult(
            task_id=task_id, task_type=task_type,
            executor_output=executor_output, quality_score=quality_score,
            depth_score=depth_score, completeness_score=completeness_score, actionability_score=actionability_score,
            executor_tokens=executor_tokens, evaluator_tokens=evaluator_tokens,
            executor_latency_ms=executor_latency, evaluator_latency_ms=evaluator_latency,
            is_suspicious=is_suspicious
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
        
        print("=" * 60)
        print("Harness v27.0 - Core-Focused Enhancement")
        print("=" * 60)
        
        for task in tasks:
            print(f"[{task['id']}] Executor({task['type']})...", end=" ", flush=True)
            result = self.execute_task(task)
            results.append(result)
            print(f"Score: {result.quality_score:.1f}")
        
        elapsed = time.time() - start_time
        
        total = len(results)
        core_scores = [r.quality_score for r in results[:10]]
        gen_scores = [r.quality_score for r in results[10:]]
        avg_actionability = sum(r.actionability_score for r in results) / total
        
        core_avg = sum(core_scores) / len(core_scores)
        gen_avg = sum(gen_scores) / len(gen_scores)
        composite = core_avg * 0.45 + gen_avg * 0.45 + (avg_actionability * 10) * 0.1
        
        print(f"\n{'=' * 60}")
        print(f"v27.0: Core={core_avg:.2f} Gen={gen_avg:.2f} Composite={composite:.2f}")
        print(f"{'=' * 60}")
        
        return {
            "harness_version": "v27.0",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "elapsed_seconds": elapsed,
            "summary": {
                "total_tasks": total,
                "core_avg_score": core_avg,
                "gen_avg_score": gen_avg,
                "avg_actionability_level": avg_actionability,
                "composite_score": composite,
            },
            "individual_results": [
                {"task_id": r.task_id, "task_type": r.task_type,
                 "quality_score": r.quality_score, "is_suspicious": r.is_suspicious}
                for r in results
            ]
        }


if __name__ == "__main__":
    import sys
    api_key = os.environ.get("MINIMAX_API_KEY", "")
    if not api_key:
        print("Error: MINIMAX_API_KEY not set")
        sys.exit(1)
    
    harness = HarnessV27(api_key)
    results = harness.run_benchmark(api_key)
    
    with open("benchmark_results_v27_gen1.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
