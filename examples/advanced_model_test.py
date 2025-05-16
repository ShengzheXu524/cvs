#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
高级OpenRouter模型测试脚本
用于测试OpenRouter API支持的各种模型的能力和性能差异
"""

import os
import sys
import json
import time
import logging
import argparse
from dotenv import load_dotenv

# 添加父目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.openrouter_api import OpenRouterAPI
from src.model_config import list_available_models, get_model_info, get_model

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("advanced_model_test")

def test_model(api_key, model_name, test_prompt, save_results=False, site_url=None, site_name=None):
    """测试特定模型的API调用"""
    logger.info(f"\n======= 测试模型: {model_name} =======")
    
    # 创建OpenRouterAPI实例
    openrouter = OpenRouterAPI(
        api_key=api_key, 
        model=model_name,
        site_url=site_url,
        site_name=site_name
    )
    
    # 发送测试请求
    logger.info("发送测试请求...")
    start_time = time.time()
    
    messages = [
        {"role": "user", "content": test_prompt}
    ]
    
    try:
        # 打印请求的有效载荷
        payload = {
            "model": model_name,
            "max_tokens": 1000,
            "temperature": 0.3,
            "messages": messages,
            "allow_training": "true",
            "allow_logging": "true"
        }
        logger.info(f"请求体: {json.dumps(payload, indent=2)}")
        
        # 发送请求
        response = openrouter._make_api_request(
            messages=messages,
            max_tokens=1000,
            temperature=0.3,
            routes_params={"allow_training": "true", "allow_logging": "true"}
        )
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        if "error" in response:
            logger.error(f"测试请求失败: {response['error']}")
            return {
                "model": model_name,
                "success": False,
                "error": response.get("error"),
                "time_seconds": elapsed_time
            }
        
        # 解析响应
        content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
        
        # 打印token使用情况
        usage = response.get("usage", {})
        logger.info(f"模型响应 ({len(content)} 字符):\n {content[:200]}...")
        logger.info(f"响应时间: {elapsed_time:.2f} 秒")
        logger.info("Token使用情况:")
        logger.info(f"- 输入tokens: {usage.get('prompt_tokens', 'N/A')}")
        logger.info(f"- 输出tokens: {usage.get('completion_tokens', 'N/A')}")
        logger.info(f"- 总tokens: {usage.get('total_tokens', 'N/A')}")
        
        # 保存结果到文件
        if save_results:
            result_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../test_results")
            os.makedirs(result_dir, exist_ok=True)
            
            # 清理模型名称，用于文件名
            safe_model_name = model_name.replace("/", "_").replace(":", "_")
            result_file = os.path.join(result_dir, f"{safe_model_name}_result.json")
            
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "model": model_name,
                    "prompt": test_prompt,
                    "response": content,
                    "usage": usage,
                    "time_seconds": elapsed_time
                }, f, ensure_ascii=False, indent=2)
            
            logger.info(f"结果已保存到: {result_file}")
        
        return {
            "model": model_name,
            "success": True,
            "response": content,
            "tokens": usage,
            "time_seconds": elapsed_time
        }
    
    except Exception as e:
        logger.exception(f"测试中发生错误: {str(e)}")
        return {
            "model": model_name,
            "success": False,
            "error": str(e),
            "time_seconds": time.time() - start_time
        }

def get_test_prompt(prompt_type="extraction"):
    """获取用于测试的提示词"""
    prompts = {
        "short": "用简短的一段话描述考研英语的重要性和备考方法。",
        
        "extraction": """
请分析下面的考研英语真题文档，提取所有题目内容和相关信息。
请以JSON格式返回结果，确保包含所有必要信息。

# 分析任务
请分析这份考研英语真题文档片段，并提取以下信息：
1. 基本信息（年份、考试类型）
2. 完形填空原文和答案汇总

# 文档片段
Section I Use of English
Directions:
Read the following text.Choose the best word(s)for each numbered blank and mark A, B,C or D on the ANSWER SHEET.(10 points)
There's nothing more welcoming than a door opening for you. 1 the need to be touched to open or close,automatic doors are essential in 2 disabled access to buildings and helping provide general 3 to commercial buildings.
Self-sliding doors began to emerge as a commercial product in 1960 after being invented six years 4 by Americans Dee Horton and Lew Hewitt.They 5 as a novelty feature,but as their use has grown,their 6 have extended within our technologically advanced world.Particularly 7 in busy locations or during times of emergency,the doors 8 crowd management by reducing the obstacles put in peoples'way.
9 making access both in and out of buildings easier for people,the difference
in the way many of these doors open helps reduce the total area 10 by them.

