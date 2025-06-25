#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
白泽AI 应用图标生成器
从现有logo生成各种尺寸的应用图标
"""

import os
from PIL import Image
from pathlib import Path


def create_app_icons():
    """生成应用图标的各种尺寸"""
    
    print("🔖 开始生成白泽AI应用图标...")
    
    # 输入logo文件（按优先级排序）
    logo_files = [
        "assets/baize_logo_traditional.png",  # 推荐用作应用图标
        "assets/baize_logo_modern.png",
        "assets/baize_logo_tech.png",
    ]
    
    # 输出图标尺寸
    icon_sizes = [
        16, 24, 32, 48, 64, 96, 128, 256, 512, 1024
    ]
    
    # 找到可用的logo文件
    source_logo = None
    for logo_file in logo_files:
        if os.path.exists(logo_file):
            source_logo = logo_file
            print(f"📁 使用源Logo: {logo_file}")
            break
    
    if not source_logo:
        print("❌ 未找到任何logo文件！")
        return False
    
    try:
        # 打开源图片
        with Image.open(source_logo) as img:
            print(f"📐 源图片尺寸: {img.size}")
            
            # 创建icons目录
            icons_dir = Path("assets/icons")
            icons_dir.mkdir(exist_ok=True)
            
            # 生成各种尺寸的图标
            for size in icon_sizes:
                try:
                    # 保持长宽比缩放
                    resized_img = img.resize((size, size), Image.Resampling.LANCZOS)
                    
                    # 保存PNG格式
                    png_path = icons_dir / f"baize_icon_{size}x{size}.png"
                    resized_img.save(png_path, "PNG", optimize=True)
                    print(f"✅ 生成图标: {png_path}")
                    
                except Exception as e:
                    print(f"❌ 生成 {size}x{size} 图标失败: {e}")
                    continue
            
            # 生成ICO文件（Windows应用图标）
            try:
                ico_sizes = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
                ico_images = []
                
                for size in ico_sizes:
                    resized_img = img.resize(size, Image.Resampling.LANCZOS)
                    ico_images.append(resized_img)
                
                ico_path = icons_dir / "baize_app_icon.ico"
                ico_images[0].save(ico_path, "ICO", sizes=ico_sizes)
                print(f"🔖 生成ICO图标: {ico_path}")
                
            except Exception as e:
                print(f"❌ 生成ICO图标失败: {e}")
            
            # 生成ICNS文件（macOS应用图标）
            try:
                icns_path = icons_dir / "baize_app_icon.icns"
                # 注意：生成ICNS需要额外的库，这里先生成一个大尺寸的PNG作为替代
                large_img = img.resize((1024, 1024), Image.Resampling.LANCZOS)
                large_img.save(icns_path.with_suffix('.png'), "PNG")
                print(f"🍎 生成macOS图标: {icns_path.with_suffix('.png')}")
                
            except Exception as e:
                print(f"❌ 生成macOS图标失败: {e}")
            
            # 创建应用图标简化链接
            main_icon_path = Path("assets/app_icon.png")
            if main_icon_path.exists():
                main_icon_path.unlink()
            
            # 复制一个中等尺寸的作为主图标
            main_size_img = img.resize((128, 128), Image.Resampling.LANCZOS)
            main_size_img.save(main_icon_path, "PNG")
            print(f"📌 创建主应用图标: {main_icon_path}")
            
            # 生成图标使用说明
            readme_content = f"""# 白泽AI 应用图标

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

- 源Logo: {source_logo}
- 生成时间: {Path(__file__).stat().st_mtime}
- 总图标数: {len(icon_sizes)} 个PNG + ICO + macOS图标
"""
            
            readme_path = icons_dir / "README.md"
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(readme_content)
            
            print(f"📄 使用说明已保存至: {readme_path}")
            print("\n🎉 应用图标生成完成!")
            print(f"📁 所有图标保存在: {icons_dir.absolute()}")
            
            return True
            
    except Exception as e:
        print(f"❌ 生成应用图标时出错: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("=" * 50)
    print("🔖 白泽AI 应用图标生成器")
    print("=" * 50)
    
    success = create_app_icons()
    
    if success:
        print("\n✨ 图标生成任务完成！")
        print("💡 提示：请查看assets/icons目录中的图标文件")
        print("🔧 建议在PyInstaller配置中使用ico文件")
    else:
        print("\n❌ 图标生成失败！")
        print("🔧 请检查logo文件是否存在") 