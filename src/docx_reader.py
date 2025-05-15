#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
文档读取模块，负责读取docx文件并预处理文本内容。
"""

import os
import re
import docx
import logging
from pathlib import Path

logger = logging.getLogger("考研英语真题处理.docx_reader")

class DocxReader:
    """
    DOCX文件读取器，用于读取考研英语真题文档。
    """
    
    def __init__(self):
        """
        初始化文档读取器。
        """
        pass
    
    def read_file(self, file_path):
        """
        读取docx文件并提取文本内容。
        
        Args:
            file_path (str): docx文件路径
        
        Returns:
            str: 提取的文本内容
        """
        if not os.path.exists(file_path):
            logger.error(f"文件不存在: {file_path}")
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        logger.info(f"开始读取文件: {file_path}")
        
        try:
            doc = docx.Document(file_path)
            
            # 读取所有段落内容
            full_text = []
            for para in doc.paragraphs:
                if para.text.strip():  # 确保不添加空白段落
                    full_text.append(para.text)
            
            # 读取所有表格内容
            for table in doc.tables:
                for row in table.rows:
                    row_text = []
                    for cell in row.cells:
                        if cell.text.strip():  # 确保不添加空白单元格
                            row_text.append(cell.text.strip())
                    if row_text:  # 确保不添加空白行
                        full_text.append(" | ".join(row_text))
            
            all_text = "\n".join(full_text)
            logger.debug(f"提取了 {len(all_text)} 个字符")
            
            return all_text
            
        except Exception as e:
            logger.error(f"读取文件时出错: {str(e)}")
            raise
    
    def read_file_with_structure(self, file_path):
        """
        读取docx文件并尝试保留更多结构信息。
        
        Args:
            file_path (str): docx文件路径
        
        Returns:
            dict: 包含文档结构信息的字典
        """
        if not os.path.exists(file_path):
            logger.error(f"文件不存在: {file_path}")
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        logger.info(f"开始读取文件（保留结构）: {file_path}")
        
        try:
            doc = docx.Document(file_path)
            
            # 提取文档基本信息
            result = {
                "title": self._extract_title(doc),
                "sections": self._extract_sections(doc),
                "paragraphs": [p.text for p in doc.paragraphs if p.text.strip()],
                "tables": self._extract_tables(doc),
                "full_text": self.read_file(file_path)
            }
            
            return result
            
        except Exception as e:
            logger.error(f"读取文件结构时出错: {str(e)}")
            raise
    
    def _extract_title(self, doc):
        """
        尝试从文档中提取标题。
        
        Args:
            doc (docx.Document): 文档对象
        
        Returns:
            str: 提取的标题
        """
        # 通常标题是文档的第一个段落，并且有特殊格式
        if doc.paragraphs and doc.paragraphs[0].text.strip():
            return doc.paragraphs[0].text.strip()
        return ""
    
    def _extract_sections(self, doc):
        """
        尝试从文档中提取各个部分。
        
        Args:
            doc (docx.Document): 文档对象
        
        Returns:
            dict: 各部分内容的字典
        """
        # 根据常见的题型标记识别各部分
        sections = {}
        current_section = "默认部分"
        current_content = []
        
        section_markers = [
            (r"Section\s+[A-D]", ""),  # 如 Section A
            (r"Part\s+[A-D]", ""),  # 如 Part A
            (r"完形填空", "完形填空"),
            (r"阅读理解", "阅读理解"),
            (r"Text\s+[1-4]", ""),  # 如 Text 1
            (r"新题型", "新题型"),
            (r"翻译", "翻译"),
            (r"写作", "写作")
        ]
        
        for para in doc.paragraphs:
            text = para.text.strip()
            if not text:
                continue
                
            # 检查是否是新部分的开始
            section_found = False
            for pattern, name in section_markers:
                if re.search(pattern, text, re.IGNORECASE):
                    # 保存之前的部分内容
                    if current_content:
                        sections[current_section] = "\n".join(current_content)
                    
                    # 开始新部分
                    current_section = name if name else text
                    current_content = [text]
                    section_found = True
                    break
            
            if not section_found:
                current_content.append(text)
        
        # 保存最后一个部分
        if current_content:
            sections[current_section] = "\n".join(current_content)
            
        return sections
    
    def _extract_tables(self, doc):
        """
        提取文档中的所有表格。
        
        Args:
            doc (docx.Document): 文档对象
        
        Returns:
            list: 表格内容列表
        """
        tables = []
        
        for table in doc.tables:
            table_data = []
            for row in table.rows:
                row_data = [cell.text.strip() for cell in row.cells]
                if any(row_data):  # 确保不添加完全空白的行
                    table_data.append(row_data)
            
            if table_data:  # 确保不添加完全空白的表格
                tables.append(table_data)
                
        return tables
        
    def preprocess_text(self, text):
        """
        对提取的文本进行预处理，清理不必要的内容。
        
        Args:
            text (str): 原始文本
        
        Returns:
            str: 预处理后的文本
        """
        # 删除多余的空白字符
        text = re.sub(r'\s+', ' ', text)
        
        # 替换常见的特殊字符
        text = text.replace('–', '-')
        text = text.replace(''', "'")
        text = text.replace(''', "'")
        text = text.replace('"', '"')
        text = text.replace('"', '"')
        
        # 清理页眉页脚等内容
        text = re.sub(r'页码\s*\d+\s*', '', text)
        text = re.sub(r'Page\s*\d+\s*', '', text)
        
        return text.strip() 