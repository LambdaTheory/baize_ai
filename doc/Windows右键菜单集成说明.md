# Windows右键菜单集成功能说明

## 功能概述

Windows右键菜单集成功能允许您在文件资源管理器中右键点击图片文件时，直接选择"使用AI图片信息提取工具打开"，快速启动应用程序并加载选中的图片。

## 🆕 应用程序内置管理功能

从 v3.0 版本开始，右键菜单的安装和卸载功能已经直接集成到应用程序的设置界面中，无需单独运行安装脚本！

### 使用内置管理功能（推荐）

1. **启动应用程序**
   - 运行 `main.py` 或双击应用程序图标

2. **打开设置界面**
   - 在应用程序的导航栏中点击"设置"
   - 找到"系统集成"部分的"Windows右键菜单集成"卡片

3. **管理右键菜单功能**
   - 点击"安装右键菜单"按钮来启用功能
   - 点击"卸载右键菜单"按钮来禁用功能
   - 实时查看当前安装状态

4. **权限处理**
   - 如果需要管理员权限，应用程序会自动提示
   - 建议以管理员身份运行应用程序以获得最佳体验

## 支持的文件类型

- PNG
- JPG/JPEG
- BMP
- GIF
- TIFF
- WEBP

## 安装步骤

### 方法一：使用批处理文件（推荐）

1. **以管理员身份运行安装程序**
   - 右键点击 `install_context_menu.bat`
   - 选择"以管理员身份运行"

2. **确认安装**
   - 在弹出的窗口中输入 `y` 并按回车键
   - 等待安装完成

### 方法二：直接运行Python脚本

1. **打开管理员命令提示符**
   - 按 `Win + R`，输入 `cmd`
   - 按 `Ctrl + Shift + Enter` 以管理员身份运行

2. **导航到项目目录**
   ```bash
   cd /path/to/pic_tool
   ```

3. **运行安装脚本**
   ```bash
   python install_context_menu.py
   ```

## 使用方法

安装完成后：

1. **在文件资源管理器中找到任意支持的图片文件**

2. **右键点击图片文件**

3. **从右键菜单中选择"使用AI图片信息提取工具打开"**

4. **应用程序将自动启动并加载选中的图片**

## 卸载步骤

### 方法一：使用批处理文件（推荐）

1. **以管理员身份运行卸载程序**
   - 右键点击 `uninstall_context_menu.bat`
   - 选择"以管理员身份运行"

2. **确认卸载**
   - 在弹出的窗口中输入 `y` 并按回车键
   - 等待卸载完成

### 方法二：直接运行Python脚本

1. **打开管理员命令提示符**

2. **导航到项目目录**
   ```bash
   cd /path/to/pic_tool
   ```

3. **运行卸载脚本**
   ```bash
   python uninstall_context_menu.py
   ```

## 技术实现

### 注册表修改

该功能通过修改Windows注册表来实现：

- **注册表路径**: `HKEY_CLASSES_ROOT\<文件扩展名>\shell\AI图片信息提取工具`
- **命令路径**: `HKEY_CLASSES_ROOT\<文件扩展名>\shell\AI图片信息提取工具\command`

### 命令行参数支持

`main.py` 已经被修改以支持命令行参数：

```python
python main.py <图片文件路径>
```

当通过右键菜单启动时，选中的文件路径会自动传递给应用程序。

## 注意事项

1. **管理员权限**
   - 安装和卸载都需要管理员权限
   - 这是因为需要修改系统注册表

2. **杀毒软件**
   - 某些杀毒软件可能会拦截注册表修改
   - 如果遇到问题，请临时关闭杀毒软件或将脚本加入白名单

3. **路径包含空格**
   - 脚本已经处理了路径包含空格的情况
   - 所有路径都会被正确地用引号包围

4. **开发环境 vs 打包环境**
   - 在开发环境中，右键菜单会调用Python解释器来运行main.py
   - 在打包环境中，右键菜单会直接调用exe文件

## 故障排除

### 右键菜单没有出现

1. **检查是否以管理员权限运行了安装脚本**
2. **重启文件资源管理器**
   - 按 `Ctrl + Shift + Esc` 打开任务管理器
   - 找到"Windows资源管理器"进程并结束
   - 在任务管理器中点击"文件" → "运行新任务" → 输入 `explorer.exe`

3. **检查注册表**
   - 按 `Win + R`，输入 `regedit`
   - 导航到 `HKEY_CLASSES_ROOT\.png\shell`
   - 查看是否有"AI图片信息提取工具"项

### 点击右键菜单无反应

1. **检查Python环境**
   - 确保Python已正确安装且在PATH中

2. **检查应用程序路径**
   - 确保main.py文件存在于正确位置

3. **查看命令行**
   - 可以手动运行以下命令测试：
   ```bash
   python main.py "C:\path\to\test_image.png"
   ```

### 权限问题

如果遇到权限相关错误：

1. **确保以管理员身份运行**
2. **检查UAC设置**
3. **临时关闭杀毒软件**

## 文件清单

### 应用程序集成文件
- `ui/fluent_settings_widget.py` - 🆕 设置界面组件（包含右键菜单管理）
- `main.py` - 已修改为支持命令行参数的主程序
- `test_integrated_context_menu.py` - 🆕 集成功能测试脚本

### 独立安装脚本（备用）
- `install_context_menu.py` - Python安装脚本
- `uninstall_context_menu.py` - Python卸载脚本
- `install_context_menu.bat` - Windows安装批处理文件
- `uninstall_context_menu.bat` - Windows卸载批处理文件
- `test_context_menu.py` - 功能测试脚本

## 更新记录

- **v3.0** - 🆕 应用程序内置管理功能
  - 右键菜单管理直接集成到设置界面
  - 实时状态显示和操作反馈
  - 异步操作处理，避免界面冻结
  - 自动权限检查和提示
- **v1.0** - 初始版本，支持基本的右键菜单功能
  - 支持多种图片格式
  - 自动检测开发环境和打包环境
  - 包含完整的安装和卸载功能 