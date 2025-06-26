#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
许可证和激活功能组件
"""

from PyQt5.QtCore import QObject, pyqtSignal, Qt
from qfluentwidgets import InfoBar, InfoBarPosition
from .fluent_activation_dialog import FluentActivationDialog


class FluentLicenseManager(QObject):
    """许可证和激活功能组件"""
    
    # 定义信号
    license_status_changed = pyqtSignal(bool, str, dict)  # 许可证状态变化信号
    
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
    
    def set_license_status(self, is_valid, message, data):
        """设置许可证状态"""
        self.parent.license_status = {
            "is_valid": is_valid,
            "message": message,
            "data": data
        }
        
        # 更新导航界面
        self.update_navigation_for_activation()
        
        # 发出状态变化信号
        self.license_status_changed.emit(is_valid, message, data)
        
        # 显示许可证状态
        if hasattr(self.parent, 'license_status_bar'):
            if is_valid:
                self.parent.license_status_bar.setText(f"✅ 已激活 - {message}")
                self.parent.license_status_bar.setStyleSheet("""
                    QLabel {
                        color: #27ae60;
                        background-color: rgba(39, 174, 96, 0.1);
                        padding: 4px 8px;
                        border-radius: 4px;
                        font-size: 12px;
                    }
                """)
            else:
                trial_info = ""
                if data.get("trial", False):
                    remaining_days = data.get("remaining_days", 0)
                    trial_info = f" (试用期剩余 {remaining_days} 天)"
                
                self.parent.license_status_bar.setText(f"⚠️ 未激活{trial_info} - {message}")
                self.parent.license_status_bar.setStyleSheet("""
                    QLabel {
                        color: #e67e22;
                        background-color: rgba(230, 126, 34, 0.1);
                        padding: 4px 8px;
                        border-radius: 4px;
                        font-size: 12px;
                    }
                """)
    
    def show_activation_dialog(self):
        """显示激活对话框"""
        dialog = FluentActivationDialog(self.parent)
        dialog.activation_completed.connect(self.on_activation_completed)
        dialog.exec_()
    
    def on_activation_completed(self, success, message):
        """激活完成回调"""
        if success:
            InfoBar.success(
                title="激活成功",
                content=message,
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self.parent
            )
            
            # 重新检查许可证状态
            is_valid, license_message, license_data = self.parent.license_manager.check_license_validity()
            self.set_license_status(is_valid, license_message, license_data)
            
        else:
            InfoBar.error(
                title="激活失败",
                content=message,
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=4000,
                parent=self.parent
            )
    
    def update_navigation_for_activation(self):
        """根据激活状态更新导航界面"""
        try:
            # 根据许可证状态显示或隐藏激活页面
            is_valid = self.parent.license_status.get("is_valid", False)
            
            # 如果已激活，隐藏激活页面；如果未激活，显示激活页面
            if hasattr(self.parent, 'activation_interface'):
                # 这里可以根据需要调整导航显示逻辑
                pass
                
        except Exception as e:
            print(f"更新导航界面时出错: {e}")
    
    def check_feature_access(self, feature_name):
        """检查功能访问权限"""
        is_valid = self.parent.license_status.get("is_valid", False)
        data = self.parent.license_status.get("data", {})
        
        # 如果许可证有效，允许所有功能
        if is_valid:
            return True
        
        # 如果在试用期，允许部分功能
        if data.get("trial", False):
            # 试用期允许的功能列表
            trial_features = [
                "basic_extraction",
                "image_display",
                "prompt_editing",
                "history_view",
                "single_export"
            ]
            
            if feature_name in trial_features:
                return True
            else:
                # 试用期限制的功能
                InfoBar.warning(
                    title="功能受限",
                    content=f"试用期不支持 {feature_name} 功能，请激活完整版本",
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=3000,
                    parent=self.parent
                )
                return False
        
        # 未激活且不在试用期，提示激活
        InfoBar.error(
            title="需要激活",
            content="请激活软件后使用此功能",
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=3000,
            parent=self.parent
        )
        return False 