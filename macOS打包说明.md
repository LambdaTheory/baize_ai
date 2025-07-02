# 白泽AI - macOS 打包说明

## 概述
本文档介绍如何在macOS平台上打包白泽AI应用，生成可分发的.app文件和DMG安装包。

## 前置要求

### 1. 系统要求
- macOS 10.14 (Mojave) 或更高版本
- Python 3.10 或更高版本
- 足够的磁盘空间（至少1GB用于构建过程）

### 2. 开发环境准备
```bash
# 1. 确保安装了Python 3.10+
python3 --version

# 2. 创建虚拟环境（推荐）
python3 -m venv venv_mac
source venv_mac/bin/activate

# 3. 安装macOS专用依赖
pip install -r requirements-mac.txt

# 4. 验证关键依赖是否正确安装
python3 -c "import PyQt5; print('PyQt5 安装成功')"
python3 -c "import qfluentwidgets; print('Fluent Widgets 安装成功')"
```

## 打包步骤

### 1. 基本打包
```bash
# 运行macOS打包脚本
python3 build_mac.py
```

### 2. 免激活版本打包
```bash
# 打包不需要激活码的版本
python3 build_mac.py --no-activation
```

### 3. 同时创建DMG安装包
```bash
# 打包并创建DMG文件
python3 build_mac.py --create-dmg
```

### 4. 完整命令示例
```bash
# 最完整的打包命令
python3 build_mac.py --no-activation --create-dmg
```

## 输出文件

打包完成后，您将在 `dist/` 目录中找到以下文件：

- **白泽.app** - macOS应用包，可直接运行
- **白泽.dmg** - DMG安装包（如果使用了 --create-dmg 选项）

## 应用分发

### 1. 直接分发.app文件
- 将 `白泽.app` 压缩为ZIP文件
- 用户下载后解压即可使用

### 2. 使用DMG安装包
- 直接分发 `白泽.dmg` 文件
- 用户双击挂载后，将应用拖拽到Applications文件夹

## 常见问题

### 1. 安全性问题
macOS可能会阻止未签名的应用运行，用户需要：
```
系统偏好设置 > 安全性与隐私 > 通用 > 允许从以下位置下载的应用
选择："App Store 和被认可的开发者" 或 "任何来源"
```

或者在终端中运行：
```bash
sudo spctl --master-disable
```

### 2. 权限问题
如果应用需要访问某些系统资源，可能需要在Info.plist中添加权限说明。

### 3. 代码签名（推荐但不必需）
为了更好的用户体验，建议进行代码签名：
```bash
# 需要Apple Developer账户
codesign --force --deep --sign "Developer ID Application: Your Name" dist/白泽.app
```

### 4. 公证（Notarization）
对于公开分发，建议进行公证：
```bash
# 需要Apple Developer账户
xcrun notarytool submit dist/白泽.dmg --keychain-profile "notary-profile" --wait
```

## 打包脚本说明

`build_mac.py` 脚本包含以下主要功能：

1. **自动清理** - 清理旧的构建文件和临时文件
2. **图标转换** - 自动将PNG图标转换为macOS所需的ICNS格式
3. **依赖打包** - 自动包含所有必要的Python依赖
4. **资源包含** - 确保assets目录正确包含在应用包中
5. **DMG创建** - 可选择性创建DMG安装包

## 性能优化建议

1. **构建环境** - 在macOS上构建以获得最佳兼容性
2. **虚拟环境** - 使用干净的虚拟环境避免不必要的依赖
3. **资源优化** - 确保assets目录只包含必要的文件
4. **测试** - 在不同版本的macOS上测试应用

## 故障排除

### 构建失败
1. 检查Python版本是否符合要求
2. 确认所有依赖已正确安装
3. 查看错误日志，通常在构建输出中显示

### 运行时问题
1. 检查.app包是否完整
2. 确认所有资源文件是否正确包含
3. 检查macOS系统版本兼容性

### 依赖问题
```bash
# 重新安装依赖
pip uninstall -r requirements-mac.txt -y
pip install -r requirements-mac.txt
```

## 联系支持
如果遇到打包问题，请检查：
1. 系统环境是否满足要求
2. 依赖是否正确安装
3. 错误日志的具体信息 