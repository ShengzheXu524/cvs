#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
考研英语真题文档处理主程序
负责流程编排与控制
"""

import os
import sys
import json
import logging
import argparse
import time
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path
import re

# 导入自定义模块
from src.openrouter_handler import OpenRouterHandler
from src.content_analyzer import ContentAnalyzer
from src.model_config import get_model
from src.data_organizer import DataOrganizer
from src.csv_generator import CSVGenerator
from src.sentence_splitter import split_sentences
from src.docx_reader import DocxReader

# 配置日志
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("main")

# 加载环境变量
load_dotenv()

def process_file(input_file, model_name=None, output_dir="test_results", save_debug=False, gen_csv=True):
    """
    处理指定的文档文件
    
    Args:
        input_file: 输入文件路径
        model_name: 模型名称，如果为None则使用环境变量或默认模型
        output_dir: 输出目录
        save_debug: 是否保存调试信息
        gen_csv: 是否生成CSV文件
    
    Returns:
        dict: 包含处理结果的字典，包括:
            - success: 处理是否成功
            - json_path: 保存的JSON结果路径
            - csv_path: 保存的CSV结果路径(如果生成了)
            - analysis_time: 分析耗时
    """
    logger.info(f"开始处理文件: {input_file}")
    
    # 记录开始时间
    start_time = time.time()
    
    try:
        # 检查文件扩展名
        file_extension = Path(input_file).suffix.lower()
        
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(os.path.join(output_dir, "analysis"), exist_ok=True)
        if save_debug:
            os.makedirs(os.path.join(output_dir, "debug"), exist_ok=True)
        
        # 根据文件类型读取内容
        if file_extension == '.docx':
            logger.info("检测到Word文档，使用DocxReader读取")
            docx_reader = DocxReader()
            document_text = docx_reader.read_file(input_file)
            
            # 如果需要调试，保存提取的文本
            if save_debug:
                # 提取年份作为目录名（从文件名中提取）
                file_name = os.path.basename(input_file)
                year_match = re.search(r'(\d{4})', file_name)
                year = year_match.group(1) if year_match else "unknown"
                
                # 确保年份目录存在
                year_dir = os.path.join(output_dir, year)
                os.makedirs(year_dir, exist_ok=True)
                os.makedirs(os.path.join(year_dir, "debug"), exist_ok=True)
                
                # 保存提取的文本
                extracted_text_path = os.path.join(year_dir, "debug", f"{os.path.splitext(file_name)[0]}_extracted.txt")
                with open(extracted_text_path, 'w', encoding='utf-8') as f:
                    f.write(document_text)
                logger.info(f"提取的文本已保存到: {extracted_text_path}")
        else:
            # 默认当作文本文件处理
            logger.info("文本文件，直接读取内容")
            with open(input_file, 'r', encoding='utf-8') as f:
                document_text = f.read()
        
        # 初始化API处理器
        api_handler = OpenRouterHandler(model=model_name)
        
        # 初始化内容分析器
        content_analyzer = ContentAnalyzer(api_handler=api_handler)
        
        # 提取数据
        extract_start_time = time.time()
        result = content_analyzer.extract_data(document_text, save_debug=save_debug, output_dir=output_dir)
        extract_time = time.time() - extract_start_time
        logger.info(f"数据提取耗时: {extract_time:.2f} 秒")
        
        # 保存结果到JSON文件
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = os.path.splitext(os.path.basename(input_file))[0]
        safe_model_name = api_handler.model.replace('/', '_')
        
        # 提取年份作为目录名
        year_match = re.search(r'(\d{4})', base_name)
        year = year_match.group(1) if year_match else None
        if year:
            # 使用年份作为子目录
            year_dir = os.path.join(output_dir, year)
            os.makedirs(year_dir, exist_ok=True)
            os.makedirs(os.path.join(year_dir, "analysis"), exist_ok=True)
            if save_debug:
                os.makedirs(os.path.join(year_dir, "debug"), exist_ok=True)
            output_json = os.path.join(year_dir, "analysis", f"{base_name}_{safe_model_name}_{timestamp}.json")
        else:
            # 没有年份时使用原目录
            output_json = os.path.join(output_dir, "analysis", f"{base_name}_{safe_model_name}_{timestamp}.json")
        
        with open(output_json, 'w', encoding='utf-8') as f:
            json.dump({
                "model": api_handler.model,
                "input_file": os.path.basename(input_file),
                "analysis_time_seconds": extract_time,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "result": result
            }, f, ensure_ascii=False, indent=2)
        
        logger.info(f"JSON结果已保存到: {output_json}")
        
        # 检查是否完整提取了52道题
        questions = result.get("questions", [])
        if len(questions) < 52:
            logger.warning(f"警告：只提取了 {len(questions)} 道题目，不是完整的52道题")
            logger.info(f"题号列表: {sorted([q.get('number', 0) for q in questions])}")
        else:
            logger.info(f"成功提取了所有 {len(questions)} 道题目")
        
        # 如果需要生成CSV
        csv_path = None
        if gen_csv:
            try:
                logger.info("开始生成CSV文件...")
                csv_start_time = time.time()
                
                # 初始化数据组织器和CSV生成器
                data_organizer = DataOrganizer()
                csv_generator = CSVGenerator()
                
                # 组织数据
                organized_data = data_organizer.organize_data(result)
                
                # 确保数据集完整
                complete_data = data_organizer.ensure_complete_dataset(organized_data)
                
                # 应用句子拆分
                processed_data = data_organizer.apply_sentence_splitter(complete_data, split_sentences)
                
                # 保存组织后的数据
                if year:
                    organized_json = os.path.join(year_dir, "analysis", f"organized_data_{timestamp}.json")
                    csv_dir = year_dir
                else:
                    organized_json = os.path.join(output_dir, "analysis", f"organized_data_{timestamp}.json")
                    csv_dir = output_dir
                
                with open(organized_json, 'w', encoding='utf-8') as f:
                    json.dump(processed_data, f, ensure_ascii=False, indent=2)
                logger.info(f"组织后的数据已保存到: {organized_json}")
                
                # 确定CSV文件名
                year_from_result = result.get("metadata", {}).get("year", year if year else "未知年份")
                exam_type = result.get("metadata", {}).get("exam_type", "未知类型")
                csv_filename = f"{year_from_result}{exam_type}.csv"
                csv_path = os.path.join(csv_dir, csv_filename)
                
                # 生成CSV文件
                csv_success = csv_generator.generate_csv(processed_data, csv_path)
                csv_time = time.time() - csv_start_time
                
                if csv_success:
                    logger.info(f"CSV文件已成功生成: {csv_path}，耗时: {csv_time:.2f} 秒")
                else:
                    logger.error(f"CSV文件生成失败，耗时: {csv_time:.2f} 秒")
                    csv_path = None
                
            except Exception as e:
                logger.error(f"生成CSV文件时出错: {str(e)}", exc_info=True)
                csv_path = None
        
        # 计算总处理时间
        total_time = time.time() - start_time
        logger.info(f"文件处理完成，总耗时: {total_time:.2f} 秒")
        
        return {
            "success": True,
            "json_path": output_json,
            "csv_path": csv_path,
            "analysis_time": total_time
        }
        
    except Exception as e:
        logger.error(f"处理文件时出错: {str(e)}", exc_info=True)
        return {
            "success": False,
            "json_path": None,
            "csv_path": None,
            "analysis_time": time.time() - start_time
        }

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="考研英语真题文档处理工具")
    parser.add_argument('input_file', help="输入文件路径，支持txt和docx格式")
    parser.add_argument('--model', help="使用的模型名称，留空则使用环境变量中DEFAULT_MODEL指定的模型")
    parser.add_argument('--output-dir', default="test_results", help="输出目录，会自动根据年份创建子目录")
    parser.add_argument('--debug', action='store_true', help="保存调试信息，包括API响应和中间结果")
    parser.add_argument('--no-csv', action='store_true', help="不生成CSV文件，仅生成JSON结果")
    parser.add_argument('--year', help="指定年份，用于创建输出子目录，默认从文件名中提取")
    
    # 添加帮助文本
    parser.epilog = """
