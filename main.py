#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
白泽AI - 智能图片信息提取工具
主启动文件
"""

import sys
import os
import argparse
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt, QTimer
from ui.fluent_main_window import FluentMainWindow
from ui.fluent_splash_screen import BaizeSplashScreen
from ui.fluent_activation_dialog import FluentActivationDialog
from core.license_manager import LicenseManager
from single_instance import get_instance_manager


def get_resource_path(relative_path):
    """获取资源文件的绝对路径，支持PyInstaller打包后的路径"""
    try:
        # PyInstaller创建的临时文件夹路径
        base_path = sys._MEIPASS
    except AttributeError:
        # 在开发环境下，使用当前脚本所在目录
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    return os.path.join(base_path, relative_path)


def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='白泽AI - 智能图片信息提取工具')
    parser.add_argument('file_path', nargs='?', help='要加载的图片文件路径')
    parser.add_argument('--version', action='version', version='3.0.0')
    
    args = parser.parse_args()
    
    # 单实例检查
    instance_manager = get_instance_manager()
    is_first_instance, should_continue = instance_manager.ensure_single_instance(args.file_path)
    
    if not should_continue:
        print("[单实例] 退出当前实例")
        return
    
    # 确保支持高DPI
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    app = QApplication(sys.argv)
    app.setApplicationName("白泽AI")
    app.setApplicationVersion("3.0.0")
    
    # 设置应用图标
    def set_app_icon():
        """设置应用图标"""
        from PyQt5.QtGui import QIcon
        icon_paths = [
            "assets/app_icon_taskbar.ico",         # 主应用图标（任务栏优化ICO）
            "assets/icons/baize_icon_256x256.png", # 256x256 图标（PNG备用）
            "assets/icons/baize_icon_128x128.png", # 128x128 图标
            "assets/icons/baize_icon_64x64.png",   # 64x64 图标
            "assets/icons/baize_icon_48x48.png",   # 48x48 图标
            "assets/icons/baize_icon_32x32.png",   # 32x32 图标
            "assets/app_icon.png",                 # 主应用图标（PNG备用）
            "assets/baize_logo_modern.png",        # 备用大logo
            "assets/baize_logo.png",               # 基础logo
            "assets/baize_icon.png",               # 基础icon
        ]
        
        for relative_path in icon_paths:
            icon_path = get_resource_path(relative_path)
            print(f"尝试加载图标: {icon_path}")
            if os.path.exists(icon_path):
                try:
                    icon = QIcon(icon_path)
                    if not icon.isNull():
                        app.setWindowIcon(icon)
                        print(f"✅ 设置应用图标: {icon_path}")
                        return True
                except Exception as e:
                    print(f"⚠️ 加载应用图标失败 {icon_path}: {e}")
                    continue
            else:
                print(f"❌ 图标文件不存在: {icon_path}")
        
        print("⚠️ 未找到应用图标文件")
        return False
    
    set_app_icon()
    
    # 检查许可证状态
    license_manager = LicenseManager()
    is_license_valid, license_message, license_data = license_manager.check_license_validity()
    
    # 创建并显示启动画面
    splash = BaizeSplashScreen()
    splash.show_splash()
    
    # 创建主窗口 (Fluent Design版本)
    window = FluentMainWindow()
    
    # 如果许可证无效且不在试用期，显示激活对话框
    def check_activation_after_splash():
        if not is_license_valid and not license_data.get("trial", False):
            activation_dialog = FluentActivationDialog(window)
            result = activation_dialog.exec_()
            if result != activation_dialog.Accepted:
                # 用户取消激活，但仍允许在试用期内使用
                license_manager = LicenseManager()
                is_valid, message, data = license_manager.check_license_validity()
                if not is_valid and not data.get("trial", False):
                    # 既没有激活也没有试用期，退出程序
                    app.quit()
                    return
        
        # 设置许可证状态到主窗口
        window.set_license_status(is_license_valid, license_message, license_data)
    
    # 当启动画面完成时显示主窗口
    def on_splash_finished():
        window.show()
        # 检查激活状态
        check_activation_after_splash()
        # 如果通过命令行传入了图片文件路径，则自动加载
        if args.file_path and os.path.exists(args.file_path):
            print(f"从命令行加载图片: {args.file_path}")
            window.business_logic.process_image(args.file_path)
    
    splash.finished.connect(on_splash_finished)
    
    # 如果是第一个实例，启动单实例服务器
    if is_first_instance:
        if instance_manager.start_server():
            server = instance_manager.get_server()
            # 连接新文件接收信号
            server.new_file_received.connect(window.event_handlers.handle_new_file_from_instance)
        
        # 清理函数
        def cleanup():
            instance_manager.cleanup()
        
        app.aboutToQuit.connect(cleanup)
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main() 