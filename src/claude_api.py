#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Claude API调用模块，负责构建请求并调用Claude 3.7 API。
"""

import os
import json
import logging
import time
from anthropic import Anthropic
from .model_config import get_model

logger = logging.getLogger("考研英语真题处理.claude_api")

class ClaudeAPI:
    """
    Claude API调用器，用于发送请求到Claude 3.7 API。
    """
    
    def __init__(self, api_key=None, model=None):
        """
        初始化Claude API调用器。
        
        Args:
            api_key (str, optional): Claude API密钥
            model (str, optional): 使用的Claude模型名称或模型类型标识符
                可以是具体模型名称，如"claude-3-7-sonnet-20250219"
                也可以是类型标识符，如"default", "fastest", "balanced", "most_capable"
        """
        self.api_key = api_key
        if not self.api_key:
            # 尝试从环境变量获取API密钥
            self.api_key = os.getenv("CLAUDE_API_KEY")
            
        if not self.api_key:
            raise ValueError("未提供Claude API密钥。请通过参数提供或设置CLAUDE_API_KEY环境变量。")
        
        # 使用model_config模块获取模型名称    
        self.model = get_model(model)
        
        # 使用简化的初始化方式，避免版本兼容问题
        # 只使用api_key参数，不使用任何其他可能导致兼容性问题的参数
        self.client = Anthropic(api_key=self.api_key)
        logger.info(f"初始化Claude API客户端，使用模型: {self.model}")
        
    def analyze_document(self, document_text, max_retries=3, retry_delay=5):
        """
        发送文档内容到Claude API进行分析。
        
        Args:
            document_text (str): 文档文本内容
            max_retries (int, optional): 最大重试次数
            retry_delay (int, optional): 重试延迟时间（秒）
        
        Returns:
            dict: Claude API的分析结果
        """
        system_prompt = """
你是一个专业的考研英语真题文档分析工具。你的任务是分析考研英语真题docx文件的内容，提取所有题目和原文信息，并按照规定格式输出结构化数据。

请仔细识别文件中的考试年份、考试类型（英语一或英语二）、各个题型、原文内容、题目内容、选项和答案等信息。

文档内容可能包括：
1. 完形填空题（题号1-20）：包含原文和选项
2. 阅读理解题（题号21-40）：包括四篇阅读短文（Text 1至Text 4），每篇有5个题目
3. 新题型（题号41-45）：包含原文和问题
4. 翻译题（题号46-50）：包含原文段落
5. 写作题（题号51-52）：包含写作A和写作B的题目说明

请按照以下结构对每个题目进行分析，并以JSON格式返回：
1. 所有题目共52个，按题号1-52排列
2. 对于每个题目，提取以下信息：
   - 年份：考试年份
   - 考试类型：英语（一）或英语（二）
   - 题型：完形填空、阅读 Text 1-4、新题型、翻译、写作A或写作B
   - 原文（卷面）：原始试卷上的原文内容，完形填空需包含空格标记如[1], [2]等
   - 试卷答案：试卷上的标准答案
   - 题目编号：1-52之间的数字
   - 题干：题目的具体内容（完形填空可空）
   - 选项：选择题的选项（A, B, C, D）
   - 正确答案：该题的正确答案
   - 原文（还原后）：将正确答案填入原文后的完整版本
   - 干扰选项：错误的选项列表

只返回JSON格式的分析结果，不要包含任何其他解释或额外文本。确保JSON结构完整，所有字段名称准确，值符合要求。
"""
        
        user_message = f"""
请分析以下考研英语真题文档，提取结构化信息：

{document_text}

