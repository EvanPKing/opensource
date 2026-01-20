"""LLM增强的工作流编排器"""
from typing import Dict, Any
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from agents.llm_planner_agent import LLMPlannerAgent
from agents.llm_crawler_agent import LLMCrawlerAgent
from agents.llm_extractor_agent import LLMExtractorAgent
from agents.llm_analyzer_agent import LLMAnalyzerAgent
from agents.llm_writer_agent import LLMWriterAgent
from config.llm_config import AGENT_CONFIG


class LLMOrchestrator:
    """LLM增强的工作流协调器 (5步工作流)"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or AGENT_CONFIG
        
        # 初始化所有LLM Agents
        self.planner = LLMPlannerAgent(self.config.get('planner', {}))
        self.crawler = LLMCrawlerAgent(self.config.get('crawler', {}))
        self.extractor = LLMExtractorAgent(self.config.get('extractor', {})) # 新增
        self.analyzer = LLMAnalyzerAgent(self.config.get('analyzer', {}))
        self.writer = LLMWriterAgent(self.config.get('writer', {}))
        
        print("="*60)
        print("🤖 LLM增强工作流初始化完成")
        print("🔥 全网热梗分析系统 (Tavily + Playwright + DeepSeek)")
        print("="*60)
    
    def run(self, user_input: str) -> str:
        """
        执行完整的5步工作流
        """
        print(f"\n{'='*60}")
        print(f"🚀 开始执行LLM增强工作流")
        print(f"💬 用户输入: {user_input}")
        print(f"{'='*60}\n")
        
        # Step 1: LLM Planner (规划)
        print("🧠 Step 1: LLM-Planner (规划)...")
        plan = self.planner.execute(user_input)
        print(f"   ✓ 意图: {plan.get('intent', 'unknown')}")
        print(f"   ✓ Tavily查询: {len(plan.get('tavily_queries', []))}条")
        print(f"   ✓ Playwright目标: {len(plan.get('playwright_targets', []))}个\n")
        
        # Step 2: Multi-Tool Crawler (数据采集)
        print("🌐 Step 2: Multi-Tool Crawler (数据采集)...")
        print("   └─ 2.1 Tavily搜索 (媒体报道)")
        print("   └─ 2.2 Playwright爬取 (实时热榜)")
        raw_data_path = self.crawler.execute(plan)
        print(f"   ✓ 原始数据已保存: {raw_data_path}\n")
        
        # Step 3: LLM Extractor (结构化提取)
        print("⛏️ Step 3: LLM-Extractor (结构化提取)...")
        print("   └─ 从杂乱数据中提取梗信息")
        memes_path = self.extractor.execute(raw_data_path)
        print(f"   ✓ 结构化数据已保存: {memes_path}\n")
        
        # Step 4: LLM Analyzer (深度分析)
        print("📊 Step 4: LLM-Analyzer (深度分析)...")
        print("   └─ 6轮深度分析 (Top10/生态/传播/趋势/文化/商业)")
        insights_path = self.analyzer.execute(memes_path)
        print(f"   ✓ 洞察已保存: {insights_path}\n")
        
        # Step 5: LLM Writer (报告生成)
        print("📝 Step 5: LLM-Writer (报告生成)...")
        print("   └─ 撰写4000-6000字深度报告")
        report_path = self.writer.execute(insights_path)
        print(f"   ✓ 报告已保存: {report_path}\n")
        
        print(f"{'='*60}")
        print(f"🎉 工作流执行完成!")
        print(f"📄 最终报告: {report_path}")
        print(f"{'='*60}\n")
        
        return report_path
