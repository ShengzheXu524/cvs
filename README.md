# 考研英语真题文档处理工具

> **助手指引**: 每次会话开始时，请先阅读此README了解项目当前状态，会话结束后请更新本文档，记录新增功能和变更，避免重复工作。更新时，请在文档末尾的"项目开发历史"章节添加新的条目，使用版本号（如v1.0、v1.1）标识，包括实现的功能和修改的内容。

这是一个使用大语言模型API自动提取和分析考研英语真题的工具。它可以从docx和txt格式的考研英语真题文档中提取结构化数据，生成标准CSV格式文件，便于后续分析和数据处理。

## 功能特点

- 自动分析考研英语真题文档，提取完整的题目结构和内容
- 支持直接处理Word文档(.docx)和文本文件(.txt)
- 支持从文件名自动提取年份，根据年份创建对应的输出目录
- 支持完形填空、阅读理解、新题型、翻译和写作等各类题型
- 可选择使用不同的大型语言模型进行分析
- 可配置的环境变量和参数设置
- 自动分段处理大型文档，解决token限制导致的不完整输出问题
- 智能文档长度检测，针对超过3000字符的文档自动使用分段处理方式
- 优化五段处理流程，分别提取不同部分内容，确保提取完整性

## 更新日志

### v3.0 (2025-05-21)
- 增强docx处理能力，支持直接处理Word文档
- 添加通用处理脚本，可处理任意年份的考研真题
- 优化批量处理功能，支持同时处理多种文件格式
- 自动从文件名提取年份，按年份组织输出目录
- 增强文本提取和预处理能力，优化对不同格式文档的支持
- 将五段处理优化，更好地支持完整提取所有题目

### v2.6 (2025-05-20)
- 添加数据处理器模块，整合文档处理和CSV生成流程
- 添加专用CSV生成命令行工具，支持单文件和批量处理
- 支持从提取的结构化数据直接生成标准格式CSV文件
- 添加示例脚本，展示如何使用数据处理器生成CSV
- 优化文件命名规则，自动根据元数据确定CSV文件名

### v2.5 (2025-05-20)
- 优化分段处理流程，采用四段处理方式
- 将原来的两段处理（1-25题和26-52题）扩展为四段处理：
  1. 提取基本信息和sections中的cloze和readings部分
  2. 提取sections中的剩余部分(new_type, translation, writing)
  3. 提取题目1-25
  4. 提取题目26-52
- 解决了sections部分内容过大导致上下文不足的问题
- 确保各部分内容的完整提取，提高了提取质量

### v2.4 (2025-05-18)
- 优化文档处理逻辑，添加智能文档长度检测功能
- 对超过3000字符的文档自动使用分段处理，提高处理效率
- 避免不必要的API调用尝试，节约API使用成本

### v2.3 (2025-05-16)
- 添加分段处理功能，解决token限制导致的不完整输出问题
- 现在可以完整提取所有52道考研英语题目，不会因为token限制而截断

### v2.2 (2025-05-15)
- 移除硬编码默认模型，统一使用环境变量中的DEFAULT_MODEL
- 优化模型配置管理，支持更多模型类型

### v2.1 (2025-05-12)
- 增加模型选择功能
- 支持使用不同的LLM模型处理同一文档
- 增加结果对比分析功能

### v2.0 (2025-05-10)
- 重构代码架构，采用模块化设计
- 使用OpenRouter API支持多种模型
- 增加JSON格式输出支持

### v1.0 (2025-05-01)
- 初始版本发布
- 基本文档处理功能

## 快速开始

### 环境准备

1. 克隆本仓库到本地：
```bash
git clone https://github.com/yourusername/cvs.git
cd cvs
```

