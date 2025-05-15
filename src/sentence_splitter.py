#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
句子拆分器模块，用于将原文按句子拆分并进行标注。
"""

import re
import logging
import nltk
from nltk.tokenize import sent_tokenize

logger = logging.getLogger("考研英语真题处理.sentence_splitter")

class SentenceSplitter:
    """
    句子拆分器，用于将原文按句子拆分并标注。
    """
    
    def __init__(self):
        """
        初始化句子拆分器。
        """
        # 确保nltk数据已下载
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            logger.info("正在下载NLTK数据...")
            nltk.download('punkt')
    
    def split_text(self, text):
        """
        将文本按句子拆分并添加标注。
        
        Args:
            text (str): 要拆分的文本
        
        Returns:
            str: 拆分并标注后的文本
        """
        if not text:
            return ""
        
        try:
            # 使用NLTK拆分句子
            sentences = sent_tokenize(text)
            
            # 添加句子标注
            result = []
            for i, sentence in enumerate(sentences):
                result.append(f"[Sentence{i+1}]{sentence.strip()}")
            
            # 用空格连接所有句子
            return " ".join(result)
            
        except Exception as e:
            logger.error(f"句子拆分失败: {str(e)}")
            # 如果拆分失败，返回原始文本
            return text
    
    def split_text_custom(self, text):
        """
        使用自定义规则拆分句子。
        
        Args:
            text (str): 要拆分的文本
        
        Returns:
            str: 拆分并标注后的文本
        """
        if not text:
            return ""
        
        try:
            # 以句号、问号、感叹号为分隔符拆分句子
            pattern = r'(?<=[.!?])\s+'
            sentences = re.split(pattern, text)
            
            # 清理空白句子
            sentences = [s.strip() for s in sentences if s.strip()]
            
            # 添加句子标注
            result = []
            for i, sentence in enumerate(sentences):
                result.append(f"[Sentence{i+1}]{sentence}")
            
            # 用空格连接所有句子
            return " ".join(result)
            
        except Exception as e:
            logger.error(f"自定义句子拆分失败: {str(e)}")
            # 如果拆分失败，返回原始文本
            return text
    
    def split_text_with_context(self, text, preserve_linebreaks=True):
        """
        考虑上下文的句子拆分，保留原文格式。
        
        Args:
            text (str): 要拆分的文本
            preserve_linebreaks (bool): 是否保留原文换行
        
        Returns:
            str: 拆分并标注后的文本
        """
        if not text:
            return ""
        
        try:
            # 处理换行符
            if preserve_linebreaks:
                # 替换换行符为特殊标记
                text = text.replace('\n', ' <<LINEBREAK>> ')
            
            # 使用NLTK拆分句子
            sentences = sent_tokenize(text)
            
            # 恢复换行符并添加句子标注
            result = []
            for i, sentence in enumerate(sentences):
                # 恢复换行符
                if preserve_linebreaks:
                    sentence = sentence.replace('<<LINEBREAK>>', '\n')
                
                # 添加标注
                result.append(f"[Sentence{i+1}]{sentence.strip()}")
            
            # 连接所有句子
            if preserve_linebreaks:
                # 使用空格连接
                return " ".join(result)
            else:
                # 使用空格连接
                return " ".join(result)
            
        except Exception as e:
            logger.error(f"带上下文的句子拆分失败: {str(e)}")
            # 如果拆分失败，返回原始文本
            return text

# 导出主要的句子拆分函数，便于其他模块导入使用
def split_sentences(text):
    """
    拆分句子的快捷函数。
    
    Args:
        text (str): 要拆分的文本
    
    Returns:
        str: 拆分并标注后的文本
    """
    splitter = SentenceSplitter()
    return splitter.split_text(text) 