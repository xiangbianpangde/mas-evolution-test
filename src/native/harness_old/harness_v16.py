#!/usr/bin/env python3
"""
OpenClaw Native Harness v16.0 - Task-Specific Examples

v12 教训：1 good + 1 bad example 是最优的
v15 结果：48.4 (回归 v12 设计但分数更低)
v12_rerun：51.26 (确认 v12 稳定在 51-52)

v16 假设：v12 使用同一个 Redis example 对所有任务类型，
但 research/code/review 任务需要不同的示例。

v16 改进：
1. 为每种任务类型提供专用的 good example
2. research → 带引用和数据源的示例
3. code → 带测试和错误处理的示例
4. review → 带风险矩阵的示例
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
            
            tokens = result.get("usage", {}).get("output_tokens", 0)
            
            return {
                "success": True,
                "content": content,
                "tokens_used": tokens,
                "latency_ms": latency,
                "error": None
            }
            
        except Exception as e:
            latency = (time.time() - start) * 1000
            return {
                "success": False,
                "content": "",
                "tokens_used": 0,
                "latency_ms": latency,
                "error": str(e)
            }

class HarnessV16:
    """
    v16.0 - Task-Specific Examples
    
    v12: Same Redis example for all task types → 52.0
    v16: Task-specific examples (research/code/review)
    """
    
    # Good Example for RESEARCH tasks
    GOOD_EXAMPLE_RESEARCH = """
## 好的研究分析示例

问题：对比 PostgreSQL 和 MongoDB 的性能特点

输出：
1. **核心差异**：
   | 维度 | PostgreSQL | MongoDB |
   |------|------------|---------|
   | 数据模型 | 关系型 | 文档型 |
   | 事务 | ACID 完全支持 | 有限支持 |
   | join | 强大 | 受限 |

2. **量化数据**：
   - PostgreSQL: 100万行 JOIN 耗时 ~200ms
   - MongoDB: 100万文档写入 QPS ~50000
   - (数据来源: ClickHouse 官方 Benchmark 2024)

3. **建议**：
   - 强一致性需求 → PostgreSQL
   - 高写入 + 灵活 schema → MongoDB

关键：给出具体数字、对比表格、明确建议"""

    # Good Example for CODE tasks
    GOOD_EXAMPLE_CODE = """
## 好的代码示例

问题：实现一个 HTTP 请求库

输出：
```python
import requests
from typing import Optional, Dict

class HTTPClient:
    def __init__(self, base_url: str, timeout: int = 30):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
    
    def get(self, path: str, params: Optional[Dict] = None) -> Dict:
        url = f"{self.base_url}/{path.lstrip('/')}"
        resp = self.session.get(url, params=params, timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()
    
    def post(self, path: str, data: Dict) -> Dict:
        url = f"{self.base_url}/{path.lstrip('/')}"
        resp = self.session.post(url, json=data, timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()

# 使用示例
client = HTTPClient("https://api.example.com")
result = client.get("/users", params={"page": 1})
```

关键：完整可运行、有类型注解、有使用示例"""

    # Good Example for REVIEW tasks
    GOOD_EXAMPLE_REVIEW = """
## 好的架构评审示例

问题：评审微服务架构的订单系统

输出：
1. **风险矩阵**：
   | 风险 | 概率 | 影响 | 等级 |
   |------|------|------|------|
   | 库存服务挂 | 高 | 高 | 🔴严重 |
   | 支付超时 | 中 | 高 | 🟠高 |
   | 网络抖动 | 低 | 中 | 🟡中 |

2. **关键改进建议**：
   - 库存预留 + 30s 超时释放
     - 步骤：先锁库存，再支付，超时回滚
     - 资源：Redis 1GB + 熔断器
   - 支付幂等设计
     - 步骤：使用 idempotency_key
     - 资源：Redis 存储 key

3. **验证方法**：
   - 混沌测试：注入 10% 网络延迟
   - 预期：P99 < 2s，成功率 > 99.9%

