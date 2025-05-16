#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
快速设置脚本
自动处理环境变量设置、依赖安装和初始测试
"""

import os
import sys
import time
import shutil
import logging
import platform
import subprocess
from pathlib import Path

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("quick_setup")

def check_python_version():
    """检查Python版本是否满足要求"""
    logger.info("检查Python版本...")
    version = tuple(map(int, platform.python_version_tuple()))
    
    if version < (3, 7, 0):
        logger.error(f"Python版本过低: {platform.python_version()}")
        logger.error("请升级到Python 3.7或更高版本")
        return False
    
    logger.info(f"Python版本: {platform.python_version()} (OK)")
    return True

def check_pip():
    """检查pip是否可用"""
    logger.info("检查pip是否可用...")
    
    try:
        subprocess.run([sys.executable, "-m", "pip", "--version"], 
                      stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                      check=True, universal_newlines=True)
        logger.info("pip可用 (OK)")
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        logger.error("pip不可用。请安装pip后再运行此脚本。")
        return False

def install_requirements():
    """安装项目依赖"""
    logger.info("安装项目依赖...")
    
    # 获取项目根目录
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    requirements_file = os.path.join(root_dir, "requirements.txt")
    
    if not os.path.isfile(requirements_file):
        logger.error(f"未找到依赖文件: {requirements_file}")
        return False
    
    try:
        logger.info("开始安装依赖...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", requirements_file], 
                      check=True, universal_newlines=True)
        logger.info("依赖安装完成 (OK)")
        return True
    except subprocess.SubprocessError as e:
        logger.error(f"安装依赖时出错: {str(e)}")
        return False

def setup_env_file():
    """设置环境变量文件"""
    logger.info("设置环境变量文件...")
    
    # 获取项目根目录
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env_file = os.path.join(root_dir, ".env")
    env_example = os.path.join(root_dir, ".env.example")
    
    # 如果存在.env文件，备份它
    if os.path.isfile(env_file):
        backup_file = f"{env_file}.bak.{int(time.time())}"
        logger.info(f"已存在.env文件，备份到 {backup_file}")
        shutil.copy2(env_file, backup_file)
    
    # 如果存在.env.example文件，复制它
    if os.path.isfile(env_example):
        logger.info("使用.env.example作为模板")
        shutil.copy2(env_example, env_file)
    else:
        # 创建新的.env文件
        logger.info("创建新的.env文件")
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write("""# OpenRouter API配置
OPENROUTER_API_KEY=sk-or-xxxxxxxxxxxxxxxxxxx

# 默认使用的模型
DEFAULT_MODEL=mistralai/mistral-7b-instruct:free

# 网站信息（可选，用于OpenRouter统计）
SITE_URL=
SITE_NAME=

# 数据隐私设置（对某些模型可能必需）
ALLOW_TRAINING=true
ALLOW_LOGGING=true
""")
    
    logger.info(f".env文件已设置在 {env_file}")
    return True

def setup_openrouter_api_key():
    """设置OpenRouter API密钥"""
    logger.info("设置OpenRouter API密钥...")
    
    # 获取项目根目录
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env_file = os.path.join(root_dir, ".env")
    
    if not os.path.isfile(env_file):
        logger.error(f"未找到.env文件: {env_file}")
        return False
    
    # 读取现有内容
    with open(env_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 询问API密钥
    print("\n请输入您的OpenRouter API密钥（通常以sk-or-开头）")
    print("如果您还没有API密钥，请访问 https://openrouter.ai/ 注册并创建一个")
    api_key = input("> ").strip()
    
    if not api_key:
        logger.warning("未输入API密钥，将使用默认值（无效）")
        return False
    
    if not api_key.startswith("sk-or-"):
        print("\n警告: 您输入的API密钥似乎不是OpenRouter密钥 (应以sk-or-开头)")
        confirm = input("您确定要继续使用这个密钥吗? (y/n) > ").strip().lower()
        if confirm != 'y':
            logger.info("已取消设置API密钥")
            return False
    
    # 更新API密钥
    if "OPENROUTER_API_KEY=" in content:
        # 替换现有的API密钥
        import re
        new_content = re.sub(
            r'OPENROUTER_API_KEY=.*', 
            f'OPENROUTER_API_KEY={api_key}', 
            content
        )
    else:
        # 添加新的API密钥
        new_content = content + f"\nOPENROUTER_API_KEY={api_key}\n"
    
    # 写入更新后的内容
    with open(env_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    logger.info("API密钥已更新")
    return True

def run_test():
    """运行简单测试以验证设置"""
    logger.info("运行简单测试...")
    
    try:
        # 导入必要的模块
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from dotenv import load_dotenv
        load_dotenv()
        
        # 检查API密钥是否已设置
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key or api_key == "sk-or-xxxxxxxxxxxxxxxxxxx":
            logger.error("API密钥未设置或使用了默认值")
            return False
        
        # 测试API连接
        logger.info("测试API连接...")
        
        # 使用不导入OpenRouterAPI的方式测试，避免依赖问题
        import requests
        response = requests.get(
            "https://openrouter.ai/api/v1/models",
            headers={"Authorization": f"Bearer {api_key}"}
        )
        
        if response.status_code == 200:
            logger.info("API连接测试成功 (OK)")
            
            # 显示可用的免费模型
            data = response.json()
            free_models = []
            for model in data.get("data", []):
                pricing = model.get("pricing", {})
                if pricing.get("output", 0) == 0:  # 如果输出价格为0，认为是免费模型
                    free_models.append(model.get("id"))
            
            if free_models:
                logger.info(f"可用的免费模型: {', '.join(free_models)}")
            else:
                logger.info("未找到免费模型")
            
            return True
        else:
            logger.error(f"API连接测试失败，状态码: {response.status_code}")
            logger.error(f"错误详情: {response.text}")
            return False
    
    except Exception as e:
        logger.exception(f"测试时出错: {str(e)}")
        return False

def create_test_script():
    """创建简单的测试脚本"""
    logger.info("创建简单测试脚本...")
    
    # 获取项目根目录
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    test_dir = os.path.join(root_dir, "examples")
    test_file = os.path.join(test_dir, "simple_test.py")
    
    # 创建测试脚本
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write("""#!/usr/bin/env python3
# -*- coding: utf-8 -*-

