#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
埋点分析功能测试脚本
用于验证Mixpanel集成是否正常工作
"""

import os
import sys
import time
from datetime import datetime

def test_analytics():
    """测试埋点分析功能"""
    print("=" * 60)
    print("埋点分析功能测试")
    print("=" * 60)
    
    # 检查依赖
    print("\n1. 检查依赖...")
    try:
        import mixpanel
        print("✓ mixpanel 库已安装")
    except ImportError:
        print("✗ mixpanel 库未安装，请运行: pip install mixpanel")
        return False
    
    try:
        import psutil
        print("✓ psutil 库已安装")
    except ImportError:
        print("✗ psutil 库未安装，请运行: pip install psutil")
        return False
    
    # 检查配置
    print("\n2. 检查配置...")
    
    # 检查环境变量
    token_from_env = os.getenv('MIXPANEL_TOKEN')
    if token_from_env and token_from_env != 'YOUR_MIXPANEL_PROJECT_TOKEN_HERE':
        print(f"✓ 环境变量中找到 Mixpanel Token: {token_from_env[:10]}...")
        token = token_from_env
    else:
        print("- 环境变量中未找到有效的 Mixpanel Token")
        
        # 检查配置文件
        config_file = "analytics_config.json"
        if os.path.exists(config_file):
            try:
                import json
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                token = config.get('mixpanel', {}).get('project_token', '')
                if token and token != 'YOUR_MIXPANEL_PROJECT_TOKEN_HERE':
                    print(f"✓ 配置文件中找到 Mixpanel Token: {token[:10]}...")
                else:
                    print("✗ 配置文件中未找到有效的 Mixpanel Token")
                    return False
            except Exception as e:
                print(f"✗ 读取配置文件失败: {e}")
                return False
        else:
            print("✗ 未找到配置文件 analytics_config.json")
            print("  请复制 analytics_config.json.example 并设置你的 Mixpanel Token")
            return False
    
    # 测试分析管理器
    print("\n3. 测试分析管理器初始化...")
    try:
        from core.analytics import AnalyticsManager
        analytics = AnalyticsManager(token)
        print("✓ 分析管理器初始化成功")
        print(f"  用户ID: {analytics.user_id}")
        print(f"  埋点状态: {'启用' if analytics.enabled else '禁用'}")
    except Exception as e:
        print(f"✗ 分析管理器初始化失败: {e}")
        return False
    
    if not analytics.enabled:
        print("✗ 埋点功能被禁用")
        return False
    
    # 测试事件发送
    print("\n4. 测试事件发送...")
    try:
        # 测试基础事件
        analytics.track_event("测试事件", {
            "test_time": datetime.now().isoformat(),
            "test_type": "basic"
        })
        print("✓ 基础事件发送成功")
        
        # 测试页面浏览
        analytics.track_page_view("测试页面")
        print("✓ 页面浏览事件发送成功")
        
        # 测试功能使用
        analytics.track_feature_usage("测试功能", {
            "test_parameter": "test_value"
        })
        print("✓ 功能使用事件发送成功")
        
        # 等待一下确保事件发送
        time.sleep(1)
        
    except Exception as e:
        print(f"✗ 事件发送失败: {e}")
        return False
    
    # 结束会话
    print("\n5. 结束测试会话...")
    try:
        analytics.end_session()
        print("✓ 测试会话结束成功")
    except Exception as e:
        print(f"✗ 结束会话失败: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✅ 埋点分析功能测试通过！")
    print("=" * 60)
    print("\n提示：")
    print("- 请登录你的 Mixpanel 控制台查看是否收到测试事件")
    print("- 事件可能需要几分钟才会在控制台中显示")
    print("- 如果没有收到事件，请检查网络连接和 Token 配置")
    
    return True


def show_system_info():
    """显示系统信息"""
    print("\n系统信息:")
    print("-" * 40)
    
    try:
        from core.analytics import AnalyticsManager
        
        # 创建临时实例获取系统信息
        temp_analytics = AnalyticsManager()
        system_info = temp_analytics._get_system_info()
        
        for key, value in system_info.items():
            print(f"{key}: {value}")
            
    except Exception as e:
        print(f"获取系统信息失败: {e}")


def main():
    """主函数"""
    print("白泽AI - 埋点分析功能测试工具")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 显示系统信息
    show_system_info()
    
    # 运行测试
    success = test_analytics()
    
    if not success:
        print("\n❌ 测试失败，请检查配置后重试")
        print("\n配置步骤：")
        print("1. 获取 Mixpanel 项目 Token")
        print("2. 设置环境变量或配置文件")
        print("3. 安装必要的依赖包")
        print("\n详细说明请查看: doc/埋点分析功能说明.md")
        sys.exit(1)
    
    sys.exit(0)


if __name__ == "__main__":
    main() 