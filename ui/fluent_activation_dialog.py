#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fluent Design 激活码对话框
"""

import os
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QPushButton, QTextEdit, QFrame, QSpacerItem,
                            QSizePolicy, QWidget, QGridLayout, QTableWidget, QTableWidgetItem,
                            QHeaderView)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QPixmap, QIcon, QColor

from qfluentwidgets import (CardWidget, BodyLabel, TitleLabel, PrimaryPushButton,
                           PushButton, LineEdit, TextEdit, InfoBar, InfoBarPosition,
                           MessageBox, ProgressBar, FluentIcon, Theme, setTheme)

from .fluent_styles import FluentTheme, FluentIcons, FluentColors, FluentSpacing
from core.license_manager import LicenseManager


class FluentActivationDialog(QDialog):
    """Fluent Design 激活码对话框"""
    
    activation_completed = pyqtSignal(bool, str)  # 激活完成信号(成功, 消息)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.license_manager = LicenseManager()
        self.init_ui()
        self.setup_connections()
        self.load_license_info()
        
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("白泽AI - 软件激活")
        self.setFixedSize(520, 600)
        self.setModal(True)
        
        # 主布局
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(FluentSpacing.LG, FluentSpacing.LG, 
                                     FluentSpacing.LG, FluentSpacing.LG)
        main_layout.setSpacing(FluentSpacing.MD)
        
        # 标题区域
        self.create_header_section(main_layout)
        
        # 许可证状态卡片
        self.create_license_status_card(main_layout)
        
        # 激活码输入卡片
        self.create_activation_card(main_layout)
        
        # 硬件指纹卡片
        self.create_hardware_info_card(main_layout)
        
        # 按钮区域
        self.create_button_section(main_layout)
        
        self.setLayout(main_layout)
        self.apply_styles()
    
    def create_header_section(self, parent_layout):
        """创建标题区域"""
        header_card = CardWidget()
        header_layout = QVBoxLayout()
        header_layout.setContentsMargins(FluentSpacing.LG, FluentSpacing.LG, 
                                       FluentSpacing.LG, FluentSpacing.LG)
        
        # 应用图标和标题
        title_layout = QHBoxLayout()
        
        # 图标
        icon_label = QLabel()
        icon_label.setFixedSize(48, 48)
        try:
            icon_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'baize_icon.png')
            if os.path.exists(icon_path):
                pixmap = QPixmap(icon_path)
                scaled_pixmap = pixmap.scaled(48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                icon_label.setPixmap(scaled_pixmap)
        except:
            icon_label.setText("🔑")
            icon_label.setStyleSheet("font-size: 24px;")
        
        # 标题文本
        title_text_layout = QVBoxLayout()
        title_text_layout.setSpacing(FluentSpacing.XS)
        
        self.title_label = TitleLabel("白泽AI 软件激活")
        self.subtitle_label = BodyLabel("请输入激活码以继续使用完整功能")
        self.subtitle_label.setStyleSheet(f"color: {FluentColors.get_color('text_secondary')};")
        
        title_text_layout.addWidget(self.title_label)
        title_text_layout.addWidget(self.subtitle_label)
        
        title_layout.addWidget(icon_label)
        title_layout.addLayout(title_text_layout)
        title_layout.addStretch()
        
        header_layout.addLayout(title_layout)
        header_card.setLayout(header_layout)
        parent_layout.addWidget(header_card)
    
    def create_license_status_card(self, parent_layout):
        """创建许可证状态卡片"""
        self.status_card = CardWidget()
        status_layout = QVBoxLayout()
        status_layout.setContentsMargins(FluentSpacing.LG, FluentSpacing.LG, 
                                       FluentSpacing.LG, FluentSpacing.LG)
        
        # 状态标题
        status_title = BodyLabel("当前状态")
        status_title.setStyleSheet("font-weight: 600;")
        status_layout.addWidget(status_title)
        
        # 状态信息
        self.status_label = BodyLabel("检查中...")
        self.status_label.setWordWrap(True)
        status_layout.addWidget(self.status_label)
        
        self.status_card.setLayout(status_layout)
        parent_layout.addWidget(self.status_card)
    
    def create_activation_card(self, parent_layout):
        """创建激活码输入卡片"""
        activation_card = CardWidget()
        activation_layout = QVBoxLayout()
        activation_layout.setContentsMargins(FluentSpacing.LG, FluentSpacing.LG, 
                                           FluentSpacing.LG, FluentSpacing.LG)
        activation_layout.setSpacing(FluentSpacing.MD)
        
        # 激活码输入标题
        activation_title = BodyLabel("激活码")
        activation_title.setStyleSheet("font-weight: 600;")
        activation_layout.addWidget(activation_title)
        
        # 激活码输入框
        self.activation_input = LineEdit()
        self.activation_input.setPlaceholderText("请输入Creem许可证密钥")
        self.activation_input.textChanged.connect(self.on_activation_code_changed)
        activation_layout.addWidget(self.activation_input)
        
        # 激活码格式说明
        format_label = BodyLabel("支持格式：XXXXX-XXXXX-XXXXX-XXXXX")
        format_label.setStyleSheet(f"color: {FluentColors.get_color('text_tertiary')}; font-size: 12px;")
        activation_layout.addWidget(format_label)
        
        # 购买链接
        purchase_layout = QHBoxLayout()
        purchase_layout.setSpacing(FluentSpacing.SM)
        
        purchase_label = BodyLabel("还没有激活码？")
        purchase_label.setStyleSheet(f"color: {FluentColors.get_color('text_secondary')};")
        
        self.purchase_button = PushButton("立即购买")
        self.purchase_button.clicked.connect(self.open_purchase_page)
        self.purchase_button.setMinimumWidth(80)
        self.purchase_button.setMaximumWidth(120)
        
        # 重试计数器
        self.purchase_retry_count = 0
        
        purchase_layout.addWidget(purchase_label)
        purchase_layout.addWidget(self.purchase_button)
        purchase_layout.addStretch()
        
        activation_layout.addLayout(purchase_layout)
        
        activation_card.setLayout(activation_layout)
        parent_layout.addWidget(activation_card)
    
    def create_hardware_info_card(self, parent_layout):
        """创建硬件信息卡片"""
        hardware_card = CardWidget()
        hardware_layout = QVBoxLayout()
        hardware_layout.setContentsMargins(FluentSpacing.LG, FluentSpacing.LG, 
                                         FluentSpacing.LG, FluentSpacing.LG)
        
        # 硬件信息标题
        hardware_title = BodyLabel("设备信息")
        hardware_title.setStyleSheet("font-weight: 600;")
        hardware_layout.addWidget(hardware_title)
        
        # 硬件指纹
        fingerprint_layout = QHBoxLayout()
        fingerprint_label = BodyLabel("硬件指纹：")
        
        self.fingerprint_value = BodyLabel("获取中...")
        self.fingerprint_value.setStyleSheet(f"color: {FluentColors.get_color('text_secondary')}; font-family: 'Consolas', monospace;")
        
        self.copy_fingerprint_btn = PushButton("复制")
        self.copy_fingerprint_btn.clicked.connect(self.copy_hardware_fingerprint)
        self.copy_fingerprint_btn.setMaximumWidth(60)
        
        fingerprint_layout.addWidget(fingerprint_label)
        fingerprint_layout.addWidget(self.fingerprint_value)
        fingerprint_layout.addWidget(self.copy_fingerprint_btn)
        fingerprint_layout.addStretch()
        
        hardware_layout.addLayout(fingerprint_layout)
        
        # 硬件指纹说明
        fingerprint_help = BodyLabel("激活码将绑定到当前设备，转移到其他设备需要重新激活")
        fingerprint_help.setStyleSheet(f"color: {FluentColors.get_color('text_tertiary')}; font-size: 11px;")
        fingerprint_help.setWordWrap(True)
        hardware_layout.addWidget(fingerprint_help)
        
        hardware_card.setLayout(hardware_layout)
        parent_layout.addWidget(hardware_card)
    
    def create_button_section(self, parent_layout):
        """创建按钮区域"""
        button_layout = QHBoxLayout()
        
        # 取消按钮
        self.cancel_button = PushButton("稍后激活")
        self.cancel_button.clicked.connect(self.reject)
        
        # 激活按钮
        self.activate_button = PrimaryPushButton("立即激活")
        self.activate_button.clicked.connect(self.activate_license)
        self.activate_button.setEnabled(False)
        
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.activate_button)
        
        parent_layout.addLayout(button_layout)
    
    def setup_connections(self):
        """设置信号连接"""
        pass
    
    def apply_styles(self):
        """应用样式"""
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {FluentColors.get_color('bg_primary')};
                border-radius: 12px;
            }}
        """)
    
    def load_license_info(self):
        """加载许可证信息"""
        try:
            # 获取硬件指纹
            hw_fingerprint = self.license_manager._get_hardware_fingerprint()
            self.fingerprint_value.setText(hw_fingerprint)
            
            # 检查许可证状态
            license_info = self.license_manager.get_license_info()
            is_valid = license_info.get("is_valid", False)
            message = license_info.get("message", "未知状态")
            data = license_info.get("data", {})
            
            if is_valid:
                if data.get("trial", False):
                    # 试用期
                    remaining_days = data.get("remaining_days", 0)
                    self.status_label.setText(f"✅ 试用期 - 剩余 {remaining_days} 天")
                    self.status_card.setStyleSheet(f"""
                        CardWidget {{
                            background-color: rgba(34, 197, 94, 0.1);
                            border: 1px solid rgba(34, 197, 94, 0.3);
                        }}
                    """)
                else:
                    # 已激活
                    self.status_label.setText("✅ 已激活 - 感谢您的支持！")
                    self.status_card.setStyleSheet(f"""
                        CardWidget {{
                            background-color: rgba(34, 197, 94, 0.1);
                            border: 1px solid rgba(34, 197, 94, 0.3);
                        }}
                    """)
                    self.activation_input.setEnabled(False)
                    self.activate_button.setText("已激活")
                    self.activate_button.setEnabled(False)
            else:
                # 未激活或过期
                self.status_label.setText(f"❌ {message}")
                self.status_card.setStyleSheet(f"""
                    CardWidget {{
                        background-color: rgba(239, 68, 68, 0.1);
                        border: 1px solid rgba(239, 68, 68, 0.3);
                    }}
                """)
        except Exception as e:
            self.status_label.setText(f"⚠️ 状态检查失败: {str(e)}")
    
    def on_activation_code_changed(self, text):
        """激活码输入变化"""
        # Creem格式验证：XXXXX-XXXXX-XXXXX-XXXXX-XXXXX
        is_creem_format = (
            len(text) == 29 and  # 5个5字符段 + 4个连字符
            text.count("-") == 4 and
            all(c.isalnum() or c == '-' for c in text) and  # 只允许字母数字和连字符
            all(len(part) == 5 for part in text.split("-"))  # 每段都是5个字符
        )
        
        # 基本长度检查（至少10个字符，避免过短的输入就启用按钮）
        is_min_length = len(text.strip()) >= 10
        
        # 启用按钮条件：符合Creem格式或达到最小长度要求
        self.activate_button.setEnabled(is_creem_format or is_min_length)
    
    def activate_license(self):
        """激活许可证"""
        activation_code = self.activation_input.text().strip()
        if not activation_code:
            InfoBar.warning("提示", "请输入激活码", parent=self)
            return
        
        # 禁用按钮防止重复点击
        self.activate_button.setEnabled(False)
        self.activate_button.setText("激活中...")
        
        try:
            success, message = self.license_manager.activate_license(activation_code)
            
            if success:
                InfoBar.success("成功", message, parent=self)
                self.activation_completed.emit(True, message)
                QTimer.singleShot(1500, self.accept)  # 延迟关闭对话框
            else:
                InfoBar.error("失败", message, parent=self)
                self.activate_button.setEnabled(True)
                self.activate_button.setText("立即激活")
        except Exception as e:
            InfoBar.error("错误", f"激活过程中发生错误：{str(e)}", parent=self)
            self.activate_button.setEnabled(True)
            self.activate_button.setText("立即激活")
    
    def copy_hardware_fingerprint(self):
        """复制硬件指纹"""
        from PyQt5.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        clipboard.setText(self.fingerprint_value.text())
        InfoBar.success("提示", "硬件指纹已复制到剪贴板", parent=self)
    
    def open_purchase_page(self):
        """打开购买页面"""
        try:
            from core.payment_manager import PaymentManager
            
            # 禁用按钮防止重复点击
            self.purchase_button.setEnabled(False)
            self.purchase_button.setText("创建中...")
            
            # 获取硬件指纹
            hardware_fingerprint = self.license_manager._get_hardware_fingerprint()
            
            # 创建支付管理器
            payment_manager = PaymentManager()
            
            # 创建支付会话
            success, message, checkout_url = payment_manager.create_checkout_session(hardware_fingerprint)
            
            if success and checkout_url:
                # 重置重试计数器
                self.purchase_retry_count = 0
                
                # 使用系统默认浏览器打开支付页面
                import webbrowser
                webbrowser.open(checkout_url)
                
                # 显示信息提示
                InfoBar.success(
                    title="支付页面已打开",
                    content="请在浏览器中完成支付，支付完成后点击'检查支付状态'按钮",
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=5000,
                    parent=self
                )
                
                # 显示支付完成确认弹窗
                self.show_payment_completion_dialog()
                
            else:
                # 增加重试计数
                self.purchase_retry_count += 1
                
                # 根据错误类型提供不同的处理建议
                if "配置错误" in message or "认证失败" in message:
                    InfoBar.error(
                        title="支付系统故障",
                        content=f"{message}\n\n您也可以尝试：\n1. 联系客服获取人工激活码\n2. 稍后重试",
                        orient=Qt.Horizontal,
                        isClosable=True,
                        position=InfoBarPosition.TOP,
                        duration=8000,  # 增加显示时间
                        parent=self
                    )
                elif "服务器内部错误" in message:
                    retry_text = f" (已重试{self.purchase_retry_count}次)" if self.purchase_retry_count > 1 else ""
                    InfoBar.warning(
                        title="服务器暂时不可用",
                        content=f"{message}{retry_text}\n\n请稍后重试，或联系客服获取帮助。",
                        orient=Qt.Horizontal,
                        isClosable=True,
                        position=InfoBarPosition.TOP,
                        duration=6000,
                        parent=self
                    )
                else:
                    InfoBar.error(
                        title="创建支付会话失败",
                        content=f"无法创建支付链接: {message}",
                        orient=Qt.Horizontal,
                        isClosable=True,
                        position=InfoBarPosition.TOP,
                        duration=5000,
                        parent=self
                    )
                
        except Exception as e:
            InfoBar.error(
                title="打开支付页面失败",
                content=f"无法打开支付页面: {str(e)}",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=5000,
                parent=self
            )
        finally:
            # 重新启用按钮
            self.purchase_button.setEnabled(True)
            self.purchase_button.setText("立即购买")
    
    def show_payment_completion_dialog(self):
        """显示支付完成确认弹窗"""
        msgbox = MessageBox(
            title="支付完成确认",
            content="请确认您是否已经完成支付？\n\n如果已完成支付，您将在Creem的订单确认页面或邮件中看到许可证密钥，请复制并粘贴到激活码输入框中。",
            parent=self
        )
        
        # 添加自定义按钮
        msgbox.yesButton.setText("已完成支付")
        msgbox.cancelButton.setText("取消")
        
        if msgbox.exec_() == msgbox.Accepted:
            # 用户确认已完成支付，显示许可证密钥输入提示
            InfoBar.info(
                title="请输入许可证密钥",
                content="请在上方激活码输入框中输入您从Creem获得的许可证密钥，然后点击'立即激活'按钮。\n\nCreem许可证密钥格式通常为：XXXXX-XXXXX-XXXXX-XXXXX-XXXXX",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=10000,  # 显示10秒
                parent=self
            )
            
            # 高亮激活码输入框
            self.activation_input.setFocus()
    

