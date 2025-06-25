#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Windows右键菜单卸载脚本
移除AI图片工具的右键菜单选项
"""

import sys
import winreg as reg


def uninstall_context_menu():
    """卸载右键菜单"""
    try:
        # 应用程序显示名称
        app_name = "AI图片信息提取工具"
        
        # 需要清理的文件类型
        file_types = [
            '.png',
            '.jpg', 
            '.jpeg',
            '.bmp',
            '.gif',
            '.tiff',
            '.webp'
        ]
        
        removed_count = 0
        
        for file_type in file_types:
            # 注册表键路径
            shell_key_path = f"{file_type}\\shell\\{app_name}"
            
            try:
                # 删除命令键
                try:
                    reg.DeleteKey(reg.HKEY_CLASSES_ROOT, f"{shell_key_path}\\command")
                except FileNotFoundError:
                    pass
                
                # 删除主键
                try:
                    reg.DeleteKey(reg.HKEY_CLASSES_ROOT, shell_key_path)
                    print(f"✓ 已移除 {file_type} 文件的右键菜单")
                    removed_count += 1
                except FileNotFoundError:
                    print(f"- {file_type} 文件没有找到相关的右键菜单项")
                    
            except Exception as e:
                print(f"✗ 移除 {file_type} 文件右键菜单时出错: {e}")
        
        if removed_count > 0:
            print(f"\n🎉 右键菜单卸载完成！成功移除了 {removed_count} 个文件类型的菜单项。")
        else:
            print(f"\n💭 没有找到需要移除的右键菜单项。")
        
    except Exception as e:
        print(f"卸载失败: {e}")
        return False
    
    return True


def main():
    """主函数"""
    print("=" * 60)
    print("AI图片信息提取工具 - Windows右键菜单卸载程序")
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
    
    print("准备卸载右键菜单功能...")
    print("将移除以下文件类型的右键菜单: PNG, JPG, JPEG, BMP, GIF, TIFF, WEBP")
    print()
    
    confirm = input("是否继续卸载? (y/N): ").strip().lower()
    if confirm not in ['y', 'yes', '是']:
        print("卸载已取消")
        return
    
    print()
    print("正在卸载...")
    
    if uninstall_context_menu():
        print()
        print("✅ 卸载完成！")
    else:
        print()
        print("❌ 卸载失败，请检查权限或重试。")
    
    input("\n按回车键退出...")


if __name__ == "__main__":
    main() 