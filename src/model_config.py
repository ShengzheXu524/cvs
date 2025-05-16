#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
模型配置模块，定义了可用的OpenRouter API模型信息。
提供了一个集中管理模型名称的地方，方便在不同模型之间切换。
"""

import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 可用的OpenRouter模型配置
OPENROUTER_MODELS = {
    # 默认模型（从环境变量获取，不再硬编码）
    "default": os.getenv("DEFAULT_MODEL", ""),
    
    # 免费模型列表（带有:free后缀的模型每天有免费限额）
    "free": [
        "mistralai/mistral-7b-instruct:free",
        # 以下模型在当前OpenRouter账户下不可用
        # "deepseek/deepseek-r1:free",
        # "nvidia/llama-3.1-nemotron-nano-8b-v1:free",
        # "google/gemma-7b-it:free",
        # "meta-llama/llama-3-8b-instruct:free"
    ],
    
    # 所有可用模型及其说明
    "models": {
        # 免费模型
        "mistralai/mistral-7b-instruct:free": {
            "description": "Mistral 7B指令模型免费版",
            "type": "free",
            "max_tokens": 4096
        },
        # Google模型
        "google/gemini-2.5-flash-preview": {
            "description": "Google Gemini 2.5 Flash预览版",
            "type": "paid",
            "max_tokens": 4096
        },
        # 以下模型在当前账户不可用
        "deepseek/deepseek-r1:free": {
            "description": "DeepSeek R1免费版，中英文表现优秀",
            "type": "free",
            "max_tokens": 4096
        },
        "nvidia/llama-3.1-nemotron-nano-8b-v1:free": {
            "description": "英伟达基于Llama的免费模型",
            "type": "free",
            "max_tokens": 4096
        },
        "google/gemma-7b-it:free": {
            "description": "谷歌Gemma 7B指令模型免费版",
            "type": "free",
            "max_tokens": 4096
        },
        "meta-llama/llama-3-8b-instruct:free": {
            "description": "Meta Llama 3 8B指令模型免费版",
            "type": "free",
            "max_tokens": 4096
        },
        
        # 付费高质量模型
        "openai/gpt-4o": {
            "description": "OpenAI GPT-4o模型，性能强大",
            "type": "paid",
            "max_tokens": 8192
        },
        "anthropic/claude-3-5-sonnet": {
            "description": "Anthropic Claude 3.5 Sonnet模型",
            "type": "paid",
            "max_tokens": 15000
        },
        "anthropic/claude-3-haiku": {
            "description": "Anthropic Claude 3 Haiku模型，速度快",
            "type": "paid",
            "max_tokens": 8192
        }
    },
    
    # 按性能/价格分类的模型
    "by_tier": {
        "fastest": "mistralai/mistral-7b-instruct:free",
        "balanced": "google/gemini-2.5-flash-preview",
        "most_capable": "openai/gpt-4o"
    }
}

def get_model(model_key=None):
    """
    获取指定模型名称，如果未指定则返回默认模型。
    
    Args:
        model_key (str, optional): 模型键名或完整模型ID，可以是:
            - "default": 默认模型
            - "fastest": 最快的模型
            - "balanced": 平衡性能和速度的模型
            - "most_capable": 最强大的模型
            - 具体的模型名称: 如"openai/gpt-4o"或"anthropic/claude-3-haiku"
            - None: 返回默认模型
    
    Returns:
        str: 模型名称
    
    Examples:
        >>> get_model()  # 返回默认模型
        'google/gemini-2.5-flash-preview'
        >>> get_model("fastest")  # 返回最快的模型
        'mistralai/mistral-7b-instruct:free'
        >>> get_model("openai/gpt-4o")  # 直接返回指定模型
        'openai/gpt-4o'
    """
    if not model_key:
        # 从环境变量获取默认模型
        env_default = os.getenv("DEFAULT_MODEL")
        
        # 如果环境变量中设置了默认模型，返回它
        if env_default:
            return env_default
        
        # 如果环境变量中没有设置，但配置中有默认值
        if OPENROUTER_MODELS["default"]:
            return OPENROUTER_MODELS["default"]
        
        # 如果两者都没有，返回一个安全的免费模型
        return "mistralai/mistral-7b-instruct:free"
    
    # 检查是否为预定义类别
    if model_key in OPENROUTER_MODELS["by_tier"]:
        return OPENROUTER_MODELS["by_tier"][model_key]
    
    # 检查是否为已知模型
    if model_key in OPENROUTER_MODELS["models"]:
        return model_key
    
    # 如果是未配置的模型ID，直接返回
    # OpenRouter支持直接使用模型ID，即使没有在配置中预定义
    if "/" in model_key:
        return model_key
    
    # 如果没有找到匹配的模型，返回默认模型
    return get_model(None)

def get_model_max_tokens(model_name):
    """
    获取指定模型的最大输出token数。
    
    Args:
        model_name (str): 模型名称
        
    Returns:
        int: 模型的最大输出token数
    """
    # 如果模型已配置，返回配置的值
    if model_name in OPENROUTER_MODELS["models"]:
        return OPENROUTER_MODELS["models"][model_name].get("max_tokens", 4096)
    
    # 对未配置的模型返回默认值
    # 根据模型ID推测合理的token限制
    if "gpt-4" in model_name:
        return 8192
    elif "claude-3-opus" in model_name:
        return 25000
    elif "claude-3-sonnet" in model_name:
        return 15000
    elif "claude-3-haiku" in model_name:
        return 8192
    elif "gemini-pro" in model_name or "gemini-flash" in model_name or "gemini-2.5" in model_name:
        return 8192
    elif "claude-instant" in model_name:
        return 5000
    elif "gpt-3.5" in model_name:
        return 4096
    
    # 保守的默认值
    return 4096

def list_available_models():
    """
    列出所有可用模型及其描述。
    
    Returns:
        list: 包含模型信息的字典列表
    """
    result = []
    for model_name, info in OPENROUTER_MODELS["models"].items():
        result.append({
            "name": model_name,
            "description": info["description"],
            "type": info["type"],
            "max_tokens": info.get("max_tokens", "未知")
        })
    return result

def get_free_models():
    """
    获取所有免费模型列表。
    
    Returns:
        list: 免费模型名称列表
    """
    return OPENROUTER_MODELS["free"]

def get_model_info(model_name):
    """
    获取指定模型的详细信息。
    
    Args:
        model_name (str): 模型名称
    
    Returns:
        dict: 模型信息字典，如果未找到则返回None
    """
    if model_name in OPENROUTER_MODELS["models"]:
        info = OPENROUTER_MODELS["models"][model_name].copy()
        info["name"] = model_name
        return info
    return None 