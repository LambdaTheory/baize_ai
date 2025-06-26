#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fluent Design 历史记录组件
使用PyQt-Fluent-Widgets组件库
"""

import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                            QTableWidgetItem, QAbstractItemView, QHeaderView, 
                            QMenu, QAction, QMessageBox, QFileDialog, QLabel)
from PyQt5.QtCore import Qt, pyqtSignal, QModelIndex, QSize
from PyQt5.QtGui import QColor, QPixmap

from qfluentwidgets import (CardWidget, PushButton, GroupHeaderCardWidget,
                           TableWidget, InfoBar, InfoBarPosition, MessageBox,
                           SubtitleLabel, BodyLabel, TransparentPushButton)
from .fluent_styles import FluentTheme, FluentIcons, FluentColors, FluentSpacing


class FluentHistoryWidget(CardWidget):
    """Fluent Design 历史记录组件"""
    
    # 信号定义
    record_selected = pyqtSignal(dict)  # 选中记录时发出信号
    
    def __init__(self, data_manager, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.history_records = []  # 存储历史记录数据
        self.init_ui()
        self.setup_connections()
        
    def init_ui(self):
        """初始化UI"""
        self.setBorderRadius(16)
        
        # 主容器
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(FluentSpacing.LG, FluentSpacing.LG, 
                                     FluentSpacing.LG, FluentSpacing.LG)
        main_layout.setSpacing(FluentSpacing.MD)
        
        # 添加标题
        title = SubtitleLabel("📊 历史记录")
        title.setStyleSheet(f"""
            color: {FluentColors.get_color('text_primary')};
            font-weight: 600;
            margin-bottom: 12px;
        """)
        main_layout.addWidget(title)
        
        # 操作按钮区域
        self.create_action_buttons(main_layout)
        
        # 统计信息
        self.create_statistics_card(main_layout)
        
        # 历史记录表格
        self.create_history_table(main_layout)
        
        main_widget.setLayout(main_layout)
        
        # 设置卡片布局
        card_layout = QVBoxLayout()
        card_layout.addWidget(main_widget)
        self.setLayout(card_layout)
        
    def create_action_buttons(self, parent_layout):
        """创建操作按钮"""
        button_layout = QHBoxLayout()
        button_layout.setSpacing(FluentSpacing.SM)
        
        # 刷新按钮
        self.refresh_btn = PushButton("刷新")
        self.refresh_btn.setFixedHeight(36)
        self.refresh_btn.setMinimumWidth(80)
        
        # 删除选中按钮
        self.delete_record_btn = PushButton("删除选中")
        self.delete_record_btn.setFixedHeight(36)
        self.delete_record_btn.setMinimumWidth(100)
        self.delete_record_btn.setEnabled(False)  # 初始禁用
        
        # 设置删除按钮样式
        self.delete_record_btn.setStyleSheet(f"""
            PushButton {{
                background-color: {FluentColors.get_color('error')};
                border: 1px solid {FluentColors.get_color('error')};
                color: white;
            }}
            PushButton:hover {{
                background-color: #dc2626;
                border: 1px solid #dc2626;
            }}
            PushButton:pressed {{
                background-color: #b91c1c;
                border: 1px solid #b91c1c;
            }}
            PushButton:disabled {{
                background-color: {FluentColors.get_color('border_primary')};
                border: 1px solid {FluentColors.get_color('border_primary')};
                color: {FluentColors.get_color('text_tertiary')};
            }}
        """)
        
        # 清理无效按钮
        self.clean_invalid_btn = PushButton("清理无效")
        self.clean_invalid_btn.setFixedHeight(36)
        self.clean_invalid_btn.setMinimumWidth(100)
        
        # 设置清理按钮样式
        self.clean_invalid_btn.setStyleSheet(f"""
            PushButton {{
                background-color: {FluentColors.get_color('warning')};
                border: 1px solid {FluentColors.get_color('warning')};
                color: white;
            }}
            PushButton:hover {{
                background-color: #f59e0b;
                border: 1px solid #f59e0b;
            }}
            PushButton:pressed {{
                background-color: #d97706;
                border: 1px solid #d97706;
            }}
        """)
        
        # 清空全部按钮
        self.delete_all_btn = PushButton("清空全部")
        self.delete_all_btn.setFixedHeight(36)
        self.delete_all_btn.setMinimumWidth(100)  # 恢复原来的宽度
        
        # 设置清空全部按钮样式（红色背景）
        self.delete_all_btn.setStyleSheet(f"""
            PushButton {{
                background-color: {FluentColors.get_color('error')};
                border: 1px solid {FluentColors.get_color('error')};
                color: white;
                padding: 4px 12px;
                text-align: center;
            }}
            PushButton:hover {{
                background-color: #dc2626;
                border: 1px solid #dc2626;
            }}
            PushButton:pressed {{
                background-color: #b91c1c;
                border: 1px solid #b91c1c;
            }}
        """)
        
        # 批量导出按钮
        self.batch_export_btn = PushButton("批量导出")
        self.batch_export_btn.setFixedHeight(36)
        self.batch_export_btn.setMinimumWidth(100)
        self.batch_export_btn.setEnabled(False)  # 初始禁用
        
        # 设置批量导出按钮样式
        self.batch_export_btn.setStyleSheet(f"""
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
            PushButton:disabled {{
                background-color: {FluentColors.get_color('border_primary')};
                border: 1px solid {FluentColors.get_color('border_primary')};
                color: {FluentColors.get_color('text_tertiary')};
            }}
        """)
        
        button_layout.addWidget(self.refresh_btn)
        button_layout.addWidget(self.batch_export_btn)
        button_layout.addWidget(self.delete_record_btn)
        button_layout.addWidget(self.clean_invalid_btn)
        button_layout.addWidget(self.delete_all_btn)
        button_layout.addStretch()
        
        parent_layout.addLayout(button_layout)
        
    def create_statistics_card(self, parent_layout):
        """创建统计信息卡片"""
        self.stats_card = CardWidget()
        self.stats_card.setBorderRadius(12)
        self.stats_card.setFixedHeight(60)
        self.stats_card.setStyleSheet(f"""
            background-color: {FluentColors.get_color('bg_secondary')};
            border: 1px solid {FluentColors.get_color('border_secondary')};
        """)
        
        stats_layout = QHBoxLayout()
        stats_layout.setContentsMargins(FluentSpacing.MD, FluentSpacing.SM, 
                                      FluentSpacing.MD, FluentSpacing.SM)
        
        # 总记录数
        self.total_label = BodyLabel("总记录: 0")
        self.total_label.setStyleSheet(f"color: {FluentColors.get_color('text_primary')};")
        
        # 有效记录数
        self.valid_label = BodyLabel("有效: 0")
        self.valid_label.setStyleSheet(f"color: {FluentColors.get_color('success')};")
        
        # 无效记录数
        self.invalid_label = BodyLabel("无效: 0")
        self.invalid_label.setStyleSheet(f"color: {FluentColors.get_color('error')};")
        
        # 选中记录数
        self.selected_label = BodyLabel("已选中: 0")
        self.selected_label.setStyleSheet(f"color: {FluentColors.get_color('primary')};")
        
        stats_layout.addWidget(self.total_label)
        stats_layout.addWidget(QLabel("  |  "))
        stats_layout.addWidget(self.valid_label)
        stats_layout.addWidget(QLabel("  |  "))
        stats_layout.addWidget(self.invalid_label)
        stats_layout.addWidget(QLabel("  |  "))
        stats_layout.addWidget(self.selected_label)
        stats_layout.addStretch()
        
        self.stats_card.setLayout(stats_layout)
        parent_layout.addWidget(self.stats_card)
        
    def create_history_table(self, parent_layout):
        """创建历史记录表格"""
        self.history_table = TableWidget()
        self.history_table.setColumnCount(4)  # 只保留4列：缩略图、标签、来源、文件名
        self.history_table.setHorizontalHeaderLabels([
            "缩略图", "标签", "来源", "文件名"
        ])
        
        # 设置表格属性
        self.history_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.history_table.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.history_table.setAlternatingRowColors(True)
        self.history_table.setSortingEnabled(True)
        
        # 启用水平滚动条
        self.history_table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.history_table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # 设置行高以适应缩略图
        self.history_table.verticalHeader().setDefaultSectionSize(80)
        self.history_table.verticalHeader().setMinimumSectionSize(80)
        
        # 设置表格的布局模式，确保列不会相互覆盖
        self.history_table.setWordWrap(False)
        self.history_table.setShowGrid(True)
        
        # 启用右键菜单
        self.history_table.setContextMenuPolicy(Qt.CustomContextMenu)
        
        # 设置列宽
        self.setup_table_columns()
        
        # 自定义表格样式
        self.history_table.setStyleSheet(f"""
            TableWidget {{
                border: 1px solid {FluentColors.get_color('border_primary')};
                border-radius: 12px;
                background-color: {FluentColors.get_color('bg_primary')};
                gridline-color: {FluentColors.get_color('border_secondary')};
                selection-background-color: rgba(79, 70, 229, 0.1);
                alternate-background-color: {FluentColors.get_color('bg_secondary')};
            }}
            TableWidget::item {{
                padding: 4px 8px;
                border: none;
                border-bottom: 1px solid {FluentColors.get_color('border_secondary')};
                color: {FluentColors.get_color('text_primary')};
            }}
            TableWidget::item:selected {{
                background-color: rgba(79, 70, 229, 0.15);
                color: {FluentColors.get_color('primary')};
            }}
            TableWidget::item:hover {{
                background-color: {FluentColors.get_color('bg_secondary')};
            }}
            QHeaderView::section {{
                background-color: {FluentColors.get_color('bg_tertiary')};
                color: {FluentColors.get_color('text_secondary')};
                padding: 10px 8px;
                border: none;
                border-bottom: 2px solid {FluentColors.get_color('border_primary')};
                border-right: 1px solid {FluentColors.get_color('border_secondary')};
                font-weight: 600;
                font-size: 13px;
                text-align: center;
            }}
            QHeaderView::section:hover {{
                background-color: {FluentColors.get_color('border_primary')};
            }}
            QHeaderView::section:first {{
                text-align: center;
            }}
        """)
        
        parent_layout.addWidget(self.history_table)
        
    def setup_table_columns(self):
        """设置表格列"""
        header = self.history_table.horizontalHeader()
        
        # 设置列的调整模式
        header.setSectionResizeMode(0, QHeaderView.Fixed)  # 缩略图列固定宽度
        header.setSectionResizeMode(1, QHeaderView.Interactive)  # 标签列可调整
        header.setSectionResizeMode(2, QHeaderView.Interactive)  # 来源列可调整
        header.setSectionResizeMode(3, QHeaderView.Interactive)  # 文件名列可调整
        
        # 设置初始列宽
        self.history_table.setColumnWidth(0, 100)  # 缩略图
        self.history_table.setColumnWidth(1, 120)  # 标签
        self.history_table.setColumnWidth(2, 120)  # 来源
        self.history_table.setColumnWidth(3, 250)  # 文件名（增加宽度）
        
        # 禁用最后一列的自动拉伸，避免影响前面列的显示
        header.setStretchLastSection(False)
        
    def setup_connections(self):
        """设置信号连接"""
        # 表格相关
        self.history_table.itemClicked.connect(self.on_item_clicked)
        self.history_table.itemSelectionChanged.connect(self.on_selection_changed)
        self.history_table.customContextMenuRequested.connect(self.show_context_menu)
        
        # 按钮相关
        self.delete_record_btn.clicked.connect(self.delete_selected_records)
        self.delete_all_btn.clicked.connect(self.delete_all_records)
        self.clean_invalid_btn.clicked.connect(self.clean_invalid_records)
        self.refresh_btn.clicked.connect(self.load_history)
        self.batch_export_btn.clicked.connect(self.batch_export_selected)
        
    def create_thumbnail_widget(self, file_path):
        """创建缩略图小部件"""
        # 创建容器widget，确保正确的布局
        container = QWidget()
        container.setFixedSize(95, 75)  # 设置容器固定尺寸
        container_layout = QHBoxLayout(container)
        container_layout.setContentsMargins(5, 2, 5, 2)
        container_layout.setAlignment(Qt.AlignCenter)
        
        thumbnail_label = QLabel()
        thumbnail_label.setAlignment(Qt.AlignCenter)
        thumbnail_label.setFixedSize(85, 71)  # 适配容器尺寸
        thumbnail_label.setScaledContents(False)
        
        # 设置基础样式
        thumbnail_label.setStyleSheet(f"""
            QLabel {{
                border: 1px solid {FluentColors.get_color('border_primary')};
                border-radius: 8px;
                background-color: {FluentColors.get_color('bg_secondary')};
                padding: 2px;
            }}
        """)
        
        if os.path.exists(file_path):
            try:
                # 加载并缩放图片
                pixmap = QPixmap(file_path)
                if not pixmap.isNull():
                    # 创建缩略图，保持宽高比
                    scaled_pixmap = pixmap.scaled(
                        81, 67, Qt.KeepAspectRatio, Qt.SmoothTransformation
                    )
                    thumbnail_label.setPixmap(scaled_pixmap)
                    thumbnail_label.setToolTip(f"图片尺寸: {pixmap.width()} × {pixmap.height()}")
                else:
                    # 图片加载失败
                    thumbnail_label.setText("🖼️\n无法\n加载")
                    thumbnail_label.setStyleSheet(f"""
                        QLabel {{
                            border: 1px solid {FluentColors.get_color('error')};
                            border-radius: 8px;
                            background-color: rgba(239, 68, 68, 0.05);
                            color: {FluentColors.get_color('error')};
                            font-size: 11px;
                            padding: 2px;
                        }}
                    """)
            except Exception as e:
                # 异常处理
                thumbnail_label.setText("❌\n错误")
                thumbnail_label.setStyleSheet(f"""
                    QLabel {{
                        border: 1px solid {FluentColors.get_color('error')};
                        border-radius: 8px;
                        background-color: rgba(239, 68, 68, 0.05);
                        color: {FluentColors.get_color('error')};
                        font-size: 11px;
                        padding: 2px;
                    }}
                """)
                print(f"创建缩略图时出错: {e}")
        else:
            # 文件不存在
            thumbnail_label.setText("❌\n文件\n不存在")
            thumbnail_label.setStyleSheet(f"""
                QLabel {{
                    border: 1px solid {FluentColors.get_color('error')};
                    border-radius: 8px;
                    background-color: rgba(239, 68, 68, 0.05);
                    color: {FluentColors.get_color('error')};
                    font-size: 10px;
                    padding: 2px;
                }}
            """)
        
        container_layout.addWidget(thumbnail_label)
        return container

    def load_history(self):
        """加载历史记录"""
        try:
            records = self.data_manager.get_all_records()
            self.history_records = records  # 存储完整记录用于删除操作
            
            self.history_table.setRowCount(len(records))
            
            valid_count = 0
            invalid_count = 0
            
            for i, record in enumerate(records):
                # 使用自定义文件名，如果没有则使用原始文件名
                display_name = record.get('custom_name', '') or os.path.basename(record.get('file_path', ''))
                file_path = record.get('file_path', '')
                
                # 检查文件状态
                file_exists = os.path.exists(file_path)
                if file_exists:
                    valid_count += 1
                    status_text = "✅"
                    status_tooltip = "文件存在"
                else:
                    invalid_count += 1
                    status_text = "❌"
                    status_tooltip = "文件不存在"
                
                tags = record.get('tags', '')
                
                # 获取生成来源
                generation_source = record.get('generation_source', 'Unknown')
                # 转换为中文显示
                source_display = {
                    'ComfyUI': 'ComfyUI',
                    'Stable Diffusion WebUI': 'SD WebUI',
                    'Unknown': '未知'
                }.get(generation_source, generation_source)
                

                
                # 创建缩略图小部件
                thumbnail_widget = self.create_thumbnail_widget(file_path)
                
                # 创建表格项并存储记录ID
                filename_item = QTableWidgetItem(display_name)
                filename_item.setData(Qt.UserRole, record.get('id'))  # 存储记录ID
                
                # 为无效文件设置特殊样式
                if not file_exists:
                    filename_item.setBackground(QColor(254, 242, 242))  # 很淡的红色背景
                    filename_item.setForeground(QColor(185, 28, 28))  # 深红色文字
                
                # 生成来源项
                source_item = QTableWidgetItem(source_display)
                if generation_source == 'ComfyUI':
                    source_item.setForeground(QColor(59, 130, 246))  # 蓝色
                elif generation_source == 'Stable Diffusion WebUI':
                    source_item.setForeground(QColor(16, 185, 129))  # 绿色
                else:
                    source_item.setForeground(QColor(156, 163, 175))  # 灰色
                
                tags_item = QTableWidgetItem(tags)
                
                # 设置工具提示显示完整信息
                if len(display_name) > 20:
                    filename_item.setToolTip(f"完整文件名: {display_name}\n文件路径: {file_path}")
                
                # 设置表格项（按新顺序：缩略图、标签、来源、文件名）
                self.history_table.setCellWidget(i, 0, thumbnail_widget)  # 缩略图（使用setCellWidget）
                self.history_table.setItem(i, 1, tags_item)      # 标签
                self.history_table.setItem(i, 2, source_item)    # 来源
                self.history_table.setItem(i, 3, filename_item)  # 文件名
                
            # 更新统计信息
            self.update_statistics(len(records), valid_count, invalid_count, 0)
            
        except Exception as e:
            print(f"加载历史记录失败: {str(e)}")
            
    def update_statistics(self, total, valid, invalid, selected):
        """更新统计信息"""
        self.total_label.setText(f"总记录: {total}")
        self.valid_label.setText(f"有效: {valid}")
        self.invalid_label.setText(f"无效: {invalid}")
        self.selected_label.setText(f"已选中: {selected}")
        
    def on_item_clicked(self, item):
        """表格项点击事件"""
        try:
            row = item.row()
            if 0 <= row < len(self.history_records):
                record = self.history_records[row]
                print(f"历史记录点击: 发出信号，文件名: {record.get('file_path', '未知')}")
                self.record_selected.emit(record)
        except Exception as e:
            print(f"点击记录时出错: {e}")
            
    def on_selection_changed(self):
        """选择改变事件"""
        selected_rows = self.history_table.selectionModel().selectedRows()
        selected_count = len(selected_rows)
        
        self.delete_record_btn.setEnabled(selected_count > 0)
        self.batch_export_btn.setEnabled(selected_count > 0)  # 启用/禁用批量导出按钮
        
        # 更新选中统计
        total = len(self.history_records)
        valid = sum(1 for record in self.history_records if os.path.exists(record.get('file_path', '')))
        invalid = total - valid
        self.update_statistics(total, valid, invalid, selected_count)
        
    def show_context_menu(self, position):
        """显示右键菜单"""
        item = self.history_table.itemAt(position)
        if item is None:
            return
            
        menu = QMenu(self)
        
        # 查看详情
        view_action = QAction("📄 查看详情", self)
        view_action.triggered.connect(lambda: self.on_item_clicked(item))
        menu.addAction(view_action)
        
        menu.addSeparator()
        
        # 删除记录
        delete_action = QAction("🗑️ 删除记录", self)
        delete_action.triggered.connect(self.delete_selected_records)
        menu.addAction(delete_action)
        
        # 检查文件状态
        row = item.row()
        if 0 <= row < len(self.history_records):
            record = self.history_records[row]
            file_path = record.get('file_path', '')
            
            if not os.path.exists(file_path):
                # 更新文件路径
                update_action = QAction("🔧 更新文件路径", self)
                update_action.triggered.connect(lambda: self.update_file_path(row))
                menu.addAction(update_action)
        
        menu.exec_(self.history_table.mapToGlobal(position))
        
    def delete_selected_records(self):
        """删除选中的记录"""
        selected_rows = self.history_table.selectionModel().selectedRows()
        if not selected_rows:
            return
            
        # 确认删除
        reply = QMessageBox.question(
            self, "确认删除", 
            f"确定要删除选中的 {len(selected_rows)} 条记录吗？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                # 获取要删除的记录ID
                record_ids = []
                for index in selected_rows:
                    row = index.row()
                    item = self.history_table.item(row, 3)  # 文件名列现在是第3列
                    if item:
                        record_id = item.data(Qt.UserRole)
                        if record_id:
                            record_ids.append(record_id)
                
                # 删除记录
                success_count = 0
                for record_id in record_ids:
                    if self.data_manager.delete_record(record_id):
                        success_count += 1
                
                # 重新加载表格
                self.load_history()
                
                QMessageBox.information(self, "删除成功", f"成功删除 {success_count} 条记录")
                
            except Exception as e:
                QMessageBox.critical(self, "删除失败", f"删除记录时出错: {str(e)}")
                
    def delete_all_records(self):
        """删除所有记录"""
        if not self.history_records:
            QMessageBox.information(self, "提示", "没有记录可删除")
            return
            
        # 确认删除
        reply = QMessageBox.question(
            self, "确认清空", 
            f"确定要删除所有 {len(self.history_records)} 条记录吗？此操作不可恢复！",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                if self.data_manager.clear_all_records():
                    self.load_history()
                    QMessageBox.information(self, "清空成功", "所有记录已删除")
                else:
                    QMessageBox.critical(self, "清空失败", "删除记录时出现错误")
            except Exception as e:
                QMessageBox.critical(self, "清空失败", f"删除记录时出错: {str(e)}")
                
    def clean_invalid_records(self):
        """清理无效记录"""
        try:
            # 找到所有无效记录
            invalid_records = []
            for record in self.history_records:
                file_path = record.get('file_path', '')
                if not os.path.exists(file_path):
                    invalid_records.append(record)
            
            if not invalid_records:
                QMessageBox.information(self, "提示", "没有发现无效记录")
                return
                
            # 确认删除
            reply = QMessageBox.question(
                self, "清理无效记录", 
                f"发现 {len(invalid_records)} 条无效记录（文件不存在），确定要删除吗？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                success_count = 0
                for record in invalid_records:
                    record_id = record.get('id')
                    if record_id and self.data_manager.delete_record(record_id):
                        success_count += 1
                
                # 重新加载表格
                self.load_history()
                
                QMessageBox.information(self, "清理完成", f"成功清理 {success_count} 条无效记录")
                
        except Exception as e:
            QMessageBox.critical(self, "清理失败", f"清理无效记录时出错: {str(e)}")
            
    def update_file_path(self, row):
        """更新文件路径"""
        if 0 <= row < len(self.history_records):
            record = self.history_records[row]
            old_path = record.get('file_path', '')
            
            file_dialog = QFileDialog()
            new_path, _ = file_dialog.getOpenFileName(
                self, "选择新的文件路径", os.path.dirname(old_path),
                "图片文件 (*.png *.jpg *.jpeg);;所有文件 (*.*)"
            )
            
            if new_path:
                try:
                    # 更新数据库中的文件路径
                    record_id = record.get('id')
                    if self.data_manager.update_record_path(record_id, new_path):
                        # 重新加载表格
                        self.load_history()
                        QMessageBox.information(self, "更新成功", "文件路径已更新")
                    else:
                        QMessageBox.critical(self, "更新失败", "更新文件路径失败")
                except Exception as e:
                    QMessageBox.critical(self, "更新失败", f"更新文件路径时出错: {str(e)}")
                    
    def batch_export_selected(self):
        """批量导出选中的记录"""
        selected_rows = self.history_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.information(self, "提示", "请先选择要导出的记录")
            return
            
        # 获取选中的记录
        selected_records = []
        for index in selected_rows:
            row = index.row()
            if 0 <= row < len(self.history_records):
                selected_records.append(self.history_records[row])
        
        if not selected_records:
            QMessageBox.information(self, "提示", "没有有效的记录可导出")
            return
            
        # 导入批量导出对话框
        from .fluent_batch_export_dialog import FluentBatchExportDialog
        
        dialog = FluentBatchExportDialog(selected_records, self)
        dialog.exec_()
    
 