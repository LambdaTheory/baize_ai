# 图标修复说明

## 问题描述
macOS应用图标显示为扁平（非正方形），影响视觉效果。

## 问题原因
原始图标文件 `assets/baize_icon.png` 的尺寸为 **370 x 281** 像素，不是正方形，导致图标显示变形。

## 解决方案

### 1. 问题诊断
```bash
# 检查原始图标尺寸
file assets/baize_icon.png
# 输出: PNG image data, 370 x 281, 8-bit/color RGBA, non-interlaced
```

### 2. 使用正方形图标
项目中已有正方形图标文件：
```
assets/icons/
├── baize_icon_16x16.png     # 16x16
├── baize_icon_32x32.png     # 32x32
├── baize_icon_64x64.png     # 64x64
├── baize_icon_128x128.png   # 128x128
├── baize_icon_256x256.png   # 256x256
├── baize_icon_512x512.png   # 512x512
└── baize_icon_1024x1024.png # 1024x1024
```

### 3. 创建标准icns文件
使用macOS的iconutil工具创建标准的icns文件：

```bash
# 创建iconset目录结构
mkdir temp_iconset.iconset

# 复制不同尺寸的图标
cp assets/icons/baize_icon_16x16.png temp_iconset.iconset/icon_16x16.png
cp assets/icons/baize_icon_32x32.png temp_iconset.iconset/icon_16x16@2x.png
cp assets/icons/baize_icon_32x32.png temp_iconset.iconset/icon_32x32.png
cp assets/icons/baize_icon_64x64.png temp_iconset.iconset/icon_32x32@2x.png
cp assets/icons/baize_icon_128x128.png temp_iconset.iconset/icon_128x128.png
cp assets/icons/baize_icon_256x256.png temp_iconset.iconset/icon_128x128@2x.png
cp assets/icons/baize_icon_256x256.png temp_iconset.iconset/icon_256x256.png
cp assets/icons/baize_icon_512x512.png temp_iconset.iconset/icon_256x256@2x.png
cp assets/icons/baize_icon_512x512.png temp_iconset.iconset/icon_512x512.png
cp assets/icons/baize_icon_1024x1024.png temp_iconset.iconset/icon_512x512@2x.png

# 生成icns文件
iconutil -c icns temp_iconset.iconset -o assets/baize_icon.icns

# 清理临时文件
rm -rf temp_iconset.iconset
```

### 4. 修改构建脚本
更新 `build_mac.py` 中的图标处理逻辑：
- 优先使用现有的icns文件
- 如果需要创建，使用正方形的PNG文件
- 添加备用图标路径

## 修复效果

### 修复前
- 图标尺寸：370 x 281（非正方形）
- 显示效果：扁平变形
- 用户体验：不专业

### 修复后
- 图标尺寸：正方形（多种尺寸）
- 显示效果：标准macOS图标
- 用户体验：专业美观

## 验证方法

### 1. 检查icns文件
```bash
ls -la assets/baize_icon.icns
# 应该显示文件存在且大小合理（~1.5MB）
```

### 2. 重新打包测试
```bash
python3 build_mac.py --create-dmg
```

### 3. 视觉检查
- 在Finder中查看.app文件图标
- 在DMG安装包中查看图标
- 在Dock中查看运行时图标

## macOS图标标准

### 推荐尺寸
- 16x16 (icon_16x16.png)
- 32x32 (icon_16x16@2x.png, icon_32x32.png)
- 64x64 (icon_32x32@2x.png)
- 128x128 (icon_128x128.png)
- 256x256 (icon_128x128@2x.png, icon_256x256.png)
- 512x512 (icon_256x256@2x.png, icon_512x512.png)
- 1024x1024 (icon_512x512@2x.png)

### 设计要求
- 必须是正方形
- 支持透明背景
- 高质量PNG格式
- 适合不同显示密度

## 总结
通过使用正方形的图标文件和标准的icns格式，成功修复了图标显示问题，提升了应用的专业度和用户体验。
