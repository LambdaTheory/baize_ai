#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fluent Design 批量文件夹处理对话框
使用PyQt-Fluent-Widgets组件库
"""

import os
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QProgressBar, QMessageBox, QCheckBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal

from qfluentwidgets import (CardWidget, PushButton, SubtitleLabel, BodyLabel, 
                           SpinBox, CheckBox)
from .fluent_styles import FluentTheme, FluentIcons, FluentColors, FluentSpacing
from core.batch_processor import BatchProcessor


class BatchFolderProcessThread(QThread):
    """批量文件夹处理线程"""
    progress_updated = pyqtSignal(int, str, int, int)  # 进度、消息、成功数、失败数
    process_finished = pyqtSignal(bool, str, int, int)  # 完成状态、消息、成功数、失败数
    
    def __init__(self, folder_path, data_manager, include_subdirs=True, max_workers=4):
        super().__init__()
        self.folder_path = folder_path
        self.data_manager = data_manager
        self.include_subdirs = include_subdirs
        self.max_workers = max_workers
        self.batch_processor = None
        
    def run(self):
        """执行批量处理"""
        try:
            # 创建批量处理器
            self.batch_processor = BatchProcessor(self.data_manager)
            
            # 扫描文件夹
            image_files = self.batch_processor.scan_folder(
                self.folder_path, 
                recursive=self.include_subdirs
            )
            
            if not image_files:
                self.process_finished.emit(False, "未找到支持的图片文件", 0, 0)
                return
            
            # 开始批量处理
            results = self.batch_processor.batch_process_images(
                image_files,
                progress_callback=self.on_progress_updated,
                auto_save=True,
                max_workers=self.max_workers
            )
            
            success_count = results['successful_count']
            error_count = results['failed_count']
            
            if error_count == 0:
                self.process_finished.emit(
                    True, 
                    f"批量处理完成！成功处理 {success_count} 个文件", 
                    success_count, 
                    error_count
                )
            else:
                self.process_finished.emit(
                    True, 
                    f"批量处理完成！成功 {success_count} 个，失败 {error_count} 个", 
                    success_count, 
                    error_count
                )
                
        except Exception as e:
            self.process_finished.emit(False, f"批量处理失败: {str(e)}", 0, 0)
            
    def on_progress_updated(self, current, total, current_file):
        """处理进度更新"""
        progress = int((current / total * 100)) if total > 0 else 0
        message = f"正在处理: {os.path.basename(current_file)} ({current}/{total})"
        # 这里暂时传递0作为成功和失败数，因为处理过程中无法准确统计
        self.progress_updated.emit(progress, message, 0, 0)


class FluentBatchFolderDialog(QDialog):
    """Fluent Design 批量文件夹处理对话框"""
    
    def __init__(self, folder_path, data_manager, parent=None):
        super().__init__(parent)
        self.folder_path = folder_path
        self.data_manager = data_manager
        self.process_thread = None
        self.init_ui()
        self.scan_folder()
        
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("批量处理文件夹")
        self.setFixedSize(500, 650)
        self.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint)
        
        # 主布局
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # 标题
        title = SubtitleLabel("📁 批量处理文件夹")
        title.setStyleSheet(f"""
            color: {FluentColors.get_color('text_primary')};
            font-weight: 600;
            margin-bottom: 10px;
        """)
        main_layout.addWidget(title)
        
        # 文件夹信息卡片
        folder_card = CardWidget()
        folder_card.setBorderRadius(12)
        folder_layout = QVBoxLayout()
        folder_layout.setContentsMargins(16, 16, 16, 16)
        
        folder_label = BodyLabel("文件夹路径:")
        folder_label.setStyleSheet(f"""
            color: {FluentColors.get_color('text_primary')};
            font-weight: 600;
            margin-bottom: 8px;
        """)
        folder_layout.addWidget(folder_label)
        
        path_label = BodyLabel(self.folder_path)
        path_label.setWordWrap(True)
        path_label.setStyleSheet(f"color: {FluentColors.get_color('text_secondary')};")
        folder_layout.addWidget(path_label)
        
        # 文件统计信息
        self.stats_label = BodyLabel("正在扫描文件...")
        self.stats_label.setStyleSheet(f"color: {FluentColors.get_color('text_tertiary')};")
        folder_layout.addWidget(self.stats_label)
        
        folder_card.setLayout(folder_layout)
        main_layout.addWidget(folder_card)
        
        # 处理选项卡片
        options_card = CardWidget()
        options_card.setBorderRadius(12)
        options_layout = QVBoxLayout()
        options_layout.setContentsMargins(16, 16, 16, 16)
        
        options_title = BodyLabel("处理选项")
        options_title.setStyleSheet(f"""
            color: {FluentColors.get_color('text_primary')};
            font-weight: 600;
            margin-bottom: 12px;
        """)
        options_layout.addWidget(options_title)
        
        # 包含子文件夹选项
        self.include_subdirs_cb = CheckBox("包含子文件夹")
        self.include_subdirs_cb.setChecked(True)
        self.include_subdirs_cb.stateChanged.connect(self.scan_folder)  # 状态改变时重新扫描
        options_layout.addWidget(self.include_subdirs_cb)
        
        # 并发处理数设置
        workers_layout = QHBoxLayout()
        workers_label = BodyLabel("并发处理数:")
        workers_label.setFixedWidth(100)
        
        self.workers_spinbox = SpinBox()
        self.workers_spinbox.setRange(1, 16)
        self.workers_spinbox.setValue(4)
        self.workers_spinbox.setFixedWidth(80)
        
        workers_layout.addWidget(workers_label)
        workers_layout.addWidget(self.workers_spinbox)
        workers_layout.addStretch()
        
        options_layout.addLayout(workers_layout)
        
        options_card.setLayout(options_layout)
        main_layout.addWidget(options_card)
        
        # 进度显示卡片
        self.progress_card = CardWidget()
        self.progress_card.setBorderRadius(12)
        self.progress_card.setVisible(False)
        
        progress_layout = QVBoxLayout()
        progress_layout.setContentsMargins(16, 16, 16, 16)
        
        progress_title = BodyLabel("处理进度")
        progress_title.setStyleSheet(f"""
            color: {FluentColors.get_color('text_primary')};
            font-weight: 600;
            margin-bottom: 12px;
        """)
        progress_layout.addWidget(progress_title)
        
        self.progress_label = BodyLabel("准备开始...")
        self.progress_label.setStyleSheet(f"color: {FluentColors.get_color('text_secondary')};")
        progress_layout.addWidget(self.progress_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(8)
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: none;
                border-radius: 4px;
                background-color: {FluentColors.get_color('bg_secondary')};
            }}
            QProgressBar::chunk {{
                border-radius: 4px;
                background-color: {FluentColors.get_color('primary')};
            }}
        """)
        progress_layout.addWidget(self.progress_bar)
        
        # 统计信息
        stats_layout = QHBoxLayout()
        self.success_label = BodyLabel("成功: 0")
        self.success_label.setStyleSheet(f"color: {FluentColors.get_color('success')};")
        
        self.error_label = BodyLabel("失败: 0")
        self.error_label.setStyleSheet(f"color: {FluentColors.get_color('error')};")
        
        stats_layout.addWidget(self.success_label)
        stats_layout.addWidget(self.error_label)
        stats_layout.addStretch()
        
        progress_layout.addLayout(stats_layout)
        
        self.progress_card.setLayout(progress_layout)
        main_layout.addWidget(self.progress_card)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.cancel_btn = PushButton("取消")
        self.cancel_btn.setFixedSize(100, 36)
        self.cancel_btn.clicked.connect(self.reject)
        
        self.start_btn = PushButton("开始处理")
        self.start_btn.setFixedSize(120, 36)
        self.start_btn.setStyleSheet(f"""
            PushButton {{
                background-color: {FluentColors.get_color('primary')};
                border: 1px solid {FluentColors.get_color('primary')};
                color: white;
            }}
            PushButton:hover {{
                background-color: #4f46e5;
                border: 1px solid #4f46e5;
            }}
            PushButton:pressed {{
                background-color: #3730a3;
                border: 1px solid #3730a3;
            }}
        """)
        self.start_btn.clicked.connect(self.start_processing)
        
        button_layout.addWidget(self.cancel_btn)
        button_layout.addSpacing(10)
        button_layout.addWidget(self.start_btn)
        
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)
        
    def scan_folder(self):
        """扫描文件夹"""
        try:
            # 使用BatchProcessor来扫描文件夹
            from core.batch_processor import BatchProcessor
            processor = BatchProcessor()
            
            # 先用当前设置扫描
            include_subdirs = self.include_subdirs_cb.isChecked()
            image_files = processor.scan_folder(self.folder_path, recursive=include_subdirs)
            image_count = len(image_files)
            
            self.stats_label.setText(f"发现 {image_count} 个图片文件")
            
            if image_count == 0:
                self.start_btn.setEnabled(False)
                self.stats_label.setText("未发现支持的图片文件")
                self.stats_label.setStyleSheet(f"color: {FluentColors.get_color('error')};")
            else:
                self.start_btn.setEnabled(True)
                self.stats_label.setStyleSheet(f"color: {FluentColors.get_color('text_tertiary')};")
            
        except Exception as e:
            self.stats_label.setText(f"扫描失败: {str(e)}")
            self.stats_label.setStyleSheet(f"color: {FluentColors.get_color('error')};")
            self.start_btn.setEnabled(False)
            
    def start_processing(self):
        """开始批量处理"""
        # 显示进度卡片
        self.progress_card.setVisible(True)
        self.start_btn.setEnabled(False)
        self.cancel_btn.setText("停止")
        
        # 获取处理选项
        include_subdirs = self.include_subdirs_cb.isChecked()
        max_workers = self.workers_spinbox.value()
        
        # 启动处理线程
        self.process_thread = BatchFolderProcessThread(
            self.folder_path, 
            self.data_manager, 
            include_subdirs, 
            max_workers
        )
        self.process_thread.progress_updated.connect(self.update_progress)
        self.process_thread.process_finished.connect(self.process_finished)
        self.process_thread.start()
        
    def update_progress(self, progress, message, success_count, error_count):
        """更新进度"""
        self.progress_bar.setValue(progress)
        self.progress_label.setText(message)
        self.success_label.setText(f"成功: {success_count}")
        self.error_label.setText(f"失败: {error_count}")
        
    def process_finished(self, success, message, success_count, error_count):
        """处理完成"""
        self.start_btn.setEnabled(True)
        self.cancel_btn.setText("关闭")
        
        self.success_label.setText(f"成功: {success_count}")
        self.error_label.setText(f"失败: {error_count}")
        
        if success:
            self.progress_label.setText("✅ " + message)
            QMessageBox.information(self, "处理完成", message)
            self.accept()
        else:
            self.progress_label.setText("❌ " + message)
            QMessageBox.critical(self, "处理失败", message)
            
    def reject(self):
        """取消对话框"""
        if self.process_thread and self.process_thread.isRunning():
            # 这里可以添加停止处理的逻辑
            reply = QMessageBox.question(
                self, "确认", "确定要停止批量处理吗？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                # 强制终止线程（不推荐，但在这里可以接受）
                self.process_thread.terminate()
                self.process_thread.wait()
                super().reject()
        else:
            super().reject() 