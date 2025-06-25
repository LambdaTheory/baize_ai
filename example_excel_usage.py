#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel导出功能使用示例
"""

import os
import sys
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.excel_exporter import ExcelExporter
from core.data_manager import DataManager


def example_excel_export_with_images():
    """带图片的Excel导出示例"""
    print("=== Excel导出示例（含图片） ===")
    
    # 创建数据管理器
    dm = DataManager()
    
    # 获取所有记录
    records = dm.get_all_records()
    print(f"找到 {len(records)} 条记录")
    
    if not records:
        print("没有记录可导出")
        return
    
    # 创建Excel导出器
    exporter = ExcelExporter()
    
    # 导出文件路径
    output_path = f"AI图片信息导出_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    
    print(f"开始导出到: {output_path}")
    print("包含图片，可能需要较长时间...")
    
    # 执行导出（包含图片）
    success = exporter.export_records(
        records=records,
        output_path=output_path,
        include_images=True,  # 包含图片
        max_image_size=(120, 120)  # 图片尺寸
    )
    
    if success:
        file_size = os.path.getsize(output_path)
        print(f"导出成功！")
        print(f"文件路径: {os.path.abspath(output_path)}")
        print(f"文件大小: {file_size:,} 字节 ({file_size/1024/1024:.2f} MB)")
        print(f"包含记录: {len(records)} 条")
    else:
        print("导出失败")


def example_excel_export_data_only():
    """仅数据的Excel导出示例"""
    print("\n=== Excel导出示例（仅数据） ===")
    
    # 创建数据管理器
    dm = DataManager()
    
    # 获取所有记录
    records = dm.get_all_records()
    
    if not records:
        print("没有记录可导出")
        return
    
    # 创建Excel导出器
    exporter = ExcelExporter()
    
    # 导出文件路径
    output_path = f"AI图片数据导出_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    
    print(f"开始导出到: {output_path}")
    
    # 执行导出（不包含图片）
    success = exporter.export_records(
        records=records,
        output_path=output_path,
        include_images=False  # 不包含图片
    )
    
    if success:
        file_size = os.path.getsize(output_path)
        print(f"导出成功！")
        print(f"文件路径: {os.path.abspath(output_path)}")
        print(f"文件大小: {file_size:,} 字节")
        print(f"包含记录: {len(records)} 条")
    else:
        print("导出失败")


def show_usage_tips():
    """显示使用提示"""
    print("\n=== 使用提示 ===")
    print("1. 在UI中使用：")
    print("   - 选择记录 → 批量导出 → 选择Excel格式 → 开始导出")
    print("\n2. 导出选项：")
    print("   - 包含图片：文件较大但信息完整")
    print("   - 仅数据：文件较小，便于数据分析")
    print("\n3. 注意事项：")
    print("   - 确保图片文件存在且可访问")
    print("   - 大量图片可能需要较长时间")
    print("   - 生成的Excel文件兼容Office 2010+")


if __name__ == "__main__":
    try:
        # 仅数据导出示例（快速）
        example_excel_export_data_only()
        
        # 带图片导出示例（较慢）
        # example_excel_export_with_images()
        
        # 显示使用提示
        show_usage_tips()
        
    except Exception as e:
        print(f"示例运行出错: {e}")
        import traceback
        traceback.print_exc()