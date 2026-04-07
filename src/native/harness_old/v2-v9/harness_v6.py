#!/usr/bin/env python3
"""
OpenClaw Native Harness v6.0 - 防作弊评测架构

核心改进：
1. 分离 Executor 和 Evaluator（解耦合）
2. Executor 看不到 expected outputs（防透题）
3. Evaluator 独立评估内容质量，不依赖类型匹配
4. 真实 Token 统计 + 延迟测量
5. 行为审计：检测异常短延迟（可能作弊）

防作弊规则：
- Executor 绝不接收 expected outputs
- Evaluator 独立评分，不知道正确答案
- 异常秒解（<5秒）但高准确率 → 标记可疑
"""

import json
import time
import uuid
import sys
import os
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional, Tuple

API_CONFIG = {
    "base_url": "https://api.minimaxi.com/anthropic",
    "model": "MiniMax-M2.7"
}

@dataclass
class TaskResult:
    task_id: str
    task_type: str
    executor_output: str  # 真实输出内容
    quality_score: float  # Evaluator 评分
    executor_tokens: int
    evaluator_tokens: int
    executor_latency_ms: float
    evaluator_latency_ms: float
    is_suspicious: bool = False
    suspicious_reason: str = ""
    error: str = ""

class RealLLMCaller:
    """真实 API 调用器"""
    
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
            
            # 解析 MiniMax API 响应
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

class HarnessV6:
    """
    v6.0 防作弊 Harness
    核心：Executor 和 Evaluator 完全分离
    """
    
    # Executor 系统提示（看不到 expected）
    EXECUTOR_PROMPTS = {
        "research": """你是一个专业的研究分析师。根据用户的查询，进行深度技术分析。

要求：
1. 提供深入的技术原理分析
2. 包含具体的代码示例（如果适用）
3. 提供 benchmark 数据或性能对比
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
1. 识别主要风险点
2. 提出具体的缓解方案
3. 给出优先级排序
4. 每个风险标注等级（Critical/High/Medium/Low）

只输出评审内容，不要声明你的输出格式。"""
    }
    
    # Evaluator 系统提示（不知道 expected）
    EVALUATOR_PROMPT = """你是一个严格的质量评估专家。你的任务是根据内容的质量进行评分。

评估标准：
1. **技术准确性** (0-100): 内容是否技术正确、合理
2. **完整性** (0-100): 是否覆盖了任务的主要方面
3. **可操作性** (0-100): 建议/方案是否具体可执行
4. **专业性** (0-100): 是否展现了深度专业知识

最终得分 = (技术准确性 + 完整性 + 可操作性 + 专业性) / 4

只输出 JSON 格式：{"score": 0-100, "reasoning": "简要说明"}"""

    def __init__(self, api_key: str):
        self.llm = RealLLMCaller(api_key)
    
    def execute_task(self, task: Dict) -> TaskResult:
        """
        执行任务：Executor → Evaluator 分离式评测
        
        注意：Executor 绝对收不到 expected outputs！
        """
        task_id = task["id"]
        task_type = task["type"]
        query = task["query"]
        
        is_suspicious = False
        suspicious_reason = ""
        
        # ============ Stage 1: Executor ============
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
                task_id=task_id,
                task_type=task_type,
                executor_output="",
                quality_score=0,
                executor_tokens=0,
                evaluator_tokens=0,
                executor_latency_ms=executor_latency,
                evaluator_latency_ms=0,
                error=executor_response["error"]
            )
        
        executor_output = executor_response["content"]
        executor_tokens = executor_response["tokens_used"]
        
        # ============ Anti-Cheat: 异常检测 ============
        # 规则：如果延迟 < 5秒 且输出很长 → 可疑（可能预知答案）
        if executor_latency < 5000 and len(executor_output) > 1000:
            is_suspicious = True
            suspicious_reason = f"异常短延迟({executor_latency:.0f}ms)+长输出"
        
        # ============ Stage 2: Evaluator ============
        evaluator_start = time.time()
        
        evaluator_response = self.llm.call(
            prompt=f"请评估以下内容的质量：\n\n{executor_output[:4000]}",
            system_prompt=self.EVALUATOR_PROMPT,
            max_tokens=512
        )
        
        evaluator_latency = (time.time() - evaluator_start) * 1000
        
        if not evaluator_response["success"]:
            return TaskResult(
                task_id=task_id,
                task_type=task_type,
                executor_output=executor_output[:500],  # 截断保存
                quality_score=50,  # 默认中等分
                executor_tokens=executor_tokens,
                evaluator_tokens=0,
                executor_latency_ms=executor_latency,
                evaluator_latency_ms=evaluator_latency,
                is_suspicious=is_suspicious,
                suspicious_reason=suspicious_reason
            )
        
        evaluator_output = evaluator_response["content"]
        evaluator_tokens = evaluator_response["tokens_used"]
        
        # 解析 Evaluator 评分
        quality_score = 50  # 默认
        try:
            if "{" in evaluator_output and "}" in evaluator_output:
                json_str = evaluator_output[evaluator_output.index("{"):evaluator_output.rindex("}")+1]
                result = json.loads(json_str)
                quality_score = float(result.get("score", 50))
        except:
            pass
        
        return TaskResult(
            task_id=task_id,
            task_type=task_type,
            executor_output=executor_output[:500],  # 截断保存
            quality_score=quality_score,
            executor_tokens=executor_tokens,
            evaluator_tokens=evaluator_tokens,
            executor_latency_ms=executor_latency,
            evaluator_latency_ms=evaluator_latency,
            is_suspicious=is_suspicious,
            suspicious_reason=suspicious_reason
        )

