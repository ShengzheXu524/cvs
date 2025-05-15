#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
修复 anthropic 库版本兼容性问题
"""

import os
import sys
import logging
import subprocess
from dotenv import load_dotenv

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("fix_anthropic")

def check_anthropic_version():
    """检查当前 anthropic 库版本"""
    try:
        import anthropic
        current_version = anthropic.__version__
        logger.info(f"当前 anthropic 库版本: {current_version}")
        
        # 解析版本号
        major, minor, patch = map(int, current_version.split('.'))
        
        if major == 0 and minor < 50:
            logger.warning(f"检测到旧版本 anthropic 库 ({current_version})，需要更新")
            return current_version, True
        else:
            logger.info(f"anthropic 库版本正常 ({current_version})")
            return current_version, False
    except ImportError:
        logger.error("未安装 anthropic 库")
        return None, True
    except Exception as e:
        logger.exception(f"检查版本时出错: {str(e)}")
        return None, True

def update_anthropic_library():
    """更新 anthropic 库到最新版本"""
    try:
        logger.info("正在更新 anthropic 库...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "anthropic==0.51.0"])
        logger.info("anthropic 库更新成功!")
        return True
    except Exception as e:
        logger.exception(f"更新 anthropic 库时出错: {str(e)}")
        return False

def update_requirements_file():
    """更新 requirements.txt 文件中的 anthropic 版本"""
    requirements_file = "requirements.txt"
    
    if not os.path.exists(requirements_file):
        logger.warning(f"未找到 {requirements_file}")
        return False
    
    try:
        with open(requirements_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        new_lines = []
        updated = False
        
        for line in lines:
            if line.strip().startswith("anthropic=="):
                new_lines.append("anthropic==0.51.0\n")
                updated = True
            else:
                new_lines.append(line)
        
        if updated:
            with open(requirements_file, "w", encoding="utf-8") as f:
                f.writelines(new_lines)
            logger.info(f"已更新 {requirements_file} 中的 anthropic 版本")
        else:
            logger.warning(f"在 {requirements_file} 中未找到 anthropic 库")
        
        return updated
    except Exception as e:
        logger.exception(f"更新 requirements.txt 时出错: {str(e)}")
        return False

def update_claude_api_module():
    """更新 src/claude_api.py 文件，修复初始化问题"""
    claude_api_file = "src/claude_api.py"
    
    if not os.path.exists(claude_api_file):
        logger.warning(f"未找到 {claude_api_file}")
        return False
    
    try:
        with open(claude_api_file, "r", encoding="utf-8") as f:
            content = f.read()
        
        # 查找并替换初始化代码
        if "self.client = Anthropic(api_key=self.api_key" in content:
            # 已经是简化的初始化方式，不需要修改
            logger.info(f"{claude_api_file} 中的初始化代码已经是最新格式")
            return True
        
        # 查找可能存在proxies参数的初始化代码段
        if "proxies=" in content or "client = Anthropic" in content:
            # 替换为简化的初始化方式
            new_content = content.replace(
                "self.client = Anthropic(",
                "# 使用简化的初始化方式，避免版本兼容问题\n        # 只使用api_key参数，不使用任何其他可能导致兼容性问题的参数\n        self.client = Anthropic("
            )
            
            # 移除proxies参数和其他可能导致问题的参数
            import re
            pattern = r"self\.client\s*=\s*Anthropic\([^)]*\)"
            match = re.search(pattern, new_content)
            
            if match:
                old_init = match.group(0)
                new_init = "self.client = Anthropic(api_key=self.api_key)"
                new_content = new_content.replace(old_init, new_init)
                
                with open(claude_api_file, "w", encoding="utf-8") as f:
                    f.write(new_content)
                
                logger.info(f"已更新 {claude_api_file} 中的初始化代码")
                return True
            else:
                logger.warning(f"在 {claude_api_file} 中未找到初始化代码段")
                return False
        else:
            logger.info(f"{claude_api_file} 中未发现需要修改的初始化代码")
            return True
    
    except Exception as e:
        logger.exception(f"更新 {claude_api_file} 时出错: {str(e)}")
        return False

def test_anthropic_client():
    """测试 Anthropic 客户端是否可以正常初始化"""
    try:
        # 加载环境变量
        load_dotenv()
        
        # 获取API密钥
        api_key = os.getenv("CLAUDE_API_KEY")
        if not api_key:
            logger.warning("未找到CLAUDE_API_KEY环境变量，无法进行测试")
            return False
        
        # 尝试导入库并创建客户端
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        logger.info("Anthropic 客户端初始化成功!")
        
        return True
    except Exception as e:
        logger.exception(f"测试 Anthropic 客户端时出错: {str(e)}")
        return False

def main():
    """主函数"""
    logger.info("开始修复 anthropic 库版本兼容性问题")
    
    # 检查当前版本
    current_version, need_update = check_anthropic_version()
    
    if need_update:
        # 更新库
        if not update_anthropic_library():
            logger.error("更新 anthropic 库失败，请手动运行: pip install --upgrade anthropic==0.51.0")
            return 1
    
    # 更新 requirements.txt
    update_requirements_file()
    
    # 更新 claude_api.py
    update_claude_api_module()
    
    # 创建.env文件（如果不存在）
    env_file = ".env"
    if not os.path.exists(env_file):
        try:
            with open(env_file, "w", encoding="utf-8") as f:
                f.write("# Claude API配置\nCLAUDE_API_KEY=your_claude_api_key_here\n\n" +
                       "# 注意：替换上面的 your_claude_api_key_here 为你的真实Claude API密钥\n" +
                       "# 请勿将此文件提交到版本控制系统")
            logger.info(f"已创建 {env_file} 文件，请编辑并添加你的API密钥")
        except Exception as e:
            logger.warning(f"创建 {env_file} 文件时出错: {str(e)}")
    
    # 测试客户端初始化
    if test_anthropic_client():
        logger.info("修复完成! Anthropic 客户端可以正常初始化")
    else:
        logger.warning("修复后的 Anthropic 客户端初始化测试失败，请检查 API 密钥和网络连接")
    
    logger.info("建议运行: python examples/test_cloze_no_repeat.py 来测试完形填空原文不重复功能")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 