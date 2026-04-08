#!/usr/bin/env python3
"""
Strategy Registry - 策略注册表

根据 OpenAI Evals 最佳实践：
- 所有策略注册到统一接口
- 便于比较和复用
- 支持动态选择
"""

from typing import Dict, List, Optional
import json

class StrategyRegistry:
    """策略注册表"""
    
    def __init__(self):
        self._strategies = {}
        self._register_defaults()
    
    def _register_defaults(self):
        """注册默认策略"""
        self.register("v31_0_baseline", {
            "name": "v31_0_baseline",
            "description": "Original v31.0 baseline - 5000 tokens, MAX-2, temp=0.7",
            "research_tokens": 5000,
            "code_tokens": 5000,
            "max_runs": 2,
            "temperature": 0.7,
            "self_reflect": "core_only",
            "expected_score_range": (70, 80),
            "best_for": ["general research", "code generation"],
            "known_issues": []
        })
        
        self.register("v33_max3", {
            "name": "v33_max3",
            "description": "MAX-3 strategy - 5000 tokens, 3 runs for better selection",
            "research_tokens": 5000,
            "code_tokens": 5000,
            "max_runs": 3,
            "temperature": 0.5,
            "self_reflect": "none",
            "expected_score_range": (70, 78),
            "best_for": ["stable quality", "reduced variance"],
            "known_issues": ["slower due to 3 runs"]
        })
        
        self.register("v34_lowtemp", {
            "name": "v34_lowtemp",
            "description": "Low temperature for consistency",
            "research_tokens": 5000,
            "code_tokens": 5000,
            "max_runs": 2,
            "temperature": 0.3,
            "self_reflect": "core_only",
            "expected_score_range": (68, 76),
            "best_for": ["deterministic output"],
            "known_issues": ["may be less creative"]
        })
        
        self.register("v35_highcreative", {
            "name": "v35_highcreative",
            "description": "High temperature for creativity",
            "research_tokens": 5000,
            "code_tokens": 5000,
            "max_runs": 2,
            "temperature": 0.9,
            "self_reflect": "none",
            "expected_score_range": (65, 80),
            "best_for": ["creative tasks", "exploration"],
            "known_issues": ["high variance"]
        })
        
        self.register("v36_concise", {
            "name": "v36_concise",
            "description": "Concise output strategy",
            "research_tokens": 3000,
            "code_tokens": 3000,
            "max_runs": 2,
            "temperature": 0.5,
            "self_reflect": "none",
            "expected_score_range": (60, 72),
            "best_for": ["fast testing", "low resource"],
            "known_issues": ["quality may suffer"]
        })
    
    def register(self, name: str, strategy: Dict):
        """注册新策略"""
        self._strategies[name] = strategy
    
    def get(self, name: str) -> Optional[Dict]:
        """获取策略"""
        return self._strategies.get(name)
    
    def list_strategies(self) -> List[str]:
        """列出所有策略"""
        return list(self._strategies.keys())
    
    def select_best(self, criteria: Dict) -> Optional[str]:
        """
        根据条件选择最佳策略
        
        criteria: {"best_for": "creative tasks", "max_runs": 2}
        """
        for name, strategy in self._strategies.items():
            match = True
            for key, value in criteria.items():
                if strategy.get(key) != value:
                    match = False
                    break
            if match:
                return name
        return None
    
    def compare(self, name1: str, name2: str) -> Dict:
        """比较两个策略"""
        s1 = self.get(name1)
        s2 = self.get(name2)
        
        if not s1 or not s2:
            return {"error": "Strategy not found"}
        
        comparison = {
            "strategy1": name1,
            "strategy2": name2,
            "differences": []
        }
        
        for key in s1:
            if s1[key] != s2.get(key):
                comparison["differences"].append({
                    "key": key,
                    name1: s1[key],
                    name2: s2.get(key)
                })
        
        return comparison
    
    def export(self, filepath: str):
        """导出到文件"""
        with open(filepath, 'w') as f:
            json.dump(self._strategies, f, indent=2)
    
    def import_from(self, filepath: str):
        """从文件导入"""
        with open(filepath) as f:
            strategies = json.load(f)
            for name, strategy in strategies.items():
                self.register(name, strategy)

# 全局实例
registry = StrategyRegistry()

if __name__ == "__main__":
    # 测试
    print("Registered strategies:", registry.list_strategies())
    
    # 选择适合创意任务的策略
    best = registry.select_best({"temperature": 0.9})
    print(f"Best for high creativity: {best}")
    
    # 比较两个策略
    comparison = registry.compare("v31_0_baseline", "v33_max3")
    print(f"Comparison: {json.dumps(comparison, indent=2)}")
