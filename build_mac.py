#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
macOS 打包脚本
使用此脚本将应用打包成macOS .app 文件
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
import argparse

def clean_build_dirs():
    """清理构建目录"""
    dirs_to_clean = ['build', 'dist', '__pycache__']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"已清理目录: {dir_name}")

def clean_temp_files():
    """清理临时文件和不必要的文件"""
    print("清理临时文件...")
    
    # 清理临时HTML文件
    html_files = [f for f in os.listdir('.') if f.endswith('.html') and ('分享' in f or 'test_' in f or 'demo_' in f)]
    for html_file in html_files:
        if os.path.exists(html_file):
            os.remove(html_file)
            print(f"已删除临时文件: {html_file}")
    
    # 清理Excel测试文件
    excel_files = [f for f in os.listdir('.') if f.endswith('.xlsx') and ('test_' in f or '~$' in f)]
    for excel_file in excel_files:
        if os.path.exists(excel_file):
            os.remove(excel_file)
            print(f"已删除Excel测试文件: {excel_file}")
    
    # 清理Python缓存
    for root, dirs, files in os.walk('.'):
        # 删除__pycache__目录
        if '__pycache__' in dirs:
            shutil.rmtree(os.path.join(root, '__pycache__'))
            print(f"已删除缓存目录: {os.path.join(root, '__pycache__')}")
        
        # 删除.pyc文件
        for file in files:
            if file.endswith('.pyc'):
                os.remove(os.path.join(root, file))
                print(f"已删除缓存文件: {os.path.join(root, file)}")

def create_icns_from_png():
    """从PNG文件创建macOS所需的icns图标文件"""
    icns_path = "assets/baize_icon.icns"
    
    # 如果已经存在icns文件，直接返回
    if os.path.exists(icns_path):
        print(f"使用现有的icns文件: {icns_path}")
        return icns_path
    
    # 使用正方形的图标文件
    png_path = "assets/icons/baize_icon_1024x1024.png"
    
    if not os.path.exists(png_path):
        print(f"警告: PNG图标文件 {png_path} 不存在")
        # 尝试备用图标
        backup_path = "assets/icons/baize_app_icon.png"
        if os.path.exists(backup_path):
            png_path = backup_path
            print(f"使用备用图标: {backup_path}")
        else:
            return None
    
    try:
        # 在macOS上，可以使用sips命令转换图标
        if sys.platform == 'darwin':
            # 创建临时目录来避免权限问题
            temp_dir = os.path.expanduser("~/tmp_icon")
            os.makedirs(temp_dir, exist_ok=True)
            temp_icns = os.path.join(temp_dir, "icon.icns")
            
            subprocess.run([
                'sips', '-s', 'format', 'icns', 
                png_path, '--out', temp_icns
            ], check=True)
            
            # 复制到目标位置
            shutil.copy2(temp_icns, icns_path)
            shutil.rmtree(temp_dir)
            
            print(f"成功创建icns图标: {icns_path}")
            return icns_path
        else:
            # 在其他平台上，直接使用PNG文件
            return png_path
    except (subprocess.CalledProcessError, Exception) as e:
        print(f"创建icns图标失败: {e}")
        # 如果创建失败，直接使用PNG文件
        return png_path

