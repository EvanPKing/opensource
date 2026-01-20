"""工具函数模块"""

def format_number(num: int) -> str:
    """格式化数字，添加千位分隔符"""
    return f"{num:,}"


def truncate_text(text: str, max_length: int = 100) -> str:
    """截断文本到指定长度"""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."


def extract_hashtags(text: str) -> list:
    """从文本中提取话题标签"""
    import re
    return re.findall(r'#(\w+)', text)


def calculate_engagement_score(likes: int, comments: int, shares: int = 0) -> int:
    """计算互动分数"""
    return likes + comments * 2 + shares * 3
