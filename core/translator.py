#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI图片生成提示词翻译器
使用OpenAI GPT-4o进行专业的AI图片生成提示词翻译
"""

import os
import re
import time
from typing import List, Optional, Dict, Tuple
from openai import OpenAI


class AIImagePromptTranslator:
    """AI图片生成提示词专用翻译器"""
    
    def __init__(self, api_key: str = None, model: str = "gpt-4o-mini"):
        """初始化翻译器"""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY") or "sk-CnEoNNdwU8KeJfIoEg6rcNeLeO5XbF3HafEMckZkuZXvKSGS"
        self.model = model
        self.base_url = "https://api.ssopen.top/v1"
        
        if not self.api_key:
            raise ValueError("请设置OpenAI API密钥")
        
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=60
        )
        
        # 预定义的AI绘画术语映射
        self.common_terms = {
            # 质量相关
            "杰作": "masterpiece",
            "最高质量": "best quality",
            "高质量": "high quality",
            "超详细": "ultra detailed",
            "极详细": "extremely detailed",
            "精细": "detailed",
            "高分辨率": "high resolution",
            "4K": "4K",
            "8K": "8K",
            
            # 风格相关
            "真实": "realistic",
            "逼真": "photorealistic",
            "动漫": "anime",
            "卡通": "cartoon",
            "油画": "oil painting",
            "水彩": "watercolor",
            "素描": "sketch",
            "赛博朋克": "cyberpunk",
            
            # 人物相关
            "美丽": "beautiful",
            "可爱": "cute",
            "女孩": "girl",
            "男孩": "boy",
            "女人": "woman",
            "男人": "man",
            "长发": "long hair",
            "短发": "short hair",
            "微笑": "smile",
            
            # 场景相关
            "城市": "city",
            "夜晚": "night",
            "白天": "day",
            "森林": "forest",
            "海洋": "ocean",
            "山": "mountain",
            "天空": "sky",
            "云": "clouds",
            
            # 光照相关
            "柔和光照": "soft lighting",
            "戏剧性光照": "dramatic lighting",
            "自然光": "natural light",
            "暖色调": "warm colors",
            "冷色调": "cool colors"
        }
        
        print(f"AI图片生成提示词翻译器初始化完成 - 模型: {self.model}")
    
    def contains_chinese(self, text: str) -> bool:
        """检查文本是否包含中文"""
        return bool(re.search(r'[\u4e00-\u9fff]', text))
    
    def parse_prompts(self, text: str) -> List[str]:
        """智能解析提示词文本"""
        if not text.strip():
            return []
        
        # 使用逗号、分号、换行符分割
        prompts = []
        for delimiter in [',', '，', ';', '；', '\n']:
            if delimiter in text:
                parts = text.split(delimiter)
                prompts = [p.strip() for p in parts if p.strip()]
                break
        
        # 如果没有分隔符，按空格分割（但保留短语完整性）
        if not prompts:
            # 检查是否是长描述文本
            if len(text) > 100 and ('.' in text or '。' in text):
                prompts = [text.strip()]  # 作为整体处理
            else:
                # 按空格分割，但尝试保持短语完整
                words = text.split()
                prompts = []
                current_phrase = []
                
                for word in words:
                    current_phrase.append(word)
                    # 如果遇到常见的完整词组，结束当前短语
                    phrase = ' '.join(current_phrase)
                    if any(term in phrase.lower() for term in ['best quality', 'high quality', 'ultra detailed']):
                        prompts.append(phrase)
                        current_phrase = []
                
                # 添加剩余的词
                if current_phrase:
                    prompts.append(' '.join(current_phrase))
        
        return [p.strip() for p in prompts if p.strip()]
    
    def get_translation_prompt(self, is_chinese_to_english: bool) -> str:
        """获取翻译提示词"""
        if is_chinese_to_english:
            return """你是专业的AI图片生成提示词翻译专家。请将中文描述翻译成标准的英文AI图片生成提示词。

翻译规则：
1. 使用AI绘画社区的标准英文术语
2. 保持简洁的标签格式，避免完整句子
3. 优先使用通用关键词（如：masterpiece, best quality, detailed等）
4. 人物描述要准确（beautiful girl, long hair, smile等）
5. 场景和风格描述要专业（cyberpunk, realistic, anime style等）
6. 技术术语保持英文（4K, UHD, high resolution等）

示例：
中文：杰作，最高质量，美丽的女孩，长发，微笑，动漫风格
英文：masterpiece, best quality, beautiful girl, long hair, smile, anime style

请直接返回英文翻译，用逗号分隔，不要解释。"""
        else:
            return """你是专业的AI图片生成提示词翻译专家。请将英文AI图片生成提示词翻译成简洁的中文。

