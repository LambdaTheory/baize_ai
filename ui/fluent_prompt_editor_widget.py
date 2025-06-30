#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fluent Design 提示词修改组件 - 主容器
整合所有子组件，提供数据管理和界面控制
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                            QMessageBox, QInputDialog)
from PyQt5.QtCore import Qt, QTimer
from qfluentwidgets import (ScrollArea, StrongBodyLabel, PrimaryPushButton, 
                           PushButton, InfoBar, InfoBarPosition)

from .fluent_styles import FluentColors, FluentSpacing
from .fluent_prompt_components import AccordionCard
from .fluent_prompt_editor_panel import PromptEditorPanel
from core.data_manager import DataManager


class FluentPromptEditorWidget(ScrollArea):
    """Fluent Design 提示词修改组件主容器"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.editors = []  # 存储编辑器信息
        self.data_manager = DataManager()
        
        # 自动保存设置
        self.auto_save_timer = QTimer()
        self.auto_save_timer.timeout.connect(self.auto_save)
        self.auto_save_timer.start(10000)  # 每10秒自动保存
        
        self.init_ui()
        self.load_history_data()
        
    def init_ui(self):
        """初始化UI"""
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # 主容器
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(FluentSpacing.LG, FluentSpacing.LG, 
                                     FluentSpacing.LG, FluentSpacing.LG)
        main_layout.setSpacing(FluentSpacing.MD)
        
        # 顶部控制栏
        header_layout = self.create_header()
        main_layout.addLayout(header_layout)
        
        # 手风琴容器
        self.accordion_layout = QVBoxLayout()
        self.accordion_layout.setSpacing(FluentSpacing.SM)
        main_layout.addLayout(self.accordion_layout)
        
        # 弹性空间
        main_layout.addStretch()
        
        main_widget.setLayout(main_layout)
        self.setWidget(main_widget)
        
    def create_header(self):
        """创建顶部控制栏"""
        layout = QHBoxLayout()
        
        # 标题
        title_label = StrongBodyLabel("AI提示词管理器")
        title_label.setStyleSheet(f"""
            QLabel {{
                font-size: 24px;
                font-weight: 600;
                color: {FluentColors.get_color('text_primary')};
            }}
        """)
        
        # 按钮
        self.save_btn = PushButton("💾 保存")
        self.save_btn.clicked.connect(self.manual_save)
        self.save_btn.setFixedHeight(36)
        self.save_btn.setToolTip("手动保存当前数据")
        
        self.add_btn = PrimaryPushButton("+ 新增场景")
        self.add_btn.clicked.connect(self.add_scene)
        self.add_btn.setFixedHeight(36)
        
        layout.addWidget(title_label)
        layout.addStretch()
        layout.addWidget(self.save_btn)
        layout.addWidget(self.add_btn)
        
        return layout
        
    def add_scene(self):
        """添加新场景"""
        text, ok = QInputDialog.getText(
            self, "新增场景", "请输入场景名称:", text="新场景"
        )
        
        if ok and text.strip():
            self.create_editor_accordion(text.strip())
            self.save_history_data()
        elif ok:
            self.create_editor_accordion(f"场景 {len(self.editors) + 1}")
            self.save_history_data()
            
    def create_editor_accordion(self, title):
        """创建编辑器手风琴"""
        # 创建手风琴卡片
        accordion = AccordionCard(title)
        
        # 创建编辑面板
        editor_panel = PromptEditorPanel(title)
        editor_panel.parent_widget = self
        
        # 创建内容容器
        content_widget = QWidget()
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(8, 8, 8, 8)
        content_layout.setSpacing(8)
        
        # 控制按钮
        control_layout = self.create_control_buttons(accordion, editor_panel)
        content_layout.addLayout(control_layout)
        content_layout.addWidget(editor_panel)
        
        content_widget.setLayout(content_layout)
        accordion.setContent(content_widget)
        
        # 添加到布局
        self.accordion_layout.addWidget(accordion)
        
        # 保存编辑器信息
        editor_info = {
            'accordion': accordion,
            'panel': editor_panel,
            'title': title
        }
        self.editors.append(editor_info)
        
        # 默认展开第一个
        if len(self.editors) == 1:
            accordion.setExpanded(True)
            
        return editor_panel
        
    def create_control_buttons(self, accordion, editor_panel):
        """创建控制按钮"""
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 重命名按钮
        rename_btn = PushButton("🏷️")
        rename_btn.setFixedSize(24, 24)
        rename_btn.setToolTip("重命名场景")
        rename_btn.clicked.connect(lambda: self.rename_scene(accordion, editor_panel))
        
        # 删除按钮
        delete_btn = PushButton("🗑️")
        delete_btn.setFixedSize(24, 24)
        delete_btn.setToolTip("删除场景")
        delete_btn.setStyleSheet(f"""
            QPushButton:hover {{
                background-color: {FluentColors.get_color('error')};
                color: white;
            }}
        """)
        delete_btn.clicked.connect(lambda: self.delete_scene(accordion, editor_panel))
        
        layout.addStretch()
        layout.addWidget(rename_btn)
        layout.addWidget(delete_btn)
        
        return layout
        
    def rename_scene(self, accordion, editor_panel):
        """重命名场景"""
        current_title = accordion.title()
        text, ok = QInputDialog.getText(
            self, "重命名场景", "请输入新名称:", text=current_title
        )
        
        if ok and text.strip():
            new_title = text.strip()
            accordion.setTitle(new_title)
            editor_panel.title = new_title
            
            # 更新存储的信息
            for editor_info in self.editors:
                if editor_info['accordion'] == accordion:
                    editor_info['title'] = new_title
                    break
                    
            self.save_history_data()
            
    def delete_scene(self, accordion, editor_panel):
        """删除场景"""
        if len(self.editors) <= 1:
            InfoBar.warning(
                title="提示", content="至少需要保留一个场景",
                orient=Qt.Horizontal, isClosable=True,
                position=InfoBarPosition.TOP, duration=2000, parent=self
            )
            return
            
        # 确认删除
        result = QMessageBox.question(
            self, "确认删除", 
            f"确定要删除场景 \"{accordion.title()}\" 吗？",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if result == QMessageBox.Yes:
            # 从布局移除
            self.accordion_layout.removeWidget(accordion)
            accordion.setParent(None)
            accordion.deleteLater()
            
            # 从列表移除
            self.editors = [e for e in self.editors if e['accordion'] != accordion]
            
            InfoBar.success(
                title="删除成功", content="场景已删除",
                orient=Qt.Horizontal, isClosable=True,
                position=InfoBarPosition.TOP, duration=1500, parent=self
            )
            
            self.save_history_data()
            
    def load_history_data(self):
        """加载历史数据"""
        try:
            data = self.data_manager.load_prompt_data()
            
            if data and 'scenes' in data and data['scenes']:
                print(f"加载 {len(data['scenes'])} 个历史场景")
                
                for scene in data['scenes']:
                    title = scene.get('title', '未命名场景')
                    english_prompts = scene.get('english_prompts', [])
                    
                    editor_panel = self.create_editor_accordion(title)
                    editor_panel.set_prompts(english_prompts)
                    
            else:
                # 创建默认场景
                print("创建默认场景")
                default_data = self.data_manager.get_default_prompt_data()
                
                for scene in default_data['scenes']:
                    title = scene.get('title', '通用提示词')
                    english_prompts = scene.get('english_prompts', [])
                    
                    editor_panel = self.create_editor_accordion(title)
                    editor_panel.set_prompts(english_prompts)
                    
        except Exception as e:
            print(f"加载历史数据失败: {e}")
            # 创建默认场景
            self.create_editor_accordion("通用提示词")
            
    def save_history_data(self):
        """保存历史数据"""
        try:
            scenes_data = []
            
            for editor_info in self.editors:
                title = editor_info['title']
                prompts = editor_info['panel'].get_prompts()
                
                scene_data = {
                    'title': title,
                    'english_prompts': prompts.get('english', [])
                }
                scenes_data.append(scene_data)
                
            data = {'scenes': scenes_data}
            success = self.data_manager.save_prompt_data(data)
            
            if success:
                print(f"保存成功: {len(scenes_data)} 个场景")
            else:
                print("保存失败")
                
        except Exception as e:
            print(f"保存数据失败: {e}")
            
    def manual_save(self):
        """手动保存"""
        self.save_history_data()
        InfoBar.success(
            title="保存成功", content="数据已保存到本地",
            orient=Qt.Horizontal, isClosable=True,
            position=InfoBarPosition.TOP, duration=2000, parent=self
        )
        
    def auto_save(self):
        """自动保存"""
        self.save_history_data()
        print("自动保存完成")
        
    def get_all_prompts(self):
        """获取所有场景的提示词"""
        all_prompts = {}
        for editor_info in self.editors:
            title = editor_info['title']
            prompts = editor_info['panel'].get_prompts()
            all_prompts[title] = prompts
        return all_prompts 