2. 创建并激活虚拟环境：
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或者
venv\Scripts\activate  # Windows
```

3. 安装依赖：
```bash
pip install -r requirements.txt
```

4. 设置API密钥：
   - 在项目根目录创建`.env`文件
   - 添加以下内容：
```
OPENROUTER_API_KEY=your_api_key_here
DEFAULT_MODEL=google/gemini-2.5-flash-preview
```

### 使用方法

#### 处理单个文件

1. 使用通用处理脚本：
```bash
python process_exam.py 2023年考研英语真题.docx --debug
```

2. 手动指定年份：
```bash
python process_exam.py 考研英语真题.txt --year 2022
```

3. 指定模型和输出目录：
```bash
python process_exam.py 2024年考研英语(一)真题.docx --model anthropic/claude-3-5-sonnet --output-dir my_results/2024
```

#### 批量处理多个文件

```bash
python batch_process_exams.py --batch --input ./exams/ --pattern "*.docx;*.txt" --debug
```

#### 使用旧版命令行工具

```bash
python src/main.py input_file.txt --output-dir test_results
```

## CSV生成

本工具支持将提取的结构化数据转换为标准CSV格式，便于后续分析和使用：

### 命令行工具

1. 处理单个文件并生成CSV：
```bash
python src/gen_csv.py --input 文件路径.txt --output-dir 输出目录
```

2. 批量处理目录下的所有文件：
```bash
python src/gen_csv.py --input 数据目录 --batch --file-pattern "*.txt" --output-dir 输出目录
```

3. 指定模型并启用调试模式：
```bash
python src/gen_csv.py --input 文件路径.txt --model google/gemini-2.5-flash-preview --debug
```

### 通过Python API使用

您也可以在自己的Python脚本中使用数据处理器：

```python
from src.data_processor import DataProcessor

# 初始化数据处理器
processor = DataProcessor(model_name="google/gemini-2.5-flash-preview")

# 处理文档并生成CSV
success, csv_path, process_time = processor.process_document(
    document_path="文件路径.txt",  # 或 .docx 文件
    output_dir="输出目录",
    save_debug=True  # 保存调试信息
)

# 检查处理结果
if success:
    print(f"成功生成CSV: {csv_path}，耗时: {process_time:.2f}秒")
else:
    print(f"处理失败，耗时: {process_time:.2f}秒")
```

有关更多示例，请参考`examples/gen_csv_example.py`。

## 解决Token限制问题

当处理大型文档时，一些模型可能会因为token限制而无法完整输出所有52道考研英语题目。本工具实现了智能分段处理：

1. 首先检测文档长度，超过3000字符自动使用分段处理
2. 使用五段处理流程，确保信息完整提取：
   - 第一段：提取基本信息(metadata)和sections中的cloze和readings部分
   - 第二段：提取sections中的剩余部分(new_type, translation, writing)
   - 第三段：提取题目1-25的详细信息
   - 第四段：提取题目26-40的详细信息
   - 第五段：提取题目41-52的详细信息
3. 自动合并五部分结果，生成完整数据

这种五段处理方法解决了单一大型请求可能导致的token限制问题，同时也解决了两段处理中sections部分内容过大导致的上下文不足问题，确保提取的内容完整且准确。

## 项目结构

```
cvs/
├── .env                    # 环境变量配置文件
├── README.md               # 说明文档
├── requirements.txt        # 依赖包列表
├── setup_openrouter.py     # OpenRouter API设置工具
├── process_exam.py         # 通用处理脚本
├── batch_process_exams.py  # 批量处理脚本
├── src/                    # 源代码目录
│   ├── __init__.py
│   ├── content_analyzer.py   # 内容分析器
│   ├── main.py               # 主程序
│   ├── model_config.py       # 模型配置
│   ├── openrouter_handler.py # OpenRouter API处理器
│   ├── docx_reader.py        # Word文档读取器
│   ├── data_processor.py     # 数据处理器
│   ├── csv_generator.py      # CSV生成器
│   └── ...
├── examples/               # 示例代码
└── test_results/           # 测试结果目录
    ├── 2024/               # 按年份组织的子目录
    │   ├── analysis/       # 分析结果
    │   └── debug/          # 调试信息
    └── ...
