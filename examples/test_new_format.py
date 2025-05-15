#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试新的JSON格式处理功能的脚本。
"""

import os
import sys
import json
import argparse
from pathlib import Path

# 添加父目录到路径，以便导入src模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入工具模块
from src.data_organizer import DataOrganizer
from src.content_analyzer import ContentAnalyzer
from src.csv_generator import CSVGenerator
from src.utils import setup_logging, ensure_directory_exists

def create_sample_data():
    """
    创建一个测试用的样例数据，模拟新的JSON格式。
    
    Returns:
        dict: 模拟的新格式JSON数据
    """
    return {
        "metadata": {
            "year": "2023",
            "exam_type": "英语（一）"
        },
        "sections": {
            "cloze": {
                "original_text": "The importance of [1] as a global language is undeniable. It serves as a bridge [2] different cultures and nations.",
                "restored_text": "The importance of English as a global language is undeniable. It serves as a bridge between different cultures and nations.",
                "answers_summary": "1.A 2.C"
            },
            "reading": {
                "text_1": {
                    "original_text": "This is a sample text for reading comprehension Text 1.",
                    "answers_summary": "21.D 22.A 23.C 24.B 25.A"
                },
                "text_2": {
                    "original_text": "This is a sample text for reading comprehension Text 2.",
                    "answers_summary": "26.B 27.C 28.A 29.D 30.B"
                }
            },
            "new_type": {
                "original_text": "This is a sample text for new question type.",
                "restored_text": "This is a sample text for new question type with answers.",
                "answers_summary": "41.A 42.B 43.C 44.D 45.A"
            }
        },
        "questions": [
            {
                "number": 1,
                "section_type": "完形填空",
                "stem": "",
                "options": "A. English, B. Chinese, C. French, D. Spanish",
                "correct_answer": "A. English",
                "distractor_options": "B. Chinese, C. French, D. Spanish"
            },
            {
                "number": 2,
                "section_type": "完形填空",
                "stem": "",
                "options": "A. among, B. across, C. between, D. through",
                "correct_answer": "C. between",
                "distractor_options": "A. among, B. across, D. through"
            },
            {
                "number": 21,
                "section_type": "阅读 Text 1",
                "stem": "What is the main idea of this text?",
                "options": "A. Learning, B. Teaching, C. Research, D. Knowledge",
                "correct_answer": "D. Knowledge",
                "distractor_options": "A. Learning, B. Teaching, C. Research"
            },
            {
                "number": 41,
                "section_type": "新题型",
                "stem": "Fill in the blank to complete the sentence.",
                "options": "A. quickly, B. slowly, C. carefully, D. mindfully",
                "correct_answer": "A. quickly",
                "distractor_options": "B. slowly, C. carefully, D. mindfully"
            }
        ]
    }

def test_data_processing(output_dir="./test_results"):
    """
    测试新的JSON格式数据处理流程。
    
    Args:
        output_dir (str): 测试结果输出目录
    """
    # 设置日志
    logger = setup_logging("info")
    logger.info("开始测试新的JSON格式处理")
    
    # 确保输出目录存在
    ensure_directory_exists(output_dir)
    
    try:
        # 创建样例数据
        sample_data = create_sample_data()
        
        # 保存样例数据到文件
        sample_data_file = os.path.join(output_dir, "sample_data.json")
        with open(sample_data_file, "w", encoding="utf-8") as f:
            json.dump(sample_data, f, ensure_ascii=False, indent=2)
        logger.info(f"样例数据已保存到: {sample_data_file}")
        
        # 使用内容分析器处理数据
        content_analyzer = ContentAnalyzer()
        parsed_data = content_analyzer.parse_response(sample_data)
        
        # 保存解析结果
        parsed_data_file = os.path.join(output_dir, "parsed_data.json")
        with open(parsed_data_file, "w", encoding="utf-8") as f:
            json.dump(parsed_data, f, ensure_ascii=False, indent=2)
        logger.info(f"解析结果已保存到: {parsed_data_file}")
        
        # 使用数据组织器处理数据
        data_organizer = DataOrganizer()
        organized_data = data_organizer.organize_data(parsed_data)
        
        # 保存组织后的数据
        organized_data_file = os.path.join(output_dir, "organized_data.json")
        with open(organized_data_file, "w", encoding="utf-8") as f:
            json.dump(organized_data, f, ensure_ascii=False, indent=2)
        logger.info(f"组织后的数据已保存到: {organized_data_file}")
        
        # 生成CSV文件
        csv_generator = CSVGenerator()
        csv_file = os.path.join(output_dir, "test_new_format.csv")
        success = csv_generator.generate_csv(organized_data, csv_file)
        
        if success:
            logger.info(f"CSV文件已成功生成: {csv_file}")
        else:
            logger.error("CSV文件生成失败")
        
        # 输出CSV预览
        preview = csv_generator.preview_data(organized_data, max_rows=10)
        preview_file = os.path.join(output_dir, "csv_preview.txt")
        with open(preview_file, "w", encoding="utf-8") as f:
            f.write(preview)
        logger.info(f"CSV预览已保存到: {preview_file}")
        
        logger.info("测试完成")
        return success
    
    except Exception as e:
        logger.error(f"测试过程中出错: {str(e)}")
        import traceback
        logger.debug(traceback.format_exc())
        return False

def main():
    """脚本主入口"""
    parser = argparse.ArgumentParser(description="测试新的JSON格式处理功能")
    parser.add_argument("--output", default="./test_results", help="测试结果输出目录")
    
    args = parser.parse_args()
    
    success = test_data_processing(args.output)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main()) 