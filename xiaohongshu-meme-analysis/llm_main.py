"""LLM增强版主入口"""
import os
import sys
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from workflows.llm_orchestrator import LLMOrchestrator


def main():
    """主函数"""
    print("=" * 60)
    print("🤖 全网热梗分析系统 (Agentic Workflow)")
    print("🔥 Tavily搜索 + Playwright爬虫 + DeepSeek深度分析")
    print("=" * 60)
    print()
    
    # 检查环境变量
    deepseek_key = os.getenv('DEEPSEEK_API_KEY')
    tavily_key = os.getenv('TAVILY_API_KEY')
    
    if not deepseek_key:
        print("⚠️  未检测到 DEEPSEEK_API_KEY")
        key_input = input("请输入 DeepSeek API Key: ").strip()
        if key_input:
            os.environ['DEEPSEEK_API_KEY'] = key_input
            
    if not tavily_key:
        print("⚠️  未检测到 TAVILY_API_KEY")
        key_input = input("请输入 Tavily API Key (用于媒体搜索): ").strip()
        if key_input:
            os.environ['TAVILY_API_KEY'] = key_input
            
    # 创建目录
    os.makedirs('data/raw', exist_ok=True)
    os.makedirs('data/processed', exist_ok=True)
    os.makedirs('output', exist_ok=True)
    
    # 获取用户输入
    import sys
    if len(sys.argv) > 1:
        user_input = sys.argv[1]
        print(f"\n使用命令行参数输入: {user_input}")
    else:
        print("\n请输入你想分析的内容：")
        print("示例: '分析2025年全网最火的梗'")
        
        default_query = "分析2025年全网最火的梗"
        try:
            user_input = input(f"> (回车默认: {default_query})\n> ").strip()
        except EOFError:
            user_input = ""
        
        if not user_input:
            user_input = default_query
    
    # 运行工作流
    orchestrator = LLMOrchestrator()
    
    try:
        report_path = orchestrator.run(user_input)
        
        # 询问是否查看报告
        print("\n是否查看报告摘要? (y/n)")
        try:
            choice = input("> ").strip().lower()
            if choice in ['y', 'yes']:
                with open(report_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    print("\n" + "=" * 60)
                    print(content[:2000])
                    if len(content) > 2000:
                        print("\n... (内容较长，请查看完整文件)")
                    print("=" * 60)
        except EOFError:
            print("自动跳过查看报告 (非交互模式)")
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
