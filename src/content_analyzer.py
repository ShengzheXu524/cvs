#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
内容分析模块，负责解析文档内容并提取结构化数据
"""

import os
import json
import logging
import time
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("content_analyzer")

class ContentAnalyzer:
    """内容分析器，负责调用API分析文档内容并提取结构化数据"""
    
    def __init__(self, api_handler, max_tokens=4096, temperature=0.1):
        """
        初始化内容分析器
        
        Args:
            api_handler: API处理器实例，用于调用外部API
            max_tokens: 最大生成token数
            temperature: 生成温度，越低越确定性
        """
        self.api_handler = api_handler
        self.max_tokens = max_tokens
        self.temperature = temperature
    
    def extract_data(self, document_text, save_debug=False, output_dir="test_results"):
        """
        从文档文本中提取结构化数据
        
        Args:
            document_text: 文档文本内容
            save_debug: 是否保存调试信息
            output_dir: 输出目录
        
        Returns:
            dict: 提取的结构化数据
        """
        logger.info("开始提取文档数据...")
        
        # 记录开始时间
        start_time = time.time()
        
        try:
            # 检查文档长度，如果超过一定阈值（3000字符），直接使用分段处理
            if len(document_text) > 3000:
                logger.info(f"文档较长（{len(document_text)}字符），直接使用分段处理...")
                result = self._extract_data_in_segments(document_text, output_dir)
            else:
                # 对于较短的文档，尝试一次性提取
                logger.info(f"文档较短（{len(document_text)}字符），尝试一次性提取...")
                result = self._extract_full_data(document_text, output_dir)
                
                # 检查提取的题目数量是否完整
                questions = result.get("questions", [])
                if len(questions) < 52:
                    logger.info(f"提取的题目数量不完整（{len(questions)}/52），切换到分段提取...")
                    
                    # 分段提取并合并结果
                    result = self._extract_data_in_segments(document_text, output_dir)
            
            # 计算处理时间
            elapsed_time = time.time() - start_time
            logger.info(f"数据提取完成，用时 {elapsed_time:.2f} 秒")
            
            # 保存调试信息
            if save_debug:
                self._save_debug_info(result, document_text, elapsed_time, output_dir)
            
            return result
        
        except Exception as e:
            logger.error(f"提取数据时发生错误: {str(e)}")
            raise
    
    def _extract_full_data(self, document_text, output_dir="test_results"):
        """
        尝试提取完整的结构化数据
        
        Args:
            document_text: 文档文本内容
            output_dir: 输出目录，用于保存调试信息
        
        Returns:
            dict: 提取的结构化数据
        """
        prompt = self._create_extraction_prompt(document_text)
        response = self.api_handler.get_structured_data(
            prompt, 
            max_tokens=self.max_tokens, 
            temperature=self.temperature,
            output_dir=output_dir
        )
        return response
    
    def _extract_data_in_segments(self, document_text, output_dir="test_results"):
        """
        分段提取数据并合并结果
        
        Args:
            document_text: 文档文本内容
            output_dir: 输出目录，用于保存调试信息
            
        将提取分为五部分：
        1. 提取基本信息(metadata)和sections中的cloze和readings部分
        2. 提取sections中的剩余部分(new_type, translation, writing)
        3. 提取题目1-25
        4. 提取题目26-40
        5. 提取题目41-52
        """
        logger.info("开始分段提取数据...")
        
        # 第一部分：提取基本信息和sections中的cloze和readings部分
        logger.info("提取第一部分数据：基本信息和sections中的cloze和readings部分...")
        first_prompt = self._create_segment_prompt(document_text, segment=1)
        try:
            first_response = self.api_handler.get_structured_data(
                first_prompt,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                output_dir=output_dir
            )
        except Exception as e:
            logger.error(f"第一部分数据提取失败: {str(e)}")
            # 创建基本结构
            first_response = {
                "metadata": {"year": "2024", "exam_type": "英语（一）"},
                "sections": {
                    "cloze": {},
                    "reading": {}
                }
            }
        
        logger.info("第一部分数据提取完成，开始提取第二部分...")
        
        # 第二部分：提取sections中的剩余部分(new_type, translation, writing)
        logger.info("提取第二部分数据：sections中的剩余部分...")
        second_prompt = self._create_segment_prompt(document_text, segment=2)
        try:
            second_response = self.api_handler.get_structured_data(
                second_prompt,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                output_dir=output_dir
            )
        except Exception as e:
            logger.error(f"第二部分数据提取失败: {str(e)}")
            second_response = {"sections": {}}
        
        logger.info("第二部分数据提取完成，开始提取第三部分...")
        
        # 第三部分：提取题目1-25
        logger.info("提取第三部分数据：题目1-25...")
        third_prompt = self._create_segment_prompt(document_text, segment=3)
        try:
            third_response = self.api_handler.get_structured_data(
                third_prompt,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                output_dir=output_dir
            )
            
            # 检查第三部分是否提取成功
            if not third_response.get("questions"):
                logger.warning("第三部分未能提取到题目，尝试使用备用提示词...")
                # 尝试使用更简单的提示词
                backup_prompt = self._create_simplified_prompt(document_text, segment=3)
                third_response = self.api_handler.get_structured_data(
                    backup_prompt,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                    output_dir=output_dir
                )
        except Exception as e:
            logger.error(f"第三部分数据提取失败: {str(e)}")
            third_response = {"questions": []}
        
        logger.info("第三部分数据提取完成，开始提取第四部分...")
        
        # 第四部分：提取题目26-40
        logger.info("提取第四部分数据：题目26-40...")
        fourth_prompt = self._create_segment_prompt(document_text, segment=4)
        try:
            fourth_response = self.api_handler.get_structured_data(
                fourth_prompt,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                output_dir=output_dir
            )
        except Exception as e:
            logger.error(f"第四部分数据提取失败: {str(e)}")
            fourth_response = {"questions": []}
            
        logger.info("第四部分数据提取完成，开始提取第五部分...")
        
        # 第五部分：提取题目41-52
        logger.info("提取第五部分数据：题目41-52...")
        fifth_prompt = self._create_segment_prompt(document_text, segment=5)
        try:
            fifth_response = self.api_handler.get_structured_data(
                fifth_prompt,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                output_dir=output_dir
            )
        except Exception as e:
            logger.error(f"第五部分数据提取失败: {str(e)}")
            fifth_response = {"questions": []}
        
        logger.info("第五部分数据提取完成，开始合并结果...")
        
        # 合并sections
        merged_sections = self._merge_sections(first_response.get("sections", {}), second_response.get("sections", {}))
        
        # 合并questions
        first_questions = third_response.get("questions", [])
        second_questions = fourth_response.get("questions", [])
        third_questions = fifth_response.get("questions", [])
        
        logger.info(f"题目1-25数量: {len(first_questions)}, 题目26-40数量: {len(second_questions)}, 题目41-52数量: {len(third_questions)}")
        
        # 如果第三部分没有提取到题目，但第四、五部分成功提取了题目
        if not first_questions and (second_questions or third_questions):
            logger.info("题目1-25未提取到，尝试创建1-25的基本题目结构...")
            # 根据文档内容和第四、五部分数据，尝试创建1-25的基本题目结构
            # 优先使用第二部分数据作为模板
            template_questions = second_questions if second_questions else third_questions
            first_questions = self._create_basic_questions_1_25(document_text, template_questions)
        
        # 合并所有题目
        all_questions = first_questions + second_questions + third_questions
        
        # 创建最终结果
        merged_result = {
            "metadata": first_response.get("metadata", {}),
            "sections": merged_sections,
            "questions": all_questions
        }
        
        # 验证合并后的题目是否连续完整
        self._validate_merged_questions(merged_result["questions"])
        
        logger.info(f"合并完成，共提取 {len(merged_result.get('questions', []))} 道题目")
        return merged_result
    
    def _create_extraction_prompt(self, document_text):
        """创建数据提取提示词"""
        prompt = f"""
