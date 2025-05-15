#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
简单的API认证测试脚本，专注于检测API密钥格式和认证方式
"""

import os
import sys
import json
import logging
from dotenv import load_dotenv
import requests

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("auth_test")

def display_api_key_info():
    """显示API密钥信息"""
    # 加载环境变量
    load_dotenv()
    
    # 获取API密钥
    api_key = os.getenv("CLAUDE_API_KEY")
    if not api_key:
        logger.error("未找到CLAUDE_API_KEY环境变量")
        logger.info("请确保您的.env文件中包含：CLAUDE_API_KEY=您的密钥")
        return None
    
    # 打印密钥格式信息
    logger.info(f"API密钥长度: {len(api_key)} 个字符")
    logger.info(f"API密钥前缀: {api_key[:6]}...")
    
    # 检查格式
    if not api_key.startswith("sk-"):
        logger.warning("API密钥格式可能不正确，Claude API密钥通常以'sk-'开头")
    
    if api_key == "your_claude_api_key_here" or api_key == "你的API密钥":
        logger.error("您正在使用示例API密钥，而不是实际的API密钥")
        logger.info("请在.env文件中用您的真实API密钥替换示例值")
        return None
    
    return api_key

def try_direct_api_request(api_key):
    """使用直接HTTP请求测试API认证"""
    logger.info("正在使用直接HTTP请求测试API认证...")
    
    url = "https://api.anthropic.com/v1/messages"
    
    # 设置请求头
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    
    # 简单的消息请求
    data = {
        "model": "claude-3-7-sonnet-20240229",
        "max_tokens": 10,
        "messages": [
            {"role": "user", "content": "Just say 'Hello' and nothing else."}
        ]
    }
    
    try:
        logger.info("发送API请求...")
        response = requests.post(url, headers=headers, json=data)
        
        # 输出响应信息
        logger.info(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            logger.info("API认证成功！")
            result = response.json()
            logger.info(f"API响应: {result.get('content', [{}])[0].get('text', '')}")
            return True, None
        else:
            error_data = response.json()
            logger.error(f"API请求失败: {json.dumps(error_data, indent=2)}")
            
            # 检查特定错误类型
            error_type = error_data.get("error", {}).get("type", "")
            error_message = error_data.get("error", {}).get("message", "")
            
            if error_type == "forbidden":
                logger.error("认证错误: 403 Forbidden (禁止访问)")
                logger.info("可能原因: API密钥无效、过期或没有足够权限")
            elif error_type == "authentication_error":
                logger.error("认证错误: 身份验证失败")
                logger.info("可能原因: API密钥格式不正确或完全错误")
            
            return False, error_data
    
    except Exception as e:
        logger.exception(f"请求过程中出错: {str(e)}")
        return False, str(e)

def main():
    """主函数"""
    logger.info("===== Claude API 认证测试 =====")
    
    # 显示API密钥信息
    api_key = display_api_key_info()
    if not api_key:
        return 1
    
    # 测试API认证
    success, error_data = try_direct_api_request(api_key)
    
    if success:
        logger.info("\n===== 测试结果 =====")
        logger.info("认证成功! 您的API密钥可以正常使用")
        logger.info("您可以继续使用项目中的其他功能")
    else:
        logger.info("\n===== 测试结果 =====")
        logger.info("认证失败! 请检查以下可能的问题:")
        logger.info("1. API密钥是否正确")
        logger.info("2. API密钥是否已激活")
        logger.info("3. 您的账户是否有效")
        logger.info("4. 网络环境是否可以访问Anthropic API")
        logger.info("5. 检查.env文件格式是否正确")
        
        logger.info("\n尝试以下解决方法:")
        logger.info("1. 登录Anthropic控制台重新生成API密钥")
        logger.info("2. 确保.env文件格式为: CLAUDE_API_KEY=sk-your_real_key_here")
        logger.info("3. 如果使用代理，尝试直接连接或更换代理")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main()) 