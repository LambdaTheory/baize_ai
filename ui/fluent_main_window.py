#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fluent Design 主窗口
使用PyQt-Fluent-Widgets组件库
"""

import os
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QSplitter, QApplication, QGridLayout, QLabel,
                            QSizePolicy, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal, QSize, QThread, QObject
from PyQt5.QtGui import QPixmap, QIcon, QDragEnterEvent, QDropEvent, QPainter, QBrush, QColor, QPen, QFont, QLinearGradient

from qfluentwidgets import (NavigationInterface, NavigationItemPosition, FluentWindow,
                           SplashScreen, InfoBar, InfoBarPosition, MessageBox,
                           NavigationWidget, qrouter, CardWidget, SmoothScrollArea,
                           FlowLayout, PivotItem, Pivot, setTheme, Theme, isDarkTheme,
                           ComboBox, EditableComboBox, BodyLabel, TitleLabel, PrimaryPushButton)

from core.image_reader import ImageInfoReader
from core.data_manager import DataManager
from core.html_exporter import HTMLExporter
from core.batch_processor import BatchProcessor
from .fluent_styles import FluentTheme, FluentIcons, FluentColors, FluentSpacing
from .fluent_drop_area import FluentDropArea
from .fluent_image_info_widget import FluentImageInfoWidget
from .fluent_history_widget import FluentHistoryWidget
from .fluent_prompt_editor_widget import FluentPromptEditorWidget
from .fluent_prompt_reverser_widget import FluentPromptReverserWidget
from .fluent_settings_widget import FluentSettingsWidget
from .fluent_activation_dialog import FluentActivationDialog
from .fluent_drag_components import DragOverlay
from .fluent_ai_worker import AITagWorker
from .fluent_gallery_components import HighlightEditableComboBox, FluentImageCard, FluentGalleryWidget
from .fluent_extraction_layout import FluentExtractionLayout
from .fluent_event_handlers import FluentEventHandlers
from .fluent_business_logic import FluentBusinessLogic
from .fluent_image_display import FluentImageDisplay
from .fluent_export_share import FluentExportShare
from .fluent_license_manager import FluentLicenseManager
from .fluent_interface_creator import FluentInterfaceCreator
from core.license_manager import LicenseManager

class FluentMainWindow(FluentWindow):
    """Fluent Design 主窗口"""
    
    def __init__(self):
        super().__init__()
        self.image_reader = ImageInfoReader()
        self.data_manager = DataManager()
        self.html_exporter = HTMLExporter()
        self.current_file_path = None
        
        # 许可证管理器
        self.license_manager = LicenseManager()
        self.license_status = {"is_valid": False, "message": "", "data": {}}
        
        # 初始化AI图像打标签器
        try:
            from core.ai_image_tagger import AIImageTagger
            self.ai_tagger = AIImageTagger()
            print("AI图像打标签器初始化成功")
        except Exception as e:
            print(f"AI图像打标签器初始化失败: {e}")
            self.ai_tagger = None
        
        # 初始化各个组件
        self.event_handlers = FluentEventHandlers(self)
        self.business_logic = FluentBusinessLogic(self)
        self.image_display = FluentImageDisplay(self)
        self.export_share = FluentExportShare(self)
        self.license_component = FluentLicenseManager(self)
        self.interface_creator = FluentInterfaceCreator(self)
        
        # 存储原始提示词数据，用于重置功能
        self.original_prompts = {
            'positive': '',
            'negative': ''
        }
        
        # 初始化自动保存定时器
        from PyQt5.QtCore import QTimer
        self.auto_save_timer = QTimer()
        self.auto_save_timer.timeout.connect(self.business_logic.auto_save_current_record)
        self.auto_save_timer.setSingleShot(False)  # 重复触发
        self.auto_save_enabled = False  # 默认关闭自动保存
        
        # 初始化埋点管理器
        try:
            from core.analytics import init_analytics
            self.analytics = init_analytics()
            print("[埋点] 分析管理器初始化成功")
        except Exception as e:
            print(f"[警告] 埋点管理器初始化失败: {e}")
            self.analytics = None
        
        # 初始化主题
        FluentTheme.init_theme()
        
        self.init_ui()
        self.setup_connections()
        self.setup_shortcuts()
        
    def set_window_icon(self):
        """设置窗口图标"""
        # 优先级顺序查找图标文件
        icon_paths = [
            "assets/app_icon.png",                 # 主应用图标
            "assets/icons/baize_icon_128x128.png", # 128x128 图标
            "assets/icons/baize_icon_64x64.png",   # 64x64 图标
            "assets/icons/baize_icon_48x48.png",   # 48x48 图标
            "assets/icons/baize_icon_32x32.png",   # 32x32 图标
            "assets/baize_logo_traditional.png",   # 备用大logo
            "assets/baize_logo_modern.png",        # 备用大logo
        ]
        
        icon_set = False
        for icon_path in icon_paths:
            if os.path.exists(icon_path):
                try:
                    icon = QIcon(icon_path)
                    if not icon.isNull():
                        self.setWindowIcon(icon)
                        print(f"[成功] 设置窗口图标: {icon_path}")
                        icon_set = True
                        break
                except Exception as e:
                    print(f"[警告] 加载图标失败 {icon_path}: {e}")
                    continue
        
        if not icon_set:
            print("[警告] 未找到图标文件，使用默认图标")

    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("白泽")
        
        # 设置窗口图标
        self.set_window_icon()
        
        self.resize(1500, 1000)
        
        # 使用界面创建器创建各个页面
        self.interface_creator.create_extraction_interface()
        self.interface_creator.create_gallery_interface()
        self.interface_creator.create_prompt_editor_interface()
        self.interface_creator.create_prompt_reverser_interface()
        self.interface_creator.create_settings_interface()
        self.interface_creator.create_activation_interface()
        
        # 设置导航界面
        self.interface_creator.setup_navigation()
        
        # 显示默认页面
        self.stackedWidget.setCurrentWidget(self.extraction_interface)
        
        # 埋点：追踪应用启动和首页浏览
        if self.analytics:
            self.analytics.track_page_view("信息提取")
        
    def on_prompt_text_changed(self):
        """提示词文本变化时的处理（不自动保存，仅用于标记状态）"""
        # 这里可以添加一些UI状态更新，比如标记提示词已修改
        # 暂时不做任何处理，只是为了断开自动保存连接
        pass
    
    def create_params_layout(self, image_info):
        """创建参数布局"""
        from qfluentwidgets import BodyLabel
        
        # 确保image_info是字典类型
        if not isinstance(image_info, dict):
            return
        
        # 定义参数映射
        param_mapping = {
            'steps': '采样步数',
            'sampler_name': '采样器',
            'cfg_scale': 'CFG Scale',
            'seed': '随机种子',
            'size': '尺寸',
            'model_name': '模型',
            'model_hash': '模型哈希',
            'denoising_strength': '去噪强度',
            'clip_skip': 'Clip Skip',
            'ensd': 'ENSD'
        }
        
        # 显示主要参数
        for key, label in param_mapping.items():
            value = image_info.get(key, '')
            if value:
                param_widget = QWidget()
                param_layout = QVBoxLayout()
                param_layout.setSpacing(2)
                param_layout.setContentsMargins(0, 4, 0, 4)
                
                # 参数标签
                param_label = BodyLabel(f"{label}:")
                param_label.setStyleSheet("""
                    color: #6B7280;
                    font-size: 12px;
                    font-weight: 500;
                    margin-bottom: 2px;
                """)
                
                # 参数值
                param_value = BodyLabel(str(value))
                param_value.setWordWrap(True)
                param_value.setStyleSheet("""
                    color: #1F2937;
                    background-color: rgba(248, 250, 252, 0.8);
                    border: 1px solid rgba(229, 231, 235, 0.6);
                    padding: 4px 8px;
                    border-radius: 6px;
                    font-size: 12px;
                """)
                
                param_layout.addWidget(param_label)
                param_layout.addWidget(param_value)
                param_widget.setLayout(param_layout)
                
                self.params_layout.addWidget(param_widget)
        

    
    def resizeEvent(self, event):
        """窗口大小变化事件"""
        super().resizeEvent(event)
        # 确保蒙层大小与界面同步
        if hasattr(self, 'drag_overlay') and hasattr(self, 'extraction_interface'):
            self.drag_overlay.resize(self.extraction_interface.size())
        

    
    def create_gallery_interface(self):
        """创建图片画廊界面"""
        from .fluent_gallery_components import FluentGalleryWidget
        self.gallery_interface = FluentGalleryWidget(self.data_manager)
        self.gallery_interface.record_selected.connect(self.event_handlers.handle_gallery_record_selected)
        
        # 设置对象名称
        self.gallery_interface.setObjectName("gallery")
        
    def create_prompt_editor_interface(self):
        """创建提示词编辑界面"""
        self.prompt_editor_interface = FluentPromptEditorWidget()
        
        # 设置对象名称
        self.prompt_editor_interface.setObjectName("prompt_editor")
        
    def create_prompt_reverser_interface(self):
        """创建提示词反推界面"""
        self.prompt_reverser_interface = FluentPromptReverserWidget()
        
        # 设置对象名称
        self.prompt_reverser_interface.setObjectName("prompt_reverser")
        
    def create_settings_interface(self):
        """创建设置界面"""
        self.settings_interface = FluentSettingsWidget()
        
        # 设置对象名称
        self.settings_interface.setObjectName("settings")
        
    def create_activation_interface(self):
        """创建激活界面"""
        # 创建一个简单的激活状态显示界面
        activation_widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(FluentSpacing.LG, FluentSpacing.LG, 
                                 FluentSpacing.LG, FluentSpacing.LG)
        
        # 激活状态卡片
        status_card = CardWidget()
        status_layout = QVBoxLayout()
        status_layout.setContentsMargins(FluentSpacing.LG, FluentSpacing.LG, 
                                       FluentSpacing.LG, FluentSpacing.LG)
        
        # 标题
        title_label = TitleLabel("软件激活")
        status_layout.addWidget(title_label)
        
        # 当前状态
        self.license_status_label = BodyLabel("检查中...")
        status_layout.addWidget(self.license_status_label)
        
        # 激活按钮
        activate_btn = PrimaryPushButton("激活软件")
        activate_btn.clicked.connect(self.show_activation_dialog)
        status_layout.addWidget(activate_btn)
        
        status_card.setLayout(status_layout)
        layout.addWidget(status_card)
        layout.addStretch()
        
        activation_widget.setLayout(layout)
        activation_widget.setObjectName("activation")
        
        return activation_widget
    

        
    def setup_connections(self):
        """设置信号连接"""
        # 新布局的按钮连接
        self.save_btn.clicked.connect(self.business_logic.save_record)
        self.copy_info_btn.clicked.connect(self.copy_info)  # 复制按钮在第二列AI信息标题右边
        self.export_btn.clicked.connect(self.share_as_html)  # 分享HTML按钮在第三列标签标题右边
        self.auto_tag_btn.clicked.connect(self.business_logic.auto_tag_image)  # AI自动打标签按钮
        
        # 提示词相关按钮连接
        self.positive_translate_btn.clicked.connect(self.event_handlers.handle_positive_translate_clicked)
        self.negative_translate_btn.clicked.connect(self.event_handlers.handle_negative_translate_clicked)
        self.save_prompts_btn.clicked.connect(self.business_logic.save_prompts_only)
        self.reset_prompts_btn.clicked.connect(self.business_logic.reset_prompts)
        
        # 许可证相关按钮连接
        self.quick_activate_btn.clicked.connect(self.show_activation_dialog)
        
        # 历史记录信号
        self.history_widget.record_selected.connect(self.load_from_history_record)
        
        # 监听用户输入变化，启动自动保存定时器（不包括提示词）
        self.file_name_edit.textChanged.connect(self.on_user_input_changed)
        self.user_tags_edit.textChanged.connect(self.on_user_input_changed)
        
        # 提示词变化处理（仅用于标记修改状态，不自动保存）
        self.positive_prompt_text.textChanged.connect(self.on_prompt_text_changed)
        self.negative_prompt_text.textChanged.connect(self.on_prompt_text_changed)
        
        # 连接事件处理器信号
        self.event_handlers.file_processed.connect(self.business_logic.process_image)
        self.event_handlers.prompt_edit_requested.connect(self.handle_edit_prompt_request)
        
        # 连接业务逻辑信号
        self.business_logic.record_saved.connect(lambda record_id: print(f"记录已保存: {record_id}"))
        
        # 连接页面切换埋点
        if self.analytics:
            try:
                # 连接导航切换信号（FluentWindow的stackedWidget信号）
                self.stackedWidget.currentChanged.connect(self._track_page_change)
                print("[埋点] 页面切换追踪已连接")
            except Exception as e:
                print(f"[警告] 页面切换追踪连接失败: {e}")
        

            

            
    def copy_info(self):
        """复制信息到剪贴板 - 委托给导出分享组件"""
        self.export_share.copy_info()
    
    def share_as_html(self):
        """分享为HTML - 委托给导出分享组件"""
        self.export_share.share_as_html()
    
    def export_data(self):
        """导出数据 - 委托给导出分享组件"""
        self.export_share.export_data()
    
    def update_copy_export_button(self, image_info: dict):
        """根据图片信息更新复制/导出按钮的文本和提示"""
        if not image_info:
            self.copy_info_btn.setText("📋 复制信息")
            self.copy_info_btn.setToolTip("以SD WebUI格式复制生成信息")
            self.copy_info_btn.setVisible(False)
            return

        is_comfyui = image_info.get('generation_source') == 'ComfyUI'
        has_workflow = bool(image_info.get('workflow_data'))

        self.copy_info_btn.setVisible(True)

        if is_comfyui and has_workflow:
            self.copy_info_btn.setText("📋 导出工作流")
            self.copy_info_btn.setToolTip("将ComfyUI工作流导出为JSON文件")
        else:
            self.copy_info_btn.setText("📋 复制信息")
            self.copy_info_btn.setToolTip("以SD WebUI格式复制生成信息")
            
    def clear_all_info(self, clear_history=False):
        """清空所有信息"""
        self.business_logic.clear_current_info()
        
    def load_from_history_record(self, record):
        """从历史记录加载"""
        try:
            print(f"主窗口接收到历史记录信号: {record.get('file_path', '未知')}")
            file_path = record.get('file_path', '')
            
            if not os.path.exists(file_path):
                InfoBar.warning(
                    title="文件不存在",
                    content="文件不存在，可能已被移动或删除",
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=3000,
                    parent=self
                )
                return
                
            # 切换到信息提取页面
            self.stackedWidget.setCurrentWidget(self.extraction_interface)
            
            self.current_file_path = file_path
            
            # 重新读取图片信息
            image_info = self.image_reader.extract_info(file_path)
            
            # 显示图片信息
            self.image_display.display_image_info(file_path, image_info)
            
            # 加载用户自定义信息
            self.file_name_edit.setText(record.get('custom_name', ''))
            self.user_tags_edit.setPlainText(record.get('tags', ''))
            
            # 启用自动保存功能
            self.auto_save_enabled = True
            print(f"[历史记录] 已为记录 {file_path} 启用自动保存功能")
            
        except Exception as e:
            InfoBar.error(
                title="加载失败",
                content=f"加载历史记录时出错: {str(e)}",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
            
    def handle_edit_prompt_request(self, prompt_text, scene_name):
        """处理编辑提示词请求"""
        try:
            print(f"开始处理编辑提示词请求: {scene_name}")
            print(f"提示词内容: {prompt_text}")
            
            # 解析提示词（智能分割）
            import re
            
            # 智能判断是否为完整描述文本
            # 特征：长文本、包含完整句子（有句号）、逗号少且不是标签格式
            comma_count = prompt_text.count(',') + prompt_text.count('，')
            has_periods = '.' in prompt_text or '。' in prompt_text
            # 标签格式特征：多个逗号+空格分隔且平均长度较短
            comma_space_count = prompt_text.count(', ')
            words_count = len(prompt_text.split())
            avg_word_length = len(prompt_text.replace(' ', '')) / max(words_count, 1)
            
            # 如果文本长且包含句号，且逗号少于4个，且平均词长大于4，则认为是描述文本
            if len(prompt_text) > 150 and has_periods and comma_count < 4 and avg_word_length > 4:
                # 作为完整提示词处理，不分割
                prompts = [prompt_text.strip()]
            else:
                # 对于短文本或标签列表格式，智能分割（保护括号内的内容）
                prompts = self.smart_split_prompts(prompt_text)
            print(f"解析后的提示词: {prompts}")
            
            # 切换到提示词编辑页面
            print("正在切换到提示词编辑页面...")
            self.stackedWidget.setCurrentWidget(self.prompt_editor_interface)
            
            # 确保组件可见
            self.prompt_editor_interface.setVisible(True)
            self.prompt_editor_interface.show()
            print(f"提示词编辑器可见性: {self.prompt_editor_interface.isVisible()}")
            
            # 先收起所有现有场景
            for editor_info in self.prompt_editor_interface.editors:
                accordion = editor_info['accordion']
                accordion.setExpanded(False)
            
            # 在提示词编辑器中添加新场景
            print(f"正在添加新场景: {scene_name}")
            editor_panel = self.prompt_editor_interface.create_editor_accordion(scene_name)
            
            # 设置英文提示词
            editor_panel.set_prompts(english_prompts=prompts)
            print("已设置提示词内容")
            
            # 只展开新添加的场景
            if self.prompt_editor_interface.editors:
                last_editor = self.prompt_editor_interface.editors[-1]
                accordion = last_editor['accordion']
                accordion.setExpanded(True)
                print("已展开新场景")
                
                # 确保新场景可见，滚动到该位置
                try:
                    self.prompt_editor_interface.ensureWidgetVisible(accordion)
                    print("已滚动到新场景位置")
                except Exception as scroll_error:
                    print(f"滚动到新场景时出错: {scroll_error}")
            
            print(f"成功导入提示词到场景: {scene_name}")
            
            # 显示成功提示
            InfoBar.success(
                title="提示词已导入",
                content=f"已将提示词导入到新场景：{scene_name}",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
            
        except Exception as e:
            print(f"处理编辑提示词请求时出错: {e}")
            import traceback
            traceback.print_exc()
            InfoBar.error(
                title="导入失败",
                content=f"导入提示词时出错: {str(e)}",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )


        
    def _track_page_change(self, index):
        """追踪页面切换"""
        if not self.analytics:
            return
            
        try:
            # 获取当前显示的界面
            current_widget = self.stackedWidget.widget(index)
            if current_widget:
                # 获取页面名称
                page_name = current_widget.objectName() or "unknown"
                
                # 页面名称映射
                page_names = {
                    "extraction": "信息提取",
                    "gallery": "图片画廊", 
                    "prompt_editor": "提示词修改",
                    "prompt_reverser": "提示词反推",
                    "settings": "设置",
                    "activation": "软件激活"
                }
                
                display_name = page_names.get(page_name, page_name)
                
                # 追踪页面浏览
                self.analytics.track_page_view(display_name, self.analytics.current_page)
                print(f"[埋点] 页面切换: {display_name}")
                
        except Exception as e:
            print(f"[警告] 页面切换埋点失败: {e}")
    
    def track_feature_usage(self, feature_name, details=None):
        """追踪功能使用"""
        if self.analytics:
            self.analytics.track_feature_usage(feature_name, details or {})
    
    def closeEvent(self, event):
        """窗口关闭事件"""
        try:
            # 结束埋点会话
            if self.analytics:
                try:
                    self.analytics.end_session()
                    print("[埋点] 会话已结束")
                except Exception as e:
                    print(f"[警告] 结束埋点会话失败: {e}")
            
            # 清理AI工作线程
            self.business_logic.cleanup_ai_threads()
            
            # 保存提示词编辑器数据
            if hasattr(self, 'prompt_editor_widget') and self.prompt_editor_widget:
                self.prompt_editor_widget.save_history_data()
                print("应用关闭时自动保存了提示词数据")
        except Exception as e:
            print(f"关闭时保存数据失败: {e}")
        
        event.accept()
    
    def setup_shortcuts(self):
        """设置快捷键"""
        from PyQt5.QtWidgets import QShortcut
        from PyQt5.QtGui import QKeySequence
        
        # Ctrl+S 保存快捷键
        save_shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        save_shortcut.activated.connect(self.business_logic.save_record)
        print("设置Ctrl+S快捷键")
    
    def smart_split_prompts(self, text):
        """智能分割提示词，保护括号内的内容"""
        import re
        
        # 如果文本很短或没有特殊字符，直接返回
        if len(text.strip()) < 10 or not re.search(r'[,，.。]', text):
            return [text.strip()]
        
        prompts = []
        current_prompt = ""
        bracket_stack = []  # 用于跟踪括号嵌套
        i = 0
        
        # 定义括号对
        open_brackets = {'(': ')', '[': ']', '{': '}', '（': '）', '【': '】', '〈': '〉'}
        close_brackets = {v: k for k, v in open_brackets.items()}
        
        while i < len(text):
            char = text[i]
            
            # 检查是否是开括号
            if char in open_brackets:
                bracket_stack.append(char)
                current_prompt += char
            # 检查是否是闭括号
            elif char in close_brackets:
                if bracket_stack and bracket_stack[-1] == close_brackets[char]:
                    bracket_stack.pop()
                current_prompt += char
            # 检查是否是分隔符
            elif char in ',，.。' and not bracket_stack:
                # 只有在括号外才分割
                if current_prompt.strip():
                    prompts.append(current_prompt.strip())
                current_prompt = ""
            else:
                current_prompt += char
            
            i += 1
        
        # 添加最后一个提示词
        if current_prompt.strip():
            prompts.append(current_prompt.strip())
        
        # 如果分割结果为空或只有一个很长的项，回退到简单分割
        if not prompts or (len(prompts) == 1 and len(prompts[0]) > 200):
            return [prompt.strip() for prompt in re.split(r'[,，.。]', text) if prompt.strip()]
        
        return prompts
        
    def on_user_input_changed(self):
        """用户输入变化时的处理"""
        if not self.current_file_path:
            return  # 没有当前文件时不启动自动保存
            
        # 启用自动保存并重启定时器
        self.auto_save_enabled = True
        self.auto_save_timer.stop()  # 先停止当前定时器
        self.auto_save_timer.start(5000)  # 5秒后触发
        print("[自动保存] 检测到用户输入变化，将在5秒后自动保存")
        

    
    def set_license_status(self, is_valid, message, data):
        """设置许可证状态"""
        self.license_status = {
            "is_valid": is_valid,
            "message": message,
            "data": data
        }
        
        # 更新激活界面的状态标签
        if hasattr(self, 'license_status_label'):
            if is_valid:
                if data.get("trial", False):
                    remaining_days = data.get("remaining_days", 0)
                    self.license_status_label.setText(f"✅ 试用期 - 剩余 {remaining_days} 天")
                else:
                    self.license_status_label.setText("✅ 已激活 - 感谢您的支持！")
            else:
                self.license_status_label.setText(f"❌ {message}")
        
        # 更新顶部状态栏
        if hasattr(self, 'license_status_card'):
            if is_valid and not data.get("trial", False):
                # 软件已激活且非试用期时，隐藏状态栏以节省空间
                self.license_status_card.setVisible(False)
            else:
                # 试用期或未激活时，显示状态栏
                self.license_status_card.setVisible(True)
                
                if hasattr(self, 'license_status_text') and hasattr(self, 'license_status_icon'):
                    if is_valid:
                        if data.get("trial", False):
                            remaining_days = data.get("remaining_days", 0)
                            self.license_status_icon.setText("⏰")
                            self.license_status_text.setText(f"试用期剩余 {remaining_days} 天")
                            self.license_status_card.setStyleSheet("background-color: rgba(255, 193, 7, 0.1);")
                            self.quick_activate_btn.setVisible(True)
                            self.quick_activate_btn.setText("立即激活")
                    else:
                        self.license_status_icon.setText("❌")
                        self.license_status_text.setText(message)
                        self.license_status_card.setStyleSheet("background-color: rgba(255, 99, 71, 0.1);")
                        self.quick_activate_btn.setVisible(True)
                        self.quick_activate_btn.setText("立即激活")
        
        # 更新导航栏
        self.update_navigation_for_activation()
    
    def show_activation_dialog(self):
        """显示激活对话框"""
        dialog = FluentActivationDialog(self)
        dialog.activation_completed.connect(self.on_activation_completed)
        dialog.exec_()
    
    def on_activation_completed(self, success, message):
        """激活完成回调"""
        if success:
            # 重新检查许可证状态
            is_valid, msg, data = self.license_manager.check_license_validity()
            self.set_license_status(is_valid, msg, data)
            
            InfoBar.success(
                title="激活成功",
                content=message,
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
        else:
            InfoBar.error(
                title="激活失败",
                content=message,
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
    
    def update_navigation_for_activation(self):
        """更新导航栏以反映激活状态"""
        # 这里可以添加代码来移除或更新激活相关的导航项
        # 具体实现取决于PyQt-Fluent-Widgets的API
        pass
    
    def check_feature_access(self, feature_name):
        """检查功能访问权限"""
        if not self.license_status.get("is_valid", False):
            InfoBar.warning(
                title="功能受限",
                content=f"{feature_name}需要激活软件后才能使用",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
            return False
        return True


def main():
    """主函数"""
    app = QApplication([])
    
    # 显示启动画面（可选）
    # splash = SplashScreen(":/images/splash.png", app)
    # splash.show()
    
    window = FluentMainWindow()
    window.show()
    
    # 关闭启动画面
    # splash.finish(window)
    
    app.exec_()


if __name__ == "__main__":
    main() 