关键：风险有等级、建议有步骤、改进有验证"""

    # Bad Example (通用)
    BAD_EXAMPLE = """
## 差的输出

问题：（任何问题）

输出：
1. 这个问题很复杂
2. 需要考虑很多因素
3. 建议做好测试
4. 注意性能优化

关键问题：缺少具体步骤、数字、代码、验证方法"""

    # v16 Executor prompts - Task-specific examples
    EXECUTOR_PROMPTS = {
        "research": """你是一个专业的研究分析师。分析技术问题并给出可操作的建议。

任务：{query}

参考下面的好/差示例：

""" + GOOD_EXAMPLE_RESEARCH + """

VS

""" + BAD_EXAMPLE + """

请按照好的示例的标准输出你的分析。
要求：
- 有具体数据（数字、百分比、QPS等）
- 有对比表格（如适用）
- 有明确建议和适用场景"""

        ,
        
        "code": """你是一个专业的代码工程师。编写可直接运行的代码。

任务：{query}

参考下面的好/差示例：

""" + GOOD_EXAMPLE_CODE + """

VS

""" + BAD_EXAMPLE + """

好的代码示例应该：
- 完整可运行的代码（所有 import）
- 有类型注解
- 有使用示例（输入/输出）
- 有错误处理

请按好的示例标准输出你的代码。""",

        "review": """你是一个专业的架构评审专家。评审架构并给出可操作的改进建议。

任务：{query}

参考下面的好/差示例：

""" + GOOD_EXAMPLE_REVIEW + """

VS

""" + BAD_EXAMPLE + """

好的评审应该：
- 有风险矩阵（概率/影响/等级）
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

    def __init__(self, api_key: str):
        self.llm = RealLLMCaller(api_key)
    
    def execute_task(self, task: Dict) -> TaskResult:
        task_id = task["id"]
        task_type = task["type"]
        query = task["query"]
        
        executor_start = time.time()
        executor_system = self.EXECUTOR_PROMPTS.get(task_type, self.EXECUTOR_PROMPTS["research"])
        executor_response = self.llm.call(
            prompt=f"任务：{query}",
            system_prompt=executor_system,
            max_tokens=2048
        )
        executor_latency = (time.time() - executor_start) * 1000
        
        if not executor_response["success"]:
            return TaskResult(
                task_id=task_id, task_type=task_type,
                executor_output="",
                quality_score=0, depth_score=0, completeness_score=0, actionability_score=0,
                executor_tokens=0, evaluator_tokens=0,
                executor_latency_ms=executor_latency, evaluator_latency_ms=0,
                error=executor_response["error"]
            )
        
        executor_output = executor_response["content"]
        executor_tokens = executor_response["tokens_used"]
        
        is_suspicious = False
        if executor_latency < 5000 and len(executor_output) > 1000:
            is_suspicious = True
        
        evaluator_start = time.time()
        evaluator_response = self.llm.call(
            prompt=self.STRICT_EVALUATOR.format(content=executor_output[:4000]),
            system_prompt="你是一个严格的技术评估专家。",
            max_tokens=1024
        )
        evaluator_latency = (time.time() - evaluator_start) * 1000
        
        quality_score = 50
        depth_score = 3
        completeness_score = 3
        actionability_score = 3
        
        if evaluator_response["success"]:
            try:
                content = evaluator_response["content"]
                if "{" in content and "}" in content:
                    json_str = content[content.index("{"):content.rindex("}")+1]
                    result = json.loads(json_str)
                    
                    depth_score = int(result.get("depth", {}).get("level", 3))
                    completeness_score = int(result.get("completeness", {}).get("level", 3))
                    actionability_score = int(result.get("actionability", {}).get("level", 3))
                    quality_score = float(result.get("overall_score", 50))
            except:
                pass
        
        return TaskResult(
            task_id=task_id, task_type=task_type,
            executor_output=executor_output[:500],
            quality_score=quality_score,
            depth_score=depth_score,
            completeness_score=completeness_score,
            actionability_score=actionability_score,
            executor_tokens=executor_tokens,
            evaluator_tokens=evaluator_response["tokens_used"] if evaluator_response["success"] else 0,
            executor_latency_ms=executor_latency,
            evaluator_latency_ms=evaluator_latency,
            is_suspicious=is_suspicious
        )