```

## 文件格式支持

本工具支持以下格式的考研英语真题文档：

1. **Word文档 (.docx)**
   - 直接处理Word文档，自动提取文本内容
   - 自动识别文档中的题型部分和答案部分
   - 支持从文件名中提取年份信息

2. **文本文件 (.txt)**
   - 处理纯文本格式的考研英语真题
   - 支持各种常见编码（UTF-8, GBK等）

处理流程会根据文件类型自动选择合适的处理方式。对于Word文档，工具会智能尝试识别文档结构，提取题型部分并自动分段处理，确保完整提取所有题目信息。

## 依赖项

- Python 3.8+
- python-docx (处理Word文档)
- dotenv (环境变量处理)
- requests (API调用)
- tqdm (进度条显示)

## 开发计划

- [ ] 增加PDF文件支持
- [ ] 添加Web用户界面
- [ ] 提供更详细的结果分析
- [ ] 支持导出为更多格式

## 许可证

MIT

## 项目仓库

GitHub: https://github.com/ShengzheXu524/cvs

## 输出CSV格式

生成的CSV文件包含以下12列：
1. **年份**：考试年份（如2024）
2. **考试类型**：如"英语（一）"
3. **题型**：如"完形填空"、"阅读理解 Text 1"等
4. **原文（卷面）**：该题对应题型板块的试卷上的原文内容，完形填空包含空格标记（如第1题对应的原文（卷面）应该是整篇完形挖空版文章）
5. **试卷答案**：试卷上的标准答案汇总
6. **题目编号**：题目序号(1-52)
7. **题干**：题目题干文本
8. **选项**：选择题选项
9. **正确答案**：各题目的正确答案
10. **原文（还原后）**：将正确答案填入原文后的完整版本
11. **原文（句子拆解后）**：原文按每个句子拆分标注的处理版本
12. **干扰选项**：错误选项列表

## 重要说明

- **原文字段处理**: "原文"是指该题对应题型板块的试卷上的完整原文内容，不是单个题目的句子。例如，完形填空第1题的"原文（卷面）"应该是整篇完形填空文章（包含所有空格标记[1], [2]等），而不仅仅是该题所在的句子。相同题型的所有题目共享相同的原文。
- **题型映射**: 系统会根据题号自动映射标准题型（如完形填空、阅读理解 Text 1~4、新题型、翻译、写作A/B），确保原文正确对应到题目。
- **自动提取**: 工具会自动从文件名提取年份信息，按年份创建对应的输出目录，方便管理不同年份的数据。
- **自动识别格式**: 工具能够自动识别输入文件格式（docx或txt），并采用相应的处理方式。

## API 数据结构

工具调用 Claude API 时使用优化的提示词格式，获取的结构化数据包含以下主要部分：

```json
{
  "metadata": {
    "year": "年份，如2024",
    "exam_type": "考试类型，如'英语（一）'"
  },
  "sections": {
    "cloze": {
      "original_text": "完形填空原文（卷面版本，包含[1], [2]等标记）",
      "restored_text": "完形填空原文（还原后版本，已将答案填入）",
      "answers_summary": "答案汇总"
    },
    "reading": {
      "text_1": {
        "original_text": "阅读1原文",
        "answers_summary": "答案汇总"
      },
      // text_2, text_3, text_4...
    },
    "new_questions": {
      "original_text": "新题型原文",
      "restored_text": "新题型原文（还原后版本）",
      "answers_summary": "答案汇总"
    },
    "translation": {
      "original_text": "翻译原文",
      "answers_summary": "参考译文"
    },
    "writing": {
      "part_a": {
        "task": "写作任务A",
        "reference": "参考答案"
      },
      "part_b": {
        "task": "写作任务B",
        "reference": "参考答案"
      }
    }
  },
  "questions": [
    {
      "number": 1,
      "question_type": "完形填空",
      "stem": "", // 完形填空不需要stem
      "options": {
        "A": "选项A",
        "B": "选项B",
        "C": "选项C",
        "D": "选项D"
      },
      "correct_answer": "正确答案",
      "distractors": ["干扰项A", "干扰项B", "干扰项C"] // 除正确答案外的选项
    },
    // 题目2-52...
  ]
}
```

## 项目开发历史

见上方更新日志。