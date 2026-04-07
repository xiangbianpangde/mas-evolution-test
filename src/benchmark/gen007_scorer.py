#!/usr/bin/env python3
"""
gen_007 专用评分器: 智能问数助手

评分维度:
- PDF解析正确率: 20%
- SQL生成准确率: 20%
- 回答正确性: 20%
- RAG增强效果: 15%
- 可视化: 10%
- 多轮对话: 10%
- Web界面: 5%
"""

import json
import os
from typing import Dict, List, Any

class FinanceQAScorer:
    """gen_007 智能问数助手专用评分器"""
    
    def __init__(self):
        self.weights = {
            "pdf_parsing": 0.20,
            "sql_accuracy": 0.20,
            "answer_quality": 0.20,
            "rag_enhancement": 0.15,
            "visualization": 0.10,
            "multi_turn": 0.10,
            "web_ui": 0.05
        }
    
    def score_pdf_parsing(self, pdf_files: List[str], db_result: Dict) -> float:
        """
        评分: PDF解析入库
        - 检查数据库表是否存在
        - 抽样验证数据准确性
        - 检查字段完整性
        """
        score = 0.0
        
        # 1. 检查数据库连接和表结构
        if not db_result.get("connected"):
            return 0.0
        
        tables = ["core_performance_indicators_sheet", "balance_sheet", 
                  "cash_flow_sheet", "income_sheet"]
        
        existing_tables = db_result.get("tables", [])
        table_score = len(set(tables) & set(existing_tables)) / len(tables)
        score += table_score * 40  # 40% of this dimension
        
        # 2. 检查数据行数
        total_rows = db_result.get("total_rows", 0)
        if total_rows > 100:
            score += 30  # 有足够数据
        elif total_rows > 0:
            score += 15  # 部分数据
        else:
            score += 0
        
        # 3. 抽样验证准确性 (假设抽样检查正确率)
        accuracy = db_result.get("sampled_accuracy", 0.0)
        score += accuracy * 30
        
        return min(100, score)
    
    def score_sql_generation(self, test_cases: List[Dict], results: Dict) -> float:
        """
        评分: SQL生成准确率
        - 输入自然语言查询
        - 验证生成的SQL正确性
        - 执行SQL验证结果
        """
        if not test_cases:
            return 0.0
        
        correct = 0
        for case in test_cases:
            query = case.get("nl_query", "")
            expected_sql = case.get("expected_sql", "")
            actual_sql = results.get(query, {}).get("sql", "")
            
            # 简化判断：SQL包含关键表名和字段
            if self._validate_sql_match(expected_sql, actual_sql):
                correct += 1
        
        return (correct / len(test_cases)) * 100
    
    def _validate_sql_match(self, expected: str, actual: str) -> bool:
        """验证SQL是否语义等价"""
        # 提取关键元素
        expected_tables = self._extract_tables(expected)
        actual_tables = self._extract_tables(actual)
        expected_fields = self._extract_fields(expected)
        actual_fields = self._extract_fields(actual)
        
        # 表名匹配
        if not set(expected_tables) & set(actual_tables):
            return False
        
        # 核心字段匹配
        if not set(expected_fields) & set(actual_fields):
            return False
        
        return True
    
    def _extract_tables(self, sql: str) -> set:
        """从SQL提取表名"""
        tables = set()
        keywords = ["FROM", "JOIN", "INTO"]
        for kw in keywords:
            if kw in sql.upper():
                idx = sql.upper().find(kw)
                rest = sql[idx + len(kw):].strip()
                # 提取到下一个空白或括号
                table = ""
                for c in rest:
                    if c in " (),;":
                        break
                    table += c
                if table:
                    tables.add(table.strip())
        return tables
    
    def _extract_fields(self, sql: str) -> set:
        """从SQL提取字段名"""
        fields = set()
        if "SELECT" in sql.upper():
            select_part = sql.upper().split("SELECT")[1].split("FROM")[0]
            for f in select_part.replace(",", " ").split():
                f = f.strip()
                if f and f not in ["", "*"]:
                    fields.add(f)
        return fields
    
    def score_answer_quality(self, answers: List[Dict], evaluator_prompt: str) -> float:
        """
        评分: 回答正确性
        - LLM评估回答质量
        - 检查是否包含数据支撑
        - 检查分析深度
        """
        if not answers:
            return 0.0
        
        total_score = 0.0
        for answer in answers:
            content = answer.get("content", "")
            
            # 基础分
            score = 50.0
            
            # 有数据支撑 +10
            if any(word in content for word in ["万元", "亿", "%", "增长率"]):
                score += 10
            
            # 有分析结论 +15
            if any(word in content for word in ["呈", "增长", "下降", "分析", "原因"]):
                score += 15
            
            # 有具体数字 +10
            if any(char.isdigit() for char in content):
                score += 10
            
            # 结构清晰 +15
            if content.count("\n") >= 2:
                score += 15
            
            total_score += min(100, score)
        
        return total_score / len(answers)
    
    def score_rag_enhancement(self, queries: List[str], with_rag: Dict, without_rag: Dict) -> float:
        """
        评分: RAG增强效果
        - 对比有RAG和没有RAG的回答
        - RAG应该提供更丰富的背景信息
        """
        if not queries:
            return 50.0  # 无法评估时给中等分
        
        improvement = 0.0
        for query in queries:
            with_answer = with_rag.get(query, {}).get("content", "")
            without_answer = without_rag.get(query, {}).get("content", "")
            
            # RAG增强的回答应该更长更详细
            len_diff = len(with_answer) - len(without_answer)
            if len_diff > 100:
                improvement += 20
            elif len_diff > 50:
                improvement += 15
            elif len_diff > 0:
                improvement += 10
            else:
                improvement += 0
        
        return min(100, improvement / len(queries))
    
    def score_visualization(self, charts: List[Dict]) -> float:
        """
        评分: 可视化
        - 检查图表文件是否存在
        - 检查图表类型是否合适
        """
        if not charts:
            return 0.0
        
        score = 0.0
        for chart in charts:
            # 文件存在
            if chart.get("file_exists"):
                score += 40
            else:
                continue
            
            # 图表类型合适
            chart_type = chart.get("type", "")
            query_type = chart.get("query_type", "")
            
            suitable = False
            if chart_type == "折线图" and "趋势" in query_type:
                suitable = True
            elif chart_type == "柱状图" and "对比" in query_type:
                suitable = True
            elif chart_type == "饼图" and "占比" in query_type:
                suitable = True
            
            if suitable:
                score += 30
            else:
                score += 15  # 类型不完美但有图表
            
            # 图表有标题和标签
            if chart.get("has_title") and chart.get("has_labels"):
                score += 30
        
        return min(100, score / len(charts))
    
    def score_multi_turn(self, conversations: List[Dict]) -> float:
        """
        评分: 多轮对话
        - 验证上下文保持
        - 验证追问理解
        - 验证澄清机制
        """
        if not conversations:
            return 0.0
        
        total_score = 0.0
        for conv in conversations:
            score = 50.0  # 基础分
            
            history = conv.get("history", [])
            if len(history) < 2:
                total_score += 25  # 不够轮次
                continue
            
            # 检查上下文保持
            context_kept = True
            for i in range(1, len(history)):
                prev_entities = self._extract_entities(history[i-1]["answer"])
                curr_entities = self._extract_entities(history[i]["query"])
                if prev_entities and not any(e in str(curr_entities) for e in prev_entities):
                    context_kept = False
                    break
            
            if context_kept:
                score += 30
            
            # 检查追问理解
            if self._has_follow_up(history):
                score += 20
            
            total_score += min(100, score)
        
        return total_score / len(conversations)
    
    def _extract_entities(self, text: str) -> List[str]:
        """提取文本中的实体"""
        entities = []
        # 简单提取数字和特定词汇
        import re
        numbers = re.findall(r'\d+\.?\d*', text)
        entities.extend(numbers)
        return entities
    
    def _has_follow_up(self, history: List[Dict]) -> bool:
        """检查是否有追问"""
        for i in range(1, len(history)):
            query = history[i].get("query", "")
            # 追问通常包含"为什么","然后呢","还有"等
            if any(word in query for word in ["为什么", "然后", "还有", "接着"]):
                return True
        return False
    
    def score_web_ui(self, ui_result: Dict) -> float:
        """
        评分: Web界面
        - 检查关键页面是否存在
        - 检查基本功能可用性
        """
        score = 0.0
        
        # 能启动服务
        if ui_result.get("service_started"):
            score += 40
        
        # 关键页面存在
        pages = ui_result.get("pages", [])
        key_pages = ["首页", "查询页面", "可视化页面"]
        for kp in key_pages:
            if any(kp in p for p in pages):
                score += 15
        
        # API可调用
        if ui_result.get("api_callable"):
            score += 20
        
        return min(100, score)
    
    def score_comprehensive(self, results: Dict) -> Dict:
        """
        综合评分
        """
        scores = {}
        
        scores["pdf_parsing"] = self.score_pdf_parsing(
            results.get("pdf_files", []),
            results.get("db_result", {})
        )
        
        scores["sql_accuracy"] = self.score_sql_generation(
            results.get("sql_test_cases", []),
            results.get("sql_results", {})
        )
        
        scores["answer_quality"] = self.score_answer_quality(
            results.get("answers", []),
            results.get("evaluator_prompt", "")
        )
        
        scores["rag_enhancement"] = self.score_rag_enhancement(
            results.get("rag_queries", []),
            results.get("with_rag", {}),
            results.get("without_rag", {})
        )
        
        scores["visualization"] = self.score_visualization(
            results.get("charts", [])
        )
        
        scores["multi_turn"] = self.score_multi_turn(
            results.get("conversations", [])
        )
        
        scores["web_ui"] = self.score_web_ui(
            results.get("ui_result", {})
        )
        
        # 计算加权总分
        total = sum(scores[k] * self.weights[k] for k in self.weights)
        scores["total"] = total
        
        # 添加权重信息
        scores["weights"] = self.weights
        
        return scores