class BenchmarkTasks:
    CORE_TASKS = [
        {"id": "core_001", "type": "research", "difficulty": 8,
         "query": "分析 Transformer 架构在长上下文场景下的注意力机制优化方案"},
        {"id": "core_002", "type": "code", "difficulty": 9,
         "query": "实现一个支持动态窗口大小的滑动日志解析器，处理TB级日志"},
        {"id": "core_003", "type": "research", "difficulty": 7,
         "query": "对比 RAG 与 Fine-tuning 在垂直领域问答场景下的成本效益"},
        {"id": "core_004", "type": "code", "difficulty": 8,
         "query": "设计一个分布式限流系统，支持多节点协同和精确度控制"},
        {"id": "core_005", "type": "review", "difficulty": 6,
         "query": "审查微服务架构的潜在风险点：订单服务->支付服务->库存服务->物流服务"},
        {"id": "core_006", "type": "research", "difficulty": 9,
         "query": "调研当前 LLM 在数学推理方面的最新进展和瓶颈"},
        {"id": "core_007", "type": "code", "difficulty": 7,
         "query": "实现一个支持热更新的插件化框架，参考 Ansible/Logstash 设计"},
        {"id": "core_008", "type": "research", "difficulty": 8,
         "query": "分析向量数据库在实时推荐系统中的选型策略"},
        {"id": "core_009", "type": "code", "difficulty": 9,
         "query": "用 Python 实现一个简化版 Raft 共识算法，包括 Leader 选举和日志复制"},
        {"id": "core_010", "type": "review", "difficulty": 7,
         "query": "对一个日活 1000 万的 App 后端系统进行架构评估和优化建议"},
    ]
    
    GENERALIZATION_TASKS = [
        {"id": "gen_001", "type": "research", "difficulty": 8,
         "query": "分析量子计算在金融领域的应用前景与风险"},
        {"id": "gen_002", "type": "code", "difficulty": 9,
         "query": "实现一个联邦学习框架的梯度聚合模块，支持多方数据协作"},
        {"id": "gen_003", "type": "review", "difficulty": 8,
         "query": "评估零知识证明（ZKP）在身份认证系统中的应用风险"},
        {"id": "gen_004", "type": "research", "difficulty": 9,
         "query": "调研脑机接口（BCI）技术的最新进展与商业化挑战"},
        {"id": "gen_005", "type": "code", "difficulty": 9,
         "query": "设计一个去中心化身份认证（DID）系统，支持跨平台互认"},
    ]

def run_benchmark() -> Tuple[List[TaskResult], Dict]:
    api_key = os.environ.get("MINIMAX_API_KEY", "")
    if not api_key:
        api_key = "sk-cp-ZNEhSAB4-p-nraTwKzWoeLCpFPE-wY8If5v_1qxUvnW4_h0ryAunuH9_Vn-SItYx-D1AGFdRhD_6fn_9LhkpWG2yy6kUeRZBEjq8aFCUpruT5aFlM-Y5KDc"
    
    harness = HarnessV16(api_key)
    tasks = BenchmarkTasks()
    
    all_tasks = []
    for t in tasks.CORE_TASKS:
        t["is_generalization"] = False
        all_tasks.append(t)
    for t in tasks.GENERALIZATION_TASKS:
        t["is_generalization"] = True
        all_tasks.append(t)
    
    results = []
    
    for task in all_tasks:
        print(f"[{task['id']}] Executor({task['type']})...", end=" ", flush=True)
        result = harness.execute_task(task)
        results.append(result)
        
        sus = " [SUSPICIOUS]" if result.is_suspicious else ""
        print(f"质量:{result.quality_score:.0f}(深:L{result.depth_score}完:L{result.completeness_score}行:L{result.actionability_score}) "
              f"延迟:{result.executor_latency_ms/1000:.1f}s{sus}")
    
    summary = compute_summary(results)
    return results, summary

