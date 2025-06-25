#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
提示词反推模块
使用OpenAI GPT-4o Vision API分析图片并生成对应的提示词
"""

import base64
import json
import os
import time
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List
from openai import OpenAI


class PromptReverser:
    """提示词反推器"""
    
    def __init__(self, api_key: str = None, model: str = "gpt-4o-mini", base_url: str = None):
        """
        初始化提示词反推器
        
        Args:
            api_key: API密钥，如果为None则从环境变量读取
            model: 使用的模型，默认为gpt-4o-mini
            base_url: API基础URL，默认使用SSOPEN-API中转站
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY") or "sk-CnEoNNdwU8KeJfIoEg6rcNeLeO5XbF3HafEMckZkuZXvKSGS"
        self.model = model
        self.base_url = base_url or "https://api.ssopen.top/v1"
        
        if not self.api_key:
            raise ValueError("请设置API密钥")
        
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=120
        )
        
        # 系统提示词模板
        self.system_prompt = """你是一个专业的AI图像提示词工程师，精通Stable Diffusion和ComfyUI工作流。
你的任务是分析图片并生成高质量的提示词，同时提供中英文两个版本。

要求：
1. 仔细观察图片的所有细节，包括主体、背景、光线、风格、色彩等
2. 生成的提示词要准确描述图片内容
3. 使用专业的AI绘画术语
4. 同时提供中文和英文版本的提示词
5. 返回标准JSON格式

JSON格式要求：
{
    "sd": {
        "positive": {
            "zh": "中文正向提示词",
            "en": "English positive prompt"
        },
        "negative": {
            "zh": "中文负向提示词", 
            "en": "English negative prompt"
        }
    },
    "comfyui": {
        "clip": {
            "zh": "中文CLIP提示词（不超过75个词）",
            "en": "English CLIP prompt (no more than 75 words)"
        },
        "t5": {
            "zh": "中文T5提示词（不超过150个token）",
            "en": "English T5 prompt (no more than 150 tokens)"
        },
        "clip_weight": 0.8,
        "style": {
            "zh": "中文艺术风格描述",
            "en": "English art style description"
        }
    },
    "is_valid": true
}"""
        
        self.user_prompt = """请根据这张图片生成两套提示词，每套都要包含中英文版本：

1) Stable Diffusion套装：
   - 正向提示词：详细描述图片内容，包括主体、风格、质量关键词（中英文）
   - 负向提示词：常见的负面词汇，避免低质量输出（中英文）

2) ComfyUI套装：
   - CLIP提示词：简洁准确的核心描述（中英文，不超过75个词）
   - T5提示词：详细的场景和风格描述（中英文，不超过150个token）
   - 权重建议和风格分类（中英文）

注意：
- 英文提示词使用专业的AI绘画术语
- 中文提示词要准确传达相同的含义
- 保持中英文版本的一致性
- 最后添加 "is_valid": true 标志

请只返回严格的JSON格式，不要包含其他内容。"""

    def image_to_base64(self, image_path: str) -> str:
        """
        将图片转换为base64编码
        
        Args:
            image_path: 图片路径
            
        Returns:
            str: base64编码的图片数据
        """
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            raise Exception(f"读取图片失败: {str(e)}")

    def analyze_image(self, image_path: str) -> Tuple[bool, Dict[str, Any]]:
        """
        分析图片并生成提示词
        
        Args:
            image_path: 图片路径
            
        Returns:
            Tuple[bool, Dict[str, Any]]: (是否成功, 结果数据)
        """
        print(f"[提示词反推] 开始分析图片: {image_path}")
        
        try:
            # 检查文件是否存在
            if not os.path.exists(image_path):
                return False, {"error": "图片文件不存在"}
            
            # 转换图片为base64
            print(f"[提示词反推] 转换图片为base64...")
            base64_image = self.image_to_base64(image_path)
            
            # 构建请求消息
            messages = [
                {
                    "role": "system",
                    "content": self.system_prompt
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": self.user_prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}",
                                "detail": "high"
                            }
                        }
                    ]
                }
            ]
            
            print(f"[提示词反推] 发送API请求到模型: {self.model}")
            
            # 调用API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=2000,
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            print(f"[提示词反推] 收到API响应")
            
            # 解析响应
            content = response.choices[0].message.content
            
            try:
                result_data = json.loads(content)
                print(f"[提示词反推] JSON解析成功")
            except json.JSONDecodeError as e:
                print(f"[提示词反推] JSON解析失败: {str(e)}")
                return False, {"error": f"JSON解析失败: {str(e)}", "raw_content": content}
            
            # 验证结果格式
            if not self._validate_response_format(result_data):
                print(f"[提示词反推] 响应格式验证失败")
                return False, {"error": "响应格式不正确", "data": result_data}
            
            print(f"[提示词反推] 分析完成，Token使用: {response.usage.total_tokens}")
            
            # 返回成功结果
            return True, {
                "prompts": result_data,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                "model": self.model,
                "image_path": image_path
            }
            
        except Exception as e:
            print(f"[提示词反推] 分析异常: {str(e)}")
            return False, {"error": f"分析图片时出错: {str(e)}"}

    def _validate_response_format(self, data: Dict[str, Any]) -> bool:
        """
        验证API响应格式是否正确
        
        Args:
            data: API响应数据
            
        Returns:
            bool: 格式是否正确
        """
        try:
            # 检查基本结构
            if not isinstance(data, dict):
                return False
            
            # 检查sd部分
            if "sd" not in data or not isinstance(data["sd"], dict):
                return False
            
            sd_data = data["sd"]
            if "positive" not in sd_data or "negative" not in sd_data:
                return False
            
            # 检查sd部分的中英文结构
            for field in ["positive", "negative"]:
                if not isinstance(sd_data[field], dict):
                    return False
                if "zh" not in sd_data[field] or "en" not in sd_data[field]:
                    return False
            
            # 检查comfyui部分
            if "comfyui" not in data or not isinstance(data["comfyui"], dict):
                return False
            
            comfyui_data = data["comfyui"]
            required_fields = ["clip", "t5", "style"]
            for field in required_fields:
                if field not in comfyui_data:
                    return False
                # 检查中英文结构
                if isinstance(comfyui_data[field], dict):
                    if "zh" not in comfyui_data[field] or "en" not in comfyui_data[field]:
                        return False
            
            return True
            
        except Exception:
            return False

    def batch_analyze(self, image_paths: list) -> Dict[str, Dict[str, Any]]:
        """
        批量分析多张图片
        
        Args:
            image_paths: 图片路径列表
            
        Returns:
            Dict: 每张图片的分析结果
        """
        results = {}
        
        for i, image_path in enumerate(image_paths):
            print(f"正在分析第 {i+1}/{len(image_paths)} 张图片: {Path(image_path).name}")
            
            success, result = self.analyze_image(image_path)
            results[image_path] = {
                "success": success,
                "data": result
            }
            
            # 添加延迟避免API限流
            if i < len(image_paths) - 1:
                time.sleep(1)
        
        return results

    def export_prompts_to_text(self, result_data: Dict[str, Any], output_path: str = None) -> str:
        """
        将提示词结果导出为文本文件
        
        Args:
            result_data: 分析结果数据
            output_path: 输出文件路径，如果为None则生成默认路径
            
        Returns:
            str: 导出的文件路径
        """
        try:
            prompts = result_data.get("prompts", {})
            
            # 生成文本内容
            content_lines = [
                "=" * 80,
                "AI图片提示词反推结果 / AI Image Prompt Reverse Engineering Results",
                "=" * 80,
                "",
                f"原图路径 / Image Path: {result_data.get('image_path', '未知/Unknown')}",
                f"分析模型 / Model: {result_data.get('model', '未知/Unknown')}",
                f"Token使用 / Token Usage: {result_data.get('usage', {}).get('total_tokens', 0)}",
                "",
                "【Stable Diffusion 提示词 / Prompts】",
                "-" * 60,
                "正向提示词 (中文) / Positive Prompt (Chinese):",
                prompts.get("sd", {}).get("positive", {}).get("zh", ""),
                "",
                "正向提示词 (英文) / Positive Prompt (English):",
                prompts.get("sd", {}).get("positive", {}).get("en", ""),
                "",
                "负向提示词 (中文) / Negative Prompt (Chinese):",
                prompts.get("sd", {}).get("negative", {}).get("zh", ""),
                "",
                "负向提示词 (英文) / Negative Prompt (English):",
                prompts.get("sd", {}).get("negative", {}).get("en", ""),
                "",
                "【ComfyUI 提示词 / Prompts】",
                "-" * 60,
                "CLIP提示词 (中文) / CLIP Prompt (Chinese):",
                prompts.get("comfyui", {}).get("clip", {}).get("zh", ""),
                "",
                "CLIP提示词 (英文) / CLIP Prompt (English):",
                prompts.get("comfyui", {}).get("clip", {}).get("en", ""),
                "",
                "T5提示词 (中文) / T5 Prompt (Chinese):",
                prompts.get("comfyui", {}).get("t5", {}).get("zh", ""),
                "",
                "T5提示词 (英文) / T5 Prompt (English):",
                prompts.get("comfyui", {}).get("t5", {}).get("en", ""),
                "",
                f"CLIP权重 / CLIP Weight: {prompts.get('comfyui', {}).get('clip_weight', 0.8)}",
                "",
                "风格分类 (中文) / Style Category (Chinese):",
                prompts.get("comfyui", {}).get("style", {}).get("zh", "未指定"),
                "",
                "风格分类 (英文) / Style Category (English):",
                prompts.get("comfyui", {}).get("style", {}).get("en", "Not specified"),
                "",
                "=" * 80
            ]
            
            content = "\n".join(content_lines)
            
            # 确定输出路径
            if not output_path:
                image_path = result_data.get('image_path', '')
                if image_path:
                    base_name = Path(image_path).stem
                    output_path = f"{base_name}_prompts.txt"
                else:
                    output_path = "prompts_result.txt"
            
            # 写入文件
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"提示词已导出到: {output_path}")
            return output_path
            
        except Exception as e:
            raise Exception(f"导出文本文件失败: {str(e)}")

    def get_model_list(self) -> list:
        """
        获取可用的模型列表
        
        Returns:
            list: 可用模型列表
        """
        return [
            "gpt-4o-mini",
            "gpt-4o",
            "gpt-4-vision-preview",
            "gpt-4-turbo"
        ]

    def test_api_connection(self) -> Tuple[bool, str]:
        """
        测试API连接
        
        Returns:
            Tuple[bool, str]: (是否成功, 状态消息)
        """
        print(f"[API测试] 开始测试API连接...")
        print(f"[API测试] 模型: {self.model}")
        print(f"[API测试] Base URL: {self.base_url}")
        print(f"[API测试] API Key: {self.api_key[:10]}...{self.api_key[-4:] if len(self.api_key) > 14 else '***'}")
        
        try:
            # 使用更短的超时时间进行快速测试
            print(f"[API测试] 创建测试客户端...")
            test_client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
                timeout=10  # 10秒超时
            )
            
            print(f"[API测试] 发送测试请求...")
            # 使用当前设置的模型进行简单测试
            response = test_client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "Hi"}],
                max_tokens=5,
                temperature=0
            )
            
            print(f"[API测试] 收到响应: {response}")
            
            if response and response.choices and len(response.choices) > 0:
                print(f"[API测试] 测试成功！")
                return True, f"API连接正常 (模型: {self.model})"
            else:
                print(f"[API测试] 响应异常：没有收到有效响应")
                return False, "API响应异常：没有收到有效响应"
                
        except Exception as e:
            error_msg = str(e)
            print(f"[API测试] 异常: {error_msg}")
            
            if "timeout" in error_msg.lower():
                return False, f"API连接超时 (模型: {self.model})，请检查网络连接"
            elif "unauthorized" in error_msg.lower() or "401" in error_msg:
                return False, "API密钥无效，请检查API Key设置"
            elif "not found" in error_msg.lower() or "404" in error_msg:
                return False, f"模型 {self.model} 不可用，请选择其他模型"
            elif "rate limit" in error_msg.lower():
                return False, "API调用频率超限，请稍后再试"
            else:
                return False, f"API连接失败: {error_msg}"
