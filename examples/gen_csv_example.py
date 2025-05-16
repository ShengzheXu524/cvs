#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
示例脚本，展示如何使用数据处理器生成CSV
"""

import os
import sys
import logging
from datetime import datetime

# 添加父目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入数据处理器
from src.data_processor import DataProcessor

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("gen_csv_example")

def main():
    """主函数"""
    # 示例文件路径（用户需要替换为自己的文件路径）
    document_path = "2024年考研英语(一)真题及参考答案_extracted.txt"
    
    # 输出目录
    output_dir = "test_results"
    
    # 可选：指定模型名称
    # model_name = "google/gemini-2.5-flash-preview"  # 或 None 使用默认模型
    model_name = None
    
    logger.info(f"示例脚本启动，处理文件: {document_path}")
    
    # 初始化数据处理器
    processor = DataProcessor(model_name=model_name)
    
    # 处理文档并生成CSV
    logger.info("开始处理文档...")
    success, csv_path, process_time = processor.process_document(
        document_path=document_path,
        output_dir=output_dir,
        save_debug=True  # 保存调试信息
    )
    
    # 输出结果
    if success:
        logger.info(f"处理成功！")
        logger.info(f"CSV文件路径: {csv_path}")
        logger.info(f"处理耗时: {process_time:.2f}秒")
    else:
        logger.error(f"处理失败，耗时: {process_time:.2f}秒")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main()) 