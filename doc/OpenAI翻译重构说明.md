# OpenAI翻译重构说明

## 概述

本次重构将原有的百度翻译API替换为OpenAI GPT-4o，专门针对AI图片生成提示词进行优化，提供更准确、更专业的翻译服务。

## 主要变化

### 1. 翻译引擎升级
- **原来**: 百度翻译API + 本地词典备用
- **现在**: OpenAI GPT-4o + 专业AI图片生成提示词优化

### 2. 翻译触发机制优化
- **失去焦点触发**: 当输入框失去焦点时，立即触发翻译
- **延迟触发**: 用户停止输入2.5秒后自动触发翻译
- **智能检测**: 自动检测中文/英文输入，采用不同的处理策略

### 3. 标签显示格式统一
- **格式**: 始终显示为 `英文(中文)` 的格式
- **示例**: `beautiful girl(美丽女孩)`、`masterpiece(杰作)`
- **兼容**: 如果没有中文翻译，仅显示英文部分

### 4. 翻译提示词专业化
针对AI图片生成场景，设计了专门的翻译提示词：

#### 中文→英文翻译提示词
```
你是一个专业的AI图片生成提示词翻译专家。请将用户输入的中文描述翻译成标准的英文AI图片生成提示词。

翻译要求：
1. 保持AI图片生成的专业术语准确性（如：masterpiece, ultra detailed, high quality等）
2. 使用逗号分隔的标签格式，不要使用句子形式
3. 优先使用AI绘画社区通用的英文关键词
4. 保持原意的同时，让提示词更适合AI图片生成
5. 如果是技术类术语，保持原英文不变（如：4K, UHD, realistic等）
```

#### 英文→中文翻译提示词
```
你是一个专业的AI图片生成提示词翻译专家。请将英文AI图片生成提示词翻译成简洁准确的中文。

翻译要求：
1. 保持简洁，使用最常见的中文词汇
2. 专业术语翻译要准确（masterpiece→杰作，best quality→最高质量等）
3. 保持标签的简洁性，避免冗长描述
4. 如果是专有名词或技术术语，可保持英文
5. 用逗号分隔，保持标签格式
```

## 使用方法

### 1. 中文输入
```
用户输入: 杰作，最高质量，美丽的女孩，长发，微笑
翻译结果: masterpiece, best quality, beautiful girl, long hair, smile
标签显示: masterpiece(杰作), best quality(最高质量), beautiful girl(美丽女孩), long hair(长发), smile(微笑)
```

### 2. 英文输入
```
用户输入: masterpiece, best quality, beautiful girl, long hair, smile
自动翻译: 杰作，最高质量，美丽女孩，长发，微笑
标签显示: masterpiece(杰作), best quality(最高质量), beautiful girl(美丽女孩), long hair(长发), smile(微笑)
```

### 3. 触发方式
- **实时触发**: 输入框失去焦点时立即翻译
- **延迟触发**: 停止输入2.5秒后自动翻译
- **手动触发**: 通过复制按钮获取最新的英文提示词

## 技术细节

### 1. 翻译器类重构
- `BaiduTranslator` → `OpenAITranslator`
- 保持向后兼容性，`BaiduTranslator`作为别名仍可使用
- 新增`smart_translate()`方法，自动检测语言并翻译

### 2. 批量翻译优化
- 使用特殊分隔符`|SEPARATOR|`批量处理多个提示词
- 提高翻译效率，减少API调用次数
- 失败时自动降级为逐个翻译

### 3. 失去焦点事件处理
```python
def on_focus_out_event(self, event):
    """输入框失去焦点时的处理"""
    current_input = self.english_edit.toPlainText().strip()
    if current_input and self._contains_chinese(current_input):
        if self.translation_timer.isActive():
            self.translation_timer.stop()
            self.auto_translate()
```

### 4. 标签格式确保
```python
# 显示文本处理 - 固定格式：英文(中文)
if self.english_text:
    if self.chinese_text:
        display_text = f"{self.english_text}({self.chinese_text})"
    else:
        display_text = self.english_text
```

## 配置要求

### 1. API密钥配置
```python
# 方式1: 环境变量
export OPENAI_API_KEY="你的API密钥"

# 方式2: 代码中配置（已内置默认密钥）
translator = OpenAITranslator(api_key="你的API密钥")
```

### 2. 模型配置
- 默认模型: `gpt-4o-mini`（速度快，成本低）
- 可选模型: `gpt-4o`（质量更高，成本稍高）
- 基础URL: `https://api.ssopen.top/v1`（中转站）

## 优势对比

### 翻译质量
- ✅ **专业术语准确性**: 针对AI绘画领域优化
- ✅ **上下文理解**: GPT-4o具有更强的语言理解能力
- ✅ **格式一致性**: 严格按照标签格式输出

### 用户体验
- ✅ **触发方式多样**: 失去焦点 + 延迟触发
- ✅ **实时反馈**: 显示翻译状态和进度
- ✅ **标签统一**: 英文(中文)格式，信息更丰富

### 技术特性
- ✅ **批量处理**: 提高翻译效率
- ✅ **错误处理**: 完善的异常处理和降级方案
- ✅ **向后兼容**: 保持原有接口不变

## 注意事项

1. **网络依赖**: 需要稳定的网络连接访问OpenAI API
2. **API限制**: 受OpenAI API的速率限制影响
3. **成本考虑**: 根据使用量产生相应的API费用
4. **语言检测**: 基于Unicode范围检测中文，可能对混合语言处理有限

## 后续优化方向

1. **缓存机制**: 为常用提示词添加本地缓存
2. **离线模式**: 提供基本的离线翻译能力
3. **用户自定义**: 允许用户自定义翻译提示词
4. **多语言支持**: 扩展支持日语、韩语等其他语言 