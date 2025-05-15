#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试模块，用于验证考研英语真题处理工具的各个模块功能。
"""

import os
import sys
import json
import logging
import argparse
from pathlib import Path

# 导入自定义模块
from docx_reader import DocxReader
from claude_api import ClaudeAPI
from data_organizer import DataOrganizer
from csv_generator import CSVGenerator
from sentence_splitter import SentenceSplitter, split_sentences
from content_analyzer import ContentAnalyzer
from utils import setup_logging, ensure_directory_exists

def test_docx_reader(file_path, output_dir="./test_results"):
    """
    测试DocxReader模块。
    
    Args:
        file_path (str): 要测试的docx文件路径
        output_dir (str): 测试结果输出目录
    """
    print("\n测试DocxReader模块...")
    
    try:
        # 创建输出目录
        ensure_directory_exists(output_dir)
        
        # 初始化DocxReader
        reader = DocxReader()
        
        # 读取文件内容
        content = reader.read_file(file_path)
        
        # 保存提取的内容到文本文件
        output_path = os.path.join(output_dir, "docx_reader_result.txt")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        print(f"文件内容已成功提取并保存到 {output_path}")
        print(f"提取的字符数: {len(content)}")
        
        # 读取带结构信息的文件内容
        structured_content = reader.read_file_with_structure(file_path)
        
        # 保存结构化内容到JSON文件
        output_path = os.path.join(output_dir, "docx_reader_structured_result.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(structured_content, f, ensure_ascii=False, indent=2)
        
        print(f"结构化内容已保存到 {output_path}")
        
        return True
    except Exception as e:
        print(f"测试DocxReader失败: {str(e)}")
        return False

def test_sentence_splitter(text=None, output_dir="./test_results"):
    """
    测试SentenceSplitter模块。
    
    Args:
        text (str): 要拆分的文本，如果为None则使用示例文本
        output_dir (str): 测试结果输出目录
    """
    print("\n测试SentenceSplitter模块...")
    
    try:
        # 创建输出目录
        ensure_directory_exists(output_dir)
        
        # 使用示例文本（如果未提供文本）
        if text is None:
            text = """
            The importance of English as a global language is undeniable. It serves as a bridge between different cultures and nations. More than a quarter of the world's population speaks English with some degree of competence.
            In academic settings, English is often the language of instruction. Research papers are frequently published in English. This allows scholars from different countries to share their findings.
            """
        
        # 初始化SentenceSplitter
        splitter = SentenceSplitter()
        
        # 使用默认方法拆分句子
        split_text = splitter.split_text(text)
        
        # 保存拆分结果到文本文件
        output_path = os.path.join(output_dir, "sentence_splitter_result.txt")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("原始文本:\n")
            f.write(text)
            f.write("\n\n拆分结果:\n")
            f.write(split_text)
        
        print(f"句子拆分结果已保存到 {output_path}")
        
        # 使用自定义方法拆分句子
        custom_split_text = splitter.split_text_custom(text)
        
        # 保存自定义拆分结果到文本文件
        output_path = os.path.join(output_dir, "sentence_splitter_custom_result.txt")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("原始文本:\n")
            f.write(text)
            f.write("\n\n自定义拆分结果:\n")
            f.write(custom_split_text)
        
        print(f"自定义句子拆分结果已保存到 {output_path}")
        
        # 使用保留上下文的方法拆分句子
        context_split_text = splitter.split_text_with_context(text)
        
        # 保存上下文拆分结果到文本文件
        output_path = os.path.join(output_dir, "sentence_splitter_context_result.txt")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("原始文本:\n")
            f.write(text)
            f.write("\n\n带上下文拆分结果:\n")
            f.write(context_split_text)
        
        print(f"带上下文句子拆分结果已保存到 {output_path}")
        
        return True
    except Exception as e:
        print(f"测试SentenceSplitter失败: {str(e)}")
        return False

def test_claude_api(text, api_key, output_dir="./test_results"):
    """
    测试ClaudeAPI模块。
    
    Args:
        text (str): 要发送给API的文本
        api_key (str): Claude API密钥
        output_dir (str): 测试结果输出目录
    """
    print("\n测试ClaudeAPI模块...")
    
    try:
        # 创建输出目录
        ensure_directory_exists(output_dir)
        
        # 初始化ClaudeAPI
        claude_api = ClaudeAPI(api_key=api_key)
        
        # 发送文本到API
        print("正在发送请求到Claude API...")
        response = claude_api.analyze_document(text)
        
        # 保存API响应到JSON文件
        output_path = os.path.join(output_dir, "claude_api_response.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(response, f, ensure_ascii=False, indent=2)
        
        print(f"API响应已保存到 {output_path}")
        
        return True
    except Exception as e:
        print(f"测试ClaudeAPI失败: {str(e)}")
        return False

def test_data_organizer(data, output_dir="./test_results"):
    """
    测试DataOrganizer模块。
    
    Args:
        data (dict): 要组织的数据
        output_dir (str): 测试结果输出目录
    """
    print("\n测试DataOrganizer模块...")
    
    try:
        # 创建输出目录
        ensure_directory_exists(output_dir)
        
        # 初始化DataOrganizer
        organizer = DataOrganizer()
        
        # 组织数据
        organized_data = organizer.organize_data(data)
        
        # 保存组织后的数据到JSON文件
        output_path = os.path.join(output_dir, "data_organizer_result.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(organized_data, f, ensure_ascii=False, indent=2)
        
        print(f"组织后的数据已保存到 {output_path}")
        
        # 验证数据
        is_valid, message = organizer.validate_data(organized_data)
        print(f"数据验证结果: {message}")
        
        # 确保数据完整性
        complete_data = organizer.ensure_complete_dataset(organized_data)
        
        # 保存完整数据到JSON文件
        output_path = os.path.join(output_dir, "data_organizer_complete_result.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(complete_data, f, ensure_ascii=False, indent=2)
        
        print(f"完整数据已保存到 {output_path}")
        
        return True
    except Exception as e:
        print(f"测试DataOrganizer失败: {str(e)}")
        return False

def test_csv_generator(data, output_dir="./test_results"):
    """
    测试CSVGenerator模块。
    
    Args:
        data (list): 要生成CSV的数据
        output_dir (str): 测试结果输出目录
    """
    print("\n测试CSVGenerator模块...")
    
    try:
        # 创建输出目录
        ensure_directory_exists(output_dir)
        
        # 初始化CSVGenerator
        generator = CSVGenerator()
        
        # 生成CSV文件
        output_path = os.path.join(output_dir, "csv_generator_result.csv")
        success = generator.generate_csv(data, output_path)
        
        if success:
            print(f"CSV文件已成功生成: {output_path}")
        else:
            print("CSV文件生成失败")
        
        # 预览数据
        preview = generator.preview_data(data)
        
        # 保存预览到文本文件
        preview_path = os.path.join(output_dir, "csv_preview.txt")
        with open(preview_path, "w", encoding="utf-8") as f:
            f.write(preview)
        
        print(f"数据预览已保存到 {preview_path}")
        
        return success
    except Exception as e:
        print(f"测试CSVGenerator失败: {str(e)}")
        return False

def test_content_analyzer(response_text, output_dir="./test_results"):
    """
    测试ContentAnalyzer模块。
    
    Args:
        response_text (str): API响应文本
        output_dir (str): 测试结果输出目录
    """
    print("\n测试ContentAnalyzer模块...")
    
    try:
        # 创建输出目录
        ensure_directory_exists(output_dir)
        
        # 初始化ContentAnalyzer
        analyzer = ContentAnalyzer()
        
        # 解析响应
        questions = analyzer.parse_response(response_text)
        
        # 保存解析结果到JSON文件
        output_path = os.path.join(output_dir, "content_analyzer_result.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(questions, f, ensure_ascii=False, indent=2)
        
        print(f"解析结果已保存到 {output_path}")
        
        # 增强题目数据
        enhanced_questions = analyzer.enhance_question_data(questions)
        
        # 保存增强结果到JSON文件
        output_path = os.path.join(output_dir, "content_analyzer_enhanced_result.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(enhanced_questions, f, ensure_ascii=False, indent=2)
        
        print(f"增强结果已保存到 {output_path}")
        
        return True
    except Exception as e:
        print(f"测试ContentAnalyzer失败: {str(e)}")
        return False

def test_full_pipeline(file_path, api_key, output_dir="./test_results"):
    """
    测试完整处理流程。
    
    Args:
        file_path (str): 要处理的docx文件路径
        api_key (str): Claude API密钥
        output_dir (str): 测试结果输出目录
    """
    print("\n测试完整处理流程...")
    
    try:
        # 创建输出目录
        ensure_directory_exists(output_dir)
        
        # 初始化各模块
        reader = DocxReader()
        claude_api = ClaudeAPI(api_key=api_key)
        analyzer = ContentAnalyzer()
        organizer = DataOrganizer()
        generator = CSVGenerator()
        
        # 1. 读取文件
        print("1. 读取文件内容...")
        content = reader.read_file(file_path)
        
        # 保存文件内容
        with open(os.path.join(output_dir, "pipeline_file_content.txt"), "w", encoding="utf-8") as f:
            f.write(content)
        
        # 2. 调用API分析
        print("2. 调用API分析内容...")
        api_response = claude_api.extract_structured_data(content)
        
        # 保存API响应
        with open(os.path.join(output_dir, "pipeline_api_response.json"), "w", encoding="utf-8") as f:
            json.dump(api_response, f, ensure_ascii=False, indent=2)
        
        # 3. 解析API响应
        print("3. 解析API响应...")
        questions = analyzer.parse_response(api_response)
        
        # 保存解析结果
        with open(os.path.join(output_dir, "pipeline_parsed_questions.json"), "w", encoding="utf-8") as f:
            json.dump(questions, f, ensure_ascii=False, indent=2)
        
        # 4. 组织数据
        print("4. 组织数据...")
        organized_data = organizer.organize_data(questions)
        
        # 保存组织后的数据
        with open(os.path.join(output_dir, "pipeline_organized_data.json"), "w", encoding="utf-8") as f:
            json.dump(organized_data, f, ensure_ascii=False, indent=2)
        
        # 5. 确保数据完整
        print("5. 确保数据完整...")
        complete_data = organizer.ensure_complete_dataset(organized_data)
        
        # 保存完整数据
        with open(os.path.join(output_dir, "pipeline_complete_data.json"), "w", encoding="utf-8") as f:
            json.dump(complete_data, f, ensure_ascii=False, indent=2)
        
        # 6. 应用句子拆分
        print("6. 应用句子拆分...")
        data_with_split = organizer.apply_sentence_splitter(complete_data, split_sentences)
        
        # 保存拆分后的数据
        with open(os.path.join(output_dir, "pipeline_split_data.json"), "w", encoding="utf-8") as f:
            json.dump(data_with_split, f, ensure_ascii=False, indent=2)
        
        # 7. 生成CSV
        print("7. 生成CSV...")
        csv_path = os.path.join(output_dir, "pipeline_result.csv")
        success = generator.generate_csv(data_with_split, csv_path)
        
        if success:
            print(f"完整流程测试成功，CSV文件已生成: {csv_path}")
        else:
            print("CSV生成失败")
        
        return success
    except Exception as e:
        print(f"测试完整流程失败: {str(e)}")
        return False

def main():
    """主入口函数。"""
    parser = argparse.ArgumentParser(description="测试考研英语真题处理工具的各个模块功能")
    
    parser.add_argument("--docx", help="用于测试的docx文件路径")
    parser.add_argument("--api_key", help="Claude API密钥")
    parser.add_argument("--output", default="./test_results", help="测试结果输出目录")
    parser.add_argument("--module", choices=["docx_reader", "sentence_splitter", "claude_api", 
                                           "data_organizer", "csv_generator", "content_analyzer", 
                                           "full_pipeline", "all"], 
                        default="all", help="要测试的模块")
    
    args = parser.parse_args()
    
    # 设置日志
    setup_logging("debug")
    
    # 准备示例数据
    example_data = [
        {
            "年份": "2023",
            "考试类型": "英语（一）",
            "题型": "完形填空",
            "原文（卷面）": "The importance of [1] as a global language is undeniable.",
            "试卷答案": "1. A",
            "题目编号": 1,
            "题干": "",
            "选项": "A. English, B. Chinese, C. French, D. Spanish",
            "正确答案": "A. English",
            "原文（还原后）": "The importance of English as a global language is undeniable.",
            "原文（句子拆解后）": "",
            "干扰选项": "B. Chinese, C. French, D. Spanish"
        }
    ]
    
    # 根据选择的模块执行测试
    if args.module == "docx_reader" or args.module == "all":
        if args.docx:
            test_docx_reader(args.docx, args.output)
        else:
            print("跳过DocxReader测试，未提供docx文件路径")
    
    if args.module == "sentence_splitter" or args.module == "all":
        test_sentence_splitter(None, args.output)
    
    if args.module == "claude_api" or args.module == "all":
        if args.api_key and args.docx:
            # 读取文件内容用于测试
            reader = DocxReader()
            content = reader.read_file(args.docx)
            test_claude_api(content, args.api_key, args.output)
        else:
            print("跳过ClaudeAPI测试，未提供API密钥或docx文件路径")
    
    if args.module == "data_organizer" or args.module == "all":
        test_data_organizer(example_data, args.output)
    
    if args.module == "csv_generator" or args.module == "all":
        test_csv_generator(example_data, args.output)
    
    if args.module == "content_analyzer" or args.module == "all":
        test_content_analyzer(example_data, args.output)
    
    if args.module == "full_pipeline" or args.module == "all":
        if args.api_key and args.docx:
            test_full_pipeline(args.docx, args.api_key, args.output)
        else:
            print("跳过完整流程测试，未提供API密钥或docx文件路径")
    
    print("\n测试完成。")

if __name__ == "__main__":
    main() 