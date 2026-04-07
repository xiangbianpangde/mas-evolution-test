#!/usr/bin/env python3
"""
OpenClaw Native Harness v10.0 - Strict Comparative Evaluator

核心改进（相对于 v6-v9）：
v6-v9: Evaluator 使用宽松的绝对评分（返回 ~50 分，无区分度）
v10:   使用严格的对比评分机制

新评分机制：
1. 每个维度分 5 个等级（L1-L5）
2. L3 = 合格，L5 = 卓越
3. 必须有具体证据支持评分
4. 强制区分度：不能全是 L3

架构：
v10: Executor → [对比评估] → 严格分数
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
    depth_score: int  # 1-5
    completeness_score: int  # 1-5
    actionability_score: int  # 1-5
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

class HarnessV10:
    """
    v10.0 严格对比评估架构
    
    核心问题：v6-v9 的 Evaluator 返回 ~50 分，无区分度
    解决方案：使用 5 级对比评分
    """
    
    # Executor prompts（保持 v9 的高质量要求）
    EXECUTOR_PROMPTS = {
        "research": """你是一个专业的研究分析师。进行深度技术分析。

任务：{query}

要求：
1. 深入分析技术原理
2. 提供可运行的代码示例
3. 提供具体 benchmark 数据（必须包含数字）
4. 引用具体论文/文档
5. 分析局限性和未来方向

输出 400+ 字结构化内容。""",

        "code": """你是一个专业的代码工程师。生成高质量代码解决方案。

任务：{query}

要求：
1. 完整可运行的代码
2. 包含单元测试
3. 提供架构设计说明
4. 分析复杂度
5. 提供使用示例

输出完整代码和说明，400+ 字。""",

        "review": """你是一个专业的架构评审专家。进行深度架构评审。

任务：{query}

要求：
1. 识别至少 5 个风险点（影响程度、发生概率、描述）
2. 每个风险有缓解方案
3. 优先级排序（P0/P1/P2）
4. 成本效益分析
5. 具体可执行的改进计划

输出完整评审报告，400+ 字。"""
    }
    
    # v10 严格对比评估器
    STRICT_EVALUATOR = """你是一个严格的技术评估专家。你的任务是评估输出质量的 5 个等级。

## 评分标准（必须严格遵守）

### 技术深度 (depth)
- **L5 (90-100分)**: 卓越 - 有独到见解，包含原创性分析，引用最新论文/技术
- **L4 (75-89分)**: 优秀 - 分析深入，有技术洞察，包含具体实现细节
- **L3 (60-74分)**: 合格 - 技术正确，有一定深度，但缺乏深度见解
- **L2 (40-59分)**: 不足 - 分析表面，缺少关键技术细节
- **L1 (0-39分)**: 差 - 错误频发或严重缺失

### 完整性 (completeness)
- **L5 (90-100分)**: 完整 - 覆盖所有方面，无重要遗漏
- **L4 (75-89分)**: 较好 - 覆盖主要方面，少量遗漏
- **L3 (60-74分)**: 基本完整 - 覆盖核心内容，但有遗漏
- **L2 (40-59分)**: 不完整 - 遗漏重要方面
- **L1 (0-39分)**: 严重缺失 - 核心内容缺失

### 可操作性 (actionability)
- **L5 (90-100分)**: 极强 - 建议可直接落地，包含具体步骤/参数
- **L4 (75-89分)**: 较强 - 建议可操作，有具体方案
- **L3 (60-74分)**: 基本可操作 - 有建议但需要进一步细化
- **L2 (40-59分)**: 难以操作 - 建议过于抽象
- **L1 (0-39分)**: 不可操作 - 建议无用或不现实

## 强制要求

1. **每个维度必须给出 1-5 的整数等级**
2. **必须写出评分的具体证据**（引用输出中的具体内容）
3. **等级不能全是 L3** - 必须有区分度
4. **证据必须具体** - 不能写"整体不错"这种模糊描述

## 输出格式

```json
{
  "depth": {"level": 1-5, "evidence": "引用输出中的具体句子或数据"},
  "completeness": {"level": 1-5, "evidence": "引用输出中的具体内容"},
  "actionability": {"level": 1-5, "evidence": "引用输出中的具体建议或代码"},
  "overall_score": 0-100,
  "reasoning": "整体评价"
}
```

## 要评估的内容

请评估以下技术输出的质量：

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
                task_id=task_id, task_type=task_type,
                executor_output="",
                quality_score=0, depth_score=0, completeness_score=0, actionability_score=0,
                executor_tokens=0, evaluator_tokens=0,
                executor_latency_ms=executor_latency, evaluator_latency_ms=0,
                error=executor_response["error"]
            )
        
        executor_output = executor_response["content"]
        executor_tokens = executor_response["tokens_used"]
        
        # 异常检测
        is_suspicious = False
        if executor_latency < 5000 and len(executor_output) > 1000:
            is_suspicious = True
        
        # ============ Stage 2: 严格评估 ============
        evaluator_start = time.time()
        evaluator_response = self.llm.call(
            prompt=self.STRICT_EVALUATOR.format(content=executor_output[:4000]),
            system_prompt="你是一个严格的技术评估专家。评分必须客观有据。",
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
                    
                    depth_level = int(result.get("depth", {}).get("level", 3))
                    complete_level = int(result.get("completeness", {}).get("level", 3))
                    action_level = int(result.get("actionability", {}).get("level", 3))
                    
                    # 映射 L1-L5 到 0-100
                    # L1=20, L2=40, L3=60, L4=80, L5=100
                    depth_score = depth_level
                    completeness_score = complete_level
                    actionability_score = action_level
                    
                    quality_score = float(result.get("overall_score", 50))
            except Exception as e:
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
    
    harness = HarnessV10(api_key)
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
    print("OpenClaw Harness v10.0 - Strict Comparative Evaluator")
    print("核心：L1-L5 严格分级，强制区分度")
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
        "harness_version": "v10.0",
        "architecture": "Strict L1-L5 Comparative Evaluator",
        "timestamp": datetime.now().isoformat(),
        "elapsed_seconds": elapsed,
        "summary": summary,
        "individual_results": [asdict(r) for r in results]
    }
    
    output_file = "/root/.openclaw/workspace/mas_repo/openclaw_native/benchmark_results_v10_gen1.json"
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\n[保存] 结果已保存至: {output_file}")
    return summary

if __name__ == "__main__":
    main()