def build_mac_app(no_activation: bool = False):
    """构建macOS .app文件"""
    print("开始构建macOS应用...")

    if no_activation:
        print("构建免激活版本...")
        flag_file = Path("no_activation.flag")
        flag_file.touch()
        print("已创建免激活标记文件: no_activation.flag")

    # 尝试创建icns图标
    icon_path = create_icns_from_png()

    # PyInstaller 命令参数
    cmd = [
        'python3', '-m', 'PyInstaller',
        '--onedir',                     # 创建目录而不是单文件（推荐用于macOS）
        '--windowed',                   # 创建GUI应用（无终端窗口）
        '--name=白泽',                  # 指定应用名称
        '--add-data=assets:assets',     # 包含assets目录（macOS用冒号分隔）
        '--hidden-import=PyQt5.sip',    # 确保PyQt5正确导入
        '--hidden-import=PIL._tkinter_finder',  # Pillow依赖
        '--hidden-import=qfluentwidgets',       # Fluent Widgets
        '--hidden-import=cryptography',         # 加密库
        '--hidden-import=cryptography.hazmat.primitives',
        '--hidden-import=cryptography.hazmat.backends',
        '--noconfirm',                  # 不询问覆盖
        # 排除不必要的模块
        '--exclude-module=matplotlib',
        '--exclude-module=pandas',
        '--exclude-module=numpy',
        '--exclude-module=scipy',
        '--exclude-module=tkinter',
        '--exclude-module=pytest',
        '--exclude-module=setuptools',
        # 排除测试文件
        '--exclude-module=test_*',
        # macOS特定选项
        '--osx-bundle-identifier=com.baize.ai-image-reader',
        'main.py'                       # 主文件
    ]

    # 如果有图标文件，添加图标参数
    if icon_path:
        cmd.insert(-1, f'--icon={icon_path}')
    
    if no_activation:
        cmd.insert(-1, '--add-data=no_activation.flag:.')
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("构建成功！")
        print("应用文件位置: dist/白泽.app")
        
        # 显示文件夹大小
        app_path = "dist/白泽.app"
        if os.path.exists(app_path):
            # 计算应用包的大小
            total_size = 0
            for dirpath, dirnames, filenames in os.walk(app_path):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    total_size += os.path.getsize(fp)
            
            size_mb = total_size / (1024 * 1024)  # MB
            print(f"应用包大小: {size_mb:.1f} MB")
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"构建失败: {e}")
        print(f"错误输出: {e.stderr}")
        return False
    finally:
        if no_activation and 'flag_file' in locals() and flag_file.exists():
            flag_file.unlink()
            print("已清理免激活标记文件。")

