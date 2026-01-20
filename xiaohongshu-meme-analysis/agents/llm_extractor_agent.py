"""LLM增强的Extractor Agent - 结构化提取"""
from typing import Dict, Any, List
import json
import os
from .llm_base_agent import LLMBaseAgent


class LLMExtractorAgent(LLMBaseAgent):
    """使用LLM从原始数据中提取结构化梗信息"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("LLM-ExtractorAgent", config)
    
    def execute(self, data_path: str) -> str:
        """
        执行结构化提取
        
        Args:
            data_path: 原始数据文件路径 (data/raw/multi_source.json)
            
        Returns:
            处理后的数据文件路径 (data/processed/memes.json)
        """
        self.log_execution("开始结构化提取", data_path)
        
        # 读取原始数据
        if not os.path.exists(data_path):
            self.logger.error(f"找不到数据文件: {data_path}")
            return ""
            
        with open(data_path, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
            
        # 准备Prompt上下文
        # 恢复正常的上下文长度，确保提取质量
        raw_tavily = raw_data.get('tavily_results', [])[:5] # 恢复到5条
        tavily_results = []
        for item in raw_tavily:
            tavily_results.append({
                "title": item.get('title'),
                "content": item.get('content', '')[:1000], # 恢复到1000字，保留更多细节
                "source": "tavily"
            })
            
        playwright_results = raw_data.get('playwright_results', [])[:5] # 恢复到5条
        
        # 简化Playwright内容
        simplified_playwright = []
        for item in playwright_results:
            simplified_playwright.append({
                "source": item.get('source'),
                "target": item.get('target'),
                "content_snippet": item.get('content_snippet', '')[:800] # 恢复到800字
            })
            
        context_data = {
            "media_reports": tavily_results,
            "realtime_data": simplified_playwright
        }
        
        # 调用LLM进行提取
        memes = self._extract_memes(context_data)
        
        if not memes:
            self.logger.warning("LLM提取失败，尝试使用简单的正则表达式备选方案")
            memes = self._fallback_extract(raw_data)
        
        # 保存结果
        output_path = "data/processed/memes.json"
        self.save_output(memes, output_path)
        
        self.logger.info(f"✓ 结构化提取完成，共提取 {len(memes)} 个梗")
        return output_path
    
    def _extract_memes(self, data: Dict) -> List[Dict]:
        """使用LLM提取梗信息"""
        
        system_prompt = """你是一个专业的数据结构化专家。
你的任务是从杂乱的搜索结果和爬取数据中，提取出清晰的"网络热梗"信息。

请提取以下字段：
1. name: 梗名称/流行语
2. platform: 主要来源/流行平台
3. heat: 热度/流行程度描述
4. description: 详细描述（含义、用法、来源）
5. tags: 标签列表

返回标准的JSON数组格式。"""
        
        user_prompt = f"""以下是收集到的多源数据：
{json.dumps(data, ensure_ascii=False, indent=2)}

请从中提取所有识别到的热梗信息（目标25-40条）。
返回JSON数组：
[
  {{
    "name": "梗名称",
    "platform": "平台",
    "heat": "热度描述",
    "description": "描述",
    "tags": ["标签1", "标签2"]
  }},
  ...
]"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        # 增加超时时间和重试
        import time
        max_retries = 3
        for i in range(max_retries):
            try:
                print(f"DEBUG: Attempting to call LLM (Attempt {i+1}/{max_retries})...")
                response = self.call_llm(messages, temperature=0.1, max_tokens=4000)
                if response:
                    break
                else:
                    print("DEBUG: Empty response from LLM, retrying...")
                    time.sleep(2)
            except Exception as e:
                print(f"DEBUG: Error calling LLM: {e}, retrying...")
                time.sleep(2)
        
        if not response:
            self.logger.error("Failed to get response from LLM after retries")
            return []

        print(f"DEBUG: LLM Response length: {len(response)}")
        print(f"DEBUG: LLM Response preview: {response[:200]}")
        
        try:
            return self._extract_json_from_response(response)
        except Exception as e:
            self.logger.error(f"提取JSON失败: {e}")
            return []

    def _extract_json_from_response(self, response: str) -> Any:
        """从响应中提取JSON"""
        import re
        
        # 尝试直接解析
        try:
            return json.loads(response)
        except:
            pass
            
        # 尝试提取代码块
        match = re.search(r'```(?:json)?\s*(\[.*\])\s*```', response, re.DOTALL)
        if match:
            return json.loads(match.group(1))
            
        # 尝试提取数组
        match = re.search(r'\[.*\]', response, re.DOTALL)
        if match:
            return json.loads(match.group(0))
            
        raise ValueError("无法提取JSON数组")

    def _fallback_extract(self, raw_data: Dict) -> List[Dict]:
        """备选提取方案，当LLM失败时使用"""
        memes = []
        # 简单提取playwright的热搜数据
        playwright_results = raw_data.get('playwright_results', [])
        for item in playwright_results:
            if item.get('content_snippet'):
                # 假设内容片段的第一行可能是标题
                lines = item.get('content_snippet', '').split('\n')
                title = lines[0] if lines else "未知热梗"
                memes.append({
                    "name": title[:20],
                    "platform": item.get('source', 'unknown'),
                    "heat": "未知",
                    "description": item.get('content_snippet', '')[:100],
                    "tags": ["自动提取", "备选方案"]
                })
        
        # 简单提取Tavily的标题
        tavily_results = raw_data.get('tavily_results', [])
        for item in tavily_results:
            memes.append({
                "name": item.get('title', '未知')[:20],
                "platform": "media",
                "heat": "未知",
                "description": item.get('content', '')[:100],
                "tags": ["自动提取", "备选方案"]
            })
            
        return memes[:10] # 限制返回数量
