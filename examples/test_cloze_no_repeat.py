#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试完形填空原文不重复处理
"""

import os
import sys
import json
import logging
from dotenv import load_dotenv
import anthropic

# 添加src目录到路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.data_organizer import DataOrganizer

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("cloze_test")

def test_api_call():
    """简单的API调用测试"""
    # 加载环境变量
    load_dotenv()
    
    # 从环境变量获取API密钥
    api_key = os.getenv("CLAUDE_API_KEY")
    if not api_key:
        logger.error("未找到API密钥，请设置CLAUDE_API_KEY环境变量")
        return False
    
    try:
        # 创建客户端
        client = anthropic.Anthropic(api_key=api_key)
        
        # 简单的测试文本
        test_text = """
完形填空测试
In the past, I have usually [1] myself as optimistic, but i am feeling rather 
[2] these days. It seems that my [3] is becoming rather negative,and I find myself [4] about life.

Section A: 完形填空
Directions: For each blank in the following passage there are four choices given below and
marked A), B), C) and D). Choose the one that best fits into the textual meaning of the passage
or fits into the grammatical structure and blacken the corresponding letter on the Answer Sheet.

For years, British historian Richard Sears has been making entries in what has become 
one of the world's most popular websites for Chinese language lovers: www.chineseetymology.org. 
The website [1] thousands of images showing Chinese character evolution from ancient 
to modern scripts, in a [2] manner that's much like flipping 
through pages in a book. In fact, in 2007, Sears decided to [3]
his website collection into a book about the story of Chinese characters.

1. A) contains     B) provides     C) reflects     D) displays
2. A) confident    B) fluent       C) logical      D) natural
3. A) alter        B) compile      C) transfer     D) translate

答案：1. A  2. B  3. D
        """
        
        # 测试提示词
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
- 每道题的"试卷答案"字段应该只包含该题的单独答案，如"A"、"B"、"C"或"D"，不要包含完整选项内容。

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
    // ... 其他题目
  ]
}
```

注意事项：
1. sections部分要提供每个题型的完整原文，这些原文将被所有相应题号的题目共享
2. questions部分不要包含重复的原文，只包含题目的具体信息（题号、题干、选项等）
3. 对于完形填空题，原文只在sections.cloze中出现一次，不要在每道题的数据中重复包含原文

只返回提取的JSON数据，不要包含任何其他解释或说明文字。确保JSON格式正确无误。
"""
        
        logger.info("发送测试请求...")
        response = client.messages.create(
            model="claude-3-7-sonnet-20240229",
            system=system_prompt,
            messages=[{"role": "user", "content": test_text}],
            max_tokens=4000,
            temperature=0.1,
        )
        
        result_text = response.content[0].text
        
        # 保存原始响应
        os.makedirs("../test_results", exist_ok=True)
        with open("../test_results/cloze_test_response.txt", "w", encoding="utf-8") as f:
            f.write(result_text)
        
        # 提取JSON
        try:
            # 查找JSON开始标记
            json_start = result_text.find('{')
            if json_start >= 0:
                result = json.loads(result_text[json_start:])
                
                # 保存JSON结果
                with open("../test_results/cloze_test_result.json", "w", encoding="utf-8") as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
                
                # 验证结果
                if "sections" in result and "cloze" in result.get("sections", {}):
                    logger.info("测试成功! 找到了sections.cloze部分")
                    
                    # 检查questions部分是否每道题都包含完形填空原文
                    cloze_questions = [q for q in result.get("questions", []) if q.get("section_type") == "完形填空"]
                    
                    duplicated_original_text = False
                    for q in cloze_questions:
                        if "original_text" in q:
                            duplicated_original_text = True
                            break
                    
                    if not duplicated_original_text:
                        logger.info("验证成功! 完形填空题目不包含重复的原文")
                    else:
                        logger.warning("验证失败! 完形填空题目包含重复的原文")
                    
                    return True
                else:
                    logger.error("未找到sections.cloze部分")
                    return False
            else:
                logger.error("无法找到JSON数据")
                return False
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析失败: {str(e)}")
            return False
        
    except Exception as e:
        logger.exception(f"测试失败: {str(e)}")
        return False

def main():
    """主函数"""
    success = test_api_call()
    
    if success:
        logger.info("测试完成，API调用成功!")
        return 0
    else:
        logger.error("测试失败")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 