详细说明:
  本工具支持处理txt和docx格式的考研英语真题，会自动根据文件扩展名选择处理方式:
  - 对于docx文件，会自动提取文本并处理
  - 对于txt文件，直接读取内容处理
  - 结果会根据年份自动保存在对应的子目录中
  - 超过3000字符的长文档会自动使用分段处理，提高API调用效率
  - 使用--debug参数可以保存API响应和中间处理结果，便于分析和调试
  - 默认会同时生成JSON和CSV格式的结果文件，使用--no-csv可以禁用CSV生成
  
示例:
  python src/main.py input.txt --model google/gemini-2.5-flash-preview --debug
  python src/main.py 2023年考研英语真题.docx --output-dir custom_results
  python src/main.py input.txt --year 2022 --no-csv  # 手动指定年份，不生成CSV文件
"""
    
    args = parser.parse_args()
    
    # 检查文件是否存在
    if not os.path.exists(args.input_file):
        logger.error(f"文件不存在: {args.input_file}")
        return 1
    
    # 如果用户指定了年份，修改输出目录
    output_dir = args.output_dir
    if args.year:
        output_dir = os.path.join(args.output_dir, args.year)
    
    # 处理文件
    result = process_file(
        args.input_file, 
        model_name=args.model, 
        output_dir=output_dir,
        save_debug=args.debug,
        gen_csv=not args.no_csv
    )
    
    # 输出处理结果摘要
    if result["success"]:
        logger.info("✅ 文件处理成功")
        logger.info(f"📊 JSON结果: {result['json_path']}")
        if result["csv_path"]:
            logger.info(f"📝 CSV结果: {result['csv_path']}")
        logger.info(f"⏱️ 总耗时: {result['analysis_time']:.2f} 秒")
        return 0
    else:
        logger.error("❌ 文件处理失败")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 