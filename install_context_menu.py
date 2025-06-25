#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Windows右键菜单安装脚本
为PNG图片文件添加"使用AI图片工具打开"右键菜单选项
"""

import os
import sys
import winreg as reg
from pathlib import Path


def get_app_path():
    """获取应用程序路径"""
    if getattr(sys, 'frozen', False):
        # 如果是打包后的exe文件
        app_path = sys.executable
    else:
        # 如果是Python脚本
        script_dir = Path(__file__).parent.absolute()
        app_path = str(script_dir / "main.py")
    return app_path


def get_python_path():
    """获取Python解释器路径"""
    return sys.executable


def install_context_menu():
    """安装右键菜单"""
    try:
        app_path = get_app_path()
        python_path = get_python_path()
        
        # 应用程序显示名称
        app_name = "AI图片信息提取工具"
        menu_text = f"使用{app_name}打开"
        
        # 构建命令行
        if app_path.endswith('.exe'):
            # 如果是打包的exe文件
            command = f'"{app_path}" "%1"'
        else:
            # 如果是Python脚本
            command = f'"{python_path}" "{app_path}" "%1"'
        
        print(f"安装路径: {app_path}")
        print(f"Python路径: {python_path}")
        print(f"执行命令: {command}")
        
        # 为PNG文件类型添加右键菜单
        file_types = [
            '.png',
            '.jpg', 
            '.jpeg',
            '.bmp',
            '.gif',
            '.tiff',
            '.webp'
        ]
        
        for file_type in file_types:
            # 创建或打开文件类型的shell键
            shell_key_path = f"{file_type}\\shell\\{app_name}"
            command_key_path = f"{file_type}\\shell\\{app_name}\\command"
            
            try:
                # 创建主菜单项
                with reg.CreateKey(reg.HKEY_CLASSES_ROOT, shell_key_path) as key:
                    reg.SetValue(key, "", reg.REG_SZ, menu_text)
                    reg.SetValueEx(key, "Icon", 0, reg.REG_SZ, app_path)
                
                # 创建命令
                with reg.CreateKey(reg.HKEY_CLASSES_ROOT, command_key_path) as key:
                    reg.SetValue(key, "", reg.REG_SZ, command)
                
                print(f"✓ 已为 {file_type} 文件添加右键菜单")
                
            except Exception as e:
                print(f"✗ 为 {file_type} 文件添加右键菜单失败: {e}")
        
        print(f"\n🎉 右键菜单安装完成！")
        print(f"现在你可以右键点击支持的图片文件，选择'{menu_text}'来快速打开应用程序。")
        
    except Exception as e:
        print(f"安装失败: {e}")
        return False
    
    return True


def main():
    """主函数"""
    print("=" * 60)
    print("AI图片信息提取工具 - Windows右键菜单安装程序")
    print("=" * 60)
    print()
    
    # 检查是否以管理员权限运行
    try:
        import ctypes
        if not ctypes.windll.shell32.IsUserAnAdmin():
            print("⚠️  警告: 建议以管理员权限运行此脚本以确保注册表修改成功")
            print("请右键点击命令提示符，选择'以管理员身份运行'，然后再执行此脚本")
            print()
    except:
        pass
    
    print("准备安装右键菜单功能...")
    print("支持的文件类型: PNG, JPG, JPEG, BMP, GIF, TIFF, WEBP")
    print()
    
    confirm = input("是否继续安装? (y/N): ").strip().lower()
    if confirm not in ['y', 'yes', '是']:
        print("安装已取消")
        return
    
    print()
    print("正在安装...")
    
    if install_context_menu():
        print()
        print("✅ 安装成功！现在可以通过右键菜单快速打开图片文件了。")
    else:
        print()
        print("❌ 安装失败，请检查权限或重试。")
    
    input("\n按回车键退出...")


if __name__ == "__main__":
    main() 