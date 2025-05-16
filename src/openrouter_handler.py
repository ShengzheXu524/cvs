#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
OpenRouter API 处理模块
负责与OpenRouter API交互，发送请求并获取响应
"""

import os
import json
import time
import logging
import re
import requests
from dotenv import load_dotenv
from src.model_config import get_model, get_model_max_tokens

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("openrouter_handler")

# 加载环境变量
load_dotenv()

class OpenRouterHandler:
    """OpenRouter API处理器，负责发送请求和获取响应"""
    
    def __init__(self, model=None, api_key=None):
        """
        初始化OpenRouter API处理器
        
        Args:
            model: 模型名称，如果为None则使用环境变量或默认模型
            api_key: API密钥，如果为None则使用环境变量
        """
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("缺少OpenRouter API密钥，请在.env文件中设置OPENROUTER_API_KEY")
        
        # 获取模型名称（如果未指定，将使用环境变量或默认模型）
        self.model = model or get_model()
        logger.info(f"使用模型: {self.model}")
        
        # API请求URL和头信息
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": os.getenv("APP_URL", "https://github.com/yourusername/your-repo"),
            # 使用ASCII编码的应用名称，避免Unicode编码问题
            "X-Title": "CET-Extractor"
        }
    
    def get_structured_data(self, prompt, max_tokens=4096, temperature=0.1, output_dir="test_results"):
        """
        获取结构化数据
        
        Args:
            prompt: 提示词
            max_tokens: 最大生成token数
            temperature: 生成温度，越低越确定性
            output_dir: 输出目录，用于保存调试信息
        
        Returns:
            dict: 解析后的结构化数据
        """
        logger.info(f"发送API请求获取结构化数据，模型: {self.model}，最大tokens: {max_tokens}")
        
        # 构建请求数据
        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "你是一个专业的考研英语真题内容提取助手，擅长将考研英语真题文档解析为结构化的JSON数据。"},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
            "response_format": {"type": "json_object"}
        }
        
        # 发送请求
        try:
            response = requests.post(self.api_url, headers=self.headers, json=data)
            response.raise_for_status()
            
            # 解析响应
            response_data = response.json()
            
            if "choices" in response_data and len(response_data["choices"]) > 0:
                # 提取回答内容
                content = response_data["choices"][0]["message"]["content"]
                
                # 为调试目的保存原始内容到指定目录
                debug_dir = os.path.join(output_dir, "debug")
                os.makedirs(debug_dir, exist_ok=True)
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                with open(os.path.join(debug_dir, f"raw_response_{timestamp}.txt"), "w", encoding="utf-8") as f:
                    f.write(content)
                
                # 解析JSON
                try:
                    # 尝试直接解析
                    result = json.loads(content)
                    logger.info("成功解析API响应为JSON")
                    
                    # 添加原始响应用于调试
                    result["raw_response"] = content
                    
                    # 添加模型信息
                    result["model"] = self.model
                    
                    return result
                except json.JSONDecodeError:
                    # 尝试从内容中提取JSON部分
                    logger.warning("无法直接解析为JSON，尝试提取JSON部分")
                    extracted_json = self._extract_json_from_text(content)
                    
                    if extracted_json:
                        try:
                            result = json.loads(extracted_json)
                            
                            # 添加原始响应用于调试
                            result["raw_response"] = content
                            
                            # 添加模型信息
                            result["model"] = self.model
                            
                            logger.info("从内容中提取JSON部分成功")
                            return result
                        except json.JSONDecodeError:
                            logger.warning("提取的JSON部分仍然无法解析，尝试修复格式")
                            fixed_json = self._fix_json_format(extracted_json)
                            if fixed_json:
                                result = json.loads(fixed_json)
                                
                                # 添加原始响应用于调试
                                result["raw_response"] = content
                                
                                # 添加模型信息
                                result["model"] = self.model
                                
                                logger.info("成功修复并解析JSON")
                                return result
                            else:
                                # 最后尝试构建一个简单的JSON格式
                                logger.warning("无法修复JSON，创建空结构")
                                result = {
                                    "model": self.model,
                                    "raw_response": content,
                                    "metadata": {
                                        "year": "2024",
                                        "exam_type": "英语（一）"
                                    },
                                    "sections": {},
                                    "questions": []
                                }
                                return result
                    else:
                        # 如果无法提取JSON，创建一个基本结构
                        logger.warning("无法从响应中提取JSON，创建基本结构")
                        result = {
                            "model": self.model,
                            "raw_response": content,
                            "metadata": {
                                "year": "2024",
                                "exam_type": "英语（一）"
                            },
                            "sections": {},
                            "questions": []
                        }
                        return result
            else:
                logger.error("API响应中没有选择项")
                raise ValueError("API响应格式不正确")
        
        except requests.exceptions.RequestException as e:
            logger.error(f"API请求失败: {str(e)}")
            raise
    
    def _extract_json_from_text(self, text):
        """
        从文本中提取JSON部分
        
        Args:
            text: 原始文本
        
        Returns:
            str: 提取的JSON文本，如果没有找到则返回None
        """
        # 查找JSON代码块，格式为```json ... ```
        start_marker = "```json"
        end_marker = "```"
        
        if start_marker in text:
            start_idx = text.find(start_marker) + len(start_marker)
            end_idx = text.find(end_marker, start_idx)
            
            if end_idx != -1:
                # 提取JSON文本
                json_text = text[start_idx:end_idx].strip()
                return json_text
        
        # 如果没有找到代码块标记，尝试查找可能的大括号匹配
        start_brace = text.find('{')
        if start_brace != -1:
            # 尝试查找匹配的闭合括号
            brace_count = 1
            for i in range(start_brace + 1, len(text)):
                if text[i] == '{':
                    brace_count += 1
                elif text[i] == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        # 提取JSON文本
                        return text[start_brace:i+1]
        
        return None
    
    def _fix_json_format(self, json_text):
        """
        修复JSON格式问题
        
        Args:
            json_text: 待修复的JSON文本
        
        Returns:
            str: 修复后的JSON文本，如果无法修复则返回None
        """
        try:
            # 处理阅读理解题中可能出现的方括号格式问题
            # 将 A] 格式转换为 "A]" 格式，确保在JSON中正确解析
            fixed_text = re.sub(r'("correct_answer":\s*)"([A-G])(\].*?")', r'\1"\2\3', json_text)
            
            # 替换未转义的双引号
            fixed_text = re.sub(r'(?<!\\)"(?=.*?[^\\]")', r'\"', fixed_text)
            
            # 尝试修复缺少的引号
            fixed_text = re.sub(r'([{,])\s*(\w+)\s*:', r'\1"\2":', fixed_text)
            
            # 尝试修复逗号后面直接是闭合括号的情况
            fixed_text = re.sub(r',\s*}', '}', fixed_text)
            fixed_text = re.sub(r',\s*]', ']', fixed_text)
            
            # 尝试解析修复后的文本
            json.loads(fixed_text)
            return fixed_text
        except json.JSONDecodeError:
            # 如果仍然不能解析，尝试更激进的修复
            try:
                # 特殊处理阅读理解题中的选项格式
                # 可能是因为带方括号的选项格式导致解析错误
                pattern = r'"options":\s*"(.+?)",\s*"correct_answer":\s*"(.+?)",\s*"distractors":\s*"(.+?)"'
                if re.search(pattern, fixed_text):
                    fixed_text = re.sub(pattern, lambda m: self._fix_options_format(m), fixed_text)
                
                # 再次尝试解析
                json.loads(fixed_text)
                return fixed_text
            except:
                # 如果仍然不能解析，返回None
                return None
                
    def _fix_options_format(self, match):
        """
        修复选项格式，特别是处理带方括号的选项
        
        Args:
            match: 正则表达式匹配对象
        
        Returns:
            str: 修复后的字符串
        """
        options = match.group(1).replace('\\n', '\\\\n').replace('[', '\\[')
        correct = match.group(2).replace('[', '\\[')
        distractors = match.group(3).replace('\\n', '\\\\n').replace('[', '\\[')
        
        return f'"options": "{options}", "correct_answer": "{correct}", "distractors": "{distractors}"' 