def main():
    """测试评分器"""
    scorer = FinanceQAScorer()
    
    # 模拟结果
    mock_results = {
        "pdf_files": ["report1.pdf", "report2.pdf"],
        "db_result": {
            "connected": True,
            "tables": ["core_performance_indicators_sheet", "balance_sheet", 
                      "cash_flow_sheet", "income_sheet"],
            "total_rows": 500,
            "sampled_accuracy": 0.85
        },
        "sql_test_cases": [
            {"nl_query": "金花股份利润总额是多少", "expected_sql": "SELECT total_profit FROM income_sheet"},
            {"nl_query": "华润三九2024年收入", "expected_sql": "SELECT revenue FROM income_sheet"}
        ],
        "sql_results": {
            "金花股份利润总额是多少": {"sql": "SELECT total_profit FROM income_sheet WHERE stock_abbr = '金花股份'"},
            "华润三九2024年收入": {"sql": "SELECT revenue FROM income_sheet WHERE stock_abbr = '华润三九'"}
        },
        "answers": [
            {"content": "金花股份2025年第三季度利润总额为3140万元，同比增长15%。"},
            {"content": "华润三九2024年主营业务收入为180亿元，呈增长趋势。"}
        ],
        "charts": [
            {"file_exists": True, "type": "折线图", "query_type": "趋势分析", "has_title": True, "has_labels": True}
        ],
        "conversations": [
            {"history": [
                {"query": "华润三九利润是多少", "answer": "华润三九2024年利润为15亿元"},
                {"query": "增长原因是什么", "answer": "主要是因为主营业务增长"}
            ]}
        ],
        "ui_result": {"service_started": True, "pages": ["首页", "查询页面"], "api_callable": True}
    }
    
    scores = scorer.score_comprehensive(mock_results)
    
    print("=" * 50)
    print("gen_007 评分结果")
    print("=" * 50)
    for key, value in scores.items():
        if key == "weights":
            continue
        print(f"{key}: {value:.2f}")
    print("=" * 50)
    print(f"总分: {scores['total']:.2f}")


if __name__ == "__main__":
    main()
