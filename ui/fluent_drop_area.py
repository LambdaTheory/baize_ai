#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fluent Design 拖拽区域组件
使用PyQt-Fluent-Widgets组件库
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFileDialog, QLabel
from PyQt5.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve, QRect
from PyQt5.QtGui import QDragEnterEvent, QDropEvent, QPainter, QBrush, QColor, QPen

from qfluentwidgets import (CardWidget, BodyLabel, SubtitleLabel, PushButton)
from .fluent_styles import FluentTheme, FluentIcons, FluentColors, FluentSpacing


class FluentDropArea(CardWidget):
    """Fluent Design 拖拽区域组件"""
    filesDropped = pyqtSignal(list)
    folderDropped = pyqtSignal(str)  # 新增文件夹拖拽信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_drag_active = False
        self.init_ui()
        self.setup_animations()
        
    def init_ui(self):
        """初始化UI"""
        self.setAcceptDrops(True)
        self.setMinimumHeight(320)
        self.setFixedHeight(320)
        
        # 设置卡片样式
        self.setBorderRadius(20)
        
        # 主布局
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(FluentSpacing.LG, FluentSpacing.LG, 
                                     FluentSpacing.LG, FluentSpacing.LG)
        main_layout.setSpacing(FluentSpacing.MD)
        main_layout.setAlignment(Qt.AlignCenter)
        
        # 移除图标区域，使用更简洁的设计
        
        # 标题
        self.title_label = SubtitleLabel("拖拽图片到此处")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setWordWrap(True)  # 允许文字换行
        self.title_label.setStyleSheet(f"""
            color: {FluentColors.get_color('text_primary')};
            font-weight: 600;
            font-size: 18px;
            margin: 8px 0px;
            padding: 4px;
        """)
        
        # 副标题
        self.subtitle_label = BodyLabel("支持 PNG、JPG、JPEG 格式\n也可拖拽文件夹进行批量处理")
        self.subtitle_label.setAlignment(Qt.AlignCenter)
        self.subtitle_label.setWordWrap(True)  # 允许文字换行
        self.subtitle_label.setStyleSheet(f"""
            color: {FluentColors.get_color('text_secondary')};
            font-size: 14px;
            margin-bottom: 16px;
            padding: 4px;
        """)
        
        # 分割线
        separator_layout = QHBoxLayout()
        separator_layout.setAlignment(Qt.AlignCenter)
        
        left_line = QLabel()
        left_line.setFixedSize(60, 1)
        left_line.setStyleSheet(f"background-color: {FluentColors.get_color('border_primary')};")
        
        or_label = BodyLabel("或")
        or_label.setStyleSheet(f"""
            color: {FluentColors.get_color('text_tertiary')};
            margin: 0px 16px;
        """)
        
        right_line = QLabel()
        right_line.setFixedSize(60, 1)
        right_line.setStyleSheet(f"background-color: {FluentColors.get_color('border_primary')};")
        
        separator_layout.addWidget(left_line)
        separator_layout.addWidget(or_label)
        separator_layout.addWidget(right_line)
        
        # 选择文件按钮
        self.select_files_btn = PushButton("选择文件")
        self.select_files_btn.setFixedSize(120, 40)
        self.select_files_btn.clicked.connect(self.select_files)
        
        # 选择文件夹按钮
        self.select_folder_btn = PushButton("选择文件夹")
        self.select_folder_btn.setFixedSize(120, 40)
        self.select_folder_btn.clicked.connect(self.select_folder)
        
        # 按钮布局
        btn_layout = QHBoxLayout()
        btn_layout.setAlignment(Qt.AlignCenter)
        btn_layout.addWidget(self.select_files_btn)
        btn_layout.addSpacing(16)
        btn_layout.addWidget(self.select_folder_btn)
        
        # 添加到主布局
        main_layout.addWidget(self.title_label)
        main_layout.addWidget(self.subtitle_label)
        main_layout.addLayout(separator_layout)
        main_layout.addLayout(btn_layout)
        
        self.setLayout(main_layout)
        
        # 设置正常状态样式
        self.set_normal_state()
        
    def setup_animations(self):
        """设置动画"""
        # 移除图标动画，保持简洁
        pass
        
    def set_normal_state(self):
        """设置正常状态"""
        self.setStyleSheet(f"""
            CardWidget {{
                background-color: {FluentColors.get_color('bg_primary')};
                border: 2px dashed {FluentColors.get_color('border_primary')};
                border-radius: 20px;
            }}
            CardWidget:hover {{
                background-color: {FluentColors.get_color('bg_secondary')};
                border: 2px dashed {FluentColors.get_color('primary')};
            }}
        """)
        
        self.title_label.setText("拖拽图片或文件夹到此处")
        self.title_label.setStyleSheet(f"""
            color: {FluentColors.get_color('text_primary')};
            font-weight: 600;
            font-size: 18px;
            margin: 8px 0px;
            padding: 4px;
        """)
        
    def set_drag_active_state(self):
        """设置拖拽激活状态"""
        self.setStyleSheet(f"""
            CardWidget {{
                background-color: rgba(79, 70, 229, 0.05);
                border: 2px dashed {FluentColors.get_color('primary')};
                border-radius: 20px;
            }}
        """)
        
        self.title_label.setText("释放以添加图片")
        self.title_label.setStyleSheet(f"""
            color: {FluentColors.get_color('primary')};
            font-weight: 600;
            font-size: 18px;
            margin: 8px 0px;
            padding: 4px;
        """)
        
        # 启动动画
        self.animate_to_active()
        
    def set_drag_reject_state(self):
        """设置拖拽拒绝状态"""
        self.setStyleSheet(f"""
            CardWidget {{
                background-color: rgba(239, 68, 68, 0.05);
                border: 2px dashed {FluentColors.get_color('error')};
                border-radius: 20px;
            }}
        """)
        
        self.title_label.setText("不支持的文件格式")
        self.title_label.setStyleSheet(f"""
            color: {FluentColors.get_color('error')};
            font-weight: 600;
            font-size: 18px;
            margin: 8px 0px;
            padding: 4px;
        """)
        
    def animate_to_active(self):
        """动画到激活状态"""
        # 简化动画，只保留状态切换
        pass
        
    def animate_to_normal(self):
        """动画到正常状态"""
        # 简化动画，只保留状态切换
        pass
        
    def dragEnterEvent(self, event: QDragEnterEvent):
        """拖拽进入事件"""
        if event.mimeData().hasUrls():
            # 检查是否有支持的文件格式或文件夹
            has_valid_items = False
            for url in event.mimeData().urls():
                if url.isLocalFile():
                    file_path = url.toLocalFile()
                    import os
                    # 检查是否是文件夹或支持的图片格式
                    if os.path.isdir(file_path) or file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
                        has_valid_items = True
                        break
                else:
                    # 支持从浏览器拖拽的网络图片URL或临时文件
                    url_string = url.toString()
                    # 检查URL是否包含图片扩展名或是常见的图片服务
                    if (url_string.lower().endswith(('.png', '.jpg', '.jpeg')) or 
                        'data:image/' in url_string.lower() or
                        any(service in url_string.lower() for service in ['blob:', 'localhost:', '127.0.0.1:', 'webui', 'comfyui'])):
                        has_valid_items = True
                        break
            
            if has_valid_items:
                event.accept()
                self.is_drag_active = True
                self.set_drag_active_state()
            else:
                event.ignore()
                self.set_drag_reject_state()
        elif event.mimeData().hasImage():
            # 直接支持图片数据拖拽（从浏览器复制粘贴的图片）
            event.accept()
            self.is_drag_active = True
            self.set_drag_active_state()
        else:
            event.ignore()
            
    def dragLeaveEvent(self, event):
        """拖拽离开事件"""
        self.is_drag_active = False
        self.set_normal_state()
        
    def dropEvent(self, event: QDropEvent):
        """拖拽放下事件"""
        import os
        import tempfile
        import uuid
        import requests
        from PyQt5.QtGui import QImage
        
        files = []
        folders = []
        
        # 检查是否有直接的图片数据（从浏览器复制的图片）
        if event.mimeData().hasImage():
            try:
                # 保存图片数据到临时文件
                image = event.mimeData().imageData()
                if isinstance(image, QImage) and not image.isNull():
                    temp_dir = tempfile.gettempdir()
                    temp_filename = f"browser_image_{uuid.uuid4().hex}.png"
                    temp_path = os.path.join(temp_dir, temp_filename)
                    
                    if image.save(temp_path, "PNG"):
                        self.filesDropped.emit([temp_path])
                        self.show_success_state("浏览器图片添加成功！")
                        self.is_drag_active = False
                        event.accept()
                        return
            except Exception as e:
                print(f"处理浏览器图片数据失败: {e}")
        
        # 处理URL拖拽
        for url in event.mimeData().urls():
            if url.isLocalFile():
                file_path = url.toLocalFile()
                if os.path.isdir(file_path):
                    folders.append(file_path)
                elif file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
                    files.append(file_path)
            else:
                # 处理从浏览器拖拽的网络图片URL
                url_string = url.toString()
                try:
                    # 检查是否是支持的图片URL
                    if (url_string.lower().endswith(('.png', '.jpg', '.jpeg')) or 
                        'data:image/' in url_string.lower() or
                        any(service in url_string.lower() for service in ['blob:', 'localhost:', '127.0.0.1:', 'webui', 'comfyui'])):
                        
                        # 下载图片到临时文件
                        temp_dir = tempfile.gettempdir()
                        temp_filename = f"browser_download_{uuid.uuid4().hex}.png"
                        temp_path = os.path.join(temp_dir, temp_filename)
                        
                        # 处理不同类型的URL
                        if url_string.startswith('data:image/'):
                            # Base64编码的图片数据
                            import base64
                            header, data = url_string.split(',', 1)
                            image_data = base64.b64decode(data)
                            with open(temp_path, 'wb') as f:
                                f.write(image_data)
                            files.append(temp_path)
                        else:
                            # HTTP/HTTPS URL或本地服务器URL
                            response = requests.get(url_string, timeout=10)
                            response.raise_for_status()
                            
                            with open(temp_path, 'wb') as f:
                                f.write(response.content)
                            files.append(temp_path)
                            
                except Exception as e:
                    print(f"下载图片失败: {url_string}, 错误: {e}")
                    self.show_success_state("图片下载失败！")
                    continue
        
        # 优先处理文件夹（批量处理）
        if folders:
            # 只处理第一个文件夹
            self.folderDropped.emit(folders[0])
            self.show_success_state("文件夹添加成功！")
        elif files:
            self.filesDropped.emit(files)
            success_msg = "浏览器图片添加成功！" if any('browser_' in f for f in files) else "文件添加成功！"
            self.show_success_state(success_msg)
        
        self.is_drag_active = False
        event.accept()
        
    def show_success_state(self, message="添加成功！"):
        """显示成功状态"""
        self.setStyleSheet(f"""
            CardWidget {{
                background-color: rgba(34, 197, 94, 0.05);
                border: 2px solid {FluentColors.get_color('success')};
                border-radius: 20px;
            }}
        """)
        
        self.title_label.setText(message)
        self.title_label.setStyleSheet(f"""
            color: {FluentColors.get_color('success')};
            font-weight: 600;
            margin: 8px 0px;
        """)
        
        # 1秒后恢复正常状态
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(1000, self.set_normal_state)
        
    def select_files(self):
        """选择文件"""
        file_dialog = QFileDialog()
        files, _ = file_dialog.getOpenFileNames(
            self, "选择图片文件", "", 
            "图片文件 (*.png *.jpg *.jpeg);;PNG文件 (*.png);;JPG文件 (*.jpg *.jpeg)"
        )
        if files:
            self.filesDropped.emit(files)
            self.show_success_state("文件添加成功！")
            
    def select_folder(self):
        """选择文件夹"""
        import os
        folder = QFileDialog.getExistingDirectory(
            self, "选择图片文件夹", os.path.expanduser("~")
        )
        if folder:
            self.folderDropped.emit(folder)
            self.show_success_state("文件夹添加成功！")
            
    def enterEvent(self, event):
        """鼠标进入事件"""
        if not self.is_drag_active:
            self.setStyleSheet(f"""
                CardWidget {{
                    background-color: {FluentColors.get_color('bg_secondary')};
                    border: 2px dashed {FluentColors.get_color('primary')};
                    border-radius: 20px;
                }}
            """)
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        """鼠标离开事件"""
        if not self.is_drag_active:
            self.set_normal_state()
        super().leaveEvent(event) 