请分析下面的考研英语真题文档，提取所有题目内容和相关信息。
请以JSON格式返回结果，确保包含所有必要信息。

# 分析任务
请分析这份考研英语真题文档，并提取以下信息：
1. 基本信息（年份、考试类型）
2. 各部分原文和答案汇总
3. 所有52道题目的详细信息（题干、选项、正确答案、干扰项等）

# 重要说明
1. 请确保返回完整的JSON结构，包含所有52道题目
2. 原文在sections部分只需生成一次，不要在questions部分重复
3. 完形填空的原文请包含空格标记([1], [2]等)
4. 对于每个题目，请提供准确的题干、选项、正确答案和干扰项（干扰项是指除正确答案外的选项）
5. 答案汇总应该按照顺序排列
6. 对于完形填空题(1-20题)，不需要提供stem，可以将stem设置为空字符串或"/"
7. 对于阅读理解题和新题型题，正确答案格式应为"字母]选项内容"，如"D]hiding them from the locals."，而不仅仅是字母

# 文档内容
{document_text}

# 输出格式
请以下面的JSON格式返回结果：

```json
{{
  "metadata": {{
    "year": "年份，如2024",
    "exam_type": "考试类型，如'英语（一）'"
  }},
  "sections": {{
    "cloze": {{
      "original_text": "完形填空原文（卷面版本，包含[1], [2]等标记）",
      "restored_text": "完形填空原文（还原后版本，已将答案填入）",
      "answers_summary": "完形填空答案汇总，如'1.D 2.C 3.B...'"
    }},
    "reading": {{
      "text_1": {{
        "original_text": "阅读Text 1原文",
        "answers_summary": "阅读Text 1答案汇总，如'21.D 22.D 23.A...'"
      }},
      // 其他text_2, text_3, text_4等
    }},
    // 其他部分如new_type, translation, writing等
  }},
  "questions": [
    {{
      "number": 1,
      "section_type": "完形填空",
      "stem": "",  // 完形填空题无需提供stem，设置为空字符串
      "options": "选项文本，如'A. Without, B. Though, C. Despite, D. Besides'",
      "correct_answer": "D. Without",
      "distractors": "干扰项，即除正确答案外的选项，如'A. Though, B. Despite, C. Besides'"
    }},
    {{
      "number": 21,
      "section_type": "阅读理解",
      "stem": "题干文本",
      "options": "A]选项A内容\\n[B]选项B内容\\n[C]选项C内容\\n[D]选项D内容",
      "correct_answer": "D]选项D的完整内容",  // 带字母和选项内容
      "distractors": "A]选项A内容\\n[B]选项B内容\\n[C]选项C内容"  // 除正确答案外的选项
    }},
    // ... 所有52道题目
  ]
}}
```

