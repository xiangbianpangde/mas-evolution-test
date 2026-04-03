#!/usr/bin/env python3
"""
OpenClaw Harness v7.0 - 改进的多维度评分

改进：
1. Evaluator 引入多维度评分（技术深度、完整性、可执行性）
2. 每个维度独立打分，最终加权平均
3. 去除 task_type hint，避免评分偏见
4. 优化 prompt，减少 LLM 评分随机性
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
    # 多维度评分
    technical_depth: float      # 技术深度 0-100
    completeness: float        # 完整性 0-100
    actionability: float       # 可执行性 0-100
    overall_score: float       # 综合评分
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

class HarnessV7:
    """
    v7.0 改进的多维度评分 Harness
    """
    
    EXECUTOR_PROMPTS = {
        "research": """你是一个专业的研究分析师。根据用户的查询，进行深度技术分析。

要求：
1. 提供深入的技术原理分析
2. 包含具体的代码示例或数据
3. 提供对比或性能分析
4. 输出结构化内容，长度 200+ 字

只输出分析内容，不要声明你的输出格式。""",
        
        "code": """你是一个专业的代码工程师。根据用户需求，生成高质量的代码解决方案。

要求：
1. 提供完整可运行的代码
2. 包含测试用例
3. 包含架构设计说明
4. 代码必须有复杂度分析

只输出代码和说明，不要声明你的输出格式。""",
        
        "review": """你是一个专业的架构评审专家。分析系统/架构的风险并提出改进建议。

要求：
1. 识别主要风险点（至少3个）
2. 提出具体的缓解方案
3. 给出优先级排序
4. 每个风险标注等级（Critical/High/Medium/Low）

只输出评审内容，不要声明你的输出格式。"""
    }
    
    # 改进的多维度 Evaluator prompt
    EVALUATOR_PROMPT = """你是一个严格的质量评估专家。请对以下内容进行多维度评分。

评分维度（每个 0-100）：

1. **技术深度** (technical_depth): 
   - 技术原理是否深入准确
   - 是否有理论支撑或引用
   - 复杂度是否合理

2. **完整性** (completeness):
   - 是否覆盖任务的主要方面
   - 是否有遗漏的关键点
   - 结构是否完整

3. **可执行性** (actionability):
   - 方案/代码是否可直接实施
   - 建议是否具体可操作
   - 是否有明确步骤

最终评分 = (技术深度 + 完整性 + 可执行性) / 3

