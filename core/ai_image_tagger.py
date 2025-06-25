#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI图像自动打标签模块
使用OpenAI GPT-4o Vision API分析图片内容并自动生成标签
"""

import base64
import json
import os
import re
from typing import Dict, Any, Optional, Tuple, List, Set
from openai import OpenAI
from difflib import SequenceMatcher


class AIImageTagger:
    """AI图像自动打标签器"""
    
    def __init__(self, api_key: str = None, model: str = "gpt-4o-mini", base_url: str = None):
        """
        初始化AI图像打标签器
        
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
            timeout=60
        )
        
        # 系统提示词
        self.system_prompt = """你是一个专业的图像标签分析师，擅长准确识别图像内容并生成相关标签。

你的任务是：
1. 仔细分析图像的所有重要元素
2. 生成准确、具体的中文标签
3. 标签应该涵盖：主体、风格、场景、情感、色彩、技术特征等
4. 每个标签应该简洁（1-4个字），具体且有意义
5. 返回5-15个最相关的标签

请以JSON格式返回结果：
{
    "tags": ["标签1", "标签2", "标签3", ...],
    "confidence": 0.9,
    "description": "简要描述图像内容"
}

标签分类参考：
- 人物：美女、男性、儿童、老人等
- 风格：写实、动漫、油画、素描、水彩等  
- 场景：室内、户外、自然、城市、海滩等
- 情感：开心、悲伤、严肃、温馨等
- 色彩：明亮、暗色、彩色、黑白等
- 技术：HDR、虚化、特写、全身等
- 物体：建筑、动物、植物、食物、车辆等

请确保返回正确的JSON格式，标签准确且有意义。"""

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

    def analyze_image_for_tags(self, image_path: str) -> Tuple[bool, Dict[str, Any]]:
        """
        分析图片并生成标签
        
        Args:
            image_path: 图片路径
            
        Returns:
            Tuple[bool, Dict[str, Any]]: (是否成功, 结果数据)
        """
        print(f"[AI打标签] 开始分析图片: {image_path}")
        
        try:
            # 检查文件是否存在
            if not os.path.exists(image_path):
                return False, {"error": "图片文件不存在"}
            
            # 转换图片为base64
            print(f"[AI打标签] 转换图片为base64...")
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
                            "text": "请分析这张图片并生成相关的中文标签。"
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
            
            print(f"[AI打标签] 发送API请求到模型: {self.model}")
            
            # 调用API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=800,
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            print(f"[AI打标签] 收到API响应")
            
            # 解析响应
            content = response.choices[0].message.content
            
            try:
                result_data = json.loads(content)
                print(f"[AI打标签] JSON解析成功")
            except json.JSONDecodeError as e:
                print(f"[AI打标签] JSON解析失败: {str(e)}")
                return False, {"error": f"JSON解析失败: {str(e)}", "raw_content": content}
            
            # 验证结果格式
            if not self._validate_tags_response(result_data):
                print(f"[AI打标签] 响应格式验证失败")
                return False, {"error": "响应格式不正确", "data": result_data}
            
            print(f"[AI打标签] 分析完成，生成标签: {result_data.get('tags', [])}")
            print(f"[AI打标签] Token使用: {response.usage.total_tokens}")
            
            # 返回成功结果
            return True, {
                "tags": result_data.get('tags', []),
                "confidence": result_data.get('confidence', 0.8),
                "description": result_data.get('description', ''),
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                "model": self.model,
                "image_path": image_path
            }
            
        except Exception as e:
            print(f"[AI打标签] 分析异常: {str(e)}")
            return False, {"error": f"分析图片时出错: {str(e)}"}

    def _validate_tags_response(self, data: Dict[str, Any]) -> bool:
        """
        验证标签响应格式
        
        Args:
            data: 响应数据
            
        Returns:
            bool: 是否有效
        """
        if not isinstance(data, dict):
            return False
        
        # 检查必需字段
        if 'tags' not in data:
            return False
        
        tags = data['tags']
        if not isinstance(tags, list) or len(tags) == 0:
            return False
        
        # 检查标签格式
        for tag in tags:
            if not isinstance(tag, str) or not tag.strip():
                return False
        
        return True

    def match_existing_tags(self, ai_tags: List[str], existing_tags: Set[str], 
                           similarity_threshold: float = 0.8) -> Dict[str, Any]:
        """
        将AI生成的标签与已存在的标签进行匹配
        
        Args:
            ai_tags: AI生成的标签列表
            existing_tags: 已存在的标签集合
            similarity_threshold: 相似度阈值
            
        Returns:
            Dict: 匹配结果
        """
        print(f"[标签匹配] AI生成标签: {ai_tags}")
        print(f"[标签匹配] 已存在标签数量: {len(existing_tags)}")
        
        matched_tags = []  # 匹配到的已存在标签
        new_tags = []      # 需要创建的新标签
        
        for ai_tag in ai_tags:
            ai_tag = ai_tag.strip()
            if not ai_tag:
                continue
                
            best_match = None
            best_similarity = 0
            
            # 首先检查是否有完全匹配
            if ai_tag in existing_tags:
                matched_tags.append(ai_tag)
                continue
            
            # 进行相似度匹配
            for existing_tag in existing_tags:
                similarity = self._calculate_similarity(ai_tag, existing_tag)
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_match = existing_tag
            
            # 如果相似度足够高，使用已存在的标签
            if best_similarity >= similarity_threshold and best_match:
                matched_tags.append(best_match)
                print(f"[标签匹配] '{ai_tag}' -> '{best_match}' (相似度: {best_similarity:.2f})")
            else:
                new_tags.append(ai_tag)
                print(f"[标签匹配] '{ai_tag}' -> 新标签")
        
        result = {
            "matched_tags": matched_tags,
            "new_tags": new_tags,
            "all_tags": matched_tags + new_tags
        }
        
        print(f"[标签匹配] 匹配到 {len(matched_tags)} 个已存在标签，创建 {len(new_tags)} 个新标签")
        return result

    def _calculate_similarity(self, tag1: str, tag2: str) -> float:
        """
        计算两个标签的相似度
        
        Args:
            tag1: 标签1
            tag2: 标签2
            
        Returns:
            float: 相似度（0-1）
        """
        # 使用多种相似度计算方法
        
        # 方法1：完全匹配
        if tag1 == tag2:
            return 1.0
        
        # 方法2：包含关系
        if tag1 in tag2 or tag2 in tag1:
            return 0.9
        
        # 方法3：序列匹配
        seq_similarity = SequenceMatcher(None, tag1, tag2).ratio()
        
        # 方法4：字符级相似度（针对中文）
        char_similarity = self._calculate_char_similarity(tag1, tag2)
        
        # 取最高相似度
        return max(seq_similarity, char_similarity)

    def _calculate_char_similarity(self, tag1: str, tag2: str) -> float:
        """
        计算字符级相似度（针对中文标签）
        
        Args:
            tag1: 标签1
            tag2: 标签2
            
        Returns:
            float: 字符级相似度
        """
        if not tag1 or not tag2:
            return 0.0
        
        # 计算共同字符数
        chars1 = set(tag1)
        chars2 = set(tag2)
        
        common_chars = chars1.intersection(chars2)
        total_chars = chars1.union(chars2)
        
        if not total_chars:
            return 0.0
        
        return len(common_chars) / len(total_chars)

    def extract_existing_tags_from_records(self, records: List[Dict[str, Any]]) -> Set[str]:
        """
        从记录中提取所有已存在的标签
        
        Args:
            records: 记录列表
            
        Returns:
            Set[str]: 标签集合
        """
        existing_tags = set()
        
        for record in records:
            tags_str = record.get('tags', '').strip()
            if tags_str:
                # 支持多种分隔符
                tag_list = re.split(r'[,，;；\s]+', tags_str)
                for tag in tag_list:
                    tag = tag.strip()
                    if tag:
                        existing_tags.add(tag)
        
        print(f"[标签提取] 从 {len(records)} 条记录中提取到 {len(existing_tags)} 个不重复标签")
        return existing_tags

    def auto_tag_image(self, image_path: str, existing_tags: Set[str] = None, 
                      similarity_threshold: float = 0.8) -> Tuple[bool, Dict[str, Any]]:
        """
        自动为图片打标签（完整流程）
        
        Args:
            image_path: 图片路径
            existing_tags: 已存在的标签集合
            similarity_threshold: 相似度阈值
            
        Returns:
            Tuple[bool, Dict[str, Any]]: (是否成功, 结果数据)
        """
        print(f"[自动打标签] 开始处理图片: {image_path}")
        
        # 第一步：AI分析生成标签
        success, ai_result = self.analyze_image_for_tags(image_path)
        if not success:
            return False, ai_result
        
        ai_tags = ai_result.get('tags', [])
        if not ai_tags:
            return False, {"error": "AI没有生成任何标签"}
        
        # 第二步：标签匹配（如果提供了已存在标签）
        if existing_tags:
            match_result = self.match_existing_tags(ai_tags, existing_tags, similarity_threshold)
            final_tags = match_result['all_tags']
        else:
            match_result = {
                "matched_tags": [],
                "new_tags": ai_tags,
                "all_tags": ai_tags
            }
            final_tags = ai_tags
        
        # 第三步：组装结果
        result = {
            "success": True,
            "tags": final_tags,
            "tags_string": ", ".join(final_tags),  # 便于直接使用的字符串格式
            "ai_analysis": ai_result,
            "matching_result": match_result
        }
        
        print(f"[自动打标签] 完成，最终标签: {result['tags_string']}")
        return True, result

    def test_api_connection(self) -> Tuple[bool, str]:
        """
        测试API连接
        
        Returns:
            Tuple[bool, str]: (是否成功, 状态消息)
        """
        try:
            test_client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
                timeout=10
            )
            
            response = test_client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "Hi"}],
                max_tokens=5,
                temperature=0
            )
            
            if response and response.choices and len(response.choices) > 0:
                return True, f"API连接正常 (模型: {self.model})"
            else:
                return False, "API响应异常：没有收到有效响应"
                
        except Exception as e:
            return False, f"API连接失败: {str(e)}" 