请确保返回完整的JSON结构，务必包含所有52道题目的信息。
        """
        return prompt
    
    def _create_segment_prompt(self, document_text, segment=1):
        """
        创建分段提取提示词
        
        Args:
            document_text: 文档文本
            segment: 段号（1-5），分别对应：
                    1: 提取基本信息和sections中的cloze和readings部分
                    2: 提取sections中的剩余部分
                    3: 提取题目1-25
                    4: 提取题目26-40
                    5: 提取题目41-52
        
        Returns:
            str: 提示词
        """
        if segment == 1:
            # 第一部分：基本信息和sections中的cloze和readings部分
            prompt = f"""
请分析下面的考研英语真题文档，提取基本信息和sections中的cloze和readings部分。
请以JSON格式返回结果，确保包含所有必要信息。

# 分析任务
请分析这份考研英语真题文档，并提取以下信息：
1. 基本信息（年份、考试类型）
2. sections部分中的cloze（完形填空）和readings（阅读理解）部分原文及答案汇总
不需要提取题目信息。

# 重要说明
1. 请确保返回完整的JSON结构
2. 必须包含完形填空和阅读原文
3. 不需要提取题目信息，题目将在后续步骤提取
4. 完形填空的原文请包含空格标记([1], [2]等)

# 文档内容
{document_text}

# 输出格式
请以下面的JSON格式返回结果：

