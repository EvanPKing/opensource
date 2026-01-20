"""LLM增强的Analyzer Agent - 深度分析"""
from typing import Dict, Any, List
import json
from .llm_base_agent import LLMBaseAgent


class LLMAnalyzerAgent(LLMBaseAgent):
    """使用LLM进行多维度深度分析 (6轮调用)"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("LLM-AnalyzerAgent", config)
    
    def execute(self, data_path: str) -> str:
        """
        执行深度分析
        
        Args:
            data_path: 结构化数据路径 (data/processed/memes.json)
            
        Returns:
            洞察数据文件路径 (data/processed/insights.json)
        """
        self.log_execution("开始深度分析 (6轮LLM调用)", data_path)
        
        with open(data_path, 'r', encoding='utf-8') as f:
            memes = json.load(f)
            
        insights = {}
        
        # 4.1 热门梗Top10 + 传播机制
        self.logger.info(">>> 4.1 分析Top10及传播机制...")
        insights['top_10_analysis'] = self._analyze_top_10(memes)
        
        # 4.2 平台生态对比
        self.logger.info(">>> 4.2 分析平台生态对比...")
        insights['platform_comparison'] = self._analyze_platforms(memes)
        
        # 4.3 跨平台传播路径
        self.logger.info(">>> 4.3 分析跨平台传播...")
        insights['propagation_paths'] = self._analyze_propagation(memes)
        
        # 4.4 时间趋势
        self.logger.info(">>> 4.4 分析时间趋势...")
        insights['time_trends'] = self._analyze_trends(memes)
        
        # 4.5 文化洞察
        self.logger.info(">>> 4.5 分析文化洞察...")
        insights['cultural_insights'] = self._analyze_culture(memes)
        
        # 4.6 商业价值预测
        self.logger.info(">>> 4.6 预测商业价值...")
        insights['commercial_value'] = self._predict_commercial(memes)
        
        # 保存洞察
        output_path = "data/processed/insights.json"
        self.save_output(insights, output_path)
        
        self.logger.info(f"✓ 深度分析完成，结果已保存至 {output_path}")
        return output_path

    def _call_analysis_llm(self, prompt: str, data: List[Dict]) -> Any:
        """通用分析调用方法"""
        # 为了节省token，只传入必要信息，或者分批传入
        # 这里简化处理，传入所有memes的摘要
        memes_summary = [
            f"{m.get('name')} ({m.get('platform')}): {m.get('description')[:50]}" 
            for m in data
        ]
        
        messages = [
            {"role": "system", "content": "你是一个资深的互联网文化研究员和数据分析师。"},
            {"role": "user", "content": f"{prompt}\n\n数据摘要:\n{json.dumps(memes_summary, ensure_ascii=False)}"}
        ]
        
        response = self.call_llm(messages, temperature=0.7)
        return response

    def _analyze_top_10(self, memes: List[Dict]) -> str:
        prompt = """请从数据中选出Top 10最火的梗。
对于每一个梗，详细分析其传播机制（为什么火？利用了什么心理？传播节点是什么？）。
返回Markdown格式的分析。"""
        return self._call_analysis_llm(prompt, memes)

    def _analyze_platforms(self, memes: List[Dict]) -> str:
        prompt = """请对比微博、B站、抖音、小红书等平台的梗文化生态。
分析各平台产生的梗有何不同？用户互动方式有何差异？
返回Markdown格式的分析。"""
        return self._call_analysis_llm(prompt, memes)

    def _analyze_propagation(self, memes: List[Dict]) -> str:
        prompt = """分析梗的跨平台传播路径。
通常一个梗是如何从一个小圈子（如贴吧、B站）扩散到大众平台（抖音、微博）的？
结合数据中的例子进行说明。
返回Markdown格式的分析。"""
        return self._call_analysis_llm(prompt, memes)

    def _analyze_trends(self, memes: List[Dict]) -> str:
        prompt = """分析这些梗的时间趋势。
现在的梗生命周期是变短了还是变长了？
有什么季节性或事件驱动的规律？
返回Markdown格式的分析。"""
        return self._call_analysis_llm(prompt, memes)

    def _analyze_culture(self, memes: List[Dict]) -> str:
        prompt = """请提供深度的文化洞察。
这些梗反映了当代年轻人什么样的心理状态、价值观或社会焦虑？
例如：发疯文学、躺平、电子榨菜等背后的社会心理。
返回Markdown格式的分析。"""
        return self._call_analysis_llm(prompt, memes)

    def _predict_commercial(self, memes: List[Dict]) -> str:
        prompt = """预测这些梗的商业价值。
品牌如何借势营销？
哪些梗适合商业化，哪些不适合（有风险）？
请给出具体的营销建议。
返回Markdown格式的分析。"""
        return self._call_analysis_llm(prompt, memes)
