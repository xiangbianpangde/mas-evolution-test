#!/usr/bin/env python3
"""
gen_006 专用评分器: AI辅助学习系统

评分维度:
- 学习计划完整性: 25%
- 降阶法内容质量: 20%
- 费曼测试题质量: 20%
- 复习机制: 15%
- 系统可运行性: 10%
- Agent协作: 10%
"""

import json
from typing import Dict, List, Any

class LearningAssistantScorer:
    """gen_006 AI辅助学习系统专用评分器"""
    
    def __init__(self):
        self.weights = {
            "plan_completeness": 0.25,
            "degradation_content": 0.20,
            "feynman_questions": 0.20,
            "review_mechanism": 0.15,
            "system_runnable": 0.10,
            "agent_collaboration": 0.10
        }
    
    def score_plan_completeness(self, learning_plan: Dict) -> float:
        """
        评分: 学习计划完整性
        - 是否包含学习目标
        - 是否包含知识点分解
        - 是否包含时间规划
        - 是否包含降阶路径
        """
        if not learning_plan:
            return 0.0
        
        score = 0.0
        
        # 有明确目标 (25%)
        if learning_plan.get("goals"):
            score += 25
        
        # 知识点分解 (25%)
        if learning_plan.get("knowledge_points"):
            score += 25
        
        # 时间规划 (25%)
        if learning_plan.get("timeline"):
            score += 25
        
        # 降阶路径 (25%)
        if learning_plan.get("degradation_path"):
            score += 25
        
        return min(100, score)
    
    def score_degradation_content(self, content: Dict) -> float:
        """
        评分: 降阶法内容质量
        - 是否按难度递进
        - 是否有基础概念
        - 是否有进阶内容
        - 是否有实践应用
        """
        if not content:
            return 0.0
        
        score = 50.0  # 基础分
        
        # 难度递进 (20%)
        levels = content.get("levels", [])
        if len(levels) >= 3:
            # 检查是否真的递进
            if self._is_progressive(levels):
                score += 20
            else:
                score += 10
        elif len(levels) >= 1:
            score += 5
        
        # 基础概念覆盖 (15%)
        basics = content.get("basics", [])
        if len(basics) >= 3:
            score += 15
        elif len(basics) >= 1:
            score += 8
        
        # 进阶内容 (15%)
        advanced = content.get("advanced", [])
        if len(advanced) >= 2:
            score += 15
        elif len(advanced) >= 1:
            score += 8
        
        return min(100, score)
    
    def _is_progressive(self, levels: List) -> bool:
        """检查是否真正递进"""
        if len(levels) < 2:
            return False
        
        # 检查难度是否递增
        for i in range(1, len(levels)):
            prev_difficulty = levels[i-1].get("difficulty", 0)
            curr_difficulty = levels[i].get("difficulty", 0)
            if curr_difficulty < prev_difficulty:
                return False
        return True
    
    def score_feynman_questions(self, questions: List[Dict]) -> float:
        """
        评分: 费曼测试题质量
        - 是否有概念解释题
        - 是否有应用题
        - 是否有深入理解题
        - 答案是否完整
        """
        if not questions:
            return 0.0
        
        score = 0.0
        
        # 题目数量足够 (20%)
        if len(questions) >= 10:
            score += 20
        elif len(questions) >= 5:
            score += 10
        elif len(questions) >= 1:
            score += 5
        
        # 题目类型覆盖 (40%)
        types = set()
        for q in questions:
            q_type = q.get("type", "")
            if "概念" in q_type or "解释" in q_type:
                types.add("concept")
            if "应用" in q_type or "计算" in q_type:
                types.add("application")
            if "分析" in q_type or "深入" in q_type:
                types.add("analysis")
        
        type_score = len(types) / 3 * 40
        score += type_score
        
        # 答案完整性 (40%)
        complete_answers = sum(1 for q in questions if q.get("answer"))
        answer_ratio = complete_answers / len(questions)
        score += answer_ratio * 40
        
        return min(100, score)
    
    def score_review_mechanism(self, review_plan: Dict) -> float:
        """
        评分: 复习机制
        - 是否基于遗忘曲线
        - 是否有复习时间点
        - 是否有个性化调整
        """
        if not review_plan:
            return 0.0
        
        score = 50.0  # 基础分
        
        # 遗忘曲线应用 (30%)
        if review_plan.get("forgetting_curve_based"):
            score += 30
        
        # 复习时间点 (20%)
        review_points = review_plan.get("review_points", [])
        if len(review_points) >= 4:  # 24小时内、1天、3天、7天等
            score += 20
        elif len(review_points) >= 2:
            score += 10
        
        return min(100, score)
    
    def score_system_runnable(self, system_result: Dict) -> float:
        """
        评分: 系统可运行性
        - 代码是否可运行
        - 是否缺少依赖
        - 是否能正常启动
        """
        if not system_result:
            return 0.0
        
        score = 0.0
        
        # 代码可运行 (50%)
        if system_result.get("runnable"):
            score += 50
        
        # 无致命错误 (30%)
        errors = system_result.get("errors", [])
        fatal_errors = [e for e in errors if e.get("severity") == "fatal"]
        if not fatal_errors:
            score += 30
        elif len(fatal_errors) < len(errors):
            score += 15
        
        # 能正常启动 (20%)
        if system_result.get("started"):
            score += 20
        
        return min(100, score)
    
    def score_agent_collaboration(self, collaboration_log: List[Dict]) -> float:
        """
        评分: Agent协作
        - Agent之间是否正确通信
        - 任务是否正确分配
        - 是否有死锁或冲突
        """
        if not collaboration_log:
            return 50.0  # 无法评估时给中等分
        
        score = 50.0
        
        # 成功通信 (30%)
        successful_comm = sum(1 for log in collaboration_log if log.get("success"))
        if collaboration_log:
            comm_ratio = successful_comm / len(collaboration_log)
            score += comm_ratio * 30
        
        # 无死锁 (20%)
        deadlocks = sum(1 for log in collaboration_log if log.get("deadlock"))
        if deadlocks == 0:
            score += 20
        else:
            score -= deadlocks * 5
        
        # 任务分配合理 (20%)
        task_assignments = sum(1 for log in collaboration_log if log.get("task_assigned"))
        if collaboration_log:
            assign_ratio = task_assignments / len(collaboration_log)
            score += assign_ratio * 20
        
        return max(0, min(100, score))
    
    def score_comprehensive(self, results: Dict) -> Dict:
        """
        综合评分
        """
        scores = {}
        
        scores["plan_completeness"] = self.score_plan_completeness(
            results.get("learning_plan", {})
        )
        
        scores["degradation_content"] = self.score_degradation_content(
            results.get("degradation_content", {})
        )
        
        scores["feynman_questions"] = self.score_feynman_questions(
            results.get("feynman_questions", [])
        )
        
        scores["review_mechanism"] = self.score_review_mechanism(
            results.get("review_mechanism", {})
        )
        
        scores["system_runnable"] = self.score_system_runnable(
            results.get("system_result", {})
        )
        
        scores["agent_collaboration"] = self.score_agent_collaboration(
            results.get("collaboration_log", [])
        )
        
        # 计算加权总分
        total = sum(scores[k] * self.weights[k] for k in self.weights)
        scores["total"] = total
        
        return scores


