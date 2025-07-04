#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据管理模块
负责本地数据库的创建、存储和查询，以及提示词编辑器的历史记录
"""

import sqlite3
import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional


class DataManager:
    """数据管理器"""
    
    def __init__(self, db_path=None, data_dir: str = None):
        # 获取用户主目录下的应用数据目录
        app_data_dir = os.path.expanduser("~/Library/Application Support/白泽AI")
        
        # 数据库相关
        if db_path is None:
            self.db_path = os.path.join(app_data_dir, "database", "records.db")
        else:
            # 如果是相对路径，转换为用户目录下的路径
            if not os.path.isabs(db_path):
                self.db_path = os.path.join(app_data_dir, db_path)
            else:
                self.db_path = db_path
                
        self.ensure_database_exists()
        self.init_database()
        
        # 提示词数据相关
        if data_dir is None:
            self.data_dir = os.path.join(app_data_dir, "data")
        else:
            # 如果是相对路径，转换为用户目录下的路径
            if not os.path.isabs(data_dir):
                self.data_dir = os.path.join(app_data_dir, data_dir)
            else:
                self.data_dir = data_dir
                
        self.prompt_data_file = os.path.join(self.data_dir, "prompt_history.json")
        self.ensure_data_dir()
    
    def ensure_database_exists(self):
        """确保数据库目录存在"""
        db_dir = os.path.dirname(self.db_path)
        if not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
    
    def ensure_data_dir(self):
        """确保数据目录存在"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir, exist_ok=True)
    
    def init_database(self):
        """初始化数据库表"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 创建记录表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS image_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_path TEXT NOT NULL,
                    file_name TEXT NOT NULL,
                    custom_name TEXT,
                    prompt TEXT,
                    negative_prompt TEXT,
                    model TEXT,
                    sampler TEXT,
                    steps INTEGER,
                    cfg_scale REAL,
                    seed INTEGER,
                    lora_info TEXT,
                    notes TEXT,
                    tags TEXT,
                    generation_source TEXT,
                    workflow_data TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            
            # 检查是否需要添加新字段（数据库迁移）
            cursor.execute("PRAGMA table_info(image_records)")
            columns = [column[1] for column in cursor.fetchall()]
            if 'lora_info' not in columns:
                cursor.execute("ALTER TABLE image_records ADD COLUMN lora_info TEXT")
            if 'custom_name' not in columns:
                cursor.execute("ALTER TABLE image_records ADD COLUMN custom_name TEXT")
            if 'generation_source' not in columns:
                cursor.execute("ALTER TABLE image_records ADD COLUMN generation_source TEXT")
            if 'workflow_data' not in columns:
                cursor.execute("ALTER TABLE image_records ADD COLUMN workflow_data TEXT")
            
            # 创建索引
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_file_path ON image_records(file_path)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_created_at ON image_records(created_at)")
            
            conn.commit()
    
    # ===================== 图片记录数据库功能 =====================
    
    def save_record(self, record_data: Dict) -> int:
        """
        保存记录
        
        Args:
            record_data: 记录数据字典
        
        Returns:
            int: 新记录的ID
        """
        file_path = record_data.get('file_path', '')
        file_name = os.path.basename(file_path)
        current_time = datetime.now().isoformat()
        
        # 检查是否已存在相同文件路径的记录
        existing_id = self.get_record_id_by_path(file_path)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            if existing_id:
                # 更新现有记录
                cursor.execute("""
                    UPDATE image_records SET
                        file_name = ?,
                        custom_name = ?,
                        prompt = ?,
                        negative_prompt = ?,
                        model = ?,
                        sampler = ?,
                        steps = ?,
                        cfg_scale = ?,
                        seed = ?,
                        lora_info = ?,
                        notes = ?,
                        tags = ?,
                        generation_source = ?,
                        workflow_data = ?,
                        updated_at = ?
                    WHERE id = ?
                """, (
                    file_name,
                    record_data.get('custom_name', ''),
                    record_data.get('prompt', ''),
                    record_data.get('negative_prompt', ''),
                    record_data.get('model', ''),
                    record_data.get('sampler', ''),
                    self._safe_int(record_data.get('steps')),
                    self._safe_float(record_data.get('cfg_scale')),
                    self._safe_int(record_data.get('seed')),
                    self._serialize_lora_info(record_data.get('lora_info')),
                    record_data.get('notes', ''),
                    record_data.get('tags', ''),
                    record_data.get('generation_source', ''),
                    self._serialize_workflow_data(record_data.get('workflow_data')),
                    current_time,
                    existing_id
                ))
                return existing_id
            else:
                # 插入新记录
                cursor.execute("""
                    INSERT INTO image_records (
                        file_path, file_name, custom_name, prompt, negative_prompt, model,
                        sampler, steps, cfg_scale, seed, lora_info, notes, tags, generation_source, workflow_data, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    file_path,
                    file_name,
                    record_data.get('custom_name', ''),
                    record_data.get('prompt', ''),
                    record_data.get('negative_prompt', ''),
                    record_data.get('model', ''),
                    record_data.get('sampler', ''),
                    self._safe_int(record_data.get('steps')),
                    self._safe_float(record_data.get('cfg_scale')),
                    self._safe_int(record_data.get('seed')),
                    self._serialize_lora_info(record_data.get('lora_info')),
                    record_data.get('notes', ''),
                    record_data.get('tags', ''),
                    record_data.get('generation_source', ''),
                    self._serialize_workflow_data(record_data.get('workflow_data')),
                    current_time,
                    current_time
                ))
                
                return cursor.lastrowid
    
    def get_record_by_path(self, file_path: str) -> Optional[Dict]:
        """根据文件路径获取记录"""
        record_id = self.get_record_id_by_path(file_path)
        if record_id:
            return self.get_record_by_id(record_id)
        return None
    
    def get_record_id_by_path(self, file_path: str) -> Optional[int]:
        """根据文件路径获取记录ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM image_records WHERE file_path = ?", (file_path,))
            result = cursor.fetchone()
            return result[0] if result else None
    
    def get_all_records(self) -> List[Dict]:
        """获取所有记录"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM image_records 
                ORDER BY created_at DESC
            """)
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def get_record_by_id(self, record_id: int) -> Optional[Dict]:
        """根据ID获取记录"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM image_records WHERE id = ?", (record_id,))
            row = cursor.fetchone()
            
            return dict(row) if row else None
    
    def delete_record(self, record_id: int) -> bool:
        """删除记录"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM image_records WHERE id = ?", (record_id,))
            return cursor.rowcount > 0
    
    def update_record_file_path(self, record_id: int, new_file_path: str) -> bool:
        """更新记录的文件路径"""
        try:
            current_time = datetime.now().isoformat()
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE image_records SET
                        file_path = ?,
                        file_name = ?,
                        updated_at = ?
                    WHERE id = ?
                """, (
                    new_file_path,
                    os.path.basename(new_file_path),
                    current_time,
                    record_id
                ))
                
                return cursor.rowcount > 0
        except Exception as e:
            print(f"更新记录文件路径时出错: {e}")
            return False
    
    def search_records(self, keyword: str) -> List[Dict]:
        """搜索记录"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # 在多个字段中搜索
            cursor.execute("""
                SELECT * FROM image_records 
                WHERE file_name LIKE ? 
                   OR prompt LIKE ? 
                   OR negative_prompt LIKE ?
                   OR model LIKE ?
                   OR notes LIKE ?
                ORDER BY created_at DESC
            """, (f'%{keyword}%',) * 5)
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def export_to_json(self, file_path: str) -> bool:
        """导出数据为JSON格式"""
        try:
            records = self.get_all_records()
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(records, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"导出JSON失败: {e}")
            return False
    
    def export_to_csv(self, file_path: str) -> bool:
        """导出数据为CSV格式"""
        try:
            import csv
            
            records = self.get_all_records()
            if not records:
                return False
            
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=records[0].keys())
                writer.writeheader()
                writer.writerows(records)
            
            return True
        except Exception as e:
            print(f"导出CSV失败: {e}")
            return False
    
    def _safe_int(self, value) -> Optional[int]:
        """安全转换为整数"""
        if value is None or value == '':
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            return None
             
    def _safe_float(self, value) -> Optional[float]:
        """安全转换为浮点数"""
        if value is None or value == '':
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
         
    def _serialize_lora_info(self, lora_info) -> str:
        """序列化Lora信息为JSON字符串"""
        if not lora_info:
            return ""
        try:
            return json.dumps(lora_info, ensure_ascii=False)
        except (TypeError, ValueError):
            return ""
    
    def _deserialize_lora_info(self, lora_info_str: str) -> Optional[dict]:
        """反序列化Lora信息从JSON字符串"""
        if not lora_info_str:
            return None
        try:
            return json.loads(lora_info_str)
        except (json.JSONDecodeError, TypeError):
            return None
    
    def _serialize_workflow_data(self, workflow_data) -> str:
        """序列化工作流数据为JSON字符串"""
        if not workflow_data:
            return ""
        try:
            return json.dumps(workflow_data, ensure_ascii=False)
        except (TypeError, ValueError):
            return ""
    
    def _deserialize_workflow_data(self, workflow_data_str: str) -> Optional[dict]:
        """反序列化工作流数据"""
        if not workflow_data_str:
            return None
        try:
            return json.loads(workflow_data_str)
        except (json.JSONDecodeError, TypeError):
            return None
    
    # ===================== 提示词历史记录功能 =====================
    
    def save_prompt_data(self, prompt_data: Dict[str, Any]) -> bool:
        """
        保存提示词数据
        
        Args:
            prompt_data: 提示词数据字典，格式如下：
            {
                "scenes": [
                    {
                        "title": "场景名称",
                        "english_prompts": ["prompt1", "prompt2"],
                        "chinese_prompts": ["提示词1", "提示词2"]
                    }
                ],
                "last_updated": "2024-01-01 12:00:00"
            }
        """
        try:
            # 添加时间戳
            prompt_data["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # 保存到文件
            with open(self.prompt_data_file, 'w', encoding='utf-8') as f:
                json.dump(prompt_data, f, ensure_ascii=False, indent=2)
            
            print(f"提示词数据已保存到: {self.prompt_data_file}")
            return True
            
        except Exception as e:
            print(f"保存提示词数据失败: {e}")
            return False
    
    def load_prompt_data(self) -> Optional[Dict[str, Any]]:
        """
        加载提示词数据
        
        Returns:
            提示词数据字典，如果文件不存在或加载失败则返回None
        """
        try:
            if not os.path.exists(self.prompt_data_file):
                print("提示词历史文件不存在，将创建新的记录")
                return None
            
            with open(self.prompt_data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            print(f"成功加载提示词数据，最后更新时间: {data.get('last_updated', '未知')}")
            return data
            
        except Exception as e:
            print(f"加载提示词数据失败: {e}")
            return None
    
    def get_default_prompt_data(self) -> Dict[str, Any]:
        """
        获取默认的提示词数据
        """
        return {
            "scenes": [
                {
                    "title": "通用提示词",
                    "english_prompts": [
                        "masterpiece",
                        "best quality",
                        "ultra detailed",
                        "beautiful girl",
                        "elegant dress"
                    ],
                    "chinese_prompts": [
                        "杰作",
                        "最高质量", 
                        "超详细",
                        "美丽女孩",
                        "优雅裙子"
                    ]
                }
            ],
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def backup_prompt_data(self) -> bool:
        """
        备份提示词数据
        """
        try:
            if not os.path.exists(self.prompt_data_file):
                return True
            
            # 创建备份文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(self.data_dir, f"prompt_history_backup_{timestamp}.json")
            
            # 复制文件
            import shutil
            shutil.copy2(self.prompt_data_file, backup_file)
            
            print(f"数据已备份到: {backup_file}")
            return True
            
        except Exception as e:
            print(f"备份数据失败: {e}")
            return False
    
    def export_prompt_data(self, export_path: str) -> bool:
        """
        导出提示词数据到指定路径
        """
        try:
            data = self.load_prompt_data()
            if not data:
                return False
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print(f"数据已导出到: {export_path}")
            return True
            
        except Exception as e:
            print(f"导出数据失败: {e}")
            return False
    
    def import_prompt_data(self, import_path: str) -> Optional[Dict[str, Any]]:
        """
        从指定路径导入提示词数据
        """
        try:
            if not os.path.exists(import_path):
                print(f"导入文件不存在: {import_path}")
                return None
                
            with open(import_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 验证数据格式
            if not isinstance(data.get('scenes'), list):
                print("导入数据格式错误: scenes字段不是列表")
                return None
            
            print(f"成功导入数据，包含 {len(data['scenes'])} 个场景")
            return data
            
        except Exception as e:
            print(f"导入数据失败: {e}")
            return None
    
    def clear_all_records(self) -> bool:
        """清空所有记录"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM image_records")
                return cursor.rowcount >= 0  # 即使没有记录也返回True
        except Exception as e:
            print(f"清空所有记录时出错: {e}")
            return False
    
    def update_record_path(self, record_id: int, new_file_path: str) -> bool:
        """更新记录的文件路径（别名方法）"""
        return self.update_record_file_path(record_id, new_file_path)
    
    def get_all_unique_tags(self) -> set:
        """获取所有唯一标签"""
        try:
            import re
            all_tags = set()
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT tags FROM image_records WHERE tags IS NOT NULL AND tags != ''")
                
                for (tags_str,) in cursor.fetchall():
                    if tags_str and tags_str.strip():
                        # 支持多种分隔符分割标签
                        tag_list = re.split(r'[,，;；\s]+', tags_str.strip())
                        for tag in tag_list:
                            tag = tag.strip()
                            if tag:
                                all_tags.add(tag)
            
            print(f"从数据库中提取到 {len(all_tags)} 个不重复标签")
            return all_tags
        except Exception as e:
            print(f"获取标签失败: {e}")
            return set()