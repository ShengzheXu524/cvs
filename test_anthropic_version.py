#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试 anthropic 库版本和 API 连接
"""

import os
import sys
import json
import logging
from dotenv import load_dotenv
import anthropic

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("anthropic_test")

def main():
    """主函数"""
    # 加载环境变量
    load_dotenv()
    
    # 检查版本
    logger.info(f"当前 anthropic 库版本: {anthropic.__version__}")
    
    # 从环境变量获取API密钥
    api_key = os.getenv("CLAUDE_API_KEY")
    if not api_key:
        logger.error("未找到API密钥，请设置CLAUDE_API_KEY环境变量")
        return 1
    
    try:
        # 尝试创建客户端
        logger.info("尝试创建 Anthropic 客户端...")
        client = anthropic.Anthropic(api_key=api_key)
        logger.info("客户端创建成功!")
        
        # 尝试简单的API调用
        logger.info("尝试发送一个简单的API请求...")
        response = client.messages.create(
            model="claude-3-7-sonnet-20240229",
            max_tokens=100,
            messages=[
                {"role": "user", "content": "Hello! Please respond in just one sentence."}
            ]
        )
        
        logger.info(f"API调用成功! 响应: {response.content[0].text}")
        return 0
        
    except Exception as e:
        logger.exception(f"测试失败: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 