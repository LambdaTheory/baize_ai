#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试ComfyUI工作流存储功能
"""

import sys
import os
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.data_manager import DataManager
from core.image_reader import ImageInfoReader
from core.comfyui_integration import ComfyUIIntegration


def test_workflow_storage():
    """测试工作流存储功能"""
    print("=== 测试ComfyUI工作流存储功能 ===")
    
    # 1. 初始化组件
    data_manager = DataManager()
    image_reader = ImageInfoReader()
    comfyui = ComfyUIIntegration()
    
    # 2. 查找ComfyUI生成的图片
    test_dirs = [
        ".",
        "assets",
        os.path.expanduser("~/Desktop"),
        os.path.expanduser("~/Downloads")
    ]
    
    comfyui_images = []
    for test_dir in test_dirs:
        if os.path.exists(test_dir):
            for file in os.listdir(test_dir):
                if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                    file_path = os.path.join(test_dir, file)
                    print(f"\n检查文件: {file_path}")
                    
                    # 提取图片信息
                    info = image_reader.extract_info(file_path)
                    if info and info.get('generation_source') == 'ComfyUI':
                        print(f"✅ 找到ComfyUI图片: {file}")
                        print(f"   工作流类型: {info.get('workflow_type', '未知')}")
                        print(f"   是否包含workflow数据: {'是' if info.get('workflow_data') else '否'}")
                        
                        if info.get('workflow_data'):
                            comfyui_images.append((file_path, info))
                            if len(comfyui_images) >= 3:  # 最多测试3张图片
                                break
        if len(comfyui_images) >= 3:
            break
    
    if not comfyui_images:
        print("❌ 未找到包含workflow数据的ComfyUI图片")
        print("请确保有ComfyUI生成的图片包含完整的workflow信息")
        return False
    
    print(f"\n找到 {len(comfyui_images)} 张包含workflow数据的ComfyUI图片")
    
    # 3. 测试数据存储
    print("\n=== 测试数据存储 ===")
    stored_records = []
    
    for file_path, info in comfyui_images:
        print(f"\n存储图片: {os.path.basename(file_path)}")
        
        # 构造记录数据
        record_data = {
            'file_path': file_path,
            'custom_name': f"测试_{os.path.basename(file_path)}",
            'prompt': info.get('prompt', ''),
            'negative_prompt': info.get('negative_prompt', ''),
            'model': info.get('model', ''),
            'sampler': info.get('sampler', ''),
            'steps': info.get('steps'),
            'cfg_scale': info.get('cfg_scale'),
            'seed': info.get('seed'),
            'generation_source': info.get('generation_source', ''),
            'workflow_data': info.get('workflow_data'),  # 重要：存储workflow数据
            'notes': '测试工作流存储功能'
        }
        
        # 存储到数据库
        record_id = data_manager.save_record(record_data)
        if record_id:
            print(f"✅ 记录已存储，ID: {record_id}")
            stored_records.append(record_id)
        else:
            print("❌ 记录存储失败")
    
    # 4. 测试数据读取
    print("\n=== 测试数据读取 ===")
    for record_id in stored_records:
        record = data_manager.get_record_by_id(record_id)
        if record:
            print(f"\n记录ID {record_id}:")
            print(f"  文件路径: {record.get('file_path', '')}")
            print(f"  生成来源: {record.get('generation_source', '')}")
            
            workflow_data_str = record.get('workflow_data', '')
            if workflow_data_str:
                try:
                    workflow_data = json.loads(workflow_data_str)
                    print(f"  工作流节点数: {len(workflow_data) if isinstance(workflow_data, dict) else '未知'}")
                    print("  ✅ 工作流数据完整")
                except json.JSONDecodeError:
                    print("  ❌ 工作流数据解析失败")
            else:
                print("  ❌ 未找到工作流数据")
        else:
            print(f"❌ 无法读取记录ID {record_id}")
    
    # 5. 测试ComfyUI加载功能
    print("\n=== 测试ComfyUI加载功能 ===")
    
    # 检查ComfyUI状态
    is_running, status_msg = comfyui.check_comfyui_status()
    print(f"ComfyUI状态: {status_msg}")
    
    if is_running and stored_records:
        # 测试从数据库记录加载工作流
        test_record_id = stored_records[0]
        test_record = data_manager.get_record_by_id(test_record_id)
        
        if test_record:
            print(f"\n测试加载记录ID {test_record_id} 到ComfyUI...")
            success, message = comfyui.load_workflow_from_database_record(test_record)
            
            if success:
                print(f"✅ 工作流加载成功: {message}")
            else:
                print(f"❌ 工作流加载失败: {message}")
        else:
            print("❌ 无法获取测试记录")
    else:
        print("⚠️  ComfyUI未运行，跳过加载测试")
    
    # 6. 清理测试数据
    print("\n=== 清理测试数据 ===")
    for record_id in stored_records:
        if data_manager.delete_record(record_id):
            print(f"✅ 已删除测试记录ID {record_id}")
        else:
            print(f"❌ 删除测试记录ID {record_id} 失败")
    
    print("\n=== 测试完成 ===")
    return True


if __name__ == "__main__":
    try:
        test_workflow_storage()
    except Exception as e:
        print(f"测试过程中出错: {e}")
        import traceback
        traceback.print_exc() 