class FeatureComparisonDialog(QDialog):
    """功能对比对话框"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("白泽AI - 软件激活")
        self.setFixedSize(520, 600)
        self.setModal(True)
        
        # 主布局
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(FluentSpacing.LG, FluentSpacing.LG, 
                                     FluentSpacing.LG, FluentSpacing.LG)
        main_layout.setSpacing(FluentSpacing.MD)
        
        # 标题区域
        self.create_header_section(main_layout)
        
        # 许可证状态卡片
        self.create_license_status_card(main_layout)
        
        # 激活码输入卡片
        self.create_activation_card(main_layout)
        
        # 硬件指纹卡片
        self.create_hardware_info_card(main_layout)
        
        # 按钮区域
        self.create_button_section(main_layout)
        
        self.setLayout(main_layout)
        self.apply_styles()

    def create_header_section(self, parent_layout):
        """创建标题区域"""
        header_card = CardWidget()
        header_layout = QVBoxLayout()
        header_layout.setContentsMargins(FluentSpacing.LG, FluentSpacing.LG, 
                                       FluentSpacing.LG, FluentSpacing.LG)
        
        # 应用图标和标题
        title_layout = QHBoxLayout()
        
        # 图标
        icon_label = QLabel()
        icon_label.setFixedSize(48, 48)
        try:
            icon_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'baize_icon.png')
            if os.path.exists(icon_path):
                pixmap = QPixmap(icon_path)
                scaled_pixmap = pixmap.scaled(48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                icon_label.setPixmap(scaled_pixmap)
        except:
            icon_label.setText("🔑")
            icon_label.setStyleSheet("font-size: 24px;")
        
        # 标题文本
        title_text_layout = QVBoxLayout()
        title_text_layout.setSpacing(FluentSpacing.XS)
        
        self.title_label = TitleLabel("白泽AI 软件激活")
        self.subtitle_label = BodyLabel("请输入激活码以继续使用完整功能")
        self.subtitle_label.setStyleSheet(f"color: {FluentColors.get_color('text_secondary')};")
        
        title_text_layout.addWidget(self.title_label)
        title_text_layout.addWidget(self.subtitle_label)
        
        title_layout.addWidget(icon_label)
        title_layout.addLayout(title_text_layout)
        title_layout.addStretch()
        
        header_layout.addLayout(title_layout)
        header_card.setLayout(header_layout)
        parent_layout.addWidget(header_card)
    
    def create_license_status_card(self, parent_layout):
        """创建许可证状态卡片"""
        self.status_card = CardWidget()
        status_layout = QVBoxLayout()
        status_layout.setContentsMargins(FluentSpacing.LG, FluentSpacing.LG, 
                                       FluentSpacing.LG, FluentSpacing.LG)
        
        # 状态标题
        status_title = BodyLabel("当前状态")
        status_title.setStyleSheet("font-weight: 600;")
        status_layout.addWidget(status_title)
        
        # 状态信息
        self.status_label = BodyLabel("检查中...")
        self.status_label.setWordWrap(True)
        status_layout.addWidget(self.status_label)
        
        self.status_card.setLayout(status_layout)
        parent_layout.addWidget(self.status_card)
    
    def create_activation_card(self, parent_layout):
        """创建激活码输入卡片"""
        activation_card = CardWidget()
        activation_layout = QVBoxLayout()
        activation_layout.setContentsMargins(FluentSpacing.LG, FluentSpacing.LG, 
                                           FluentSpacing.LG, FluentSpacing.LG)
        activation_layout.setSpacing(FluentSpacing.MD)
        
        # 激活码输入标题
        activation_title = BodyLabel("激活码")
        activation_title.setStyleSheet("font-weight: 600;")
        activation_layout.addWidget(activation_title)
        
        # 激活码输入框
        self.activation_input = LineEdit()
        self.activation_input.setPlaceholderText("请输入Creem许可证密钥")
        self.activation_input.textChanged.connect(self.on_activation_code_changed)
        activation_layout.addWidget(self.activation_input)
        
        # 激活码格式说明
        format_label = BodyLabel("支持格式：XXXXX-XXXXX-XXXXX-XXXXX")
        format_label.setStyleSheet(f"color: {FluentColors.get_color('text_tertiary')}; font-size: 12px;")
        activation_layout.addWidget(format_label)
        
        # 购买链接
        purchase_layout = QHBoxLayout()
        purchase_layout.setSpacing(FluentSpacing.SM)
        
        purchase_label = BodyLabel("还没有激活码？")
        purchase_label.setStyleSheet(f"color: {FluentColors.get_color('text_secondary')};")
        
        self.purchase_button = PushButton("立即购买")
        self.purchase_button.clicked.connect(self.open_purchase_page)
        self.purchase_button.setMinimumWidth(80)
        self.purchase_button.setMaximumWidth(120)
        
        # 重试计数器
        self.purchase_retry_count = 0
        
        purchase_layout.addWidget(purchase_label)
        purchase_layout.addWidget(self.purchase_button)
        purchase_layout.addStretch()
        
        activation_layout.addLayout(purchase_layout)
        
        activation_card.setLayout(activation_layout)
        parent_layout.addWidget(activation_card)
    
    def create_hardware_info_card(self, parent_layout):
        """创建硬件信息卡片"""
        hardware_card = CardWidget()
        hardware_layout = QVBoxLayout()
        hardware_layout.setContentsMargins(FluentSpacing.LG, FluentSpacing.LG, 
                                         FluentSpacing.LG, FluentSpacing.LG)
        
        # 硬件信息标题
        hardware_title = BodyLabel("设备信息")
        hardware_title.setStyleSheet("font-weight: 600;")
        hardware_layout.addWidget(hardware_title)
        
        # 硬件指纹
        fingerprint_layout = QHBoxLayout()
        fingerprint_label = BodyLabel("硬件指纹：")
        
        self.fingerprint_value = BodyLabel("获取中...")
        self.fingerprint_value.setStyleSheet(f"color: {FluentColors.get_color('text_secondary')}; font-family: 'Consolas', monospace;")
        
        self.copy_fingerprint_btn = PushButton("复制")
        self.copy_fingerprint_btn.clicked.connect(self.copy_hardware_fingerprint)
        self.copy_fingerprint_btn.setMaximumWidth(60)
        
        fingerprint_layout.addWidget(fingerprint_label)
        fingerprint_layout.addWidget(self.fingerprint_value)
        fingerprint_layout.addWidget(self.copy_fingerprint_btn)
        fingerprint_layout.addStretch()
        
        hardware_layout.addLayout(fingerprint_layout)
        
        # 硬件指纹说明
        fingerprint_help = BodyLabel("激活码将绑定到当前设备，转移到其他设备需要重新激活")
        fingerprint_help.setStyleSheet(f"color: {FluentColors.get_color('text_tertiary')}; font-size: 11px;")
        fingerprint_help.setWordWrap(True)
        hardware_layout.addWidget(fingerprint_help)
        
        hardware_card.setLayout(hardware_layout)
        parent_layout.addWidget(hardware_card)
    
    def create_button_section(self, parent_layout):
        """创建按钮区域"""
        button_layout = QHBoxLayout()
        
        # 取消按钮
        self.cancel_button = PushButton("稍后激活")
        self.cancel_button.clicked.connect(self.reject)
        
        # 激活按钮
        self.activate_button = PrimaryPushButton("立即激活")
        self.activate_button.clicked.connect(self.activate_license)
        self.activate_button.setEnabled(False)
        
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.activate_button)
        
        parent_layout.addLayout(button_layout)
    
    def apply_styles(self):
        """应用样式"""
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {FluentColors.get_color('bg_primary')};
                border-radius: 8px;
            }}
            QTableWidget {{
                background-color: transparent;
                border: none;
            }}
            QHeaderView::section {{
                background-color: {FluentColors.get_color('bg_tertiary')};
                color: {FluentColors.get_color('text_primary')};
                border: none;
                padding: 4px;
            }}
            QTableWidget::item {{
                padding: 5px;
            }}
        """)
    
    def on_activation_code_changed(self, text):
        """激活码输入变化"""
        # Creem格式验证：XXXXX-XXXXX-XXXXX-XXXXX-XXXXX
        is_creem_format = (
            len(text) == 29 and  # 5个5字符段 + 4个连字符
            text.count("-") == 4 and
            all(c.isalnum() or c == '-' for c in text) and  # 只允许字母数字和连字符
            all(len(part) == 5 for part in text.split("-"))  # 每段都是5个字符
        )
        
        # 基本长度检查（至少10个字符，避免过短的输入就启用按钮）
        is_min_length = len(text.strip()) >= 10
        
        # 启用按钮条件：符合Creem格式或达到最小长度要求
        self.activate_button.setEnabled(is_creem_format or is_min_length)
    
    def activate_license(self):
        """激活许可证"""
        activation_code = self.activation_input.text().strip()
        if not activation_code:
            InfoBar.warning("提示", "请输入激活码", parent=self)
            return
        
        # 禁用按钮防止重复点击
        self.activate_button.setEnabled(False)
        self.activate_button.setText("激活中...")
        
        try:
            success, message = self.license_manager.activate_license(activation_code)
            
            if success:
                InfoBar.success("成功", message, parent=self)
                self.activation_completed.emit(True, message)
                QTimer.singleShot(1500, self.accept)  # 延迟关闭对话框
            else:
                InfoBar.error("失败", message, parent=self)
                self.activate_button.setEnabled(True)
                self.activate_button.setText("立即激活")
        except Exception as e:
            InfoBar.error("错误", f"激活过程中发生错误：{str(e)}", parent=self)
            self.activate_button.setEnabled(True)
            self.activate_button.setText("立即激活")
    
    def copy_hardware_fingerprint(self):
        """复制硬件指纹"""
        from PyQt5.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        clipboard.setText(self.fingerprint_value.text())
        InfoBar.success("提示", "硬件指纹已复制到剪贴板", parent=self)
    
    def open_purchase_page(self):
        """打开购买页面"""
        try:
            from core.payment_manager import PaymentManager
            
            # 禁用按钮防止重复点击
            self.purchase_button.setEnabled(False)
            self.purchase_button.setText("创建中...")
            
            # 获取硬件指纹
            hardware_fingerprint = self.license_manager._get_hardware_fingerprint()
            
            # 创建支付管理器
            payment_manager = PaymentManager()
            
            # 创建支付会话
            success, message, checkout_url = payment_manager.create_checkout_session(hardware_fingerprint)
            
            if success and checkout_url:
                # 重置重试计数器
                self.purchase_retry_count = 0
                
                # 使用系统默认浏览器打开支付页面
                import webbrowser
                webbrowser.open(checkout_url)
                
                # 显示信息提示
                InfoBar.success(
                    title="支付页面已打开",
                    content="请在浏览器中完成支付，支付完成后点击'检查支付状态'按钮",
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=5000,
                    parent=self
                )
                
                # 显示支付完成确认弹窗
                self.show_payment_completion_dialog()
                
            else:
                # 增加重试计数
                self.purchase_retry_count += 1
                
                # 根据错误类型提供不同的处理建议
                if "配置错误" in message or "认证失败" in message:
                    InfoBar.error(
                        title="支付系统故障",
                        content=f"{message}\n\n您也可以尝试：\n1. 联系客服获取人工激活码\n2. 稍后重试",
                        orient=Qt.Horizontal,
                        isClosable=True,
                        position=InfoBarPosition.TOP,
                        duration=8000,  # 增加显示时间
                        parent=self
                    )
                elif "服务器内部错误" in message:
                    retry_text = f" (已重试{self.purchase_retry_count}次)" if self.purchase_retry_count > 1 else ""
                    InfoBar.warning(
                        title="服务器暂时不可用",
                        content=f"{message}{retry_text}\n\n请稍后重试，或联系客服获取帮助。",
                        orient=Qt.Horizontal,
                        isClosable=True,
                        position=InfoBarPosition.TOP,
                        duration=6000,
                        parent=self
                    )
                else:
                    InfoBar.error(
                        title="创建支付会话失败",
                        content=f"无法创建支付链接: {message}",
                        orient=Qt.Horizontal,
                        isClosable=True,
                        position=InfoBarPosition.TOP,
                        duration=5000,
                        parent=self
                    )
                
        except Exception as e:
            InfoBar.error(
                title="打开支付页面失败",
                content=f"无法打开支付页面: {str(e)}",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=5000,
                parent=self
            )
        finally:
            # 重新启用按钮
            self.purchase_button.setEnabled(True)
            self.purchase_button.setText("立即购买")
    
    def show_payment_completion_dialog(self):
        """显示支付完成确认弹窗"""
        msgbox = MessageBox(
            title="支付完成确认",
            content="请确认您是否已经完成支付？\n\n如果已完成支付，您将在Creem的订单确认页面或邮件中看到许可证密钥，请复制并粘贴到激活码输入框中。",
            parent=self
        )
        
        # 添加自定义按钮
        msgbox.yesButton.setText("已完成支付")
        msgbox.cancelButton.setText("取消")
        
        if msgbox.exec_() == msgbox.Accepted:
            # 用户确认已完成支付，显示许可证密钥输入提示
            InfoBar.info(
                title="请输入许可证密钥",
                content="请在上方激活码输入框中输入您从Creem获得的许可证密钥，然后点击'立即激活'按钮。\n\nCreem许可证密钥格式通常为：XXXXX-XXXXX-XXXXX-XXXXX-XXXXX",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=10000,  # 显示10秒
                parent=self
            )
            
            # 高亮激活码输入框
            self.activation_input.setFocus()
    

    
 