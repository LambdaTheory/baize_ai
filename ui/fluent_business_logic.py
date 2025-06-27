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
            
            # 读取图片信息
            image_info = self.parent.image_reader.extract_info(file_path)
            
            # 显示图片信息
            self.parent.image_display.display_image_info(file_path, image_info)
            
            # 自动保存记录
            self.auto_save_record(file_path, image_info)
            
            # 启用自动保存功能
            self.parent.auto_save_enabled = True
            print(f"[处理图片] 已为图片 {file_path} 启用自动保存功能")
            
            # 刷新历史记录和画廊
            self.parent.history_widget.load_history()
            self.parent.gallery_interface.load_records()
            
            # 发出信号
            self.image_info_updated.emit(file_path, image_info or {})
            
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
    
    def auto_save_current_record(self):
        """自动保存当前记录"""
        if not self.parent.auto_save_enabled or not self.parent.current_file_path:
            return
            
        try:
            print("[自动保存] 开始自动保存当前记录...")
            
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
                print(f"[自动保存] 自动保存成功，记录ID: {record_id}")
                # 注释掉自动保存提示，减少干扰
                # InfoBar.info(
                #     title="自动保存",
                #     content="记录已自动保存",
                #     orient=Qt.Horizontal,
                #     isClosable=True,
                #     position=InfoBarPosition.TOP,
                #     duration=1500,
                #     parent=self.parent
                # )
                # 刷新历史记录和画廊
                self.parent.history_widget.load_history()
                self.parent.gallery_interface.load_records()
                self.record_saved.emit(record_id)
            else:
                print("[自动保存] 自动保存失败")
                
        except Exception as e:
            print(f"[自动保存] 自动保存记录时出错: {e}")
        
        # 停止定时器，等待下次用户输入变化
        self.parent.auto_save_timer.stop()
    
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