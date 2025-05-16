#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
2024年考研英语(一)真题处理脚本
用于从文本文件提取结构化数据并生成CSV文件
"""

import os
import sys
import logging
import time
from pathlib import Path
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("process_2024_exam")

# 将当前目录添加到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入数据处理器
from src.data_processor import DataProcessor

def main():
    """主函数：处理2024年考研英语(一)真题文件"""
    
    # 指定输入文件和输出目录
    input_file = "2024年考研英语(一)真题及参考答案_extracted.txt"
    output_dir = "test_results/2024"
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    logger.info(f"开始处理2024年考研英语(一)真题...")
    logger.info(f"输入文件: {input_file}")
    logger.info(f"输出目录: {output_dir}")
    
    # 记录开始时间
    start_time = time.time()
    
    try:
        # 初始化数据处理器（可选择模型）
        # 使用环境变量中设置的默认模型，也可以通过参数指定：
        # processor = DataProcessor(model_name="google/gemini-2.5-flash-preview")
        processor = DataProcessor()
        
        # 处理文档并生成CSV
        logger.info("正在提取数据并生成CSV文件...")
        success, csv_path, process_time = processor.process_document(
            document_path=input_file,
            output_dir=output_dir,
            save_debug=True  # 保存调试信息
        )
        
        # 处理结果
        if success:
            logger.info(f"✅ 处理成功！")
            logger.info(f"📊 CSV文件已生成: {csv_path}")
            logger.info(f"⏱️ 处理耗时: {process_time:.2f}秒")
            
            # 计算单个部分的时间占比
            json_path = os.path.join(output_dir, "analysis", f"extraction_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
            if os.path.exists(json_path):
                logger.info(f"📄 结构化数据JSON文件: {json_path}")
        else:
            logger.error(f"❌ 处理失败，耗时: {process_time:.2f}秒")
            return 1
        
        # 总耗时
        total_time = time.time() - start_time
        logger.info(f"总耗时: {total_time:.2f}秒")
        
        return 0
    
    except Exception as e:
        logger.error(f"处理过程中出错: {str(e)}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main()) 