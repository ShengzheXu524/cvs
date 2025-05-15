# 考研英语真题文档处理工具

> **助手指引**: 每次会话开始时，请先阅读此README了解项目当前状态，会话结束后请更新本文档，记录新增功能和变更，避免重复工作。更新时，请在文档末尾的"项目开发历史"章节添加新的条目，使用版本号（如v1.0、v1.1）标识，包括实现的功能和修改的内容。

这是一个用于处理考研英语真题docx文件的Python工具，能够通过调用Claude 3.7 API提取试题内容并生成标准化CSV文件。

## 项目仓库

GitHub: https://github.com/ShengzheXu524/cvs

## 功能介绍

本工具可以：
1. 读取考研英语真题的docx文件
2. 调用Claude 3.7 API进行内容分析和结构识别
3. 提取文档中的所有相关信息（题目、原文、答案等）
4. 按照规定格式组织数据并输出为CSV文件

## 输出CSV格式

生成的CSV文件包含以下12列：
1. **年份**：考试年份（如2024）
2. **考试类型**：如"英语（一）"
3. **题型**：如"完形填空"、"阅读 Text 1"等
4. **原文（卷面）**：该题对应题型板块的试卷上的原文内容，完型填空包含空格标记（如第1题对应的原文（卷面）应该是整篇完形挖空版文章）
5. **试卷答案**：试卷上的标准答案汇总
6. **题目编号**：题目序号(1-52)
7. **题干**：题目题干文本
8. **选项**：选择题选项
9. **正确答案**：各题目的正确答案
10. **原文（还原后）**：将正确答案填入原文后的完整版本
11. **原文（句子拆解后）**：原文按每个句子拆分标注的处理版本
12. **干扰选项**：错误选项列表

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
      "answers_summary": "完形填空答案汇总，如'1.D 2.C 3.B...'"
    },
    "reading": {
      "text_1": {
        "original_text": "阅读Text 1原文",
        "answers_summary": "阅读Text 1答案汇总，如'21.D 22.D 23.A...'"
      },
      // text_2, text_3, text_4...
    },
    // new_type, translation, writing...
  },
  "questions": [
    {
      "number": 1,
      "section_type": "完形填空",
      "stem": "题干（完形填空通常为空或'/'）",
      "options": "A. Without, B. Though, C. Despite, D. Besides",
      "correct_answer": "A. Without",
      "distractor_options": "B. Though, C. Despite, D. Besides"
    },
    // ... 其他题目，总共52个
  ]
}
```

## 目录结构
```
.
├── README.md                    # 项目说明文档
├── requirements.txt             # 项目依赖
├── src/                         # 源代码目录
│   ├── main.py                  # 主程序入口
│   ├── docx_reader.py           # 文档读取模块
│   ├── claude_api.py            # Claude API调用模块
│   ├── content_analyzer.py      # 内容分析模块
│   ├── data_organizer.py        # 数据组织模块
│   ├── csv_generator.py         # CSV生成模块
│   ├── sentence_splitter.py     # 句子拆分模块
│   ├── test_module.py           # 测试模块
│   └── utils.py                 # 工具函数
└── examples/                    # 示例文件
    ├── example_usage.py         # 示例使用脚本
    └── batch_process.py         # 批处理脚本
```

## 安装与配置

1. 克隆此仓库到本地
2. 安装所需依赖：
```bash
pip install -r requirements.txt
```
3. 设置Claude API密钥：
   - 创建一个`.env`文件
   - 添加你的API密钥：`CLAUDE_API_KEY=你的API密钥`

## 使用方法

### 基本用法
```bash
python src/main.py --input 考研英语真题.docx --output 结果.csv
```

### 参数说明
- `--input`：输入的docx文件路径，必填
- `--output`：输出的CSV文件路径，必填
- `--api_key`：Claude API密钥，可选，优先使用环境变量
- `--model`：要使用的Claude模型，默认为"claude-3-7-sonnet-20240229"
- `--batch`：是否进行批处理，如果指定目录，将处理所有docx文件
- `--log`：日志级别，可选值为debug、info、warning、error，默认为info
- `--debug`：启用调试模式，保存中间结果

## 示例
```bash
# 处理单个文件
python src/main.py --input ./examples/2023英语一.docx --output ./results/2023英语一.csv

# 批处理文件夹中的所有docx文件
python src/main.py --input ./examples/ --output ./results/ --batch
```

## 注意事项

1. 确保您的网络环境可以访问Claude API
2. docx文件格式应符合标准考研英语真题格式
3. API调用可能产生费用，请合理控制使用频率

## 问题解决

如遇问题，请检查：
1. API密钥是否配置正确
2. 网络连接是否正常
3. docx文件格式是否符合要求

## 项目维护计划
1. 定期更新支持新年份的试题格式
2. 持续优化Claude提示词以提高信息提取准确率
3. 添加更多数据验证和错误处理机制 

## 项目开发历史

### v1.0
- 创建项目基本结构
- 实现文档读取模块、API调用模块、内容分析模块、数据组织模块和CSV生成模块
- 添加句子拆分功能
- 创建基本的命令行界面

### v1.1
- 更新Claude API调用模块，支持新的结构化JSON格式
- 改进数据组织模块，优化新格式处理
- 添加测试脚本examples/test_new_format.py

### v1.2
- 修复anthropic库版本兼容问题
- 优化.cursorrules配置文件
- 添加README助手指引，便于项目状态追踪 

### v1.3
- 创建GitHub仓库并推送代码
- 完善.gitignore文件，确保敏感信息不被提交
- 更新README文档，添加仓库链接 