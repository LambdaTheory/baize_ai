#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
翻译器模块
使用百度翻译API进行文本翻译
"""

import hashlib
import random
import time
import requests
import json
from typing import List, Optional


class BaiduTranslator:
    """百度翻译器"""
    
    def __init__(self, app_id: str = None, secret_key: str = None):
        # 如果没有提供API密钥，使用免费的在线翻译接口（有限制）
        self.app_id = app_id
        self.secret_key = secret_key
        self.use_free_api = not (app_id and secret_key)
        
        if self.use_free_api:
            print("使用免费翻译接口（有频率限制）")
        else:
            print("使用百度翻译API")
    
    def translate_text(self, text: str, from_lang: str = 'en', to_lang: str = 'zh') -> Optional[str]:
        """翻译文本"""
        if not text.strip():
            return ""
            
        try:
            if self.use_free_api:
                return self._translate_free(text, from_lang, to_lang)
            else:
                return self._translate_baidu_api(text, from_lang, to_lang)
        except Exception as e:
            print(f"翻译失败: {e}")
            return None
    
    def translate_prompts(self, prompts: List[str], from_lang: str = 'en', to_lang: str = 'zh') -> List[str]:
        """翻译提示词列表"""
        translated = []
        
        for prompt in prompts:
            prompt = prompt.strip()
            if not prompt:
                translated.append("")
                continue
                
            # 为了避免API频率限制，添加小延迟
            if len(translated) > 0:
                time.sleep(0.1)
                
            result = self.translate_text(prompt, from_lang, to_lang)
            if result:
                translated.append(result)
            else:
                # 翻译失败时保持原文
                translated.append(prompt)
                
        return translated
    
    def _translate_free(self, text: str, from_lang: str, to_lang: str) -> Optional[str]:
        """使用免费翻译接口"""
        try:
            # 使用一个简单的免费翻译接口
            url = "https://translate.googleapis.com/translate_a/single"
            params = {
                'client': 'gtx',
                'sl': from_lang,
                'tl': to_lang,
                'dt': 't',
                'q': text
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if result and len(result) > 0 and len(result[0]) > 0:
                    return result[0][0][0]
            
            return None
            
        except Exception as e:
            print(f"免费翻译接口调用失败: {e}")
            # 如果免费接口失败，使用本地词典作为备用
            return self._translate_local_dict(text)
    
    def _translate_baidu_api(self, text: str, from_lang: str, to_lang: str) -> Optional[str]:
        """使用百度翻译API"""
        try:
            salt = str(random.randint(32768, 65536))
            sign_str = f"{self.app_id}{text}{salt}{self.secret_key}"
            sign = hashlib.md5(sign_str.encode('utf-8')).hexdigest()
            
            url = "https://fanyi-api.baidu.com/api/trans/vip/translate"
            params = {
                'q': text,
                'from': from_lang,
                'to': to_lang,
                'appid': self.app_id,
                'salt': salt,
                'sign': sign
            }
            
            response = requests.get(url, params=params, timeout=10)
            result = response.json()
            
            if 'trans_result' in result and len(result['trans_result']) > 0:
                return result['trans_result'][0]['dst']
            else:
                print(f"百度翻译API返回错误: {result}")
                return None
                
        except Exception as e:
            print(f"百度翻译API调用失败: {e}")
            return None
    
    def _translate_local_dict(self, text: str) -> str:
        """本地词典翻译（备用）"""
        # 常见的AI绘画提示词翻译词典（英文到中文）
        en_to_zh_translations = {
            'masterpiece': '杰作',
            'best quality': '最高质量',
            'ultra detailed': '超详细',
            'detailed': '详细',
            'high quality': '高质量',
            'beautiful': '美丽',
            'girl': '女孩',
            'boy': '男孩',
            'woman': '女人',
            'man': '男人',
            'face': '脸',
            'eyes': '眼睛',
            'hair': '头发',
            'long hair': '长发',
            'short hair': '短发',
            'dress': '裙子',
            'clothing': '衣服',
            'elegant': '优雅',
            'cute': '可爱',
            'pretty': '漂亮',
            'smile': '微笑',
            'portrait': '肖像',
            'landscape': '风景',
            'background': '背景',
            'lighting': '光线',
            'soft lighting': '柔和光线',
            'natural lighting': '自然光线',
            'sunset': '日落',
            'sunrise': '日出',
            'night': '夜晚',
            'day': '白天',
            'outdoors': '户外',
            'indoors': '室内',
            'nature': '自然',
            'forest': '森林',
            'beach': '海滩',
            'mountain': '山',
            'sky': '天空',
            'cloud': '云',
            'flower': '花',
            'tree': '树',
            'anime': '动漫',
            'realistic': '写实',
            'digital art': '数字艺术',
            'painting': '绘画',
            'illustration': '插画',
            'concept art': '概念艺术',
            'fantasy': '幻想',
            'sci-fi': '科幻',
            'futuristic': '未来主义',
            'retro': '复古',
            'vintage': 'vintage',
            'modern': '现代',
            'traditional': '传统',
            'japanese': '日式',
            'chinese': '中式',
            'western': '西式',
            'colorful': '多彩',
            'monochrome': '单色',
            'black and white': '黑白',
            'vibrant': '鲜艳',
            'pastel': '粉彩',
            'dark': '黑暗',
            'bright': '明亮',
            'warm': '温暖',
            'cool': '冷色',
            'artistic': '艺术性',
            'creative': '创意',
            'unique': '独特',
            'amazing': '惊人',
            'stunning': '令人惊叹',
            'gorgeous': '华丽',
            'perfect': '完美',
            'excellent': '优秀',
            'professional': '专业',
            'studio': '工作室',
            'photography': '摄影',
            'render': '渲染',
            '3d': '3D',
            '2d': '2D',
            'texture': '纹理',
            'material': '材质',
            'shading': '阴影',
            'reflection': '反射',
            'transparent': '透明',
            'glossy': '光泽',
            'matte': '哑光',
            'metallic': '金属',
            'wooden': '木质',
            'fabric': '布料',
            'leather': '皮革',
            'glass': '玻璃',
            'crystal': '水晶',
            'jewelry': '珠宝',
            'accessories': '配饰',
            'weapon': '武器',
            'armor': '盔甲',
            'magic': '魔法',
            'spell': '法术',
            'dragon': '龙',
            'fairy': '仙女',
            'angel': '天使',
            'demon': '恶魔',
            'castle': '城堡',
            'palace': '宫殿',
            'temple': '神庙',
            'church': '教堂',
            'city': '城市',
            'village': '村庄',
            'room': '房间',
            'bedroom': '卧室',
            'kitchen': '厨房',
            'garden': '花园',
            'park': '公园',
            'street': '街道',
            'bridge': '桥',
            'river': '河流',
            'lake': '湖',
            'ocean': '海洋',
            'island': '岛屿',
            'desert': '沙漠',
            'snow': '雪',
            'rain': '雨',
            'storm': '暴风雨',
            'rainbow': '彩虹',
            'star': '星星',
            'moon': '月亮',
            'sun': '太阳',
            'planet': '行星',
            'space': '太空',
            'galaxy': '银河',
            'universe': '宇宙'
        }
        
        # 创建中文到英文的反向词典
        zh_to_en_translations = {v: k for k, v in en_to_zh_translations.items()}
        
        # 根据文本内容判断是中译英还是英译中
        if self._is_chinese_text(text):
            # 中译英
            # 首先尝试完全匹配
            if text in zh_to_en_translations:
                return zh_to_en_translations[text]
            
            # 如果没有完全匹配，尝试部分匹配
            for zh, en in zh_to_en_translations.items():
                if zh in text:
                    return text.replace(zh, en)
            
            # 如果都没有匹配，返回原文并标记
            return f"{text}(untranslated)"
        else:
            # 英译中
            # 首先尝试完全匹配
            text_lower = text.lower()
            if text_lower in en_to_zh_translations:
                return en_to_zh_translations[text_lower]
            
            # 如果没有完全匹配，尝试部分匹配
            for en, zh in en_to_zh_translations.items():
                if en in text_lower:
                    return text.replace(en, zh)
            
            # 如果都没有匹配，返回原文并标记
            return f"{text}(未翻译)"
    
    def _is_chinese_text(self, text: str) -> bool:
        """判断文本是否主要包含中文字符"""
        chinese_char_count = 0
        total_char_count = len(text.strip())
        
        if total_char_count == 0:
            return False
            
        for char in text:
            if '\u4e00' <= char <= '\u9fff':  # 中文字符范围
                chinese_char_count += 1
        
        # 如果中文字符超过50%，认为是中文文本
        return chinese_char_count / total_char_count > 0.5


# 创建全局翻译器实例
translator = BaiduTranslator()


def translate_prompts(prompts: List[str], from_lang: str = 'en', to_lang: str = 'zh') -> List[str]:
    """翻译提示词列表的便捷函数"""
    return translator.translate_prompts(prompts, from_lang, to_lang)


def translate_text(text: str, from_lang: str = 'en', to_lang: str = 'zh') -> Optional[str]:
    """翻译文本的便捷函数"""
    return translator.translate_text(text, from_lang, to_lang) 