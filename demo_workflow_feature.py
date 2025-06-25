#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ComfyUI工作流存储功能演示
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.data_manager import DataManager
from core.image_reader import ImageInfoReader


def demo_workflow_feature():
    """演示ComfyUI工作流存储功能"""
    print("🎯 ComfyUI工作流存储功能演示")
    print("=" * 50)
    
    # 初始化组件
    data_manager = DataManager()
    image_reader = ImageInfoReader()
    
    # 获取所有记录
    records = data_manager.get_all_records()
    
    print(f"📊 数据库统计:")
    print(f"   总记录数: {len(records)}")
    
    # 分类统计
    comfyui_count = 0
    comfyui_with_workflow = 0
    sd_webui_count = 0
    
    for record in records:
        source = record.get('generation_source', '')
        workflow_data = record.get('workflow_data', '')
        
        if source == 'ComfyUI':
            comfyui_count += 1
            if workflow_data:
                comfyui_with_workflow += 1
        elif source == 'Stable Diffusion WebUI':
            sd_webui_count += 1
    
    print(f"   ComfyUI记录: {comfyui_count}")
    print(f"   └─ 包含workflow数据: {comfyui_with_workflow}")
    print(f"   SD WebUI记录: {sd_webui_count}")
    print(f"   其他记录: {len(records) - comfyui_count - sd_webui_count}")
    
    # 显示ComfyUI记录详情
    if comfyui_with_workflow > 0:
        print(f"\n🔧 ComfyUI工作流记录详情:")
        print("-" * 50)
        
        count = 0
        for record in records:
            if record.get('generation_source') == 'ComfyUI' and record.get('workflow_data'):
                count += 1
                if count > 5:  # 只显示前5条
                    print(f"   ... 还有 {comfyui_with_workflow - 5} 条记录")
                    break
                
                file_name = record.get('custom_name') or os.path.basename(record.get('file_path', ''))
                workflow_size = len(record.get('workflow_data', ''))
                
                print(f"   {count}. {file_name}")
                print(f"      文件路径: {record.get('file_path', '')}")
                print(f"      工作流数据大小: {workflow_size:,} 字符")
                print(f"      创建时间: {record.get('created_at', '')[:19]}")
                print()
    
    # 功能说明
    print("💡 功能说明:")
    print("-" * 50)
    print("1. 自动存储: 导入ComfyUI图片时自动提取并存储完整工作流")
    print("2. 一键加载: 在历史记录中点击'加载到ComfyUI'按钮")
    print("3. 数据安全: 即使原图片丢失，工作流数据仍然保存")
    print("4. 兼容性强: 支持所有ComfyUI工作流类型")
    
    print("\n🚀 使用方法:")
    print("-" * 50)
    print("1. 运行主程序: python main.py")
    print("2. 拖拽ComfyUI图片到工具中")
    print("3. 在历史记录中选择ComfyUI记录")
    print("4. 点击'加载到ComfyUI'按钮")
    print("5. 在ComfyUI中点击'Queue Prompt'重新生成")
    
    if comfyui_with_workflow == 0:
        print("\n⚠️  提示:")
        print("-" * 50)
        print("当前数据库中没有包含工作流数据的ComfyUI记录")
        print("请先导入一些ComfyUI生成的图片来体验此功能")
    
    print("\n✨ 此功能解决了ComfyUI用户的核心痛点!")
    print("   现在您再也不用担心工作流丢失的问题了! 🎉")


if __name__ == "__main__":
    try:
        demo_workflow_feature()
    except Exception as e:
        print(f"演示过程中出错: {e}")
        import traceback
        traceback.print_exc() 