翻译规则：
1. 使用最常见的中文词汇
2. 保持标签的简洁性
3. 专业术语准确翻译（masterpiece→杰作，best quality→最高质量）
4. 技术术语可保持英文（4K, HDR等）
5. 用逗号分隔

示例：
英文：masterpiece, best quality, beautiful girl, long hair, smile, anime style
中文：杰作，最高质量，美丽女孩，长发，微笑，动漫风格

请直接返回中文翻译，用逗号分隔，不要解释。"""
    
    def translate_prompts_batch(self, prompts: List[str], to_english: bool = True) -> List[str]:
        """批量翻译提示词"""
        if not prompts:
            return []
        
        # 过滤空值
        filtered_prompts = [p.strip() for p in prompts if p.strip()]
        if not filtered_prompts:
            return []
        
        try:
            # 使用特殊分隔符组合多个提示词
            combined_text = " |SEP| ".join(filtered_prompts)
            
            system_prompt = self.get_translation_prompt(to_english)
            user_prompt = f"请翻译以下用 |SEP| 分隔的提示词：\n{combined_text}\n\n请保持相同的分隔符格式返回结果。"
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.2,  # 低温度确保一致性
                max_tokens=2000
            )
            
            result = response.choices[0].message.content.strip()
            
            # 分解结果
            translated_prompts = [p.strip() for p in result.split("|SEP|")]
            
            # 确保数量匹配
            while len(translated_prompts) < len(filtered_prompts):
                translated_prompts.append(filtered_prompts[len(translated_prompts)])
            
            result_list = translated_prompts[:len(filtered_prompts)]
            
            print(f"[批量翻译] 成功翻译 {len(filtered_prompts)} 个提示词")
            return result_list
            
        except Exception as e:
            print(f"批量翻译失败: {e}")
            # 失败时逐个翻译
            return self._translate_prompts_fallback(filtered_prompts, to_english)
    
    def _translate_prompts_fallback(self, prompts: List[str], to_english: bool = True) -> List[str]:
        """翻译失败时的备用方案"""
        results = []
        system_prompt = self.get_translation_prompt(to_english)
        
        for i, prompt in enumerate(prompts):
            if not prompt.strip():
                results.append("")
                continue
            
            try:
                # 添加延迟避免请求过快
                if i > 0:
                    time.sleep(0.3)
                
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.2,
                    max_tokens=500
                )
                
                result = response.choices[0].message.content.strip()
                results.append(result)
                print(f"[单独翻译] '{prompt}' → '{result}'")
                
            except Exception as e:
                print(f"翻译失败 '{prompt}': {e}")
                results.append(prompt)  # 保持原文
        
        return results
    
    def smart_translate(self, text: str) -> Tuple[List[str], Dict[str, str]]:
        """
        智能翻译：自动检测语言并翻译
        返回: (英文提示词列表, 英文→中文映射字典)
        """
        if not text.strip():
            return [], {}
        
        # 解析提示词
        prompts = self.parse_prompts(text)
        if not prompts:
            return [], {}
        
        # 检测语言
        is_chinese_input = any(self.contains_chinese(prompt) for prompt in prompts)
        
        english_prompts = []
        translation_map = {}
        
        if is_chinese_input:
            # 中文输入，翻译成英文
            print(f"检测到中文输入，开始翻译 {len(prompts)} 个提示词")
            english_prompts = self.translate_prompts_batch(prompts, to_english=True)
            
            # 建立英文→中文映射
            for i in range(min(len(english_prompts), len(prompts))):
                if english_prompts[i] and prompts[i]:
                    translation_map[english_prompts[i]] = prompts[i]
        else:
            # 英文输入，获取中文翻译用于显示
            print(f"检测到英文输入，获取中文翻译用于显示")
            english_prompts = prompts[:]
            chinese_translations = self.translate_prompts_batch(prompts, to_english=False)
            
            # 建立英文→中文映射
            for i in range(min(len(english_prompts), len(chinese_translations))):
                if chinese_translations[i]:
                    translation_map[english_prompts[i]] = chinese_translations[i]
        
        print(f"翻译完成: 英文提示词 {len(english_prompts)} 个，映射关系 {len(translation_map)} 个")
        return english_prompts, translation_map


# 全局翻译器实例
_translator_instance = None

def get_translator() -> AIImagePromptTranslator:
    """获取全局翻译器实例"""
    global _translator_instance
    if _translator_instance is None:
        _translator_instance = AIImagePromptTranslator()
    return _translator_instance

def translate_ai_prompts(text: str) -> Tuple[List[str], Dict[str, str]]:
    """
    翻译AI图片生成提示词的便捷函数
    返回: (英文提示词列表, 英文→中文映射字典)
    """
    translator = get_translator()
    return translator.smart_translate(text) 