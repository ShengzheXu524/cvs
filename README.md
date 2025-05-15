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

## 问题排查

### API认证问题检测工具
如果遇到API相关问题，可以运行以下工具进行检测：

```bash
# 检查API密钥格式和有效性
python examples/auth_test.py

# 详细检查API认证问题
python check_api_key.py
```

### anthropic库版本兼容性问题
如果遇到错误："Client.__init__() got an unexpected keyword argument 'proxies'"，这是由于anthropic库版本兼容性问题导致的。解决方法：

1. 运行修复脚本：
```bash
python fix_anthropic_error.py
```

2. 或者手动更新anthropic库：
```bash
pip install --upgrade anthropic==0.51.0
```

3. 修改src/claude_api.py文件中的客户端初始化代码，只使用api_key参数：
```python
self.client = Anthropic(api_key=self.api_key)
```

### 403权限错误
如果遇到403权限错误（"Error code: 403 - {'error': {'type': 'forbidden', 'message': 'Request not allowed'}}"），可能有以下原因：

1. **API密钥问题**：
   - API密钥无效或过期
   - API密钥格式不正确（Claude API密钥通常以'sk-'开头）
   - API密钥没有足够的权限或余额

2. **账户问题**：
   - 账户可能已被暂停
   - 账户没有访问特定模型的权限
   - 账户有计费问题

3. **环境问题**：
   - 网络连接问题
   - 代理配置问题
   - 请求头格式问题

