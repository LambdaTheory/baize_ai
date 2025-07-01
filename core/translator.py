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
from openai import OpenAI, APIConnectionError
from core.cache_manager import get_cache_manager

PROMPT_SEPARATOR = "[/-_PROMPT_SEPARATOR_-/]"

class AIImagePromptTranslator:
    """AI图片生成提示词专用翻译器"""
    
    def __init__(self, api_key: str = None, model: str = "gpt-4o-mini"):
        """初始化翻译器和缓存"""
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
        
        self.cache_manager = get_cache_manager()
        
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
            return f"""你是专业的AI图片生成提示词翻译专家。请将中文描述翻译成标准的英文AI图片生成提示词。

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

请直接返回英文翻译，并使用 `{PROMPT_SEPARATOR}` 分隔，不要解释。"""
        else:
            return f"""你是专业的AI图片生成提示词翻译专家。请将英文AI图片生成提示词翻译成简洁的中文。

翻译规则：
1. 使用最常见的中文词汇
2. 保持标签的简洁性
3. 专业术语准确翻译（masterpiece→杰作，best quality→最高质量）
4. 技术术语可保持英文（4K, HDR等）
5. 使用 `{PROMPT_SEPARATOR}` 分隔

示例：
英文：masterpiece, best quality, beautiful girl, long hair, smile, anime style
中文：杰作，最高质量，美丽女孩，长发，微笑，动漫风格

请直接返回中文翻译，并使用 `{PROMPT_SEPARATOR}` 分隔，不要解释。"""
    
    def translate_prompts_batch(self, prompts: List[str], to_english: bool = True) -> List[str]:
        """
        批量翻译提示词，并集成缓存机制。
        如果批量失败，则自动降级为逐个翻译。
        """
        if not prompts:
            return []
        
        filtered_prompts = [p.strip() for p in prompts if p.strip()]
        if not filtered_prompts:
            return []

        # 缓存键的前缀，区分翻译方向
        cache_prefix = "en_to_zh" if not to_english else "zh_to_en"
        
        # 1. 查找缓存
        results = {}
        prompts_to_translate = []
        for i, prompt in enumerate(filtered_prompts):
            cache_key = f"{cache_prefix}:{prompt}"
            cached_result = self.cache_manager.get(cache_key)
            if cached_result:
                results[i] = cached_result
            else:
                prompts_to_translate.append((i, prompt))
        
        print(f"缓存命中: {len(results)}/{len(filtered_prompts)}")

        # 2. 对未缓存的内容进行API调用
        if prompts_to_translate:
            original_indices = [item[0] for item in prompts_to_translate]
            prompts_for_api = [item[1] for item in prompts_to_translate]
            
            batch_failed = False
            max_retries = 3
            last_exception = None

            for attempt in range(max_retries):
                try:
                    print(f"调用API批量翻译 (第 {attempt + 1}/{max_retries} 次)...")
                    combined_text = f" {PROMPT_SEPARATOR} ".join(prompts_for_api)
                    system_prompt = self.get_translation_prompt(to_english)
                    user_prompt = f"请翻译以下用 `{PROMPT_SEPARATOR}` 分隔的提示词：\n{combined_text}\n\n请保持相同的分隔符格式返回结果。"
                    
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        temperature=0.2, max_tokens=2000
                    )
                    
                    api_results_raw = response.choices[0].message.content.strip()
                    api_results = [p.strip().strip('`') for p in api_results_raw.split(PROMPT_SEPARATOR)]

                    if len(api_results) != len(prompts_for_api):
                        raise ValueError(f"翻译结果数量({len(api_results)})与输入({len(prompts_for_api)})不匹配")
                    
                    # 3. 更新缓存和结果
                    for i, translated_prompt in enumerate(api_results):
                        original_index = original_indices[i]
                        original_prompt = prompts_for_api[i]
                        
                        results[original_index] = translated_prompt
                        cache_key = f"{cache_prefix}:{original_prompt}"
                        self.cache_manager.set(cache_key, translated_prompt)
                    
                    last_exception = None
                    break

                except (APIConnectionError, ValueError) as e:
                    last_exception = e
                    print(f"批量翻译失败 (第 {attempt + 1} 次): {e}")
                    if attempt < max_retries - 1:
                        time.sleep(1)
                    else:
                        print("批量翻译达到最大重试次数。")
                        batch_failed = True
                
                except Exception as e:
                    last_exception = e
                    print(f"批量翻译遇到未知错误 (第 {attempt + 1} 次): {e}")
                    if attempt < max_retries - 1:
                        time.sleep(1)
                    else:
                        print("批量翻译达到最大重试次数。")
                        batch_failed = True

            if batch_failed:
                print("批量翻译失败，降级为逐个翻译...")
                fallback_results = self._translate_prompts_fallback(prompts_for_api, to_english)
                for i, translated_prompt in enumerate(fallback_results):
                    original_index = original_indices[i]
                    original_prompt = prompts_for_api[i]
                    
                    results[original_index] = translated_prompt
                    # 只有成功翻译的才缓存
                    if translated_prompt != original_prompt:
                         cache_key = f"{cache_prefix}:{original_prompt}"
                         self.cache_manager.set(cache_key, translated_prompt)

        # 4. 按原始顺序组装最终结果
        final_results = [results[i] for i in range(len(filtered_prompts))]
        return final_results
    
    def _translate_prompts_fallback(self, prompts: List[str], to_english: bool = True) -> List[str]:
        """翻译失败时的备用方案，带重试机制"""
        results = []
        system_prompt = self.get_translation_prompt(to_english).replace(PROMPT_SEPARATOR, "") # 单个翻译不需要分隔符
        
        for i, prompt in enumerate(prompts):
            if not prompt.strip():
                results.append("")
                continue
            
            max_retries = 3
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    if i > 0 and attempt == 0: # 仅在第一次尝试时延迟
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
                    
                    result = response.choices[0].message.content.strip().strip('`')
                    results.append(result)
                    print(f"[单独翻译成功] '{prompt}' → '{result}'")
                    last_exception = None
                    break
                    
                except Exception as e:
                    last_exception = e
                    print(f"单独翻译 '{prompt}' 失败 (第 {attempt + 1} 次): {e}")
                    if attempt < max_retries - 1:
                        time.sleep(1)

            if last_exception:
                print(f"单独翻译 '{prompt}' 达到最大重试次数，保持原文。")
                results.append(prompt)
        
        return results
    
    def smart_translate(self, text: str) -> Tuple[List[str], Dict[str, str]]:
        """
        智能翻译：自动检测语言并翻译。始终返回与输入提示词对应的完整英文列表和翻译映射。
        """
        if not text.strip():
            return [], {}
        
        prompts = self.parse_prompts(text)
        if not prompts:
            return [], {}

        # 检查原始输入中是否存在中文和英文
        is_chinese_present = any(self.contains_chinese(p) for p in prompts)
        is_english_present = any(not self.contains_chinese(p) for p in prompts)

        # 1. 统一翻译成英文（第一步API调用）
        #    - 这一步确保我们有一个与用户输入语序一致的全英文基线
        #    - "你好" -> "hello", "world" -> "world"
        english_prompts = self.translate_prompts_batch(prompts, to_english=True)
        translation_map = {}

        # 2. 如果原始输入包含英文，为它们获取中文翻译（第二步API调用）
        if is_english_present:
            original_english_prompts = [p for p in prompts if not self.contains_chinese(p) and p.strip()]
            if original_english_prompts:
                chinese_for_english = self.translate_prompts_batch(original_english_prompts, to_english=False)
                english_to_chinese_map = {eng: chn for eng, chn in zip(original_english_prompts, chinese_for_english)}
            else:
                english_to_chinese_map = {}
        
        # 3. 构建最终的完整映射
        for i, original_prompt in enumerate(prompts):
            final_english_prompt = english_prompts[i]
            
            if self.contains_chinese(original_prompt):
                # 如果原始词是中文: 最终英文 -> 原始中文
                translation_map[final_english_prompt] = original_prompt
            else:
                # 如果原始词是英文: 最终英文 -> 查表得到的中文
                # 使用 final_english_prompt 作为 key, 因为它可能被 GPT 轻微修正过
                # 使用 original_prompt 去查找它的中文翻译
                translation_map[final_english_prompt] = english_to_chinese_map.get(original_prompt, "")

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