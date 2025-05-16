#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
OpenRouter账户管理工具
用于查询OpenRouter账户信息、配额使用情况、可用模型、费用等
"""

import os
import sys
import json
import time
import logging
import argparse
import requests
from tabulate import tabulate
from dotenv import load_dotenv

# 添加父目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.openrouter_api import OpenRouterAPI

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("openrouter_account")

class OpenRouterAccount:
    """OpenRouter账户管理类"""
    
    def __init__(self, api_key=None):
        """初始化账户管理器"""
        self.api_key = api_key
        if not self.api_key:
            # 尝试从环境变量获取API密钥
            self.api_key = os.getenv("OPENROUTER_API_KEY")
            
        if not self.api_key:
            raise ValueError("未提供API密钥，请设置环境变量OPENROUTER_API_KEY或在初始化时提供api_key参数")
        
        # API端点
        self.base_url = "https://openrouter.ai/api/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def get_models(self):
        """获取可用模型列表"""
        logger.info("获取可用模型列表...")
        
        try:
            response = requests.get(
                f"{self.base_url}/models",
                headers=self.headers
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("data", [])
            else:
                logger.error(f"获取模型列表失败，状态码: {response.status_code}")
                logger.error(f"错误详情: {response.text}")
                return []
                
        except Exception as e:
            logger.exception(f"获取模型列表时出错: {str(e)}")
            return []
    
    def get_credits(self):
        """获取账户余额信息"""
        logger.info("获取账户余额信息...")
        
        try:
            # OpenRouter API没有直接获取余额的端点，这里使用一个模拟示例
            # 实际上，余额信息通常显示在OpenRouter控制台
            logger.warning("OpenRouter API目前不支持通过API直接查询账户余额")
            logger.info("请访问 https://openrouter.ai/account 查看您的账户余额")
            
            return {
                "credits": "unknown",
                "message": "请访问OpenRouter控制台查看余额信息"
            }
                
        except Exception as e:
            logger.exception(f"获取账户余额时出错: {str(e)}")
            return {"error": str(e)}
    
    def get_usage(self, days=30):
        """获取使用情况（模拟，OpenRouter当前不支持）"""
        logger.info(f"获取最近 {days} 天的使用情况...")
        
        try:
            # 这是模拟示例，OpenRouter目前没有提供API来获取使用情况
            logger.warning("OpenRouter API目前不支持通过API直接查询使用情况")
            logger.info("请访问 https://openrouter.ai/account 查看您的使用情况")
            
            return {
                "usage": "unknown",
                "message": "请访问OpenRouter控制台查看使用情况"
            }
                
        except Exception as e:
            logger.exception(f"获取使用情况时出错: {str(e)}")
            return {"error": str(e)}
    
    def test_connection(self):
        """测试API连接"""
        logger.info("测试API连接...")
        
        try:
            response = requests.get(
                f"{self.base_url}/models",
                headers=self.headers
            )
            
            if response.status_code == 200:
                logger.info("API连接成功!")
                return True
            else:
                logger.error(f"API连接失败，状态码: {response.status_code}")
                logger.error(f"错误详情: {response.text}")
                return False
                
        except Exception as e:
            logger.exception(f"测试API连接时出错: {str(e)}")
            return False

def format_model_list(models):
    """格式化模型列表为表格显示"""
    if not models:
        return "未找到可用模型"
    
    # 准备表格数据
    table_data = []
    for model in models:
        context_length = model.get("context_length", "未知")
        pricing = model.get("pricing", {})
        input_price = pricing.get("input", 0) * 1000  # 转换为每1000个token的价格
        output_price = pricing.get("output", 0) * 1000
        
        table_data.append([
            model.get("id", "未知"),
            model.get("name", "未知"),
            context_length,
            f"${input_price:.6f}/1K",
            f"${output_price:.6f}/1K",
        ])
    
    # 排序：先免费模型，再按价格
    def sort_key(item):
        # 如果输出价格为0，排在前面（免费模型）
        output_price = float(item[4].replace("$", "").replace("/1K", ""))
        if output_price == 0:
            return (0, item[0])  # 免费模型按ID排序
        return (1, output_price, item[0])  # 付费模型按价格和ID排序
    
    table_data.sort(key=sort_key)
    
    # 添加表头
    headers = ["模型ID", "模型名称", "最大Context", "输入价格", "输出价格"]
    
    # 生成表格
    return tabulate(table_data, headers=headers, tablefmt="grid")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="OpenRouter账户管理工具")
    parser.add_argument("--models", action="store_true", help="获取可用模型列表")
    parser.add_argument("--credits", action="store_true", help="获取账户余额信息")
    parser.add_argument("--usage", action="store_true", help="获取使用情况")
    parser.add_argument("--test", action="store_true", help="测试API连接")
    parser.add_argument("--all", action="store_true", help="显示所有信息")
    
    args = parser.parse_args()
    
    # 如果没有提供参数，显示帮助信息
    if not any(vars(args).values()):
        parser.print_help()
        return 0
    
    # 加载环境变量
    load_dotenv()
    
    try:
        # 创建账户管理器
        account = OpenRouterAccount()
        
        # 执行请求的操作
        if args.all or args.test:
            test_result = account.test_connection()
            print(f"\nAPI连接测试: {'成功' if test_result else '失败'}")
            
        if args.all or args.models:
            models = account.get_models()
            print("\n=== 可用模型列表 ===")
            print(format_model_list(models))
            
        if args.all or args.credits:
            credits = account.get_credits()
            print("\n=== 账户余额 ===")
            if "error" in credits:
                print(f"获取余额失败: {credits['error']}")
            else:
                print(credits["message"])
            
        if args.all or args.usage:
            usage = account.get_usage()
            print("\n=== 使用情况 ===")
            if "error" in usage:
                print(f"获取使用情况失败: {usage['error']}")
            else:
                print(usage["message"])
        
        return 0
        
    except Exception as e:
        logger.exception(f"程序执行出错: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 