# 答案部分
Section I
1. D) Without
2. C) improving
3. B) convenience
4. A) previously
5. B) started out
6. C) benefits
7. A) useful
8. D) act as 
9. A) As well as
10. D) occupied

# 输出格式
请以下面的JSON格式返回结果：

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
    }
  }
}

注意事项：
1. 确保提取完整的原文，包括所有空格标记
2. 在还原后文本中，用实际的单词或短语替换空格标记
3. 答案汇总应包含完形填空部分的所有答案

请生成完整的JSON结构，确保格式正确无误。
        """
    }
    
    return prompts.get(prompt_type, prompts["short"])

def list_models():
    """列出所有可用的模型"""
    models = list_available_models()
    
    print("\n=== 可用的模型 ===")
    print(f"总数: {len(models)}")
    print("\n免费模型:")
    for model in models:
        if model["type"] == "free":
            print(f"- {model['name']} ({model['description']})")
    
    print("\n付费模型:")
    for model in models:
        if model["type"] == "paid":
            print(f"- {model['name']} ({model['description']})")
    
def main():
    """主函数"""
    # 加载环境变量
    load_dotenv()
    
    # 获取API密钥
    api_key = os.getenv("OPENROUTER_API_KEY")
    site_url = os.getenv("SITE_URL")
    site_name = os.getenv("SITE_NAME")
    
    if not api_key:
        logger.error("未找到API密钥，请设置OPENROUTER_API_KEY环境变量")
        return 1
    
    parser = argparse.ArgumentParser(description="测试OpenRouter API模型的能力和性能")
    parser.add_argument("--list", action="store_true", help="列出所有可用模型")
    parser.add_argument("--save", action="store_true", help="保存测试结果到文件")
    parser.add_argument("--prompt", choices=["short", "extraction"], default="extraction", 
                        help="选择提示词类型 (默认: extraction)")
    parser.add_argument("--model", help="要测试的模型名称，如不提供则使用默认模型")
    parser.add_argument("--compare", help="要与默认模型进行对比测试的另一个模型名称")
    
    args = parser.parse_args()
    
    if args.list:
        list_models()
        return 0
    
    # 获取默认模型，使用环境变量中的DEFAULT_MODEL
    default_model = get_model()
    logger.info(f"默认模型: {default_model}")
    
    # 测试提示词
    test_prompt = get_test_prompt(args.prompt)
    results = []
    
    # 仅测试指定模型或默认模型
    if args.model:
        # 用户指定了特定模型
        result = test_model(api_key, args.model, test_prompt, args.save, site_url, site_name)
        results.append(result)
    elif args.compare:
        # 用户要求对比测试
        # 先测试默认模型
        default_result = test_model(api_key, default_model, test_prompt, args.save, site_url, site_name)
        results.append(default_result)
        time.sleep(2)  # 添加短暂延迟，避免API限制
        
        # 再测试比较模型
        compare_result = test_model(api_key, args.compare, test_prompt, args.save, site_url, site_name)
        results.append(compare_result)
    else:
        # 只测试默认模型
        result = test_model(api_key, default_model, test_prompt, args.save, site_url, site_name)
        results.append(result)
    
    # 如果有多个结果才打印对比表格
    if len(results) > 1:
        # 打印测试结果总结
        logger.info("\n======= 测试结果对比 =======")
        logger.info(f"{'模型':<40} | {'状态':<10} | {'响应时间(秒)':<15} | {'总tokens':<10}")
        logger.info("-" * 80)
        
        for result in results:
            status = "成功" if result.get("success") else "失败"
            time_str = f"{result.get('time_seconds', 0):.2f}" if result.get("success") else "N/A"
            tokens = result.get("tokens", {}).get("total_tokens", "N/A") if result.get("success") else "N/A"
            
            logger.info(f"{result.get('model', 'Unknown'):<40} | {status:<10} | {time_str:<15} | {tokens:<10}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 