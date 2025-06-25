#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTML导出模块
用于生成美观的AI图片信息分享页面
"""

import os
import json
import base64
from datetime import datetime
from typing import Dict, Any, Optional


class HTMLExporter:
    """HTML导出器"""
    
    def __init__(self):
        self.template = self._get_html_template()
    
    def export_to_html(self, record_data: Dict[str, Any], output_path: str, 
                      include_image: bool = True) -> bool:
        """
        导出记录为HTML分享页面
        
        Args:
            record_data: 图片记录数据
            output_path: 输出文件路径
            include_image: 是否在HTML中包含图片
            
        Returns:
            bool: 是否成功导出
        """
        try:
            # 准备数据
            html_data = self._prepare_html_data(record_data, include_image)
            
            # 渲染HTML
            html_content = self._render_html(html_data)
            
            # 写入文件
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            return True
            
        except Exception as e:
            print(f"导出HTML失败: {e}")
            return False
    
    def _prepare_html_data(self, record_data: Dict[str, Any], 
                          include_image: bool) -> Dict[str, Any]:
        """准备HTML渲染数据"""
        
        # 处理图片
        image_data = ""
        if include_image and record_data.get('file_path'):
            try:
                image_data = self._encode_image_to_base64(record_data['file_path'])
            except:
                image_data = ""
        
        # 处理LoRA信息
        lora_info = record_data.get('lora_info', '')
        lora_data = {}
        
        if isinstance(lora_info, str) and lora_info.strip():
            try:
                lora_data = json.loads(lora_info)
                # 如果是包装格式 {"loras": [...]}，提取内部的loras数组
                if isinstance(lora_data, dict) and 'loras' in lora_data:
                    lora_data = lora_data['loras']
            except:
                lora_data = {}
        elif lora_info:
            lora_data = lora_info
        
        # 整理标签
        tags = record_data.get('tags', '')
        tag_list = [tag.strip() for tag in tags.split(',') if tag.strip()] if tags else []
        
        return {
            'title': record_data.get('custom_name') or record_data.get('file_name', '未命名图片'),
            'image_data': image_data,
            'prompt': record_data.get('prompt', ''),
            'negative_prompt': record_data.get('negative_prompt', ''),
            'model': record_data.get('model', ''),
            'sampler': record_data.get('sampler', ''),
            'steps': record_data.get('steps', ''),
            'cfg_scale': record_data.get('cfg_scale', ''),
            'seed': record_data.get('seed', ''),
            'lora_data': lora_data,
            'notes': record_data.get('notes', ''),
            'tags': tag_list,
            'created_at': record_data.get('created_at', ''),
            'export_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def _encode_image_to_base64(self, image_path: str) -> str:
        """将图片编码为base64"""
        if not os.path.exists(image_path):
            return ""
        
        try:
            with open(image_path, 'rb') as f:
                image_data = f.read()
            
            # 获取文件扩展名确定MIME类型
            ext = os.path.splitext(image_path)[1].lower()
            mime_type = {
                '.png': 'image/png',
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.webp': 'image/webp'
            }.get(ext, 'image/png')
            
            base64_data = base64.b64encode(image_data).decode('utf-8')
            return f"data:{mime_type};base64,{base64_data}"
            
        except Exception as e:
            print(f"图片编码失败: {e}")
            return ""
    
    def _render_html(self, data: Dict[str, Any]) -> str:
        """渲染HTML内容"""
        
        # 渲染LoRA信息
        lora_html = ""
        if data['lora_data']:
            # 处理不同格式的LoRA数据
            if isinstance(data['lora_data'], list):
                # 列表格式：[{'name': '...', 'weight': 0.8, 'hash': '...'}, ...]
                for lora_item in data['lora_data']:
                    if isinstance(lora_item, dict):
                        lora_name = lora_item.get('name', '未知LoRA')
                        lora_weight = lora_item.get('weight', 'N/A')
                        lora_hash = lora_item.get('hash', '')
                        
                        lora_html += f"""
                        <div class="info-bubble lora-bubble">
                            <div class="bubble-label">LoRA</div>
                            <div class="bubble-content">
                                <div class="lora-name">{lora_name}</div>
                                <div class="lora-weight">权重: {lora_weight}</div>
                                {f'<div class="lora-hash">Hash: {lora_hash[:8]}...</div>' if lora_hash else ''}
                            </div>
                        </div>
                        """
            elif isinstance(data['lora_data'], dict):
                # 字典格式：{'lora_name': weight, ...}
                for lora_name, lora_weight in data['lora_data'].items():
                    lora_html += f"""
                    <div class="info-bubble lora-bubble">
                        <div class="bubble-label">LoRA</div>
                        <div class="bubble-content">
                            <div class="lora-name">{lora_name}</div>
                            <div class="lora-weight">权重: {lora_weight}</div>
                        </div>
                    </div>
                    """
            else:
                # 其他格式，显示原始数据
                lora_html += f"""
                <div class="info-bubble lora-bubble">
                    <div class="bubble-label">LoRA</div>
                    <div class="bubble-content">
                        <div class="lora-raw">{str(data['lora_data'])}</div>
                    </div>
                </div>
                """
        
        # 渲染图片
        image_html = ""
        if data['image_data']:
            image_html = f'<img src="{data["image_data"]}" alt="AI Generated Image" class="preview-image">'
        else:
            image_html = '<div class="no-image-placeholder">📷<br>未包含图片</div>'
        
        # 准备复制的文本数据
        # 处理LoRA数据格式转换
        lora_copy_data = data['lora_data']
        if isinstance(data['lora_data'], list):
            # 将列表格式转换为便于复制的格式
            lora_copy_data = {}
            for lora_item in data['lora_data']:
                if isinstance(lora_item, dict):
                    name = lora_item.get('name', '未知LoRA')
                    weight = lora_item.get('weight', 'N/A')
                    lora_copy_data[name] = weight
        
        copy_data = {
            'prompt': data['prompt'],
            'negative_prompt': data['negative_prompt'],
            'model': data['model'],
            'sampler': data['sampler'],
            'steps': data['steps'],
            'cfg_scale': data['cfg_scale'],
            'seed': data['seed'],
            'lora': lora_copy_data
        }
        
        # 填充模板
        return self.template.format(
            title=data['title'],
            image_html=image_html,
            prompt=data['prompt'],
            negative_prompt=data['negative_prompt'],
            model=data['model'],
            sampler=data['sampler'],
            steps=data['steps'],
            cfg_scale=data['cfg_scale'],
            seed=data['seed'],
            lora_html=lora_html,
            export_time=data['export_time'],
            copy_data_json=json.dumps(copy_data, ensure_ascii=False)
        )
    
    def _get_html_template(self) -> str:
        """获取HTML模板"""
        return """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI图片生成信息 - {title}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Segoe UI', 'Microsoft YaHei', -apple-system, BlinkMacSystemFont, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 30px;
            color: #333;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.98);
            border-radius: 24px;
            padding: 40px;
            box-shadow: 0 25px 50px rgba(0, 0, 0, 0.15);
            backdrop-filter: blur(20px);
        }}

        .main-content {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 40px;
            align-items: start;
        }}

        .left-panel {{
            display: flex;
            flex-direction: column;
            gap: 30px;
        }}

        .right-panel {{
            display: flex;
            flex-direction: column;
            gap: 30px;
            max-height: calc(70vh + 90px);
            overflow-y: auto;
            padding-right: 10px;
        }}

        /* 自定义滚动条样式 */
        .right-panel::-webkit-scrollbar {{
            width: 8px;
        }}

        .right-panel::-webkit-scrollbar-track {{
            background: rgba(240, 240, 240, 0.3);
            border-radius: 10px;
        }}

        .right-panel::-webkit-scrollbar-thumb {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 10px;
            transition: all 0.3s ease;
        }}

        .right-panel::-webkit-scrollbar-thumb:hover {{
            background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%);
            box-shadow: 0 0 10px rgba(102, 126, 234, 0.3);
        }}

        /* Firefox滚动条样式 */
        .right-panel {{
            scrollbar-width: thin;
            scrollbar-color: #667eea rgba(240, 240, 240, 0.3);
        }}

        .header {{
            text-align: center;
            margin-bottom: 50px;
            padding-bottom: 30px;
            border-bottom: 3px solid #f0f0f0;
        }}

        .title {{
            font-size: 2.2rem;
            font-weight: 700;
            background: linear-gradient(45deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 15px;
        }}

        .subtitle {{
            color: #666;
            font-size: 1rem;
            font-weight: 500;
        }}

        .copy-btn {{
            position: fixed;
            bottom: 30px;
            right: 30px;
            background: linear-gradient(45deg, #4CAF50, #45a049);
            color: white;
            border: none;
            padding: 12px 20px;
            font-size: 0.9rem;
            font-weight: 600;
            border-radius: 40px;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 6px 20px rgba(76, 175, 80, 0.3);
            z-index: 1000;
        }}

        .copy-btn:hover {{
            transform: translateY(-3px);
            box-shadow: 0 12px 35px rgba(76, 175, 80, 0.4);
        }}

        .copy-btn:active {{
            transform: translateY(-1px);
        }}

        .image-section {{
            text-align: center;
            padding: 25px;
            background: rgba(248, 249, 255, 0.8);
            border-radius: 20px;
            border: 2px solid rgba(102, 126, 234, 0.1);
            min-height: 500px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            position: sticky;
            top: 20px;
        }}

        .preview-image {{
            max-width: 100%;
            max-height: 70vh;
            width: auto;
            height: auto;
            object-fit: contain;
            border-radius: 16px;
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.2);
            transition: transform 0.3s ease;
        }}

        .preview-image:hover {{
            transform: scale(1.02);
        }}

        .no-image-placeholder {{
            padding: 80px 40px;
            color: #999;
            font-size: 1.5rem;
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            border-radius: 16px;
            border: 2px dashed #ddd;
            flex-shrink: 0;
            width: fit-content;
            align-self: center;
        }}

        .section-title {{
            font-size: 1.4rem;
            font-weight: 600;
            color: #444;
            margin-bottom: 30px;
            text-align: center;
            position: relative;
        }}

        .section-title::after {{
            content: '';
            position: absolute;
            bottom: -10px;
            left: 50%;
            transform: translateX(-50%);
            width: 60px;
            height: 3px;
            background: linear-gradient(45deg, #667eea, #764ba2);
            border-radius: 2px;
        }}

        .prompt-section {{
            margin-bottom: 0;
        }}

        .prompt-grid {{
            display: grid;
            grid-template-columns: 1fr;
            gap: 20px;
        }}

        .param-section {{
            margin-bottom: 0;
        }}

        .param-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 20px;
        }}

        .lora-section {{
            margin-bottom: 0;
        }}

        .lora-grid {{
            display: grid;
            grid-template-columns: 1fr;
            gap: 20px;
        }}

        .info-bubble {{
            background: linear-gradient(135deg, #fff 0%, #f8f9ff 100%);
            border-radius: 18px;
            padding: 25px;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08);
            border: 1px solid rgba(102, 126, 234, 0.1);
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
            cursor: pointer;
        }}

        .info-bubble::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 5px;
            background: linear-gradient(45deg, #667eea, #764ba2);
        }}

        .info-bubble:hover {{
            transform: translateY(-8px);
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.15);
        }}

        .bubble-label {{
            font-size: 0.85rem;
            font-weight: 700;
            color: #667eea;
            text-transform: uppercase;
            letter-spacing: 1.2px;
            margin-bottom: 12px;
        }}

        .bubble-content {{
            font-size: 0.95rem;
            line-height: 1.6;
            color: #333;
            word-break: break-word;
        }}

        .param-value {{
            font-size: 1rem;
            font-weight: 700;
            color: #e65100;
            margin-top: auto;
        }}

        .lora-bubble .bubble-label {{
            color: #4CAF50;
            font-size: 0.75rem;
            font-weight: 600;
            margin-bottom: 6px;
        }}

        .lora-name {{
            font-weight: 700;
            font-size: 1rem;
            color: #2e7d32;
            margin-bottom: 6px;
        }}

        .lora-weight {{
            color: #4CAF50;
            font-size: 0.9rem;
            font-weight: 500;
        }}

        .lora-hash {{
            color: #888;
            font-size: 0.8rem;
            font-family: 'Courier New', monospace;
            margin-top: 4px;
        }}

        .lora-raw {{
            color: #555;
            font-size: 0.85rem;
            font-family: 'Courier New', monospace;
            background: #f8f9fa;
            padding: 10px;
            border-radius: 6px;
            word-break: break-all;
        }}

        .footer {{
            text-align: center;
            margin-top: 50px;
            padding-top: 30px;
            border-top: 2px solid #eee;
            color: #999;
            font-size: 1rem;
        }}

        .success-message {{
            position: fixed;
            top: 30px;
            right: 30px;
            background: #4CAF50;
            color: white;
            padding: 18px 30px;
            border-radius: 12px;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
            transform: translateX(400px);
            transition: transform 0.3s ease;
            z-index: 1000;
            font-weight: 600;
        }}

        .success-message.show {{
            transform: translateX(0);
        }}

        @media (max-width: 1024px) {{
            .main-content {{
                grid-template-columns: 1fr;
                gap: 30px;
            }}

            .param-grid {{
                grid-template-columns: repeat(3, 1fr);
            }}

            .lora-grid {{
                grid-template-columns: repeat(2, 1fr);
            }}
        }}

        @media (max-width: 768px) {{
            body {{
                padding: 20px;
            }}

            .container {{
                padding: 25px;
            }}

            .title {{
                font-size: 1.8rem;
            }}

            .main-content {{
                grid-template-columns: 1fr;
                gap: 25px;
            }}

            .param-grid {{
                grid-template-columns: repeat(2, 1fr);
            }}

            .lora-grid {{
                grid-template-columns: 1fr;
            }}

            .copy-btn {{
                bottom: 20px;
                right: 20px;
                padding: 15px 20px;
                font-size: 0.9rem;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 class="title">{title}</h1>
            <p class="subtitle">AI图片生成信息分享</p>
        </div>

        <div class="main-content">
            <!-- 左侧面板：图片展示 -->
            <div class="left-panel">
                <div class="image-section">
                    {image_html}
                </div>
            </div>

            <!-- 右侧面板：参数详情 -->
            <div class="right-panel">
                <div class="prompt-section">
                    <h2 class="section-title">🎨 提示词信息</h2>
                    <div class="prompt-grid">
                        <div class="info-bubble prompt-bubble">
                            <div class="bubble-label">正向提示词 (Prompt)</div>
                            <div class="bubble-content">{prompt}</div>
                        </div>

                        <div class="info-bubble negative-prompt-bubble">
                            <div class="bubble-label">负向提示词 (Negative Prompt)</div>
                            <div class="bubble-content">{negative_prompt}</div>
                        </div>
                    </div>
                </div>

                <div class="param-section">
                    <h2 class="section-title">⚙️ 生成参数</h2>
                    <div class="param-grid">
                        <div class="info-bubble">
                            <div class="bubble-label">📱 模型</div>
                            <div class="bubble-content">{model}</div>
                        </div>

                        <div class="info-bubble">
                            <div class="bubble-label">⚙️ 采样器</div>
                            <div class="bubble-content">{sampler}</div>
                        </div>

                        <div class="info-bubble">
                            <div class="bubble-label">🔢 步数</div>
                            <div class="bubble-content">{steps}</div>
                        </div>

                        <div class="info-bubble">
                            <div class="bubble-label">📊 CFG</div>
                            <div class="bubble-content">{cfg_scale}</div>
                        </div>

                        <div class="info-bubble">
                            <div class="bubble-label">🎲 种子</div>
                            <div class="bubble-content">{seed}</div>
                        </div>
                    </div>
                </div>

                <div class="lora-section">
                    <h2 class="section-title">🎯 LoRA模型</h2>
                    <div class="lora-grid">
                        {lora_html}
                    </div>
                </div>
            </div>
        </div>

        <div class="footer">
            <p>生成时间: {export_time}</p>
            <p>由 AI图片信息提取工具 生成</p>
        </div>
    </div>

    <!-- 悬浮复制按钮 -->
    <button class="copy-btn" onclick="copyAllInfo()">
        📋 复制全部生成信息
    </button>

    <div id="successMessage" class="success-message">
        ✅ 信息已复制到剪贴板！
    </div>

    <script>
        const copyData = {copy_data_json};

        function copyAllInfo() {{
            let copyText = '';
            
            if (copyData.prompt) {{
                copyText += `Prompt: ${{copyData.prompt}}\\n\\n`;
            }}
            
            if (copyData.negative_prompt) {{
                copyText += `Negative Prompt: ${{copyData.negative_prompt}}\\n\\n`;
            }}
            
            if (copyData.model) {{
                copyText += `Model: ${{copyData.model}}\\n`;
            }}
            
            if (copyData.sampler) {{
                copyText += `Sampler: ${{copyData.sampler}}\\n`;
            }}
            
            if (copyData.steps) {{
                copyText += `Steps: ${{copyData.steps}}\\n`;
            }}
            
            if (copyData.cfg_scale) {{
                copyText += `CFG Scale: ${{copyData.cfg_scale}}\\n`;
            }}
            
            if (copyData.seed) {{
                copyText += `Seed: ${{copyData.seed}}\\n`;
            }}
            
            if (copyData.lora && Object.keys(copyData.lora).length > 0) {{
                copyText += `\\nLoRA:\\n`;
                for (const [name, weight] of Object.entries(copyData.lora)) {{
                    copyText += `- ${{name}}: ${{weight}}\\n`;
                }}
            }}

            navigator.clipboard.writeText(copyText).then(() => {{
                showSuccessMessage();
            }}).catch(err => {{
                // 降级方案
                const textArea = document.createElement('textarea');
                textArea.value = copyText;
                document.body.appendChild(textArea);
                textArea.select();
                document.execCommand('copy');
                document.body.removeChild(textArea);
                showSuccessMessage();
            }});
        }}

        function showSuccessMessage() {{
            const message = document.getElementById('successMessage');
            message.classList.add('show');
            setTimeout(() => {{
                message.classList.remove('show');
            }}, 3000);
        }}

        // 添加一些交互效果
        document.querySelectorAll('.info-bubble').forEach(bubble => {{
            bubble.addEventListener('click', function() {{
                const contentElement = this.querySelector('.bubble-content, .param-value');
                const content = contentElement ? contentElement.textContent : '';
                if (content.trim()) {{
                    navigator.clipboard.writeText(content).then(() => {{
                        showSuccessMessage();
                    }});
                }}
            }});
        }});
    </script>
</body>
</html>""" 