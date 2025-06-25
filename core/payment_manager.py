#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Payment Manager - 支付管理模块
安全的Creem支付系统集成
"""

import json
import time
import uuid
import hashlib
import requests
import os
from typing import Dict, Optional, Tuple
from pathlib import Path


class PaymentManager:
    """支付管理器 - 安全版本"""
    
    def __init__(self):
        # 指向本地支付服务器（生产环境应改为实际服务器地址）
        self.api_base = os.environ.get("BAIZE_API_BASE", "http://localhost:5000/api")
        self.product_id = "baize_ai_pro"  # 产品标识符
        
        # 本地临时支付会话存储（仅存储会话ID，不存储敏感信息）
        self.session_file = Path.home() / ".baize_payment_session.json"
        
    def create_checkout_session(self, hardware_fingerprint: str) -> Tuple[bool, str, Optional[str]]:
        """
        创建支付会话 - 通过安全服务器
        
        Args:
            hardware_fingerprint: 硬件指纹，用于绑定设备
            
        Returns:
            (成功状态, 消息, 支付链接)
        """
        try:
            # 生成本地会话ID
            local_session_id = str(uuid.uuid4())
            
            # 请求服务器创建支付会话
            payload = {
                "product_id": self.product_id,
                "hardware_fingerprint": hardware_fingerprint,
                "local_session_id": local_session_id,
                "client_version": "3.0.0",
                "timestamp": int(time.time())
            }
            
            response = requests.post(
                f"{self.api_base}/payment/create-checkout",
                json=payload,
                timeout=30,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                checkout_url = data.get("checkout_url")
                server_session_id = data.get("session_id")
                
                if checkout_url and server_session_id:
                    # 保存会话映射（不包含敏感信息）
                    self._save_session_mapping(local_session_id, server_session_id)
                    return True, "支付链接创建成功", checkout_url
                else:
                    return False, "支付链接获取失败", None
            else:
                try:
                    error_data = response.json()
                    error_msg = error_data.get("message", error_data.get("error", "创建支付会话失败"))
                    
                    # 为常见错误提供更友好的提示
                    if "Forbidden" in error_msg or "403" in str(response.status_code):
                        error_msg = f"支付系统配置错误，请联系客服。错误详情：{error_msg}"
                    elif "Unauthorized" in error_msg or "401" in str(response.status_code):
                        error_msg = f"支付系统认证失败，请联系客服。错误详情：{error_msg}"
                    elif response.status_code >= 500:
                        error_msg = f"支付服务器内部错误，请稍后重试。错误详情：{error_msg}"
                    
                    return False, error_msg, None
                except:
                    return False, f"创建支付会话失败 (HTTP {response.status_code})", None
                
        except requests.exceptions.RequestException as e:
            return False, f"网络连接失败，请检查网络: {str(e)}", None
        except Exception as e:
            return False, f"创建支付会话时发生错误: {str(e)}", None
    
    def check_payment_and_activate(self, hardware_fingerprint: str) -> Tuple[bool, str, Optional[str]]:
        """
        检查支付状态并自动激活
        
        Args:
            hardware_fingerprint: 硬件指纹
            
        Returns:
            (成功状态, 消息, 激活码)
        """
        try:
            # 获取所有本地会话
            session_mappings = self._load_session_mappings()
            
            if not session_mappings:
                return False, "没有待处理的支付会话", None
            
            # 检查每个会话的支付状态
            for local_session_id, server_session_id in session_mappings.items():
                success, message, activation_code = self._check_session_payment(
                    server_session_id, hardware_fingerprint
                )
                
                if success and activation_code:
                    # 清理已完成的会话
                    self._clear_session_mapping(local_session_id)
                    return True, "支付完成，激活码已生成", activation_code
                elif "expired" in message.lower():
                    # 清理过期会话
                    self._clear_session_mapping(local_session_id)
            
            return False, "支付尚未完成或已过期", None
            
        except Exception as e:
            return False, f"检查支付状态时发生错误: {str(e)}", None
    
    def verify_activation_code_with_server(self, activation_code: str, hardware_fingerprint: str) -> Tuple[bool, str]:
        """
        通过服务器验证激活码
        
        Args:
            activation_code: 激活码
            hardware_fingerprint: 硬件指纹
            
        Returns:
            (验证成功, 消息)
        """
        try:
            payload = {
                "key": activation_code,
                "instance_id": hardware_fingerprint
            }
            
            response = requests.post(
                f"{self.api_base}/license/validate",
                json=payload,
                timeout=30,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("valid", False):
                    return True, "许可证验证成功"
                else:
                    reason = data.get("reason", data.get("message", "许可证无效"))
                    return False, reason
            else:
                try:
                    error_data = response.json()
                    error_msg = error_data.get("message", error_data.get("error", "服务器验证失败"))
                except:
                    error_msg = f"服务器验证失败 (HTTP {response.status_code})"
                return False, error_msg
                
        except requests.exceptions.RequestException as e:
            return False, f"网络连接失败，请检查网络: {str(e)}"
        except Exception as e:
            return False, f"验证激活码时发生错误: {str(e)}"
    
    def _check_session_payment(self, server_session_id: str, hardware_fingerprint: str) -> Tuple[bool, str, Optional[str]]:
        """检查特定会话的支付状态"""
        try:
            payload = {
                "session_id": server_session_id,
                "hardware_fingerprint": hardware_fingerprint,
                "timestamp": int(time.time())
            }
            
            response = requests.post(
                f"{self.api_base}/payment/check-status",
                json=payload,
                timeout=30,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                status = data.get("status")
                
                if status == "completed":
                    activation_code = data.get("activation_code")
                    return True, "支付已完成", activation_code
                elif status == "pending":
                    return False, "支付待处理", None
                elif status == "expired":
                    return False, "支付会话已过期", None
                else:
                    return False, f"未知状态: {status}", None
            else:
                return False, "查询支付状态失败", None
                
        except Exception as e:
            return False, f"查询支付状态时发生错误: {str(e)}", None
    

    

    

    
    def _save_session_mapping(self, local_id: str, server_id: str):
        """保存会话映射"""
        try:
            mappings = self._load_session_mappings()
            mappings[local_id] = server_id
            
            with open(self.session_file, 'w', encoding='utf-8') as f:
                json.dump(mappings, f)
                
        except Exception as e:
            print(f"保存会话映射失败: {e}")
    
    def _load_session_mappings(self) -> Dict[str, str]:
        """加载会话映射"""
        try:
            if not self.session_file.exists():
                return {}
                
            with open(self.session_file, 'r', encoding='utf-8') as f:
                return json.load(f)
                
        except Exception as e:
            print(f"加载会话映射失败: {e}")
            return {}
    
    def _clear_session_mapping(self, local_id: str):
        """清理特定会话映射"""
        try:
            mappings = self._load_session_mappings()
            if local_id in mappings:
                del mappings[local_id]
                
                with open(self.session_file, 'w', encoding='utf-8') as f:
                    json.dump(mappings, f)
                    
        except Exception as e:
            print(f"清理会话映射失败: {e}")
    
    def cleanup_expired_sessions(self):
        """清理过期的会话映射"""
        try:
            # 简单的清理策略：删除超过24小时的本地会话文件
            if self.session_file.exists():
                file_age = time.time() - self.session_file.stat().st_mtime
                if file_age > 24 * 3600:  # 24小时
                    self.session_file.unlink()
                    
        except Exception as e:
            print(f"清理过期会话失败: {e}") 