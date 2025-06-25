#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
白泽AI Logo生成器
使用OpenAI DALL-E生成白泽神兽主题的logo
"""

import os
import requests
import base64
from datetime import datetime
from pathlib import Path
from openai import OpenAI


def generate_logo():
    """生成白泽AI的Logo"""
    
    # 参考项目中的OpenAI配置
    api_key = os.getenv("OPENAI_API_KEY") or "sk-CnEoNNdwU8KeJfIoEg6rcNeLeO5XbF3HafEMckZkuZXvKSGS"
    base_url = "https://api.ssopen.top/v1"
    
    print("🎨 开始生成白泽AI Logo...")
    print(f"📡 API Base URL: {base_url}")
    
    try:
        # 初始化OpenAI客户端
        client = OpenAI(
            api_key=api_key,
            base_url=base_url,
            timeout=120
        )
        
        # Logo设计提示词
        logo_prompts = [
            # 现代简约版本
            {
                "name": "baize_modern",
                "prompt": """Create a modern minimalist logo for 'Baize AI' (白泽AI). 
                Feature a stylized white mythical creature Baize (白泽) - a legendary beast with wisdom and knowledge. 
                The creature should have a majestic appearance with flowing mane, wise eyes, and ethereal presence.
                Use a clean, modern design with gradient colors from white to blue-purple.
                Include subtle AI circuit patterns or neural network elements integrated into the creature's design.
                The overall style should be professional, elegant, and tech-savvy.
                Background should be transparent or clean white.
                Vector-style illustration, high quality, 1024x1024 pixels."""
            },
            
            # 传统文化版本
            {
                "name": "baize_traditional", 
                "prompt": """Create a logo combining traditional Chinese mythology with modern AI aesthetics for 'Baize AI' (白泽AI).
                Feature the legendary Baize creature - a wise mythical beast that knows all things.
                Design it with traditional Chinese artistic elements like flowing clouds, ancient patterns, but with a modern twist.
                Use colors: deep blue, gold, white, and subtle gradients.
                Include subtle technological elements like digital patterns or geometric shapes.
                The creature should look wise, majestic, and mystical.
                Clean background, professional logo design, 1024x1024 pixels."""
            },
            
            # 科技感版本
            {
                "name": "baize_tech",
                "prompt": """Design a high-tech logo for 'Baize AI' featuring a futuristic interpretation of the mythical Baize creature.
                The Baize should have a cyber-mystical appearance with glowing elements, digital particles, and neural network patterns.
                Use colors: electric blue, cyan, white, with neon accents.
                Incorporate holographic effects, data streams, and AI-inspired geometric patterns.
                The creature should maintain its mythical wisdom appearance while looking cutting-edge.
                Dark background with bright glowing elements, professional logo design, 1024x1024 pixels."""
            }
        ]
        
        # 创建assets目录
        assets_dir = Path("assets")
        assets_dir.mkdir(exist_ok=True)
        
        # 生成每个版本的logo
        for i, logo_config in enumerate(logo_prompts, 1):
            print(f"\n🎯 正在生成Logo {i}/3: {logo_config['name']}")
            print(f"📝 提示词: {logo_config['prompt'][:100]}...")
            
            try:
                # 调用DALL-E API生成图片
                response = client.images.generate(
                    model="dall-e-3",
                    prompt=logo_config['prompt'],
                    size="1024x1024",
                    quality="hd",
                    style="vivid",
                    n=1
                )
                
                # 获取生成的图片URL
                image_url = response.data[0].url
                print(f"✅ Logo生成成功! 图片URL: {image_url}")
                
                # 下载图片
                print("📥 正在下载图片...")
                img_response = requests.get(image_url, timeout=30)
                img_response.raise_for_status()
                
                # 保存图片
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"baize_logo_{logo_config['name']}_{timestamp}.png"
                filepath = assets_dir / filename
                
                with open(filepath, 'wb') as f:
                    f.write(img_response.content)
                
                print(f"💾 Logo已保存至: {filepath}")
                
                # 创建图标版本 (适用于应用图标)
                icon_filename = f"baize_icon_{logo_config['name']}_{timestamp}.png"
                icon_filepath = assets_dir / icon_filename
                
                # 复制一份作为图标 (实际项目中可能需要调整尺寸)
                with open(icon_filepath, 'wb') as f:
                    f.write(img_response.content)
                
                print(f"🔖 应用图标已保存至: {icon_filepath}")
                
            except Exception as e:
                print(f"❌ 生成Logo {logo_config['name']} 时出错: {e}")
                continue
        
        print("\n🎉 Logo生成完成!")
        print(f"📁 所有文件保存在: {assets_dir.absolute()}")
        
        # 生成logo使用说明
        readme_content = f"""# 白泽AI Logo 使用说明

## 📁 文件说明

本目录包含白泽AI的Logo设计文件，生成时间：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

### 🎨 Logo版本

1. **baize_modern** - 现代简约版本
   - 适用场景：官网、应用界面、商务场合
   - 特点：简洁现代，科技感强

2. **baize_traditional** - 传统文化版本  
   - 适用场景：品牌宣传、文化展示
   - 特点：融合传统元素，文化底蕴深厚

3. **baize_tech** - 科技感版本
   - 适用场景：技术文档、开发者社区
   - 特点：未来感强，突出AI科技属性

### 📐 尺寸规格

- **Logo**: 1024x1024 像素，PNG格式
- **Icon**: 1024x1024 像素，PNG格式（可缩放至16x16, 32x32, 64x64等）

### 🎯 使用建议

- 启动画面：推荐使用modern版本
- 应用图标：推荐使用traditional版本  
- 技术文档：推荐使用tech版本

### 🔧 技术实现

Logo由OpenAI DALL-E 3生成，基于山海经中白泽神兽的设计理念。
白泽象征智慧和知识，完美契合AI图片分析工具的定位。
"""
        
        readme_path = assets_dir / "README.md"
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        print(f"📄 使用说明已保存至: {readme_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ 生成Logo时出错: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("=" * 50)
    print("🐉 白泽AI Logo生成器")
    print("=" * 50)
    
    success = generate_logo()
    
    if success:
        print("\n✨ Logo生成任务完成！")
        print("💡 提示：请查看assets目录中的logo文件")
        print("📋 建议选择一个作为主Logo，并相应更新应用代码")
    else:
        print("\n❌ Logo生成失败！")
        print("🔧 请检查API配置和网络连接") 