解决方案：
1. 登录[Anthropic控制台](https://console.anthropic.com/)检查API密钥状态
2. 重新生成一个新的API密钥
3. 检查.env文件格式：
   ```
   CLAUDE_API_KEY=sk-your_real_api_key_here
   ```
4. 确保.env文件没有多余空格、引号或注释
5. 使用测试工具验证API密钥：`python examples/auth_test.py`
6. 检查网络环境，尝试使用不同的网络连接
7. 如果使用VPN，尝试关闭或更换服务器

### 超时问题解决
如果在处理大型文档时遇到超时错误（"Streaming is strongly recommended for operations that may take longer than 10 minutes"），这是因为普通的Claude API调用在处理较大的文档时可能会超过10分钟限制。解决方法：

1. **使用流式API**：
   - 项目已经在`src/claude_api.py`中实现了流式API调用
   - 流式API通过逐步返回结果，避免了长时间等待和超时问题

2. **运行直接测试**：
   如果想验证流式API是否正常工作，可以运行直接测试脚本：
   ```bash
   python examples/direct_test.py
   ```
   该脚本使用流式API处理文档，显示进度并保存中间结果

3. **手动修改API调用**：
   如果您正在编写自己的API调用代码，确保使用流式API：
   ```python
   # 替换普通API调用
   # response = client.messages.create(...)
   
   # 使用流式API调用
   with client.messages.stream(
       model="claude-3-7-sonnet-20240229",
       system=system_prompt,
       messages=[{"role": "user", "content": document_text}],
       max_tokens=30000,
       temperature=0.1,
   ) as stream:
       response_text = ""
       for text in stream.text_stream:
           response_text += text
           # 可选：打印进度
           if len(response_text) % 2000 == 0:
               print(f"已接收 {len(response_text)} 个字符")
   ```

4. **增加最大令牌数**：
   - 对于大型文档，可能需要增加max_tokens参数值
   - 项目中已设置为30000，这应该足够处理大多数考研英语真题文档

5. **分批处理**：
   - 如果文档非常大，考虑将文档分成多个部分分别处理
   - 使用批处理功能：`python src/main.py --input ./examples/ --output ./results/ --batch`

6. **增加重试机制**：
   - 项目已经内置了最多3次的重试机制
   - 可以根据需要在代码中调整`max_retries`和`retry_delay`参数

注意：即使使用流式API，处理大型文档也可能需要较长时间，请保持耐心。成功后会有提示信息，如"流式传输完成，共接收 X 个字符"。

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

### v1.4
- 修复原文字段处理问题，确保"原文（卷面）"包含整篇原文而非单个句子
- 更新Claude API调用模块的提示词，明确说明原文的定义
- 改进数据组织模块中的原文映射逻辑，支持根据题号自动映射题型
- 添加题型标准化处理，确保相同类型的题目共享相同的原文
- 添加测试脚本examples/test_full_original_text.py用于验证改进效果 

### v1.5
- 改进"试卷答案"字段处理，确保每道题的答案为单独的答案字母（如"A"、"B"等），而非整个板块的答案汇总
- 增强答案解析功能，支持各种格式的答案汇总字符串解析
- 添加_parse_individual_answer函数，用于从各种格式的答案中提取出单一的答案字母
- 优化API返回数据处理逻辑，当返回题目数量不足时自动创建和补全所有52道题目
- 强化Claude API提示词，明确要求返回包含所有52道题目的完整数据
- 添加测试脚本examples/test_answer_extraction.py用于验证答案解析和题目补全功能
- 实现数据完整性检查，确保CSV文件始终包含完整的52道题目数据 

### v1.6
- 优化Claude API提示词，明确指示完形填空和其他题型原文只在sections部分生成一次
- 针对完形填空题特别加强提示，确保原文不在questions部分的每道题中重复
- 重新定义JSON数据结构中原文字段的处理方式，使其更高效、更一致
- 增加详细的注意事项说明，明确原文在sections和questions部分的不同处理要求
- 改进原文引用机制，确保所有题目能正确关联到其对应题型的原文
- 解决完形填空题重复生成原文的问题，减少API响应的冗余，提高效率
- 使数据结构更加符合完形填空和阅读理解题型处理的一致性要求

### v1.7
- 解决anthropic库版本兼容性问题，修复"Client.__init__() got an unexpected keyword argument 'proxies'"错误
- 将anthropic库从0.19.1更新到0.51.0，提高API调用稳定性
- 修改claude_api.py中的客户端初始化代码，简化参数，避免兼容性问题
- 添加test_anthropic_version.py脚本检测库版本兼容性问题
- 创建fix_anthropic_error.py修复脚本，提供自动化解决方案
- 添加test_cloze_no_repeat.py测试脚本，验证完形填空原文不重复处理
- 更新direct_test.py脚本，使用流式API避免超时问题
- 改进README.md，添加问题排查部分和anthropic库版本兼容性问题解决方法
- 优化测试脚本，提高代码健壮性和API调用效率
- 启用流式API处理大型响应，避免超时问题

### v1.8
- 添加专门的API权限问题诊断工具check_api_key.py
- 添加examples/auth_test.py脚本用于快速验证API密钥格式和认证问题
- 解决403 Forbidden权限错误问题
- 扩展README中的问题排查部分，添加完整的API认证问题解决步骤
- 改进错误信息显示，提供更详细的API错误原因分析
- 增强API密钥检测功能，识别常见的密钥格式问题
- 添加直接HTTP请求测试方法，绕过anthropic库进行API测试
- 提供多种403错误排查方法和解决方案 
- 已经创建.env文件并输入api-key

### v1.9
- 强化流式API处理功能，解决大文档处理时的超时问题
- 优化src/claude_api.py中的extract_structured_data方法，使用流式API处理
- 增加max_tokens参数从4000到20000，确保能容纳更大文档的完整响应内容
- 添加流式响应进度显示，每2000个字符输出一次进度提示
- 改进examples/direct_test.py脚本，提供流式API调用的示例代码
- 在API调用过程中增加错误处理和重试机制，提高处理大型文档的稳定性
- 添加.env.example模板文件，提供API密钥配置的标准格式和使用说明
- 优化JSON解析逻辑，确保能正确提取更大响应中的JSON数据
- 更新文档，增加关于流式API处理的说明和最佳实践
- 添加"超时问题解决"章节，提供详细的解决方案和示例代码