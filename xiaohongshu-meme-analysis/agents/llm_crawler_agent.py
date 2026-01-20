"""LLM增强的Crawler Agent - 多源数据采集"""
from typing import Dict, Any, List
import json
import os
import time
from datetime import datetime
from .llm_base_agent import LLMBaseAgent

try:
    from tavily import TavilyClient
except ImportError:
    TavilyClient = None

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sync_playwright = None

class LLMCrawlerAgent(LLMBaseAgent):
    """多工具数据采集Agent (Tavily + Playwright)"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("LLM-CrawlerAgent", config)
        self.tavily_api_key = os.getenv("TAVILY_API_KEY")
    
    def execute(self, plan: Dict[str, Any]) -> str:
        """
        执行数据采集
        
        Args:
            plan: 规划结果，包含 tavily_queries 和 playwright_targets
            
        Returns:
            数据文件路径
        """
        self.log_execution("开始多源数据采集", plan)
        
        tavily_queries = plan.get("tavily_queries", [])
        playwright_targets = plan.get("playwright_targets", [])
        self.logger.info(f"Received plan - Tavily Queries: {tavily_queries}")
        self.logger.info(f"Received plan - Playwright Targets: {playwright_targets}")
        
        results = {
            "tavily_results": [],
            "playwright_results": [],
            "timestamp": datetime.now().isoformat()
        }
        
        # 2.1 Tavily搜索
        tavily_queries = plan.get("tavily_queries", [])
        if tavily_queries:
            results["tavily_results"] = self._run_tavily_search(tavily_queries)
            
        # 2.2 Playwright爬取
        playwright_targets = plan.get("playwright_targets", [])
        if playwright_targets:
            results["playwright_results"] = self._run_playwright_crawl(playwright_targets)
            
        # 保存数据
        output_path = "data/raw/multi_source.json"
        self.save_output(results, output_path)
        
        self.logger.info(f"✓ 数据采集完成，保存至 {output_path}")
        self.logger.info(f"  - Tavily结果: {len(results['tavily_results'])} 条")
        self.logger.info(f"  - Playwright结果: {len(results['playwright_results'])} 条")
        
        return output_path
    
    def _run_tavily_search(self, queries: List[str]) -> List[Dict]:
        """执行Tavily搜索"""
        self.logger.info("启动Tavily搜索...")
        
        if not self.tavily_api_key:
            self.logger.warning("未检测到 TAVILY_API_KEY，跳过Tavily搜索")
            return []
        
        all_results = []
        
        # 优先使用SDK
        # if TavilyClient:
        if False: # 强制使用Requests以提高稳定性
            client = TavilyClient(api_key=self.tavily_api_key)
            for query in queries:
                try:
                    self.logger.info(f"搜索 (SDK): {query}")
                    response = client.search(query, search_depth="advanced", max_results=10)
                    for res in response.get('results', []):
                        res['query'] = query
                        res['source'] = 'tavily'
                        all_results.append(res)
                    time.sleep(1)
                except Exception as e:
                    self.logger.error(f"Tavily SDK搜索失败 ({query}): {e}")
        else:
            # Fallback to Requests
            self.logger.warning("未安装tavily-python，使用Requests Fallback")
            import requests
            for query in queries:
                try:
                    self.logger.info(f"搜索 (API): {query}")
                    payload = {
                        "api_key": self.tavily_api_key,
                        "query": query,
                        "search_depth": "advanced",
                        "max_results": 10
                    }
                    response = requests.post("https://api.tavily.com/search", json=payload, timeout=30)
                    response.raise_for_status()
                    data = response.json()
                    
                    for res in data.get('results', []):
                        res['query'] = query
                        res['source'] = 'tavily'
                        all_results.append(res)
                    time.sleep(1)
                except Exception as e:
                    self.logger.error(f"Tavily API搜索失败 ({query}): {e}")
                
        return all_results
    
    def _run_playwright_crawl(self, targets: List[str]) -> List[Dict]:
        """执行Playwright爬取"""
        self.logger.info("启动Playwright爬取...")
        
        if not sync_playwright:
            self.logger.warning("未安装 playwright，跳过爬取")
            return []
            
        crawled_data = []
        
        try:
            with sync_playwright() as p:
                # 启动浏览器 (headless=True)
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                )
                
                for target in targets:
                    try:
                        page = context.new_page()
                        self.logger.info(f"爬取目标: {target}")
                        
                        url = self._get_url_for_target(target)
                        if not url:
                            self.logger.warning(f"未知目标: {target}")
                            continue
                            
                        page.goto(url, wait_until="domcontentloaded", timeout=60000)
                        
                        # 等待主要内容加载
                        page.wait_for_timeout(2000)

                        
                        # 简单的提取逻辑 (实际项目中需要根据不同网站定制选择器)
                        # 这里我们获取页面标题和主要文本内容作为简化演示
                        title = page.title()
                        content = page.evaluate("() => document.body.innerText")
                        
                        # 截取前2000字符作为上下文
                        cleaned_content = content[:5000].replace('\n', ' ')
                        
                        crawled_data.append({
                            "source": "playwright",
                            "target": target,
                            "url": url,
                            "title": title,
                            "content_snippet": cleaned_content,
                            "crawled_at": datetime.now().isoformat()
                        })
                        
                        page.close()
                        time.sleep(2)
                        
                    except Exception as e:
                        self.logger.error(f"爬取失败 ({target}): {e}")
                
                browser.close()
                
        except Exception as e:
            self.logger.error(f"Playwright执行出错: {e}")
            
        return crawled_data
    
    def _get_url_for_target(self, target: str) -> str:
        """根据目标名称获取URL映射"""
        target_map = {
            "微博热搜": "https://s.weibo.com/top/summary",
            "知乎热榜": "https://www.zhihu.com/billboard",
            "B站热门": "https://www.bilibili.com/v/popular/all",
            "百度热搜": "https://top.baidu.com/board",
            "抖音热点": "https://www.douyin.com/hot", # 注意抖音可能很难爬
            "36氪": "https://36kr.com/hot-list/catalog"
        }
        
        # 模糊匹配
        for key, url in target_map.items():
            if key in target or target in key:
                return url
                
        return ""
