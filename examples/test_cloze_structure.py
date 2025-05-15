#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试完形填空原文处理优化，确保原文只在sections中出现一次，
而每道完形填空题目都引用相同的原文。
"""

import os
import sys
import json
import logging
from pathlib import Path

# 添加src目录到路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.data_organizer import DataOrganizer
from src.csv_generator import CSVGenerator

def setup_logging(level="info"):
    """
    设置日志级别
    
    Args:
        level (str): 日志级别
    
    Returns:
        logging.Logger: 日志对象
    """
    # 设置日志级别
    level_map = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING,
        "error": logging.ERROR
    }
    log_level = level_map.get(level.lower(), logging.INFO)
    
    # 配置日志
    logger = logging.getLogger()
    logger.setLevel(log_level)
    
    # 如果已经有处理器，清除它们
    if logger.handlers:
        logger.handlers.clear()
    
    # 添加控制台处理器
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger

def ensure_directory_exists(directory):
    """
    确保目录存在，如果不存在则创建
    
    Args:
        directory (str): 目录路径
    """
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"创建目录: {directory}")

def create_optimized_cloze_data():
    """
    创建优化后的完形填空数据结构示例
    
    Returns:
        dict: 模拟的API响应数据
    """
    return {
        "metadata": {
            "year": "2024",
            "exam_type": "英语（一）"
        },
        "sections": {
            "cloze": {
                "original_text": "This is the complete cloze passage with all blanks: There's nothing more welcoming than a door opening for you. [1] the need to be touched to open or close, automatic doors are essential in [2] disabled access to buildings and helping provide general [3] to commercial buildings. They [4] from the traditional simple hinged designs to powered doors [5] by motors.",
                "restored_text": "This is the complete cloze passage with answers filled in: There's nothing more welcoming than a door opening for you. Without the need to be touched to open or close, automatic doors are essential in improving disabled access to buildings and helping provide general convenience to commercial buildings. They range from the traditional simple hinged designs to powered doors controlled by motors.",
                "answers_summary": "1.D 2.C 3.B 4.A 5.D"
            },
            "reading": {
                "text_1": {
                    "original_text": "This is the complete reading text 1: Nearly 2,000 years ago, as the Romans began to pull out of Scotland, they left behind a curious treasure: 10 tons of nails, nearly a million of the things.",
                    "answers_summary": "21.D 22.D 23.A"
                }
            }
        },
        "questions": [
            {
                "number": 1,
                "section_type": "完形填空",
                "stem": "/",
                "options": "A. Through, B. Despite, C. Besides, D. Without",
                "correct_answer": "D. Without",
                "distractor_options": "A. Through, B. Despite, C. Besides"
            },
            {
                "number": 2,
                "section_type": "完形填空",
                "stem": "/",
                "options": "A. revealing, B. demanding, C. improving, D. tracing",
                "correct_answer": "C. improving",
                "distractor_options": "A. revealing, B. demanding, D. tracing"
            },
            {
                "number": 3,
                "section_type": "完形填空",
                "stem": "/",
                "options": "A. experience, B. convenience, C. guidance, D. reference",
                "correct_answer": "B. convenience",
                "distractor_options": "A. experience, C. guidance, D. reference"
            },
            {
                "number": 21,
                "section_type": "阅读理解",
                "stem": "The Romans buried the nails probably for the sake of",
                "options": "[A]saving them for future use. [B]keeping them from rusting. [C]letting them grow in value. [D]hiding them from the locals.",
                "correct_answer": "[D]hiding them from the locals",
                "distractor_options": "[A]saving them for future use. [B]keeping them from rusting. [C]letting them grow in value."
            }
        ]
    }

def test_cloze_text_optimization():
    """
    测试完形填空原文优化处理
    """
    logger = setup_logging("info")
    logger.info("开始测试完形填空原文优化处理")
    
    # 确保输出目录存在
    output_dir = "./test_results"
    ensure_directory_exists(output_dir)
    
    try:
        # 创建优化后的数据结构
        optimized_data = create_optimized_cloze_data()
        
        # 保存原始数据
        mock_data_file = os.path.join(output_dir, "optimized_cloze_data.json")
        with open(mock_data_file, "w", encoding="utf-8") as f:
            json.dump(optimized_data, f, ensure_ascii=False, indent=2)
        logger.info(f"优化后的数据结构已保存到: {mock_data_file}")
        
        # 创建数据组织器
        data_organizer = DataOrganizer()
        
        # 处理数据
        logger.info("处理优化后的数据结构")
        organized_data = data_organizer._process_new_format(optimized_data)
        
        # 保存处理后的数据
        organized_data_file = os.path.join(output_dir, "organized_cloze_data.json")
        with open(organized_data_file, "w", encoding="utf-8") as f:
            json.dump(organized_data, f, ensure_ascii=False, indent=2)
        logger.info(f"组织后的数据已保存到: {organized_data_file}")
        
        # 检查所有完形填空题是否共享相同原文
        cloze_original_texts = set()
        cloze_restored_texts = set()
        
        for item in organized_data:
            if item.get("题型") == "完形填空":
                original_text = item.get("原文（卷面）", "")
                restored_text = item.get("原文（还原后）", "")
                
                cloze_original_texts.add(original_text)
                cloze_restored_texts.add(restored_text)
        
        # 验证所有完形填空题是否使用同一个原文
        logger.info(f"完形填空题目使用的不同原文数量: {len(cloze_original_texts)}")
        logger.info(f"完形填空题目使用的不同还原原文数量: {len(cloze_restored_texts)}")
        
        if len(cloze_original_texts) == 1 and len(cloze_restored_texts) == 1:
            logger.info("测试通过：所有完形填空题目共享同一个原文")
        else:
            logger.error("测试失败：完形填空题目使用了不同的原文")
        
        # 生成CSV文件
        csv_generator = CSVGenerator()
        csv_file = os.path.join(output_dir, "test_cloze_structure.csv")
        success = csv_generator.generate_csv(organized_data, csv_file)
        
        if success:
            logger.info(f"成功生成CSV文件: {csv_file}")
        else:
            logger.error("生成CSV文件失败")
    
    except Exception as e:
        logger.exception(f"测试过程中出错: {str(e)}")
        raise

def main():
    """主函数"""
    test_cloze_text_optimization()

if __name__ == "__main__":
    main()
    print("完形填空原文优化测试完成!") 