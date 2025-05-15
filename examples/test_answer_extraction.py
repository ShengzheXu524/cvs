#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试改进后的答案解析功能和题目自动补全功能。
"""

import os
import sys
import json
import logging
from pathlib import Path

# 添加src目录到路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.data_organizer import DataOrganizer

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

def create_mock_data_with_various_answers():
    """
    创建包含各种答案格式的模拟数据
    
    Returns:
        dict: 模拟数据
    """
    return {
        "metadata": {
            "year": "2023",
            "exam_type": "英语（一）"
        },
        "sections": {
            "cloze": {
                "original_text": "This is the complete cloze test passage with blanks: [1] learning a second language, [2] learners make what are called inter-language [3].",
                "restored_text": "This is the complete cloze test passage with answers filled in: When learning a second language, all learners make what are called inter-language errors.",
                "answers_summary": "1.A 2.B 3.C 4-D 5:A 6A 7.B"
            },
            "reading": {
                "text_1": {
                    "original_text": "This is the complete reading text 1 passage: The study of language acquisition...",
                    "answers_summary": "21.D 22.D 23.A"
                },
                "text_2": {
                    "original_text": "This is the complete reading text 2 passage: The effects of climate change...",
                    "answers_summary": "26.C 27.B"
                }
            }
        },
        "questions": [
            {
                "number": 1,
                "section_type": "完形填空",
                "stem": "/",
                "options": "A. When, B. After, C. Before, D. While",
                "correct_answer": "A. When",
                "distractor_options": "B. After, C. Before, D. While"
            },
            {
                "number": 2,
                "section_type": "完形填空",
                "stem": "/",
                "options": "A. few, B. all, C. some, D. many",
                "correct_answer": "B. all",
                "distractor_options": "A. few, C. some, D. many"
            },
            {
                "number": 21,
                "section_type": "阅读理解",
                "stem": "The main topic of this passage is",
                "options": "[A]language teaching. [B]child development. [C]educational policy. [D]language acquisition.",
                "correct_answer": "[D]language acquisition",
                "distractor_options": "[A]language teaching. [B]child development. [C]educational policy."
            }
        ]
    }

def test_parse_answers_summary():
    """测试答案汇总解析功能"""
    logger = setup_logging("info")
    logger.info("测试答案汇总解析功能")
    
    data_organizer = DataOrganizer()
    
    # 测试各种格式的答案汇总
    test_cases = [
        "1.A 2.B 3.C 4.D 5.A",
        "1-A 2-B 3-C 4-D 5-A",
        "1:A 2:B 3:C 4:D 5:A",
        "1A 2B 3C 4D 5A",
        "1.[A] 2.[B] 3.[C] 4.[D] 5.[A]",
        "1. A, 2. B, 3. C, 4. D, 5. A",
        "答案：1.A 2.B 3.C 4.D 5.A",
        "1.A. Option 2.B. Option 3.C. Option"
    ]
    
    for i, case in enumerate(test_cases):
        logger.info(f"测试案例 {i+1}: {case}")
        result = data_organizer._parse_answers_summary(case)
        logger.info(f"结果: {result}")
        
    logger.info("答案汇总解析测试完成")

def test_parse_individual_answer():
    """测试单个答案解析功能"""
    logger = setup_logging("info")
    logger.info("测试单个答案解析功能")
    
    data_organizer = DataOrganizer()
    
    # 准备测试数据
    answer_mappings = {
        1: "A",
        2: "B. Option",
        3: "[C]",
        4: "D. Long option description"
    }
    
    test_cases = [
        (1, "A. Option", answer_mappings),  # 应该使用映射中的简单答案 "A"
        (2, "C. Wrong", answer_mappings),   # 应该使用映射中的答案，提取出"B"
        (3, "", answer_mappings),           # 应该使用映射中的答案，提取出"C"
        (4, "A. Wrong", answer_mappings),   # 应该使用映射中的答案，提取出"D"
        (5, "B. Option", {}),               # 映射为空，使用correct_answer提取"B"
        (6, "[C]Option", {}),               # 使用correct_answer提取"C"
        (7, "D", {}),                       # 使用原始correct_answer "D"
        (8, "", {})                         # 应该返回空字符串
    ]
    
    for i, (number, correct_answer, mapping) in enumerate(test_cases):
        logger.info(f"测试案例 {i+1}: 题号={number}, correct_answer='{correct_answer}'")
        result = data_organizer._parse_individual_answer(number, correct_answer, mapping)
        logger.info(f"结果: '{result}'")
        
    logger.info("单个答案解析测试完成")

def test_complete_question_set():
    """测试题目集自动补全功能"""
    logger = setup_logging("info")
    logger.info("测试题目集自动补全功能")
    
    # 创建数据组织器
    data_organizer = DataOrganizer()
    
    # 创建包含少量题目的模拟数据
    mock_data = create_mock_data_with_various_answers()
    
    # 处理模拟数据
    logger.info("处理包含少量题目的模拟数据")
    organized_data = data_organizer._process_new_format(mock_data)
    
    # 输出每道题目的编号和各个字段值
    logger.info(f"处理后的题目数: {len(organized_data)}")
    logger.info("题目编号列表: " + ", ".join([q["题目编号"] for q in organized_data]))
    
    # 检查特定题目的数据
    for num in [1, 2, 21, 25, 30, 40, 52]:  # 抽样检查一些题号
        for q in organized_data:
            if q["题目编号"] == str(num):
                logger.info(f"题号 {num}:")
                logger.info(f"  题型: {q['题型']}")
                logger.info(f"  题干: {q['题干'][:50]}...")
                logger.info(f"  试卷答案: {q['试卷答案']}")
                logger.info(f"  原文是否有内容: {'是' if q['原文（卷面）'] else '否'}")
                break
    
    logger.info("题目集自动补全测试完成")

def main():
    """主函数，运行所有测试"""
    ensure_directory_exists("./test_results")
    
    # 测试答案汇总解析
    test_parse_answers_summary()
    
    # 测试单个答案解析
    test_parse_individual_answer()
    
    # 测试题目集自动补全
    test_complete_question_set()

if __name__ == "__main__":
    main()
    print("所有测试完成!") 