def main():
    """测试评分器"""
    scorer = LearningAssistantScorer()
    
    # 模拟结果
    mock_results = {
        "learning_plan": {
            "goals": "掌握高等数学下册核心内容",
            "knowledge_points": ["微分方程", "多元函数", "重积分"],
            "timeline": "7天学习计划",
            "degradation_path": "基础→进阶→应用"
        },
        "degradation_content": {
            "levels": [
                {"name": "基础", "difficulty": 1},
                {"name": "进阶", "difficulty": 3},
                {"name": "应用", "difficulty": 5}
            ],
            "basics": ["极限", "导数", "微分"],
            "advanced": ["偏导数", "重积分"]
        },
        "feynman_questions": [
            {"type": "概念解释", "question": "什么是微分？", "answer": "微分是..."},
            {"type": "概念解释", "question": "什么是积分？", "answer": "积分是..."},
            {"type": "应用计算", "question": "求y=x^2的导数", "answer": "2x"},
            {"type": "应用计算", "question": "求∫x dx", "answer": "x^2/2+C"},
            {"type": "分析理解", "question": "微分和积分的关系", "answer": "互为逆运算"}
        ],
        "review_mechanism": {
            "forgetting_curve_based": True,
            "review_points": ["24h", "1天", "3天", "7天", "14天"]
        },
        "system_result": {
            "runnable": True,
            "errors": [{"severity": "warning", "msg": "模块A有警告"}],
            "started": True
        },
        "collaboration_log": [
            {"success": True, "task_assigned": True},
            {"success": True, "task_assigned": True},
            {"success": True, "task_assigned": False}
        ]
    }
    
    scores = scorer.score_comprehensive(mock_results)
    
    print("=" * 50)
    print("gen_006 AI辅助学习系统 评分结果")
    print("=" * 50)
    for key, value in scores.items():
        if key == "weights":
            continue
        print(f"{key}: {value:.2f}")
    print("=" * 50)
    print(f"总分: {scores['total']:.2f}")


if __name__ == "__main__":
    main()
