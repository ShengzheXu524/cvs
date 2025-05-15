#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
模型配置模块，定义了可用的Claude API模型信息。
提供了一个集中管理模型名称的地方，方便在不同模型之间切换。
"""

# 可用的Claude模型配置
CLAUDE_MODELS = {
    # 默认模型（推荐，最快的模型，适合日常任务）
    "default": "claude-3-5-haiku-20241022",
    
    # 所有可用模型及其说明
    "models": {
        # 最新版本模型
        "claude-3-7-sonnet-20250219": {
            "description": "最新最智能的模型",
            "released": "2025-02-19",
            "tier": "sonnet",
            "generation": "3.7",
            "max_tokens": 200000  # 假设的最大token数
        },
        "claude-3-5-haiku-20241022": {
            "description": "最快速的模型，适合日常任务",
            "released": "2024-10-22",
            "tier": "haiku",
            "generation": "3.5",
            "max_tokens": 8192  # 根据错误信息得知的最大token数
        },
        "claude-3-opus-20240229": {
            "description": "擅长写作和复杂任务的模型",
            "released": "2024-02-29",
            "tier": "opus",
            "generation": "3",
            "max_tokens": 100000  # 假设的最大token数
        },
        "claude-3-5-sonnet-20241022": {
            "description": "3.5版本的sonnet模型",
            "released": "2024-10-22",
            "tier": "sonnet",
            "generation": "3.5",
            "max_tokens": 15000  # 假设的最大token数
        },
        "claude-3-5-sonnet-20240620": {
            "description": "3.5版本的sonnet模型较旧版本",
            "released": "2024-06-20",
            "tier": "sonnet",
            "generation": "3.5",
            "max_tokens": 15000  # 假设的最大token数
        },
        "claude-3-haiku-20240307": {
            "description": "早期haiku模型",
            "released": "2024-03-07",
            "tier": "haiku",
            "generation": "3",
            "max_tokens": 8192  # 假设的最大token数
        }
    },
    
    # 按性能/价格分类的模型
    "by_tier": {
        "fastest": "claude-3-5-haiku-20241022",
        "balanced": "claude-3-5-haiku-20241022",
        "most_capable": "claude-3-opus-20240229"
    }
}

def get_model(model_key=None):
    """
    获取指定模型名称，如果未指定则返回默认模型。
    
    Args:
        model_key (str, optional): 模型键名，可以是:
            - "default": 默认模型
            - "fastest": 最快的模型
            - "balanced": 平衡性能和速度的模型
            - "most_capable": 最强大的模型
            - 具体的模型名称: 如"claude-3-7-sonnet-20250219"
    
    Returns:
        str: 模型名称
    
    Examples:
        >>> get_model()  # 返回默认模型
        'claude-3-7-sonnet-20250219'
        >>> get_model("fastest")  # 返回最快的模型
        'claude-3-5-haiku-20241022'
        >>> get_model("claude-3-opus-20240229")  # 直接返回指定模型
        'claude-3-opus-20240229'
    """
    if not model_key:
        return CLAUDE_MODELS["default"]
    
    if model_key in CLAUDE_MODELS["by_tier"]:
        return CLAUDE_MODELS["by_tier"][model_key]
    
    if model_key in CLAUDE_MODELS["models"]:
        return model_key
    
    # 如果没有找到匹配的模型，返回默认模型
    return CLAUDE_MODELS["default"]

def get_model_max_tokens(model_name):
    """
    获取指定模型的最大输出token数。
    
    Args:
        model_name (str): 模型名称
        
    Returns:
        int: 模型的最大输出token数
    """
    if model_name in CLAUDE_MODELS["models"]:
        return CLAUDE_MODELS["models"][model_name].get("max_tokens", 8000)
    
    # 如果找不到模型信息，返回保守的默认值
    return 8000

def list_available_models():
    """
    列出所有可用模型及其描述。
    
    Returns:
        list: 包含模型信息的字典列表
    """
    result = []
    for model_name, info in CLAUDE_MODELS["models"].items():
        result.append({
            "name": model_name,
            "description": info["description"],
            "released": info["released"],
            "tier": info["tier"],
            "generation": info["generation"],
            "max_tokens": info.get("max_tokens", "未知")
        })
    return result

def get_model_info(model_name):
    """
    获取指定模型的详细信息。
    
    Args:
        model_name (str): 模型名称
    
    Returns:
        dict: 模型信息字典，如果未找到则返回None
    """
    if model_name in CLAUDE_MODELS["models"]:
        info = CLAUDE_MODELS["models"][model_name].copy()
        info["name"] = model_name
        return info
    return None 