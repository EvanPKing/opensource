# 🎨 小红书热梗分析系统

基于多智能体（Multi-Agent）架构的小红书表情包和热梗分析系统。

## 📋 项目简介

这是一个自动化的数据分析系统，能够：
- 📊 爬取小红书平台的表情包和热梗数据
- 🧹 清洗和标准化原始数据
- 📈 分析热门趋势和用户情感
- 📝 自动生成可视化分析报告

## 🏗️ 系统架构

系统采用多智能体架构，包含5个专业Agent：

```
用户输入 → Planner → Crawler → Cleaner → Analyzer → Writer → 报告输出
```

### Agent职责

1. **PlannerAgent** 📋
   - 解析用户查询
   - 生成爬虫和分析计划

2. **CrawlerAgent** 🕷️
   - 执行数据爬取
   - 输出原始数据 (raw_data.json)

3. **CleanerAgent** 🧹
   - 数据清洗和标准化
   - 输出清洗数据 (clean_data.json)

4. **AnalyzerAgent** 📊
   - 数据聚类和趋势分析
   - 提取热门梗和情感分析
   - 输出洞察报告 (insights.json)

5. **WriterAgent** 📝
   - 生成Markdown格式报告
   - 输出最终报告 (report_*.md)

## 🚀 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行分析

```bash
python main.py
```

或使用命令行参数：

```bash
python main.py "分析2025年1月到12月小红书热梗"
```

或直接运行工作流：

```bash
python workflows/orchestrator.py "分析2025年1-3月热门表情包"
```

## 📁 项目结构

```
xiaohongshu-meme-analysis/
├── agents/                 # Agent模块
│   ├── base_agent.py      # 基础Agent类
│   ├── planner_agent.py   # 规划Agent
│   ├── crawler_agent.py   # 爬虫Agent
│   ├── cleaner_agent.py   # 清洗Agent
│   ├── analyzer_agent.py  # 分析Agent
│   └── writer_agent.py    # 写作Agent
├── workflows/             # 工作流
│   └── orchestrator.py    # 工作流协调器
├── data/                  # 数据目录
│   ├── raw/              # 原始数据
│   └── processed/        # 处理后数据
├── output/               # 输出报告
├── config/               # 配置文件
├── utils/                # 工具函数
├── tests/                # 测试文件
├── notebooks/            # Jupyter notebooks
├── docs/                 # 文档
├── main.py              # 主入口
└── requirements.txt     # 依赖列表
```

## 💡 使用示例

### 示例1: 分析年度热梗

```python
from workflows.orchestrator import WorkflowOrchestrator

orchestrator = WorkflowOrchestrator()
report = orchestrator.run("分析2025年1月到12月小红书热梗")
print(f"报告已生成: {report}")
```

### 示例2: 自定义配置

```python
config = {
    'crawler': {
        'max_posts': 1000,
        'timeout': 30
    },
    'analyzer': {
        'top_n_memes': 20
    }
}

orchestrator = WorkflowOrchestrator(config)
report = orchestrator.run("分析搞笑表情包趋势")
```

## 📊 输出报告内容

生成的报告包含：
- 📈 数据统计概览
- 🔥 热门梗 Top 10
- 🎯 梗文化聚类分析
- 📅 时间趋势分析
- 💭 用户情感分析
- 🎯 关键洞察总结

## 🛠️ 扩展开发

### 添加新的Agent

1. 在 `agents/` 目录创建新文件
2. 继承 `BaseAgent` 类
3. 实现 `execute()` 方法
4. 在 `orchestrator.py` 中集成

示例：

```python
from agents.base_agent import BaseAgent

class MyCustomAgent(BaseAgent):
    def __init__(self, config=None):
        super().__init__("MyCustomAgent", config)
    
    def execute(self, input_data):
        # 实现自定义逻辑
        return output_data
```

### 自定义工作流

修改 `workflows/orchestrator.py` 中的 `run()` 方法来调整执行流程。

## ⚠️ 注意事项

1. **爬虫合规**: 请遵守小红书的robots.txt和使用条款
2. **API限制**: 注意API调用频率限制
3. **数据隐私**: 不要爬取和存储用户隐私数据
4. **商业使用**: 商业使用前请获得相应授权

## 🔧 配置说明

创建 `.env` 文件配置环境变量：

```env
# API配置
XIAOHONGSHU_API_KEY=your_api_key
XIAOHONGSHU_API_SECRET=your_api_secret

# 爬虫配置
MAX_RETRY=3
REQUEST_TIMEOUT=30

# LLM配置 (可选)
OPENAI_API_KEY=your_openai_key
```

## 🧪 测试

运行测试：

```bash
pytest tests/
```

运行覆盖率测试：

```bash
pytest --cov=agents --cov=workflows tests/
```

## 📚 相关文档

- [小红书API文档](https://www.xiaohongshu.com/dev)
- [Agent架构设计](docs/architecture.md)
- [数据结构说明](docs/data_schema.md)

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License

## 👥 作者

- 开发者: Mr 派
- 邮箱: shenghaow95@gmail.com

## 🙏 致谢

感谢所有贡献者和开源社区的支持！

---

**注意**: 这是一个示例项目，实际使用时需要实现真实的爬虫逻辑和数据处理流程。
