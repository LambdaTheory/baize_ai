#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
埋点分析模块
集成Mixpanel SDK，用于追踪用户使用情况和页面访问
"""

import os
import sys
import time
import json
import hashlib
import platform
from datetime import datetime, timezone
from typing import Dict, Any, Optional
import uuid

try:
    import mixpanel
    MIXPANEL_AVAILABLE = True
except ImportError:
    MIXPANEL_AVAILABLE = False
    print("[警告] Mixpanel库未安装，埋点功能将被禁用")


class AnalyticsManager:
    """分析埋点管理器"""
    
    def __init__(self, project_token: str = None):
        """
        初始化分析管理器
        
        Args:
            project_token: Mixpanel项目token
        """
        self.project_token = project_token or self._get_default_token()
        self.mp = None
        self.enabled = True
        self.user_id = None
        self.session_start_time = None
        self.current_page = None
        self.previous_page = None
        
        # 初始化Mixpanel
        self._init_mixpanel()
        
        # 生成用户标识
        self._init_user_id()
        
        # 开始会话
        self._start_session()
    
    def _get_default_token(self) -> str:
        """获取默认的Mixpanel token"""
        # 优先从环境变量读取
        token_from_env = os.getenv('MIXPANEL_TOKEN')
        if token_from_env and token_from_env != 'YOUR_MIXPANEL_PROJECT_TOKEN_HERE':
            return token_from_env
        
        # 从配置文件读取
        config_file = "analytics_config.json"
        if os.path.exists(config_file):
            try:
                import json
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                # 检查是否禁用埋点
                if not config.get('mixpanel', {}).get('enabled', True):
                    return None
                
                token = config.get('mixpanel', {}).get('project_token', '')
                if token and token != 'YOUR_MIXPANEL_PROJECT_TOKEN_HERE':
                    return token
            except Exception as e:
                print(f"[警告] 读取埋点配置文件失败: {e}")
        
        # 检查是否通过环境变量禁用
        if os.getenv('ANALYTICS_DISABLED', '').lower() in ('true', '1', 'yes'):
            return None
        
        return 'YOUR_MIXPANEL_PROJECT_TOKEN_HERE'
    
    def _init_mixpanel(self):
        """初始化Mixpanel客户端"""
        if not MIXPANEL_AVAILABLE:
            self.enabled = False
            return
            
        if not self.project_token or self.project_token == 'YOUR_MIXPANEL_PROJECT_TOKEN_HERE':
            if self.project_token is None:
                print("[信息] 埋点功能已被配置禁用")
            else:
                print("[信息] 未设置有效的Mixpanel项目token，埋点功能已禁用")
            self.enabled = False
            return
            
        try:
            self.mp = mixpanel.Mixpanel(self.project_token)
            print(f"[成功] Mixpanel客户端初始化成功")
        except Exception as e:
            print(f"[错误] Mixpanel客户端初始化失败: {e}")
            self.enabled = False
    
    def _init_user_id(self):
        """初始化用户标识"""
        # 生成基于机器的唯一标识
        try:
            # 使用MAC地址生成稳定的用户ID
            import psutil
            
            # 获取网络接口信息
            network_interfaces = psutil.net_if_addrs()
            mac_addresses = []
            
            for interface_name, interface_addresses in network_interfaces.items():
                for address in interface_addresses:
                    if address.family == psutil.AF_LINK:  # MAC地址
                        mac_addresses.append(address.address)
            
            # 使用第一个有效的MAC地址
            if mac_addresses:
                primary_mac = next((mac for mac in mac_addresses if mac != '00:00:00:00:00:00'), None)
                if primary_mac:
                    # 生成基于MAC地址的哈希用户ID
                    user_hash = hashlib.sha256(primary_mac.encode()).hexdigest()[:16]
                    self.user_id = f"user_{user_hash}"
                else:
                    self.user_id = f"user_{uuid.uuid4().hex[:16]}"
            else:
                self.user_id = f"user_{uuid.uuid4().hex[:16]}"
                
        except ImportError:
            # 如果psutil不可用，使用UUID
            self.user_id = f"user_{uuid.uuid4().hex[:16]}"
        except Exception as e:
            print(f"[警告] 生成用户ID时出错: {e}")
            self.user_id = f"user_{uuid.uuid4().hex[:16]}"
        
        print(f"[信息] 用户ID: {self.user_id}")
    
    def _start_session(self):
        """开始新的会话"""
        self.session_start_time = time.time()
        
        # 发送会话开始事件
        self.track_event("SessionStart", {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            **self._get_system_info()
        })
    
    def _get_system_info(self) -> Dict[str, Any]:
        """获取系统信息"""
        try:
            import psutil
            
            system_info = {
                "os": platform.system(),
                "os_version": platform.version(),
                "architecture": platform.architecture()[0],
                "python_version": platform.python_version(),
                "cpu_count": psutil.cpu_count(),
                "memory_gb": round(psutil.virtual_memory().total / (1024**3), 2),
                "app_version": "3.0.0",  # 从应用程序获取版本号
                "is_frozen": getattr(sys, 'frozen', False),  # 是否为打包后的exe
            }
            
            return system_info
            
        except ImportError:
            # 如果psutil不可用，返回基础信息
            return {
                "os": platform.system(),
                "os_version": platform.version(),
                "architecture": platform.architecture()[0],
                "python_version": platform.python_version(),
                "app_version": "3.0.0",
                "is_frozen": getattr(sys, 'frozen', False),
            }
        except Exception as e:
            print(f"[警告] 获取系统信息时出错: {e}")
            return {"error": "failed_to_get_system_info"}
    
    def track_event(self, event_name: str, properties: Dict[str, Any] = None):
        """
        追踪事件
        
        Args:
            event_name: 事件名称
            properties: 事件属性
        """
        if not self.enabled or not self.mp:
            return
            
        try:
            # 合并默认属性
            event_properties = {
                "user_id": self.user_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "session_id": self.session_start_time,
                **(properties or {})
            }
            
            # 发送事件到Mixpanel
            self.mp.track(self.user_id, event_name, event_properties)
            print(f"[埋点] 事件已发送: {event_name}")
            
        except Exception as e:
            print(f"[错误] 发送埋点事件失败: {e}")
    
    def track_use_time(self, duration: float):
        """
        追踪使用时长
        
        Args:
            duration: 使用时长（秒）
        """
        self.track_event("UseTime", {
            "duration": duration,
            "duration_minutes": round(duration / 60, 2),
            "session_duration": time.time() - self.session_start_time if self.session_start_time else 0
        })
    
    def track_page_view(self, page_name: str, referrer_url_path: str = None):
        """
        追踪页面浏览
        
        Args:
            page_name: 页面名称
            referrer_url_path: 来源URL路径
        """
        # 更新页面状态
        self.previous_page = self.current_page
        self.current_page = page_name
        
        self.track_event("PageView", {
            "page_name": page_name,
            "referrer_url_path": referrer_url_path or self.previous_page,
            "previous_page": self.previous_page,
            "navigation_type": "direct" if not self.previous_page else "internal"
        })
    
    def track_feature_usage(self, feature_name: str, details: Dict[str, Any] = None):
        """
        追踪功能使用
        
        Args:
            feature_name: 功能名称
            details: 功能详情
        """
        self.track_event("FeatureUsage", {
            "feature_name": feature_name,
            "current_page": self.current_page,
            **(details or {})
        })
    
    def track_error(self, error_type: str, error_message: str, context: Dict[str, Any] = None):
        """
        追踪错误
        
        Args:
            error_type: 错误类型
            error_message: 错误消息
            context: 错误上下文
        """
        self.track_event("Error", {
            "error_type": error_type,
            "error_message": error_message,
            "current_page": self.current_page,
            **(context or {})
        })
    
    def update_user_profile(self, properties: Dict[str, Any]):
        """
        更新用户档案
        
        Args:
            properties: 用户属性
        """
        if not self.enabled or not self.mp:
            return
            
        try:
            self.mp.people_set(self.user_id, properties)
            print(f"[埋点] 用户档案已更新")
        except Exception as e:
            print(f"[错误] 更新用户档案失败: {e}")
    
    def flush(self):
        """刷新埋点数据，确保数据发送"""
        if not self.enabled or not self.mp:
            return
            
        try:
            # Mixpanel Python SDK会自动处理数据发送
            print("[埋点] 数据刷新完成")
        except Exception as e:
            print(f"[错误] 刷新埋点数据失败: {e}")
    
    def end_session(self):
        """结束会话"""
        if self.session_start_time:
            session_duration = time.time() - self.session_start_time
            
            # 发送会话结束事件
            self.track_event("SessionEnd", {
                "session_duration": session_duration,
                "session_duration_minutes": round(session_duration / 60, 2),
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            
            # 追踪总使用时长
            self.track_use_time(session_duration)
            
            # 刷新数据
            self.flush()


# 全局分析管理器实例
_analytics_manager = None


def get_analytics_manager() -> AnalyticsManager:
    """获取全局分析管理器实例"""
    global _analytics_manager
    if _analytics_manager is None:
        _analytics_manager = AnalyticsManager()
    return _analytics_manager


def init_analytics(project_token: str = None) -> AnalyticsManager:
    """
    初始化分析管理器
    
    Args:
        project_token: Mixpanel项目token
        
    Returns:
        AnalyticsManager实例
    """
    global _analytics_manager
    _analytics_manager = AnalyticsManager(project_token)
    return _analytics_manager


# 便捷函数
def track_event(event_name: str, properties: Dict[str, Any] = None):
    """追踪事件的便捷函数"""
    get_analytics_manager().track_event(event_name, properties)


def track_use_time(duration: float):
    """追踪使用时长的便捷函数"""
    get_analytics_manager().track_use_time(duration)


def track_page_view(page_name: str, referrer_url_path: str = None):
    """追踪页面浏览的便捷函数"""
    get_analytics_manager().track_page_view(page_name, referrer_url_path)


def track_feature_usage(feature_name: str, details: Dict[str, Any] = None):
    """追踪功能使用的便捷函数"""
    get_analytics_manager().track_feature_usage(feature_name, details)


def track_error(error_type: str, error_message: str, context: Dict[str, Any] = None):
    """追踪错误的便捷函数"""
    get_analytics_manager().track_error(error_type, error_message, context)


def end_session():
    """结束会话的便捷函数"""
    get_analytics_manager().end_session() 