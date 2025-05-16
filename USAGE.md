# 考研英语真题文档处理工具使用指南

本指南将帮助您快速上手使用考研英语真题文档处理工具，从环境准备到数据处理和CSV生成，提供全面的说明。

## 1. 环境准备

### 1.1 安装依赖

首先，确保您已安装Python 3.8或更高版本，然后安装所需依赖：

```bash
# 克隆仓库（如果尚未克隆）
git clone https://github.com/ShengzheXu524/cvs.git
cd cvs

# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或者
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 1.2 配置API密钥

本工具使用OpenRouter API调用大型语言模型提取结构化数据，您需要配置API密钥：

1. 访问[OpenRouter官网](https://openrouter.ai/)注册账户
2. 在控制台获取API密钥
3. 在项目根目录创建`.env`文件
4. 添加以下内容：

```
OPENROUTER_API_KEY=your_api_key_here
DEFAULT_MODEL=google/gemini-2.5-flash-preview
```

或者使用配置工具进行设置：

```bash
python setup_openrouter.py
```

## 2. 处理单个文件

### 2.1 使用主程序处理文件

使用`main.py`处理单个文件：

```bash
python src/main.py 2024年考研英语(一)真题及参考答案_extracted.txt --output-dir test_results
```

参数说明：
- 第一个参数为输入文件路径
- `--output-dir`：指定输出目录（默认为test_results）
- `--model`：指定使用的模型（可选，默认使用环境变量中的模型）
- `--debug`：启用调试模式，保存中间结果
- `--no-csv`：不生成CSV文件，仅生成JSON结果

### 2.2 使用CSV生成工具

如果您已有提取好的JSON数据，可以使用`gen_csv.py`工具生成CSV：

```bash
python src/gen_csv.py --input 2024年考研英语(一)真题及参考答案_extracted.txt --output-dir test_results
```

参数说明：
- `--input`：输入文件路径
- `--output-dir`：输出目录
- `--model`：使用的模型名称（可选）
- `--debug`：保存调试信息

### 2.3 使用示例脚本

本项目还提供了便捷的示例脚本，直接处理2024年考研英语真题：

```bash
python process_2024_exam.py
```

这个脚本会自动处理`2024年考研英语(一)真题及参考答案_extracted.txt`文件，并将结果保存在`test_results/2024`目录。

## 3. 批量处理多个文件

### 3.1 使用批处理模式

使用`main.py`的批处理模式处理目录中的所有文件：

```bash
python src/main.py input_files --output-dir test_results --batch
```

### 3.2 使用CSV生成工具批处理

使用`gen_csv.py`批量处理多个文件：

```bash
python src/gen_csv.py --input input_files --batch --file-pattern "*.txt" --output-dir test_results
```

### 3.3 使用批处理脚本

使用专用的批处理脚本处理多个文件：

```bash
python batch_process_exams.py --input-dir input_files --output-dir test_results/batch
```

参数说明：
- `--input-dir`：输入文件目录
- `--output-dir`：输出目录
- `--file-pattern`：文件匹配模式（默认为"*.txt"）
- `--model`：使用的模型名称（可选）
- `--debug`：保存调试信息

## 4. 输出文件说明

处理完成后，会生成以下文件：

1. **JSON结构化数据**：包含完整的提取信息，保存在`<output_dir>/analysis/`目录
2. **CSV数据文件**：按照标准格式组织的数据，保存在输出目录，命名格式为`<年份><考试类型>.csv`
3. **调试信息**（如启用）：包括API原始响应等，保存在`<output_dir>/debug/`目录

CSV文件包含以下12列：
- **年份**：考试年份（如2024）
- **考试类型**：如"英语（一）"
- **题型**：如"完形填空"、"阅读理解 Text 1"等
- **原文（卷面）**：题型对应的原文内容
- **试卷答案**：标准答案
- **题目编号**：题目序号(1-52)
- **题干**：题目题干文本
- **选项**：选择题选项
- **正确答案**：各题目的正确答案
- **原文（还原后）**：将正确答案填入原文后的完整版本
- **原文（句子拆解后）**：原文按每个句子拆分标注的处理版本
- **干扰选项**：错误选项列表

## 5. 故障排除

### 5.1 API认证问题

如果遇到API认证问题：

1. 确认您的API密钥格式正确
2. 检查`.env`文件格式，确保没有多余空格或引号
3. 尝试重新生成API密钥
4. 确保您的网络环境可以访问OpenRouter API

### 5.2 处理错误

如果处理过程中出现错误：

1. 检查输入文件格式是否正确
2. 确认您的API密钥有足够的额度
3. 启用调试模式（添加`--debug`参数）获取更多信息
4. 检查日志输出，了解详细错误原因

### 5.3 超时问题

如果在处理大型文档时遇到超时错误：

1. 系统已经针对大型文档实现了自动分段处理
2. 对于超过3000字符的文档，会自动使用分段处理流程
3. 分段处理会将文档分为四个部分分别提取，然后合并结果

## 6. 高级用法

### 6.1 使用不同的模型

您可以通过以下方式指定使用不同的模型：

```bash
# 使用命令行参数指定
python src/main.py input.txt --model anthropic/claude-3-haiku

# 在.env文件中设置默认模型
DEFAULT_MODEL=anthropic/claude-3-haiku
```

支持的模型包括：
- `google/gemini-2.5-flash-preview`：Google最新模型
- `anthropic/claude-3-haiku`：Anthropic的Claude 3 Haiku模型（速度快）
- `mistralai/mistral-7b-instruct:free`：开源免费模型

### 6.2 通过Python API使用

您也可以在自己的Python脚本中使用数据处理器：

```python
from src.data_processor import DataProcessor

# 初始化数据处理器
processor = DataProcessor(model_name="google/gemini-2.5-flash-preview")

# 处理文档并生成CSV
success, csv_path, process_time = processor.process_document(
    document_path="文件路径.txt",
    output_dir="输出目录",
    save_debug=True  # 保存调试信息
)

# 检查处理结果
if success:
    print(f"成功生成CSV: {csv_path}，耗时: {process_time:.2f}秒")
else:
    print(f"处理失败，耗时: {process_time:.2f}秒")
```

## 7. 常见问题

### 问：API调用消耗多少额度/费用？

答：不同模型的调用费用不同。Google Gemini 2.5 Flash预览版每百万token约为0.125美元，Claude 3 Haiku约为0.25美元。每次处理考研真题文档大约需要3000-5000个tokens，可以参考模型提供商的价格计算具体费用。

### 问：如何验证提取的数据是否准确？

答：系统会自动检查提取的题目数量是否为52道，并为不完整的数据补充缺失结构。但具体内容准确性需要您手动检查。推荐使用`--debug`参数保存中间结果，以便进行验证。

### 问：处理大型文档需要多长时间？

答：处理时间取决于文档大小、选择的模型和网络环境。通常，使用Google Gemini 2.5 Flash处理一份考研真题约需15-30秒，Claude 3 Haiku可能需要30-60秒。

### 问：是否可以批量处理多年的考研真题？

答：是的，您可以使用批处理功能同时处理多年的考研真题。将所有文件放在同一目录下，然后使用批处理命令处理。 