```json
{{
  "metadata": {{
    "year": "年份，如2024",
    "exam_type": "考试类型，如'英语（一）'"
  }},
  "sections": {{
    "cloze": {{
      "original_text": "完形填空原文（卷面版本，包含[1], [2]等标记）",
      "restored_text": "完形填空原文（还原后版本，已将答案填入）",
      "answers_summary": "完形填空答案汇总，如'1.D 2.C 3.B...'"
    }},
    "reading": {{
      "text_1": {{
        "original_text": "阅读Text 1原文",
        "answers_summary": "阅读Text 1答案汇总，如'21.D 22.D 23.A...'"
      }},
      "text_2": {{
        "original_text": "阅读Text 2原文",
        "answers_summary": "阅读Text 2答案汇总"
      }},
      "text_3": {{
        "original_text": "阅读Text 3原文",
        "answers_summary": "阅读Text 3答案汇总"
      }},
      "text_4": {{
        "original_text": "阅读Text 4原文",
        "answers_summary": "阅读Text 4答案汇总"
      }}
    }}
  }}
}}
```

请确保返回完整的JSON结构，必须包含完形填空和阅读部分的原文和答案汇总，但不要提取具体题目信息。
            """
        elif segment == 2:
            # 第二部分：sections中的剩余部分(new_type, translation, writing)
            prompt = f"""
请分析下面的考研英语真题文档，提取sections中的new_type, translation, writing等剩余部分。
请以JSON格式返回结果，确保包含所有必要信息。

# 分析任务
请分析这份考研英语真题文档，并提取以下内容：
1. sections部分中的new_type（新题型）
2. sections部分中的translation（翻译）
3. sections部分中的writing（写作）
不需要提取metadata和题目信息。

# 重要说明
1. 请确保返回完整的JSON结构
2. 必须包含new_type, translation, writing等完整原文
3. 不需要提取cloze和reading部分，它们已在之前步骤提取
4. 不需要提取题目信息，题目将在后续步骤提取
5. 对于new_type部分，请同时提供原始文本和还原后的文本（删除人名和题号标记的版本）

# 文档内容
{document_text}

# 输出格式
请以下面的JSON格式返回结果：

```json
{{
  "sections": {{
    "new_type": {{
      "original_text": "新题型原文",
      "restored_text": "新题型原文（去除人名和题号标记的还原版本）",
      "answers_summary": "新题型答案汇总，如'41.F 42.C 43.F 44.G 45.B'"
    }},
    "translation": {{
      "original_text": "翻译部分原文",
      "answers_summary": "翻译参考答案"
    }},
    "writing": {{
      "part_a": {{
        "original_text": "小作文题目原文",
        "answers_summary": "小作文参考答案"
      }},
      "part_b": {{
        "original_text": "大作文题目原文",
        "answers_summary": "大作文参考答案"
      }}
    }}
  }}
}}
```

请确保返回完整的JSON结构，必须包含各个部分的原文和答案汇总，但不要提取具体题目信息。
            """
        elif segment == 3:
            # 第三部分：题目1-25
            prompt = f"""
请分析下面的考研英语真题文档，提取题目1-25的内容。
请以JSON格式返回结果，确保包含所有必要信息。

# 分析任务
请分析这份考研英语真题文档，并提取题目1-25的详细信息。
不需要提取基本信息和原文，这些内容已在之前步骤提取。

# 重要说明
1. 请确保返回完整的JSON结构
2. 仅提取题目1-25，不要提取26-52题
3. 题目信息应包括题号、类型、题干、选项、正确答案和干扰项（干扰项是除正确答案外的选项）
4. 对于完形填空题（1-20题），不需要提供stem（题干），可以设置为空字符串或"/"
5. 对于阅读理解题（21-25题及以后），正确答案格式应为"字母]选项内容"，例如"D]hiding them from the locals."

# 文档内容
{document_text}

# 输出格式
请以下面的JSON格式返回结果：

