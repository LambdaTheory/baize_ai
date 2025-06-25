# ComfyUI集成功能说明

## 功能概述

本AI图片信息提取工具现已集成ComfyUI支持，可以实现**一键将图片中的工作流导入到本地ComfyUI**。这个功能特别适合：

- 🎯 **ComfyUI用户**：快速导入他人分享的工作流
- 🔄 **工作流复用**：从生成的图片中提取和重用工作流
- 📚 **学习研究**：分析他人的工作流构建方法
- 🚀 **效率提升**：无需手动重建复杂的工作流

## 核心特性

### ✨ 主要功能

1. **自动检测ComfyUI状态**
   - 实时检查本地ComfyUI是否运行
   - 显示连接状态和系统信息

2. **智能工作流提取**
   - 从PNG图片中提取嵌入的ComfyUI工作流
   - 支持多种工作流数据格式
   - 自动解析工作流JSON结构

3. **一键导入功能**
   - 直接调用ComfyUI API导入工作流
   - 自动上传相关图片文件
   - 实时显示导入进度和结果

4. **工作流转换**
   - 将Stable Diffusion WebUI参数转换为ComfyUI工作流
   - 生成基础的ComfyUI节点结构
   - 保持参数一致性

5. **用户友好界面**
   - 绿色的"🎯 导入ComfyUI"按钮
   - 详细的状态提示和错误信息
   - 连接失败时的解决方案提示

## 使用前准备

### 1. 启动ComfyUI

首先确保您的ComfyUI正在运行：

```bash
# 进入ComfyUI目录
cd /path/to/ComfyUI

# 启动ComfyUI（Windows）
python main.py

# 启动ComfyUI（Linux/Mac）
python3 main.py
```

### 2. 验证ComfyUI状态

启动后，ComfyUI默认运行在：
- **地址**：http://127.0.0.1:8188
- **WebUI**：可在浏览器中访问上述地址
- **API**：自动启用，无需额外配置

### 3. 准备测试图片

最佳测试图片类型：
- ✅ **ComfyUI生成的PNG图片**（包含完整工作流数据）
- ✅ **Stable Diffusion WebUI生成的PNG图片**（可转换为基础工作流）
- ⚠️ **其他AI工具生成的图片**（可能需要手动转换）

## 使用方法

### 📖 基本使用流程

1. **启动工具**
   ```bash
   python main.py
   ```

2. **选择图片**
   - 点击"选择文件"或拖拽图片到工具中
   - 工具会自动分析图片信息

3. **导入工作流**
   - 确保ComfyUI正在运行
   - 点击绿色的"🎯 导入ComfyUI"按钮
   - 等待处理完成

4. **查看结果**
   - 成功：会显示"工作流已成功导入ComfyUI"
   - 失败：会显示具体的错误原因和解决建议

### 🔧 高级功能

#### 自定义ComfyUI地址

如果您的ComfyUI运行在非默认地址，可以修改配置：

```python
# 在 core/comfyui_integration.py 中修改
comfyui_integration = ComfyUIIntegration(host="192.168.1.100", port=8188)
```

#### 批量处理

您可以连续选择多张图片进行工作流导入，每次点击按钮都会处理当前选中的图片。

## 支持的图片格式

### 🟢 完全支持

**ComfyUI原生PNG图片**
- 包含完整的工作流JSON数据
- 支持所有节点类型和连接
- 导入后可立即使用

**特征识别**：
- 图片metadata中包含`workflow`字段
- JSON数据包含ComfyUI节点结构
- 通常文件较大（因包含工作流数据）

### 🟡 基础支持

**Stable Diffusion WebUI PNG图片**
- 自动转换为基础ComfyUI工作流
- 支持基本参数：prompt、model、sampler等
- 适合简单的文生图工作流

**转换内容**：
- 正向和负向提示词
- 模型选择
- 采样器设置
- 基本参数（steps、CFG、seed等）

### 🔴 暂不支持

- 不包含生成信息的普通图片
- 其他AI工具的专有格式
- 加密或压缩的工作流数据

## 故障排除

### 常见问题及解决方案

#### 1. "无法连接到ComfyUI"

**可能原因**：
- ComfyUI未启动
- 端口被占用
- 防火墙阻止连接

**解决方案**：
```bash
# 检查ComfyUI是否运行
curl http://127.0.0.1:8188/system_stats

# 检查端口占用
netstat -an | grep 8188

# 重启ComfyUI
python main.py --port 8188
```

#### 2. "图片中未找到ComfyUI工作流数据"

**可能原因**：
- 图片不是ComfyUI生成的
- 工作流数据损坏或缺失
- 图片格式不支持

**解决方案**：
- 使用ComfyUI原生生成的PNG图片
- 检查图片是否包含metadata
- 尝试重新下载原始图片

#### 3. "工作流导入失败"

**可能原因**：
- 工作流包含未安装的节点
- ComfyUI版本不兼容
- 模型文件缺失

**解决方案**：
- 检查ComfyUI控制台的错误信息
- 安装缺失的自定义节点
- 更新ComfyUI到最新版本

### 调试模式

启用详细日志输出：

```python
# 在测试脚本中启用调试
python test_comfyui_integration.py
```

这将显示详细的连接、提取和导入过程信息。

## API参考

### ComfyUIIntegration类

#### 主要方法

```python
# 检查ComfyUI状态
is_running, message = comfyui_integration.check_comfyui_status()

# 提取工作流
workflow = comfyui_integration.extract_comfyui_workflow(image_path)

# 导入工作流
success, message = comfyui_integration.load_workflow_from_image(image_path)

# 上传图片
result = comfyui_integration.upload_image_to_comfyui(image_path)

# 在浏览器中打开ComfyUI
success, message = comfyui_integration.open_comfyui_in_browser()
```

#### 配置选项

```python
# 自定义连接参数
comfyui = ComfyUIIntegration(
    host="127.0.0.1",    # ComfyUI服务器地址
    port=8188            # ComfyUI服务器端口
)
```

## 开发计划

### 🚀 即将推出

- [ ] **自定义节点支持**：自动下载和安装缺失的节点
- [ ] **工作流预览**：导入前预览工作流结构
- [ ] **批量导入**：一次导入多个工作流
- [ ] **工作流比较**：对比不同版本的工作流差异

### 💡 未来计划

- [ ] **远程ComfyUI支持**：连接到远程ComfyUI实例
- [ ] **工作流优化**：自动优化工作流性能
- [ ] **模板库**：内置常用工作流模板
- [ ] **版本管理**：工作流版本控制和回滚

## 技术实现

### 核心技术栈

- **HTTP API调用**：使用requests库与ComfyUI通信
- **图片元数据解析**：使用PIL提取PNG文本块
- **JSON处理**：解析和构建工作流数据结构
- **异步处理**：非阻塞的用户界面交互

### 数据流程

```
图片文件 → 元数据提取 → 工作流解析 → API调用 → ComfyUI导入
     ↓
   错误处理 ← 状态检查 ← JSON验证 ← 网络通信
```

## 支持与反馈

### 获取帮助

1. **查看日志**：检查控制台输出的详细错误信息
2. **运行测试**：使用`test_comfyui_integration.py`诊断问题
3. **检查网络**：确认ComfyUI API访问正常

### 常用测试命令

```bash
# 测试ComfyUI连接
curl http://127.0.0.1:8188/system_stats

# 测试工作流导入
python test_comfyui_integration.py

# 查看ComfyUI队列状态
curl http://127.0.0.1:8188/queue
```

---

**享受ComfyUI集成功能，让工作流分享和复用变得更加简单！** 🎨✨ 