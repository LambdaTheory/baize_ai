#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fluent Design 批量导出对话框
使用PyQt-Fluent-Widgets组件库
"""

import os
import json
import csv
from datetime import datetime
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFileDialog, 
                            QLabel, QProgressBar, QTextEdit, QMessageBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal

from qfluentwidgets import (CardWidget, PushButton, RadioButton, 
                           SubtitleLabel, BodyLabel, LineEdit, ComboBox)
from .fluent_styles import FluentTheme, FluentIcons, FluentColors, FluentSpacing


class BatchExportThread(QThread):
    """批量导出线程"""
    progress_updated = pyqtSignal(int, str)  # 进度和状态消息
    export_finished = pyqtSignal(bool, str)  # 完成状态和消息
    
    def __init__(self, records, export_format, output_path, include_images=False):
        super().__init__()
        self.records = records
        self.export_format = export_format
        self.output_path = output_path
        self.include_images = include_images
        
    def run(self):
        """执行导出"""
        try:
            total_records = len(self.records)
            
            if self.export_format == "HTML":
                self.export_to_html()
            elif self.export_format == "JSON":  
                self.export_to_json()
            elif self.export_format == "CSV":
                self.export_to_csv()
            elif self.export_format == "EXCEL":
                self.export_to_excel()
                
            self.export_finished.emit(True, f"成功导出 {total_records} 条记录")
            
        except Exception as e:
            self.export_finished.emit(False, f"导出失败: {str(e)}")
            
    def export_to_html(self):
        """导出为HTML格式"""
        html_content = self.generate_html_content()
        
        output_file = os.path.join(self.output_path, f"批量导出_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
            
        self.progress_updated.emit(100, f"HTML文件已保存到: {output_file}")
        
    def export_to_json(self):
        """导出为JSON格式"""
        export_data = []
        
        for i, record in enumerate(self.records):
            # 处理Lora信息
            lora_info_str = record.get('lora_info', '')
            lora_data = None
            if lora_info_str:
                try:
                    from core.data_manager import DataManager
                    dm = DataManager()
                    lora_data = dm._deserialize_lora_info(lora_info_str)
                except:
                    lora_data = {"raw": lora_info_str}
            
            export_record = {
                "id": record.get('id'),
                "file_path": record.get('file_path'),
                "custom_name": record.get('custom_name'),
                "positive_prompt": record.get('prompt'),
                "negative_prompt": record.get('negative_prompt'),
                "model": record.get('model'),
                "sampler": record.get('sampler'),
                "steps": record.get('steps'),
                "cfg_scale": record.get('cfg_scale'),
                "seed": record.get('seed'),
                "lora_info": lora_data,
                "generation_params": record.get('generation_params'),
                "generation_source": record.get('generation_source'),
                "tags": record.get('tags'),
                "notes": record.get('notes'),
                "workflow_data": record.get('workflow_data'),
                "created_at": record.get('created_at'),
                "updated_at": record.get('updated_at')
            }
            export_data.append(export_record)
            
            progress = int((i + 1) / len(self.records) * 100)
            self.progress_updated.emit(progress, f"处理记录 {i+1}/{len(self.records)}")
            
        output_file = os.path.join(self.output_path, f"批量导出_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
            
        self.progress_updated.emit(100, f"JSON文件已保存到: {output_file}")
        
    def export_to_csv(self):
        """导出为CSV格式"""
        output_file = os.path.join(self.output_path, f"批量导出_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
        
        with open(output_file, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            
            # 写入表头
            headers = [
                "ID", "文件路径", "自定义名称", "正向提示词", "负向提示词", 
                "模型", "采样器", "采样步数", "CFG缩放", "种子", "Lora信息", 
                "生成参数", "生成来源", "标签", "备注", "工作流数据", "创建时间", "更新时间"
            ]
            writer.writerow(headers)
            
            for i, record in enumerate(self.records):
                # 处理Lora信息显示
                lora_info_str = record.get('lora_info', '')
                lora_display = ""
                if lora_info_str:
                    try:
                        from core.data_manager import DataManager
                        dm = DataManager()
                        lora_info = dm._deserialize_lora_info(lora_info_str)
                        if lora_info and 'loras' in lora_info and lora_info['loras']:
                            lora_names = [lora.get('name', '未知') for lora in lora_info['loras']]
                            lora_display = "; ".join(lora_names)
                        elif lora_info and 'raw_lora_text' in lora_info:
                            lora_display = lora_info['raw_lora_text']
                    except:
                        lora_display = "解析错误"
                
                row = [
                    record.get('id', ''),
                    record.get('file_path', ''),
                    record.get('custom_name', ''),
                    record.get('prompt', ''),
                    record.get('negative_prompt', ''),
                    record.get('model', ''),
                    record.get('sampler', ''),
                    record.get('steps', ''),
                    record.get('cfg_scale', ''),
                    record.get('seed', ''),
                    lora_display,
                    record.get('generation_params', ''),
                    record.get('generation_source', ''),
                    record.get('tags', ''),
                    record.get('notes', ''),
                    record.get('workflow_data', ''),
                    record.get('created_at', ''),
                    record.get('updated_at', '')
                ]
                writer.writerow(row)
                
                progress = int((i + 1) / len(self.records) * 100)
                self.progress_updated.emit(progress, f"处理记录 {i+1}/{len(self.records)}")
                
        self.progress_updated.emit(100, f"CSV文件已保存到: {output_file}")
        
    def export_to_excel(self):
        """导出为Excel格式"""
        from core.excel_exporter import ExcelExporter
        
        output_file = os.path.join(self.output_path, f"批量导出_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx")
        
        exporter = ExcelExporter()
        
        # 更新进度
        self.progress_updated.emit(50, "正在生成Excel文件...")
        
        success = exporter.export_records(
            self.records, 
            output_file, 
            include_images=self.include_images
        )
        
        if success:
            self.progress_updated.emit(100, f"Excel文件已保存到: {output_file}")
        else:
            raise Exception("Excel导出失败")
        
    def generate_html_content(self):
        """生成HTML内容"""
        html_template = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI图片信息批量导出</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 600;
        }}
        
        .header p {{
            font-size: 1.1em;
            opacity: 0.9;
        }}
        
        .stats {{
            display: flex;
            justify-content: center;
            gap: 40px;
            margin-top: 20px;
            flex-wrap: wrap;
        }}
        
        .stat-item {{
            text-align: center;
        }}
        
        .stat-number {{
            font-size: 2em;
            font-weight: bold;
            display: block;
        }}
        
        .stat-label {{
            font-size: 0.9em;
            opacity: 0.8;
        }}
        
        .content {{
            padding: 30px;
        }}
        
        .record-card {{
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 16px;
            margin-bottom: 30px;
            overflow: hidden;
            transition: all 0.3s ease;
        }}
        
        .record-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        }}
        
        .record-header {{
            background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%);
            padding: 20px;
            border-bottom: 1px solid #e2e8f0;
        }}
        
        .record-title {{
            font-size: 1.3em;
            font-weight: 600;
            color: #1e293b;
            margin-bottom: 8px;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .record-meta {{
            display: flex;
            gap: 20px;
            font-size: 0.9em;
            color: #64748b;
            flex-wrap: wrap;
        }}
        
        .record-body {{
            padding: 25px;
        }}
        
        .info-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }}
        
        .info-item {{
            background: white;
            padding: 15px;
            border-radius: 12px;
            border: 1px solid #e2e8f0;
        }}
        
        .info-label {{
            font-weight: 600;
            color: #374151;
            margin-bottom: 8px;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .info-value {{
            color: #1f2937;
            line-height: 1.5;
            word-break: break-word;
        }}
        
        .prompt-section {{
            margin-top: 20px;
        }}
        
        .prompt-positive, .prompt-negative {{
            background: white;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 15px;
            margin-bottom: 15px;
        }}
        
        .prompt-positive {{
            border-left: 4px solid #10b981;
        }}
        
        .prompt-negative {{
            border-left: 4px solid #ef4444;
        }}
        
        .prompt-label {{
            font-weight: 600;
            margin-bottom: 8px;
            font-size: 0.9em;
        }}
        
        .prompt-positive .prompt-label {{
            color: #059669;
        }}
        
        .prompt-negative .prompt-label {{
            color: #dc2626;
        }}
        
        .prompt-text {{
            line-height: 1.6;
            color: #374151;
        }}
        
        .tag {{
            display: inline-block;
            background: #ddd6fe;
            color: #5b21b6;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.8em;
            margin: 2px;
            font-weight: 500;
        }}
        
        .footer {{
            background: #f8fafc;
            padding: 20px;
            text-align: center;
            color: #64748b;
            border-top: 1px solid #e2e8f0;
        }}
        
        @media (max-width: 768px) {{
            .stats {{
                gap: 20px;
            }}
            
            .record-meta {{
                flex-direction: column;
                gap: 8px;
            }}
            
            .info-grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎨 AI图片信息批量导出</h1>
            <p>AI Image Information Batch Export</p>
            <div class="stats">
                <div class="stat-item">
                    <span class="stat-number">{total_count}</span>
                    <span class="stat-label">总记录数</span>
                </div>
                <div class="stat-item">
                    <span class="stat-number">{export_time}</span>
                    <span class="stat-label">导出时间</span>
                </div>
            </div>
        </div>
        
        <div class="content">
            {records_html}
        </div>
        
        <div class="footer">
            <p>由 AI图片信息提取工具 生成 | Generated by AI Image Info Extractor</p>
            <p>导出时间: {export_time_full}</p>
        </div>
    </div>
</body>
</html>
        '''
        
        # 生成记录HTML
        records_html = ""
        for i, record in enumerate(self.records):
            # 处理Lora信息
            lora_info_str = record.get('lora_info', '')
            lora_display = "无"
            if lora_info_str:
                try:
                    from core.data_manager import DataManager
                    dm = DataManager()
                    lora_info = dm._deserialize_lora_info(lora_info_str)
                    if lora_info and 'loras' in lora_info and lora_info['loras']:
                        lora_list = []
                        for lora in lora_info['loras']:
                            name = lora.get('name', '未知')
                            strength = lora.get('strength', 1.0)
                            lora_list.append(f"{name} ({strength})")
                        lora_display = "<br>".join(lora_list)
                    elif lora_info and 'raw_lora_text' in lora_info:
                        lora_display = lora_info['raw_lora_text']
                except:
                    lora_display = "解析错误"
            
            # 处理标签
            tags_html = ""
            tags = record.get('tags', '')
            if tags:
                tag_list = [tag.strip() for tag in tags.split(',') if tag.strip()]
                tags_html = ''.join([f'<span class="tag">{tag}</span>' for tag in tag_list])
            
            record_html = f'''
            <div class="record-card">
                <div class="record-header">
                    <div class="record-title">
                        🖼️ {record.get('custom_name', '') or os.path.basename(record.get('file_path', '未知文件'))}
                    </div>
                    <div class="record-meta">
                        <span>📁 {os.path.basename(record.get('file_path', ''))}</span>
                        <span>🔗 {record.get('generation_source', '未知')}</span>
                        <span>📅 {record.get('created_at', '')[:16] if record.get('created_at') else ''}</span>
                    </div>
                </div>
                
                <div class="record-body">
                    <div class="info-grid">
                        <div class="info-item">
                            <div class="info-label">🤖 模型</div>
                            <div class="info-value">{record.get('model', '未知')}</div>
                        </div>
                        <div class="info-item">
                            <div class="info-label">🎯 Lora</div>
                            <div class="info-value">{lora_display}</div>
                        </div>
                        <div class="info-item">
                            <div class="info-label">🎲 采样器</div>
                            <div class="info-value">{record.get('sampler', '无')}</div>
                        </div>
                        <div class="info-item">
                            <div class="info-label">🔢 采样步数</div>
                            <div class="info-value">{record.get('steps', '无')}</div>
                        </div>
                        <div class="info-item">
                            <div class="info-label">📊 CFG缩放</div>
                            <div class="info-value">{record.get('cfg_scale', '无')}</div>
                        </div>
                        <div class="info-item">
                            <div class="info-label">🌱 种子</div>
                            <div class="info-value">{record.get('seed', '无')}</div>
                        </div>
                        <div class="info-item">
                            <div class="info-label">⚙️ 生成参数</div>
                            <div class="info-value">{record.get('generation_params', '无')}</div>
                        </div>
                        <div class="info-item">
                            <div class="info-label">🏷️ 标签</div>
                            <div class="info-value">{tags_html or '无标签'}</div>
                        </div>
                    </div>
                    
                    <div class="prompt-section">
                        <div class="prompt-positive">
                            <div class="prompt-label">✅ 正向提示词</div>
                            <div class="prompt-text">{record.get('prompt', '无')}</div>
                        </div>
                        <div class="prompt-negative">
                            <div class="prompt-label">❌ 负向提示词</div>
                            <div class="prompt-text">{record.get('negative_prompt', '无')}</div>
                        </div>
                    </div>
                    
                    {f'<div class="info-item"><div class="info-label">📝 备注</div><div class="info-value">{record.get("notes", "")}</div></div>' if record.get('notes') else ''}
                </div>
            </div>
            '''
            records_html += record_html
            
            progress = int((i + 1) / len(self.records) * 90)
            self.progress_updated.emit(progress, f"生成HTML内容 {i+1}/{len(self.records)}")
        
        # 填充模板
        export_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        html_content = html_template.format(
            total_count=len(self.records),
            export_time=datetime.now().strftime('%H:%M:%S'),
            export_time_full=export_time,
            records_html=records_html
        )
        
        return html_content


class FluentBatchExportDialog(QDialog):
    """Fluent Design 批量导出对话框"""
    
    def __init__(self, records, parent=None):
        super().__init__(parent)
        self.records = records
        self.export_thread = None
        self.init_ui()
        
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("批量导出")
        self.setFixedSize(500, 600)
        self.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint)
        
        # 主布局
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # 标题
        title = SubtitleLabel("📤 批量导出设置")
        title.setStyleSheet(f"""
            color: {FluentColors.get_color('text_primary')};
            font-weight: 600;
            margin-bottom: 10px;
        """)
        main_layout.addWidget(title)
        
        # 导出信息卡片
        info_card = CardWidget()
        info_card.setBorderRadius(12)
        info_layout = QVBoxLayout()
        info_layout.setContentsMargins(16, 16, 16, 16)
        
        info_label = BodyLabel(f"将导出 {len(self.records)} 条记录")
        info_label.setStyleSheet(f"color: {FluentColors.get_color('text_primary')};")
        info_layout.addWidget(info_label)
        
        info_card.setLayout(info_layout)
        main_layout.addWidget(info_card)
        
        # 导出格式选择
        format_card = CardWidget()
        format_card.setBorderRadius(12)
        format_layout = QVBoxLayout()
        format_layout.setContentsMargins(16, 16, 16, 16)
        
        format_title = BodyLabel("导出格式")
        format_title.setStyleSheet(f"""
            color: {FluentColors.get_color('text_primary')};
            font-weight: 600;
            margin-bottom: 8px;
        """)
        format_layout.addWidget(format_title)
        
        # 格式选项
        self.excel_radio = RadioButton("Excel - 表格格式（推荐，含图片）")
        self.excel_radio.setChecked(True)
        self.html_radio = RadioButton("HTML - 网页格式")
        self.json_radio = RadioButton("JSON - 数据格式")
        self.csv_radio = RadioButton("CSV - 表格格式")
        
        format_layout.addWidget(self.excel_radio)
        format_layout.addWidget(self.html_radio)
        format_layout.addWidget(self.json_radio)
        format_layout.addWidget(self.csv_radio)
        
        format_card.setLayout(format_layout)
        main_layout.addWidget(format_card)
        
        # 输出路径选择
        path_card = CardWidget()
        path_card.setBorderRadius(12)
        path_layout = QVBoxLayout()
        path_layout.setContentsMargins(16, 16, 16, 16)
        
        path_title = BodyLabel("输出路径")
        path_title.setStyleSheet(f"""
            color: {FluentColors.get_color('text_primary')};
            font-weight: 600;
            margin-bottom: 8px;
        """)
        path_layout.addWidget(path_title)
        
        path_input_layout = QHBoxLayout()
        self.path_input = LineEdit()
        self.path_input.setPlaceholderText("选择导出文件夹...")
        self.path_input.setText(os.path.expanduser("~/Desktop"))
        
        self.browse_btn = PushButton("浏览")
        self.browse_btn.setFixedWidth(80)
        self.browse_btn.clicked.connect(self.browse_output_path)
        
        path_input_layout.addWidget(self.path_input)
        path_input_layout.addWidget(self.browse_btn)
        path_layout.addLayout(path_input_layout)
        
        path_card.setLayout(path_layout)
        main_layout.addWidget(path_card)
        
        # 进度显示
        self.progress_card = CardWidget()
        self.progress_card.setBorderRadius(12)
        self.progress_card.setVisible(False)
        
        progress_layout = QVBoxLayout()
        progress_layout.setContentsMargins(16, 16, 16, 16)
        
        self.progress_label = BodyLabel("准备导出...")
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
        
        progress_layout.addWidget(self.progress_label)
        progress_layout.addWidget(self.progress_bar)
        
        self.progress_card.setLayout(progress_layout)
        main_layout.addWidget(self.progress_card)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.cancel_btn = PushButton("取消")
        self.cancel_btn.setFixedSize(100, 36)
        self.cancel_btn.clicked.connect(self.reject)
        
        self.export_btn = PushButton("开始导出")
        self.export_btn.setFixedSize(120, 36)
        self.export_btn.setStyleSheet(f"""
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
        self.export_btn.clicked.connect(self.start_export)
        
        button_layout.addWidget(self.cancel_btn)
        button_layout.addSpacing(10)
        button_layout.addWidget(self.export_btn)
        
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)
        
    def browse_output_path(self):
        """浏览输出路径"""
        folder = QFileDialog.getExistingDirectory(
            self, "选择导出文件夹", self.path_input.text()
        )
        if folder:
            self.path_input.setText(folder)
            
    def start_export(self):
        """开始导出"""
        output_path = self.path_input.text().strip()
        if not output_path:
            QMessageBox.warning(self, "警告", "请选择输出路径")
            return
            
        if not os.path.exists(output_path):
            QMessageBox.warning(self, "警告", "输出路径不存在")
            return
            
        # 确定导出格式
        if self.excel_radio.isChecked():
            export_format = "EXCEL"
        elif self.html_radio.isChecked():
            export_format = "HTML"
        elif self.json_radio.isChecked():
            export_format = "JSON"
        else:
            export_format = "CSV"
            
        # 显示进度
        self.progress_card.setVisible(True)
        self.export_btn.setEnabled(False)
        self.cancel_btn.setText("取消")
        
        # 启动导出线程
        self.export_thread = BatchExportThread(
            self.records, export_format, output_path, include_images=True
        )
        self.export_thread.progress_updated.connect(self.update_progress)
        self.export_thread.export_finished.connect(self.export_finished)
        self.export_thread.start()
        
    def update_progress(self, progress, message):
        """更新进度"""
        self.progress_bar.setValue(progress)
        self.progress_label.setText(message)
        
    def export_finished(self, success, message):
        """导出完成"""
        self.export_btn.setEnabled(True)
        self.cancel_btn.setText("关闭")
        
        if success:
            self.progress_label.setText("✅ " + message)
            QMessageBox.information(self, "导出成功", message)
            self.accept()
        else:
            self.progress_label.setText("❌ " + message)
            QMessageBox.critical(self, "导出失败", message) 