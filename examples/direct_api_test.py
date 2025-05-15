#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
简化版测试脚本，直接使用requests库调用Claude API，避免版本兼容问题。
"""

import os
import sys
import json
import argparse
import requests
from pathlib import Path
from dotenv import load_dotenv

# 添加父目录到路径，以便导入src模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入工具模块
from src.docx_reader import DocxReader

def load_api_key():
    """从环境变量加载API密钥"""
    load_dotenv()
    api_key = os.getenv("CLAUDE_API_KEY")
    if not api_key:
        raise ValueError("未找到Claude API密钥。请在.env文件中设置CLAUDE_API_KEY或通过参数提供。")
    return api_key

def call_claude_api(document_text, api_key, model="claude-3-haiku-20240307"):
    """
    直接使用requests库调用Claude API
    
    Args:
        document_text (str): 文档内容
        api_key (str): Claude API密钥
        model (str): 要使用的模型名称
    
    Returns:
        dict: API响应结果
    """
    print(f"正在调用Claude API，使用模型: {model}...")
    
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
    }
  ]
}
```

只返回提取的JSON数据，不要包含任何其他解释或说明文字。确保JSON格式正确无误。
"""
    
    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    
    data = {
        "model": model,
        "system": system_prompt,
        "messages": [
            {"role": "user", "content": document_text}
        ],
        "max_tokens": 4000,
        "temperature": 0.1
    }
    
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code != 200:
        print(f"API请求失败，状态码: {response.status_code}")
        print(f"错误信息: {response.text}")
        return {"error": "API请求失败", "details": response.text}
    
    try:
        result = response.json()
        
        # 提取content字段中的JSON
        if "content" in result and isinstance(result["content"], list):
            for content_item in result["content"]:
                if content_item.get("type") == "text":
                    text = content_item.get("text", "")
                    # 尝试从文本中提取JSON
                    try:
                        import re
                        json_match = re.search(r'(\{[\s\S]*\})', text)
                        if json_match:
                            extracted_json = json.loads(json_match.group(1))
                            print("成功提取JSON数据")
                            return extracted_json
                    except Exception as e:
                        print(f"JSON提取失败: {str(e)}")
                        # 失败时返回原始响应
        
        return result
    except json.JSONDecodeError as e:
        print(f"JSON解析失败: {str(e)}")
        return {"error": "JSON解析失败", "raw_response": response.text}

def process_file(input_file, output_file, api_key, model):
    """处理单个文件"""
    print(f"开始处理文件: {input_file}")
    
    # 读取文档
    docx_reader = DocxReader()
    document_text = docx_reader.read_file(input_file)
    print(f"成功读取文档，内容长度: {len(document_text)} 字符")
    
    # 调用API
    result = call_claude_api(document_text, api_key, model)
    
    # 保存结果
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"处理完成，结果已保存至: {output_file}")
    return True

def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="直接使用requests库调用Claude API处理考研英语真题")
    parser.add_argument("--input", required=True, help="输入的docx文件路径")
    parser.add_argument("--output", required=True, help="输出的JSON文件路径")
    parser.add_argument("--api_key", help="Claude API密钥（如不提供将从环境变量获取）")
    parser.add_argument("--model", default="claude-3-haiku-20240307", help="Claude模型名称")
    
    args = parser.parse_args()
    
    # 获取API密钥
    api_key = args.api_key
    if not api_key:
        try:
            api_key = load_api_key()
        except ValueError as e:
            print(str(e))
            return 1
    
    # 处理文件
    success = process_file(args.input, args.output, api_key, args.model)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main()) 