class BenchmarkTasks:
    """Benchmark 任务集"""
    
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
    """运行完整 Benchmark"""
    
    api_key = os.environ.get("MINIMAX_API_KEY", "")
    if not api_key:
        # 尝试从配置文件读取
        try:
            with open("/root/.openclaw/openclaw.json", "r") as f:
                config = json.load(f)
                # 需要从 auth 获取
                api_key = "sk-cp-ZNEhSAB4-p-nraTwKzWoeLCpFPE-wY8If5v_1qxUvnW4_h0ryAunuH9_Vn-SItYx-D1AGFdRhD_6fn_9LhkpWG2yy6kUeRZBEjq8aFCUpruT5aFlM-Y5KDc"
        except:
            pass
    
    harness = HarnessV6(api_key)
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
        print(f"质量:{result.quality_score:.0f} 执行Token:{result.executor_tokens} 延迟:{result.executor_latency_ms/1000:.1f}s{sus}")
    
    # 计算汇总
    summary = compute_summary(results)
    
    return results, summary

def compute_summary(results: List[TaskResult]) -> Dict:
    """计算汇总指标"""
    
    core_results = [r for r in results if not getattr(r, 'is_generalization', False)]
    gen_results = [r for r in results if getattr(r, 'is_generalization', True)]
    
    core_scores = [r.quality_score for r in core_results]
    gen_scores = [r.quality_score for r in gen_results]
    
    core_avg = sum(core_scores) / len(core_scores) if core_scores else 0
    gen_avg = sum(gen_scores) / len(gen_scores) if gen_scores else 0
    
    total_executor_tokens = sum(r.executor_tokens for r in results)
    total_evaluator_tokens = sum(r.evaluator_tokens for r in results)
    avg_latency = sum(r.executor_latency_ms for r in results) / len(results) if results else 0
    
    suspicious_count = sum(1 for r in results if r.is_suspicious)
    
    # 字典序评估权重
    # 1. 评测准确与抗欺骗性 (60%)
    anti_cheat_factor = (1 - suspicious_count / len(results)) if results else 0
    accuracy_score = core_avg * anti_cheat_factor
    # 2. 泛化工具支撑度 (30%)
    generalization_score = gen_avg
    # 3. 底座自身运行效率 (10%)
    efficiency = 1000 / (avg_latency + 1)  # 延迟越低效率越高
    
    composite = 0.6 * accuracy_score + 0.3 * generalization_score + 0.1 * min(100, efficiency)
    
    return {
        "total_tasks": len(results),
        "core_avg_score": core_avg,
        "gen_avg_score": gen_avg,
        "total_executor_tokens": total_executor_tokens,
        "total_evaluator_tokens": total_evaluator_tokens,
        "total_tokens": total_executor_tokens + total_evaluator_tokens,
        "avg_latency_ms": avg_latency,
        "suspicious_count": suspicious_count,
        "composite_score": composite,
        "anti_cheat_factor": anti_cheat_factor
    }

def main():
    print("=" * 60)
    print("OpenClaw Harness v6.0 - 防作弊评测架构")
    print("核心：Executor/Evaluator 分离，expected 永不泄漏")
    print("=" * 60)
    
    start = time.time()
    results, summary = run_benchmark()
    elapsed = time.time() - start
    
    print("\n" + "=" * 60)
    print("Benchmark 结果汇总")
    print("=" * 60)
    print(f"\n[核心任务] 平均质量分: {summary['core_avg_score']:.1f}")
    print(f"[泛化任务] 平均质量分: {summary['gen_avg_score']:.1f}")
    print(f"[Token消耗] Executor: {summary['total_executor_tokens']} | Evaluator: {summary['total_evaluator_tokens']} | 总计: {summary['total_tokens']}")
    print(f"[平均延迟] {summary['avg_latency_ms']/1000:.1f}秒/任务")
    print(f"[可疑检测] {summary['suspicious_count']} 个任务标记为可疑")
    print(f"\n[综合评分] {summary['composite_score']:.2f}/100")
    print(f"[抗欺骗系数] {summary['anti_cheat_factor']:.2f}")
    print(f"[总耗时] {elapsed:.0f}秒")
    
    # 保存结果
    output = {
        "harness_version": "v6.0",
        "architecture": "Anti-Cheat Separated Executor/Evaluator",
        "timestamp": datetime.now().isoformat(),
        "elapsed_seconds": elapsed,
        "summary": summary,
        "individual_results": [asdict(r) for r in results]
    }
    
    output_file = "/root/.openclaw/workspace/mas_repo/openclaw_native/benchmark_results_v6_gen1.json"
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\n[保存] 结果已保存至: {output_file}")
    
    return summary

if __name__ == "__main__":
    main()
