#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据模型定义
"""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class ImageRecord:
    """图片记录数据类"""
    id: Optional[int] = None
    file_path: str = ""
    file_name: str = ""  # 原始文件名
    custom_name: str = ""  # 用户自定义名称
    prompt: str = ""
    negative_prompt: str = ""
    model: str = ""
    sampler: str = ""
    steps: Optional[int] = None
    cfg_scale: Optional[float] = None
    seed: Optional[int] = None
    lora_info: str = ""  # 存储Lora信息的JSON字符串
    notes: str = ""
    tags: str = ""
    generation_source: str = ""  # 生成来源
    workflow_data: str = ""  # 存储ComfyUI工作流数据的JSON字符串
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'id': self.id,
            'file_path': self.file_path,
            'file_name': self.file_name,
            'custom_name': self.custom_name,
            'prompt': self.prompt,
            'negative_prompt': self.negative_prompt,
            'model': self.model,
            'sampler': self.sampler,
            'steps': self.steps,
            'cfg_scale': self.cfg_scale,
            'seed': self.seed,
            'lora_info': self.lora_info,
            'notes': self.notes,
            'tags': self.tags,
            'generation_source': self.generation_source,
            'workflow_data': self.workflow_data,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        """从字典创建对象"""
        # 处理日期时间字段
        created_at = None
        if data.get('created_at'):
            try:
                created_at = datetime.fromisoformat(data['created_at'])
            except:
                pass
        
        updated_at = None
        if data.get('updated_at'):
            try:
                updated_at = datetime.fromisoformat(data['updated_at'])
            except:
                pass
        
        return cls(
            id=data.get('id'),
            file_path=data.get('file_path', ''),
            file_name=data.get('file_name', ''),
            custom_name=data.get('custom_name', ''),
            prompt=data.get('prompt', ''),
            negative_prompt=data.get('negative_prompt', ''),
            model=data.get('model', ''),
            sampler=data.get('sampler', ''),
            steps=data.get('steps'),
            cfg_scale=data.get('cfg_scale'),
            seed=data.get('seed'),
            lora_info=data.get('lora_info', ''),
            notes=data.get('notes', ''),
            tags=data.get('tags', ''),
            generation_source=data.get('generation_source', ''),
            workflow_data=data.get('workflow_data', ''),
            created_at=created_at,
            updated_at=updated_at
        )


@dataclass
class AIGenerationInfo:
    """AI生成信息数据类"""
    prompt: str = ""
    negative_prompt: str = ""
    model: str = ""
    sampler: str = ""
    steps: Optional[int] = None
    cfg_scale: Optional[float] = None
    seed: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    lora_info: dict = None  # 存储Lora信息的字典
    generation_source: str = ""  # 生成来源
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'prompt': self.prompt,
            'negative_prompt': self.negative_prompt,
            'model': self.model,
            'sampler': self.sampler,
            'steps': self.steps,
            'cfg_scale': self.cfg_scale,
            'seed': self.seed,
            'width': self.width,
            'height': self.height,
            'lora_info': self.lora_info,
            'generation_source': self.generation_source
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        """从字典创建对象"""
        return cls(
            prompt=data.get('prompt', ''),
            negative_prompt=data.get('negative_prompt', ''),
            model=data.get('model', ''),
            sampler=data.get('sampler', ''),
            steps=data.get('steps'),
            cfg_scale=data.get('cfg_scale'),
            seed=data.get('seed'),
            width=data.get('width'),
            height=data.get('height'),
            lora_info=data.get('lora_info'),
            generation_source=data.get('generation_source', '')
        ) 