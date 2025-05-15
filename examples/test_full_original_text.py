#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试更新后对原文字段的处理。
"""

import os
import sys
import json
import logging
from pathlib import Path

# 添加src目录到路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.content_analyzer import ContentAnalyzer
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

def create_sample_data():
    """
    创建测试用的样例数据
    
    Returns:
        dict: 样例数据
    """
    return {
        "metadata": {
            "year": "2024",
            "exam_type": "英语（一）"
        },
        "sections": {
            "cloze": {
                "original_text": "这是完整的完形填空原文，包含所有空格标记：There's nothing more welcoming than a door opening for you. [1] the need to be touched to open or close, automatic doors are essential in [2] disabled access to buildings and helping provide general [3] to commercial buildings. They [4] from the traditional simple hinged designs to powered doors [5] by motors and [6] new technological developments. The first [7] door, made of two equal parts, was installed at the entrance of the Temple of Hera in Alexandria 50 BC. [8] this type of system the door was able to open and close. Heron of Alexandria, a Greek mathematician and engineer, was one of the first to [9] automatic doors, which he operated with an innovative system that [10] steam and pulleys.",
                "restored_text": "这是完整的完形填空还原后原文：There's nothing more welcoming than a door opening for you. Without the need to be touched to open or close, automatic doors are essential in improving disabled access to buildings and helping provide general guidance to commercial buildings. They range from the traditional simple hinged designs to powered doors controlled by motors and incorporating new technological developments. The first automatic door, made of two equal parts, was installed at the entrance of the Temple of Hera in Alexandria 50 BC. Through this type of system the door was able to open and close. Heron of Alexandria, a Greek mathematician and engineer, was one of the first to design automatic doors, which he operated with an innovative system that used steam and pulleys.",
                "answers_summary": "1.A 2.C 3.B 4.D 5.A 6.C 7.B 8.A 9.D 10.B 11.C 12.D 13.A 14.B 15.C 16.A 17.D 18.B 19.C 20.D"
            },
            "reading": {
                "text_1": {
                    "original_text": "这是完整的阅读Text 1原文：Nearly 2,000 years ago, as the Romans began to pull out of Scotland, they left behind a curious treasure: 10 tons of nails, nearly a million of the things. The nail hoard was discovered in 1960 in a four-metre-deep pit covered by two metres of gravel. It was only through good luck that it was discovered at all. The pit was right in the path of a planned extension to the Inchtuthil fort. When archaeologists discovered this mass of nearly perfect nails, no one was quite sure what to make of them. It was a bit like finding a chest of solid gold, or a stack of pristine paintings from a famous artist—so valuable that it seemed nonsensical to hide them away, rather than sell them.",
                    "answers_summary": "21.D 22.D 23.A 24.B 25.A"
                },
                "text_2": {
                    "original_text": "这是完整的阅读Text 2原文：In December 1955, Rosa Parks famously refused to give up her seat on a Montgomery, Alabama, bus to a white passenger, a small act of resistance that inspired the Montgomery bus boycott and became a defining moment in the American civil rights movement. People often explain this episode in one of two ways: as the act of an ordinary person propelled by the events of her time, or as the calculated political move of a longtime activist. Both stories contain some truth, but they miss the essential fact about Parks, which is that she was an individual who had spent years developing the courage to act as she did.",
                    "answers_summary": "26.C 27.B 28.A 29.D 30.A"
                }
            },
            "new_type": {
                "original_text": "这是完整的新题型原文：Creativity was once thought to be a gift from the gods. Today we understand it to be the result of cognitive processes that can be studied and enhanced. While the popular image of a creative genius may be of someone who experiences flashes of insight in an \"aha\" moment, creativity is actually a complex process that involves multiple levels of thinking, including problem-finding, idea generation, and critical evaluation.",
                "restored_text": "这是完整的新题型还原后原文：Creativity was once thought to be a gift from the gods. Today we understand it to be the result of cognitive processes that can be studied and enhanced. While the popular image of a creative genius may be of someone who experiences flashes of insight in an \"aha\" moment, creativity is actually a complex process that involves multiple levels of thinking, including problem-finding, idea generation, and critical evaluation.",
                "answers_summary": "41.C 42.A 43.D 44.B 45.C"
            }
        },
        "questions": [
            {
                "number": 1,
                "section_type": "完形填空",
                "stem": "/",
                "options": "A. Without, B. Though, C. Despite, D. Besides",
                "correct_answer": "A. Without",
                "distractor_options": "B. Though, C. Despite, D. Besides"
            },
            {
                "number": 2,
                "section_type": "完形填空",
                "stem": "/",
                "options": "A. promoting, B. blocking, C. improving, D. restricting",
                "correct_answer": "C. improving",
                "distractor_options": "A. promoting, B. blocking, D. restricting"
            },
            {
                "number": 21,
                "section_type": "阅读理解",
                "stem": "The Romans buried the nails probably for the sake of",
                "options": "[A]saving them for future use. [B]keeping them from rusting. [C]letting them grow in value. [D]hiding them from the locals.",
                "correct_answer": "[D]hiding them from the locals",
                "distractor_options": "[A]saving them for future use. [B]keeping them from rusting. [C]letting them grow in value."
            },
            {
                "number": 22,
                "section_type": "阅读理解",
                "stem": "The discovery of the nail hoard was",
                "options": "[A]immediately understood. [B]carefully calculated. [C]logically anticipated. [D]entirely unexpected.",
                "correct_answer": "[D]entirely unexpected",
                "distractor_options": "[A]immediately understood. [B]carefully calculated. [C]logically anticipated."
            },
            {
                "number": 41,
                "section_type": "新题型",
                "stem": "According to the passage, the old view of creativity saw it as",
                "options": "[A]an inborn talent. [B]a mysterious process. [C]a divine endowment. [D]a rare achievement.",
                "correct_answer": "[C]a divine endowment",
                "distractor_options": "[A]an inborn talent. [B]a mysterious process. [D]a rare achievement."
            }
        ]
    }

def process_and_save_mock_data(output_dir="./test_results"):
    """
    处理和保存模拟数据以测试更新后的功能
    
    Args:
        output_dir (str): 输出目录
    """
    # 设置日志
    logger = setup_logging("info")
    logger.info("开始测试原文字段处理")
    
    # 确保输出目录存在
    ensure_directory_exists(output_dir)
    
    try:
        # 创建模拟数据
        mock_data = create_sample_data()
        
        # 保存模拟数据
        mock_data_file = os.path.join(output_dir, "mock_original_text_data.json")
        with open(mock_data_file, "w", encoding="utf-8") as f:
            json.dump(mock_data, f, ensure_ascii=False, indent=2)
        logger.info(f"模拟数据已保存到: {mock_data_file}")
        
        # 使用内容分析器处理数据
        content_analyzer = ContentAnalyzer()
        parsed_data = mock_data  # 直接使用模拟数据，不需要解析
        
        # 使用数据组织器处理数据
        data_organizer = DataOrganizer()
        organized_data = data_organizer.organize_data(parsed_data)
        
        # 保存组织后的数据
        organized_data_file = os.path.join(output_dir, "organized_original_text_data.json")
        with open(organized_data_file, "w", encoding="utf-8") as f:
            json.dump(organized_data, f, ensure_ascii=False, indent=2)
        logger.info(f"组织后的数据已保存到: {organized_data_file}")
        
        # 生成CSV文件
        csv_generator = CSVGenerator()
        csv_file = os.path.join(output_dir, "test_original_text.csv")
        success = csv_generator.generate_csv(organized_data, csv_file)
        
        if success:
            logger.info(f"成功生成CSV文件: {csv_file}")
            # 创建预览
            preview = csv_generator.preview_data(organized_data)
            preview_file = os.path.join(output_dir, "original_text_preview.txt")
            with open(preview_file, "w", encoding="utf-8") as f:
                f.write(preview)
            logger.info(f"数据预览已保存到: {preview_file}")
        else:
            logger.error("生成CSV文件失败")
    
    except Exception as e:
        logger.exception(f"测试过程中出错: {str(e)}")
        raise

if __name__ == "__main__":
    # 运行测试
    process_and_save_mock_data()
    print("测试完成！") 