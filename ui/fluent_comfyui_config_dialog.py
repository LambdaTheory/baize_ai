#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ComfyUI配置弹窗组件
"""

import json
import os
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QFormLayout, QDialogButtonBox, QGroupBox, QCheckBox)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QIcon

from qfluentwidgets import (LineEdit, PushButton, BodyLabel, SubtitleLabel, 
                           InfoBar, InfoBarPosition, CardWidget, 
                           TransparentPushButton)
from .fluent_styles import FluentColors, FluentSpacing


class FluentComfyUIConfigDialog(QDialog):
    """ComfyUI配置弹窗"""
    
    # 信号：配置保存完成，传递(host, port, save_config)
    config_saved = pyqtSignal(str, int, bool)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.config_file = "data/comfyui_config.json"
        self.init_ui()
        self.load_config()
        
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("ComfyUI连接配置")
        self.setFixedSize(540, 720)
        self.setModal(True)
        
        # 设置窗口样式
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {FluentColors.get_color('bg_primary')};
                border-radius: 12px;
            }}
        """)
        
        # 主布局
        main_layout = QVBoxLayout()
        main_layout.setSpacing(24)  # 适中的区域间距
        main_layout.setContentsMargins(24, 24, 24, 24)
        
        # 标题
        title = SubtitleLabel("🎯 ComfyUI连接配置")
        title.setStyleSheet(f"""
            color: {FluentColors.get_color('text_primary')};
            font-weight: 600;
            margin-bottom: 8px;
        """)
        
        description = BodyLabel("配置您的ComfyUI服务器连接信息")
        description.setStyleSheet(f"""
            color: {FluentColors.get_color('text_secondary')};
            margin-bottom: 16px;
        """)
        
        main_layout.addWidget(title)
        main_layout.addWidget(description)
        
        # 配置卡片
        config_card = CardWidget()
        config_card.setBorderRadius(12)
        config_layout = QVBoxLayout()
        config_layout.setContentsMargins(24, 24, 24, 24)  # 保持合适的边距
        config_layout.setSpacing(20)  # 输入框之间适中的间距
        
        # 服务器地址输入
        host_container = QVBoxLayout()
        host_container.setSpacing(8)  # 确保label和输入框间距合适
        
        host_label = BodyLabel("服务器地址")
        host_label.setStyleSheet(f"""
            color: {FluentColors.get_color('text_primary')};
            font-weight: 500;
            font-size: 14px;
        """)
        
        self.host_edit = LineEdit()
        self.host_edit.setPlaceholderText("例如: 127.0.0.1 或 192.168.1.100")
        self.host_edit.setText("127.0.0.1")
        # 设置输入框尺寸，使用更宽的宽度适配新的对话框尺寸
        self.host_edit.setFixedSize(420, 44)
        # 清除任何可能的样式干扰
        self.host_edit.setStyleSheet("")
        
        host_container.addWidget(host_label)
        host_container.addWidget(self.host_edit)
        config_layout.addLayout(host_container)
        
        # 端口号输入
        port_container = QVBoxLayout()
        port_container.setSpacing(8)  # 确保label和输入框间距合适
        
        port_label = BodyLabel("端口号")
        port_label.setStyleSheet(f"""
            color: {FluentColors.get_color('text_primary')};
            font-weight: 500;
            font-size: 14px;
        """)
        
        self.port_edit = LineEdit()
        self.port_edit.setPlaceholderText("默认: 8188")
        self.port_edit.setText("8188")
        # 设置输入框尺寸，使用更宽的宽度适配新的对话框尺寸
        self.port_edit.setFixedSize(420, 44)
        # 清除任何可能的样式干扰
        self.port_edit.setStyleSheet("")
        
        port_container.addWidget(port_label)
        port_container.addWidget(self.port_edit)
        config_layout.addLayout(port_container)
        
        # 测试连接按钮
        test_layout = QHBoxLayout()
        test_layout.setContentsMargins(0, 16, 0, 0)  # 适中的上边距
        test_layout.addStretch()
        
        self.test_btn = TransparentPushButton("🔍 测试连接")
        self.test_btn.setFixedHeight(36)
        self.test_btn.setStyleSheet(f"""
            TransparentPushButton {{
                border: 2px solid {FluentColors.get_color('primary')};
                border-radius: 8px;
                padding: 8px 16px;
                color: {FluentColors.get_color('primary')};
                font-weight: 500;
                font-size: 14px;
                background-color: transparent;
            }}
            TransparentPushButton:hover {{
                background-color: {FluentColors.get_color('primary')};
                color: white;
            }}
            TransparentPushButton:pressed {{
                background-color: rgba(16, 137, 211, 0.8);
            }}
        """)
        self.test_btn.clicked.connect(self.test_connection)
        
        test_layout.addWidget(self.test_btn)
        config_layout.addLayout(test_layout)
        
        config_card.setLayout(config_layout)
        main_layout.addWidget(config_card)
        
        # 选项区域
        options_card = CardWidget()
        options_card.setBorderRadius(12)
        options_layout = QVBoxLayout()
        options_layout.setContentsMargins(24, 24, 24, 24)  # 保持合适的边距
        
        self.save_config_checkbox = QCheckBox("保存配置信息")
        self.save_config_checkbox.setChecked(True)
        self.save_config_checkbox.setStyleSheet(f"""
            QCheckBox {{
                color: {FluentColors.get_color('text_primary')};
                font-size: 14px;
                font-weight: 500;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border: 2px solid {FluentColors.get_color('border_primary')};
                border-radius: 4px;
                background-color: {FluentColors.get_color('bg_secondary')};
            }}
            QCheckBox::indicator:checked {{
                background-color: {FluentColors.get_color('primary')};
                border-color: {FluentColors.get_color('primary')};
                image: url(:/qfluentwidgets/images/check_box/Accept_white.svg);
            }}
            QCheckBox::indicator:hover {{
                border-color: {FluentColors.get_color('primary')};
            }}
        """)
        
        options_layout.addWidget(self.save_config_checkbox)
        options_card.setLayout(options_layout)
        main_layout.addWidget(options_card)
        
        # 预设配置
        presets_layout = QHBoxLayout()
        presets_layout.setSpacing(12)
        presets_layout.setContentsMargins(0, 16, 0, 0)  # 适中的上边距
        
        preset_label = BodyLabel("快速设置:")
        preset_label.setStyleSheet(f"""
            color: {FluentColors.get_color('text_secondary')};
            font-size: 13px;
        """)
        
        local_btn = TransparentPushButton("本地")
        local_btn.setFixedHeight(32)
        local_btn.clicked.connect(lambda: self.set_preset("127.0.0.1", "8188"))
        
        remote_btn = TransparentPushButton("远程...")
        remote_btn.setFixedHeight(32)
        remote_btn.clicked.connect(self.show_remote_tips)
        
        for btn in [local_btn, remote_btn]:
            btn.setStyleSheet(f"""
                TransparentPushButton {{
                    border: 1px solid {FluentColors.get_color('border_primary')};
                    border-radius: 16px;
                    padding: 6px 16px;
                    background-color: {FluentColors.get_color('bg_secondary')};
                    color: {FluentColors.get_color('text_primary')};
                    font-size: 13px;
                    font-weight: 500;
                }}
                TransparentPushButton:hover {{
                    background-color: {FluentColors.get_color('primary')};
                    color: white;
                    border-color: {FluentColors.get_color('primary')};
                }}
            """)
        
        presets_layout.addWidget(preset_label)
        presets_layout.addWidget(local_btn)
        presets_layout.addWidget(remote_btn)
        presets_layout.addStretch()
        
        main_layout.addLayout(presets_layout)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.setSpacing(16)
        button_layout.setContentsMargins(0, 24, 0, 0)  # 适中的上边距
        
        self.cancel_btn = PushButton("取消")
        self.cancel_btn.setFixedHeight(40)
        self.cancel_btn.setFixedWidth(80)
        self.cancel_btn.setStyleSheet(f"""
            PushButton {{
                background-color: {FluentColors.get_color('bg_secondary')};
                color: {FluentColors.get_color('text_primary')};
                border: 2px solid {FluentColors.get_color('border_primary')};
                border-radius: 8px;
                font-weight: 500;
                font-size: 14px;
            }}
            PushButton:hover {{
                border-color: {FluentColors.get_color('primary')};
                background-color: {FluentColors.get_color('bg_primary')};
            }}
        """)
        self.cancel_btn.clicked.connect(self.reject)
        
        self.ok_btn = PushButton("确定")
        self.ok_btn.setFixedHeight(40)
        self.ok_btn.setFixedWidth(80)
        self.ok_btn.setStyleSheet(f"""
            PushButton {{
                background-color: {FluentColors.get_color('primary')};
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: 600;
                font-size: 14px;
            }}
            PushButton:hover {{
                background-color: rgba(16, 137, 211, 0.8);
            }}
            PushButton:pressed {{
                background-color: rgba(16, 137, 211, 0.6);
            }}
        """)
        self.ok_btn.clicked.connect(self.accept_config)
        
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_btn)
        button_layout.addWidget(self.ok_btn)
        
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)
    
    def set_preset(self, host, port):
        """设置预设配置"""
        self.host_edit.setText(host)
        self.port_edit.setText(port)
    
    def show_remote_tips(self):
        """显示远程配置提示"""
        InfoBar.info(
            title="远程连接提示",
            content="请确保远程ComfyUI启用了API访问，并且网络可达",
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=3000,
            parent=self
        )
    
    def test_connection(self):
        """测试连接"""
        host = self.host_edit.text().strip()
        port = self.port_edit.text().strip()
        
        if not host or not port:
            InfoBar.warning(
                title="配置错误",
                content="请填写完整的服务器地址和端口号",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=2000,
                parent=self
            )
            return
        
        try:
            port_num = int(port)
            
            # 导入ComfyUI集成器并测试连接
            from core.comfyui_integration import ComfyUIIntegration
            
            # 创建临时集成器实例进行测试
            test_integration = ComfyUIIntegration(host=host, port=port_num)
            is_running, message = test_integration.check_comfyui_status()
            
            if is_running:
                InfoBar.success(
                    title="连接成功",
                    content=f"成功连接到ComfyUI: {message}",
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=3000,
                    parent=self
                )
            else:
                InfoBar.error(
                    title="连接失败",
                    content=f"无法连接到ComfyUI: {message}",
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=4000,
                    parent=self
                )
                
        except ValueError:
            InfoBar.error(
                title="配置错误",
                content="端口号必须是有效的数字",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=2000,
                parent=self
            )
        except Exception as e:
            InfoBar.error(
                title="测试失败",
                content=f"测试连接时出错: {str(e)}",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
    
    def accept_config(self):
        """确认配置"""
        host = self.host_edit.text().strip()
        port = self.port_edit.text().strip()
        
        if not host or not port:
            InfoBar.warning(
                title="配置错误",
                content="请填写完整的服务器地址和端口号",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=2000,
                parent=self
            )
            return
        
        try:
            port_num = int(port)
            save_config = self.save_config_checkbox.isChecked()
            
            # 保存配置
            if save_config:
                self.save_config_to_file(host, port_num)
            
            # 发射信号
            self.config_saved.emit(host, port_num, save_config)
            self.accept()
            
        except ValueError:
            InfoBar.error(
                title="配置错误",
                content="端口号必须是有效的数字",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=2000,
                parent=self
            )
    
    def load_config(self):
        """加载保存的配置"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    
                self.host_edit.setText(config.get('host', '127.0.0.1'))
                self.port_edit.setText(str(config.get('port', 8188)))
                
        except Exception as e:
            print(f"加载ComfyUI配置失败: {e}")
    
    def save_config_to_file(self, host, port):
        """保存配置到文件"""
        try:
            # 确保data目录存在
            os.makedirs('data', exist_ok=True)
            
            config = {
                'host': host,
                'port': port,
                'last_updated': __import__('datetime').datetime.now().isoformat()
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"保存ComfyUI配置失败: {e}") 