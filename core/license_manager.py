#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
License Manager - 激活码管理模块
实现安全的买断制激活码验证机制
"""

import os
import json
import time
import hashlib
import platform
import subprocess
import uuid
import sys
from typing import Tuple, Optional, Dict, Any
from pathlib import Path
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import base64

class LicenseManager:
    """激活码管理器"""
    
    def __init__(self):
        self.app_name = "BaizeAI"
        self.version = "3.0.0"
        self.license_file = self._get_license_file_path()
        self.public_key = self._get_public_key()
        self.trial_days = 30  # 试用期天数
        
    def _is_no_activation_build(self) -> bool:
        """检查是否为免激活构建版本"""
        # 检查打包环境中的根目录
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            base_path = sys._MEIPASS
        else:
            # 检查开发环境中的项目根目录
            base_path = os.path.abspath(".")
        
        flag_file = os.path.join(base_path, 'no_activation.flag')
        return os.path.exists(flag_file)

    def _get_license_file_path(self) -> str:
        """获取许可证文件路径"""
        # 多个存储位置提高安全性
        base_paths = [
            os.path.expanduser("~/.baize_license"),
            os.path.join(os.environ.get('APPDATA', ''), 'BaizeAI', 'license.dat'),
            os.path.join(os.path.dirname(__file__), '..', 'data', 'license.dat')
        ]
        
        # 尝试找到已存在的许可证文件
        for path in base_paths:
            if os.path.exists(path):
                return path
        
        # 返回首选路径
        preferred_path = base_paths[1] if platform.system() == "Windows" else base_paths[0]
        os.makedirs(os.path.dirname(preferred_path), exist_ok=True)
        return preferred_path
    
    def _get_public_key(self) -> bytes:
        """获取RSA公钥 - 内嵌在代码中"""
        # 实际部署时应该用您的公钥替换
        public_key_pem = b"""-----BEGIN RSA PUBLIC KEY-----
