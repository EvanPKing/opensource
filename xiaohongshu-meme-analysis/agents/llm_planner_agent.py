"""LLM增强的Planner Agent - 智能理解用户意图"""
from typing import Dict, Any
import json
from datetime import datetime
from .llm_base_agent import LLMBaseAgent


class LLMPlannerAgent(LLMBaseAgent):
    """使用LLM理解用户自然语言输入，生成智能执行计划"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("LLM-PlannerAgent", config)
    
    def execute(self, user_input: str) -> Dict[str, Any]:
        """
        使用LLM理解用户输入并生成计划
        
        Args:
            user_input: 用户的自然语言输入
            
        Returns:
            智能执行计划
        """
        self.log_execution("开始智能规划", user_input)
        
        # 构建LLM提示词
        system_prompt = """你是一个专业的数据分析规划专家。
你的任务是理解用户的分析需求，并生成详细的执行计划。

输出JSON格式，包含：
1. intent: 用户意图（trend_analysis/content_analysis/comparison等）
2. tavily_queries: Tavily搜索关键词列表（用于获取媒体报道、背景信息），例如 ["2025微博热梗", "B站梗文化"]
3. playwright_targets: Playwright爬取目标列表（用于获取实时热榜），例如 ["微博热搜", "知乎热榜", "B站热门"]

注意：
- 如果用户没说明年份，默认2025年
- tavily_queries应包含多个维度的搜索词
- playwright_targets应包含主流社交平台的热榜页面
"""
        
        user_prompt = f"""请分析以下用户需求并生成执行计划：

用户输入: "{user_input}"

请生成完整的JSON执行计划。"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        # 调用LLM
        response = self.call_llm(messages, temperature=0.3)
        
        if not response:
            # LLM失败，使用传统方法兜底
            self.logger.warning("LLM规划失败，使用传统方法")
            return self._fallback_planning(user_input)
        
        # 解析LLM返回的JSON
        try:
            plan = self._extract_json_from_response(response)
            
            # 补充元数据
            plan['user_input'] = user_input
            plan['created_at'] = datetime.now().isoformat()
            plan['planner_type'] = 'llm'
            
            self.log_execution("✓ LLM规划完成", plan)
            return plan
            
        except Exception as e:
            self.logger.error(f"解析LLM响应失败: {e}")
            return self._fallback_planning(user_input)
    
    def _extract_json_from_response(self, response: str) -> Dict:
        """从LLM响应中提取JSON"""
        # 尝试直接解析
        try:
            return json.loads(response)
        except:
            pass
        
        # 尝试提取代码块中的JSON
        import re
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(1))
        
        # 尝试找到第一个完整的JSON对象
        json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', response, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(0))
        
        raise ValueError("无法从响应中提取JSON")
    
    def _fallback_planning(self, user_input: str) -> Dict[str, Any]:
        """传统规划方法（兜底）"""
        import re
        
        # 提取年份
        year_match = re.search(r'20(\d{2})', user_input)
        year = f"20{year_match.group(1)}" if year_match else "2025"
        
        # 基础关键词
        keywords = ['热梗', '网络流行语', '表情包', 'meme']
        
        if '对比' in user_input or '比较' in user_input:
            intent = 'comparison'
        elif '趋势' in user_input or '变化' in user_input:
            intent = 'trend_analysis'
        else:
            intent = 'content_analysis'
        
        # 生成基础搜索查询
        base_queries = [
            f"{year}网络热梗流行语",
            f"{year}十大热梗",
            f"{year}梗文化趋势",
            f"{year}social media trends china"
        ]
        
        self.logger.info(f"Fallback plan generated queries: {base_queries}")
        
        return {
            'intent': intent,
            'tavily_queries': base_queries,
            'playwright_targets': ['微博热搜', '知乎热榜', 'B站热门'],
            'time_range': {
                'start': f'{year}-01',
                'end': f'{year}-12'
            },
            'keywords': keywords,
            'platforms': ['小红书', '微博', '知乎', 'B站'],
            'analysis_tasks': [
                'hot_meme_extraction',
                'trend_analysis',
                'platform_comparison'
            ],
            'output_requirements': 'markdown_report',
            'user_input': user_input,
            'created_at': datetime.now().isoformat(),
            'planner_type': 'fallback'
        }