def compute_summary(results: List[TaskResult]) -> Dict:
    core = [r for r in results if not getattr(r, 'is_generalization', False)]
    gen = [r for r in results if getattr(r, 'is_generalization', True)]
    
    core_avg = sum(r.quality_score for r in core) / len(core) if core else 0
    gen_avg = sum(r.quality_score for r in gen) / len(gen) if gen else 0
    
    avg_depth = sum(r.depth_score for r in results) / len(results) if results else 0
    avg_complete = sum(r.completeness_score for r in results) / len(results) if results else 0
    avg_action = sum(r.actionability_score for r in results) / len(results) if results else 0
    
    total_tokens = sum(r.executor_tokens + r.evaluator_tokens for r in results)
    avg_latency = sum(r.executor_latency_ms for r in results) / len(results) / 1000 if results else 0
    
    suspicious = sum(1 for r in results if r.is_suspicious)
    anti_cheat = (1 - suspicious / len(results)) if results else 0
    
    composite = 0.6 * core_avg * anti_cheat + 0.3 * gen_avg + 0.1 * min(100, 1000 / (avg_latency + 1))
    
    return {
        "total_tasks": len(results),
        "core_avg_score": core_avg,
        "gen_avg_score": gen_avg,
        "avg_depth_level": avg_depth,
        "avg_completeness_level": avg_complete,
        "avg_actionability_level": avg_action,
        "total_tokens": total_tokens,
        "avg_latency_s": avg_latency,
        "suspicious_count": suspicious,
        "composite_score": composite,
        "anti_cheat_factor": anti_cheat
    }

def main():
    from datetime import datetime
    
    print("=" * 60)
    print("OpenClaw Harness v16.0 - Task-Specific Examples")
    print("核心：每种任务类型使用专用的 good example")
    print("=" * 60)
    
    start = time.time()
    results, summary = run_benchmark()
    elapsed = time.time() - start
    
    print("\n" + "=" * 60)
    print("Benchmark 结果汇总")
    print("=" * 60)
    print(f"\n[核心任务] 平均质量分: {summary['core_avg_score']:.1f}")
    print(f"  - 平均深度等级: L{summary['avg_depth_level']:.1f}")
    print(f"  - 平均完整性等级: L{summary['avg_completeness_level']:.1f}")
    print(f"  - 平均可操作性等级: L{summary['avg_actionability_level']:.1f}")
    print(f"\n[泛化任务] 平均质量分: {summary['gen_avg_score']:.1f}")
    print(f"[Token消耗] 总计: {summary['total_tokens']}")
    print(f"[平均延迟] {summary['avg_latency_s']:.1f}秒/任务")
    print(f"[可疑检测] {summary['suspicious_count']} 个任务标记为可疑")
    print(f"\n[综合评分] {summary['composite_score']:.2f}/100")
    print(f"[抗欺骗系数] {summary['anti_cheat_factor']:.2f}")
    print(f"[总耗时] {elapsed:.0f}秒")
    
    output = {
        "harness_version": "v16.0",
        "architecture": "Task-Specific Examples",
        "timestamp": datetime.now().isoformat(),
        "elapsed_seconds": elapsed,
        "summary": summary,
        "individual_results": [asdict(r) for r in results]
    }
    
    output_file = "/root/.openclaw/workspace/mas_repo/openclaw_native/benchmark_results_v16_gen1.json"
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\n[保存] 结果已保存至: {output_file}")
    return summary

if __name__ == "__main__":
    main()