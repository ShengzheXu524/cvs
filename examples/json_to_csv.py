#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
简单的脚本，将JSON格式的考研英语真题数据转换为CSV格式。
"""

import os
import sys
import json
import argparse
import pandas as pd
from pathlib import Path

def convert_json_to_csv(json_file, csv_file):
    """
    将JSON格式的考研英语真题数据转换为CSV格式
    
    Args:
        json_file (str): 输入的JSON文件路径
        csv_file (str): 输出的CSV文件路径
    
    Returns:
        bool: 是否成功转换
    """
    print(f"开始将 {json_file} 转换为CSV格式...")
    
    try:
        # 读取JSON文件
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 提取元数据
        year = data.get('metadata', {}).get('year', '')
        exam_type = data.get('metadata', {}).get('exam_type', '')
        
        # 提取问题数据
        questions = data.get('questions', [])
        
        # 创建一个列表存储所有行数据
        rows = []
        
        # 处理每个问题
        for question in questions:
            number = question.get('number', '')
            section_type = question.get('section_type', '')
            stem = question.get('stem', '')
            options = question.get('options', '')
            correct_answer = question.get('correct_answer', '')
            distractor_options = question.get('distractor_options', '')
            
            # 获取对应部分的原文
            original_text = ''
            restored_text = ''
            answers_summary = ''
            
            # 根据题目类型获取原文
            if section_type in ['完型填空', '完形填空']:
                if 'cloze' in data.get('sections', {}):
                    original_text = data['sections']['cloze'].get('original_text', '')
                    restored_text = data['sections']['cloze'].get('restored_text', '')
                    answers_summary = data['sections']['cloze'].get('answers_summary', '')
            elif section_type in ['阅读理解', '阅读 Text 1']:
                if 'reading' in data.get('sections', {}) and 'text_1' in data['sections']['reading']:
                    original_text = data['sections']['reading']['text_1'].get('original_text', '')
                    restored_text = original_text  # 阅读没有还原版本
                    answers_summary = data['sections']['reading']['text_1'].get('answers_summary', '')
            elif section_type in ['阅读 Text 2']:
                if 'reading' in data.get('sections', {}) and 'text_2' in data['sections']['reading']:
                    original_text = data['sections']['reading']['text_2'].get('original_text', '')
                    restored_text = original_text
                    answers_summary = data['sections']['reading']['text_2'].get('answers_summary', '')
            # 其他题型...
            
            # 创建行数据
            row = {
                '年份': year,
                '考试类型': exam_type,
                '题型': section_type,
                '原文（卷面）': original_text,
                '试卷答案': answers_summary,
                '题目编号': number,
                '题干': stem,
                '选项': options,
                '正确答案': correct_answer,
                '原文（还原后）': restored_text,
                '原文（句子拆解后）': '',  # 这需要额外处理
                '干扰选项': distractor_options
            }
            
            rows.append(row)
        
        # 创建DataFrame
        df = pd.DataFrame(rows)
        
        # 保存为CSV
        df.to_csv(csv_file, index=False, encoding='utf-8-sig')
        
        print(f"成功将JSON数据转换为CSV，保存为: {csv_file}")
        print(f"CSV包含 {len(rows)} 行数据")
        return True
        
    except Exception as e:
        print(f"转换过程中出错: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return False

def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="将JSON格式的考研英语真题数据转换为CSV格式")
    parser.add_argument("--input", required=True, help="输入的JSON文件路径")
    parser.add_argument("--output", required=True, help="输出的CSV文件路径")
    
    args = parser.parse_args()
    
    # 转换文件
    success = convert_json_to_csv(args.input, args.output)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main()) 