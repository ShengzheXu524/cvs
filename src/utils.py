#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
工具函数模块，提供各种辅助功能。
"""

import os
import logging
import json
from dotenv import load_dotenv
from pathlib import Path

def setup_logging(log_level="info"):
    """
    设置日志记录级别和格式。
    
    Args:
        log_level (str): 日志级别，可以是 'debug', 'info', 'warning', 'error'
    
    Returns:
        logging.Logger: 配置好的日志记录器
    """
    log_levels = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING,
        "error": logging.ERROR
    }
    
    level = log_levels.get(log_level.lower(), logging.INFO)
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    return logging.getLogger("考研英语真题处理")

def load_api_key():
    """
    从环境变量或.env文件加载API密钥。
    
    Returns:
        str: Claude API密钥
    """
    load_dotenv()
    api_key = os.getenv("CLAUDE_API_KEY")
    
    if not api_key:
        raise ValueError("未找到Claude API密钥。请在.env文件中设置CLAUDE_API_KEY或通过参数提供。")
    
    return api_key

def ensure_directory_exists(file_path):
    """
    确保文件的目录存在，如果不存在则创建。
    
    Args:
        file_path (str): 文件路径
    """
    directory = os.path.dirname(file_path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)

def get_all_docx_files(directory):
    """
    获取目录中所有的.docx文件。
    
    Args:
        directory (str): 目录路径
    
    Returns:
        list: 所有.docx文件的路径列表
    """
    return [
        os.path.join(directory, file)
        for file in os.listdir(directory)
        if file.endswith('.docx')
    ]

def extract_exam_info_from_filename(filename):
    """
    从文件名中提取考试年份和类型信息。
    
    Args:
        filename (str): 文件名
    
    Returns:
        tuple: (年份, 考试类型)
    """
    basename = os.path.basename(filename)
    name_without_ext = os.path.splitext(basename)[0]
    
    # 尝试从文件名中提取年份和类型
    # 假设文件名格式为: 2023英语一.docx 或 2022考研英语(一).docx
    year = ""
    exam_type = ""
    
    # 提取年份 (通常是文件名开头的4位数字)
    for i, char in enumerate(name_without_ext):
        if char.isdigit() and len(year) < 4:
            year += char
        elif year and len(year) >= 4:
            break
    
    # 提取考试类型 (查找"英语一"或"英语（一）"等模式)
    if "英语一" in name_without_ext or "英语(一)" in name_without_ext or "英语（一）" in name_without_ext:
        exam_type = "英语（一）"
    elif "英语二" in name_without_ext or "英语(二)" in name_without_ext or "英语（二）" in name_without_ext:
        exam_type = "英语（二）"
    else:
        exam_type = "未知类型"
    
    return year, exam_type

def save_json_debug(data, filename):
    """
    将数据以JSON格式保存到文件，用于调试。
    
    Args:
        data (dict): 要保存的数据
        filename (str): 文件路径
    """
    ensure_directory_exists(filename)
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def make_output_path(input_path, output_dir, ext=".csv"):
    """
    根据输入文件路径和输出目录创建输出文件路径。
    
    Args:
        input_path (str): 输入文件路径
        output_dir (str): 输出目录
        ext (str): 输出文件扩展名
    
    Returns:
        str: 输出文件路径
    """
    basename = os.path.basename(input_path)
    name_without_ext = os.path.splitext(basename)[0]
    return os.path.join(output_dir, f"{name_without_ext}{ext}")

def get_question_type(question_number):
    """
    根据题号确定题型。
    
    Args:
        question_number (int): 题号(1-52)
    
    Returns:
        str: 题型描述
    """
    if 1 <= question_number <= 20:
        return "完形填空"
    elif 21 <= question_number <= 25:
        return "阅读 Text 1"
    elif 26 <= question_number <= 30:
        return "阅读 Text 2"
    elif 31 <= question_number <= 35:
        return "阅读 Text 3"
    elif 36 <= question_number <= 40:
        return "阅读 Text 4"
    elif 41 <= question_number <= 45:
        return "新题型"
    elif 46 <= question_number <= 50:
        return "翻译"
    elif question_number == 51:
        return "写作A"
    elif question_number == 52:
        return "写作B"
    else:
        return "未知题型" 