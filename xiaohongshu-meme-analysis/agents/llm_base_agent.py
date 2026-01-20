"""LLM增强的基础Agent类"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import json
import os
from datetime import datetime


class LLMBaseAgent(ABC):
    """所有LLM Agent的基类"""
    
    def __init__(self, name: str, config: Dict[str, Any] = None):
        self.name = name
        self.config = config or {}
        self.logger = self._setup_logger()
        self.client = self._setup_llm_client()
    
    def _setup_logger(self):
        """设置日志"""
        import logging
        logger = logging.getLogger(self.name)
        logger.setLevel(logging.INFO)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                f'[{self.name}] %(asctime)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        return logger
    
    def _setup_llm_client(self):
        """设置LLM客户端"""
        api_key = os.getenv('DEEPSEEK_API_KEY')
        if not api_key:
            self.logger.warning("未配置DEEPSEEK_API_KEY，部分功能将不可用")
            return None

        # 优先使用requests，因为在当前环境中OpenAI SDK可能不稳定
        try:
            import requests
            self.logger.info("✓ DeepSeek客户端初始化成功 (Requests Mode - Forced)")
            return "requests"
        except ImportError:
            pass # Fallback to OpenAI SDK logic if requests is missing (unlikely)

        try:
            from openai import OpenAI
            client = OpenAI(
                api_key=api_key,
                base_url="https://api.deepseek.com"
            )
            self.logger.info("✓ DeepSeek客户端初始化成功 (OpenAI SDK)")
            return client
            
        except ImportError:
            self.logger.error("未安装openai或requests库，LLM功能不可用")
            return None
        except Exception as e:
            self.logger.error(f"LLM客户端初始化失败: {e}")
            return None
    
    def call_llm(
        self, 
        messages: list,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        use_web_search: bool = False
    ) -> str:
        """
        调用LLM API
        
        Args:
            messages: 消息列表
            temperature: 温度参数
            max_tokens: 最大token数
            use_web_search: 是否使用联网搜索
            
        Returns:
            LLM返回的文本
        """
        if not self.client:
            self.logger.error("LLM客户端未初始化")
            return ""
        
        temp = temperature or self.config.get('temperature', 0.7)
        tokens = max_tokens or self.config.get('max_tokens', 4000)
        model = self.config.get('model', 'deepseek-chat')
        
        # 使用OpenAI SDK
        if self.client != "requests":
            try:
                request_params = {
                    "model": model,
                    "messages": messages,
                    "temperature": temp,
                    "max_tokens": tokens,
                }
                
                # 如果启用Web Search (DeepSeek API specific)
                # 注意: 标准OpenAI SDK可能需要特殊处理，这里假设透传
                if use_web_search:
                    # DeepSeek目前并不直接支持通过tools参数传递web_search给OpenAI SDK，
                    # 除非是特定的beta接口。通常DeepSeek R1/V3 是纯文本模型。
                    # 如果DeepSeek支持online模型，需要指定model='deepseek-reasoner'等?
                    # 这里暂不处理复杂的tools，保持原样
                    pass

                self.logger.info(f"正在调用LLM (OpenAI SDK)... Token预估: {len(str(messages))/4}")
                response = self.client.chat.completions.create(**request_params)
                self.logger.info("LLM调用成功")
                return response.choices[0].message.content
            except Exception as e:
                self.logger.error(f"LLM调用失败 (OpenAI SDK): {e}")
                return ""
        
        # 使用urllib Fallback (Requests在Windows下处理大Payload可能崩溃)
        else:
            import urllib.request
            import time
            import json
            
            headers = {
                "Authorization": f"Bearer {os.getenv('DEEPSEEK_API_KEY')}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            data = {
                "model": model,
                "messages": messages,
                "temperature": temp,
                "max_tokens": tokens,
                "stream": False
            }
            
            try:
                json_data = json.dumps(data).encode('utf-8')
                print(f"DEBUG: Using urllib fallback. Payload size: {len(json_data)}", flush=True)
                
                retries = 3
                for attempt in range(retries):
                    try:
                        req = urllib.request.Request(
                            "https://api.deepseek.com/chat/completions",
                            data=json_data,
                            headers=headers,
                            method="POST"
                        )
                        
                        # 增加超时时间到300秒
                        with urllib.request.urlopen(req, timeout=300) as response:
                            if response.status == 200:
                                res_body = response.read().decode('utf-8')
                                res_json = json.loads(res_body)
                                content = res_json['choices'][0]['message']['content']
                                print(f"DEBUG: urllib success. Content length: {len(content)}", flush=True)
                                return content
                            else:
                                print(f"DEBUG: urllib status {response.status}", flush=True)
                    except Exception as e:
                        print(f"DEBUG: urllib attempt {attempt+1} failed: {e}", flush=True)
                        if attempt == retries - 1:
                            self.logger.error(f"LLM调用失败 (urllib): {e}")
                            return ""
                        time.sleep(2 * (attempt + 1))
            except Exception as e:
                self.logger.error(f"数据准备失败: {e}")
                return ""
            
            return ""

    def save_output(self, data: Any, file_path: str):
        """保存输出到文件"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            self.logger.info(f"数据已保存: {file_path}")
        except Exception as e:
            self.logger.error(f"保存文件失败: {e}")

    def log_execution(self, action: str, details: Any):
        """记录执行日志"""
        self.logger.info(f"👉 {action}")
        # self.logger.debug(f"Details: {details}")
