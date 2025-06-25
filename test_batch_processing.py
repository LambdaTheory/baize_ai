#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量处理功能测试
"""

import os
import sys
import tempfile
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.batch_processor import BatchProcessor
from core.data_manager import DataManager


def test_batch_processor():
    """测试批量处理器"""
    print("🧪 开始测试批量处理功能...")
    
    # 创建测试数据管理器
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = os.path.join(temp_dir, "test.db")
        data_manager = DataManager(db_path)
        
        # 创建批量处理器
        batch_processor = BatchProcessor(data_manager)
        
        # 测试扫描文件夹
        print("\n📁 测试文件夹扫描...")
        current_dir = Path(__file__).parent
        image_files = batch_processor.scan_folder(str(current_dir), recursive=True)
        print(f"扫描到 {len(image_files)} 个图片文件")
        
        if image_files:
            print(f"示例文件: {image_files[:3]}")  # 显示前3个文件
            
            # 测试批量处理
            print("\n⚡ 测试批量处理...")
            result = batch_processor.batch_process_images(
                image_files[:5],  # 只处理前5个文件避免测试时间过长
                auto_save=True,
                max_workers=2
            )
            
            print(f"处理结果:")
            print(f"  总文件数: {result['total_files']}")
            print(f"  成功处理: {result['successful_count']}")
            print(f"  处理失败: {result['failed_count']}")
            print(f"  处理时间: {result['processing_time']:.2f} 秒")
            
            # 测试导出功能
            if result['successful_count'] > 0:
                print("\n📤 测试导出功能...")
                
                # 获取所有记录
                records = data_manager.get_all_records()
                print(f"数据库中有 {len(records)} 条记录")
                
                # 测试JSON导出
                json_file = os.path.join(temp_dir, "test_export.json")
                json_success = batch_processor.batch_export_json(records, json_file)
                print(f"JSON导出: {'成功' if json_success else '失败'}")
                
                # 测试CSV导出  
                csv_file = os.path.join(temp_dir, "test_export.csv")
                csv_success = batch_processor.batch_export_csv(records, csv_file)
                print(f"CSV导出: {'成功' if csv_success else '失败'}")
                
                # 测试HTML导出
                html_dir = os.path.join(temp_dir, "html_export")
                html_result = batch_processor.batch_export_html(
                    records[:2],  # 只导出前2个记录
                    html_dir,
                    include_images=False  # 不包含图片以避免大文件
                )
                print(f"HTML导出: 成功 {html_result['successful_count']} 个文件")
        
        print("\n✅ 批量处理功能测试完成！")


def test_ui_components():
    """测试UI组件（需要Qt环境）"""
    try:
        from PyQt5.QtWidgets import QApplication
        from ui.fluent_batch_widget import FluentBatchWidget
        from core.data_manager import DataManager
        
        print("\n🎨 测试UI组件...")
        
        app = QApplication([])
        
        # 创建测试数据管理器
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = os.path.join(temp_dir, "test.db")
            data_manager = DataManager(db_path)
            
            # 创建批量处理组件
            batch_widget = FluentBatchWidget(data_manager)
            batch_widget.show()
            
            print("批量处理UI组件创建成功！")
            print("提示：实际使用时请在主程序中查看UI界面")
            
        app.quit()
        
    except ImportError as e:
        print(f"⚠️ UI测试跳过（缺少依赖）: {e}")
    except Exception as e:
        print(f"❌ UI测试失败: {e}")


if __name__ == "__main__":
    print("🚀 AI图片信息提取工具 - 批量处理功能测试")
    print("=" * 50)
    
    # 测试核心功能
    test_batch_processor()
    
    # 测试UI组件
    test_ui_components()
    
    print("\n🎉 所有测试完成！")
    print("\n📋 功能说明：")
    print("1. 批量扫描：支持递归扫描文件夹中的图片文件")
    print("2. 批量处理：多线程并发处理图片信息提取")
    print("3. 批量导出：支持HTML、JSON、CSV三种格式导出")
    print("4. 进度跟踪：实时显示处理进度和结果统计")
    print("5. 错误处理：优雅处理文件错误和异常情况")
    
    print("\n🔧 使用方法：")
    print("1. 运行主程序：python main.py")
    print("2. 点击导航栏中的'批量处理'")
    print("3. 选择要处理的图片文件夹")
    print("4. 配置处理选项，点击'开始批量处理'")
    print("5. 等待处理完成，查看结果统计")
    print("6. 使用批量导出功能导出处理结果") 