#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量处理模块
支持批量导入、处理和导出图片信息
"""

import os
import time
import json
import csv
from typing import List, Dict, Any, Optional, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from datetime import datetime

from .image_reader import ImageInfoReader
from .data_manager import DataManager
from .html_exporter import HTMLExporter


class BatchProcessor:
    """批量处理器"""
    
    def __init__(self, data_manager: DataManager = None):
        self.image_reader = ImageInfoReader()
        self.data_manager = data_manager or DataManager()
        self.html_exporter = HTMLExporter()
        
        # 支持的图片格式
        self.supported_formats = {'.png', '.jpg', '.jpeg', '.webp'}
        
        # 处理状态
        self.is_processing = False
        self.current_progress = 0
        self.total_files = 0
        self.processed_files = 0
        self.failed_files = []
        self.successful_files = []
        
    def scan_folder(self, folder_path: str, recursive: bool = True) -> List[str]:
        """
        扫描文件夹中的图片文件
        
        Args:
            folder_path: 文件夹路径
            recursive: 是否递归扫描子文件夹
            
        Returns:
            List[str]: 图片文件路径列表
        """
        image_files = []
        folder_path = Path(folder_path)
        
        if not folder_path.exists() or not folder_path.is_dir():
            return image_files
        
        try:
            if recursive:
                # 递归扫描所有子文件夹
                for file_path in folder_path.rglob("*"):
                    if file_path.is_file() and file_path.suffix.lower() in self.supported_formats:
                        image_files.append(str(file_path))
            else:
                # 只扫描当前文件夹
                for file_path in folder_path.iterdir():
                    if file_path.is_file() and file_path.suffix.lower() in self.supported_formats:
                        image_files.append(str(file_path))
                        
        except PermissionError as e:
            print(f"无权限访问文件夹: {folder_path}, 错误: {e}")
        except Exception as e:
            print(f"扫描文件夹时出错: {e}")
            
        return sorted(image_files)
    
    def batch_process_images(self, 
                           image_files: List[str], 
                           progress_callback: Callable[[int, int, str], None] = None,
                           auto_save: bool = True,
                           max_workers: int = 4) -> Dict[str, Any]:
        """
        批量处理图片
        
        Args:
            image_files: 图片文件路径列表
            progress_callback: 进度回调函数 (processed, total, current_file)
            auto_save: 是否自动保存到数据库
            max_workers: 最大并发数
            
        Returns:
            Dict: 处理结果统计
        """
        self.is_processing = True
        self.total_files = len(image_files)
        self.processed_files = 0
        self.failed_files = []
        self.successful_files = []
        
        start_time = time.time()
        processed_data = []
        
        try:
            # 使用线程池进行并发处理
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # 提交任务
                future_to_file = {
                    executor.submit(self._process_single_image, file_path): file_path 
                    for file_path in image_files
                }
                
                # 处理完成的任务
                for future in as_completed(future_to_file):
                    file_path = future_to_file[future]
                    
                    try:
                        result = future.result()
                        if result:
                            self.successful_files.append(file_path)
                            processed_data.append({
                                'file_path': file_path,
                                'data': result
                            })
                            
                            # 自动保存到数据库
                            if auto_save:
                                try:
                                    self.data_manager.save_record(result)
                                except Exception as e:
                                    print(f"保存记录失败 {file_path}: {e}")
                        else:
                            self.failed_files.append(file_path)
                            
                    except Exception as e:
                        print(f"处理文件失败 {file_path}: {e}")
                        self.failed_files.append(file_path)
                    
                    # 更新进度
                    self.processed_files += 1
                    if progress_callback:
                        progress_callback(self.processed_files, self.total_files, file_path)
                        
        except Exception as e:
            print(f"批量处理时出错: {e}")
        
        finally:
            self.is_processing = False
            
        # 计算处理时间
        end_time = time.time()
        processing_time = end_time - start_time
        
        # 返回处理结果
        return {
            'total_files': self.total_files,
            'successful_count': len(self.successful_files),
            'failed_count': len(self.failed_files),
            'successful_files': self.successful_files,
            'failed_files': self.failed_files,
            'processed_data': processed_data,
            'processing_time': processing_time
        }
    
    def _process_single_image(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        处理单个图片文件
        
        Args:
            file_path: 图片文件路径
            
        Returns:
            Dict: 提取的信息，如果失败返回None
        """
        try:
            # 提取图片信息
            image_info = self.image_reader.extract_info(file_path)
            
            if image_info:
                # 添加文件信息
                image_info['file_path'] = file_path
                image_info['file_name'] = os.path.basename(file_path)
                
                # 如果没有提取到信息，创建基础记录
                if not any(image_info.get(key) for key in ['prompt', 'model', 'sampler']):
                    image_info = {
                        'file_path': file_path,
                        'file_name': os.path.basename(file_path),
                        'prompt': '',
                        'negative_prompt': '',
                        'model': '',
                        'sampler': '',
                        'steps': '',
                        'cfg_scale': '',
                        'seed': '',
                        'notes': '批量导入 - 未检测到AI生成信息',
                        'tags': 'batch_import',
                        'generation_source': 'Unknown'
                    }
                
                return image_info
            else:
                # 创建基础记录（即使没有AI信息）
                return {
                    'file_path': file_path,
                    'file_name': os.path.basename(file_path),
                    'prompt': '',
                    'negative_prompt': '',
                    'model': '',
                    'sampler': '',
                    'steps': '',
                    'cfg_scale': '',
                    'seed': '',
                    'notes': '批量导入 - 未检测到AI生成信息',
                    'tags': 'batch_import',
                    'generation_source': 'Unknown'
                }
                
        except Exception as e:
            print(f"处理单个图片失败 {file_path}: {e}")
            return None
    
    def batch_export_html(self, 
                         records: List[Dict[str, Any]], 
                         output_dir: str,
                         progress_callback: Callable[[int, int, str], None] = None,
                         include_images: bool = True) -> Dict[str, Any]:
        """
        批量导出HTML文件
        
        Args:
            records: 记录列表
            output_dir: 输出目录
            progress_callback: 进度回调函数
            include_images: 是否包含图片
            
        Returns:
            Dict: 导出结果统计
        """
        os.makedirs(output_dir, exist_ok=True)
        
        successful_exports = []
        failed_exports = []
        
        for i, record in enumerate(records):
            try:
                # 生成文件名
                file_name = record.get('custom_name') or record.get('file_name', f'record_{record.get("id", i)}')
                safe_file_name = self._sanitize_filename(file_name)
                output_path = os.path.join(output_dir, f"{safe_file_name}.html")
                
                # 导出HTML
                if self.html_exporter.export_to_html(record, output_path, include_images):
                    successful_exports.append(output_path)
                else:
                    failed_exports.append(record.get('file_path', f'record_{i}'))
                    
            except Exception as e:
                print(f"导出HTML失败 {record.get('file_path', f'record_{i}')}: {e}")
                failed_exports.append(record.get('file_path', f'record_{i}'))
            
            # 更新进度
            if progress_callback:
                progress_callback(i + 1, len(records), record.get('file_path', f'record_{i}'))
        
        return {
            'total_records': len(records),
            'successful_count': len(successful_exports),
            'failed_count': len(failed_exports),
            'successful_exports': successful_exports,
            'failed_exports': failed_exports
        }
    
    def batch_export_json(self, 
                         records: List[Dict[str, Any]], 
                         output_file: str,
                         pretty_format: bool = True) -> bool:
        """
        批量导出JSON文件
        
        Args:
            records: 记录列表
            output_file: 输出文件路径
            pretty_format: 是否格式化输出
            
        Returns:
            bool: 是否成功
        """
        try:
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            
            export_data = {
                'export_time': datetime.now().isoformat(),
                'total_records': len(records),
                'records': records
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                if pretty_format:
                    json.dump(export_data, f, ensure_ascii=False, indent=2)
                else:
                    json.dump(export_data, f, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print(f"导出JSON失败: {e}")
            return False
    
    def batch_export_csv(self, 
                        records: List[Dict[str, Any]], 
                        output_file: str) -> bool:
        """
        批量导出CSV文件
        
        Args:
            records: 记录列表
            output_file: 输出文件路径
            
        Returns:
            bool: 是否成功
        """
        try:
            if not records:
                return False
            
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            
            # 定义CSV字段
            fieldnames = [
                'file_name', 'custom_name', 'prompt', 'negative_prompt', 
                'model', 'sampler', 'steps', 'cfg_scale', 'seed',
                'notes', 'tags', 'generation_source', 'created_at'
            ]
            
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                for record in records:
                    # 过滤字段
                    filtered_record = {
                        key: record.get(key, '') for key in fieldnames
                    }
                    writer.writerow(filtered_record)
            
            return True
            
        except Exception as e:
            print(f"导出CSV失败: {e}")
            return False
    
    def _sanitize_filename(self, filename: str) -> str:
        """
        清理文件名，移除不安全字符
        
        Args:
            filename: 原始文件名
            
        Returns:
            str: 清理后的文件名
        """
        # 移除文件扩展名
        if '.' in filename:
            filename = os.path.splitext(filename)[0]
        
        # 替换不安全字符
        unsafe_chars = '<>:"/\\|?*'
        for char in unsafe_chars:
            filename = filename.replace(char, '_')
        
        # 限制长度
        if len(filename) > 100:
            filename = filename[:100]
        
        # 确保不为空
        if not filename.strip():
            filename = 'unnamed'
        
        return filename.strip()
    
    def get_processing_status(self) -> Dict[str, Any]:
        """
        获取当前处理状态
        
        Returns:
            Dict: 处理状态信息
        """
        return {
            'is_processing': self.is_processing,
            'total_files': self.total_files,
            'processed_files': self.processed_files,
            'progress_percentage': (self.processed_files / self.total_files * 100) if self.total_files > 0 else 0,
            'successful_count': len(self.successful_files),
            'failed_count': len(self.failed_files)
        }
    
    def stop_processing(self):
        """停止处理（设置标志位）"""
        self.is_processing = False 