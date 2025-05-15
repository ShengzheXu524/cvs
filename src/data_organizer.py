#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
数据组织模块，负责将提取的信息按照规定格式组织。
"""

import os
import re
import json
import logging
from pathlib import Path

logger = logging.getLogger("考研英语真题处理.data_organizer")

class DataOrganizer:
    """
    数据组织器，负责规范和组织提取的考研英语试题数据。
    """
    
    def __init__(self):
        """
        初始化数据组织器。
        """
        pass
    
    def organize_data(self, raw_data, year=None, exam_type=None):
        """
        组织和规范化从API获取的原始数据。
        
        Args:
            raw_data (dict): API返回的原始数据
            year (str, optional): 考试年份，如未提供将从数据中推断
            exam_type (str, optional): 考试类型，如未提供将从数据中推断
        
        Returns:
            list: 组织好的数据列表，每个元素是一道题目的完整信息
        """
        logger.info("开始组织和规范化数据")
        
        # 检查是否是新的JSON格式
        if isinstance(raw_data, dict) and "metadata" in raw_data and "sections" in raw_data and "questions" in raw_data:
            logger.info("检测到新的JSON格式，使用新的处理方法")
            return self._process_new_format(raw_data, year, exam_type)
        
        # 检查raw_data格式并处理
        if isinstance(raw_data, list):
            # 假设raw_data已经是题目数据列表
            questions_data = raw_data
        elif isinstance(raw_data, dict):
            # 假设raw_data包含一个questions字段
            if "questions" in raw_data:
                questions_data = raw_data["questions"]
            else:
                # 如果是其他格式，尝试转换
                questions_data = self._convert_to_questions_list(raw_data)
        else:
            logger.error(f"不支持的数据格式: {type(raw_data)}")
            return []
        
        # 处理每个题目数据
        organized_data = []
        for question in questions_data:
            try:
                # 补充或覆盖年份和考试类型（如果提供）
                if year:
                    question["年份"] = year
                if exam_type:
                    question["考试类型"] = exam_type
                
                # 标准化字段名称
                standardized_question = self._standardize_fields(question)
                
                # 添加缺失字段的默认值
                complete_question = self._add_missing_fields(standardized_question)
                
                # 根据题目编号补充题型信息
                if "题目编号" in complete_question:
                    question_number = complete_question["题目编号"]
                    if isinstance(question_number, str):
                        question_number = int(question_number)
                    
                    # 覆盖或添加题型字段
                    complete_question["题型"] = self._get_question_type(question_number)
                
                organized_data.append(complete_question)
                
            except Exception as e:
                logger.error(f"处理题目数据时出错: {str(e)}")
                logger.debug(f"问题数据: {question}")
        
        # 按题目编号排序
        if organized_data:
            try:
                organized_data.sort(key=lambda x: int(x.get("题目编号", 0)))
            except Exception as e:
                logger.warning(f"按题目编号排序失败: {str(e)}")
        
        logger.info(f"数据组织完成，共 {len(organized_data)} 道题目")
        return organized_data
    
    def _process_new_format(self, raw_data, year=None, exam_type=None):
        """
        处理新的JSON格式数据。
        
        Args:
            raw_data (dict): 新格式的API返回数据
            year (str, optional): 考试年份，如未提供将从数据中推断
            exam_type (str, optional): 考试类型，如未提供将从数据中推断
            
        Returns:
            list: 组织好的数据列表
        """
        logger.info("开始处理新格式JSON数据")
        
        # 提取元数据
        metadata = raw_data.get("metadata", {})
        sections = raw_data.get("sections", {})
        questions = raw_data.get("questions", [])
        
        # 使用提供的年份和考试类型，或者从元数据中获取
        year = year or metadata.get("year", "")
        exam_type = exam_type or metadata.get("exam_type", "")
        
        # 整理原文信息和答案信息
        section_texts = {}
        section_answers = {}
        
        # 解析各板块的答案汇总，转换为题号->答案的映射
        answer_mappings = {}
        
        # 完形填空
        if "cloze" in sections:
            section_texts["完形填空"] = {
                "原文（卷面）": sections["cloze"].get("original_text", ""),
                "原文（还原后）": sections["cloze"].get("restored_text", ""),
                "答案汇总": sections["cloze"].get("answers_summary", "")
            }
            # 解析完形填空答案
            answers_summary = sections["cloze"].get("answers_summary", "")
            answer_mappings.update(self._parse_answers_summary(answers_summary))
        
        # 阅读理解
        if "reading" in sections:
            for i, text_key in enumerate(["text_1", "text_2", "text_3", "text_4"]):
                if text_key in sections["reading"]:
                    section_name = f"阅读理解" if i == 0 else f"阅读理解 Text {i+1}"
                    if i == 0:
                        # 为第一篇阅读文章设置两个名称：既可以是"阅读理解"也可以是"阅读理解 Text 1"
                        section_texts["阅读理解"] = {
                            "原文（卷面）": sections["reading"][text_key].get("original_text", ""),
                            "原文（还原后）": sections["reading"][text_key].get("original_text", ""),  # 阅读没有还原版本
                            "答案汇总": sections["reading"][text_key].get("answers_summary", "")
                        }
                        section_texts["阅读理解 Text 1"] = section_texts["阅读理解"]
                        # 解析阅读理解答案
                        answers_summary = sections["reading"][text_key].get("answers_summary", "")
                        answer_mappings.update(self._parse_answers_summary(answers_summary))
                    else:
                        section_texts[section_name] = {
                            "原文（卷面）": sections["reading"][text_key].get("original_text", ""),
                            "原文（还原后）": sections["reading"][text_key].get("original_text", ""),  # 阅读没有还原版本
                            "答案汇总": sections["reading"][text_key].get("answers_summary", "")
                        }
                        # 解析阅读理解答案
                        answers_summary = sections["reading"][text_key].get("answers_summary", "")
                        answer_mappings.update(self._parse_answers_summary(answers_summary))
        
        # 新题型
        if "new_type" in sections:
            section_texts["新题型"] = {
                "原文（卷面）": sections["new_type"].get("original_text", ""),
                "原文（还原后）": sections["new_type"].get("restored_text", ""),
                "答案汇总": sections["new_type"].get("answers_summary", "")
            }
            # 解析新题型答案
            answers_summary = sections["new_type"].get("answers_summary", "")
            answer_mappings.update(self._parse_answers_summary(answers_summary))
        
        # 翻译
        if "translation" in sections:
            section_texts["翻译"] = {
                "原文（卷面）": sections["translation"].get("original_text", ""),
                "原文（还原后）": sections["translation"].get("original_text", ""),  # 翻译没有还原版本
                "答案汇总": sections["translation"].get("answers_summary", "N/A")
            }
            # 解析翻译答案(如果有)
            answers_summary = sections["translation"].get("answers_summary", "")
            if answers_summary and answers_summary != "N/A":
                answer_mappings.update(self._parse_answers_summary(answers_summary))
        
        # 写作
        if "writing" in sections:
            if "part_a" in sections["writing"]:
                section_texts["写作A"] = {
                    "原文（卷面）": sections["writing"]["part_a"].get("original_text", ""),
                    "原文（还原后）": sections["writing"]["part_a"].get("original_text", ""),  # 写作没有还原版本
                    "答案汇总": sections["writing"]["part_a"].get("answers_summary", "N/A")
                }
            if "part_b" in sections["writing"]:
                section_texts["写作B"] = {
                    "原文（卷面）": sections["writing"]["part_b"].get("original_text", ""),
                    "原文（还原后）": sections["writing"]["part_b"].get("original_text", ""),  # 写作没有还原版本
                    "答案汇总": sections["writing"]["part_b"].get("answers_summary", "N/A")
                }
        
        # 处理每个题目数据
        organized_data = []
        
        # 记录已生成的题型对应表（用于处理题型名称差异）
        section_type_mapping = {}
        
        # 如果questions列表为空或只有少量题目，尝试创建全部52题的题目结构
        if len(questions) < 10:  # 假设少于10道题意味着数据不完整
            logger.warning(f"API返回的题目数量不足(仅有{len(questions)}道)，创建完整题目结构")
            temp_questions = []
            
            # 保存原来的questions，以便后续合并
            original_questions = questions.copy()
            
            # 创建52道题的基本结构
            for num in range(1, 53):
                question_type = self._get_question_type(num)
                temp_questions.append({
                    "number": num,
                    "section_type": question_type,
                    "stem": f"[题号 {num}]",
                    "options": "",
                    "correct_answer": "",
                    "distractor_options": ""
                })
            
            # 将原始questions中的数据合并到临时questions中
            for orig_q in original_questions:
                if "number" in orig_q and 1 <= orig_q["number"] <= 52:
                    # 用原始数据覆盖对应题号的临时数据
                    temp_questions[orig_q["number"]-1] = orig_q
            
            # 用合并后的数据替换原始questions
            questions = temp_questions
        
        for question in questions:
            try:
                # 获取题号和题型
                number = question.get("number", 0)
                section_type = question.get("section_type", "")
                
                # 如果之前遇到过相同题号范围的题型，使用之前的映射
                if number in section_type_mapping:
                    mapped_section_type = section_type_mapping[number]
                else:
                    # 根据题号范围推断题型
                    mapped_section_type = self._map_section_type(section_type, number)
                    section_type_mapping[number] = mapped_section_type
                
                # 获取正确答案并解析为单独的答案格式
                correct_answer = question.get("correct_answer", "")
                individual_answer = self._parse_individual_answer(number, correct_answer, answer_mappings)
                
                # 构建标准格式的题目数据
                question_data = {
                    "年份": year,
                    "考试类型": exam_type,
                    "题型": mapped_section_type,
                    "题目编号": str(number),
                    "题干": question.get("stem", ""),
                    "选项": question.get("options", ""),
                    "正确答案": correct_answer,
                    "干扰选项": question.get("distractor_options", ""),
                    "试卷答案": individual_answer  # 每道题的单独答案（如"A"、"B"等）
                }
                
                # 添加原文信息（根据映射后的题型）
                if mapped_section_type in section_texts:
                    question_data["原文（卷面）"] = section_texts[mapped_section_type]["原文（卷面）"]
                    question_data["原文（还原后）"] = section_texts[mapped_section_type]["原文（还原后）"]
                    # 保存板块的答案汇总（用于调试）
                    question_data["答案汇总"] = section_texts[mapped_section_type]["答案汇总"]
                else:
                    # 如果找不到对应的题型，尝试使用原始题型
                    if section_type in section_texts:
                        question_data["原文（卷面）"] = section_texts[section_type]["原文（卷面）"]
                        question_data["原文（还原后）"] = section_texts[section_type]["原文（还原后）"]
                        question_data["答案汇总"] = section_texts[section_type]["答案汇总"]
                    else:
                        # 最后尝试根据题号范围来匹配
                        found_section = False
                        if 1 <= number <= 20 and "完形填空" in section_texts:
                            question_data["原文（卷面）"] = section_texts["完形填空"]["原文（卷面）"]
                            question_data["原文（还原后）"] = section_texts["完形填空"]["原文（还原后）"]
                            question_data["答案汇总"] = section_texts["完形填空"]["答案汇总"]
                            found_section = True
                        elif 21 <= number <= 25 and "阅读理解 Text 1" in section_texts:
                            question_data["原文（卷面）"] = section_texts["阅读理解 Text 1"]["原文（卷面）"]
                            question_data["原文（还原后）"] = section_texts["阅读理解 Text 1"]["原文（还原后）"]
                            question_data["答案汇总"] = section_texts["阅读理解 Text 1"]["答案汇总"]
                            found_section = True
                        elif 26 <= number <= 30 and "阅读理解 Text 2" in section_texts:
                            question_data["原文（卷面）"] = section_texts["阅读理解 Text 2"]["原文（卷面）"]
                            question_data["原文（还原后）"] = section_texts["阅读理解 Text 2"]["原文（还原后）"]
                            question_data["答案汇总"] = section_texts["阅读理解 Text 2"]["答案汇总"]
                            found_section = True
                        elif 31 <= number <= 35 and "阅读理解 Text 3" in section_texts:
                            question_data["原文（卷面）"] = section_texts["阅读理解 Text 3"]["原文（卷面）"]
                            question_data["原文（还原后）"] = section_texts["阅读理解 Text 3"]["原文（还原后）"]
                            question_data["答案汇总"] = section_texts["阅读理解 Text 3"]["答案汇总"]
                            found_section = True
                        elif 36 <= number <= 40 and "阅读理解 Text 4" in section_texts:
                            question_data["原文（卷面）"] = section_texts["阅读理解 Text 4"]["原文（卷面）"]
                            question_data["原文（还原后）"] = section_texts["阅读理解 Text 4"]["原文（还原后）"]
                            question_data["答案汇总"] = section_texts["阅读理解 Text 4"]["答案汇总"]
                            found_section = True
                        elif 41 <= number <= 45 and "新题型" in section_texts:
                            question_data["原文（卷面）"] = section_texts["新题型"]["原文（卷面）"]
                            question_data["原文（还原后）"] = section_texts["新题型"]["原文（还原后）"]
                            question_data["答案汇总"] = section_texts["新题型"]["答案汇总"]
                            found_section = True
                        elif 46 <= number <= 50 and "翻译" in section_texts:
                            question_data["原文（卷面）"] = section_texts["翻译"]["原文（卷面）"]
                            question_data["原文（还原后）"] = section_texts["翻译"]["原文（还原后）"]
                            question_data["答案汇总"] = section_texts["翻译"]["答案汇总"]
                            found_section = True
                        elif number == 51 and "写作A" in section_texts:
                            question_data["原文（卷面）"] = section_texts["写作A"]["原文（卷面）"]
                            question_data["原文（还原后）"] = section_texts["写作A"]["原文（还原后）"]
                            question_data["答案汇总"] = section_texts["写作A"]["答案汇总"]
                            found_section = True
                        elif number == 52 and "写作B" in section_texts:
                            question_data["原文（卷面）"] = section_texts["写作B"]["原文（卷面）"]
                            question_data["原文（还原后）"] = section_texts["写作B"]["原文（还原后）"]
                            question_data["答案汇总"] = section_texts["写作B"]["答案汇总"]
                            found_section = True
                        
                        if not found_section:
                            # 如果依然找不到，使用默认值
                            question_data["原文（卷面）"] = ""
                            question_data["原文（还原后）"] = ""
                            question_data["答案汇总"] = ""
                
                # 添加缺失字段的默认值
                complete_question = self._add_missing_fields(question_data)
                
                organized_data.append(complete_question)
                
            except Exception as e:
                logger.error(f"处理新格式题目数据时出错: {str(e)}")
                logger.debug(f"问题数据: {question}")
        
        # 按题目编号排序
        if organized_data:
            try:
                organized_data.sort(key=lambda x: int(x.get("题目编号", 0)))
            except Exception as e:
                logger.warning(f"按题目编号排序失败: {str(e)}")
        
        # 确保数据集完整(52题)
        organized_data = self.ensure_complete_dataset(organized_data, year, exam_type)
        
        logger.info(f"新格式数据处理完成，共 {len(organized_data)} 道题目")
        return organized_data
    
    def _standardize_fields(self, question):
        """
        标准化题目数据的字段名称。
        
        Args:
            question (dict): 原始题目数据
        
        Returns:
            dict: 标准化后的题目数据
        """
        # 字段名映射
        field_mapping = {
            "year": "年份",
            "exam_type": "考试类型",
            "question_type": "题型",
            "section_type": "题型",
            "original_text": "原文（卷面）",
            "answers": "试卷答案",
            "answers_summary": "试卷答案",
            "question_number": "题目编号",
            "number": "题目编号",
            "question_text": "题干",
            "stem": "题干",
            "options": "选项",
            "correct_answer": "正确答案",
            "restored_text": "原文（还原后）",
            "incorrect_options": "干扰选项",
            "distractor_options": "干扰选项",
            "sentence_split_text": "原文（句子拆解后）"
        }
        
        # 创建新字典，使用标准化字段名
        standardized = {}
        
        # 先复制所有原始字段
        for key, value in question.items():
            # 检查是否需要标准化字段名
            if key in field_mapping.values():
                # 已经是标准字段名
                standardized[key] = value
            elif key in field_mapping:
                # 需要标准化
                standardized[field_mapping[key]] = value
            else:
                # 未知字段，保持原样
                standardized[key] = value
        
        return standardized
    
    def _add_missing_fields(self, question):
        """
        添加缺失字段的默认值。
        
        Args:
            question (dict): 输入的题目数据
        
        Returns:
            dict: 补充完整的题目数据
        """
        # 必要字段及其默认值
        required_fields = {
            "年份": "",
            "考试类型": "",
            "题型": "",
            "原文（卷面）": "",
            "试卷答案": "",
            "题目编号": "",
            "题干": "",
            "选项": "",
            "正确答案": "",
            "原文（还原后）": "",
            "原文（句子拆解后）": "",
            "干扰选项": ""
        }
        
        # 创建新字典，包含所有必要字段
        complete = question.copy()
        
        # 添加缺失的字段
        for field, default_value in required_fields.items():
            if field not in complete:
                complete[field] = default_value
        
        return complete
    
    def _get_question_type(self, question_number):
        """
        根据题目编号确定题型。
        
        Args:
            question_number (int): 题目编号
        
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
    
    def _convert_to_questions_list(self, data):
        """
        尝试将各种格式的数据转换为题目列表。
        
        Args:
            data (dict): 输入数据
        
        Returns:
            list: 题目数据列表
        """
        # 特定格式处理
        for key in ["questions", "items", "data", "results"]:
            if key in data and isinstance(data[key], list):
                return data[key]
        
        # 如果是包含题目编号的字典
        if all(str(i).isdigit() for i in data.keys()):
            return [data[k] for k in sorted(data.keys(), key=int)]
        
        # 尝试转换其他格式
        logger.warning("无法识别的数据格式，尝试自动转换")
        try:
            # 通过规则或者模式匹配等方式组建题目列表
            # 这里使用简单的示例方法
            questions = []
            for i in range(1, 53):  # 假设有52道题
                question = {"题目编号": i}
                # 尝试从data中提取相关信息
                for key, value in data.items():
                    if str(i) in key:
                        # 假设key是形如"题目1"的格式
                        simplified_key = re.sub(r'\d+', '', key)
                        question[simplified_key] = value
                questions.append(question)
            return questions
        except Exception as e:
            logger.error(f"转换数据格式失败: {str(e)}")
            # 返回空列表
            return []
    
    def validate_data(self, organized_data):
        """
        验证组织好的数据是否完整。
        
        Args:
            organized_data (list): 组织好的数据
        
        Returns:
            tuple: (是否有效, 错误信息)
        """
        logger.info("开始验证数据完整性")
        
        # 检查题目数量
        if len(organized_data) != 52:
            return False, f"题目数量不正确: 期望52道题，实际有{len(organized_data)}道题"
        
        # 检查题号是否完整（1-52）
        question_numbers = set()
        for question in organized_data:
            try:
                num = int(question.get("题目编号", "0"))
                question_numbers.add(num)
            except ValueError:
                return False, f"无效的题号: {question.get('题目编号')}"
        
        expected_numbers = set(range(1, 53))
        if question_numbers != expected_numbers:
            missing = expected_numbers - question_numbers
            extra = question_numbers - expected_numbers
            msg = ""
            if missing:
                msg += f"缺少题号: {sorted(missing)} "
            if extra:
                msg += f"多余题号: {sorted(extra)}"
            return False, msg
        
        # 检查每道题目的必要字段
        required_fields = ["年份", "考试类型", "题型", "原文（卷面）", "题干", "题目编号"]
        for idx, question in enumerate(organized_data):
            for field in required_fields:
                if not question.get(field):
                    return False, f"题目 #{idx+1} (题号 {question.get('题目编号', '未知')}) 缺少必要字段: {field}"
        
        logger.info("数据验证通过")
        return True, "数据验证通过"
    
    def sort_by_question_number(self, data):
        """
        按题号排序数据。
        
        Args:
            data (list): 题目数据列表
        
        Returns:
            list: 排序后的数据
        """
        try:
            return sorted(data, key=lambda x: int(x.get("题目编号", "0")))
        except Exception as e:
            logger.error(f"按题号排序失败: {str(e)}")
            return data
    
    def ensure_complete_dataset(self, data, year="2023", exam_type="英语（一）"):
        """
        确保数据集完整，如有必要填充缺失的题目。
        
        Args:
            data (list): 原始数据列表
            year (str): 考试年份
            exam_type (str): 考试类型
        
        Returns:
            list: 完整的数据集
        """
        # 检查数据中现有的题号
        existing_numbers = {int(item.get("题目编号", "0")) for item in data}
        
        # 创建完整数据集
        complete_data = data.copy()
        
        # 填充缺失的题目
        for num in range(1, 53):
            if num not in existing_numbers:
                logger.warning(f"填充缺失题号: {num}")
                
                question_type = self._get_question_type(num)
                
                # 创建缺失题目的占位数据
                placeholder = {
                    "年份": year,
                    "考试类型": exam_type,
                    "题型": question_type,
                    "原文（卷面）": f"[缺失数据] {question_type} 原文",
                    "试卷答案": "",
                    "题目编号": str(num),
                    "题干": f"[缺失数据] 题号 {num}",
                    "选项": "",
                    "正确答案": "",
                    "原文（还原后）": f"[缺失数据] {question_type} 原文",
                    "原文（句子拆解后）": "",
                    "干扰选项": ""
                }
                
                complete_data.append(placeholder)
        
        # 按题号排序
        return self.sort_by_question_number(complete_data)
    
    def save_debug_data(self, data, output_file):
        """
        将数据保存为JSON文件，用于调试。
        
        Args:
            data: 要保存的数据
            output_file (str): 输出文件路径
        """
        try:
            directory = os.path.dirname(output_file)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
                
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
            logger.info(f"调试数据已保存至: {output_file}")
        except Exception as e:
            logger.error(f"保存调试数据失败: {str(e)}")
            
    def apply_sentence_splitter(self, data, splitter_function):
        """
        应用句子拆分器函数处理"原文（还原后）"生成"原文（句子拆解后）"。
        
        Args:
            data (list): 题目数据列表
            splitter_function (callable): 句子拆分器函数
        
        Returns:
            list: 处理后的数据
        """
        logger.info("开始应用句子拆分器")
        
        for item in data:
            try:
                # 获取原文（还原后）
                original_text = item.get("原文（还原后）", "")
                
                if original_text:
                    # 使用拆分器处理文本
                    split_text = splitter_function(original_text)
                    
                    # 更新句子拆解后的文本
                    item["原文（句子拆解后）"] = split_text
            except Exception as e:
                logger.error(f"处理题目 #{item.get('题目编号', '未知')} 时发生错误: {str(e)}")
                item["原文（句子拆解后）"] = item.get("原文（还原后）", "")
        
        logger.info("句子拆分处理完成")
        return data
    
    def _map_section_type(self, section_type, question_number):
        """
        根据题号和提供的题型名称，映射到标准题型名称。
        
        Args:
            section_type (str): 原始题型名称
            question_number (int): 题目编号
            
        Returns:
            str: 标准化后的题型名称
        """
        # 根据题号范围判断题型
        if 1 <= question_number <= 20:
            return "完形填空"
        elif 21 <= question_number <= 25:
            return "阅读理解 Text 1"
        elif 26 <= question_number <= 30:
            return "阅读理解 Text 2"
        elif 31 <= question_number <= 35:
            return "阅读理解 Text 3"
        elif 36 <= question_number <= 40:
            return "阅读理解 Text 4"
        elif 41 <= question_number <= 45:
            return "新题型"
        elif 46 <= question_number <= 50:
            return "翻译"
        elif question_number == 51:
            return "写作A"
        elif question_number == 52:
            return "写作B"
        
        # 如果题号不在标准范围内，尝试根据提供的section_type判断
        section_type_lower = section_type.lower() if section_type else ""
        
        if "完形" in section_type_lower or "cloze" in section_type_lower:
            return "完形填空"
        elif "阅读" in section_type_lower or "text" in section_type_lower or "reading" in section_type_lower:
            # 如果包含数字，尝试提取
            if "text 1" in section_type_lower or "text1" in section_type_lower:
                return "阅读理解 Text 1"
            elif "text 2" in section_type_lower or "text2" in section_type_lower:
                return "阅读理解 Text 2"
            elif "text 3" in section_type_lower or "text3" in section_type_lower:
                return "阅读理解 Text 3"
            elif "text 4" in section_type_lower or "text4" in section_type_lower:
                return "阅读理解 Text 4"
            else:
                return "阅读理解"
        elif "新题型" in section_type_lower or "new" in section_type_lower:
            return "新题型"
        elif "翻译" in section_type_lower or "transl" in section_type_lower:
            return "翻译"
        elif "写作" in section_type_lower or "writing" in section_type_lower:
            if "a" in section_type_lower:
                return "写作A"
            elif "b" in section_type_lower:
                return "写作B"
            else:
                return "写作"
        
        # 如果无法判断，返回原始题型
        return section_type
    
    def _parse_answers_summary(self, answers_summary):
        """
        解析答案汇总字符串，转换为题号->答案的映射
        
        Args:
            answers_summary (str): 答案汇总字符串，如"1.A 2.C 3.B 4.D 5.A"
            
        Returns:
            dict: 题号到答案的映射，如{1: "A", 2: "C", 3: "B", 4: "D", 5: "A"}
        """
        if not answers_summary:
            return {}
        
        answer_map = {}
        
        # 尝试解析常见格式的答案汇总
        try:
            # 处理形如"1.A 2.C 3.B"的格式
            items = answers_summary.split()
            for item in items:
                # 处理形如"1.A"或"1-A"或"1:A"或"1A"的格式
                parts = re.split(r'[.\-:：]', item, 1)
                if len(parts) == 2:
                    question_num = parts[0].strip()
                    answer = parts[1].strip()
                    if question_num.isdigit():
                        answer_map[int(question_num)] = answer
                elif len(parts) == 1 and len(item) >= 2:
                    # 处理形如"1A"的无分隔符格式
                    match = re.match(r'(\d+)([A-D]|\[[A-D]\])', item)
                    if match:
                        question_num = match.group(1)
                        answer = match.group(2)
                        if question_num.isdigit():
                            answer_map[int(question_num)] = answer
        except Exception as e:
            logger.error(f"解析答案汇总失败: {str(e)}, 原文: {answers_summary}")
        
        return answer_map

    def _parse_individual_answer(self, question_number, correct_answer, answer_mappings):
        """
        解析单个题目的答案，确保返回格式统一的答案字符串
        
        Args:
            question_number (int): 题目编号
            correct_answer (str): 题目中的正确答案字段
            answer_mappings (dict): 从答案汇总中解析的题号->答案映射
            
        Returns:
            str: 格式化的答案字符串，如"A"或"B"
        """
        # 优先使用答案汇总中的答案
        if question_number in answer_mappings:
            answer = answer_mappings[question_number]
            # 提取答案字母部分（比如从"A. Without"中提取"A"）
            if isinstance(answer, str) and len(answer) > 0:
                # 如果是形如"A. Option"或"[A]Option"的格式，提取字母部分
                match = re.match(r'([A-D])[.\s]|^\[([A-D])\]', answer)
                if match:
                    letter = match.group(1) or match.group(2)
                    return letter
                return answer
        
        # 如果答案汇总中没有，尝试从correct_answer中提取
        if correct_answer:
            # 提取字母部分
            match = re.match(r'([A-D])[.\s]|^\[([A-D])\]', correct_answer)
            if match:
                letter = match.group(1) or match.group(2)
                return letter
            # 如果是完整的答案格式，尝试提取首字母
            if len(correct_answer) > 0:
                first_char = correct_answer[0]
                if first_char in "ABCD":
                    return first_char
        
        # 如果都提取不到，返回原始correct_answer或空字符串
        return correct_answer or "" 