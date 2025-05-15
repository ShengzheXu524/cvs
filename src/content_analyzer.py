#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
内容分析模块，负责处理API返回结果，提取结构化信息。
"""

import re
import json
import logging

logger = logging.getLogger("考研英语真题处理.content_analyzer")

class ContentAnalyzer:
    """
    内容分析器，用于处理Claude API返回的结果并提取结构化信息。
    """
    
    def __init__(self):
        """
        初始化内容分析器。
        """
        pass
    
    def parse_response(self, response):
        """
        解析Claude API的响应结果。
        
        Args:
            response: API响应结果
        
        Returns:
            list: 提取的结构化数据列表
        """
        logger.info("开始解析API响应")
        
        # 如果response已经是字典或列表，直接使用
        if isinstance(response, (dict, list)):
            data = response
        else:
            # 尝试将字符串解析为JSON
            try:
                data = json.loads(response)
            except json.JSONDecodeError:
                logger.warning("响应不是有效的JSON格式，尝试提取JSON部分")
                json_text = self._extract_json_from_text(response)
                if json_text:
                    try:
                        data = json.loads(json_text)
                    except json.JSONDecodeError:
                        logger.error("无法从响应文本提取有效的JSON数据")
                        return []
                else:
                    logger.error("无法提取JSON数据")
                    return []
        
        # 检查是否是新的JSON格式（有metadata、sections和questions字段）
        if isinstance(data, dict) and "metadata" in data and "sections" in data and "questions" in data:
            logger.info("检测到新的JSON格式，直接返回原始数据")
            return data
        
        # 根据数据结构提取题目列表
        questions = self._extract_questions_list(data)
        
        logger.info(f"成功解析 {len(questions)} 道题目")
        return questions
    
    def _extract_json_from_text(self, text):
        """
        从文本中提取JSON部分。
        
        Args:
            text (str): 原始文本
        
        Returns:
            str: 提取的JSON文本，如果没有找到则返回None
        """
        # 查找可能的JSON起始位置（{ 或 [）
        start_idx = -1
        for i, char in enumerate(text):
            if char in '{[':
                start_idx = i
                break
        
        if start_idx == -1:
            return None
        
        # 根据起始字符确定结束字符
        start_char = text[start_idx]
        end_char = '}' if start_char == '{' else ']'
        
        # 找到匹配的结束位置
        stack = [start_char]
        for i in range(start_idx + 1, len(text)):
            if text[i] == start_char:
                stack.append(start_char)
            elif text[i] == end_char:
                stack.pop()
                if not stack:  # 栈为空，找到匹配的结束位置
                    return text[start_idx:i+1]
        
        # 没有找到匹配的结束位置
        return None
    
    def _extract_questions_list(self, data):
        """
        从数据中提取题目列表。
        
        Args:
            data: 解析后的数据
        
        Returns:
            list: 题目列表
        """
        # 检查是否是新格式
        if isinstance(data, dict) and "questions" in data and isinstance(data["questions"], list):
            logger.info("从新格式JSON中提取题目列表")
            return data["questions"]
        
        # 如果data本身就是列表，检查是否为题目列表
        if isinstance(data, list):
            if data and isinstance(data[0], dict) and self._is_question_dict(data[0]):
                return data
        
        # 如果data是字典，查找可能的题目列表字段
        if isinstance(data, dict):
            for key in ['questions', 'items', 'data', 'results']:
                if key in data and isinstance(data[key], list):
                    return data[key]
            
            # 检查是否题目以编号为键存储
            number_keys = [k for k in data.keys() if str(k).isdigit() or 
                           (isinstance(k, str) and k.startswith('question'))]
            if number_keys:
                # 按编号排序并提取值
                sorted_keys = sorted(number_keys, key=lambda k: int(k) if str(k).isdigit() 
                                    else int(re.sub(r'\D', '', k)))
                return [data[k] for k in sorted_keys]
        
        # 没有找到合适的题目列表
        logger.warning("无法从数据中提取题目列表，数据可能格式不规范")
        return []
    
    def _is_question_dict(self, item):
        """
        判断一个字典是否为题目字典。
        
        Args:
            item (dict): 要检查的字典
        
        Returns:
            bool: 是否为题目字典
        """
        # 检查是否包含题目的常见字段
        question_fields = [
            '题目编号', '题干', '题型', 'question_number', 'question_text', 'question_type',
            'number', 'stem', 'section_type'
        ]
        
        if not isinstance(item, dict):
            return False
        
        # 如果包含任何题目相关字段，则认为是题目字典
        for field in question_fields:
            if field in item:
                return True
        
        return False
    
    def enhance_question_data(self, questions):
        """
        增强题目数据，补充和修正。
        
        Args:
            questions (list): 题目列表
        
        Returns:
            list: 增强后的题目列表
        """
        # 如果是新的格式，直接返回原始数据
        if isinstance(questions, dict) and "metadata" in questions and "sections" in questions and "questions" in questions:
            logger.info("检测到新的JSON格式，不进行数据增强")
            return questions
        
        logger.info("开始增强题目数据")
        
        enhanced = []
        
        for question in questions:
            try:
                # 转换为字典（如果不是）
                q_data = question if isinstance(question, dict) else {}
                
                # 处理题号
                if 'question_number' in q_data and '题目编号' not in q_data:
                    q_data['题目编号'] = q_data['question_number']
                elif 'number' in q_data and '题目编号' not in q_data:
                    q_data['题目编号'] = q_data['number']
                
                # 尝试将题号转换为整数
                if '题目编号' in q_data:
                    try:
                        q_data['题目编号'] = int(q_data['题目编号'])
                    except (ValueError, TypeError):
                        pass
                
                # 从section_type到题型的映射
                if 'section_type' in q_data and ('题型' not in q_data or not q_data['题型']):
                    q_data['题型'] = q_data['section_type']
                
                # 根据题号确定题型（如果缺失）
                if '题目编号' in q_data and ('题型' not in q_data or not q_data['题型']):
                    q_num = q_data['题目编号']
                    if isinstance(q_num, str):
                        q_num = int(q_num) if q_num.isdigit() else 0
                    
                    q_data['题型'] = self._get_question_type(q_num)
                
                # 处理干扰选项字段
                if 'distractor_options' in q_data and '干扰选项' not in q_data:
                    q_data['干扰选项'] = q_data['distractor_options']
                
                # 修正完形填空的原文（还原后）
                if '题型' in q_data and q_data['题型'] == '完形填空':
                    if '原文（卷面）' in q_data and '原文（还原后）' not in q_data:
                        # 尝试根据正确答案还原完形填空原文
                        q_data['原文（还原后）'] = self._restore_cloze_text(
                            q_data['原文（卷面）'], 
                            q_data.get('正确答案', ''),
                            q_data  # 传入当前题目数据
                        )
                
                enhanced.append(q_data)
                
            except Exception as e:
                logger.error(f"增强题目数据时出错: {str(e)}")
                enhanced.append(question)  # 保留原始数据
        
        logger.info(f"题目数据增强完成，共 {len(enhanced)} 道题目")
        return enhanced
    
    def _get_question_type(self, question_number):
        """
        根据题号确定题型。
        
        Args:
            question_number (int): 题号
        
        Returns:
            str: 题型
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
    
    def _restore_cloze_text(self, cloze_text, answers, question=None):
        """
        还原完形填空文本，将空格替换为正确答案。
        
        Args:
            cloze_text (str): 带空格标记的完形填空文本
            answers (str): 正确答案列表
            question (dict, optional): 题目数据，用于获取选项信息
        
        Returns:
            str: 还原后的文本
        """
        if not cloze_text:
            return ""
        
        # 如果answers是字符串，尝试转换为列表
        answers_list = []
        if isinstance(answers, str):
            # 尝试匹配形如"1. A, 2. B, 3. C"的格式
            matches = re.findall(r'(\d+)\.\s*([A-D])', answers)
            if matches:
                # 创建一个字典，键为题号，值为答案
                answers_dict = {int(num): ans for num, ans in matches}
                # 生成完整的答案列表
                for i in range(1, 21):  # 完形填空有20题
                    if i in answers_dict:
                        answers_list.append(answers_dict[i])
                    else:
                        answers_list.append("")
            else:
                # 尝试直接提取A、B、C、D答案
                letter_answers = re.findall(r'[A-D]', answers)
                answers_list = letter_answers
        elif isinstance(answers, list):
            answers_list = answers
        
        # 创建答案映射，将[1], [2]等替换为对应的答案
        restored_text = cloze_text
        
        # 正则表达式匹配[数字]模式
        pattern = r'\[(\d+)\]'
        
        # 查找所有匹配项
        matches = re.finditer(pattern, cloze_text)
        
        # 保存原始文本，从后向前替换
        for match in sorted(list(matches), key=lambda m: int(m.group(1)), reverse=True):
            index = int(match.group(1)) - 1
            if 0 <= index < len(answers_list):
                # 获取对应的答案
                answer = answers_list[index]
                # 如果答案是选项字母（如A、B、C、D），获取对应的单词
                if answer in "ABCD" and question and '选项' in question:
                    options = question.get('选项', '')
                    # 查找对应选项的词语
                    option_pattern = f"{answer}\.\s*(\w+)"
                    option_match = re.search(option_pattern, options)
                    if option_match:
                        answer = option_match.group(1)
                
                # 替换对应的空格标记
                start, end = match.span()
                restored_text = restored_text[:start] + answer + restored_text[end:]
        
        return restored_text 