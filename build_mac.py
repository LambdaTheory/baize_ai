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
    png_path = "assets/baize_icon.png"
    icns_path = "assets/baize_icon.icns"
    
    if not os.path.exists(png_path):
        print(f"警告: PNG图标文件 {png_path} 不存在")
        return None
    
    # 如果已经存在icns文件，直接返回
    if os.path.exists(icns_path):
        print(f"发现现有的icns文件: {icns_path}")
        return icns_path
    
    try:
        # 在macOS上，可以使用sips命令转换图标
        if sys.platform == 'darwin':
            subprocess.run([
                'sips', '-s', 'format', 'icns', 
                png_path, '--out', icns_path
            ], check=True)
            print(f"成功创建icns图标: {icns_path}")
            return icns_path
        else:
            # 在其他平台上，尝试使用pillow转换（需要额外的库）
            print("非macOS平台，无法直接创建icns文件")
            return None
    except subprocess.CalledProcessError:
        print("创建icns图标失败")
        return None

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
        'pyinstaller',
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
    """创建DMG安装包"""
    app_path = f"dist/{app_name}.app"
    dmg_path = f"dist/{app_name}.dmg"
    
    if not os.path.exists(app_path):
        print(f"错误: 找不到应用文件 {app_path}")
        return False
    
    if os.path.exists(dmg_path):
        os.remove(dmg_path)
        print(f"已删除现有的DMG文件: {dmg_path}")
    
    try:
        # 使用hdiutil创建DMG文件
        subprocess.run([
            'hdiutil', 'create',
            '-volname', app_name,
            '-srcfolder', app_path,
            '-ov', '-format', 'UDZO',
            dmg_path
        ], check=True)
        
        print(f"成功创建DMG安装包: {dmg_path}")
        
        # 显示DMG文件大小
        if os.path.exists(dmg_path):
            file_size = os.path.getsize(dmg_path) / (1024 * 1024)  # MB
            print(f"DMG文件大小: {file_size:.1f} MB")
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"创建DMG失败: {e}")
        return False

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
        subprocess.run(['pyinstaller', '--version'], check=True, capture_output=True)
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