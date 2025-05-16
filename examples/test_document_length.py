#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试文档长度检测功能
此脚本用于验证系统是否会根据文档长度自动选择合适的处理方式
"""

import os
import sys
import logging
import argparse
from pathlib import Path

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("test_document_length")

# 添加父目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入测试函数
from src.test_module import test_document_length_detection

def main():
    """程序主入口"""
    parser = argparse.ArgumentParser(description="测试文档长度检测功能")
    parser.add_argument("--input", required=True, help="输入文档路径")
    parser.add_argument("--output-dir", default="test_results", help="输出目录")
    
    args = parser.parse_args()
    
    # 检查文件是否存在
    if not os.path.exists(args.input):
        logger.error(f"文件不存在: {args.input}")
        return 1
    
    # 确保输出目录存在
    os.makedirs(args.output_dir, exist_ok=True)
    
    # 测试文档长度检测功能
    logger.info(f"开始测试文档 {args.input} 的长度检测功能")
    success = test_document_length_detection(
        document_path=args.input,
        output_dir=args.output_dir
    )
    
    if success:
        logger.info("测试完成，文档长度检测功能运行正常")
    else:
        logger.error("测试失败，文档长度检测功能可能存在问题")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main()) 