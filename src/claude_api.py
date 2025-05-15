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

logger = logging.getLogger("考研英语真题处理.claude_api")

class ClaudeAPI:
    """
    Claude API调用器，用于发送请求到Claude 3.7 API。
    """
    
    def __init__(self, api_key=None, model="claude-3-7-sonnet-20240229"):
        """
        初始化Claude API调用器。
        
        Args:
            api_key (str, optional): Claude API密钥
            model (str, optional): 使用的Claude模型
        """
        self.api_key = api_key
        if not self.api_key:
            # 尝试从环境变量获取API密钥
            self.api_key = os.getenv("CLAUDE_API_KEY")
            
        if not self.api_key:
            raise ValueError("未提供Claude API密钥。请通过参数提供或设置CLAUDE_API_KEY环境变量。")
            
        self.model = model
        # 使用简化的初始化方式，避免版本兼容问题
        self.client = Anthropic(api_key=self.api_key)
        logger.info(f"初始化Claude API客户端，使用模型: {model}")
        
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
                
                message = self.client.messages.create(
                    model=self.model,
                    system=system_prompt,
                    messages=[{"role": "user", "content": user_message}],
                    max_tokens=4000,
                    temperature=0.1,
                )
                
                response_text = message.content[0].text
                
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
        使用更详细的提示词从文档中提取结构化数据。
        
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
      "original_text": "完形填空原文（卷面版本，包含[1], [2]等标记）",
      "restored_text": "完形填空原文（还原后版本，已将答案填入）",
      "answers_summary": "完形填空答案汇总，如'1.D 2.C 3.B...'"
    },
    "reading": {
      "text_1": {
        "original_text": "阅读Text 1原文",
        "answers_summary": "阅读Text 1答案汇总，如'21.D 22.D 23.A...'"
      },
      "text_2": {
        "original_text": "阅读Text 2原文",
        "answers_summary": "阅读Text 2答案汇总"
      },
      "text_3": {
        "original_text": "阅读Text 3原文",
        "answers_summary": "阅读Text 3答案汇总"
      },
      "text_4": {
        "original_text": "阅读Text 4原文",
        "answers_summary": "阅读Text 4答案汇总"
      }
    },
    "new_type": {
      "original_text": "新题型原文",
      "restored_text": "新题型还原后原文（如果有的话，否则与原文相同）",
      "answers_summary": "新题型答案汇总"
    },
    "translation": {
      "original_text": "翻译题原文",
      "answers_summary": "无客观答案，可填写'N/A'"
    },
    "writing": {
      "part_a": {
        "original_text": "写作A题目",
        "answers_summary": "无客观答案，可填写'N/A'"
      },
      "part_b": {
        "original_text": "写作B题目",
        "answers_summary": "无客观答案，可填写'N/A'"
      }
    }
  },
  "questions": [
    {
      "number": 1,
      "section_type": "完型填空",
      "stem": "题干（完形填空通常为空或'/'）",
      "options": "A. Without, B. Though, C. Despite, D. Besides",
      "correct_answer": "A. Without",
      "distractor_options": "B. Though, C. Despite, D. Besides"
    },
    // ... 其他题目，总共应有52个题目
    {
      "number": 52,
      "section_type": "写作B",
      "stem": "写作B题目描述",
      "options": null,
      "correct_answer": null,
      "distractor_options": null
    }
  ]
}
```

只返回提取的JSON数据，不要包含任何其他解释或说明文字。确保JSON格式正确无误。
"""

        for attempt in range(max_retries):
            try:
                logger.info(f"正在发送结构化数据提取请求，尝试次数: {attempt + 1}/{max_retries}")
                
                message = self.client.messages.create(
                    model=self.model,
                    system=system_prompt,
                    messages=[{"role": "user", "content": document_text}],
                    max_tokens=30000,  # 增大token数以容纳完整响应
                    temperature=0.1,
                )
                
                response_text = message.content[0].text
                
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