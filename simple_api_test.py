#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
最简单的Claude API测试脚本，仅使用requests库
"""

import os
import sys
import json
import logging
import requests
from dotenv import load_dotenv

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("simple_api_test")

def main():
    """主函数"""
    # 加载环境变量
    load_dotenv()
    
    # 获取API密钥
    api_key = os.getenv("CLAUDE_API_KEY")
    if not api_key:
        logger.error("未找到API密钥，请设置CLAUDE_API_KEY环境变量")
        return 1
    
    # 打印密钥前4位和后4位（出于安全考虑只显示部分）
    masked_key = api_key[:4] + "*" * (len(api_key) - 8) + api_key[-4:]
    logger.info(f"使用API密钥: {masked_key}")
    
    # 请求头
    headers = {
        "x-api-key": api_key,
        "content-type": "application/json",
        "anthropic-version": "2023-06-01"
    }
    
    # 测试不同的模型
    models = [
        "claude-3-opus-20240229",
        "claude-3-5-haiku-20241022",
        "claude-3-haiku-20240307",
        "claude-3-7-sonnet-20250219"
    ]
    
    for model in models:
        # 创建一个简单请求
        data = {
            "model": model,
            "max_tokens": 200,  # 足够用于简单测试
            "messages": [
                {"role": "user", "content": "Say hello and mention which model you are."}
            ]
        }
        
        try:
            logger.info(f"测试模型: {model}...")
            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=data
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"成功! 模型 {model} 响应: {result.get('content', [{}])[0].get('text', '')}")
            else:
                logger.error(f"错误! 模型 {model} 状态码: {response.status_code}")
                error_data = response.json()
                logger.error(f"错误详情: {json.dumps(error_data, indent=2)}")
        
        except Exception as e:
            logger.exception(f"测试模型 {model} 时出错: {str(e)}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 