输出严格 JSON 格式：
{"technical_depth": 0-100, "completeness": 0-100, "actionability": 0-100, "reasoning": "简要说明(50字内)"}"""

    def __init__(self, api_key: str):
        self.llm = RealLLMCaller(api_key)
    
    def execute_task(self, task: Dict) -> TaskResult:
        task_id = task["id"]
        task_type = task["type"]
        query = task["query"]
        
        is_suspicious = False
        suspicious_reason = ""
        
        # Stage 1: Executor
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
                executor_output="", technical_depth=0, completeness=0, actionability=0,
                overall_score=0, executor_tokens=0, evaluator_tokens=0,
                executor_latency_ms=executor_latency, evaluator_latency_ms=0,
                error=executor_response["error"]
            )
        
        executor_output = executor_response["content"]
        executor_tokens = executor_response["tokens_used"]
        
        # Anti-cheat check
        if executor_latency < 5000 and len(executor_output) > 1000:
            is_suspicious = True
            suspicious_reason = f"异常短延迟({executor_latency:.0f}ms)+长输出"
        
        # Stage 2: Multi-dimensional Evaluator
        evaluator_start = time.time()
        
        evaluator_response = self.llm.call(
            prompt=f"请评估以下内容的质量：\n\n{executor_output[:4000]}",
            system_prompt=self.EVALUATOR_PROMPT,
            max_tokens=512
        )
        
        evaluator_latency = (time.time() - evaluator_start) * 1000
        
        technical_depth = 50
        completeness = 50
        actionability = 50
        overall_score = 50
        
        if evaluator_response["success"]:
            evaluator_output = evaluator_response["content"]
            evaluator_tokens = evaluator_response["tokens_used"]
            
            try:
                if "{" in evaluator_output and "}" in evaluator_output:
                    json_str = evaluator_output[evaluator_output.index("{"):evaluator_output.rindex("}")+1]
                    result = json.loads(json_str)
                    technical_depth = float(result.get("technical_depth", 50))
                    completeness = float(result.get("completeness", 50))
                    actionability = float(result.get("actionability", 50))
                    overall_score = (technical_depth + completeness + actionability) / 3
            except:
                pass
        else:
            evaluator_tokens = 0
        
        return TaskResult(
            task_id=task_id,
            task_type=task_type,
            executor_output=executor_output[:500],
            technical_depth=technical_depth,
            completeness=completeness,
            actionability=actionability,
            overall_score=overall_score,
            executor_tokens=executor_tokens,
            evaluator_tokens=evaluator_tokens,
            executor_latency_ms=executor_latency,
            evaluator_latency_ms=evaluator_latency,
            is_suspicious=is_suspicious,
            suspicious_reason=suspicious_reason
        )

class BenchmarkTasks:
    CORE_TASKS = [
        {"id": "core_001", "type": "research",
         "query": "分析 Transformer 架构在长上下文场景下的注意力机制优化方案"},
        {"id": "core_002", "type": "code",
         "query": "实现一个支持动态窗口大小的滑动日志解析器，处理TB级日志"},
        {"id": "core_003", "type": "research",
         "query": "对比 RAG 与 Fine-tuning 在垂直领域问答场景下的成本效益"},
        {"id": "core_004", "type": "code",
         "query": "设计一个分布式限流系统，支持多节点协同和精确度控制"},
        {"id": "core_005", "type": "review",
         "query": "审查微服务架构的潜在风险点：订单服务->支付服务->库存服务->物流服务"},
        {"id": "core_006", "type": "research",
         "query": "调研当前 LLM 在数学推理方面的最新进展和瓶颈"},
        {"id": "core_007", "type": "code",
         "query": "实现一个支持热更新的插件化框架，参考 Ansible/Logstash 设计"},
        {"id": "core_008", "type": "research",
         "query": "分析向量数据库在实时推荐系统中的选型策略"},
        {"id": "core_009", "type": "code",
         "query": "用 Python 实现一个简化版 Raft 共识算法，包括 Leader 选举和日志复制"},
        {"id": "core_010", "type": "review",
         "query": "对一个日活 1000 万的 App 后端系统进行架构评估和优化建议"},
    ]
    
    GENERALIZATION_TASKS = [
        {"id": "gen_001", "type": "research",
         "query": "分析量子计算在金融领域的应用前景与风险"},
        {"id": "gen_002", "type": "code",
         "query": "实现一个联邦学习框架的梯度聚合模块，支持多方数据协作"},
        {"id": "gen_003", "type": "review",
         "query": "评估零知识证明（ZKP）在身份认证系统中的应用风险"},
        {"id": "gen_004", "type": "research",
         "query": "调研脑机接口（BCI）技术的最新进展与商业化挑战"},
        {"id": "gen_005", "type": "code",
         "query": "设计一个去中心化身份认证（DID）系统，支持跨平台互认"},
    ]

def run_benchmark() -> Tuple[List[TaskResult], Dict]:
    api_key = os.environ.get("MINIMAX_API_KEY", "sk-cp-ZNEhSAB4-p-nraTwKzWoeLCpFPE-wY8If5v_1qxUvnW4_h0ryAunuH9_Vn-SItYx-D1AGFdRhD_6fn_9LhkpWG2yy6kUeRZBEjq8aFCUpruT5aFlM-Y5KDc")
    
    harness = HarnessV7(api_key)
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
        print(f"[{task['id']}] {task['type']}...", end=" ", flush=True)
        result = harness.execute_task(task)
        results.append(result)
        
        sus = " [SUSPICIOUS]" if result.is_suspicious else ""
        print(f"技术:{result.technical_depth:.0f} 完整:{result.completeness:.0f} 可执行:{result.actionability:.0f} "
              f"综合:{result.overall_score:.0f}{sus}")
    
    summary = compute_summary(results)
    return results, summary

def compute_summary(results: List[TaskResult]) -> Dict:
    core = [r for r in results if not getattr(r, 'is_generalization', False)]
    gen = [r for r in results if getattr(r, 'is_generalization', True)]
    
    def avg(lst): return sum(lst) / len(lst) if lst else 0
    
    core_scores = [r.overall_score for r in core]
    gen_scores = [r.overall_score for r in gen]
    
    suspicious_count = sum(1 for r in results if r.is_suspicious)
    
    # 字典序评估
    anti_cheat_factor = (1 - suspicious_count / len(results)) if results else 1
    accuracy = avg(core_scores) * anti_cheat_factor
    generalization = avg(gen_scores)
    efficiency = 1000 / (avg([r.executor_latency_ms for r in results]) + 1)
    
    composite = 0.6 * accuracy + 0.3 * generalization + 0.1 * min(100, efficiency)
    
    return {
        "total_tasks": len(results),
        "core_avg_score": avg(core_scores),
        "gen_avg_score": avg(gen_scores),
        "core_technical_depth": avg([r.technical_depth for r in core]),
        "core_completeness": avg([r.completeness for r in core]),
        "core_actionability": avg([r.actionability for r in core]),
        "total_executor_tokens": sum(r.executor_tokens for r in results),
        "total_evaluator_tokens": sum(r.evaluator_tokens for r in results),
        "avg_latency_ms": avg([r.executor_latency_ms for r in results]),
        "suspicious_count": suspicious_count,
        "composite_score": composite,
        "anti_cheat_factor": anti_cheat_factor
    }

def main():
    from datetime import datetime
    
    print("=" * 60)
    print("OpenClaw Harness v7.0 - Multi-Dimensional Scoring")
    print("=" * 60)
    
    start = time.time()
    results, summary = run_benchmark()
    elapsed = time.time() - start
    
    print("\n" + "=" * 60)
    print("Benchmark Results")
    print("=" * 60)
    print(f"\n[Core Tasks]")
    print(f"  Technical Depth: {summary['core_technical_depth']:.1f}")
    print(f"  Completeness: {summary['core_completeness']:.1f}")
    print(f"  Actionability: {summary['core_actionability']:.1f}")
    print(f"  Overall: {summary['core_avg_score']:.1f}")
    print(f"\n[Generalization]")
    print(f"  Overall: {summary['gen_avg_score']:.1f}")
    print(f"\n[Tokens] Executor: {summary['total_executor_tokens']} | Evaluator: {summary['total_evaluator_tokens']}")
    print(f"[Latency] {summary['avg_latency_ms']/1000:.1f}s/task")
    print(f"[Suspicious] {summary['suspicious_count']}")
    print(f"\n[Composite Score] {summary['composite_score']:.2f}")
    
    output = {
        "harness_version": "v7.0",
        "architecture": "Multi-Dimensional Scoring",
        "timestamp": datetime.now().isoformat(),
        "elapsed_seconds": elapsed,
        "summary": summary,
        "individual_results": [asdict(r) for r in results]
    }
    
    output_file = "/root/.openclaw/workspace/mas_repo/openclaw_native/benchmark_results_v7_gen1.json"
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\n[Saved] {output_file}")
    return summary

if __name__ == "__main__":
    main()
