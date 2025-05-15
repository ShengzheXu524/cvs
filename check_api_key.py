#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
检查API密钥问题，显示完整的错误信息和解决方案
"""

import os
import sys
import logging
import json
import requests
from dotenv import load_dotenv

# 导入模型配置模块，但首先要确保src目录在sys.path中
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    from src.model_config import get_model
except ImportError:
    # 如果无法导入，使用默认模型名称
    def get_model(_=None):
        return "claude-3-7-sonnet-20250219"

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("api_key_check")

def check_env_file():
    """检查.env文件是否存在并检查内容"""
    logger.info("正在检查.env文件...")
    
    if not os.path.exists(".env"):
        logger.error("未找到.env文件，请在项目根目录创建此文件")
        logger.info("示例内容: CLAUDE_API_KEY=sk-your_actual_key_here")
        return False, None
    
    # 加载环境变量
    load_dotenv()
    
    # 获取API密钥
    api_key = os.getenv("CLAUDE_API_KEY")
    if not api_key:
        logger.error("在.env文件中未找到CLAUDE_API_KEY环境变量")
        return False, None
    
    # 检查密钥格式
    if not api_key.startswith("sk-"):
        logger.warning("API密钥格式可能不正确，Claude API密钥通常以'sk-'开头")
    
    # 隐藏部分密钥进行打印
    masked_key = api_key[:5] + "*" * (len(api_key) - 8) + api_key[-3:]
    logger.info(f"找到API密钥: {masked_key}")
    
    return True, api_key

def test_direct_api_request(api_key):
    """使用requests库直接测试API请求，绕过anthropic库"""
    logger.info("正在使用requests库直接测试API连接...")
    
    # Claude API的Base URL
    url = "https://api.anthropic.com/v1/messages"
    
    # 请求头
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    
    # 非常简单的请求体
    payload = {
        "model": get_model("default"),  # 使用模型配置模块获取默认模型
        "max_tokens": 100,  # 使用较小的值，足够简单测试
        "messages": [
            {"role": "user", "content": "Hello! Please respond with 'API key is working' and nothing else."}
        ]
    }
    
    logger.info(f"使用模型: {payload['model']}")
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            # 成功
            result = response.json()
            content = result.get("content", [{}])[0].get("text", "")
            logger.info(f"API请求成功! 响应: {content}")
            return True, None
        else:
            # 错误
            error_data = response.json()
            error_message = json.dumps(error_data, indent=2)
            logger.error(f"API请求失败，状态码: {response.status_code}, 错误信息: {error_message}")
            return False, error_data
    
    except Exception as e:
        logger.exception(f"请求过程中出错: {str(e)}")
        return False, str(e)

def print_troubleshooting_guide(error_data=None):
    """打印问题排查指南"""
    logger.info("\n" + "="*50)
    logger.info("API密钥问题排查指南")
    logger.info("="*50)
    
    if error_data and isinstance(error_data, dict):
        error_type = error_data.get("error", {}).get("type", "")
        error_message = error_data.get("error", {}).get("message", "")
        
        if error_type == "forbidden":
            logger.info("遇到403 Forbidden错误，可能的原因:")
            logger.info("1. API密钥无效或过期")
            logger.info("2. API密钥没有足够的权限")
            logger.info("3. 账户可能已被暂停或有计费问题")
        
        elif error_type == "authentication_error":
            logger.info("遇到身份验证错误，可能的原因:")
            logger.info("1. API密钥格式不正确")
            logger.info("2. API密钥完全错误")
        
        elif error_type == "rate_limit_error":
            logger.info("遇到速率限制错误，可能的原因:")
            logger.info("1. 短时间内发送了太多请求")
            logger.info("2. 超出了API使用配额")
        
        else:
            logger.info(f"遇到错误类型: {error_type}, 错误消息: {error_message}")
    
    logger.info("\n解决方法:")
    logger.info("1. 登录Anthropic控制台检查API密钥状态: https://console.anthropic.com/")
    logger.info("2. 重新生成一个新的API密钥")
    logger.info("3. 更新.env文件，确保格式为: CLAUDE_API_KEY=your_new_api_key")
    logger.info("4. 确保没有代理设置影响API请求")
    logger.info("5. 检查您的账户计费状态")
    logger.info("6. 如果使用VPN，尝试关闭或更换服务器")
    logger.info("7. 尝试使用备用服务器地址（如有提供）")
    
    logger.info("\n检查.env文件的内容:")
    logger.info("1. 确保.env文件在项目根目录")
    logger.info("2. 确保格式正确，没有多余的引号、空格或换行符")
    logger.info("3. 确保CLAUDE_API_KEY设置正确")
    logger.info("示例: CLAUDE_API_KEY=sk-your_actual_key_here")

def main():
    """主函数"""
    logger.info("开始检查API密钥问题...")
    
    # 创建.env.example文件（如果不存在）
    env_example_file = ".env.example"
    if not os.path.exists(env_example_file):
        try:
            with open(env_example_file, "w", encoding="utf-8") as f:
                f.write("# Claude API配置\n")
                f.write("# 复制此文件为.env并替换下面的值为你的真实API密钥\n")
                f.write("CLAUDE_API_KEY=sk-your_claude_api_key_here\n\n")
                f.write("# 注意事项:\n")
                f.write("# 1. API密钥通常以'sk-'开头\n")
                f.write("# 2. 请勿在密钥前后添加引号或空格\n")
                f.write("# 3. 确保.env文件已添加到.gitignore中，避免将密钥提交到版本控制系统\n")
                f.write("# 4. 如果遇到API认证问题，请运行 python check_api_key.py 进行诊断\n")
            logger.info(f"已创建 {env_example_file} 文件，作为API密钥配置模板")
        except Exception as e:
            logger.warning(f"创建 {env_example_file} 文件时出错: {str(e)}")
    
    # 检查.env文件
    env_exists, api_key = check_env_file()
    if not env_exists or not api_key:
        print_troubleshooting_guide()
        return 1
    
    # 直接测试API
    success, error_data = test_direct_api_request(api_key)
    
    if not success:
        print_troubleshooting_guide(error_data)
        return 1
    
    logger.info("API密钥验证成功! 您的密钥可以正常使用Claude API。")
    return 0

if __name__ == "__main__":
    sys.exit(main()) 