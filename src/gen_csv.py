#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
命令行脚本，用于将提取的考研英语真题结构化数据转换为CSV格式
"""

import os
import sys
import logging
import argparse
from datetime import datetime
from dotenv import load_dotenv

# 添加当前目录到模块搜索路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入自定义模块
from src.data_processor import DataProcessor

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("gen_csv")

def setup_logging(level_str):
    """设置日志级别"""
    levels = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR
    }
    level = levels.get(level_str.lower(), logging.INFO)
    logging.getLogger().setLevel(level)

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="考研英语真题数据CSV生成工具")
    parser.add_argument('--input', required=True, help="输入文件或目录路径")
    parser.add_argument('--output-dir', default="test_results", help="输出目录")
    parser.add_argument('--model', help="使用的模型名称，留空则使用环境变量中DEFAULT_MODEL指定的模型")
    parser.add_argument('--batch', action='store_true', help="批量处理模式，当输入为目录时生效")
    parser.add_argument('--file-pattern', default="*.txt", help="批量处理模式下的文件匹配模式")
    parser.add_argument('--debug', action='store_true', help="保存调试信息，包括API响应和中间结果")
    parser.add_argument('--log', choices=['debug', 'info', 'warning', 'error'], 
                       default='info', help="日志级别")
    
    # 添加帮助文本
    parser.epilog = """
详细说明:
  本工具将提取的考研英语真题结构化数据转换为CSV格式。
  
  1. 单文件处理:
     python src/gen_csv.py --input 数据文件.txt --output-dir 输出目录
  
  2. 批量处理:
     python src/gen_csv.py --input 数据目录 --batch --file-pattern "*.txt" --output-dir 输出目录
  
  3. 指定模型:
     python src/gen_csv.py --input 数据文件.txt --model google/gemini-2.5-flash-preview
  
  4. 调试模式:
     python src/gen_csv.py --input 数据文件.txt --debug --log debug
"""
    
    args = parser.parse_args()
    
    # 设置日志级别
    setup_logging(args.log)
    
    # 检查输入路径是否存在
    if not os.path.exists(args.input):
        logger.error(f"输入路径不存在: {args.input}")
        return 1
    
    # 初始化数据处理器
    processor = DataProcessor(model_name=args.model)
    
    # 确定处理模式
    if os.path.isdir(args.input) and args.batch:
        # 批量处理模式
        logger.info(f"启动批量处理模式，输入目录: {args.input}")
        results = processor.batch_process(
            input_dir=args.input,
            output_dir=args.output_dir,
            file_pattern=args.file_pattern,
            save_debug=args.debug
        )
        
        # 输出汇总信息
        successful = sum(1 for _, success, _, _ in results if success)
        logger.info(f"批量处理完成，成功: {successful}/{len(results)}")
        
        # 如果有失败的，返回非零状态码
        return 0 if successful == len(results) else 1
    else:
        # 单文件处理模式
        if os.path.isdir(args.input):
            logger.warning(f"输入路径是目录，但未启用批量处理模式。请加上 --batch 参数启用批量处理。")
            return 1
        
        logger.info(f"启动单文件处理模式，输入文件: {args.input}")
        success, csv_path, process_time = processor.process_document(
            document_path=args.input,
            output_dir=args.output_dir,
            save_debug=args.debug
        )
        
        if success:
            logger.info(f"处理成功，生成CSV文件: {csv_path}，耗时: {process_time:.2f}秒")
            return 0
        else:
            logger.error(f"处理失败，耗时: {process_time:.2f}秒")
            return 1

if __name__ == "__main__":
    sys.exit(main()) 