\"\"\"
简单测试脚本
用于测试OpenRouter API的基本功能
\"\"\"

import os
import sys
import json
from dotenv import load_dotenv

# 添加父目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.openrouter_api import OpenRouterAPI

def main():
    \"\"\"主函数\"\"\"
    # 加载环境变量
    load_dotenv()
    
    # 创建OpenRouterAPI实例
    api = OpenRouterAPI()
    
    # 测试消息
    messages = [
        {"role": "user", "content": "你好，请简单介绍一下考研英语。"}
    ]
    
    # 发送请求
    print("发送测试请求...")
    response = api._make_api_request(
        messages=messages,
        max_tokens=100,
        temperature=0.7,
        routes_params={"allow_training": "true", "allow_logging": "true"}
    )
    
    # 处理响应
    if "error" in response:
        print(f"请求失败: {response['error']}")
        return 1
    
    # 提取响应内容
    content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
    
    # 打印响应
    print(f"\\n模型响应:\\n{content}")
    
    # 打印token使用情况
    usage = response.get("usage", {})
    print(f"\\n令牌使用情况:")
    print(f"- 输入令牌: {usage.get('prompt_tokens', 'N/A')}")
    print(f"- 输出令牌: {usage.get('completion_tokens', 'N/A')}")
    print(f"- 总令牌数: {usage.get('total_tokens', 'N/A')}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
""")
    
    # 设置执行权限
    try:
        os.chmod(test_file, 0o755)
    except:
        pass
    
    logger.info(f"测试脚本已创建: {test_file}")
    return test_file

def main():
    """主函数"""
    print("\n====== 考研英语真题处理工具 - 快速设置 ======\n")
    print("此脚本将帮助您完成以下设置：")
    print("1. 检查Python环境")
    print("2. 安装必要的依赖")
    print("3. 设置OpenRouter API密钥")
    print("4. 运行基本测试验证设置\n")
    
    # 询问是否继续
    continue_setup = input("是否继续? (y/n) > ").strip().lower()
    if continue_setup != 'y':
        print("设置已取消")
        return 1
    
    # 检查Python版本
    if not check_python_version():
        return 1
    
    # 检查pip
    if not check_pip():
        return 1
    
    # 设置环境变量文件
    if not setup_env_file():
        return 1
    
    # 安装依赖
    if not install_requirements():
        print("\n警告: 依赖安装失败，但将继续后续步骤")
    
    # 设置API密钥
    if not setup_openrouter_api_key():
        print("\n警告: API密钥设置失败或被跳过")
    
    # 运行测试
    if run_test():
        print("\n基本测试成功！")
    else:
        print("\n警告: 测试失败，可能需要手动检查配置")
    
    # 创建并提示如何使用测试脚本
    test_file = create_test_script()
    print(f"\n已创建简单测试脚本: {test_file}")
    print("可以运行以下命令测试API:")
    print(f"  python {test_file}")
    
    print("\n====== 设置完成 ======")
    print("下一步:")
    print("1. 使用以下命令测试OpenRouter账户和可用模型:")
    print("   python examples/openrouter_account.py --models")
    print("2. 测试处理简单的考研英语文本:")
    print("   python examples/test_mistral.py")
    print("3. 使用以下命令开始处理考研英语真题:")
    print("   python src/main.py --input <docx文件路径> --output <csv输出路径>")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 