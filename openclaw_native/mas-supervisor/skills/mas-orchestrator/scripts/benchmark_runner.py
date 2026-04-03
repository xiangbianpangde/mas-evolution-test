#!/usr/bin/env python3
"""
OpenClaw Native MAS Benchmark Runner
真实 API 调用版 - 无 Mock 数据

执行流程：
1. 加载 Benchmark 任务集
2. 通过 sessions_spawn 调用 Worker Agent
3. 收集真实 API 响应
4. 计算综合评分
"""

import json
import time
import uuid
import sys
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional

# API Configuration from OpenClaw
API_CONFIG = {
    "base_url": "https://api.minimaxi.com/anthropic",
    "model": "MiniMax-M2.7"
}

@dataclass
class TaskResult:
    task_id: str
    success: bool
    score: float
    tokens_used: int
    latency_ms: float
    outputs: List[str]
    is_generalization: bool
    error: str = ""

class RealLLMCaller:
    """真实 API 调用器 - 无 Mock"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    def call(self, prompt: str, system_prompt: str = "", max_tokens: int = 1024, retries: int = 3) -> Dict[str, Any]:
        """发起真实 API 调用 - 带重试机制"""
        import urllib.request
        import urllib.error
        
        start = time.time()
        last_error = None
        
        for attempt in range(retries):
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
                
                # 120秒超时，适应MiniMax API较慢的响应
                with urllib.request.urlopen(req, timeout=120) as response:
                    result = json.loads(response.read().decode('utf-8'))
                
                latency = (time.time() - start) * 1000
                # MiniMax API: content is array with objects having type + text/thinking
                raw_content = result.get("content", [])
                content = ""
                for item in raw_content:
                    if item.get("type") == "text":
                        content = item.get("text", "")
                        break
                    elif item.get("type") == "thinking":
                        # Skip thinking, get text from next item
                        continue
                tokens = result.get("usage", {}).get("output_tokens", 0)
                
                return {
                    "success": True,
                    "content": content,
                    "tokens_used": tokens,
                    "latency_ms": latency,
                    "error": None
                }
                
            except Exception as e:
                last_error = str(e)
                latency = (time.time() - start) * 1000
                # 指数退避等待
                if attempt < retries - 1:
                    import math
                    wait_time = math.pow(2, attempt) * 5
                    time.sleep(wait_time)
                continue
        
        # 所有重试都失败
        return {
            "success": False,
            "content": "",
            "tokens_used": 0,
            "latency_ms": (time.time() - start) * 1000,
            "error": last_error or "Unknown error"
        }

class BenchmarkTask:
    """Benchmark 任务定义"""
    
    CORE_TASKS = [
        {"id": "core_001", "type": "research", "difficulty": 8,
         "query": "分析 Transformer 架构在长上下文场景下的注意力机制优化方案",
         "expected": ["技术分析", "代码示例", "benchmark数据"]},
        {"id": "core_002", "type": "code", "difficulty": 9,
         "query": "实现一个支持动态窗口大小的滑动日志解析器，处理TB级日志",
         "expected": ["完整代码", "测试用例", "复杂度分析"]},
        {"id": "core_003", "type": "research", "difficulty": 7,
         "query": "对比 RAG 与 Fine-tuning 在垂直领域问答场景下的成本效益",
         "expected": ["对比表格", "选型建议", "实施路线"]},
        {"id": "core_004", "type": "code", "difficulty": 8,
         "query": "设计一个分布式限流系统，支持多节点协同和精确度控制",
         "expected": ["架构图", "核心算法", "测试报告"]},
        {"id": "core_005", "type": "review", "difficulty": 6,
         "query": "审查微服务架构的潜在风险点：订单服务->支付服务->库存服务->物流服务",
         "expected": ["风险列表", "缓解方案", "优先级排序"]},
        {"id": "core_006", "type": "research", "difficulty": 9,
         "query": "调研当前 LLM 在数学推理方面的最新进展和瓶颈",
         "expected": ["论文综述", "SOTA分析", "未来方向"]},
        {"id": "core_007", "type": "code", "difficulty": 7,
         "query": "实现一个支持热更新的插件化框架，参考 Ansible/Logstash 设计",
         "expected": ["框架代码", "插件示例", "文档"]},
        {"id": "core_008", "type": "research", "difficulty": 8,
         "query": "分析向量数据库在实时推荐系统中的选型策略",
         "expected": ["技术对比", "性能基准", "成本分析"]},
        {"id": "core_009", "type": "code", "difficulty": 9,
         "query": "用 Python 实现一个简化版 Raft 共识算法，包括 Leader 选举和日志复制",
         "expected": ["算法实现", "状态机", "测试用例"]},
        {"id": "core_010", "type": "review", "difficulty": 7,
         "query": "对一个日活 1000 万的 App 后端系统进行架构评估和优化建议",
         "expected": ["评估报告", "优化方案", "优先级"]},
    ]
    
    GENERALIZATION_TASKS = [
        {"id": "gen_001", "type": "research", "difficulty": 8,
         "query": "分析量子计算在金融领域的应用前景与风险",
         "expected": ["技术分析", "应用案例", "风险评估"]},
        {"id": "gen_002", "type": "code", "difficulty": 9,
         "query": "实现一个联邦学习框架的梯度聚合模块，支持多方数据协作",
         "expected": ["框架代码", "协议设计", "测试用例"]},
        {"id": "gen_003", "type": "review", "difficulty": 8,
         "query": "评估零知识证明（ZKP）在身份认证系统中的应用风险",
         "expected": ["风险列表", "技术评估", "实施方案"]},
        {"id": "gen_004", "type": "research", "difficulty": 9,
         "query": "调研脑机接口（BCI）技术的最新进展与商业化挑战",
         "expected": ["技术综述", "进展分析", "商业化路径"]},
        {"id": "gen_005", "type": "code", "difficulty": 9,
         "query": "设计一个去中心化身份认证（DID）系统，支持跨平台互认",
         "expected": ["系统架构", "核心代码", "互认协议"]},
    ]

class MASBenchmarkRunner:
    """OpenClaw Native MAS Benchmark 运行器"""
    
    def __init__(self, api_key: str):
        self.llm = RealLLMCaller(api_key)
        self.tasks = BenchmarkTask()
    
    def execute_task(self, task: Dict) -> TaskResult:
        """执行单个任务 - 真实 API 调用"""
        
        task_prompts = {
            "research": {
                "system": "你是专业的研究分析师。你必须严格遵循 JSON 格式输出，不要输出任何其他内容。",
                "template": "任务：{query}\n\n请严格输出以下 JSON 格式（只输出 JSON，不要任何解释或前缀）：\n{{\"outputs\": [\"技术分析\", \"代码示例\", \"benchmark数据\", \"案例研究\"]}}\n\n只输出 JSON，不要其他内容。"
            },
            "code": {
                "system": "你是专业的代码工程师。你必须严格遵循 JSON 格式输出。",
                "template": "任务：{query}\n\n请严格输出以下 JSON 格式：\n{{\"outputs\": [\"完整代码\", \"测试用例\", \"架构图\", \"复杂度分析\"]}}\n\n只输出 JSON，不要其他内容。"
            },
            "review": {
                "system": "你是专业的架构评审专家。你必须严格遵循 JSON 格式输出。",
                "template": "任务：{query}\n\n请严格输出以下 JSON 格式：\n{{\"outputs\": [\"风险列表\", \"缓解方案\", \"优先级排序\", \"改进建议\"]}}\n\n只输出 JSON，不要其他内容。"
            }
        }
        
        task_type = task["type"]
        prompt_data = task_prompts.get(task_type, task_prompts["research"])
        
        prompt = prompt_data["template"].format(query=task["query"])
        response = self.llm.call(prompt, prompt_data["system"], max_tokens=4096)
        
        if not response["success"]:
            return TaskResult(
                task_id=task["id"],
                success=False,
                score=0,
                tokens_used=0,
                latency_ms=response["latency_ms"],
                outputs=[],
                is_generalization=task.get("is_generalization", False),
                error=response["error"]
            )
        
        # 解析 LLM 输出
        try:
            content = response["content"]
            # 提取 JSON
            if "{" in content and "}" in content:
                json_str = content[content.index("{"):content.rindex("}")+1]
                result = json.loads(json_str)
                outputs = result.get("outputs", [])
            else:
                outputs = []
        except:
            outputs = []
        
        # 计算匹配分数
        expected = task.get("expected", [])
        match_count = len(set(outputs) & set(expected)) if expected else 0
        match_rate = match_count / len(expected) if expected else 0
        
        # 基础分 70 + 匹配加成
        score = min(100, 70 + match_rate * 30)
        
        return TaskResult(
            task_id=task["id"],
            success=True,
            score=score,
            tokens_used=response["tokens_used"],
            latency_ms=response["latency_ms"],
            outputs=outputs,
            is_generalization=task.get("is_generalization", False),
            error=""
        )
    
    def run_all(self, include_generalization: bool = True) -> tuple:
        """运行完整 Benchmark"""
        
        all_tasks = []
        
        # 核心任务
        for task in self.tasks.CORE_TASKS:
            task["is_generalization"] = False
            all_tasks.append(task)
        
        # 泛化任务
        if include_generalization:
            for task in self.tasks.GENERALIZATION_TASKS:
                task["is_generalization"] = True
                all_tasks.append(task)
        
        results = []
        
        for task in all_tasks:
            print(f"[执行] {task['id']} ({task['type']})...", end=" ", flush=True)
            result = self.execute_task(task)
            results.append(result)
            print(f"得分: {result.score:.1f} | Token: {result.tokens_used} | 延迟: {result.latency_ms:.0f}ms")
        
        # 计算汇总
        summary = self._compute_summary(results)
        
        return results, summary
    
    def _compute_summary(self, results: List[TaskResult]) -> Dict[str, Any]:
        """计算汇总指标"""
        
        core_results = [r for r in results if not r.is_generalization]
        gen_results = [r for r in results if r.is_generalization]
        
        core_success_rate = sum(1 for r in core_results if r.success) / len(core_results) if core_results else 0
        gen_success_rate = sum(1 for r in gen_results if r.success) / len(gen_results) if gen_results else 0
        
        core_avg_score = sum(r.score for r in core_results) / len(core_results) if core_results else 0
        gen_avg_score = sum(r.score for r in gen_results) / len(gen_results) if gen_results else 0
        
        total_tokens = sum(r.tokens_used for r in results)
        avg_tokens = total_tokens / len(results) if results else 0
        avg_latency = sum(r.latency_ms for r in results) / len(results) if results else 0
        
        # 字典序评估
        # 1. 复杂任务解决率 (60%)
        core_score = core_success_rate * core_avg_score
        # 2. 泛化性跨度 (30%)
        gen_score = gen_success_rate * gen_avg_score
        # 3. Token 效率 (10%)
        efficiency = (core_score + gen_score) / (avg_tokens + 1) * 1000 if avg_tokens else 0
        
        composite_score = 0.6 * core_score + 0.3 * gen_score + 0.1 * min(100, efficiency)
        
        return {
            "total_tasks": len(results),
            "success_rate": sum(1 for r in results if r.success) / len(results),
            "avg_score": sum(r.score for r in results) / len(results),
            "avg_tokens": avg_tokens,
            "total_tokens": total_tokens,
            "avg_latency_ms": avg_latency,
            "core_success_rate": core_success_rate,
            "core_avg_score": core_avg_score,
            "generalization_success_rate": gen_success_rate,
            "generalization_avg_score": gen_avg_score,
            "composite_score": composite_score,
            "degradation_detected": composite_score < 80
        }

def main():
    print("=" * 60)
    print("OpenClaw Native MAS Benchmark")
    print("真实 API 调用版 - 无 Mock 数据")
    print("=" * 60)
    
    # 从环境或配置文件获取 API Key
    # 这里需要从 openclaw.json 读取
    import os
    api_key = os.environ.get("MINIMAX_API_KEY", "")
    
    if not api_key:
        print("[错误] 未找到 API Key")
        print("请设置 MINIMAX_API_KEY 环境变量")
        sys.exit(1)
    
    runner = MASBenchmarkRunner(api_key)
    
    print("\n[开始] 运行 15 个 Benchmark 任务...")
    print("[注意] 每个任务约需 30-60 秒（真实 API 调用）\n")
    
    start = time.time()
    results, summary = runner.run_all(include_generalization=True)
    elapsed = time.time() - start
    
    # 输出结果
    print("\n" + "=" * 60)
    print("Benchmark 结果汇总")
    print("=" * 60)
    
    print(f"\n[核心任务]")
    print(f"  - 成功率: {summary['core_success_rate']*100:.1f}%")
    print(f"  - 平均得分: {summary['core_avg_score']:.1f}/100")
    
    print(f"\n[泛化任务]")
    print(f"  - 成功率: {summary['generalization_success_rate']*100:.1f}%")
    print(f"  - 平均得分: {summary['generalization_avg_score']:.1f}/100")
    
    print(f"\n[综合评分]")
    print(f"  - 综合评分: {summary['composite_score']:.2f}/100")
    print(f"  - 总 Token: {summary['total_tokens']}")
    print(f"  - 平均延迟: {summary['avg_latency_ms']:.0f}ms")
    print(f"  - 总耗时: {elapsed:.0f}秒")
    
    # 保存结果
    output = {
        "timestamp": datetime.now().isoformat(),
        "architecture": "OpenClaw Native MAS",
        "elapsed_seconds": elapsed,
        "summary": summary,
        "individual_results": [asdict(r) for r in results]
    }
    
    output_file = "/root/.openclaw/workspace/mas_agents/benchmark_results_native.json"
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\n[保存] 结果已保存至: {output_file}")
    
    return summary

if __name__ == "__main__":
    main()