请以JSON格式返回分析结果，确保包含所有52个题目（题号1-52）的完整信息。每个题目需包含：年份、考试类型、题型、原文（卷面）、试卷答案、题目编号、题干、选项、正确答案、原文（还原后）、干扰选项。
"""

        for attempt in range(max_retries):
            try:
                logger.info(f"正在发送API请求，尝试次数: {attempt + 1}/{max_retries}")
                
                # 使用流式处理API，避免超时问题
                response_text = ""
                with self.client.messages.stream(
                    model=self.model,
                    system=system_prompt,
                    messages=[{"role": "user", "content": user_message}],
                    max_tokens=20000,
                    temperature=0.1,
                ) as stream:
                    logger.info("开始接收流式响应...")
                    for text in stream.text_stream:
                        response_text += text
                        # 可选：每收到1000个字符打印一次进度
                        if len(response_text) % 1000 == 0:
                            logger.debug(f"已接收 {len(response_text)} 个字符")
                
                logger.info(f"流式传输完成，共接收 {len(response_text)} 个字符")
                
                # 尝试解析JSON
                try:
                    # 提取JSON部分（如果有额外文本）
                    json_text = self._extract_json(response_text)
                    result = json.loads(json_text)
                    logger.info("成功接收并解析API响应")
                    return result
                except json.JSONDecodeError as e:
                    logger.warning(f"JSON解析失败: {str(e)}")
                    logger.debug(f"接收到的响应: {response_text}")
                    
                    if attempt < max_retries - 1:
                        logger.info(f"将在{retry_delay}秒后重试")
                        time.sleep(retry_delay)
                    else:
                        logger.error("达到最大重试次数，返回原始响应文本")
                        return {"error": "JSON解析失败", "raw_response": response_text}
            
            except Exception as e:
                logger.error(f"API调用错误: {str(e)}")
                
                if attempt < max_retries - 1:
                    logger.info(f"将在{retry_delay}秒后重试")
                    time.sleep(retry_delay)
                else:
                    logger.error("达到最大重试次数")
                    raise
        
        return {"error": "所有重试均失败"}
    
    def _extract_json(self, text):
        """
        从响应文本中提取JSON部分。
        
        Args:
            text (str): API响应文本
        
        Returns:
            str: 提取的JSON文本
        """
        # 尝试查找JSON开始和结束标记
        start_markers = ['{', '[']
        end_markers = ['}', ']']
        
        for start_marker in start_markers:
            start_idx = text.find(start_marker)
            if start_idx >= 0:
                # 找到开始标记，现在寻找对应的结束标记
                if start_marker == '{':
                    end_marker = '}'
                else:  # start_marker == '['
                    end_marker = ']'
                
                # 计算嵌套级别
                level = 1
                for i in range(start_idx + 1, len(text)):
                    if text[i] == start_marker:
                        level += 1
                    elif text[i] == end_marker:
                        level -= 1
                    
                    if level == 0:
                        # 找到匹配的结束标记
                        return text[start_idx:i+1]
        
        # 如果没有找到明确的JSON标记，返回原始文本
        return text
        
    def extract_structured_data(self, document_text, max_retries=3, retry_delay=5):
        """
        使用更详细的提示词从文档中提取结构化数据，使用流式API避免超时。
        
        Args:
            document_text (str): 文档文本内容
            max_retries (int, optional): 最大重试次数
            retry_delay (int, optional): 重试延迟时间（秒）
        
        Returns:
            dict: 提取的结构化数据
        """
        system_prompt = """
请分析下面的考研英语真题文档，提取所有题目内容和相关信息。
请以JSON格式返回结果，确保包含所有必要信息。

# 分析任务
请分析这份考研英语真题文档，并提取以下信息：
1. 基本信息（年份、考试类型）
2. 各部分题型的原文
3. 各题目的编号、题干、选项、答案及干扰选项
4. 完形填空和特定新题型的还原后原文

# 重要说明
- 必须返回所有52道题目的完整数据！每份考研卷都有固定的52道题，即使原文中有些题目不明显，也请确保返回完整的52道题目。
- "原文"是指该题对应题型板块的试卷上的完整原文内容，不是单个题目的句子。
- 每个题型板块的原文只需在sections部分提取一次，questions部分不应包含重复的原文。
- 完形填空题尤其重要：必须在sections.cloze中提供一份完整的原文（包含所有[1], [2]等标记），questions部分的完形填空题不要包含重复的original_text或restored_text。
- 对于阅读理解、完形填空等所有题型，原文只在sections部分出现一次，所有相同题型的题目共享同一个原文。
- "试卷答案"字段应该包含标准答案汇总，如"1.A 2.B 3.C"；而questions部分的"correct_answer"字段则应包含完整的选项内容，如"A. Without"。

