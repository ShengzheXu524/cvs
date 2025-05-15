#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Claude API调用模块，负责构建请求并调用Claude 3.7 API。
"""

import os
import json
import logging
import time
import requests
from .model_config import get_model, get_model_max_tokens

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
            raise ValueError("未提供API密钥，请设置环境变量CLAUDE_API_KEY或在初始化时提供api_key参数")
        
        # 使用模型配置模块获取模型名称
        self.model = get_model(model)
        # 获取模型的最大token限制
        self.max_tokens = get_model_max_tokens(self.model)
        logger.info(f"使用模型: {self.model}, 最大token: {self.max_tokens}")
        
        # API端点和请求头
        self.api_endpoint = "https://api.anthropic.com/v1/messages"
        self.headers = {
            "x-api-key": self.api_key,
            "content-type": "application/json",
            "anthropic-version": "2023-06-01"
        }
    
    def _make_api_request(self, messages, max_tokens=None, temperature=0.0, max_retries=3, retry_delay=5):
        """
        发送API请求到Claude，使用直接的HTTP请求而不是anthropic库。
        
        Args:
            messages (list): 消息列表
            max_tokens (int, optional): 最大生成的token数，默认为None（使用模型的最大token数）
            temperature (float): 温度参数，控制生成的随机性
            max_retries (int): 最大重试次数
            retry_delay (int): 重试间隔（秒）
            
        Returns:
            dict: API响应结果
        """
        # 如果未指定max_tokens，使用模型的最大值
        if max_tokens is None or max_tokens > self.max_tokens:
            max_tokens = self.max_tokens
            
        payload = {
            "model": self.model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": messages
        }
        
        for attempt in range(max_retries):
            try:
                logger.info(f"发送API请求 (尝试 {attempt+1}/{max_retries})...")
                
                response = requests.post(
                    self.api_endpoint,
                    headers=self.headers,
                    json=payload
                )
                
                if response.status_code == 200:
                    # 成功响应
                    return response.json()
                else:
                    # 错误响应
                    error_data = response.json()
                    logger.error(f"API请求失败，状态码: {response.status_code}")
                    logger.error(f"错误详情: {json.dumps(error_data, indent=2)}")
                    
                    if attempt < max_retries - 1:
                        logger.info(f"将在{retry_delay}秒后重试")
                        time.sleep(retry_delay)
                    else:
                        logger.error("达到最大重试次数")
                        return {"error": error_data}
            
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
    
    def analyze_document(self, document_text, max_retries=3, retry_delay=5):
        """
        使用Claude分析文档内容。
        
        Args:
            document_text (str): 文档文本内容
            max_retries (int, optional): 最大重试次数
            retry_delay (int, optional): 重试延迟时间（秒）
        
        Returns:
            dict: 分析结果
        """
        logger.info("开始分析文档...")
        
        # 构建消息
        messages = [
            {"role": "user", "content": f"请分析以下考研英语真题文档，提取所有题目内容和答案:\n\n{document_text}"}
        ]
        
        try:
            # 发送API请求，不指定max_tokens，让模型自行决定返回长度
            result = self._make_api_request(
                messages=messages,
                temperature=0.0,
                max_retries=max_retries,
                retry_delay=retry_delay
            )
            
            if "error" in result:
                logger.error("分析文档失败")
                return result
            
            # 提取响应内容
            content = result.get("content", [{}])[0].get("text", "")
            
            # 尝试从文本中提取JSON
            try:
                json_data = self._extract_json(content)
                return json.loads(json_data)
            except json.JSONDecodeError as e:
                logger.error(f"JSON解析失败: {str(e)}")
                return {"error": "JSON解析失败", "raw_response": content}
            
        except Exception as e:
            logger.exception(f"分析文档时出错: {str(e)}")
            return {"error": str(e)}
    
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
    }
    // 注意：实际返回结果必须包含所有52个题目（题号1-52），以上仅为每种题型的示例
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

        # 构建消息
        messages = [
            {"role": "user", "content": f"{system_prompt}\n\n文档内容:\n{document_text}"}
        ]
        
        # 使用足够大的max_tokens值，确保返回完整内容
        logger.info("开始提取结构化数据...")
        try:
            result = self._make_api_request(
                messages=messages,
                # 使用模型配置的最大值，会被_make_api_request自动处理为合适的值
                temperature=0.0,
                max_retries=max_retries,
                retry_delay=retry_delay
            )
            
            if "error" in result:
                logger.error("提取结构化数据失败")
                return result
            
            # 提取响应内容
            content = result.get("content", [{}])[0].get("text", "")
            
            # 尝试从文本中提取JSON
            try:
                json_str = self._extract_json(content)
                return json.loads(json_str)
            except json.JSONDecodeError as e:
                logger.error(f"JSON解析失败: {str(e)}")
                return {"error": "JSON解析失败", "raw_response": content}
        
        except Exception as e:
            logger.exception(f"提取结构化数据时出错: {str(e)}")
            return {"error": str(e)} 