def create_dmg(app_name="白泽"):
    """创建专业的DMG安装包"""
    app_path = f"dist/{app_name}.app"
    dmg_path = f"dist/{app_name}.dmg"
    temp_dmg_dir = f"dist/dmg_temp"
    
    if not os.path.exists(app_path):
        print(f"错误: 找不到应用文件 {app_path}")
        return False
    
    if os.path.exists(dmg_path):
        os.remove(dmg_path)
        print(f"已删除现有的DMG文件: {dmg_path}")
    
    # 清理临时目录
    if os.path.exists(temp_dmg_dir):
        shutil.rmtree(temp_dmg_dir)
    
    try:
        # 创建临时目录结构
        os.makedirs(temp_dmg_dir, exist_ok=True)
        
        # 复制应用到临时目录
        shutil.copytree(app_path, f"{temp_dmg_dir}/{app_name}.app")
        
        # 创建应用程序文件夹的符号链接
        os.symlink("/Applications", f"{temp_dmg_dir}/Applications")
        
        # 创建专业的安装指南
        readme_content = f"""# 🐉 {app_name}AI 安装指南

## 🚀 快速安装
1. **拖拽安装**: 将 {app_name}.app 拖拽到 Applications 文件夹
2. **启动应用**: 在 Launchpad 或 Applications 文件夹中找到 {app_name}AI
3. **开始使用**: 双击启动，开始您的AI图片分析之旅

## 🔒 首次运行安全设置
如遇安全警告，请选择以下任一方法：

**方法一（推荐）:**
1. 打开"系统偏好设置" → "安全性与隐私"
2. 在"通用"选项卡中点击"仍要打开"

**方法二（终端命令）:**
```bash
sudo xattr -rd com.apple.quarantine /Applications/{app_name}.app
```

## ✨ 功能特点
- ✅ **100% 本地运行** - 完全保护您的隐私安全
- ✅ **智能拖拽** - 支持PNG、JPG、WebP等多种格式
- ✅ **AI信息提取** - 自动识别Prompt、模型、参数等
- ✅ **本地数据库** - 所有数据安全存储在您的设备
- ✅ **多格式导出** - 支持JSON、CSV格式导出
- ✅ **提示词管理** - 智能提示词编辑和翻译功能

## 📁 数据存储位置
用户数据自动保存在：
```
~/Library/Application Support/{app_name}AI/
├── database/records.db        # 图片记录数据库
└── data/prompt_history.json   # 提示词历史记录
```

## 🗑️ 完全卸载
1. 将 Applications 文件夹中的 {app_name}.app 移到废纸篓
2. 如需删除用户数据，请删除上述数据文件夹

## 💡 使用技巧
- 支持批量拖拽多个图片文件
- 可以直接编辑和保存提示词
- 支持中英文提示词智能翻译
- 历史记录可快速检索和管理

## 📞 技术支持
- 应用内置帮助文档
- 遇到问题请查看日志信息
- 建议在macOS 10.14+系统上运行

---
**{app_name}AI** - 智能图片信息提取工具  
版本: 1.0.0 | 适用于 macOS 10.14+  
© 2024 {app_name}AI Team. All rights reserved.
"""
        
        with open(f"{temp_dmg_dir}/📖 安装指南.txt", "w", encoding="utf-8") as f:
            f.write(readme_content)
        
        # 创建一个简单的欢迎文件
        welcome_content = f"""欢迎使用 {app_name}AI！

这是一款专业的AI图片信息提取工具，帮助您：
• 快速提取AI生成图片的元数据
• 管理和编辑提示词
• 导出和分享您的创作记录

安装方法：
将 {app_name}.app 拖拽到 Applications 文件夹即可

祝您使用愉快！
"""
        
        with open(f"{temp_dmg_dir}/欢迎使用.txt", "w", encoding="utf-8") as f:
            f.write(welcome_content)
        
        # 直接创建最终的DMG文件（使用压缩格式）
        print("正在创建专业DMG安装包...")
        subprocess.run([
            'hdiutil', 'create',
            '-volname', f'{app_name}AI Installer',
            '-srcfolder', temp_dmg_dir,
            '-ov', '-format', 'UDZO',  # 直接使用压缩格式
            '-imagekey', 'zlib-level=6',  # 中等压缩
            dmg_path
        ], check=True)
        
        # 清理临时目录
        shutil.rmtree(temp_dmg_dir)
        
        print(f"✅ 成功创建专业DMG安装包: {dmg_path}")
        
        # 显示DMG文件大小
        if os.path.exists(dmg_path):
            file_size = os.path.getsize(dmg_path) / (1024 * 1024)  # MB
            print(f"📦 DMG文件大小: {file_size:.1f} MB")
        
        # 尝试设置DMG外观（使用专业的浅灰色背景）
        print("正在尝试设置DMG外观...")
        try:
            # 挂载DMG
            mount_result = subprocess.run([
                'hdiutil', 'attach', dmg_path, '-noverify', '-noautoopen'
            ], capture_output=True, text=True)
            
            # 查找挂载点
            mount_point = None
            for line in mount_result.stdout.split('\n'):
                if f'{app_name}AI Installer' in line and '/Volumes/' in line:
                    mount_point = f"/Volumes/{app_name}AI Installer"
                    break
            
            if mount_point and os.path.exists(mount_point):
                # 设置外观的AppleScript（使用专业的浅灰色背景）
                applescript = f'''
tell application "Finder"
    tell disk "{app_name}AI Installer"
        open
        set current view of container window to icon view
        set toolbar visible of container window to false
        set statusbar visible of container window to false
        set the bounds of container window to {{100, 100, 740, 500}}
        set viewOptions to the icon view options of container window
        set arrangement of viewOptions to not arranged
        set icon size of viewOptions to 128
        
        -- 设置专业的浅灰色背景 (RGB: 240, 240, 240)
        set background color of viewOptions to {{61440, 61440, 61440}}
        
        -- 设置图标位置
        try
            set position of item "{app_name}.app" of container window to {{150, 200}}
            set position of item "Applications" of container window to {{490, 200}}
            set position of item "📖 安装指南.txt" of container window to {{320, 320}}
            set position of item "欢迎使用.txt" of container window to {{320, 380}}
        end try
        
        -- 更新并关闭
        update without registering applications
        delay 1
        close
    end tell
end tell
'''
                
                # 执行AppleScript
                subprocess.run(['osascript', '-e', applescript], 
                             check=True, timeout=30)
                print("✅ DMG外观设置完成（专业浅灰色背景）")
                
                # 卸载DMG
                subprocess.run(['hdiutil', 'detach', mount_point], check=True)
                
        except Exception as e:
            print(f"⚠️  设置DMG外观时出错: {e}")
            print("DMG已创建，但外观可能需要手动调整")
            
        # 提供使用建议
        print(f"""
🎉 DMG安装包创建完成！

📋 包含内容:
• {app_name}.app - 主应用程序
• Applications - 应用程序文件夹快捷方式
• 📖 安装指南.txt - 详细安装说明
• 欢迎使用.txt - 快速入门指南

🎨 视觉特性:
• 专业的浅灰色背景 (RGB: 240, 240, 240)
• 优化的图标布局
• 专业的窗口设置 (640x400像素)
• 128px图标大小
• 清晰的视觉层次

🚀 分发建议:
• 可直接分发给用户使用
• 用户双击DMG后拖拽安装即可
• 包含完整的安装和使用说明
• 简洁专业的视觉体验
• 符合macOS设计规范
""")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 创建DMG失败: {e}")
        cleanup_dmg_temp_files(temp_dmg_dir, dmg_path)
        return False
    except Exception as e:
        print(f"❌ 创建DMG时出错: {e}")
        cleanup_dmg_temp_files(temp_dmg_dir, dmg_path)
        return False

