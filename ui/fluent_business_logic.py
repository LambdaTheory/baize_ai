#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fluent Design 业务逻辑处理器
处理图片处理、数据保存、AI分析等业务逻辑
"""

import os
from PyQt5.QtWidgets import QApplication, QFileDialog, QMessageBox
from PyQt5.QtCore import QObject, pyqtSignal, QThread, Qt
from PyQt5.QtGui import QPixmap
from qfluentwidgets import InfoBar, InfoBarPosition
from .fluent_ai_worker import AITagWorker


class FluentBusinessLogic(QObject):
    """业务逻辑处理器类"""
    
    # 定义信号
    image_info_updated = pyqtSignal(str, dict)  # 图片信息更新信号
    record_saved = pyqtSignal(int)  # 记录保存完成信号
    
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        
        # 初始化AI工作线程相关变量
        self.ai_worker_thread = None
        self.ai_worker = None
        
    def process_image(self, file_path):
        """处理图片文件"""
        try:
            self.parent.current_file_path = file_path
            
            # 清空用户输入的标签（处理新图片时重置）
            self.parent.user_tags_edit.setPlainText("")
            
            # 检查是否为WebP格式，给出提示
            file_ext = os.path.splitext(file_path)[1].lower()
            if file_ext == '.webp':
                InfoBar.warning(
                    title="WebP格式提示",
                    content="WebP格式图片通常包含较少的AI生成信息。为获得完整的生成参数，建议使用PNG格式。",
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=4000,
                    parent=self.parent
                )
            
            # 埋点：追踪图片处理功能使用
            if hasattr(self.parent, 'track_feature_usage'):
                self.parent.track_feature_usage("图片处理", {
                    "file_extension": os.path.splitext(file_path)[1].lower(),
                    "file_size": os.path.getsize(file_path) if os.path.exists(file_path) else 0
                })
            
            # 读取图片信息 - 优先从数据库读取已保存的记录
            image_info = self.parent.image_reader.extract_info(file_path)
            
            # 检查数据库中是否有该图片的保存记录
            saved_record = self.parent.data_manager.get_record_by_path(file_path)
            
            if saved_record:
                # 如果有保存的记录，使用数据库中的信息（包括用户修改的提示词）
                if image_info is None:
                    image_info = {}
                
                # 更新提示词为用户保存的版本
                if saved_record.get('prompt'):
                    image_info['prompt'] = saved_record['prompt']
                if saved_record.get('negative_prompt'):
                    image_info['negative_prompt'] = saved_record['negative_prompt']
                
                # 更新其他用户自定义信息
                if saved_record.get('custom_name'):
                    image_info['custom_name'] = saved_record['custom_name']
                if saved_record.get('tags'):
                    image_info['user_tags'] = saved_record['tags']
            
            # 更新主窗口的复制/导出按钮状态
            self.parent.update_copy_export_button(image_info)
            
            # 显示图片信息
            self.parent.image_display.display_image_info(file_path, image_info)
            
            # 检查是否有AI信息，如果没有则询问是否使用提示词反推
            # 但如果数据库中有记录（说明用户已经处理过），则不再询问
            if not image_info or not self._has_meaningful_ai_info(image_info):
                if not saved_record:  # 只有在数据库中也没有记录时才询问
                    self._show_prompt_reverser_dialog(file_path)
            
            # 自动保存记录（首次加载图片时保存一次）
            self.auto_save_record(file_path, image_info)
            
            # 刷新历史记录和画廊
            self.parent.history_widget.load_history()
            self.parent.gallery_interface.load_records()
            
            # 发出信号
            self.image_info_updated.emit(file_path, image_info or {})
            
            # 显示相关按钮
            self.parent.save_btn.setVisible(True)
            self.parent.export_btn.setVisible(True)
            self.parent.auto_tag_btn.setVisible(True)
            
        except Exception as e:
            print(f"处理图片时出错: {e}")
            InfoBar.error(
                title="处理失败",
                content=f"处理图片时出错: {str(e)}",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self.parent
            )
            # 出错时清空UI
            self.clear_current_info()
    
    def clear_current_info(self):
        """清空当前信息"""
        
        # 清空当前文件路径和信息
        self.parent.current_file_path = None
        if hasattr(self.parent, 'current_image_info'):
            self.parent.current_image_info = {}
        
        # 清空UI显示
        self.clear_ui_display()
        
        # 更新按钮状态
        self.parent.update_copy_export_button(None)
        self.parent.save_btn.setVisible(False)
        self.parent.export_btn.setVisible(False)
        self.parent.auto_tag_btn.setVisible(False)
        
    
    def auto_save_record(self, file_path, image_info):
        """自动保存记录"""
        try:
            record_data = {
                'file_path': file_path,
                'custom_name': '',
                'tags': '',
                'notes': '',
            }
            
            if image_info:
                record_data.update(image_info)
            
            record_id = self.parent.data_manager.save_record(record_data)
            
            if record_id:
                print(f"自动保存成功，记录ID: {record_id}")
                self.record_saved.emit(record_id)
            else:
                print("自动保存失败")
                
        except Exception as e:
            print(f"自动保存记录时出错: {e}")
            
    def save_record(self):
        """保存/更新记录"""
        if not self.parent.current_file_path:
            InfoBar.warning(
                title="提示",
                content="请先选择一个图片文件",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=2000,
                parent=self.parent
            )
            return
            
        try:
            # 获取用户输入的信息
            custom_name = self.parent.file_name_edit.text().strip()
            tags = self.parent.user_tags_edit.toPlainText().strip()
            notes = ''  # 备注功能已移除，设为空字符串
            
            # 重新读取图片信息
            image_info = self.parent.image_reader.extract_info(self.parent.current_file_path)
            
            record_data = {
                'file_path': self.parent.current_file_path,
                'custom_name': custom_name,
                'tags': tags,
                'notes': notes,
            }
            
            if image_info:
                record_data.update(image_info)
            
            record_id = self.parent.data_manager.save_record(record_data)
            
            if record_id:
                # 埋点：追踪保存记录功能使用
                if hasattr(self.parent, 'track_feature_usage'):
                    self.parent.track_feature_usage("保存记录", {
                        "has_custom_name": bool(custom_name),
                        "has_tags": bool(tags),
                        "record_id": record_id
                    })
                
                InfoBar.success(
                    title="保存成功",
                    content="记录保存成功！",
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=2000,
                    parent=self.parent
                )
                # 刷新历史记录和画廊
                self.parent.history_widget.load_history()
                self.parent.gallery_interface.load_records()
                self.record_saved.emit(record_id)
            else:
                InfoBar.error(
                    title="保存失败",
                    content="保存记录失败",
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=3000,
                    parent=self.parent
                )
                
        except Exception as e:
            InfoBar.error(
                title="保存失败",
                content=f"保存记录时出错: {str(e)}",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self.parent
            )
    
    def save_prompts_only(self):
        """仅保存提示词到数据库"""
        if not self.parent.current_file_path:
            InfoBar.warning(
                title="提示",
                content="请先选择一个图片文件",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=2000,
                parent=self.parent
            )
            return
            
        try:
            # 获取当前的提示词
            positive_prompt = self.parent.positive_prompt_text.toPlainText().strip()
            negative_prompt = self.parent.negative_prompt_text.toPlainText().strip()
            
            # 获取其他用户输入的信息
            custom_name = self.parent.file_name_edit.text().strip()
            tags = self.parent.user_tags_edit.toPlainText().strip()
            notes = ''  # 备注功能已移除，设为空字符串
            
            # 重新读取图片信息并更新提示词
            image_info = self.parent.image_reader.extract_info(self.parent.current_file_path)
            
            record_data = {
                'file_path': self.parent.current_file_path,
                'custom_name': custom_name,
                'tags': tags,
                'notes': notes,
                'prompt': positive_prompt,
                'negative_prompt': negative_prompt,
            }
            
            if image_info:
                # 更新图片信息中的提示词
                image_info['prompt'] = positive_prompt
                image_info['negative_prompt'] = negative_prompt
                record_data.update(image_info)
            
            record_id = self.parent.data_manager.save_record(record_data)
            
            if record_id:
                InfoBar.success(
                    title="保存成功",
                    content="提示词已保存！",
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=2000,
                    parent=self.parent
                )
                # 刷新历史记录和画廊
                self.parent.history_widget.load_history()
                self.parent.gallery_interface.load_records()
                
                # 更新原始提示词为当前保存的提示词
                self.parent.original_prompts['positive'] = positive_prompt
                self.parent.original_prompts['negative'] = negative_prompt
                
                self.record_saved.emit(record_id)
            else:
                InfoBar.error(
                    title="保存失败",
                    content="保存提示词失败",
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=3000,
                    parent=self.parent
                )
                
        except Exception as e:
            InfoBar.error(
                title="保存失败",
                content=f"保存提示词时出错: {str(e)}",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self.parent
            )
    
    def reset_prompts(self):
        """重置提示词到原始状态"""
        try:
            # 恢复到原始提示词
            self.parent.positive_prompt_text.setPlainText(self.parent.original_prompts['positive'])
            self.parent.negative_prompt_text.setPlainText(self.parent.original_prompts['negative'])
            
            InfoBar.success(
                title="重置成功",
                content="提示词已重置到原始状态",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=2000,
                parent=self.parent
            )
            
        except Exception as e:
            print(f"重置提示词时出错: {e}")
            InfoBar.error(
                title="重置失败",
                content=f"重置提示词时出错: {str(e)}",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self.parent
            )
    
    def auto_tag_image(self):
        """AI自动打标签"""
        if not self.parent.current_file_path:
            InfoBar.warning(
                title="提示",
                content="请先选择一个图片文件",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=2000,
                parent=self.parent
            )
            return
        
        if not self.parent.ai_tagger:
            InfoBar.error(
                title="AI服务不可用",
                content="AI图像打标签器未正确初始化，请检查API配置",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self.parent
            )
            return
        
        # 埋点：追踪AI自动标签功能使用
        if hasattr(self.parent, 'track_feature_usage'):
            self.parent.track_feature_usage("AI自动标签", {
                "file_path": self.parent.current_file_path,
                "file_extension": os.path.splitext(self.parent.current_file_path)[1].lower()
            })
        
        # 禁用按钮防止重复点击
        self.parent.auto_tag_btn.setEnabled(False)
        self.parent.auto_tag_btn.setText("🤖 分析中...")
        
        try:
            InfoBar.info(
                title="开始分析",
                content="正在使用AI分析图片内容，请稍候...",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=2000,
                parent=self.parent
            )
            
            # 获取已存在的标签
            existing_tags = self.parent.data_manager.get_all_unique_tags()
            print(f"获取到 {len(existing_tags)} 个已存在标签")
            
            # 创建工作线程
            self.ai_worker_thread = QThread()
            self.ai_worker = AITagWorker(self.parent.ai_tagger, self.parent.current_file_path, existing_tags)
            self.ai_worker.moveToThread(self.ai_worker_thread)
            
            # 连接信号
            self.ai_worker_thread.started.connect(self.ai_worker.run)
            self.ai_worker.finished.connect(self.handle_ai_tag_finished)
            self.ai_worker.finished.connect(self.ai_worker_thread.quit)
            self.ai_worker_thread.finished.connect(self.ai_worker_thread.deleteLater)
            
            # 启动线程
            self.ai_worker_thread.start()
            
        except Exception as e:
            InfoBar.error(
                title="分析错误",
                content=f"AI分析过程中出错: {str(e)}",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=4000,
                parent=self.parent
            )
            print(f"AI分析异常: {e}")
            import traceback
            traceback.print_exc()
            
            # 恢复按钮状态
            self.parent.auto_tag_btn.setEnabled(True)
            self.parent.auto_tag_btn.setText("🤖 AI自动打标签")
            
    def handle_ai_tag_finished(self, success, result):
        """处理AI标签分析完成后的信号"""
        # 恢复按钮状态
        self.parent.auto_tag_btn.setEnabled(True)
        self.parent.auto_tag_btn.setText("🤖 AI自动打标签")
        
        if success:
            # 获取生成的标签字符串
            tags_string = result.get('tags_string', '')
            tags_list = result.get('tags', [])
            ai_description = result.get('ai_analysis', {}).get('description', '')
            matching_result = result.get('matching_result', {})
            
            # 埋点：追踪AI标签分析成功
            if hasattr(self.parent, 'track_feature_usage'):
                self.parent.track_feature_usage("AI标签分析成功", {
                    "tags_count": len(tags_list),
                    "matched_tags": len(matching_result.get('matched_tags', [])),
                    "new_tags": len(matching_result.get('new_tags', []))
                })
            
            # 更新标签输入框
            if tags_string:
                current_tags = self.parent.user_tags_edit.toPlainText().strip()
                if current_tags:
                    # 如果已有标签，追加新标签
                    new_tags = f"{current_tags}, {tags_string}"
                else:
                    new_tags = tags_string
                
                self.parent.user_tags_edit.setPlainText(new_tags)
                
                # 在备注中添加AI分析描述（备注功能已移除，此部分保留日志）
                if ai_description:
                    print(f"AI分析描述: {ai_description}")  # 仅记录到控制台
            
            # AI打标完成后自动保存
            print("[AI打标] 开始自动保存标签到数据库...")  
            self.save_record()  # 调用现有的保存方法
            print("[AI打标] 自动保存完成")
            
            # 显示详细结果
            matched_count = len(matching_result.get('matched_tags', []))
            new_count = len(matching_result.get('new_tags', []))
            
            success_message = f"AI分析完成！生成了 {len(tags_list)} 个标签并已自动保存"
            if matched_count > 0 or new_count > 0:
                success_message += f"（匹配已有: {matched_count}, 新创建: {new_count}）"
            
            InfoBar.success(
                title="标签生成成功",
                content=success_message,
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=4000,
                parent=self.parent
            )
            
            print(f"AI生成标签: {tags_list}")
            print(f"匹配结果: 已有标签 {matched_count} 个，新标签 {new_count} 个")
            
        else:
            error_msg = result.get('error', '未知错误')
            
            # 埋点：追踪AI标签分析失败
            if hasattr(self.parent, 'track_feature_usage'):
                self.parent.track_feature_usage("AI标签分析失败", {
                    "error_message": error_msg
                })
            
            InfoBar.error(
                title="分析失败",
                content=f"AI分析失败: {error_msg}",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=4000,
                parent=self.parent
            )
            print(f"AI分析失败: {error_msg}")
    
    # 注释掉定时器自动保存方法，不再需要
    # def auto_save_current_record(self):
    #     """自动保存当前记录"""
    #     pass
    
    def clear_ui_display(self):
        """清空UI显示"""
        try:
            print("[清空UI] 开始清空UI显示...")
            
            # 清空图片显示
            self.parent.image_label.clear()
            self.parent.image_label.setText("🖼️ 将图片拖拽到此处\n💻 支持从SD WebUI、ComfyUI等浏览器拖拽")
            print("[清空UI] 已清空图片显示")
            
            # 清空提示词
            self.parent.positive_prompt_text.clear()
            self.parent.positive_prompt_text.setPlainText("")
            self.parent.negative_prompt_text.clear()
            self.parent.negative_prompt_text.setPlainText("")
            print("[清空UI] 已清空提示词")
            
            # 清空参数布局
            while self.parent.params_layout.count():
                child = self.parent.params_layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
            print("[清空UI] 已清空参数布局")
            
            # 清空用户输入
            self.parent.file_name_edit.clear()
            self.parent.file_name_edit.setText("")
            self.parent.user_tags_edit.clear()
            self.parent.user_tags_edit.setPlainText("")
            print("[清空UI] 已清空用户输入")
            
            # 清空文件信息标签
            if hasattr(self.parent, 'file_path_label'):
                self.parent.file_path_label.setText("-")
            if hasattr(self.parent, 'file_size_label'):
                self.parent.file_size_label.setText("-")
            if hasattr(self.parent, 'image_size_label'):
                self.parent.image_size_label.setText("-")
            print("[清空UI] 已清空文件信息标签")
            
            # 清空原始提示词数据
            self.parent.original_prompts['positive'] = ''
            self.parent.original_prompts['negative'] = ''
            print("[清空UI] 已清空原始提示词数据")
            
            # 强制刷新界面
            self.parent.update()
            self.parent.repaint()
            print("[清空UI] 已强制刷新界面")
            
            print("[清空UI] UI显示清空完成")
            
        except Exception as e:
            print(f"清空UI显示时出错: {e}")
            import traceback
            traceback.print_exc()
    
    def _has_meaningful_ai_info(self, image_info):
        """检查是否包含有意义的AI生成信息"""
        if not image_info or not isinstance(image_info, dict):
            return False
        
        # 检查关键的AI生成信息字段
        key_fields = ['prompt', 'negative_prompt', 'model', 'sampler', 'steps', 'cfg_scale']
        meaningful_fields = 0
        
        for field in key_fields:
            if field in image_info and image_info[field]:
                # 检查字段值是否有意义（不是空字符串或默认值）
                value = str(image_info[field]).strip()
                if value and value.lower() not in ['', 'none', 'null', 'unknown', '未知']:
                    meaningful_fields += 1
        
        # 如果有2个或以上有意义的字段，认为包含AI信息
        return meaningful_fields >= 2
    
    def _show_prompt_reverser_dialog(self, file_path):
        """显示提示词反推确认对话框"""
        from qfluentwidgets import MessageBox
        
        dialog = MessageBox(
            title="未检测到AI生成信息",
            content="当前图片未检测到AI生成信息。\n\n是否使用AI提示词反推功能来分析这张图片？",
            parent=self.parent
        )
        
        # qfluentwidgets的MessageBox返回值是布尔值，exec()返回True表示点击了确认按钮
        if dialog.exec():
            # 切换到提示词反推界面
            self.parent.switchTo(self.parent.prompt_reverser_interface)
            
            # 在提示词反推界面中加载图片
            if hasattr(self.parent.prompt_reverser_interface, 'load_image'):
                self.parent.prompt_reverser_interface.load_image(file_path)
                
                InfoBar.success(
                    title="已切换到提示词反推",
                    content="图片已加载到提示词反推界面，可以开始分析",
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=3000,
                    parent=self.parent
                )
    
    def cleanup_ai_threads(self):
        """清理AI工作线程"""
        try:
            if self.ai_worker_thread and self.ai_worker_thread.isRunning():
                print("正在停止AI工作线程...")
                self.ai_worker_thread.quit()
                self.ai_worker_thread.wait(3000)  # 等待最多3秒
                if self.ai_worker_thread.isRunning():
                    self.ai_worker_thread.terminate()
                print("AI工作线程已停止")
        except Exception as e:
            print(f"清理AI线程时出错: {e}") 