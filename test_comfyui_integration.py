#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ComfyUI集成功能测试脚本
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.append(str(Path(__file__).parent))

from core.comfyui_integration import ComfyUIIntegration
from core.image_reader import ImageInfoReader


def test_comfyui_status():
    """测试ComfyUI状态检查"""
    print("=" * 50)
    print("测试ComfyUI状态检查")
    print("=" * 50)
    
    comfyui = ComfyUIIntegration()
    is_running, message = comfyui.check_comfyui_status()
    
    print(f"ComfyUI状态: {'运行中' if is_running else '未运行'}")
    print(f"状态消息: {message}")
    print()
    
    return is_running


def test_workflow_extraction():
    """测试工作流提取"""
    print("=" * 50)
    print("测试工作流提取功能")
    print("=" * 50)
    
    # 查找测试图片
    test_images = []
    
    # 查找data目录中的图片
    data_dir = Path("data")
    if data_dir.exists():
        for ext in ["*.png", "*.jpg", "*.jpeg"]:
            test_images.extend(data_dir.glob(ext))
    
    # 查找根目录中的图片
    for ext in ["*.png", "*.jpg", "*.jpeg"]:
        test_images.extend(Path(".").glob(ext))
    
    if not test_images:
        print("未找到测试图片文件")
        print("请将包含ComfyUI工作流的PNG图片放在data目录或项目根目录中")
        return False
    
    comfyui = ComfyUIIntegration()
    found_workflow = False
    
    for img_path in test_images[:5]:  # 最多测试5张图片
        print(f"\n正在测试图片: {img_path}")
        
        workflow = comfyui.extract_comfyui_workflow(str(img_path))
        
        if workflow:
            print(f"✅ 找到工作流数据！")
            print(f"工作流节点数量: {len(workflow)}")
            print(f"工作流键: {list(workflow.keys())[:10]}...")  # 显示前10个键
            found_workflow = True
            break
        else:
            print(f"❌ 未找到工作流数据")
    
    if not found_workflow:
        print("\n📝 提示: 要测试工作流提取功能，请使用包含ComfyUI工作流的PNG图片")
        print("这些图片通常是由ComfyUI生成的，包含嵌入的工作流JSON数据")
    
    return found_workflow


def test_sd_to_comfyui_conversion():
    """测试SD WebUI到ComfyUI工作流转换"""
    print("=" * 50)
    print("测试SD WebUI到ComfyUI工作流转换")
    print("=" * 50)
    
    # 模拟SD WebUI参数
    sd_params = {
        'prompt': 'a beautiful landscape, highly detailed, masterpiece',
        'negative_prompt': 'blurry, low quality, worst quality',
        'model': 'sd_xl_base_1.0.safetensors',
        'sampler': 'DPM++ 2M Karras',
        'steps': 25,
        'cfg_scale': 7.5,
        'seed': 123456789,
        'width': 1024,
        'height': 1024
    }
    
    comfyui = ComfyUIIntegration()
    workflow = comfyui.convert_sd_webui_to_comfyui_workflow(sd_params)
    
    if workflow:
        print("✅ 成功生成ComfyUI工作流")
        print(f"工作流节点数量: {len(workflow)}")
        
        # 检查关键节点
        key_nodes = ['1', '2', '3', '4', '5', '6', '7']  # 基础工作流节点
        for node_id in key_nodes:
            if node_id in workflow:
                node = workflow[node_id]
                print(f"节点 {node_id}: {node.get('class_type', 'Unknown')}")
        
        return True
    else:
        print("❌ 工作流转换失败")
        return False


def test_full_integration():
    """测试完整集成流程"""
    print("=" * 50)
    print("测试完整集成流程")
    print("=" * 50)
    
    # 查找包含工作流的测试图片
    test_images = []
    
    data_dir = Path("data")
    if data_dir.exists():
        test_images.extend(data_dir.glob("*.png"))
    
    test_images.extend(Path(".").glob("*.png"))
    
    if not test_images:
        print("未找到PNG测试图片，跳过完整集成测试")
        return False
    
    comfyui = ComfyUIIntegration()
    
    for img_path in test_images[:3]:  # 测试前3张图片
        print(f"\n正在测试完整流程: {img_path}")
        
        success, message = comfyui.load_workflow_from_image(str(img_path))
        
        print(f"结果: {'成功' if success else '失败'}")
        print(f"消息: {message}")
        
        if success:
            return True
    
    return False


def main():
    """主测试函数"""
    print("ComfyUI集成功能测试")
    print("=" * 70)
    
    results = {}
    
    # 1. 测试ComfyUI状态
    results['status'] = test_comfyui_status()
    
    # 2. 测试工作流提取
    results['extraction'] = test_workflow_extraction()
    
    # 3. 测试工作流转换
    results['conversion'] = test_sd_to_comfyui_conversion()
    
    # 4. 如果ComfyUI运行中，测试完整集成
    if results['status']:
        results['full_integration'] = test_full_integration()
    else:
        results['full_integration'] = None
        print("⚠️  ComfyUI未运行，跳过完整集成测试")
    
    # 总结结果
    print("\n" + "=" * 70)
    print("测试结果总结")
    print("=" * 70)
    
    print(f"ComfyUI状态检查: {'✅ 通过' if results['status'] else '❌ 失败'}")
    print(f"工作流提取功能: {'✅ 通过' if results['extraction'] else '❌ 失败'}")
    print(f"工作流转换功能: {'✅ 通过' if results['conversion'] else '❌ 失败'}")
    
    if results['full_integration'] is not None:
        print(f"完整集成测试: {'✅ 通过' if results['full_integration'] else '❌ 失败'}")
    else:
        print(f"完整集成测试: ⚠️  跳过 (ComfyUI未运行)")
    
    # 提供使用建议
    print("\n" + "=" * 70)
    print("使用建议")
    print("=" * 70)
    
    if not results['status']:
        print("🔧 要使用ComfyUI集成功能，请先启动ComfyUI:")
        print("   1. 进入ComfyUI目录")
        print("   2. 运行: python main.py")
        print("   3. 等待启动完成，默认地址: http://127.0.0.1:8188")
    else:
        print("✨ ComfyUI集成功能已就绪！")
        print("📋 使用方法:")
        print("   1. 在AI图片信息提取工具中选择包含工作流的图片")
        print("   2. 点击 '🎯 导入ComfyUI' 按钮")
        print("   3. 工作流将自动导入到ComfyUI中")
    
    print("\n💡 提示:")
    print("   - 支持的图片格式: PNG (推荐), JPG")
    print("   - ComfyUI生成的PNG图片通常包含完整的工作流数据")
    print("   - Stable Diffusion WebUI生成的图片可以转换为基础ComfyUI工作流")


if __name__ == "__main__":
    main() 