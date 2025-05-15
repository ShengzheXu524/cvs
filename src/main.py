#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
主程序入口，用于处理考研英语真题docx文件。
"""

import os
import sys
import argparse
import logging
import traceback
from pathlib import Path
from tqdm import tqdm

# 导入自定义模块
from docx_reader import DocxReader
from claude_api import ClaudeAPI
from data_organizer import DataOrganizer
from csv_generator import CSVGenerator
from sentence_splitter import split_sentences
from utils import (
    setup_logging,
    load_api_key,
    ensure_directory_exists,
    get_all_docx_files,
    extract_exam_info_from_filename,
    make_output_path
)

def process_single_file(input_file, output_file, api_key=None, model=None, debug=False):
    """
    处理单个docx文件。
    
    Args:
        input_file (str): 输入docx文件路径
        output_file (str): 输出CSV文件路径
        api_key (str, optional): Claude API密钥
        model (str, optional): 要使用的Claude模型
        debug (bool, optional): 是否启用调试模式
    
    Returns:
        bool: 是否成功处理
    """
    logger = logging.getLogger("考研英语真题处理")
    logger.info(f"开始处理文件: {input_file}")
    
    try:
        # 提取年份和考试类型
        year, exam_type = extract_exam_info_from_filename(input_file)
        logger.info(f"从文件名提取到信息 - 年份: {year}, 类型: {exam_type}")
        
        # 创建各模块实例
        docx_reader = DocxReader()
        claude_api = ClaudeAPI(api_key=api_key, model=model if model else "claude-3-7-sonnet-20240229")
        data_organizer = DataOrganizer()
        csv_generator = CSVGenerator()
        
        # 读取docx文件
        logger.info("读取文档内容...")
        document_text = docx_reader.read_file(input_file)
        
        # 发送到Claude API进行分析
        logger.info("发送到Claude API进行内容分析...")
        api_result = claude_api.extract_structured_data(document_text)
        
        # 保存原始API结果（调试用）
        if debug:
            debug_dir = os.path.join(os.path.dirname(output_file), "debug")
            ensure_directory_exists(debug_dir)
            debug_file = os.path.join(debug_dir, f"{os.path.basename(input_file)}.json")
            data_organizer.save_debug_data(api_result, debug_file)
            
            # 如果返回了原始响应文本，则同时保存原始响应
            if isinstance(api_result, dict) and "raw_response" in api_result:
                raw_response_file = os.path.join(debug_dir, f"{os.path.basename(input_file)}_raw.txt")
                with open(raw_response_file, "w", encoding="utf-8") as f:
                    f.write(api_result.get("raw_response", ""))
        
        # 组织和规范化数据
        logger.info("组织和规范化数据...")
        organized_data = data_organizer.organize_data(api_result, year, exam_type)
        
        # 确保数据完整性
        logger.info("确保数据完整...")
        complete_data = data_organizer.ensure_complete_dataset(organized_data, year, exam_type)
        
        # 验证数据
        is_valid, message = data_organizer.validate_data(complete_data)
        if not is_valid:
            logger.warning(f"数据验证失败: {message}")
            logger.warning("尝试继续处理...")
        
        # 应用句子拆分器
        logger.info("应用句子拆分器...")
        data_with_split_sentences = data_organizer.apply_sentence_splitter(complete_data, split_sentences)
        
        # 生成CSV文件
        logger.info(f"生成CSV文件: {output_file}")
        success = csv_generator.generate_csv(data_with_split_sentences, output_file)
        
        if success:
            logger.info(f"成功处理文件: {input_file}")
            return True
        else:
            logger.error(f"处理文件失败: {input_file}")
            return False
            
    except Exception as e:
        logger.error(f"处理文件时出错: {str(e)}")
        logger.debug(traceback.format_exc())
        return False

def process_batch(input_dir, output_dir, api_key=None, model=None, debug=False):
    """
    批处理目录中的所有docx文件。
    
    Args:
        input_dir (str): 输入目录
        output_dir (str): 输出目录
        api_key (str, optional): Claude API密钥
        model (str, optional): 要使用的Claude模型
        debug (bool, optional): 是否启用调试模式
    
    Returns:
        tuple: (成功数, 失败数)
    """
    logger = logging.getLogger("考研英语真题处理")
    logger.info(f"开始批处理目录: {input_dir}")
    
    # 获取所有docx文件
    docx_files = get_all_docx_files(input_dir)
    logger.info(f"找到 {len(docx_files)} 个docx文件")
    
    if not docx_files:
        logger.warning(f"目录中没有找到docx文件: {input_dir}")
        return 0, 0
    
    # 确保输出目录存在
    ensure_directory_exists(output_dir)
    
    # 处理每个文件
    success_count = 0
    failure_count = 0
    
    for file_path in tqdm(docx_files, desc="处理文件"):
        # 创建输出文件路径
        output_file = make_output_path(file_path, output_dir)
        
        # 处理文件
        if process_single_file(file_path, output_file, api_key, model, debug):
            success_count += 1
        else:
            failure_count += 1
    
    logger.info(f"批处理完成 - 成功: {success_count}, 失败: {failure_count}")
    return success_count, failure_count

def main():
    """程序主入口。"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="处理考研英语真题docx文件，提取结构化信息并生成CSV文件。")
    
    parser.add_argument("--input", required=True, help="输入的docx文件路径或目录")
    parser.add_argument("--output", required=True, help="输出的CSV文件路径或目录")
    parser.add_argument("--api_key", help="Claude API密钥（如不提供将尝试从环境变量获取）")
    parser.add_argument("--model", default="claude-3-7-sonnet-20240229", help="要使用的Claude模型")
    parser.add_argument("--batch", action="store_true", help="批处理模式，处理目录下所有docx文件")
    parser.add_argument("--log", choices=["debug", "info", "warning", "error"], default="info", help="日志级别")
    parser.add_argument("--debug", action="store_true", help="调试模式，保存中间结果")
    
    args = parser.parse_args()
    
    # 设置日志
    logger = setup_logging(args.log)
    logger.info("开始执行考研英语真题处理程序")
    
    # 获取API密钥
    api_key = args.api_key
    if not api_key:
        try:
            api_key = load_api_key()
        except ValueError as e:
            logger.error(str(e))
            return 1
    
    # 执行处理
    try:
        if args.batch or os.path.isdir(args.input):
            # 批处理模式
            input_dir = args.input
            output_dir = args.output
            
            if not os.path.isdir(input_dir):
                logger.error(f"输入路径不是有效目录: {input_dir}")
                return 1
            
            success_count, failure_count = process_batch(
                input_dir, output_dir, api_key, args.model, args.debug
            )
            
            if failure_count > 0:
                logger.warning(f"部分文件处理失败 - 成功: {success_count}, 失败: {failure_count}")
                return 1 if success_count == 0 else 0
        else:
            # 单文件模式
            input_file = args.input
            output_file = args.output
            
            if not os.path.isfile(input_file):
                logger.error(f"输入文件不存在: {input_file}")
                return 1
            
            if not input_file.endswith('.docx'):
                logger.error(f"输入文件不是docx格式: {input_file}")
                return 1
            
            success = process_single_file(
                input_file, output_file, api_key, args.model, args.debug
            )
            
            if not success:
                logger.error("处理失败")
                return 1
        
        logger.info("程序执行完毕")
        return 0
        
    except Exception as e:
        logger.error(f"程序执行出错: {str(e)}")
        logger.debug(traceback.format_exc())
        return 1

if __name__ == "__main__":
    sys.exit(main()) 