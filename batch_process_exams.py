#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
考研英语真题批量处理脚本
支持处理多年真题，自动从文件名中提取年份
"""

import os
import sys
import argparse
import logging
import glob
import re
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

def process_exam_file(input_file, output_dir=None, model_name=None, save_debug=False):
    """
    处理单个考研英语真题文件
    
    Args:
        input_file: 输入文件路径
        output_dir: 输出目录，如果为None则自动根据年份创建
        model_name: 模型名称
        save_debug: 是否保存调试信息
    
    Returns:
        tuple: (是否成功, CSV文件路径, 处理时间)
    """
    # 检查文件是否存在
    if not os.path.exists(input_file):
        logger.error(f"文件不存在: {input_file}")
        return False, None, 0
    
    # 尝试从文件名中提取年份
    file_name = os.path.basename(input_file)
    year_match = re.search(r'(\d{4})', file_name)
    year = year_match.group(1) if year_match else "unknown"
    
    # 如果没有指定输出目录，则使用年份作为子目录
    if output_dir is None:
        output_dir = os.path.join("test_results", year)
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    logger.info(f"处理文件: {input_file}")
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
    
    return success, csv_path, process_time

def batch_process_directory(input_dir, output_base_dir="test_results", model_name=None, 
                          file_pattern="*.docx;*.txt", save_debug=False):
    """
    批量处理目录下的所有考研英语真题文件
    
    Args:
        input_dir: 输入目录
        output_base_dir: 输出基础目录
        model_name: 模型名称
        file_pattern: 文件匹配模式，多个模式用分号分隔
        save_debug: 是否保存调试信息
    
    Returns:
        list: 处理结果列表
    """
    logger.info(f"批量处理目录: {input_dir}")
    logger.info(f"文件匹配模式: {file_pattern}")
    
    # 拆分文件模式
    patterns = file_pattern.split(';')
    
    # 获取所有匹配的文件
    all_files = []
    for pattern in patterns:
        matched_files = glob.glob(os.path.join(input_dir, pattern.strip()))
        all_files.extend(matched_files)
    
    # 去重并排序
    all_files = sorted(set(all_files))
    
    logger.info(f"找到 {len(all_files)} 个匹配的文件")
    
    # 处理结果
    results = []
    
    # 处理每个文件
    for file_path in all_files:
        # 尝试从文件名中提取年份
        file_name = os.path.basename(file_path)
        year_match = re.search(r'(\d{4})', file_name)
        year = year_match.group(1) if year_match else "unknown"
        
        # 设置输出目录
        output_dir = os.path.join(output_base_dir, year)
        
        # 处理文件
        success, csv_path, process_time = process_exam_file(
            input_file=file_path,
            output_dir=output_dir,
            model_name=model_name,
            save_debug=save_debug
        )
        
        # 记录结果
        results.append({
            "file": file_name,
            "year": year,
            "success": success,
            "csv_path": csv_path,
            "process_time": process_time
        })
    
    # 输出汇总信息
    successful = sum(1 for r in results if r["success"])
    logger.info(f"\n批量处理汇总:\n" + "-" * 50)
    logger.info(f"总文件数: {len(results)}")
    logger.info(f"成功处理: {successful}")
    logger.info(f"失败数量: {len(results) - successful}")
    
    # 打印详细结果
    logger.info(f"\n处理详情:")
    for r in results:
        status = "✅" if r["success"] else "❌"
        logger.info(f"{status} {r['year']}年 - {r['file']} - 耗时: {r['process_time']:.2f}秒")
    
    return results

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="考研英语真题批量处理工具")
    parser.add_argument('--input', '-i', help="输入文件或目录路径")
    parser.add_argument('--output-dir', '-o', default="test_results", help="输出目录")
    parser.add_argument('--model', '-m', help="使用的模型名称")
    parser.add_argument('--batch', '-b', action='store_true', help="批量处理模式")
    parser.add_argument('--pattern', '-p', default="*.docx;*.txt", help="文件匹配模式，多种格式用分号分隔")
    parser.add_argument('--debug', '-d', action='store_true', help="保存调试信息")
    parser.add_argument('--year', '-y', help="手动指定年份（单文件处理时）")
    
    # 细节说明
    parser.epilog = """
使用示例:
  # 处理单个文件
  python batch_process_exams.py --input 2022年考研英语真题.docx --debug
  
  # 手动指定年份
  python batch_process_exams.py --input english_exam.docx --year 2021
  
  # 批量处理目录下的所有docx和txt文件
  python batch_process_exams.py --batch --input ./exams/ --pattern "*.docx;*.txt" --debug
  
  # 使用特定模型处理
  python batch_process_exams.py --input 2023年考研英语.docx --model anthropic/claude-3-5-sonnet
  
功能说明:
  - 自动识别docx和txt格式的考研英语真题文件
  - 自动从文件名提取年份，生成对应的输出目录
  - 支持批量处理多个文件，汇总处理结果
  - 处理结果会保存为CSV文件，便于数据分析和应用
  - 支持保存中间处理结果，方便调试和分析问题
"""
    
    args = parser.parse_args()
    
    # 检查输入路径
    if not args.input:
        parser.print_help()
        return 1
    
    if not os.path.exists(args.input):
        logger.error(f"输入路径不存在: {args.input}")
        return 1
    
    # 批量处理模式
    if args.batch or os.path.isdir(args.input):
        if not os.path.isdir(args.input):
            logger.error(f"批量处理模式需要指定目录: {args.input}")
            return 1
        
        results = batch_process_directory(
            input_dir=args.input,
            output_base_dir=args.output_dir,
            model_name=args.model,
            file_pattern=args.pattern,
            save_debug=args.debug
        )
        
        # 返回成功与否
        return 0 if any(r["success"] for r in results) else 1
    
    # 单文件处理模式
    else:
        # 如果指定了年份，设置输出目录
        output_dir = args.output_dir
        if args.year:
            output_dir = os.path.join(args.output_dir, args.year)
        
        success, csv_path, process_time = process_exam_file(
            input_file=args.input,
            output_dir=output_dir,
            model_name=args.model,
            save_debug=args.debug
        )
        
        return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main()) 