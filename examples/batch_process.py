#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
批处理脚本，用于处理多个考研英语真题文档。
"""

import os
import sys
import argparse
import logging
from dotenv import load_dotenv
from pathlib import Path

# 添加父目录到路径，以便导入src模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入工具模块
from src.main import process_batch
from src.utils import setup_logging, ensure_directory_exists

def main():
    """批处理脚本主入口。"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="考研英语真题批量处理工具")
    
    parser.add_argument("--input_dir", required=True, help="输入目录，包含要处理的docx文件")
    parser.add_argument("--output_dir", required=True, help="输出目录，用于保存生成的CSV文件")
    parser.add_argument("--api_key", help="Claude API密钥（如不提供将从环境变量获取）")
    parser.add_argument("--model", default="claude-3-7-sonnet-20240229", help="要使用的Claude模型")
    parser.add_argument("--log", choices=["debug", "info", "warning", "error"], default="info", help="日志级别")
    parser.add_argument("--debug", action="store_true", help="启用调试模式")
    
    args = parser.parse_args()
    
    # 设置日志
    logger = setup_logging(args.log)
    logger.info("开始执行批处理脚本")
    
    # 加载环境变量
    load_dotenv()
    
    # 获取API密钥
    api_key = args.api_key or os.getenv("CLAUDE_API_KEY")
    if not api_key:
        logger.error("未提供Claude API密钥。请通过--api_key参数提供或设置CLAUDE_API_KEY环境变量。")
        return 1
    
    # 确保输入目录存在
    if not os.path.isdir(args.input_dir):
        logger.error(f"输入目录不存在: {args.input_dir}")
        return 1
    
    # 确保输出目录存在
    ensure_directory_exists(args.output_dir)
    
    # 执行批处理
    success_count, failure_count = process_batch(
        args.input_dir,
        args.output_dir,
        api_key,
        args.model,
        args.debug
    )
    
    # 打印处理结果
    logger.info(f"批处理完成")
    logger.info(f"成功处理: {success_count} 个文件")
    logger.info(f"处理失败: {failure_count} 个文件")
    
    # 根据处理结果返回状态码
    if failure_count > 0:
        if success_count == 0:
            logger.error("所有文件处理失败")
            return 1
        else:
            logger.warning("部分文件处理失败")
            return 0
    else:
        logger.info("所有文件处理成功")
        return 0

if __name__ == "__main__":
    sys.exit(main()) 