#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
OpenRouter API配置工具，用于设置API密钥和默认模型
"""

import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv, set_key, find_dotenv

# 添加父目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from src.model_config import list_available_models, get_free_models, get_model
from src.openrouter_api import OPENROUTER_API_URL, OPENROUTER_MODELS_API_URL

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("setup_openrouter")

def main():
    """配置OpenRouter API密钥和默认模型"""
    print("\n====== OpenRouter API 配置工具 ======\n")
    print(f"API 端点: {OPENROUTER_API_URL}")
    print(f"模型列表 API 端点: {OPENROUTER_MODELS_API_URL}")
    
    # 尝试加载现有的.env文件
    dotenv_path = find_dotenv()
    if not dotenv_path:
        dotenv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
        Path(dotenv_path).touch(exist_ok=True)
        print(f"创建了新的.env文件: {dotenv_path}")
    else:
        print(f"已找到现有的.env文件: {dotenv_path}")
        load_dotenv(dotenv_path)
    
    # 获取现有的API密钥（如果有）
    current_api_key = os.getenv("OPENROUTER_API_KEY", "")
    if current_api_key:
        print(f"当前的API密钥: {current_api_key[:8]}...{current_api_key[-4:]}")
    
    # 输入新的API密钥
    print("\n请输入您的OpenRouter API密钥 (通常以sk-or-开头)")
    print("如果您还没有API密钥，请访问 https://openrouter.ai/ 注册并创建一个")
    print("要保持现有密钥不变，请直接按回车键")
    
    api_key = input("> ").strip()
    
    if api_key:
        if not api_key.startswith("sk-or-"):
            print("\n警告: 您输入的API密钥似乎不是OpenRouter密钥 (应以sk-or-开头)")
            confirm = input("您确定要继续使用这个密钥吗? (y/n) > ").strip().lower()
            if confirm != 'y':
                print("已取消设置API密钥")
                return 1
        
        # 保存API密钥到.env文件
        set_key(dotenv_path, "OPENROUTER_API_KEY", api_key)
        print("\nAPI密钥已保存到.env文件")
    else:
        print("\n保持现有API密钥不变")
    
    # 配置默认模型
    print("\n---- 可用的免费模型 ----")
    free_models = get_free_models()
    for i, model in enumerate(free_models, 1):
        print(f"{i}. {model}")
    
    # 获取当前的默认模型
    current_model = os.getenv("DEFAULT_MODEL", "")
    if current_model:
        print(f"\n当前默认模型: {current_model}")
    else:
        print("\n当前未设置默认模型")
    
    # 选择新的默认模型
    print("\n要更改默认模型，请输入模型名称或编号")
    print("推荐模型: google/gemini-2.5-flash-preview 或 mistralai/mistral-7b-instruct:free")
    print("要保持当前默认模型不变，请直接按回车键")
    
    model_choice = input("> ").strip()
    
    if model_choice:
        # 如果输入是数字，尝试从免费模型列表中选择
        if model_choice.isdigit():
            idx = int(model_choice) - 1
            if 0 <= idx < len(free_models):
                model = free_models[idx]
                set_key(dotenv_path, "DEFAULT_MODEL", model)
                print(f"\n默认模型已设置为: {model}")
            else:
                print("\n无效的选择，保持默认模型不变")
        else:
            # 直接使用输入的模型名称
            set_key(dotenv_path, "DEFAULT_MODEL", model_choice)
            print(f"\n默认模型已设置为: {model_choice}")
    else:
        print("\n保持默认模型不变")
    
    # 配置网站信息（可选）
    print("\n---- 网站信息配置（可选）----")
    print("OpenRouter使用这些信息进行统计，您可以选择设置或跳过")
    
    current_site_url = os.getenv("SITE_URL", "")
    current_site_name = os.getenv("SITE_NAME", "")
    
    if current_site_url:
        print(f"当前网站URL: {current_site_url}")
    if current_site_name:
        print(f"当前网站名称: {current_site_name}")
    
    print("\n要更新网站URL，请输入新值（或直接按回车键保持不变）")
    site_url = input("> ").strip()
    if site_url:
        set_key(dotenv_path, "SITE_URL", site_url)
        print("网站URL已更新")
    
    print("\n要更新网站名称，请输入新值（或直接按回车键保持不变）")
    site_name = input("> ").strip()
    if site_name:
        set_key(dotenv_path, "SITE_NAME", site_name)
        print("网站名称已更新")
    
    # 完成配置
    print("\n===== OpenRouter API配置完成 =====")
    print(f"API端点: {OPENROUTER_API_URL}")
    
    # 显示配置后的默认模型
    current_model = get_model()
    print(f"当前使用的默认模型: {current_model}")
    print("要测试API连接，请运行: python test_openrouter_api.py")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 