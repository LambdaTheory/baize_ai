#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
导出和分享功能组件
"""

import os
import json
from PyQt5.QtCore import QObject, pyqtSignal, Qt
from PyQt5.QtWidgets import QApplication, QFileDialog, QMessageBox
from qfluentwidgets import InfoBar, InfoBarPosition, MessageBox


class FluentExportShare(QObject):
    """导出和分享功能组件"""
    
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
    
    def copy_info(self):
        """复制图片信息到剪贴板"""
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
            # 获取当前显示的信息
            info_parts = []
            
            # 基础信息
            info_parts.append("=== 图片信息 ===")
            info_parts.append(f"文件名: {os.path.basename(self.parent.current_file_path)}")
            info_parts.append(f"文件路径: {self.parent.current_file_path}")
            info_parts.append(f"文件大小: {self.parent.file_size_label.text()}")
            info_parts.append(f"图片尺寸: {self.parent.image_size_label.text()}")
            info_parts.append(f"生成方式: {self.parent.generation_method_text.text()}")
            
            # 提示词信息
            positive_prompt = self.parent.positive_prompt_text.toPlainText().strip()
            negative_prompt = self.parent.negative_prompt_text.toPlainText().strip()
            
            if positive_prompt:
                info_parts.append("\n=== 正向提示词 ===")
                info_parts.append(positive_prompt)
            
            if negative_prompt:
                info_parts.append("\n=== 负向提示词 ===")
                info_parts.append(negative_prompt)
            
            # 用户标签和备注
            user_tags = self.parent.user_tags_edit.toPlainText().strip()
            user_notes = self.parent.user_notes_edit.toPlainText().strip()
            
            if user_tags:
                info_parts.append("\n=== 用户标签 ===")
                info_parts.append(user_tags)
            
            if user_notes:
                info_parts.append("\n=== 用户备注 ===")
                info_parts.append(user_notes)
            
            # 生成参数（从当前显示的参数中提取）
            try:
                image_info = self.parent.image_reader.extract_info(self.parent.current_file_path)
                if image_info and isinstance(image_info, dict):
                    param_info = []
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
                    
                    for key, label in param_mapping.items():
                        value = image_info.get(key, '')
                        if value:
                            param_info.append(f"{label}: {value}")
                    
                    if param_info:
                        info_parts.append("\n=== 生成参数 ===")
                        info_parts.extend(param_info)
            except Exception as e:
                print(f"获取生成参数时出错: {e}")
            
            # 合并所有信息
            full_info = "\n".join(info_parts)
            
            # 复制到剪贴板
            clipboard = QApplication.clipboard()
            clipboard.setText(full_info)
            
            InfoBar.success(
                title="复制成功",
                content="图片信息已复制到剪贴板",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=2000,
                parent=self.parent
            )
            
        except Exception as e:
            InfoBar.error(
                title="复制失败",
                content=f"复制信息时出错: {str(e)}",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self.parent
            )
    
    def share_as_html(self):
        """生成HTML分享页面"""
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
            # 获取保存路径
            default_name = f"{os.path.splitext(os.path.basename(self.parent.current_file_path))[0]}_分享页面.html"
            save_path, _ = QFileDialog.getSaveFileName(
                self.parent,
                "保存HTML分享页面",
                default_name,
                "HTML文件 (*.html);;所有文件 (*)"
            )
            
            if not save_path:
                return
            
            # 收集数据
            image_info = self.parent.image_reader.extract_info(self.parent.current_file_path)
            
            # 获取用户输入的信息
            custom_name = self.parent.file_name_edit.text().strip()
            tags = self.parent.user_tags_edit.toPlainText().strip()
            notes = self.parent.user_notes_edit.toPlainText().strip()
            positive_prompt = self.parent.positive_prompt_text.toPlainText().strip()
            negative_prompt = self.parent.negative_prompt_text.toPlainText().strip()
            
            # 准备导出数据
            export_data = {
                'file_path': self.parent.current_file_path,
                'custom_name': custom_name or os.path.basename(self.parent.current_file_path),
                'tags': tags,
                'notes': notes,
                'prompt': positive_prompt,
                'negative_prompt': negative_prompt,
            }
            
            if image_info:
                export_data.update(image_info)
            
            # 生成HTML
            html_content = self.parent.html_exporter.export_single_record(export_data)
            
            # 保存HTML文件
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            InfoBar.success(
                title="分享成功",
                content=f"HTML分享页面已保存到: {save_path}",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self.parent
            )
            
            # 询问是否打开文件
            reply = MessageBox(
                "打开文件",
                "是否要打开生成的HTML分享页面？",
                self.parent
            ).exec()
            
            if reply == MessageBox.Yes:
                import webbrowser
                webbrowser.open(f"file://{os.path.abspath(save_path)}")
                
        except Exception as e:
            InfoBar.error(
                title="分享失败",
                content=f"生成HTML分享页面时出错: {str(e)}",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=4000,
                parent=self.parent
            )
            print(f"HTML分享异常: {e}")
            import traceback
            traceback.print_exc()
    
    def export_data(self):
        """导出数据"""
        try:
            # 获取所有记录
            records = self.parent.data_manager.get_all_records()
            
            if not records:
                InfoBar.warning(
                    title="提示",
                    content="没有可导出的数据",
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=2000,
                    parent=self.parent
                )
                return
            
            # 选择导出格式
            from .fluent_batch_export_dialog import FluentBatchExportDialog
            dialog = FluentBatchExportDialog(self.parent)
            dialog.set_records(records)
            
            if dialog.exec_() == dialog.Accepted:
                export_config = dialog.get_export_config()
                
                if export_config['export_type'] == 'excel':
                    self._export_to_excel(records, export_config)
                elif export_config['export_type'] == 'html':
                    self._export_to_html(records, export_config)
                elif export_config['export_type'] == 'json':
                    self._export_to_json(records, export_config)
                    
        except Exception as e:
            InfoBar.error(
                title="导出失败",
                content=f"导出数据时出错: {str(e)}",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=4000,
                parent=self.parent
            )
            print(f"导出异常: {e}")
            import traceback
            traceback.print_exc()
    
    def _export_to_excel(self, records, config):
        """导出到Excel"""
        try:
            from core.excel_exporter import ExcelExporter
            exporter = ExcelExporter()
            
            # 获取保存路径
            save_path, _ = QFileDialog.getSaveFileName(
                self.parent,
                "导出Excel文件",
                "图片信息导出.xlsx",
                "Excel文件 (*.xlsx);;所有文件 (*)"
            )
            
            if save_path:
                exporter.export_records(records, save_path, config)
                InfoBar.success(
                    title="导出成功",
                    content=f"Excel文件已保存到: {save_path}",
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=3000,
                    parent=self.parent
                )
        except Exception as e:
            raise e
    
    def _export_to_html(self, records, config):
        """导出到HTML"""
        try:
            # 获取保存路径
            save_path, _ = QFileDialog.getSaveFileName(
                self.parent,
                "导出HTML文件",
                "图片信息导出.html",
                "HTML文件 (*.html);;所有文件 (*)"
            )
            
            if save_path:
                html_content = self.parent.html_exporter.export_multiple_records(records, config)
                with open(save_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                
                InfoBar.success(
                    title="导出成功",
                    content=f"HTML文件已保存到: {save_path}",
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=3000,
                    parent=self.parent
                )
        except Exception as e:
            raise e
    
    def _export_to_json(self, records, config):
        """导出到JSON"""
        try:
            # 获取保存路径
            save_path, _ = QFileDialog.getSaveFileName(
                self.parent,
                "导出JSON文件",
                "图片信息导出.json",
                "JSON文件 (*.json);;所有文件 (*)"
            )
            
            if save_path:
                # 处理记录数据
                export_records = []
                for record in records:
                    # 根据配置过滤字段
                    filtered_record = {}
                    if config.get('include_basic_info', True):
                        filtered_record.update({
                            'file_path': record.get('file_path', ''),
                            'custom_name': record.get('custom_name', ''),
                            'file_size': record.get('file_size', ''),
                            'image_size': record.get('image_size', ''),
                        })
                    
                    if config.get('include_prompts', True):
                        filtered_record.update({
                            'prompt': record.get('prompt', ''),
                            'negative_prompt': record.get('negative_prompt', ''),
                        })
                    
                    if config.get('include_user_data', True):
                        filtered_record.update({
                            'tags': record.get('tags', ''),
                            'notes': record.get('notes', ''),
                        })
                    
                    if config.get('include_generation_params', True):
                        # 包含生成参数
                        for key, value in record.items():
                            if key not in filtered_record:
                                filtered_record[key] = value
                    
                    export_records.append(filtered_record)
                
                # 保存JSON文件
                with open(save_path, 'w', encoding='utf-8') as f:
                    json.dump(export_records, f, ensure_ascii=False, indent=2)
                
                InfoBar.success(
                    title="导出成功",
                    content=f"JSON文件已保存到: {save_path}",
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=3000,
                    parent=self.parent
                )
        except Exception as e:
            raise e 