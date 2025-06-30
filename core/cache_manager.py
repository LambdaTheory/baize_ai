#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
翻译缓存管理器
- 使用JSON文件持久化存储翻译过的内容
- 提供简单的get/set接口
- 自动处理缓存的加载和保存
"""
import os
import json
import threading
from typing import Dict, Optional

class TranslationCacheManager:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, cache_file: str = 'data/translation_cache.json'):
        if not hasattr(self, '_initialized'):
            with self._lock:
                if not hasattr(self, '_initialized'):
                    self.cache_file = cache_file
                    self.cache = self._load_cache()
                    self._initialized = True
                    print(f"翻译缓存已加载, 共 {len(self.cache)} 条记录")

    def _load_cache(self) -> Dict[str, str]:
        """从文件加载缓存"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"警告: 加载缓存文件失败 {self.cache_file}: {e}")
                return {}
        return {}

    def _save_cache(self):
        """保存缓存到文件"""
        try:
            os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=4)
        except IOError as e:
            print(f"错误: 保存缓存文件失败 {self.cache_file}: {e}")

    def get(self, key: str) -> Optional[str]:
        """从缓存获取值"""
        return self.cache.get(key)

    def set(self, key: str, value: str):
        """设置缓存值并保存"""
        if key and value:
            self.cache[key] = value
            self._save_cache()

# 全局缓存实例
_cache_manager_instance = None

def get_cache_manager() -> TranslationCacheManager:
    """获取全局缓存管理器实例"""
    global _cache_manager_instance
    if _cache_manager_instance is None:
        _cache_manager_instance = TranslationCacheManager()
    return _cache_manager_instance 