#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PyInstaller 打包脚本
使用此脚本将应用打包成exe文件
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

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

def build_exe():
    """构建exe文件"""
    print("开始构建exe文件...")
    
    # PyInstaller 命令参数
    cmd = [
        'pyinstaller',
        '--onefile',                    # 打包成单个exe文件
        '--windowed',                   # 隐藏控制台窗口
        '--name=白泽',      # 指定exe文件名
        '--icon=assets/app_icon_pyinstaller.ico',  # 白泽AI应用图标（PyInstaller兼容ICO）
        '--add-data=assets;assets',     # 只包含assets目录
        '--hidden-import=PyQt5.sip',    # 确保PyQt5正确导入
        '--hidden-import=PIL._tkinter_finder',  # Pillow依赖
        '--hidden-import=qfluentwidgets',       # Fluent Widgets
        '--hidden-import=cryptography',         # 加密库
        '--hidden-import=cryptography.hazmat.primitives',
        '--hidden-import=cryptography.hazmat.backends'
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
        'main.py'                       # 主文件
    ]
    
    # 检查图标文件是否存在
    if not os.path.exists('assets/app_icon_pyinstaller.ico'):
        print("警告: 图标文件 assets/app_icon_pyinstaller.ico 不存在，将使用默认图标")
        cmd = [c for c in cmd if not c.startswith('--icon')]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("构建成功！")
        print("exe文件位置: dist/白泽AI.exe")
        
        # 显示文件大小
        exe_path = "dist/白泽AI.exe"
        if os.path.exists(exe_path):
            file_size = os.path.getsize(exe_path) / (1024 * 1024)  # MB
            print(f"文件大小: {file_size:.1f} MB")
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"构建失败: {e}")
        print(f"错误输出: {e.stderr}")
        return False

def main():
    """主函数"""
    print("=== 白泽AI - exe打包程序 ===")
    
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
    success = build_exe()
    
    if success:
        print("\n构建完成！您可以在 dist/ 目录中找到生成的exe文件。")
        print("建议测试exe文件确保所有功能正常工作。")
    else:
        print("\n构建失败，请检查错误信息并修复。")
    
    return success

if __name__ == "__main__":
    main() 