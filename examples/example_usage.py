#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
示例使用脚本，演示如何使用考研英语真题处理工具。
"""

import os
import sys
import argparse
from dotenv import load_dotenv

# 添加父目录到路径，以便导入src模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入工具模块
from src.main import process_single_file, process_batch
from src.utils import setup_logging

def main():
    """示例脚本主入口。"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="考研英语真题处理工具示例")
    
    parser.add_argument("--input", required=True, help="输入的docx文件路径或目录")
    parser.add_argument("--output", required=True, help="输出的CSV文件路径或目录")
    parser.add_argument("--batch", action="store_true", help="批处理模式")
    parser.add_argument("--api_key", help="OpenRouter API密钥（如不提供将从环境变量获取）")
    parser.add_argument("--model", help="要使用的模型，如'default'或'deepseek/deepseek-r1:free'")
    parser.add_argument("--debug", action="store_true", help="启用调试模式")
    
    args = parser.parse_args()
    
    # 设置日志
    logger = setup_logging("info")
    logger.info("开始执行示例脚本")
    
    # 加载环境变量
    load_dotenv()
    
    # 获取API密钥
    api_key = args.api_key or os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        logger.error("未提供OpenRouter API密钥。请通过--api_key参数提供或设置OPENROUTER_API_KEY环境变量。")
        return 1
    
    # 执行处理
    if args.batch:
        # 批处理模式
        success_count, failure_count = process_batch(
            args.input, args.output, api_key, args.model, args.debug
        )
        logger.info(f"批处理完成 - 成功: {success_count}, 失败: {failure_count}")
    else:
        # 单文件模式
        success = process_single_file(
            args.input, args.output, api_key, args.model, args.debug
        )
        if success:
            logger.info("文件处理成功")
        else:
            logger.error("文件处理失败")
    
    logger.info("示例脚本执行完毕")
    return 0

if __name__ == "__main__":
    sys.exit(main()) 