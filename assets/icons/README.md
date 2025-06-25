# 白泽AI 应用图标

## 📁 文件说明

本目录包含白泽AI的应用图标文件，支持各种尺寸和格式。

### 🔖 图标文件

#### PNG图标 (各种尺寸)
- `baize_icon_16x16.png` - 16x16 像素
- `baize_icon_24x24.png` - 24x24 像素  
- `baize_icon_32x32.png` - 32x32 像素
- `baize_icon_48x48.png` - 48x48 像素
- `baize_icon_64x64.png` - 64x64 像素
- `baize_icon_128x128.png` - 128x128 像素
- `baize_icon_256x256.png` - 256x256 像素
- `baize_icon_512x512.png` - 512x512 像素
- `baize_icon_1024x1024.png` - 1024x1024 像素

#### 平台特定格式
- `baize_app_icon.ico` - Windows应用图标
- `baize_app_icon.png` - macOS应用图标 (1024x1024)

#### 主图标
- `../app_icon.png` - 主应用图标 (128x128)

### 🎯 使用建议

- **PyQt应用**: 使用 `app_icon.png` 或任意PNG格式
- **Windows exe**: 使用 `baize_app_icon.ico`
- **macOS app**: 使用 `baize_app_icon.png`
- **任务栏/系统托盘**: 推荐使用 32x32 或 48x48

### 🔧 代码示例

```python
# PyQt5 设置窗口图标
from PyQt5.QtGui import QIcon
app.setWindowIcon(QIcon("assets/app_icon.png"))

# PyInstaller 设置exe图标
--icon=assets/icons/baize_app_icon.ico
```

### 📊 文件信息

- 源Logo: assets/baize_logo_modern.png
- 生成时间: 1750822108.1928334
- 总图标数: 10 个PNG + ICO + macOS图标
