#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fluent Design 事件处理器
处理主窗口的各种事件和信号
"""

import os
from PyQt5.QtWidgets import QApplication, QMessageBox, QFileDialog
from PyQt5.QtCore import Qt, QObject, pyqtSignal
from PyQt5.QtGui import QDragEnterEvent, QDropEvent, QImage
from qfluentwidgets import InfoBar, InfoBarPosition
import tempfile
import uuid
import requests


class FluentEventHandlers(QObject):
    """事件处理器类"""
    
    # 定义信号
    file_processed = pyqtSignal(str)  # 文件处理完成信号
    record_save_requested = pyqtSignal()  # 请求保存记录信号
    prompt_edit_requested = pyqtSignal(str, str)  # 请求编辑提示词信号
    
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        
    def handle_positive_translate_clicked(self):
        """处理正向提示词跳转翻译按钮点击"""
        try:
            # 获取当前的正向提示词
            positive_prompt = self.parent.positive_prompt_text.toPlainText().strip()
            
            if not positive_prompt:
                InfoBar.warning(
                    title="提示",
                    content="正向提示词为空，无法跳转翻译",
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=2000,
                    parent=self.parent
                )
                return
            
            # 获取当前图片的场景名称
            scene_name = "正向提示词"
            if hasattr(self.parent, 'current_file_path') and self.parent.current_file_path:
                scene_name = f"{os.path.splitext(os.path.basename(self.parent.current_file_path))[0]}_正向"
            
            # 触发编辑提示词请求信号
            self.prompt_edit_requested.emit(positive_prompt, scene_name)
            
        except Exception as e:
            print(f"处理正向提示词跳转翻译时出错: {e}")
    
    def handle_negative_translate_clicked(self):
        """处理反向提示词跳转翻译按钮点击"""
        try:
            # 获取当前的反向提示词
            negative_prompt = self.parent.negative_prompt_text.toPlainText().strip()
            
            if not negative_prompt:
                InfoBar.warning(
                    title="提示",
                    content="反向提示词为空，无法跳转翻译",
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=2000,
                    parent=self.parent
                )
                return
            
            # 获取当前图片的场景名称
            scene_name = "反向提示词"
            if hasattr(self.parent, 'current_file_path') and self.parent.current_file_path:
                scene_name = f"{os.path.splitext(os.path.basename(self.parent.current_file_path))[0]}_反向"
            
            # 触发编辑提示词请求信号
            self.prompt_edit_requested.emit(negative_prompt, scene_name)
            
        except Exception as e:
            print(f"处理反向提示词跳转翻译时出错: {e}")
    
    def handle_files_dropped(self, files):
        """处理拖拽的文件"""
        if files:
            self.file_processed.emit(files[0])  # 处理第一个文件
            
    def handle_folder_dropped(self, folder_path):
        """处理拖拽的文件夹"""
        try:
            # 显示批量处理对话框
            from .fluent_batch_folder_dialog import FluentBatchFolderDialog
            
            dialog = FluentBatchFolderDialog(folder_path, self.parent.data_manager, self.parent)
            if dialog.exec_() == dialog.Accepted:
                # 刷新历史记录和画廊
                self.parent.history_widget.load_history()
                self.parent.gallery_interface.load_records()
                
                InfoBar.success(
                    title="批量处理完成",
                    content="文件夹中的图片已成功处理",
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=3000,
                    parent=self.parent
                )
                
        except Exception as e:
            print(f"处理文件夹时出错: {e}")
            InfoBar.error(
                title="处理失败",
                content=f"处理文件夹时出错: {str(e)}",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self.parent
            )
    
    def handle_drag_enter_event(self, event: QDragEnterEvent):
        """拖拽进入事件"""
        if event.mimeData().hasUrls():
            # 检查是否有支持的文件格式或文件夹
            has_valid_items = False
            for url in event.mimeData().urls():
                if url.isLocalFile():
                    file_path = url.toLocalFile()
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
                # 显示蒙层
                self.parent.drag_overlay.resize(self.parent.extraction_interface.size())
                self.parent.drag_overlay.show()
            else:
                event.ignore()
        elif event.mimeData().hasImage():
            # 直接支持图片数据拖拽（从浏览器复制粘贴的图片）
            event.accept()
            self.parent.drag_overlay.resize(self.parent.extraction_interface.size())
            self.parent.drag_overlay.show()
        else:
            event.ignore()
            
    def handle_drag_leave_event(self, event):
        """拖拽离开事件"""
        # 隐藏蒙层
        self.parent.drag_overlay.hide()
        
    def handle_drop_event(self, event: QDropEvent):
        """拖拽放下事件"""
        files = []
        folders = []
        
        # 隐藏蒙层
        self.parent.drag_overlay.hide()
        
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
                        self.handle_files_dropped([temp_path])
                        InfoBar.success(
                            title="图片处理成功",
                            content="从浏览器拖拽的图片已成功加载",
                            orient=Qt.Horizontal,
                            isClosable=True,
                            position=InfoBarPosition.TOP,
                            duration=3000,
                            parent=self.parent
                        )
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
                    InfoBar.warning(
                        title="图片下载失败",
                        content=f"无法从浏览器下载图片: {str(e)[:50]}...",
                        orient=Qt.Horizontal,
                        isClosable=True,
                        position=InfoBarPosition.TOP,
                        duration=3000,
                        parent=self.parent
                    )
                    continue
        
        # 优先处理文件夹（批量处理）
        if folders:
            # 只处理第一个文件夹
            self.handle_folder_dropped(folders[0])
        elif files:
            self.handle_files_dropped(files)
            if any('browser_' in f for f in files):
                InfoBar.success(
                    title="浏览器图片处理成功",
                    content="从浏览器拖拽的图片已成功加载",
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=3000,
                    parent=self.parent
                )
        
        event.accept()
    
    def handle_gallery_record_selected(self, record_data):
        """画廊记录选中事件"""
        print(f"画廊记录被选中: {record_data.get('file_path', '未知')}")
        
        # 切换到信息提取页面
        self.parent.stackedWidget.setCurrentWidget(self.parent.extraction_interface)
        print("已切换到信息提取页面")
        
        # 检查界面状态
        print(f"信息提取页面可见: {self.parent.extraction_interface.isVisible()}")
        
        # 强制显示组件
        self.parent.extraction_interface.setVisible(True)
        
        # 加载选中的记录
        self.parent.load_from_history_record(record_data)
        
        InfoBar.success(
            title="记录已加载",
            content=f"已加载记录：{os.path.basename(record_data.get('file_path', ''))}",
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=2000,
            parent=self.parent
        )
    
    def handle_new_file_from_instance(self, file_path):
        """处理来自其他实例的新文件"""
        if file_path and os.path.exists(file_path):
            print(f"[单实例] 接收到新文件: {file_path}")
            # 激活窗口到前台
            self.parent.activateWindow()
            self.parent.raise_()
            self.parent.showNormal()
            # 处理图片
            self.file_processed.emit(file_path)
        else:
            # 空文件路径，只是激活窗口
            print(f"[单实例] 激活窗口")
            self.parent.activateWindow()
            self.parent.raise_()
            self.parent.showNormal() 