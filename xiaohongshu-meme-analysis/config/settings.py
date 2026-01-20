"""配置管理模块"""
import os
from typing import Dict, Any


class Config:
    """配置类"""
    
    # 默认配置
    DEFAULT_CONFIG = {
        'crawler': {
            'max_posts_per_month': 1000,
            'timeout': 30,
            'retry': 3
        },
        'analyzer': {
            'top_n_memes': 10,
            'min_engagement_score': 100
        },
        'output': {
            'format': 'markdown',
            'include_visualizations': True
        }
    }
    
    @classmethod
    def load(cls, config_path: str = None) -> Dict[str, Any]:
        """加载配置"""
        config = cls.DEFAULT_CONFIG.copy()
        
        # 从环境变量加载
        if os.getenv('MAX_POSTS'):
            config['crawler']['max_posts_per_month'] = int(os.getenv('MAX_POSTS'))
        
        # TODO: 从配置文件加载
        
        return config
