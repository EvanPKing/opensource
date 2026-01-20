"""LLM增强的Writer Agent - 报告生成"""
from typing import Dict, Any
import json
import os
from datetime import datetime
from .llm_base_agent import LLMBaseAgent


class LLMWriterAgent(LLMBaseAgent):
    """使用LLM生成深度分析报告"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("LLM-WriterAgent", config)
    
    def execute(self, insights_path: str) -> str:
        """
        生成最终报告
        
        Args:
            insights_path: 洞察数据路径 (data/processed/insights.json)
            
        Returns:
            报告文件路径 (output/report_YYYYMMDD.md)
        """
        self.log_execution("开始生成报告", insights_path)
        
        with open(insights_path, 'r', encoding='utf-8') as f:
            insights = json.load(f)
            
        # 整合所有洞察内容
        report_content = self._generate_report(insights)
        
        # 保存报告
        date_str = datetime.now().strftime("%Y%m%d")
        output_dir = "reports"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        output_path = f"{output_dir}/report_{date_str}.md"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
            
        self.logger.info(f"✓ 报告生成完成，已保存至 {output_path}")
        return output_path
    
    def _generate_report(self, insights: Dict[str, Any]) -> str:
        """使用LLM生成完整报告"""
        
        # 组装上下文
        context = f"""
【Top 10分析】: {insights.get('top_10_analysis', '')}
【平台对比】: {insights.get('platform_comparison', '')}
【传播路径】: {insights.get('propagation_paths', '')}
【时间趋势】: {insights.get('time_trends', '')}
【文化洞察】: {insights.get('cultural_insights', '')}
【商业价值】: {insights.get('commercial_value', '')}
"""
        
        system_prompt = """你是一个专业的商业分析师和内容创作者。
你需要基于提供的分析素材，撰写一份高质量的《网络热梗深度分析报告》。
报告应逻辑清晰、见解深刻，字数在4000-6000字左右。

报告结构：
1. # 执行摘要 (Executive Summary)
   - 核心发现
   - 关键趋势
2. # 2025年热门梗Top10深度解析
   - 详细分析每个梗的起因、经过、结果
3. # 平台生态全景对比
   - 微博 vs B站 vs 抖音 vs 小红书
4. # 跨平台传播机制解密
   - 传播路径图谱
   - 关键节点分析
5. # 未来趋势预测
   - 梗文化的发展方向
6. # 商业化与实用建议
   - 对品牌方的建议
   - 对内容创作者的建议
"""

        user_prompt = f"""请根据以下素材撰写完整报告：

{context}

请直接输出Markdown格式的报告内容。"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        response = self.call_llm(messages, temperature=0.7, max_tokens=4000)
        return response