```json
{{
  "questions": [
    // 完形填空题（1-20）
    {{
      "number": 1,
      "section_type": "完形填空",
      "stem": "",  // 完形填空题无需提供stem
      "options": "选项文本，如'A. Without, B. Though, C. Despite, D. Besides'",
      "correct_answer": "D. Without",
      "distractors": "干扰项，即除正确答案外的选项，如'A. Though, B. Despite, C. Besides'"
    }},
    // 阅读理解题（21-25）
    {{
      "number": 21,
      "section_type": "阅读理解",
      "stem": "题干文本",
      "options": "A]选项A内容\\n[B]选项B内容\\n[C]选项C内容\\n[D]选项D内容",
      "correct_answer": "D]选项D的完整内容",  // 带字母和选项内容
      "distractors": "A]选项A内容\\n[B]选项B内容\\n[C]选项C内容"  // 除正确答案外的所有选项
    }},
    // ... 其他题目，到25题为止
  ]
}}
```

请确保返回完整的JSON结构，务必包含题目1-25的完整信息。
            """
        elif segment == 4:
            # 第四部分：题目26-40
            prompt = f"""
请分析下面的考研英语真题文档，提取题目26-40的内容。
请以JSON格式返回结果，确保包含所有必要信息。

# 分析任务
请分析这份考研英语真题文档，并仅提取题目26-40的详细信息。
不需要提取基本信息和原文，这些内容已在之前步骤提取。

# 重要说明
1. 请确保返回完整的JSON结构
2. 只包含题目26-40，不包含1-25或41-52题
3. 题目信息应包括题号、类型、题干、选项、正确答案和干扰项（干扰项是除正确答案外的选项）
4. 对于阅读理解题，正确答案格式应为"字母]选项内容"，例如"B]sharing childcare among community members."，而不仅仅是字母

# 文档内容
{document_text}

# 输出格式
请以下面的JSON格式返回结果：

```json
{{
  "questions": [
    // 仅包含题目26-40
    {{
      "number": 26,
      "section_type": "阅读理解",
      "stem": "题干文本",
      "options": "[A]选项A内容\\n[B]选项B内容\\n[C]选项C内容\\n[D]选项D内容",
      "correct_answer": "B]选项B的完整内容",  // 带字母和选项内容
      "distractors": "[A]选项A内容\\n[C]选项C内容\\n[D]选项D内容"  // 除正确答案外的所有选项
    }},
    // ... 其他题目，到40题为止
  ]
}}
```

请确保返回完整的JSON结构，务必包含题目26-40的完整信息。
            """
        elif segment == 5:
            # 第五部分：题目41-52
            prompt = f"""
请分析下面的考研英语真题文档，提取题目41-52的内容。
请以JSON格式返回结果，确保包含所有必要信息。

# 分析任务
请分析这份考研英语真题文档，并仅提取题目41-52的详细信息。
不需要提取基本信息和原文，这些内容已在之前步骤提取。

# 重要说明
1. 请确保返回完整的JSON结构
2. 只包含题目41-52，不包含1-40题
3. 题目信息应包括题号、类型、题干、选项、正确答案和干扰项（干扰项是除正确答案外的选项）
4. 对于新题型题目，正确答案格式应为"字母]选项内容"，例如"F]Ways to get artifacts from other countries must be decent and lawful."，而不仅仅是字母

# 文档内容
{document_text}

# 输出格式
请以下面的JSON格式返回结果：

```json
{{
  "questions": [
    // 仅包含题目41-52
    {{
      "number": 41,
      "section_type": "新题型",
      "stem": "题干文本",
      "options": "[A]选项A内容\\n[B]选项B内容\\n...",
      "correct_answer": "F]选项F的完整内容",  // 带字母和选项内容
      "distractors": "其他选项内容"  // 除正确答案外的所有选项
    }},
    // ... 其他题目，到52题为止
  ]
}}
```

