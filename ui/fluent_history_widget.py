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
                           SubtitleLabel, BodyLabel, TransparentPushButton,
                           SearchLineEdit)
from .fluent_styles import FluentTheme, FluentIcons, FluentColors, FluentSpacing


class FluentHistoryWidget(CardWidget):
    """Fluent Design 历史记录组件"""
    
    # 信号定义
    record_selected = pyqtSignal(dict)  # 选中记录时发出信号
    
    def __init__(self, data_manager, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.history_records = []  # 存储历史记录数据
        self.filtered_records = []  # 存储过滤后的记录数据
        self.current_search_text = ""  # 当前搜索文本
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
        
        # 添加搜索框
        self.create_search_area(main_layout)
        
        # 操作按钮区域
        self.create_action_buttons(main_layout)
        

        
        # 历史记录表格
        self.create_history_table(main_layout)
        
        main_widget.setLayout(main_layout)
        
        # 设置卡片布局
        card_layout = QVBoxLayout()
        card_layout.setContentsMargins(0, 0, 0, 0)  # 移除边距
        card_layout.addWidget(main_widget, 1)  # 添加拉伸因子
        self.setLayout(card_layout)
        
    def create_search_area(self, parent_layout):
        """创建搜索区域"""
        search_layout = QHBoxLayout()
        search_layout.setSpacing(FluentSpacing.SM)
        
        # 搜索框
        self.search_edit = SearchLineEdit()
        self.search_edit.setPlaceholderText("搜索历史记录（支持多个关键词，用空格分隔）...")
        self.search_edit.setFixedHeight(36)
        self.search_edit.setMinimumWidth(300)
        
        # 设置搜索框样式
        self.search_edit.setStyleSheet(f"""
            SearchLineEdit {{
                border: 1px solid {FluentColors.get_color('border_primary')};
                border-radius: 8px;
                padding: 6px 12px;
                background-color: {FluentColors.get_color('bg_primary')};
                color: {FluentColors.get_color('text_primary')};
                font-size: 13px;
            }}
            SearchLineEdit:focus {{
                border: 2px solid {FluentColors.get_color('primary')};
                background-color: {FluentColors.get_color('bg_primary')};
            }}
        """)
        
        # 搜索按钮
        self.search_btn = PushButton("搜索")
        self.search_btn.setFixedHeight(36)
        self.search_btn.setMinimumWidth(60)
        self.search_btn.setEnabled(False)  # 初始禁用
        
        # 设置搜索按钮样式
        self.search_btn.setStyleSheet(f"""
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
        
        # 清除搜索按钮
        self.clear_search_btn = PushButton("清除")
        self.clear_search_btn.setFixedHeight(36)
        self.clear_search_btn.setMinimumWidth(60)
        self.clear_search_btn.setEnabled(False)  # 初始禁用
        
        search_layout.addWidget(self.search_edit)
        search_layout.addWidget(self.search_btn)
        search_layout.addWidget(self.clear_search_btn)
        search_layout.addStretch()
        
        parent_layout.addLayout(search_layout)
        
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
        button_layout.addWidget(self.delete_all_btn)
        button_layout.addStretch()
        
        parent_layout.addLayout(button_layout)
        

        
    def create_history_table(self, parent_layout):
        """创建历史记录表格"""
        self.history_table = TableWidget()
        self.history_table.setColumnCount(3)  # 只保留3列：缩略图、生成信息、来源
        self.history_table.setHorizontalHeaderLabels([
            "缩略图", "生成信息", "来源"
        ])
        
        # 设置表格属性
        self.history_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.history_table.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.history_table.setAlternatingRowColors(True)
        self.history_table.setSortingEnabled(False)  # 禁用排序避免数据错位
        
        # 启用水平滚动条
        self.history_table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.history_table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # 保持增加的行高以容纳更多内容
        self.history_table.verticalHeader().setDefaultSectionSize(120)
        self.history_table.verticalHeader().setMinimumSectionSize(100)
        
        # 禁用文字换行，每行信息单行显示，超出用省略号
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
        
        parent_layout.addWidget(self.history_table, 1)  # 添加拉伸因子，让表格占用剩余空间
        
    def setup_table_columns(self):
        """设置表格列"""
        header = self.history_table.horizontalHeader()
        
        # 设置列的调整模式
        header.setSectionResizeMode(0, QHeaderView.Fixed)  # 缩略图列固定宽度
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # 生成信息列自动拉伸，占用大部分空间
        header.setSectionResizeMode(2, QHeaderView.Fixed)  # 来源列固定宽度
        
        # 设置初始列宽
        self.history_table.setColumnWidth(0, 100)  # 缩略图固定宽度
        self.history_table.setColumnWidth(2, 120)  # 来源列固定宽度
        # 生成信息列的宽度由拉伸模式自动管理
        
        # 启用最后一列的自动拉伸，让表格充满整个宽度
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
        self.refresh_btn.clicked.connect(self.load_history)
        self.batch_export_btn.clicked.connect(self.batch_export_selected)
        
        # 搜索相关
        self.search_edit.textChanged.connect(self.on_search_text_changed)  # 只用于启用/禁用按钮
        self.search_edit.returnPressed.connect(self.perform_search)  # 回车搜索
        self.search_btn.clicked.connect(self.perform_search)  # 点击搜索
        self.clear_search_btn.clicked.connect(self.clear_search)
        
    def create_thumbnail_widget(self, file_path):
        """创建缩略图小部件"""
        # 创建容器widget，确保正确的布局，适应新的行高
        container = QWidget()
        container.setFixedSize(95, 115)  # 从75增加到115，适应120行高
        container_layout = QHBoxLayout(container)
        container_layout.setContentsMargins(5, 2, 5, 2)
        container_layout.setAlignment(Qt.AlignCenter)
        
        thumbnail_label = QLabel()
        thumbnail_label.setAlignment(Qt.AlignCenter)
        thumbnail_label.setFixedSize(85, 111)  # 从71增加到111，适应新容器
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
                    # 创建缩略图，保持宽高比，适应新尺寸
                    scaled_pixmap = pixmap.scaled(
                        81, 107, Qt.KeepAspectRatio, Qt.SmoothTransformation  # 从67增加到107
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
            # 添加调试信息
            print(f"[调试] data_manager 类型: {type(self.data_manager)}")
            print(f"[调试] data_manager 对象: {self.data_manager}")
            print(f"[调试] data_manager 是否有 get_all_records 方法: {hasattr(self.data_manager, 'get_all_records')}")
            
            if not hasattr(self.data_manager, 'get_all_records'):
                print(f"[错误] data_manager 对象没有 get_all_records 方法!")
                print(f"[错误] data_manager 可用方法: {[method for method in dir(self.data_manager) if not method.startswith('_')]}")
                return
            
            records = self.data_manager.get_all_records()
            self.history_records = records  # 存储完整记录用于删除操作
            
            # 如果当前有搜索条件，重新应用搜索过滤
            if self.current_search_text:
                self.apply_search_filter()
            else:
                self.filtered_records = self.history_records.copy()
                self.display_records(self.filtered_records)
            
        except Exception as e:
            print(f"加载历史记录失败: {str(e)}")
            import traceback
            traceback.print_exc()
            
    def display_records(self, records):
        """显示记录"""
        self.history_table.setRowCount(len(records))
        
        valid_count = 0
        invalid_count = 0
        
        for i, record in enumerate(records):
            file_path = record.get('file_path', '')
            
            # 检查文件状态
            file_exists = os.path.exists(file_path)
            if file_exists:
                valid_count += 1
            else:
                invalid_count += 1
            
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
            
            # 创建富文本生成信息项（替换原来的tags）
            generation_info_item = self.create_generation_info_item(record)
            
            # 生成来源项
            source_item = QTableWidgetItem(source_display)
            if generation_source == 'ComfyUI':
                source_item.setForeground(QColor(59, 130, 246))  # 蓝色
            elif generation_source == 'Stable Diffusion WebUI':
                source_item.setForeground(QColor(16, 185, 129))  # 绿色
            else:
                source_item.setForeground(QColor(156, 163, 175))  # 灰色
            
            # 为无效文件设置特殊样式
            if not file_exists:
                generation_info_item.setBackground(QColor(254, 242, 242))  # 很淡的红色背景
                generation_info_item.setForeground(QColor(185, 28, 28))  # 深红色文字
                source_item.setBackground(QColor(254, 242, 242))  # 很淡的红色背景
                source_item.setForeground(QColor(185, 28, 28))  # 深红色文字
            
            # 设置表格项（按新顺序：缩略图、生成信息、来源）
            self.history_table.setCellWidget(i, 0, thumbnail_widget)  # 缩略图（使用setCellWidget）
            self.history_table.setItem(i, 1, generation_info_item)    # 生成信息（替换原来的标签）
            self.history_table.setItem(i, 2, source_item)             # 来源
            
            # 为了保持兼容性，将记录ID存储在生成信息项中
            generation_info_item.setData(Qt.UserRole, record.get('id'))
            

        
    def on_item_clicked(self, item):
        """表格项点击事件"""
        try:
            row = item.row()
            # 注意：这里需要使用过滤后的记录
            if 0 <= row < len(self.filtered_records):
                record = self.filtered_records[row]
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
        if 0 <= row < len(self.filtered_records):
            record = self.filtered_records[row]
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
                    # 使用过滤后的记录获取正确的记录
                    if 0 <= row < len(self.filtered_records):
                        record = self.filtered_records[row]
                        record_id = record.get('id')
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
                

            
    def update_file_path(self, row):
        """更新文件路径"""
        if 0 <= row < len(self.filtered_records):
            record = self.filtered_records[row]
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
            
        # 获取选中的记录（使用过滤后的记录）
        selected_records = []
        for index in selected_rows:
            row = index.row()
            if 0 <= row < len(self.filtered_records):
                selected_records.append(self.filtered_records[row])
        
        if not selected_records:
            QMessageBox.information(self, "提示", "没有有效的记录可导出")
            return
            
        # 导入批量导出对话框
        from .fluent_batch_export_dialog import FluentBatchExportDialog
        
        dialog = FluentBatchExportDialog(selected_records, self)
        dialog.exec_()

    def create_generation_info_item(self, record):
        """创建生成信息项，显示格式化的生成参数"""
        info_parts = []
        
        # 检查是否有标签，如果有标签则优先保证标签显示
        tags = record.get('tags', '').strip()
        has_tags = bool(tags)
        
        # 1. 模型信息 - 优先显示，单行显示
        model = record.get('model', '').strip()
        if model:
            model_display = model.split('/')[-1] if '/' in model else model
            if model_display.endswith('.safetensors'):
                model_display = model_display[:-12]
            elif model_display.endswith('.ckpt'):
                model_display = model_display[:-5]
            
            # 限制长度确保单行显示，超出用省略号
            if len(model_display) > 30:
                model_display = model_display[:27] + '...'
            info_parts.append(f"🤖 {model_display}")
        
        # 2. LoRA信息 - 如果没有标签或空间足够则显示，单行显示
        lora_info_str = record.get('lora_info', '')
        if lora_info_str and (not has_tags or len(info_parts) < 3):
            lora_display = self.format_lora_info(lora_info_str)
            if lora_display:
                # 限制长度确保单行显示
                if len(lora_display) > 25:
                    lora_display = lora_display[:22] + '...'
                info_parts.append(f"🎯 LoRA: {lora_display}")
        
        # 3. 核心生成参数 - 合并在一行显示
        param_parts = []
        sampler = record.get('sampler', '').strip()
        steps = record.get('steps')
        cfg_scale = record.get('cfg_scale')
        
        if sampler:
            sampler_short = sampler.replace('_', ' ').replace('DPM++', 'DPM++').title()
            if len(sampler_short) > 12:
                sampler_short = sampler_short[:9] + '...'
            param_parts.append(f"{sampler_short}")
        if steps:
            param_parts.append(f"{steps}步")
        if cfg_scale:
            param_parts.append(f"CFG{cfg_scale}")
        
        if param_parts:
            param_line = f"⚙️ {' • '.join(param_parts)}"
            # 限制参数行长度，确保单行显示
            if len(param_line) > 35:
                param_line = param_line[:32] + '...'
            info_parts.append(param_line)
        
        # 4. 种子信息 - 如果没有标签或空间足够则显示，单行显示
        seed = record.get('seed')
        if seed and (not has_tags or len(info_parts) < 4):
            seed_display = str(seed)[-6:] if len(str(seed)) > 6 else str(seed)
            info_parts.append(f"🎲 {seed_display}")
        
        # 5. 标签信息 - 如果有标签必须显示，单行显示
        if has_tags:
            # 限制标签显示长度，确保单行显示，超出用省略号
            if len(tags) > 35:
                tags_display = tags[:32] + '...'
            else:
                tags_display = tags
            info_parts.append(f"🏷️ {tags_display}")
        
        # 合并所有信息，每行一个，单行显示
        full_text = '\n'.join(info_parts) if info_parts else '暂无生成信息'
        
        # 创建完整的工具提示信息
        tooltip_parts = []
        if model:
            tooltip_parts.append(f"模型: {record.get('model', '')}")
        if lora_info_str:
            tooltip_parts.append(f"LoRA: {self.format_lora_info_detailed(lora_info_str)}")
        if sampler:
            tooltip_parts.append(f"采样器: {sampler}")
        if steps:
            tooltip_parts.append(f"步数: {steps}")
        if cfg_scale:
            tooltip_parts.append(f"CFG Scale: {cfg_scale}")
        if seed:
            tooltip_parts.append(f"种子: {seed}")
        if tags:
            tooltip_parts.append(f"标签: {tags}")
        
        full_tooltip = '\n'.join(tooltip_parts) if tooltip_parts else '暂无生成信息'
        
        # 创建表格项
        item = QTableWidgetItem(full_text)
        item.setToolTip(full_tooltip)  # 设置详细信息为提示
        
        # 设置字体和样式
        font = item.font()
        font.setPointSize(9)  # 稍小的字体
        item.setFont(font)
        
        return item
    
    def format_lora_info(self, lora_info_str):
        """格式化LoRA信息为简洁显示"""
        if not lora_info_str:
            return ""
        
        try:
            import json
            lora_info = json.loads(lora_info_str)
            
            if isinstance(lora_info, dict) and 'loras' in lora_info and lora_info['loras']:
                lora_names = []
                for lora in lora_info['loras']:
                    if isinstance(lora, dict):
                        name = lora.get('name', '未知')
                        weight = lora.get('weight', 1.0)
                        # 只显示LoRA名称和权重，格式简洁
                        lora_names.append(f"{name}({weight})")
                
                if lora_names:
                    # 限制显示的LoRA数量，避免过长
                    if len(lora_names) > 2:
                        display_loras = lora_names[:2] + [f"等{len(lora_names)}个"]
                    else:
                        display_loras = lora_names
                    return ", ".join(display_loras)
            
            elif isinstance(lora_info, dict) and 'raw_lora_text' in lora_info:
                raw_text = lora_info['raw_lora_text']
                # 限制原始文本长度
                if len(raw_text) > 30:
                    return raw_text[:27] + '...'
                return raw_text
            
            # 其他格式的处理
            elif isinstance(lora_info, dict):
                lora_items = []
                count = 0
                for name, weight in lora_info.items():
                    if name != 'loras':  # 避免显示结构键
                        lora_items.append(f"{name}({weight})")
                        count += 1
                        if count >= 2:  # 最多显示2个
                            break
                
                if lora_items:
                    if len(lora_info) > 2:
                        lora_items.append(f"等{len(lora_info)}个")
                    return ", ".join(lora_items)
            
            return "有LoRA"
            
        except Exception as e:
            print(f"格式化LoRA信息失败: {e}")
            return "LoRA解析错误"
    
    def format_lora_info_detailed(self, lora_info_str):
        """格式化LoRA信息为详细显示（用于工具提示）"""
        if not lora_info_str:
            return "无LoRA信息"
        
        try:
            import json
            lora_info = json.loads(lora_info_str)
            
            if isinstance(lora_info, dict) and 'loras' in lora_info and lora_info['loras']:
                lora_details = []
                for i, lora in enumerate(lora_info['loras'], 1):
                    if isinstance(lora, dict):
                        name = lora.get('name', '未知')
                        weight = lora.get('weight', 1.0)
                        hash_val = lora.get('hash', '')
                        detail = f"{i}. {name} (权重: {weight})"
                        if hash_val:
                            detail += f" [Hash: {hash_val[:8]}...]"
                        lora_details.append(detail)
                return '\n'.join(lora_details)
            
            elif isinstance(lora_info, dict) and 'raw_lora_text' in lora_info:
                return lora_info['raw_lora_text']
            
            elif isinstance(lora_info, dict):
                lora_details = []
                for i, (name, weight) in enumerate(lora_info.items(), 1):
                    if name != 'loras':  # 避免显示结构键
                        lora_details.append(f"{i}. {name} (权重: {weight})")
                return '\n'.join(lora_details)
            
            return str(lora_info)
            
        except Exception as e:
            print(f"格式化详细LoRA信息失败: {e}")
            return "LoRA信息解析错误"
    
    def on_search_text_changed(self, text):
        """搜索文本改变事件（仅用于控制按钮状态）"""
        text = text.strip()
        has_text = bool(text)
        self.search_btn.setEnabled(has_text)
        self.clear_search_btn.setEnabled(has_text or bool(self.current_search_text))
        
    def perform_search(self):
        """执行搜索"""
        search_text = self.search_edit.text().strip()
        self.current_search_text = search_text
        
        if search_text:
            self.apply_search_filter()
        else:
            # 如果搜索文本为空，显示所有记录
            self.filtered_records = self.history_records.copy()
            self.display_records(self.filtered_records)
            
    def apply_search_filter(self):
        """应用搜索过滤"""
        if not self.current_search_text or not self.history_records:
            self.filtered_records = self.history_records.copy()
            self.display_records(self.filtered_records)
            return
        
        # 分割搜索关键词（支持空格、逗号、分号分隔）
        import re
        keywords = re.split(r'[,，;；\s]+', self.current_search_text.strip())
        keywords = [kw.lower().strip() for kw in keywords if kw.strip()]
        
        if not keywords:
            self.filtered_records = self.history_records.copy()
            self.display_records(self.filtered_records)
            return
        
        self.filtered_records = []
        
        for record in self.history_records:
            # 收集所有搜索字段
            search_fields = [
                record.get('file_name', ''),
                record.get('model', ''),
                record.get('tags', ''),
                record.get('prompt', ''),
                record.get('negative_prompt', ''),
                record.get('sampler', ''),
                record.get('notes', ''),
                record.get('generation_source', ''),
                str(record.get('steps', '')),
                str(record.get('cfg_scale', '')),
                str(record.get('seed', ''))
            ]
            
            # 搜索LoRA信息
            lora_info = record.get('lora_info', '')
            if lora_info:
                try:
                    import json
                    if isinstance(lora_info, str) and lora_info.strip():
                        lora_data = json.loads(lora_info)
                        if isinstance(lora_data, dict) and 'loras' in lora_data:
                            # 正确的LoRA数据结构
                            for lora_item in lora_data['loras']:
                                if isinstance(lora_item, dict) and 'name' in lora_item:
                                    search_fields.append(lora_item['name'])
                        elif isinstance(lora_data, dict):
                            # 备用：直接从字典键中查找
                            for key in lora_data.keys():
                                if key != 'loras':
                                    search_fields.append(key)
                except Exception:
                    # 如果解析失败，直接添加原始字符串
                    search_fields.append(lora_info)
            
            # 将所有字段合并为一个搜索文本（小写）
            combined_text = ' '.join(str(field).lower() for field in search_fields if field)
            
            # 检查所有关键词是否都匹配（AND逻辑）
            all_keywords_match = True
            for keyword in keywords:
                if keyword not in combined_text:
                    all_keywords_match = False
                    break
            
            if all_keywords_match:
                self.filtered_records.append(record)
        
        # 显示过滤后的记录
        self.display_records(self.filtered_records)
        
        # 打印搜索结果信息
        keywords_display = ', '.join(keywords)
        print(f"搜索结果: 找到 {len(self.filtered_records)} 条匹配关键词 [{keywords_display}] 的记录")
        
    def clear_search(self):
        """清除搜索"""
        self.search_edit.clear()
        self.current_search_text = ""
        self.search_btn.setEnabled(False)
        self.clear_search_btn.setEnabled(False)
        self.filtered_records = self.history_records.copy()
        self.display_records(self.filtered_records)
 