#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fluent Design 设置界面组件
包含应用程序各种设置选项，如右键菜单管理等
"""

import os
import sys
from pathlib import Path

# 平台特定的导入
try:
    import winreg as reg
    WINDOWS_AVAILABLE = True
except ImportError:
    WINDOWS_AVAILABLE = False
    reg = None  # 在非Windows平台上设为None
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QMessageBox, QApplication)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap

from qfluentwidgets import (CardWidget, PrimaryPushButton, PushButton, 
                           BodyLabel, SubtitleLabel, CaptionLabel,
                           InfoBar, InfoBarPosition, MessageBox,
                           SmoothScrollArea, SettingCardGroup, SwitchSettingCard,
                           PushSettingCard, FluentIcon as FIF)

from .fluent_styles import FluentSpacing, FluentColors


class ContextMenuWorker(QThread):
    """右键菜单操作异步工作类"""
    finished = pyqtSignal(bool, str, str)  # 完成信号(成功, 操作类型, 消息)
    
    def __init__(self, operation, parent=None):
        super().__init__(parent)
        self.operation = operation  # 'install' 或 'uninstall'
    
    def run(self):
        """执行右键菜单操作"""
        try:
            if self.operation == 'install':
                success, message = self.install_context_menu()
            elif self.operation == 'uninstall':
                success, message = self.uninstall_context_menu()
            else:
                success, message = False, "未知操作"
            
            self.finished.emit(success, self.operation, message)
            
        except Exception as e:
            self.finished.emit(False, self.operation, f"操作失败: {str(e)}")
    
    def get_app_path(self):
        """获取应用程序路径"""
        if getattr(sys, 'frozen', False):
            # 如果是打包后的exe文件
            return sys.executable
        else:
            # 如果是Python脚本
            script_dir = Path(__file__).parent.parent.absolute()
            return str(script_dir / "main.py")
    
    def install_context_menu(self):
        """安装右键菜单"""
        # 检查是否在Windows平台
        if not WINDOWS_AVAILABLE:
            return False, "右键菜单功能仅在Windows系统上可用"
        
        try:
            app_path = self.get_app_path()
            python_path = sys.executable
            
            # 应用程序显示名称
            app_name = "AI图片信息提取工具"
            menu_text = f"加入到{app_name}"
            
            # 构建命令行
            if app_path.endswith('.exe'):
                command = f'"{app_path}" "%1"'
            else:
                command = f'"{python_path}" "{app_path}" "%1"'
            
            # 基础文件扩展名
            base_file_types = ['.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff', '.webp']
            
            # 常见的程序关联类型（包括WPS等）
            program_file_types = [
                'WPS.PIC.png', 'WPS.PIC.jpg', 'WPS.PIC.jpeg', 'WPS.PIC.bmp', 
                'WPS.PIC.gif', 'WPS.PIC.tiff', 'WPS.PIC.webp',
                'PhotoViewer.FileAssoc.Png', 'PhotoViewer.FileAssoc.Jpeg', 'PhotoViewer.FileAssoc.Jpg',
                'PhotoViewer.FileAssoc.Bmp', 'PhotoViewer.FileAssoc.Gif', 'PhotoViewer.FileAssoc.Tiff',
                'jpegfile', 'pngfile', 'giffile', 'bmpfile', 'tifffile'
            ]
            
            # 合并所有文件类型
            all_file_types = base_file_types + program_file_types
            installed_count = 0
            failed_types = []
            
            for file_type in all_file_types:
                shell_key_path = f"{file_type}\\shell\\{app_name}"
                command_key_path = f"{file_type}\\shell\\{app_name}\\command"
                
                try:
                    # 检查文件类型是否存在
                    try:
                        with reg.OpenKey(reg.HKEY_CLASSES_ROOT, file_type):
                            pass
                    except FileNotFoundError:
                        # 如果是基础扩展名类型，跳过不存在的不算错误
                        if file_type in base_file_types:
                            continue
                        # 如果是程序关联类型，跳过不存在的
                        else:
                            continue
                    
                    # 创建主菜单项
                    with reg.CreateKey(reg.HKEY_CLASSES_ROOT, shell_key_path) as key:
                        reg.SetValue(key, "", reg.REG_SZ, menu_text)
                        reg.SetValueEx(key, "Icon", 0, reg.REG_SZ, app_path)
                        # 设置菜单优先级 - 让菜单显示在顶部而不是"更多选项"中
                        reg.SetValueEx(key, "Position", 0, reg.REG_SZ, "Top")
                        # 移除Extended标志，让菜单直接显示在主菜单中
                        # reg.SetValueEx(key, "Extended", 0, reg.REG_SZ, "")
                    
                    # 创建命令
                    with reg.CreateKey(reg.HKEY_CLASSES_ROOT, command_key_path) as key:
                        reg.SetValue(key, "", reg.REG_SZ, command)
                    
                    installed_count += 1
                    
                except PermissionError:
                    failed_types.append(file_type)
                    print(f"为 {file_type} 文件添加右键菜单失败: 权限不足")
                except Exception as e:
                    failed_types.append(file_type)
                    print(f"为 {file_type} 文件添加右键菜单失败: {e}")
            
            if installed_count > 0:
                return True, f"成功为 {installed_count} 种文件类型添加了右键菜单（包括程序关联类型）"
            elif failed_types:
                # 如果所有类型都因为权限失败，提供解决方案
                return False, (
                    "安装失败：权限不足\n\n"
                    "解决方案：\n"
                    "1. 关闭应用程序\n"
                    "2. 右键点击应用程序图标\n"
                    "3. 选择'以管理员身份运行'\n"
                    "4. 重新尝试安装\n\n"
                    f"失败的文件类型: {', '.join(failed_types[:5])}{'...' if len(failed_types) > 5 else ''}"
                )
            else:
                return False, "没有成功添加任何右键菜单项"
                
        except Exception as e:
            return False, f"安装失败: {str(e)}"
    
    def uninstall_context_menu(self):
        """卸载右键菜单"""
        # 检查是否在Windows平台
        if not WINDOWS_AVAILABLE:
            return False, "右键菜单功能仅在Windows系统上可用"
        
        try:
            app_name = "AI图片信息提取工具"
            
            # 基础文件扩展名
            base_file_types = ['.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff', '.webp']
            
            # 常见的程序关联类型（包括WPS等）
            program_file_types = [
                'WPS.PIC.png', 'WPS.PIC.jpg', 'WPS.PIC.jpeg', 'WPS.PIC.bmp', 
                'WPS.PIC.gif', 'WPS.PIC.tiff', 'WPS.PIC.webp',
                'PhotoViewer.FileAssoc.Png', 'PhotoViewer.FileAssoc.Jpeg', 'PhotoViewer.FileAssoc.Jpg',
                'PhotoViewer.FileAssoc.Bmp', 'PhotoViewer.FileAssoc.Gif', 'PhotoViewer.FileAssoc.Tiff',
                'jpegfile', 'pngfile', 'giffile', 'bmpfile', 'tifffile'
            ]
            
            # 合并所有文件类型
            all_file_types = base_file_types + program_file_types
            removed_count = 0
            
            for file_type in all_file_types:
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
                        removed_count += 1
                    except FileNotFoundError:
                        pass
                        
                except Exception as e:
                    print(f"移除 {file_type} 文件右键菜单时出错: {e}")
            
            if removed_count > 0:
                return True, f"成功移除了 {removed_count} 种文件类型的右键菜单（包括程序关联类型）"
            else:
                return True, "没有找到需要移除的右键菜单项"
                
        except Exception as e:
            return False, f"卸载失败: {str(e)}"


class ContextMenuCard(CardWidget):
    """右键菜单管理卡片"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.worker = None
        self.init_ui()
        self.check_context_menu_status()
    
    def init_ui(self):
        """初始化UI"""
        self.setFixedHeight(180)
        
        # 主布局
        layout = QVBoxLayout()
        layout.setContentsMargins(FluentSpacing.MD, FluentSpacing.MD, 
                                 FluentSpacing.MD, FluentSpacing.MD)
        layout.setSpacing(FluentSpacing.SM)
        
        # 标题区域
        title_layout = QHBoxLayout()
        
        # 图标
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(32, 32)
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.icon_label.setStyleSheet(f"""
            QLabel {{
                border-radius: 8px;
                background-color: {FluentColors.get_color('accent_light')};
                color: white;
                font-size: 16px;
                font-weight: bold;
            }}
        """)
        self.icon_label.setText("🖼️")
        
        # 标题和描述
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        
        self.title_label = SubtitleLabel("Windows右键菜单集成")
        self.desc_label = CaptionLabel("在文件资源管理器中右键图片文件时显示'加入到AI图片信息提取工具'选项，快速添加到历史记录")
        self.desc_label.setStyleSheet(f"color: {FluentColors.get_color('text_secondary')};")
        
        text_layout.addWidget(self.title_label)
        text_layout.addWidget(self.desc_label)
        
        title_layout.addWidget(self.icon_label)
        title_layout.addLayout(text_layout)
        title_layout.addStretch()
        
        # 状态指示
        self.status_label = CaptionLabel()
        self.status_label.setAlignment(Qt.AlignRight)
        title_layout.addWidget(self.status_label)
        
        layout.addLayout(title_layout)
        
        # 详细信息
        self.info_label = BodyLabel()
        self.info_label.setWordWrap(True)
        self.info_label.setStyleSheet(f"color: {FluentColors.get_color('text_tertiary')};")
        layout.addWidget(self.info_label)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        # 管理员重启按钮（仅在没有管理员权限时显示）
        self.admin_restart_btn = PushButton("以管理员身份重启")
        self.admin_restart_btn.clicked.connect(self.restart_as_admin)
        
        self.install_btn = PrimaryPushButton("安装右键菜单")
        self.uninstall_btn = PushButton("卸载右键菜单")
        
        self.install_btn.clicked.connect(self.install_context_menu)
        self.uninstall_btn.clicked.connect(self.uninstall_context_menu)
        
        # 检查是否有管理员权限
        try:
            import ctypes
            if ctypes.windll.shell32.IsUserAnAdmin():
                self.admin_restart_btn.setVisible(False)
            else:
                button_layout.addWidget(self.admin_restart_btn)
        except:
            self.admin_restart_btn.setVisible(False)
        
        button_layout.addWidget(self.install_btn)
        button_layout.addWidget(self.uninstall_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def restart_as_admin(self):
        """以管理员身份重启应用程序"""
        try:
            import ctypes
            import subprocess
            
            # 确认对话框
            confirm_msgbox = MessageBox(
                "重启应用程序",
                "将以管理员身份重新启动应用程序。\n\n"
                "当前的工作将会丢失，确定要继续吗？",
                parent=self.window()
            )
            confirm_msgbox.yesButton.setText("确定重启")
            confirm_msgbox.cancelButton.setText("取消")
            
            result = confirm_msgbox.exec_()
            # 检查用户是否点击了确定按钮
            if not result or result == 0:  # 用户取消或关闭对话框
                return
            
            # 获取当前可执行文件路径
            if getattr(sys, 'frozen', False):
                # 打包后的exe文件
                exe_path = sys.executable
                # 以管理员身份运行exe
                ctypes.windll.shell32.ShellExecuteW(
                    None, "runas", exe_path, "", "", 1
                )
            else:
                # Python脚本
                script_path = str(Path(__file__).parent.parent / "main.py")
                python_path = sys.executable
                # 以管理员身份运行Python脚本
                ctypes.windll.shell32.ShellExecuteW(
                    None, "runas", python_path, f'"{script_path}"', "", 1
                )
            
            # 关闭当前应用程序
            QApplication.quit()
            
        except Exception as e:
            InfoBar.error(
                title="重启失败",
                content=f"无法以管理员身份重启应用程序: {str(e)}",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=5000,
                parent=self.window()
            )
    
    def check_context_menu_status(self):
        """检查右键菜单状态"""
        # 在非Windows平台上，右键菜单功能不可用
        if not WINDOWS_AVAILABLE:
            self.update_status(False, is_non_windows=True)
            return False
            
        try:
            app_name = "AI图片信息提取工具"
            shell_key_path = f".png\\shell\\{app_name}"
            
            try:
                with reg.OpenKey(reg.HKEY_CLASSES_ROOT, shell_key_path) as key:
                    # 如果能打开键，说明已安装
                    self.update_status(True)
                    return True
            except FileNotFoundError:
                self.update_status(False)
                return False
                
        except Exception as e:
            print(f"检查右键菜单状态时出错: {e}")
            self.update_status(False)
            return False
    
    def update_status(self, installed, is_non_windows=False):
        """更新状态显示"""
        # 在非Windows平台上显示特殊信息
        if is_non_windows:
            self.status_label.setText("ℹ️ 不适用")
            self.status_label.setStyleSheet(f"color: {FluentColors.get_color('text_tertiary')};")
            self.info_label.setText("右键菜单功能仅在Windows系统上可用。\n"
                                  "在macOS上，您可以直接拖拽图片文件到应用程序图标来打开文件。")
            self.install_btn.setText("仅Windows可用")
            self.install_btn.setEnabled(False)
            self.uninstall_btn.setEnabled(False)
            return
        
        # 检查管理员权限
        is_admin = False
        try:
            import ctypes
            is_admin = ctypes.windll.shell32.IsUserAnAdmin()
        except:
            pass
        
        if installed:
            self.status_label.setText("✅ 已安装")
            self.status_label.setStyleSheet(f"color: {FluentColors.get_color('success')};")
            self.info_label.setText("支持的格式: PNG, JPG, JPEG, BMP, GIF, TIFF, WEBP\n"
                                  "现在可以右键点击图片文件选择'加入到AI图片信息提取工具'，自动添加到历史记录")
            self.install_btn.setText("重新安装")
            self.uninstall_btn.setEnabled(True)
        else:
            self.status_label.setText("❌ 未安装")
            self.status_label.setStyleSheet(f"color: {FluentColors.get_color('text_tertiary')};")
            
            if is_admin:
                self.info_label.setText("安装后可以在文件资源管理器中右键点击图片文件，"
                                      "选择'加入到AI图片信息提取工具'来快速添加到历史记录")
            else:
                self.info_label.setText("安装后可以在文件资源管理器中右键点击图片文件，"
                                      "选择'加入到AI图片信息提取工具'来快速添加到历史记录\n\n"
                                      "💡 提示：当前未以管理员身份运行，可能无法安装右键菜单")
            
            self.install_btn.setText("安装右键菜单")
            self.uninstall_btn.setEnabled(False)
    
    def install_context_menu(self):
        """安装右键菜单"""
        if self.worker and self.worker.isRunning():
            return
        
        # 检查管理员权限
        try:
            import ctypes
            if not ctypes.windll.shell32.IsUserAnAdmin():
                # 使用更好的弹窗显示
                msgbox = MessageBox(
                    "需要管理员权限",
                    "安装右键菜单需要管理员权限来修改系统注册表。\n\n"
                    "建议操作：\n"
                    "1. 关闭应用程序\n"
                    "2. 右键点击应用程序图标\n"
                    "3. 选择'以管理员身份运行'\n"
                    "4. 重新尝试安装右键菜单\n\n"
                    "或者点击'继续'尝试安装（可能会失败）",
                    parent=self.window()
                )
                msgbox.yesButton.setText("继续")
                msgbox.cancelButton.setText("取消")
                
                result = msgbox.exec_()
                # 检查用户是否点击了确定按钮
                if not result or result == 0:  # 用户取消或关闭对话框
                    return
        except:
            pass
        
        # 禁用按钮
        self.install_btn.setEnabled(False)
        self.install_btn.setText("正在安装...")
        
        # 启动工作线程
        self.worker = ContextMenuWorker('install')
        self.worker.finished.connect(self.on_operation_finished)
        self.worker.start()
    
    def uninstall_context_menu(self):
        """卸载右键菜单"""
        if self.worker and self.worker.isRunning():
            return
        
        # 确认对话框
        confirm_msgbox = MessageBox(
            "确认卸载",
            "确定要卸载右键菜单功能吗？\n\n"
            "卸载后将无法通过右键菜单快速打开图片文件。",
            parent=self.window()
        )
        confirm_msgbox.yesButton.setText("确定卸载")
        confirm_msgbox.cancelButton.setText("取消")
        
        result = confirm_msgbox.exec_()
        # 检查用户是否点击了确定按钮
        if not result or result == 0:  # 用户取消或关闭对话框
            return
        
        # 检查管理员权限
        try:
            import ctypes
            if not ctypes.windll.shell32.IsUserAnAdmin():
                # 使用更好的弹窗显示
                msgbox = MessageBox(
                    "需要管理员权限",
                    "卸载右键菜单需要管理员权限来修改系统注册表。\n\n"
                    "建议操作：\n"
                    "1. 关闭应用程序\n"
                    "2. 右键点击应用程序图标\n"
                    "3. 选择'以管理员身份运行'\n"
                    "4. 重新尝试卸载右键菜单\n\n"
                    "或者点击'继续'尝试卸载（可能会失败）",
                    parent=self.window()
                )
                msgbox.yesButton.setText("继续")
                msgbox.cancelButton.setText("取消")
                
                result = msgbox.exec_()
                # 检查用户是否点击了确定按钮
                if not result or result == 0:  # 用户取消或关闭对话框
                    return
        except:
            pass
        
        # 禁用按钮
        self.uninstall_btn.setEnabled(False)
        self.uninstall_btn.setText("正在卸载...")
        
        # 启动工作线程
        self.worker = ContextMenuWorker('uninstall')
        self.worker.finished.connect(self.on_operation_finished)
        self.worker.start()
    
    def on_operation_finished(self, success, operation, message):
        """操作完成处理"""
        # 恢复按钮状态
        self.install_btn.setEnabled(True)
        self.uninstall_btn.setEnabled(True)
        
        # 更新状态
        if operation == 'install':
            if success:
                self.update_status(True)
                InfoBar.success(
                    title="安装成功",
                    content=message,
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=3000,
                    parent=self.window()
                )
            else:
                InfoBar.error(
                    title="安装失败",
                    content=message,
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=5000,
                    parent=self.window()
                )
        elif operation == 'uninstall':
            if success:
                self.update_status(False)
                InfoBar.success(
                    title="卸载成功",
                    content=message,
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=3000,
                    parent=self.window()
                )
            else:
                InfoBar.error(
                    title="卸载失败",
                    content=message,
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=5000,
                    parent=self.window()
                )


class FluentSettingsWidget(SmoothScrollArea):
    """Fluent Design 设置界面"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        # 主容器
        container = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(FluentSpacing.LG, FluentSpacing.LG, 
                                 FluentSpacing.LG, FluentSpacing.LG)
        layout.setSpacing(FluentSpacing.MD)
        
        # 页面标题
        title_label = SubtitleLabel("应用程序设置")
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {FluentColors.get_color('text_primary')};
                font-weight: 600;
                margin-bottom: {FluentSpacing.SM}px;
            }}
        """)
        layout.addWidget(title_label)
        
        # 系统集成设置组
        integration_group = QWidget()
        integration_layout = QVBoxLayout()
        integration_layout.setSpacing(FluentSpacing.SM)
        
        # 组标题
        group_title = BodyLabel("系统集成")
        group_title.setStyleSheet(f"""
            QLabel {{
                color: {FluentColors.get_color('text_secondary')};
                font-weight: 500;
                margin-bottom: {FluentSpacing.XS}px;
            }}
        """)
        integration_layout.addWidget(group_title)
        
        # 右键菜单管理卡片
        self.context_menu_card = ContextMenuCard()
        integration_layout.addWidget(self.context_menu_card)
        
        integration_group.setLayout(integration_layout)
        layout.addWidget(integration_group)
        
        # 添加弹性空间
        layout.addStretch()
        
        container.setLayout(layout)
        self.setWidget(container)
        
        # 设置滚动属性
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded) 