def cleanup_dmg_temp_files(temp_dmg_dir, dmg_path):
    """清理DMG创建过程中的临时文件"""
    if os.path.exists(temp_dmg_dir):
        shutil.rmtree(temp_dmg_dir)
    temp_dmg_path = f"{dmg_path}.temp.dmg"
    if os.path.exists(temp_dmg_path):
        os.remove(temp_dmg_path)

def create_dmg_background_image():
    """创建DMG背景图片"""
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # 设置画布尺寸
        width, height = 640, 400
        
        # 创建渐变背景
        img = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(img)
        
        # 创建从白色到浅灰色的渐变
        for y in range(height):
            ratio = y / height
            gray_value = int(255 - (ratio * 30))
            color = (gray_value, gray_value, gray_value)
            draw.line([(0, y), (width, y)], fill=color)
        
        # 添加标题区域
        title_height = 80
        draw.rectangle([(0, 0), (width, title_height)], fill=(45, 45, 45))
        
        # 尝试加载字体
        try:
            title_font = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 28)
            subtitle_font = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 16)
        except:
            title_font = ImageFont.load_default()
            subtitle_font = ImageFont.load_default()
        
        # 添加标题文字
        title_text = "白泽AI"
        subtitle_text = "AI图片信息提取工具"
        
        # 计算文字位置（居中）
        title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
        title_width = title_bbox[2] - title_bbox[0]
        title_x = (width - title_width) // 2
        
        subtitle_bbox = draw.textbbox((0, 0), subtitle_text, font=subtitle_font)
        subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
        subtitle_x = (width - subtitle_width) // 2
        
        # 绘制标题
        draw.text((title_x, 15), title_text, fill='white', font=title_font)
        draw.text((subtitle_x, 50), subtitle_text, fill=(200, 200, 200), font=subtitle_font)
        
        # 添加箭头指示
        arrow_y = height // 2 - 20
        arrow_points = [
            (width//2 - 30, arrow_y),
            (width//2 - 10, arrow_y - 10),
            (width//2 - 10, arrow_y - 5),
            (width//2 + 30, arrow_y - 5),
            (width//2 + 30, arrow_y + 5),
            (width//2 - 10, arrow_y + 5),
            (width//2 - 10, arrow_y + 10)
        ]
        draw.polygon(arrow_points, fill=(100, 150, 255), outline=(80, 130, 235))
        
        # 保存图片
        background_path = "assets/dmg_background.png"
        img.save(background_path, 'PNG', quality=95)
        print(f"DMG背景图片已创建: {background_path}")
        
    except ImportError:
        print("警告: 无法导入PIL库，跳过背景图片创建")
    except Exception as e:
        print(f"创建背景图片时出错: {e}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="白泽AI - macOS打包程序")
    parser.add_argument('--no-activation', action='store_true', help='构建一个不需要激活的版本')
    parser.add_argument('--create-dmg', action='store_true', help='同时创建DMG安装包')
    args = parser.parse_args()

    print("=== 白泽AI - macOS打包程序 ===")
    
    # 检查是否在macOS上运行
    if sys.platform != 'darwin':
        print("警告: 建议在macOS系统上进行macOS应用打包以获得最佳兼容性")
    
    # 检查pyinstaller是否安装
    try:
        subprocess.run(['python3', '-m', 'PyInstaller', '--version'], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("错误: 未找到PyInstaller，请先安装:")
        print("pip install pyinstaller")
        return False
    
    # 清理临时文件
    clean_temp_files()
    
    # 清理旧的构建文件
    clean_build_dirs()
    
    # 开始构建
    success = build_mac_app(no_activation=args.no_activation)
    
    if success:
        print("\n应用构建完成！您可以在 dist/ 目录中找到生成的.app文件。")
        
        if args.create_dmg:
            print("\n开始创建DMG安装包...")
            dmg_success = create_dmg()
            if dmg_success:
                print("DMG安装包创建完成！")
            else:
                print("DMG创建失败，但.app文件可以正常使用。")
        
        print("\n使用说明:")
        print("1. 在macOS上，可以直接双击运行.app文件")
        print("2. 如果系统提示安全警告，请在系统偏好设置 > 安全性与隐私中允许运行")
        print("3. 建议在macOS系统上测试应用确保所有功能正常工作")
        
    else:
        print("\n构建失败，请检查错误信息并修复。")
    
    return success

if __name__ == "__main__":
    main() 