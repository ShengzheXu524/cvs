#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试四段处理功能
此脚本用于验证四段处理流程的正确性和有效性
"""

import os
import sys
import json
import logging
import argparse
import time
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("test_four_segment")

# 添加父目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class MockOpenRouterHandler:
    """模拟OpenRouter处理器，记录API调用但不实际发送请求"""
    
    def __init__(self, model=None):
        self.model = model or "mock_model"
        self.calls = []
    
    def get_structured_data(self, prompt, max_tokens=4096, temperature=0.1):
        """模拟API调用，记录参数，返回模拟数据"""
        # 记录调用
        self.calls.append({
            "prompt": prompt,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "timestamp": datetime.now().isoformat()
        })
        
        # 根据prompt内容返回不同的模拟数据
        if "sections中的cloze和readings部分" in prompt:
            # 第一段：metadata + cloze + readings
            return {
                "metadata": {"year": "2024", "exam_type": "英语（一）"},
                "sections": {
                    "cloze": {
                        "original_text": "模拟完形填空原文",
                        "restored_text": "模拟完形填空还原文",
                        "answers_summary": "1.A 2.B 3.C"
                    },
                    "reading": {
                        "text_1": {
                            "original_text": "模拟阅读1原文",
                            "answers_summary": "21.A 22.B 23.C"
                        },
                        "text_2": {
                            "original_text": "模拟阅读2原文",
                            "answers_summary": "26.A 27.B 28.C"
                        }
                    }
                }
            }
        elif "sections中的new_type, translation, writing" in prompt:
            # 第二段：sections中的剩余部分
            return {
                "sections": {
                    "new_type": {
                        "original_text": "模拟新题型原文",
                        "answers_summary": "41.A 42.B 43.C"
                    },
                    "translation": {
                        "original_text": "模拟翻译原文",
                        "answers_summary": "参考译文..."
                    },
                    "writing": {
                        "part_a": {
                            "original_text": "模拟小作文题目",
                            "answers_summary": "参考答案..."
                        },
                        "part_b": {
                            "original_text": "模拟大作文题目",
                            "answers_summary": "参考答案..."
                        }
                    }
                }
            }
        elif "题目1-25" in prompt:
            # 第三段：题目1-25
            return {
                "questions": [
                    {
                        "number": i,
                        "section_type": "完形填空" if i <= 20 else "阅读Text 1",
                        "stem": f"题目{i}的题干",
                        "options": "A. 选项A, B. 选项B, C. 选项C, D. 选项D",
                        "correct_answer": "A. 选项A"
                    } for i in range(1, 26)
                ]
            }
        elif "题目26-52" in prompt:
            # 第四段：题目26-52
            return {
                "questions": [
                    {
                        "number": i,
                        "section_type": "阅读Text " + str(1 + (i - 26) // 5) if i <= 40 else 
                                        "新题型" if i <= 45 else 
                                        "翻译" if i <= 50 else "写作",
                        "stem": f"题目{i}的题干",
                        "options": "A. 选项A, B. 选项B, C. 选项C, D. 选项D" if i <= 45 else "",
                        "correct_answer": "A. 选项A" if i <= 45 else "参考答案"
                    } for i in range(26, 53)
                ]
            }
        else:
            # 默认返回空数据
            return {
                "metadata": {"year": "2024", "exam_type": "英语（一）"},
                "sections": {},
                "questions": []
            }

def test_four_segment_process(document_text, output_dir="test_results"):
    """
    测试四段处理功能
    
    Args:
        document_text: 文档文本内容
        output_dir: 输出目录
    
    Returns:
        bool: 测试是否成功
    """
    from src.content_analyzer import ContentAnalyzer
    
    logger.info("开始测试四段处理功能...")
    
    try:
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
        
        # 创建模拟处理器
        mock_handler = MockOpenRouterHandler()
        
        # 初始化内容分析器
        content_analyzer = ContentAnalyzer(api_handler=mock_handler)
        
        # 执行数据提取
        start_time = time.time()
        result = content_analyzer._extract_data_in_segments(document_text)
        elapsed_time = time.time() - start_time
        
        # 检查API调用次数
        logger.info(f"API调用次数: {len(mock_handler.calls)}")
        if len(mock_handler.calls) != 4:
            logger.warning(f"❌ API调用次数不符合预期，应该是4次，实际是{len(mock_handler.calls)}次")
        else:
            logger.info("✅ API调用次数符合预期，正确使用了四段处理")
        
        # 检查各部分提示词
        call_types = []
        for i, call in enumerate(mock_handler.calls):
            prompt = call["prompt"]
            if "sections中的cloze和readings部分" in prompt:
                call_types.append("第一段：metadata + cloze + readings")
                logger.info(f"✅ 调用{i+1}正确使用了第一段提示词")
            elif "sections中的new_type, translation, writing" in prompt:
                call_types.append("第二段：剩余sections")
                logger.info(f"✅ 调用{i+1}正确使用了第二段提示词")
            elif "题目1-25" in prompt:
                call_types.append("第三段：题目1-25")
                logger.info(f"✅ 调用{i+1}正确使用了第三段提示词")
            elif "题目26-52" in prompt:
                call_types.append("第四段：题目26-52")
                logger.info(f"✅ 调用{i+1}正确使用了第四段提示词")
            else:
                call_types.append("未知类型")
                logger.warning(f"❌ 调用{i+1}使用了未识别的提示词")
        
        # 检查是否涵盖所有四种类型
        expected_types = [
            "第一段：metadata + cloze + readings",
            "第二段：剩余sections",
            "第三段：题目1-25",
            "第四段：题目26-52"
        ]
        missing_types = [t for t in expected_types if t not in call_types]
        if missing_types:
            logger.warning(f"❌ 缺少以下类型的调用: {missing_types}")
        else:
            logger.info("✅ 成功调用了所有四种类型的提示词")
        
        # 检查结果的完整性
        questions = result.get("questions", [])
        if len(questions) != 52:
            logger.warning(f"❌ 结果中的题目数量不符合预期，应该是52道，实际是{len(questions)}道")
        else:
            logger.info("✅ 结果中包含了所有52道题目")
        
        # 检查sections的完整性
        sections = result.get("sections", {})
        expected_sections = ["cloze", "reading", "new_type", "translation", "writing"]
        missing_sections = [s for s in expected_sections if s not in sections]
        if missing_sections:
            logger.warning(f"❌ 结果中缺少以下sections: {missing_sections}")
        else:
            logger.info("✅ 结果中包含了所有必要的sections")
        
        # 保存结果
        output_path = os.path.join(output_dir, "four_segment_test_result.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        logger.info(f"测试结果已保存到: {output_path}")
        
        # 保存API调用记录
        calls_path = os.path.join(output_dir, "four_segment_api_calls.json")
        with open(calls_path, "w", encoding="utf-8") as f:
            json.dump(mock_handler.calls, f, ensure_ascii=False, indent=2)
        logger.info(f"API调用记录已保存到: {calls_path}")
        
        logger.info(f"测试完成，耗时: {elapsed_time:.2f} 秒")
        return True
        
    except Exception as e:
        logger.error(f"测试过程中出错: {str(e)}", exc_info=True)
        return False

def main():
    """程序主入口"""
    parser = argparse.ArgumentParser(description="测试四段处理功能")
    parser.add_argument("--input", required=True, help="输入文档路径")
    parser.add_argument("--output-dir", default="test_results", help="输出目录")
    
    args = parser.parse_args()
    
    # 检查文件是否存在
    if not os.path.exists(args.input):
        logger.error(f"文件不存在: {args.input}")
        return 1
    
    # 读取文档内容
    try:
        with open(args.input, 'r', encoding='utf-8') as f:
            document_text = f.read()
    except Exception as e:
        logger.error(f"读取文件失败: {str(e)}")
        return 1
    
    # 测试四段处理功能
    success = test_four_segment_process(document_text, args.output_dir)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main()) 