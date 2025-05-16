#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
考研英语真题批量处理脚本
用于批量处理目录中的多个真题文件并生成CSV格式输出
"""

import os
import sys
import logging
import time
import argparse
from pathlib import Path
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("batch_process_exams")

# 将当前目录添加到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入数据处理器
from src.data_processor import DataProcessor

def main():
    """主函数：批量处理考研英语真题文件"""
    
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description="考研英语真题批量处理工具")
    parser.add_argument('--input-dir', default="input_files", help="输入文件目录")
    parser.add_argument('--output-dir', default="test_results/batch", help="输出目录")
    parser.add_argument('--file-pattern', default="*.txt", help="文件匹配模式")
    parser.add_argument('--model', help="使用的模型名称，留空则使用环境变量中的默认模型")
    parser.add_argument('--debug', action='store_true', help="保存调试信息")
    
    # 解析命令行参数
    args = parser.parse_args()
    
    # 确保输入目录存在
    if not os.path.exists(args.input_dir) or not os.path.isdir(args.input_dir):
        logger.error(f"输入目录不存在或不是目录: {args.input_dir}")
        return 1
    
    # 确保输出目录存在
    os.makedirs(args.output_dir, exist_ok=True)
    
    logger.info(f"开始批量处理考研英语真题...")
    logger.info(f"输入目录: {args.input_dir}")
    logger.info(f"文件匹配: {args.file_pattern}")
    logger.info(f"输出目录: {args.output_dir}")
    if args.model:
        logger.info(f"指定模型: {args.model}")
    else:
        logger.info("使用默认模型")
    
    # 记录开始时间
    start_time = time.time()
    
    try:
        # 初始化数据处理器
        processor = DataProcessor(model_name=args.model)
        
        # 批量处理文件
        logger.info("开始批量处理...")
        results = processor.batch_process(
            input_dir=args.input_dir,
            output_dir=args.output_dir,
            file_pattern=args.file_pattern,
            save_debug=args.debug
        )
        
        # 显示处理结果统计
        successful = sum(1 for _, success, _, _ in results if success)
        logger.info(f"批量处理完成，成功: {successful}/{len(results)}")
        
        # 详细结果
        logger.info("处理详情:")
        for file_name, success, csv_path, process_time in results:
            status = "✅ 成功" if success else "❌ 失败"
            logger.info(f"{status} - {file_name} - 耗时: {process_time:.2f}秒")
            if success:
                logger.info(f"  CSV文件: {csv_path}")
        
        # 总耗时
        total_time = time.time() - start_time
        logger.info(f"总耗时: {total_time:.2f}秒")
        
        # 如果有处理失败的文件，返回非零状态码
        return 0 if successful == len(results) else 1
    
    except Exception as e:
        logger.error(f"批量处理过程中出错: {str(e)}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main()) 