请确保返回完整的JSON结构，务必包含题目41-52的完整信息。
            """
        else:
            # 第二部分保持不变
            return super()._create_segment_prompt(document_text, segment)
        
        return prompt
    
    def _merge_sections(self, first_sections, second_sections):
        """
        合并两部分sections数据
        
        Args:
            first_sections: 第一部分sections数据（包含cloze和readings）
            second_sections: 第二部分sections数据（包含new_type, translation, writing等）
        
        Returns:
            dict: 合并后的sections数据
        """
        # 创建合并后的sections，基本结构来自第一部分
        merged_sections = first_sections.copy()
        
        # 合并第二部分的sections
        for key, value in second_sections.items():
            if key not in merged_sections:
                merged_sections[key] = value
            else:
                # 如果两部分都有相同的key，合并它们
                if isinstance(merged_sections[key], dict) and isinstance(value, dict):
                    merged_sections[key].update(value)
        
        return merged_sections
    
    def _validate_merged_questions(self, questions):
        """
        验证合并后的题目列表是否连续完整
        
        Args:
            questions: 题目列表
        """
        # 按题号排序
        questions.sort(key=lambda q: q.get("number", 0))
        
        # 验证题号连续性
        expected_numbers = set(range(1, 53))  # 1-52
        actual_numbers = set(q.get("number", 0) for q in questions)
        
        missing_numbers = expected_numbers - actual_numbers
        if missing_numbers:
            logger.warning(f"合并后仍有缺失题目: {sorted(list(missing_numbers))}")
        
        duplicate_numbers = [n for n in actual_numbers if [q.get("number") for q in questions].count(n) > 1]
        if duplicate_numbers:
            logger.warning(f"存在重复题目: {sorted(list(set(duplicate_numbers)))}")
    
    def _save_debug_info(self, result, document_text, elapsed_time, output_dir):
        """保存调试信息"""
        # 获取当前时间字符串，用于文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 确保输出目录存在
        debug_dir = os.path.join(output_dir, "debug")
        os.makedirs(debug_dir, exist_ok=True)
        
        # 构建文件名
        file_base = f"extraction_result_{timestamp}"
        
        # 保存API响应结果
        result_file = os.path.join(debug_dir, f"{file_base}_result.json")
        with open(result_file, 'w', encoding='utf-8') as f:
            # 添加额外的调试信息
            debug_info = {
                "model": self.api_handler.model if hasattr(self.api_handler, 'model') else "unknown",
                "elapsed_time_seconds": elapsed_time,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "result": result
            }
            json.dump(debug_info, f, ensure_ascii=False, indent=2)
        
        logger.info(f"调试信息已保存到: {result_file}")
    
    def _create_simplified_prompt(self, document_text, segment=1):
        """
        创建简化版的提示词，专注于题目提取
        
        Args:
            document_text: 文档文本
            segment: 段号（1-5），与_create_segment_prompt相同
        
        Returns:
            str: 简化的提示词
        """
        if segment == 1:
            # 第一部分：基本信息和sections中的cloze和readings部分
            return f"""
请分析这份考研英语真题文档，提取基本信息和sections中的cloze和readings部分。
只需提取metadata、完形填空和阅读理解部分的原文和答案汇总。
返回JSON格式，包含以下结构：

```json
{{
  "metadata": {{
    "year": "2024",
    "exam_type": "英语（一）"
  }},
  "sections": {{
    "cloze": {{
      "original_text": "完形填空原文",
      "answers_summary": "答案汇总"
    }},
    "reading": {{
      "text_1": {{
        "original_text": "阅读1原文",
        "answers_summary": "答案汇总"
      }},
      // text_2, text_3, text_4
    }}
  }}
}}
```

文档内容:
{document_text}
"""
        elif segment == 2:
            # 第二部分：sections中的剩余部分
            return f"""
请分析这份考研英语真题文档，提取sections中的new_type, translation, writing部分。
只需提取sections中除cloze和reading之外的部分。
返回JSON格式，包含以下结构：

```json
{{
  "sections": {{
    "new_type": {{
      "original_text": "新题型原文",
      "restored_text": "新题型原文（去除人名和题号标记的还原版本）",
      "answers_summary": "答案汇总"
    }},
    "translation": {{
      "original_text": "翻译原文",
      "answers_summary": "答案汇总"
    }},
    "writing": {{
      // 写作部分内容
    }}
  }}
}}
```

文档内容:
{document_text}
"""
        elif segment == 3:
            # 第三部分：题目1-25
            return f"""
