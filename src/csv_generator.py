#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CSV生成模块，负责生成最终的CSV文件。
"""

import os
import csv
import logging
import pandas as pd
from pathlib import Path

logger = logging.getLogger("考研英语真题处理.csv_generator")

class CSVGenerator:
    """
    CSV生成器，用于将结构化数据输出为CSV文件。
    """
    
    def __init__(self):
        """
        初始化CSV生成器。
        """
        # CSV列名定义（按照规定的顺序）
        self.column_order = [
            "年份",
            "考试类型",
            "题型",
            "原文（卷面）",
            "试卷答案",
            "题目编号",
            "题干",
            "选项",
            "正确答案",
            "原文（还原后）",
            "原文（句子拆解后）",
            "干扰选项"
        ]
    
    def generate_csv(self, data, output_file):
        """
        将结构化数据输出为CSV文件。
        
        Args:
            data (list): 结构化数据列表
            output_file (str): 输出CSV文件路径
        
        Returns:
            bool: 是否成功生成CSV文件
        """
        logger.info(f"开始生成CSV文件: {output_file}")
        
        try:
            # 创建输出目录（如果不存在）
            output_dir = os.path.dirname(output_file)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            # 使用pandas生成CSV
            df = pd.DataFrame(data)
            
            # 确保所有列都存在（如果不存在则添加空列）
            for column in self.column_order:
                if column not in df.columns:
                    df[column] = ""
            
            # 按照指定顺序排列列
            df = df[self.column_order]
            
            # 保存为CSV
            df.to_csv(output_file, index=False, encoding='utf-8-sig')  # 使用带BOM的UTF-8编码，确保Excel正确识别中文
            
            logger.info(f"成功生成CSV文件，包含 {len(data)} 条记录")
            return True
            
        except Exception as e:
            logger.error(f"生成CSV文件失败: {str(e)}")
            return False
    
    def generate_csv_manual(self, data, output_file):
        """
        使用CSV模块手动生成CSV文件（不依赖pandas）。
        
        Args:
            data (list): 结构化数据列表
            output_file (str): 输出CSV文件路径
        
        Returns:
            bool: 是否成功生成CSV文件
        """
        logger.info(f"开始手动生成CSV文件: {output_file}")
        
        try:
            # 创建输出目录（如果不存在）
            output_dir = os.path.dirname(output_file)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            # 打开文件，使用utf-8-sig编码
            with open(output_file, 'w', newline='', encoding='utf-8-sig') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=self.column_order)
                
                # 写入表头
                writer.writeheader()
                
                # 写入数据行
                for item in data:
                    # 确保所有字段都存在
                    row_data = {}
                    for column in self.column_order:
                        row_data[column] = item.get(column, "")
                    
                    writer.writerow(row_data)
            
            logger.info(f"成功手动生成CSV文件，包含 {len(data)} 条记录")
            return True
            
        except Exception as e:
            logger.error(f"手动生成CSV文件失败: {str(e)}")
            return False
    
    def preview_data(self, data, max_rows=5):
        """
        预览数据，用于调试和验证。
        
        Args:
            data (list): 数据列表
            max_rows (int, optional): 最大预览行数
        
        Returns:
            str: 格式化的预览文本
        """
        if not data:
            return "数据为空"
        
        # 限制行数
        preview_data = data[:max_rows]
        
        # 创建预览内容
        preview_text = "数据预览（前 {} 行）:\n".format(min(max_rows, len(data)))
        
        # 使用pandas格式化预览
        try:
            df = pd.DataFrame(preview_data)
            
            # 确保所有列都存在
            for column in self.column_order:
                if column not in df.columns:
                    df[column] = ""
            
            # 按照指定顺序排列列
            df = df[self.column_order]
            
            # 将DataFrame转换为字符串格式
            preview_text += df.to_string()
            
        except Exception as e:
            # 如果pandas预览失败，使用简单格式预览
            preview_text += "字段: " + ", ".join(self.column_order) + "\n"
            
            for i, item in enumerate(preview_data):
                preview_text += f"行 {i+1}:\n"
                for column in self.column_order:
                    value = item.get(column, "")
                    # 截断过长的值
                    if isinstance(value, str) and len(value) > 50:
                        value = value[:47] + "..."
                    preview_text += f"  {column}: {value}\n"
        
        return preview_text 