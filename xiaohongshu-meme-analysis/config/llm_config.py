"""LLM配置文件"""
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# DeepSeek API配置
DEEPSEEK_CONFIG = {
    'api_key': os.getenv('DEEPSEEK_API_KEY', ''),
    'base_url': 'https://api.deepseek.com',
    'model': 'deepseek-chat',  # 或 deepseek-coder
    'temperature': 0.7,
    'max_tokens': 4000,
}

# Web Search配置
WEB_SEARCH_CONFIG = {
    'enabled': True,
    'max_results': 20,  # 每次搜索最多返回结果数
    'search_depth': 'deep',  # 'quick' or 'deep'
}

# Agent配置
AGENT_CONFIG = {
    'planner': {
        'model': 'deepseek-chat',
        'temperature': 0.3,  # 规划需要更精确
        'max_tokens': 2000,
    },
    'crawler': {
        'model': 'deepseek-chat',
        'temperature': 0.5,
        'max_tokens': 4000,
        'use_web_search': True,
        'search_keywords': [
            '2025年热梗',
            '网络流行语',
            '表情包文化',
            'meme趋势',
            '年度热词'
        ]
    },
    'analyzer': {
        'model': 'deepseek-chat',
        'temperature': 0.7,
        'max_tokens': 8000,
    },
    'writer': {
        'model': 'deepseek-chat',
        'temperature': 0.8,  # 写作需要更多创造性
        'max_tokens': 8000,
    }
}

# 数据源配置（全网搜索）
DATA_SOURCES = {
    'platforms': [
        '小红书',
        '微博',
        '知乎',
        'B站',
        '抖音',
        '豆瓣',
        '贴吧'
    ],
    'content_types': [
        '热梗',
        '网络流行语',
        '表情包',
        'meme',
        '网络用语',
        '热词',
        '流行文化'
    ]
}