# 题目编号和题型映射
- 题号1-20：完形填空 (Cloze)
- 题号21-25：阅读理解 Text 1 (Reading Text 1)
- 题号26-30：阅读理解 Text 2 (Reading Text 2)
- 题号31-35：阅读理解 Text 3 (Reading Text 3)
- 题号36-40：阅读理解 Text 4 (Reading Text 4)
- 题号41-45：新题型 (New Type)
- 题号46-50：翻译 (Translation)
- 题号51：写作A (Writing Part A)
- 题号52：写作B (Writing Part B)

# 输出格式
请以下面的JSON格式返回结果：

```json
{
  "metadata": {
    "year": "年份，如2024",
    "exam_type": "考试类型，如'英语（一）'"
  },
  "sections": {
    "cloze": {
      "original_text": "完形填空原文（卷面版本，包含[1], [2]等标记，包含整篇文章）",
      "restored_text": "完形填空原文（还原后版本，已将答案填入）",
      "answers_summary": "完形填空答案汇总，如'1.D 2.C 3.B...'"
    },
    "reading": {
      "text_1": {
        "original_text": "阅读Text 1原文（整篇文章）",
        "answers_summary": "阅读Text 1答案汇总，如'21.D 22.D 23.A...'"
      },
      "text_2": {
        "original_text": "阅读Text 2原文（整篇文章）",
        "answers_summary": "阅读Text 2答案汇总"
      },
      "text_3": {
        "original_text": "阅读Text 3原文（整篇文章）",
        "answers_summary": "阅读Text 3答案汇总"
      },
      "text_4": {
        "original_text": "阅读Text 4原文（整篇文章）",
        "answers_summary": "阅读Text 4答案汇总"
      }
    },
    "new_type": {
      "original_text": "新题型原文（完整文章）",
      "restored_text": "新题型还原后原文（如果有的话，否则与原文相同）",
      "answers_summary": "新题型答案汇总"
    },
    "translation": {
      "original_text": "翻译题原文（完整段落）",
      "answers_summary": "无客观答案，可填写'N/A'"
    },
    "writing": {
      "part_a": {
        "original_text": "写作A题目（完整题目描述）",
        "answers_summary": "无客观答案，可填写'N/A'"
      },
      "part_b": {
        "original_text": "写作B题目（完整题目描述）",
        "answers_summary": "无客观答案，可填写'N/A'"
      }
    }
  },
  "questions": [
    {
      "number": 1,
      "section_type": "完形填空",
      "stem": "题干（完形填空通常为空或'/'）",
      "options": "A. Without, B. Though, C. Despite, D. Besides",
      "correct_answer": "A. Without",
      "distractor_options": "B. Though, C. Despite, D. Besides"
    },
    {
      "number": 21,
      "section_type": "阅读理解 Text 1",
      "stem": "According to the passage, the study of music can be beneficial because it",
      "options": "A. helps students perform better in standardized tests, B. enriches students' emotional development, C. increases students' interest in mathematics, D. interferes with students' cognitive development",
      "correct_answer": "B. enriches students' emotional development",
      "distractor_options": "A. helps students perform better in standardized tests, C. increases students' interest in mathematics, D. interferes with students' cognitive development"
    },
    {
      "number": 26,
      "section_type": "阅读理解 Text 2",
      "stem": "The author mentions all of the following as possible reasons for the decline of bees EXCEPT",
      "options": "A. climate change, B. use of agricultural chemicals, C. viral infections, D. poor nutrition",
      "correct_answer": "C. viral infections",
      "distractor_options": "A. climate change, B. use of agricultural chemicals, D. poor nutrition"
    },
    {
      "number": 43,
      "section_type": "新题型",
      "stem": "According to the fourth paragraph, which of the following can be inferred about cultural exchanges?",
      "options": "A. They are universally beneficial to all parties involved, B. They can lead to both positive and negative outcomes, C. They primarily benefit economically developed nations, D. They have little impact on developing countries",
      "correct_answer": "B. They can lead to both positive and negative outcomes",
      "distractor_options": "A. They are universally beneficial to all parties involved, C. They primarily benefit economically developed nations, D. They have little impact on developing countries"
    },
    {
      "number": 47,
      "section_type": "翻译",
      "stem": "请将下列中文段落翻译成英文：随着中国经济的发展，越来越多的人认识到环境保护的重要性...",
      "options": null,
      "correct_answer": null,
      "distractor_options": null
    },
    {
      "number": 51,
      "section_type": "写作A",
      "stem": "Directions: Write an email of about 100 words in response to the following situation. You are organizing a student club meeting and need to change the venue...",
      "options": null,
      "correct_answer": null,
      "distractor_options": null
    },
    {
      "number": 52,
      "section_type": "写作B",
      "stem": "Directions: Write an essay of about 200 words on the following topic: The impact of technology on modern education",
      "options": null,
      "correct_answer": null,
      "distractor_options": null
    }
  ]
}
```

