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
import time
from datetime import datetime
from pathlib import Path

# 导入自定义模块
from docx_reader import DocxReader
from openrouter_api import OpenRouterAPI
from data_organizer import DataOrganizer
from csv_generator import CSVGenerator
from sentence_splitter import SentenceSplitter, split_sentences
from content_analyzer import ContentAnalyzer
from utils import setup_logging, ensure_directory_exists

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("test_module")

# 添加父目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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

def test_openrouter_api(text, api_key, output_dir="./test_results"):
    """
    测试OpenRouterAPI模块。
    
    Args:
        text (str): 要发送给API的文本
        api_key (str): OpenRouter API密钥
        output_dir (str): 测试结果输出目录
    """
    print("\n测试OpenRouterAPI模块...")
    
    try:
        # 创建输出目录
        ensure_directory_exists(output_dir)
        
        # 初始化OpenRouterAPI
        openrouter_api = OpenRouterAPI(api_key=api_key)
        
        # 发送文本到API
        print("正在发送请求到OpenRouter API...")
        response = openrouter_api.analyze_document(text)
        
        # 保存API响应到JSON文件
        output_path = os.path.join(output_dir, "openrouter_api_response.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(response, f, ensure_ascii=False, indent=2)
        
        print(f"API响应已保存到 {output_path}")
        
        return True
    except Exception as e:
        print(f"测试OpenRouterAPI失败: {str(e)}")
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
    测试完整的处理流程。
    
    Args:
        file_path (str): 要处理的docx文件路径
        api_key (str): API密钥
        output_dir (str): 测试结果输出目录
    """
    print("\n测试完整处理流程...")
    
    try:
        # 创建输出目录
        ensure_directory_exists(output_dir)
        
        # 读取文件
        docx_reader = DocxReader()
        content = docx_reader.read_file(file_path)
        
        # 发送到API
        openrouter_api = OpenRouterAPI(api_key=api_key)
        print("正在发送请求到OpenRouter API...")
        api_response = openrouter_api.extract_structured_data(content)
        
        # 如果返回了错误，打印详细信息并终止测试
        if "error" in api_response:
            print(f"API请求失败: {api_response['error']}")
            # 保存错误信息
            error_path = os.path.join(output_dir, "api_error.json")
            with open(error_path, "w", encoding="utf-8") as f:
                json.dump(api_response, f, ensure_ascii=False, indent=2)
            print(f"错误信息已保存到 {error_path}")
            return False
            
        # 保存API响应
        api_response_path = os.path.join(output_dir, "api_response.json")
        with open(api_response_path, "w", encoding="utf-8") as f:
            json.dump(api_response, f, ensure_ascii=False, indent=2)
        print(f"API响应已保存到 {api_response_path}")
        
        # 解析API响应
        print("3. 解析API响应...")
        analyzer = ContentAnalyzer()
        questions = analyzer.parse_response(api_response)
        
        # 保存解析结果
        with open(os.path.join(output_dir, "pipeline_parsed_questions.json"), "w", encoding="utf-8") as f:
            json.dump(questions, f, ensure_ascii=False, indent=2)
        
        # 组织数据
        print("4. 组织数据...")
        organizer = DataOrganizer()
        organized_data = organizer.organize_data(questions)
        
        # 保存组织后的数据
        with open(os.path.join(output_dir, "pipeline_organized_data.json"), "w", encoding="utf-8") as f:
            json.dump(organized_data, f, ensure_ascii=False, indent=2)
        
        # 确保数据完整
        print("5. 确保数据完整...")
        complete_data = organizer.ensure_complete_dataset(organized_data)
        
        # 保存完整数据
        with open(os.path.join(output_dir, "pipeline_complete_data.json"), "w", encoding="utf-8") as f:
            json.dump(complete_data, f, ensure_ascii=False, indent=2)
        
        # 应用句子拆分
        print("6. 应用句子拆分...")
        data_with_split = organizer.apply_sentence_splitter(complete_data, split_sentences)
        
        # 保存拆分后的数据
        with open(os.path.join(output_dir, "pipeline_split_data.json"), "w", encoding="utf-8") as f:
            json.dump(data_with_split, f, ensure_ascii=False, indent=2)
        
        # 生成CSV
        print("7. 生成CSV...")
        generator = CSVGenerator()
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

def test_document_length_detection(document_path, output_dir="test_results"):
    """
    测试文档长度检测功能
    
    Args:
        document_path: 文档路径
        output_dir: 输出目录
    """
    from src.openrouter_handler import OpenRouterHandler
    from src.content_analyzer import ContentAnalyzer
    
    logger.info(f"开始测试文档长度检测功能，使用文档: {document_path}")
    
    try:
        # 读取文档内容
        with open(document_path, 'r', encoding='utf-8') as f:
            document_text = f.read()
        
        # 获取文档长度
        doc_length = len(document_text)
        logger.info(f"文档长度: {doc_length} 字符")
        
        # 初始化API处理器（使用模拟模式，不实际调用API）
        class MockOpenRouterHandler:
            def __init__(self, model=None):
                self.model = model or "mock_model"
                self.calls = []
            
            def get_structured_data(self, prompt, max_tokens=4096, temperature=0.1):
                # 记录调用
                self.calls.append({
                    "prompt": prompt,
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                    "timestamp": datetime.now().isoformat()
                })
                
                # 返回模拟数据
                return {
                    "metadata": {"year": "2024", "exam_type": "英语（一）"},
                    "sections": {},
                    "questions": [{"number": i} for i in range(1, 53)]
                }
        
        # 创建模拟处理器
        mock_handler = MockOpenRouterHandler()
        
        # 初始化内容分析器
        content_analyzer = ContentAnalyzer(api_handler=mock_handler)
        
        # 执行数据提取
        start_time = time.time()
        result = content_analyzer.extract_data(document_text, save_debug=True, output_dir=output_dir)
        elapsed_time = time.time() - start_time
        
        # 检查API调用方式
        if doc_length > 3000:
            # 对于长文档，应该直接使用分段处理
            if len(mock_handler.calls) >= 2:
                logger.info(f"✅ 文档长度 {doc_length} > 3000 字符，正确使用了分段处理")
                
                # 检查是否使用了分段提示词
                first_prompt = mock_handler.calls[0]["prompt"]
                if "仅提取题目1-25" in first_prompt:
                    logger.info("✅ 第一次调用正确使用了分段提示词（提取题目1-25）")
                else:
                    logger.warning("❌ 第一次调用没有使用分段提示词")
                
                # 检查第二次调用
                if len(mock_handler.calls) > 1:
                    second_prompt = mock_handler.calls[1]["prompt"]
                    if "仅提取题目26-52" in second_prompt:
                        logger.info("✅ 第二次调用正确使用了分段提示词（提取题目26-52）")
                    else:
                        logger.warning("❌ 第二次调用没有使用分段提示词")
            else:
                logger.warning(f"❌ 文档长度 {doc_length} > 3000 字符，但没有使用分段处理（API调用次数不足）")
        else:
            # 对于短文档，可能先尝试完整提取，再尝试分段提取
            if len(mock_handler.calls) == 1:
                logger.info(f"✅ 文档长度 {doc_length} <= 3000 字符，正确使用了一次性提取")
            else:
                logger.info(f"✅ 文档长度 {doc_length} <= 3000 字符，先尝试一次性提取，然后进行分段提取")
        
        logger.info(f"测试完成，总API调用次数: {len(mock_handler.calls)}，耗时: {elapsed_time:.2f} 秒")
        return True
        
    except Exception as e:
        logger.error(f"测试过程中出错: {str(e)}", exc_info=True)
        return False

def main():
    """程序主入口。"""
    # 设置命令行参数解析
    parser = argparse.ArgumentParser(description="测试考研英语真题处理工具的各个模块")
    
    parser.add_argument("--output", default="./test_results", help="测试结果输出目录")
    parser.add_argument("--docx", help="要处理的docx文件路径")
    parser.add_argument("--api_key", help="API密钥")
    parser.add_argument("--module", choices=["docx_reader", "sentence_splitter", "openrouter_api",
                                           "data_organizer", "csv_generator",
                                           "content_analyzer", "full", "all"],
                       required=True, help="要测试的模块")
    parser.add_argument("--log", choices=["debug", "info", "warning", "error"],
                       default="info", help="日志级别")
    
    args = parser.parse_args()
    
    # 设置日志
    setup_logging(args.log)
    
    # 检查必要的参数
    if args.module in ["openrouter_api", "full", "all"] and not args.api_key:
        print("错误: 测试API模块需要提供API密钥")
        return 1
    
    if args.module in ["docx_reader", "full", "all"] and not args.docx:
        print("错误: 测试DocxReader模块需要提供docx文件路径")
        return 1
    
    # 运行测试
    if args.module == "docx_reader" or args.module == "all":
        test_docx_reader(args.docx, args.output)
    
    if args.module == "sentence_splitter" or args.module == "all":
        if args.docx:
            # 如果提供了docx文件，使用它的内容进行测试
            reader = DocxReader()
            content = reader.read_file(args.docx)
            test_sentence_splitter(content, args.output)
        else:
            # 否则使用默认示例文本
            test_sentence_splitter(None, args.output)
    
    if args.module == "openrouter_api" or args.module == "all":
        if args.docx and args.api_key:
            reader = DocxReader()
            content = reader.read_file(args.docx)
            test_openrouter_api(content, args.api_key, args.output)
        else:
            print("跳过OpenRouterAPI测试，未提供API密钥或docx文件路径")
            
    if args.module == "data_organizer" or args.module == "all":
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
        test_data_organizer(example_data, args.output)
    
    if args.module == "csv_generator" or args.module == "all":
        test_csv_generator(example_data, args.output)
    
    if args.module == "content_analyzer" or args.module == "all":
        test_content_analyzer(example_data, args.output)
    
    if args.module == "full" or args.module == "all":
        if args.api_key and args.docx:
            test_full_pipeline(args.docx, args.api_key, args.output)
        else:
            print("跳过完整流程测试，未提供API密钥或docx文件路径")
    
    print("\n测试完成。")

if __name__ == "__main__":
    main() 