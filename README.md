# 🐉 白泽AI - 智能图片信息提取工具

## 📌 项目概述

这是一款**本地运行的桌面应用**，用于读取AI生成图片中的生成信息（如Prompt、模型、采样器等），并以清晰的方式展示。支持用户对图片进行简单管理、记录和导出。

**特点：**
- ✅ 100% 本地运行，不联网，保护隐私
- ✅ 支持拖拽导入图片
- ✅ 自动提取AI生成信息
- ✅ 本地数据库存储
- ✅ 支持导出功能

## 🚀 快速开始

### 环境要求

- Python 3.10+
- 操作系统：Windows/macOS/Linux

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行应用

```bash
python main.py
```

## 📦 功能特性

### 1. 图片导入
- 支持拖拽导入
- 支持文件选择器导入
- 支持 PNG/JPG 格式

### 2. 信息提取
- 自动提取AI生成信息：
  - Prompt（正向提示词）
  - Negative Prompt（负向提示词）
  - Model（模型）
  - Sampler（采样器）
  - Steps（步数）
  - CFG Scale（引导强度）
  - Seed（随机种子）

### 3. 数据管理
- 本地SQLite数据库存储
- 支持添加备注和标签
- 历史记录查看
- 搜索功能

### 4. 导出功能
- 导出为JSON格式
- 导出为CSV格式

## 🗂️ 项目结构

```
ai_image_info_reader/
│
├── main.py                 # 启动入口
├── ui/
│   ├── __init__.py
│   └── main_window.py      # 主界面代码
├── core/
│   ├── __init__.py
│   ├── image_reader.py     # 图片信息读取
│   ├── data_manager.py     # 数据管理
│   └── model.py           # 数据模型
├── database/
│   └── records.db         # SQLite数据库
├── doc/
│   └── task.md           # 需求文档
├── requirements.txt       # 依赖管理
└── README.md             # 项目说明
```

## 🔧 技术栈

- **桌面框架**: PyQt5
- **图像处理**: Pillow
- **数据库**: SQLite3
- **打包工具**: PyInstaller

## 📋 使用说明

1. 启动应用后，将AI生成的图片拖拽到指定区域
2. 应用会自动提取图片中的生成信息
3. 可以添加备注或标签
4. 点击"保存记录"将信息保存到本地数据库
5. 可以在历史记录中查看和管理已保存的图片信息

## 🔐 隐私保护

- ❌ 不联网，不上传任何数据
- ❌ 不监听文件夹或自动操作
- ✅ 所有操作需用户主动触发
- ✅ 数据完全保存在本地

## 📦 打包发布

使用PyInstaller打包为可执行文件：

```bash
pyinstaller --windowed --onefile main.py
```

## 🤝 贡献

欢迎提交Issue和Pull Request！

## �� 许可证

MIT License 