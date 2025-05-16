#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
数据处理模块，整合提取和CSV生成流程
"""

import os
import json
import logging
import time
from datetime import datetime
from pathlib import Path

from src.content_analyzer import ContentAnalyzer
from src.openrouter_handler import OpenRouterHandler
from src.data_organizer import DataOrganizer
from src.csv_generator import CSVGenerator
from src.sentence_splitter import split_sentences
from src.docx_reader import DocxReader

# 配置日志
logger = logging.getLogger("data_processor")

class DataProcessor:
    """
    数据处理器，整合从原始文档到最终CSV文件的完整处理流程
    """
    
    def __init__(self, model_name=None, max_tokens=4096, temperature=0.1):
        """
        初始化数据处理器
        
        Args:
            model_name: API模型名称，如果为None则使用环境变量中的默认值
            max_tokens: 最大令牌数
            temperature: 生成温度
        """
        # 初始化API处理器
        self.api_handler = OpenRouterHandler(model=model_name)
        
        # 初始化内容分析器
        self.content_analyzer = ContentAnalyzer(api_handler=self.api_handler, 
                                               max_tokens=max_tokens,
                                               temperature=temperature)
        
        # 初始化数据组织器
        self.data_organizer = DataOrganizer()
        
        # 初始化CSV生成器
        self.csv_generator = CSVGenerator()
        
        # 初始化docx读取器
        self.docx_reader = DocxReader()
    
    def process_document(self, document_path, output_dir="test_results", save_debug=False):
        """
        处理文档并生成CSV文件
        
        Args:
            document_path: 文档路径
            output_dir: 输出目录
            save_debug: 是否保存调试信息
        
        Returns:
            tuple: (是否成功, CSV文件路径, 处理时间)
        """
        logger.info(f"开始处理文档: {document_path}")
        start_time = time.time()
        
        try:
            # 确保输出目录存在
            os.makedirs(output_dir, exist_ok=True)
            os.makedirs(os.path.join(output_dir, "debug"), exist_ok=True)
            os.makedirs(os.path.join(output_dir, "analysis"), exist_ok=True)
            
            # 检查文件类型
            file_extension = Path(document_path).suffix.lower()
            
            # 读取文档内容
            if file_extension == '.docx':
                logger.info("检测到Word文档，使用DocxReader读取内容")
                document_text = self.docx_reader.read_file(document_path)
                
                # 如果需要调试，保存提取的文本
                if save_debug:
                    extracted_text_path = os.path.join(output_dir, "debug", f"{Path(document_path).stem}_extracted.txt")
                    with open(extracted_text_path, 'w', encoding='utf-8') as f:
                        f.write(document_text)
                    logger.info(f"提取的文本已保存到: {extracted_text_path}")
                
                # 尝试从文档结构中提取元数据
                structure = self.docx_reader.read_file_with_structure(document_path)
                if structure and "metadata" in structure:
                    metadata = structure["metadata"]
                    logger.info(f"从文档中提取的元数据: {metadata}")
            else:
                logger.info("检测到文本文件，直接读取内容")
                with open(document_path, 'r', encoding='utf-8') as f:
                    document_text = f.read()
            
            # 提取数据
            extract_start_time = time.time()
            result = self.content_analyzer.extract_data(document_text, save_debug=save_debug, output_dir=output_dir)
            extract_time = time.time() - extract_start_time
            logger.info(f"数据提取耗时: {extract_time:.2f}秒")
            
            # 保存提取结果
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            result_path = os.path.join(output_dir, "analysis", f"extraction_result_{timestamp}.json")
            with open(result_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            logger.info(f"提取结果已保存到: {result_path}")
            
            # 组织数据
            organize_start_time = time.time()
            organized_data = self.data_organizer.organize_data(result)
            
            # 确保数据集完整
            complete_data = self.data_organizer.ensure_complete_dataset(organized_data)
            
            # 应用句子拆分
            processed_data = self.data_organizer.apply_sentence_splitter(complete_data, split_sentences)
            organize_time = time.time() - organize_start_time
            logger.info(f"数据组织耗时: {organize_time:.2f}秒")
            
            # 保存组织后的数据
            organized_path = os.path.join(output_dir, "analysis", f"organized_data_{timestamp}.json")
            with open(organized_path, 'w', encoding='utf-8') as f:
                json.dump(processed_data, f, ensure_ascii=False, indent=2)
            logger.info(f"组织后的数据已保存到: {organized_path}")
            
            # 获取文件名（不含扩展名）
            file_name = os.path.splitext(os.path.basename(document_path))[0]
            
            # 确定CSV文件名
            year = result.get("metadata", {}).get("year", "未知年份")
            exam_type = result.get("metadata", {}).get("exam_type", "未知类型")
            csv_filename = f"{year}{exam_type}.csv"
            csv_path = os.path.join(output_dir, csv_filename)
            
            # 生成CSV文件
            csv_start_time = time.time()
            csv_success = self.csv_generator.generate_csv(processed_data, csv_path)
            csv_time = time.time() - csv_start_time
            logger.info(f"CSV生成耗时: {csv_time:.2f}秒")
            
            if csv_success:
                logger.info(f"成功生成CSV文件: {csv_path}")
            else:
                logger.error("CSV生成失败")
                return False, None, time.time() - start_time
            
            # 计算总处理时间
            total_time = time.time() - start_time
            logger.info(f"文档处理完成，总耗时: {total_time:.2f}秒")
            
            return True, csv_path, total_time
            
        except Exception as e:
            logger.error(f"处理文档时出错: {str(e)}", exc_info=True)
            return False, None, time.time() - start_time
    
    def batch_process(self, input_dir, output_dir="test_results", file_pattern="*.txt;*.docx", save_debug=False):
        """
        批量处理目录下的文档
        
        Args:
            input_dir: 输入目录
            output_dir: 输出目录
            file_pattern: 文件匹配模式，多个模式用分号分隔
            save_debug: 是否保存调试信息
        
        Returns:
            list: 处理结果列表，每个元素为(文件名, 是否成功, CSV路径, 处理时间)
        """
        import glob
        import re
        
        logger.info(f"开始批量处理目录: {input_dir}")
        
        # 拆分文件模式
        patterns = file_pattern.split(';')
        
        # 获取所有匹配的文件
        all_files = []
        for pattern in patterns:
            pattern = pattern.strip()
            if pattern:
                matched_files = glob.glob(os.path.join(input_dir, pattern))
                all_files.extend(matched_files)
        
        # 去重并排序
        all_files = sorted(set(all_files))
        logger.info(f"找到 {len(all_files)} 个匹配的文件")
        
        results = []
        for file_path in all_files:
            file_name = os.path.basename(file_path)
            logger.info(f"处理文件: {file_name}")
            
            # 尝试从文件名提取年份
            year_match = re.search(r'(\d{4})', file_name)
            year = year_match.group(1) if year_match else "unknown"
            
            # 设置输出目录
            file_output_dir = os.path.join(output_dir, year)
            
            success, csv_path, process_time = self.process_document(
                document_path=file_path,
                output_dir=file_output_dir,
                save_debug=save_debug
            )
            
            results.append((file_name, success, csv_path, process_time))
            
            # 如果成功，记录结果
            if success:
                logger.info(f"文件 {file_name} 处理成功，耗时: {process_time:.2f}秒，CSV: {csv_path}")
            else:
                logger.error(f"文件 {file_name} 处理失败，耗时: {process_time:.2f}秒")
        
        # 输出汇总信息
        successful = sum(1 for _, success, _, _ in results if success)
        logger.info(f"批量处理完成，成功: {successful}/{len(results)}")
        
        return results 