MIIBCgKCAQEA2E8VJxKQ4dT8nF2kBnZQJ6VwW0b2U1FxYj0c3gHl8vK9qQ1mR2tS
8kL5B3xY4sG9pX7WzQ2dF6hG3vJ8kM5nL0sT1qV3uY8aZ9bD2cL7kF5yH4zI9rP0
xS6wE8tQ5jK3lU2mV9bN4vG0qS1dF2eL7pY8nR6kT3cH5zI2qV7bK9sL4tG3uH2v
B8cD5kF6gJ7pL9rS0tU3vX4yZ5aB1dE2fG3hI4jK5lM6nO7pQ8rS9tU0vW1xY2zA
3bC4dE5fG6hI7jK8lM9nO0pQ1rS2tU3vW4xY5zA6bC7dE8fG9hI0jK1lM2nO3pQw==
-----END RSA PUBLIC KEY-----"""
        return public_key_pem
    
    def _get_hardware_fingerprint(self) -> str:
        """获取硬件指纹"""
        try:
            # 收集硬件信息
            hw_info = []
            
            # CPU信息
            try:
                if platform.system() == "Windows":
                    result = subprocess.run(['wmic', 'cpu', 'get', 'ProcessorId', '/value'], 
                                          capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
                    for line in result.stdout.split('\n'):
                        if 'ProcessorId=' in line:
                            hw_info.append(line.split('=')[1].strip())
                else:
                    # Linux/Mac CPU信息
                    hw_info.append(str(os.cpu_count()))
            except:
                hw_info.append("unknown_cpu")
            
            # MAC地址
            try:
                mac = ':'.join(['{:02x}'.format((uuid.getnode() >> i) & 0xff) for i in range(0,8*6,8)][::-1])
                hw_info.append(mac)
            except:
                hw_info.append("unknown_mac")
            
            # 主板信息 (Windows)
            try:
                if platform.system() == "Windows":
                    result = subprocess.run(['wmic', 'baseboard', 'get', 'SerialNumber', '/value'], 
                                          capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
                    for line in result.stdout.split('\n'):
                        if 'SerialNumber=' in line:
                            hw_info.append(line.split('=')[1].strip())
            except:
                pass
            
            # 系统信息
            hw_info.append(platform.machine())
            hw_info.append(platform.system())
            
            # 生成指纹
            hw_string = '|'.join(filter(None, hw_info))
            return hashlib.sha256(hw_string.encode()).hexdigest()[:16]
            
        except Exception as e:
            print(f"获取硬件指纹失败: {e}")
            return hashlib.sha256(str(uuid.getnode()).encode()).hexdigest()[:16]
    
    def _encrypt_data(self, data: bytes, key: bytes) -> bytes:
        """AES加密数据"""
        iv = os.urandom(16)
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        
        # PKCS7 padding
        pad_len = 16 - (len(data) % 16)
        padded_data = data + bytes([pad_len] * pad_len)
        
        encrypted = encryptor.update(padded_data) + encryptor.finalize()
        return iv + encrypted
    
    def _decrypt_data(self, encrypted_data: bytes, key: bytes) -> Optional[bytes]:
        """AES解密数据"""
        try:
            iv = encrypted_data[:16]
            ciphertext = encrypted_data[16:]
            
            cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
            decryptor = cipher.decryptor()
            
            padded_data = decryptor.update(ciphertext) + decryptor.finalize()
            
            # Remove padding
            pad_len = padded_data[-1]
            return padded_data[:-pad_len]
        except:
            return None
    
    def _generate_license_key(self) -> bytes:
        """生成许可证加密密钥"""
        hw_fp = self._get_hardware_fingerprint()
        app_id = f"{self.app_name}_{self.version}"
        key_string = f"{hw_fp}_{app_id}"
        return hashlib.sha256(key_string.encode()).digest()
    
    def _verify_license_signature(self, license_data: str, signature: str) -> bool:
        """验证许可证签名"""
        try:
            # 加载公钥
            public_key = serialization.load_pem_public_key(
                self.public_key,
                backend=default_backend()
            )
            
            # 验证签名
            signature_bytes = base64.b64decode(signature.encode())
            public_key.verify(
                signature_bytes,
                license_data.encode(),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except Exception as e:
            print(f"签名验证失败: {e}")
            return False
    
    def validate_activation_code(self, activation_code: str) -> Tuple[bool, str]:
        """验证激活码 - 通过/api/license/validate接口验证"""
        try:
            # 基本格式检查 - 只支持Creem格式
            code_parts = activation_code.split("-")
            if len(code_parts) != 5:
                return False, "许可证密钥格式错误"
            
            # 检查是否为Creem格式：XXXXX-XXXXX-XXXXX-XXXXX-XXXXX
            is_creem_format = (
                all(len(part) == 5 for part in code_parts) and
                all(c.isalnum() or c == '-' for c in activation_code)
            )
            
            if not is_creem_format:
                return False, "许可证密钥格式错误"
            
            # 导入支付管理器进行服务器验证
            from .payment_manager import PaymentManager
            payment_manager = PaymentManager()
            
            # 通过/api/license/validate接口验证激活码
            hardware_fingerprint = self._get_hardware_fingerprint()
            is_valid, message = payment_manager.verify_activation_code_with_server(
                activation_code, hardware_fingerprint
            )
            
            if is_valid:
                # 服务器验证通过，保存激活信息
                activation_data = {
                    "code": activation_code,
                    "hardware_fingerprint": hardware_fingerprint,
                    "activated_at": int(time.time()),
                    "version": self.version,
                    "server_verified": True,
                    "type": "license_validate"
                }
                
                # 保存激活信息
                if self._save_license_data(activation_data):
                    return True, "激活成功"
                else:
                    return False, "保存激活信息失败"
            else:
                return False, message
                
        except Exception as e:
            return False, f"激活码验证失败: {str(e)}"
    
    def _save_license_data(self, license_data: Dict[str, Any]) -> bool:
        """保存许可证数据"""
        try:
            # 加密保存
            data_json = json.dumps(license_data)
            key = self._generate_license_key()
            encrypted_data = self._encrypt_data(data_json.encode(), key)
            
            # 保存到多个位置
            success = False
            for i in range(3):  # 尝试3个不同的路径
                try:
                    license_file = self.license_file.replace('.dat', f'_{i}.dat')
                    with open(license_file, 'wb') as f:
                        f.write(encrypted_data)
                    success = True
                except:
                    continue
            
            return success
        except Exception as e:
            print(f"保存许可证数据失败: {e}")
            return False
    
    def _load_license_data(self) -> Optional[Dict[str, Any]]:
        """加载许可证数据"""
        try:
            key = self._generate_license_key()
            
            # 尝试从多个位置加载
            for i in range(3):
                try:
                    license_file = self.license_file.replace('.dat', f'_{i}.dat')
                    if not os.path.exists(license_file):
                        continue
                        
                    with open(license_file, 'rb') as f:
                        encrypted_data = f.read()
                    
                    decrypted_data = self._decrypt_data(encrypted_data, key)
                    if decrypted_data:
                        return json.loads(decrypted_data.decode())
                except:
                    continue
            
            return None
        except Exception as e:
            print(f"加载许可证数据失败: {e}")
            return None
    
    def check_license_validity(self) -> Tuple[bool, str, Dict[str, Any]]:
        """
        检查许可证有效性
        返回: (is_valid, message, license_info)
        """
        # 检查是否为免激活版本
        if self._is_no_activation_build():
            return (True, "免激活版本", {
                "status": "activated",
                "type": "no_activation",
                "hardware_fingerprint": "N/A",
                "activated_at": "N/A"
            })

        # 尝试加载和验证现有的许可证
        license_data = self._load_license_data()
        
        if not license_data:
            # 检查试用期
            return self._check_trial_period()
        
        try:
            # 验证硬件指纹
            current_hw_fp = self._get_hardware_fingerprint()
            if license_data.get("hardware_fingerprint") != current_hw_fp:
                return False, "许可证与当前设备不匹配", {}
            
            # 验证版本
            if license_data.get("version") != self.version:
                return False, "许可证版本不匹配", {}
            
            # 许可证有效
            return True, "许可证有效", license_data
            
        except Exception as e:
            return False, f"许可证验证失败: {str(e)}", {}
    
    def _check_trial_period(self) -> Tuple[bool, str, Dict[str, Any]]:
        """检查试用期"""
        try:
            trial_file = self.license_file.replace('license.dat', 'trial.dat')
            
            if os.path.exists(trial_file):
                # 读取试用开始时间
                with open(trial_file, 'r') as f:
                    trial_start = float(f.read().strip())
                
                days_used = (time.time() - trial_start) / (24 * 3600)
                remaining_days = max(0, self.trial_days - days_used)
                
                if remaining_days > 0:
                    return True, f"试用期剩余 {int(remaining_days)} 天", {"trial": True, "remaining_days": int(remaining_days)}
                else:
                    return False, "试用期已结束，请购买激活码", {"trial": True, "expired": True}
            else:
                # 首次运行，创建试用期记录
                with open(trial_file, 'w') as f:
                    f.write(str(time.time()))
                
                return True, f"开始 {self.trial_days} 天试用期", {"trial": True, "remaining_days": self.trial_days}
                
        except Exception as e:
            return False, f"试用期检查失败: {str(e)}", {}
    
    def get_license_info(self) -> Dict[str, Any]:
        """获取许可证信息"""
        is_valid, message, data = self.check_license_validity()
        
        return {
            "is_valid": is_valid,
            "message": message,
            "data": data,
            "hardware_fingerprint": self._get_hardware_fingerprint(),
            "version": self.version
        }
    
    def activate_license(self, activation_code: str) -> Tuple[bool, str]:
        """激活许可证 - 使用/api/license/validate接口"""
        try:
            # 通过/api/license/validate接口验证和激活
            success, message = self.validate_activation_code(activation_code)
            return success, message
                
        except Exception as e:
            return False, f"激活许可证时发生错误: {str(e)}"
    
    def deactivate_license(self) -> bool:
        """停用许可证（用于转移到其他设备）"""
        try:
            # 删除许可证文件
            for i in range(3):
                license_file = self.license_file.replace('.dat', f'_{i}.dat')
                if os.path.exists(license_file):
                    os.remove(license_file)
            return True
        except:
            return False 