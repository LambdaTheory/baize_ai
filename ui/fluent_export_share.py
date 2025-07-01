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
        """复制图片信息到剪贴板 - SD WebUI标准格式"""
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
            # 获取图片信息
            image_info = self.parent.image_reader.extract_info(self.parent.current_file_path)
            
            # 获取当前界面显示的提示词
            positive_prompt = self.parent.positive_prompt_text.toPlainText().strip()
            negative_prompt = self.parent.negative_prompt_text.toPlainText().strip()
            
            # 如果界面没有提示词，尝试从图片信息中获取
            if not positive_prompt and image_info:
                positive_prompt = image_info.get('prompt', '')
            if not negative_prompt and image_info:
                negative_prompt = image_info.get('negative_prompt', '')
            
            # 构建SD WebUI标准格式
            sd_format_parts = []
            
            # 正向提示词（必须在第一行）
            if positive_prompt:
                sd_format_parts.append(positive_prompt)
            else:
                sd_format_parts.append("")  # 即使没有也要有空行
            
            # 负向提示词
            if negative_prompt:
                sd_format_parts.append(f"Negative prompt: {negative_prompt}")
            
            # 生成参数行
            if image_info:
                param_parts = []
                
                # Steps
                steps = image_info.get('steps', '')
                if steps:
                    param_parts.append(f"Steps: {steps}")
                
                # Sampler
                sampler = image_info.get('sampler', image_info.get('sampler_name', ''))
                if sampler:
                    param_parts.append(f"Sampler: {sampler}")
                
                # CFG scale
                cfg_scale = image_info.get('cfg_scale', '')
                if cfg_scale:
                    param_parts.append(f"CFG scale: {cfg_scale}")
                
                # Seed
                seed = image_info.get('seed', '')
                if seed:
                    param_parts.append(f"Seed: {seed}")
                
                # Size (尺寸)
                width = image_info.get('width', '')
                height = image_info.get('height', '')
                if width and height:
                    param_parts.append(f"Size: {width}x{height}")
                elif hasattr(self.parent, 'image_size_label'):
                    # 从界面标签获取尺寸信息
                    size_text = self.parent.image_size_label.text()
                    if size_text and size_text != "-":
                        # 转换 "宽 × 高" 格式为 "宽x高"
                        size_formatted = size_text.replace(' × ', 'x').replace('×', 'x')
                        param_parts.append(f"Size: {size_formatted}")
                
                # Model
                model = image_info.get('model', image_info.get('model_name', ''))
                if model:
                    param_parts.append(f"Model: {model}")
                
                # Model hash (如果有的话)
                model_hash = image_info.get('model_hash', '')
                if model_hash:
                    param_parts.append(f"Model hash: {model_hash}")
                
                # 将参数用逗号和空格连接
                if param_parts:
                    sd_format_parts.append(", ".join(param_parts))
            
            # 合并所有部分
            sd_format_text = "\n".join(sd_format_parts)
            
            # 复制到剪贴板
            clipboard = QApplication.clipboard()
            clipboard.setText(sd_format_text)
            
            # 埋点：追踪复制信息功能使用
            if hasattr(self.parent, 'track_feature_usage'):
                self.parent.track_feature_usage("复制信息", {
                    "has_prompts": bool(positive_prompt or negative_prompt),
                    "format": "sd_webui_standard",
                    "content_length": len(sd_format_text)
                })
            
            InfoBar.success(
                title="复制成功",
                content="SD标准格式信息已复制到剪贴板",
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
            print(f"复制信息异常: {e}")
            import traceback
            traceback.print_exc()
    
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
            positive_prompt = self.parent.positive_prompt_text.toPlainText().strip()
            negative_prompt = self.parent.negative_prompt_text.toPlainText().strip()
            
            # 准备导出数据
            export_data = {
                'file_path': self.parent.current_file_path,
                'custom_name': custom_name or os.path.basename(self.parent.current_file_path),
                'tags': tags,
                'notes': '',  # 备注功能已移除，设为空字符串
                'prompt': positive_prompt,
                'negative_prompt': negative_prompt,
            }
            
            if image_info:
                export_data.update(image_info)
            
            # 生成HTML
            html_content = self.parent.html_exporter.export_single_record(export_data, include_image=True)
            
            # 保存HTML文件
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # 埋点：追踪HTML分享功能使用
            if hasattr(self.parent, 'track_feature_usage'):
                self.parent.track_feature_usage("HTML分享", {
                    "has_prompts": bool(positive_prompt or negative_prompt),
                    "has_tags": bool(tags),
                    "has_custom_name": bool(custom_name),
                    "file_size": len(html_content)
                })
            
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
            msgbox = MessageBox(
                title="打开文件",
                content="是否要打开生成的HTML分享页面？",
                parent=self.parent
            )
            
            if msgbox.exec_():
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