注意事项：
1. sections部分要提供每个题型的完整原文，这些原文将被所有相应题号的题目共享
2. questions部分不要包含重复的原文，只包含题目的具体信息（题号、题干、选项等）
3. 对于完形填空题，原文只在sections.cloze中出现一次，不要在每道题的数据中重复包含原文
4. questions数组必须包含所有52道题目的完整数据（题号1-52），上述示例只展示了部分题型，实际返回必须包含全部题目
5. 正确答案(correct_answer)必须包含选项字母及其完整文本，如"A. Without"，而不仅仅是字母"A"
6. 干扰选项(distractor_options)也必须包含完整的选项内容，如"B. Though, C. Despite, D. Besides"，而不仅仅是"B, C, D"

请提取完整的题型原文，确保"原文（卷面）"字段包含整篇文章或段落，而不仅仅是单个题目对应的句子。请务必返回所有52道题的完整数据，对于文档中不明确的题目，可以标记为[缺失数据]但必须保持题号的完整性。

只返回提取的JSON数据，不要包含任何其他解释或说明文字。确保JSON格式正确无误。
"""

        for attempt in range(max_retries):
            try:
                logger.info(f"正在发送结构化数据提取请求，尝试次数: {attempt + 1}/{max_retries}")
                
                # 使用流式API处理，避免处理大文档时的超时问题
                response_text = ""
                logger.info("开始使用流式API接收结构化数据...")
                
                with self.client.messages.stream(
                    model=self.model,
                    system=system_prompt,
                    messages=[{"role": "user", "content": document_text}],
                    max_tokens=30000,  # 增大token数以容纳完整响应
                    temperature=0.1,
                ) as stream:
                    for text in stream.text_stream:
                        response_text += text
                        # 每处理一定数量的字符输出一次进度
                        if len(response_text) % 2000 == 0:
                            logger.info(f"已接收 {len(response_text)} 个字符...")
                
                logger.info(f"流式传输完成，共接收 {len(response_text)} 个字符")
                
                # 尝试解析JSON
                try:
                    # 提取JSON部分
                    json_text = self._extract_json(response_text)
                    result = json.loads(json_text)
                    logger.info("成功接收并解析结构化数据")
                    return result
                except json.JSONDecodeError as e:
                    logger.warning(f"结构化数据JSON解析失败: {str(e)}")
                    
                    if attempt < max_retries - 1:
                        logger.info(f"将在{retry_delay}秒后重试")
                        time.sleep(retry_delay)
                    else:
                        logger.error("达到最大重试次数，返回原始响应文本")
                        return {"error": "JSON解析失败", "raw_response": response_text}
            
            except Exception as e:
                logger.error(f"结构化数据提取API调用错误: {str(e)}")
                
                if attempt < max_retries - 1:
                    logger.info(f"将在{retry_delay}秒后重试")
                    time.sleep(retry_delay)
                else:
                    logger.error("达到最大重试次数")
                    raise
        
        return {"error": "所有结构化数据提取尝试均失败"} 