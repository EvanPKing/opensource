"""测试Planner Agent"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from agents.planner_agent import PlannerAgent


def test_planner_agent():
    """测试规划Agent"""
    agent = PlannerAgent()
    
    # 测试用例1
    result = agent.execute("分析2025年1月到12月小红书热梗")
    
    assert 'time_range' in result
    assert 'crawl_plan' in result
    assert 'analysis_plan' in result
    assert result['time_range']['start'] == '2025-01'
    assert result['time_range']['end'] == '2025-12'
    
    print("✓ 测试通过: PlannerAgent")


if __name__ == '__main__':
    test_planner_agent()