请分析这份考研英语真题文档，提取题目1-25的信息。
只需提取题号、题型、题干、选项、正确答案和干扰项，不需要提取原文。

重要说明：
1. 对于完形填空题（1-20题），不需要提供stem（题干），可以设置为空字符串或"/"
2. 对于阅读理解题（21-25题），正确答案格式应为"字母]选项内容"，例如"D]hiding them from the locals."

返回JSON格式，包含以下结构：

```json
{{
  "questions": [
    {{
      "number": 1,
      "section_type": "完形填空",
      "stem": "",  // 完形填空题无需stem
      "options": "选项文本",
      "correct_answer": "D. Without",
      "distractors": "干扰项，即除正确答案外的选项"
    }},
    {{
      "number": 21,
      "section_type": "阅读理解",
      "stem": "题干文本",
      "options": "选项文本",
      "correct_answer": "D]选项D的完整内容",  // 带字母和完整内容
      "distractors": "干扰项，即除正确答案外的选项"
    }},
    // ... 其他题目，到25题为止
  ]
}}
```

文档内容:
{document_text}
"""
        elif segment == 4:
            # 第四部分：题目26-40
            return f"""
请分析这份考研英语真题文档，提取题目26-40的信息。
只需提取题号、题型、题干、选项、正确答案和干扰项，不需要提取原文。

重要说明：
1. 对于阅读理解题，正确答案格式应为"字母]选项内容"，例如"B]sharing childcare among community members."，而不仅仅是字母

返回JSON格式，仅包含questions数组：

```json
{{
  "questions": [
    {{
      "number": 26,
      "section_type": "阅读理解",
      "stem": "题干文本",
      "options": "选项文本",
      "correct_answer": "B]选项B的完整内容",  // 带字母和完整内容
      "distractors": "干扰项，即除正确答案外的选项"
    }},
    // ... 其他题目，到40题为止
  ]
}}
```

文档内容:
{document_text}
"""
        else:  # segment == 5
            # 第五部分：题目41-52
            return f"""
请分析这份考研英语真题文档，提取题目41-52的信息。
只需提取题号、题型、题干、选项、正确答案和干扰项，不需要提取原文。

重要说明：
1. 对于新题型题目，正确答案格式应为"字母]选项内容"，例如"F]Ways to get artifacts from other countries must be decent and lawful."，而不仅仅是字母

返回JSON格式，仅包含questions数组：

```json
{{
  "questions": [
    {{
      "number": 41,
      "section_type": "新题型",
      "stem": "题干文本",
      "options": "选项文本",
      "correct_answer": "F]选项F的完整内容",  // 带字母和完整内容
      "distractors": "干扰项，即除正确答案外的选项"
    }},
    // ... 其他题目，到52题为止
  ]
}}
```

文档内容:
{document_text}
"""
            
    def _create_basic_questions_1_25(self, document_text, second_questions):
        """
        根据文档内容和第二部分题目，创建1-25题的基本结构
        
        Args:
            document_text: 文档文本
            second_questions: 第二部分题目
        
        Returns:
            list: 1-25题的基本结构
        """
        basic_questions = []
        
        # 根据题目编号和分类创建
        for i in range(1, 26):
            question_type = ""
            if 1 <= i <= 20:
                question_type = "完形填空"
            elif 21 <= i <= 25:
                question_type = "阅读Text 1"
            
            # 获取一个示例题目的结构
            question_format = {}
            if second_questions:
                question_format = second_questions[0].copy()
                # 删除非必要字段保留结构
                for key in list(question_format.keys()):
                    if key not in ["number", "section_type", "stem", "options", "correct_answer", "distractors"]:
                        del question_format[key]
            
            # 创建基本题目
            question = question_format.copy() if question_format else {}
            question["number"] = i
            question["section_type"] = question_type
            question["stem"] = f"题号 {i}"
            question["options"] = "选项信息未提取"
            question["correct_answer"] = "答案信息未提取"
            question["distractors"] = "干扰项信息未提取"
            
            basic_questions.append(question)
        
        return basic_questions 