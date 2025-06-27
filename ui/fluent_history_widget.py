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
        

        
        # 历史记录表格
        self.create_history_table(main_layout)
        
        main_widget.setLayout(main_layout)
        
        # 设置卡片布局
        card_layout = QVBoxLayout()
        card_layout.setContentsMargins(0, 0, 0, 0)  # 移除边距
        card_layout.addWidget(main_widget, 1)  # 添加拉伸因子
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
        
        # 修改：增加行高以容纳更多内容，确保标签信息能够显示
        self.history_table.verticalHeader().setDefaultSectionSize(120)  # 从80增加到120
        self.history_table.verticalHeader().setMinimumSectionSize(100)  # 从80增加到100
        
        # 修改：启用文字换行，让内容能够完整显示
        self.history_table.setWordWrap(True)  # 从False改为True
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
            records = self.data_manager.get_all_records()
            self.history_records = records  # 存储完整记录用于删除操作
            
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
                

            
        except Exception as e:
            print(f"加载历史记录失败: {str(e)}")
            

        
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
                    item = self.history_table.item(row, 1)  # 生成信息列现在是第1列，存储记录ID
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

    def create_generation_info_item(self, record):
        """创建生成信息项，显示格式化的生成参数"""
        info_parts = []
        
        # 1. 标签信息 - 提升优先级到第一位
        tags = record.get('tags', '').strip()
        if tags:
            # 限制标签显示长度并美化
            if len(tags) > 40:
                tags_display = tags[:37] + '...'
            else:
                tags_display = tags
            info_parts.append(f"🏷️ {tags_display}")
        
        # 2. 模型信息 - 简化显示
        model = record.get('model', '').strip()
        if model:
            # 截取模型名称，避免过长
            model_display = model.split('/')[-1] if '/' in model else model  # 取文件名部分
            # 移除常见的文件扩展名
            if model_display.endswith('.safetensors'):
                model_display = model_display[:-12]
            elif model_display.endswith('.ckpt'):
                model_display = model_display[:-5]
            
            if len(model_display) > 25:  # 进一步缩短显示长度
                model_display = model_display[:22] + '...'
            info_parts.append(f"🤖 {model_display}")
        
        # 3. 核心生成参数 - 合并显示
        param_parts = []
        sampler = record.get('sampler', '').strip()
        steps = record.get('steps')
        cfg_scale = record.get('cfg_scale')
        seed = record.get('seed')
        
        if sampler:
            # 简化采样器名称显示
            sampler_short = sampler.replace('_', ' ').replace('DPM++', 'DPM++').title()
            if len(sampler_short) > 10:
                sampler_short = sampler_short[:7] + '...'
            param_parts.append(f"{sampler_short}")
        if steps:
            param_parts.append(f"{steps}步")
        if cfg_scale:
            param_parts.append(f"CFG{cfg_scale}")
        if seed:
            seed_display = str(seed)[-4:] if len(str(seed)) > 4 else str(seed)
            param_parts.append(f"🎲{seed_display}")
        
        if param_parts:
            info_parts.append(f"⚙️ {' • '.join(param_parts)}")
        
        # 4. LoRA信息 - 简化显示
        lora_info_str = record.get('lora_info', '')
        if lora_info_str and len(info_parts) < 4:  # 只在有空间时显示LoRA
            lora_display = self.format_lora_info(lora_info_str)
            if lora_display:
                info_parts.append(f"🎯 {lora_display}")
        
        # 合并所有信息
        full_text = '\n'.join(info_parts) if info_parts else '暂无生成信息'
        
        # 创建完整的工具提示信息
        tooltip_parts = []
        if tags:
            tooltip_parts.append(f"标签: {tags}")
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
    
 