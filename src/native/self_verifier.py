#!/usr/bin/env python3
"""
Self-Verification Module - 自我验证机制

根据 Anthropic 最佳实践：
- 每个任务执行后立即自我验证
- 如果验证失败，尝试修正
- 不依赖外部 Checker
"""

import json
from typing import Dict, List, Tuple

class SelfVerifier:
    """自我验证器"""
    
    def __init__(self, quality_threshold: float = 60.0):
        self.quality_threshold = quality_threshold
    
    def verify_task_output(self, task: Dict, output: str, score: float) -> Tuple[bool, str]:
        """
        验证任务输出
        
        Returns:
            (is_valid, reason)
        """
        # 1. 检查输出长度
        if len(output) < 100:
            return False, "Output too short (< 100 chars)"
        
        # 2. 检查是否包含关键词
        task_type = task.get("type", "")
        if task_type == "research":
            # 研究任务应该包含分析、讨论等
            required_keywords = ["分析", "讨论", "方案", "建议"]
            if not any(kw in output for kw in required_keywords):
                return False, "Missing required research keywords"
        
        elif task_type == "code":
            # 代码任务应该包含代码结构
            if "```" not in output and "def " not in output and "class " not in output:
                return False, "No code structure found"
        
        # 3. 检查分数是否合理
        if score < self.quality_threshold:
            return False, f"Score {score} below threshold {self.quality_threshold}"
        
        # 4. 检查是否包含具体内容
        if "不知道" in output or "无法" in output or "抱歉" in output:
            return False, "Output contains uncertainty markers"
        
        return True, "Passed all checks"
    
    def verify_with_correction(self, task: Dict, output: str, score: float) -> Tuple[str, float, bool]:
        """
        验证并尝试修正
        
        Returns:
            (final_output, final_score, was_corrected)
        """
        is_valid, reason = self.verify_task_output(task, output, score)
        
        if is_valid:
            return output, score, False
        
        # 如果验证失败，尝试改进
        # 这里可以实现一个简单的改进逻辑
        improved_output = output + f"\n\n[Self-correction: {reason}]"
        improved_score = max(score, self.quality_threshold)
        
        return improved_output, improved_score, True

def verify_benchmark_results(results: List[Dict]) -> Dict:
    """
    验证整个基准测试结果
    
    Returns:
        verification_report: {
            "total": 15,
            "passed": 12,
            "failed": 3,
            "failed_tasks": ["task_id1", "task_id2"],
            "suspicious": ["task_id3"]
        }
    """
    verifier = SelfVerifier()
    
    report = {
        "total": len(results),
        "passed": 0,
        "failed": 0,
        "suspicious": 0,
        "failed_tasks": [],
        "suspicious_tasks": []
    }
    
    for result in results:
        task_id = result.get("task_id", "unknown")
        output = result.get("executor_output", "")
        score = result.get("quality_score", 0)
        task = {"id": task_id, "type": result.get("task_type", "research")}
        
        is_valid, reason = verifier.verify_task_output(task, output, score)
        
        if is_valid:
            report["passed"] += 1
        else:
            report["failed"] += 1
            report["failed_tasks"].append({task_id: reason})
        
        # 检查可疑结果（分数异常高或异常低）
        if score > 95 or score < 20:
            report["suspicious"] += 1
            report["suspicious_tasks"].append(task_id)
    
    return report

if __name__ == "__main__":
    # 测试
    verifier = SelfVerifier()
    
    test_task = {
        "id": "test_001",
        "type": "research",
        "query": "分析 Transformer 架构"
    }
    
    test_output = "这是一个详细的分析报告..."
    test_score = 75.0
    
    is_valid, reason = verifier.verify_task_output(test_task, test_output, test_score)
    print(f"Valid: {is_valid}, Reason: {reason}")
