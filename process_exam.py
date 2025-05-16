#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
考研英语真题通用处理脚本
支持处理任意年份的真题，自动适配docx和txt格式
"""

import os
import sys
import logging
import argparse
import time
import re
from pathlib import Path
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("process_exam")

# 将当前目录添加到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入数据处理器
from src.data_processor import DataProcessor
from src.docx_reader import DocxReader

def process_exam(input_file, output_dir=None, model_name=None, save_debug=False, year=None):
    """
    处理考研英语真题文件
    
    Args:
        input_file: 输入文件路径
        output_dir: 输出目录，如果为None则自动根据年份创建
        model_name: 模型名称
        save_debug: 是否保存调试信息
        year: 手动指定年份，如果为None则自动从文件名提取
    
    Returns:
        tuple: (是否成功, CSV文件路径, 处理时间)
    """
    start_time = time.time()
    
    # 检查文件是否存在
    if not os.path.exists(input_file):
        logger.error(f"文件不存在: {input_file}")
        return False, None, 0
    
    # 尝试从文件名中提取年份
    if year is None:
        file_name = os.path.basename(input_file)
        year_match = re.search(r'(\d{4})', file_name)
        year = year_match.group(1) if year_match else "unknown"
    
    # 如果没有指定输出目录，则使用年份作为子目录
    if output_dir is None:
        output_dir = os.path.join("test_results", year)
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(os.path.join(output_dir, "analysis"), exist_ok=True)
    os.makedirs(os.path.join(output_dir, "debug"), exist_ok=True)
    
    logger.info("=" * 50)
    logger.info(f"开始处理考研英语真题: {input_file}")
    logger.info(f"目标年份: {year}")
    logger.info(f"输出目录: {output_dir}")
    
    # 检查文件类型
    file_extension = Path(input_file).suffix.lower()
    if file_extension == '.docx':
        logger.info("检测到Word文档，将自动提取文本")
    elif file_extension == '.txt':
        logger.info("检测到文本文档，直接处理")
    else:
        logger.warning(f"未知的文件类型: {file_extension}，尝试作为文本文件处理")
    
    try:
        # 初始化数据处理器
        processor = DataProcessor(model_name=model_name)
        
        # 处理文档
        success, csv_path, process_time = processor.process_document(
            document_path=input_file,
            output_dir=output_dir,
            save_debug=save_debug
        )
        
        # 处理结果
        if success:
            logger.info(f"✅ {year}年考研英语真题处理成功！")
            logger.info(f"📊 CSV文件已生成: {csv_path}")
            logger.info(f"⏱️ 处理耗时: {process_time:.2f}秒")
        else:
            logger.error(f"❌ {year}年考研英语真题处理失败，耗时: {process_time:.2f}秒")
        
        # 显示处理结果路径
        if success and csv_path:
            analysis_dir = os.path.join(output_dir, "analysis")
            analysis_files = os.listdir(analysis_dir)
            json_files = [f for f in analysis_files if f.endswith('.json')]
            
            if json_files:
                latest_json = sorted(json_files)[-1]
                logger.info(f"📄 最新分析数据: {os.path.join(analysis_dir, latest_json)}")
        
        return success, csv_path, process_time
    
    except Exception as e:
        logger.error(f"处理过程中出错: {str(e)}", exc_info=True)
        total_time = time.time() - start_time
        return False, None, total_time

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="考研英语真题通用处理工具")
    parser.add_argument('input_file', help="输入文件路径，支持docx和txt格式")
    parser.add_argument('--output-dir', '-o', help="输出目录，默认为test_results/年份")
    parser.add_argument('--model', '-m', help="使用的模型名称，默认使用环境变量中设置的模型")
    parser.add_argument('--debug', '-d', action='store_true', help="保存调试信息")
    parser.add_argument('--year', '-y', help="手动指定年份，默认从文件名提取")
    
    # 使用说明
    parser.epilog = """
使用示例:
  # 处理docx文件 (自动从文件名提取年份)
  python process_exam.py 2022年考研英语(一)真题.docx --debug
  
  # 处理txt文件并手动指定年份
  python process_exam.py kaoyan_english.txt --year 2021
  
  # 指定输出目录和使用特定模型
  python process_exam.py 2023年考研英语.docx --output-dir my_results/2023 --model anthropic/claude-3-5-sonnet
    """
    
    args = parser.parse_args()
    
    # 处理文件
    success, csv_path, process_time = process_exam(
        input_file=args.input_file,
        output_dir=args.output_dir,
        model_name=args.model,
        save_debug=args.debug,
        year=args.year
    )
    
    # 返回状态码
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main()) 