#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Windows右键菜单功能测试脚本
测试命令行参数传递是否正常工作
"""

import os
import sys
import subprocess
from pathlib import Path


def create_test_image():
    """创建一个测试图片文件"""
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # 创建一个简单的测试图片
        img = Image.new('RGB', (400, 300), color='lightblue')
        draw = ImageDraw.Draw(img)
        
        # 添加一些文本
        try:
            # 尝试使用默认字体
            font = ImageFont.load_default()
        except:
            font = None
            
        text = "测试图片\nTest Image\n用于验证右键菜单功能"
        draw.text((50, 100), text, fill='black', font=font)
        
        # 保存图片
        test_image_path = Path(__file__).parent / "test_image.png"
        img.save(test_image_path)
        
        return str(test_image_path)
        
    except ImportError:
        print("未安装PIL库，创建空的测试图片文件")
        # 如果没有PIL，创建一个空文件作为测试
        test_image_path = Path(__file__).parent / "test_image.png"
        test_image_path.touch()
        return str(test_image_path)


def test_command_line():
    """测试命令行参数功能"""
    print("=" * 60)
    print("Windows右键菜单功能测试")
    print("=" * 60)
    print()
    
    # 创建测试图片
    print("1. 创建测试图片...")
    test_image_path = create_test_image()
    
    if os.path.exists(test_image_path):
        print(f"✓ 测试图片已创建: {test_image_path}")
    else:
        print("✗ 测试图片创建失败")
        return False
    
    # 测试命令行调用
    print("\n2. 测试命令行参数传递...")
    main_py_path = Path(__file__).parent / "main.py"
    
    if not main_py_path.exists():
        print("✗ main.py文件不存在")
        return False
    
    try:
        # 构建命令
        cmd = [sys.executable, str(main_py_path), test_image_path]
        print(f"执行命令: {' '.join(cmd)}")
        
        # 提示用户
        print("\n即将启动应用程序...")
        print("如果应用程序成功启动并加载了测试图片，说明功能正常")
        print("请在应用程序中检查是否加载了测试图片")
        
        confirm = input("\n是否继续测试? (y/N): ").strip().lower()
        if confirm not in ['y', 'yes', '是']:
            print("测试已取消")
            return False
        
        # 启动应用程序
        print("\n正在启动应用程序...")
        subprocess.Popen(cmd)
        
        print("✓ 应用程序已启动")
        print("请检查应用程序是否正确加载了测试图片")
        
        return True
        
    except Exception as e:
        print(f"✗ 启动应用程序失败: {e}")
        return False


def cleanup():
    """清理测试文件"""
    test_image_path = Path(__file__).parent / "test_image.png"
    if test_image_path.exists():
        try:
            test_image_path.unlink()
            print(f"✓ 已清理测试文件: {test_image_path}")
        except Exception as e:
            print(f"✗ 清理测试文件失败: {e}")


def main():
    """主函数"""
    try:
        success = test_command_line()
        
        print("\n" + "=" * 60)
        if success:
            print("✅ 测试完成")
            print("\n如果应用程序成功加载了测试图片，说明右键菜单功能应该可以正常工作")
            print("现在可以运行 install_context_menu.py 来安装右键菜单功能")
        else:
            print("❌ 测试失败")
            print("请检查错误信息并修复问题后重试")
            
        print("=" * 60)
        
        # 询问是否清理测试文件
        cleanup_confirm = input("\n是否删除测试图片文件? (y/N): ").strip().lower()
        if cleanup_confirm in ['y', 'yes', '是']:
            cleanup()
        
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
    except Exception as e:
        print(f"\n测试过程中出现错误: {e}")
    
    input("\n按回车键退出...")


if __name__ == "__main__":
    main() 