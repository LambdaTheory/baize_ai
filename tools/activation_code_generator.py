#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
激活码生成器工具
用于服务器端生成和签名激活码

此工具应该在安全的服务器环境中运行，不应包含在客户端分发中。
"""

import os
import json
import time
import base64
import hashlib
import secrets
from typing import Dict, Any, Tuple
from pathlib import Path

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend


class ActivationCodeGenerator:
    """激活码生成器"""
    
    def __init__(self, keys_dir: str = "keys"):
        self.keys_dir = Path(keys_dir)
        self.keys_dir.mkdir(exist_ok=True)
        
        self.private_key_file = self.keys_dir / "private_key.pem"
        self.public_key_file = self.keys_dir / "public_key.pem"
        
        # 加载或生成密钥对
        self.private_key, self.public_key = self._load_or_generate_keys()
    
    def _load_or_generate_keys(self) -> Tuple[Any, Any]:
        """加载或生成RSA密钥对"""
        if self.private_key_file.exists() and self.public_key_file.exists():
            print("加载现有密钥对...")
            return self._load_keys()
        else:
            print("生成新的RSA密钥对...")
            return self._generate_keys()
    
    def _generate_keys(self) -> Tuple[Any, Any]:
        """生成新的RSA密钥对"""
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        public_key = private_key.public_key()
        
        # 保存私钥
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        with open(self.private_key_file, 'wb') as f:
            f.write(private_pem)
        
        # 保存公钥
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        with open(self.public_key_file, 'wb') as f:
            f.write(public_pem)
        
        print(f"密钥对已保存到: {self.keys_dir}")
        return private_key, public_key
    
    def _load_keys(self) -> Tuple[Any, Any]:
        """加载现有密钥对"""
        with open(self.private_key_file, 'rb') as f:
            private_key = serialization.load_pem_private_key(
                f.read(),
                password=None,
                backend=default_backend()
            )
        
        with open(self.public_key_file, 'rb') as f:
            public_key = serialization.load_pem_public_key(
                f.read(),
                backend=default_backend()
            )
        
        return private_key, public_key
    
    def get_public_key_pem(self) -> str:
        """获取公钥PEM格式字符串（用于嵌入客户端）"""
        public_pem = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return public_pem.decode('utf-8')
    
    def generate_activation_code(self, 
                               customer_email: str = None,
                               hardware_fingerprint: str = None,
                               expires_days: int = None,
                               max_activations: int = 1) -> Dict[str, Any]:
        """
        生成激活码
        
        Args:
            customer_email: 客户邮箱
            hardware_fingerprint: 硬件指纹（如果需要绑定特定设备）
            expires_days: 过期天数（None表示永不过期）
            max_activations: 最大激活次数
        
        Returns:
            包含激活码和元数据的字典
        """
        # 生成激活码ID
        code_id = self._generate_code_id()
        
        # 创建激活数据
        activation_data = {
            "code_id": code_id,
            "customer_email": customer_email,
            "hardware_fingerprint": hardware_fingerprint,
            "generated_at": int(time.time()),
            "expires_at": int(time.time() + expires_days * 24 * 3600) if expires_days else None,
            "max_activations": max_activations,
            "current_activations": 0,
            "version": "3.0.0",
            "product": "BaizeAI"
        }
        
        # 生成可读的激活码
        readable_code = self._generate_readable_code(code_id)
        
        # 对激活数据进行签名
        data_json = json.dumps(activation_data, sort_keys=True)
        signature = self._sign_data(data_json)
        
        result = {
            "activation_code": readable_code,
            "activation_data": activation_data,
            "signature": signature,
            "signed_data": data_json
        }
        
        # 保存激活码记录
        self._save_activation_record(result)
        
        return result
    
    def _generate_code_id(self) -> str:
        """生成唯一的激活码ID"""
        return secrets.token_hex(8).upper()
    
    def _generate_readable_code(self, code_id: str) -> str:
        """生成可读的激活码格式：BAIZE-XXXXX-XXXXX-XXXXX-XXXXX"""
        # 将code_id转换为5组字符
        # 添加校验位防止typo
        checksum = hashlib.md5(code_id.encode()).hexdigest()[:4].upper()
        
        # 格式化为 BAIZE-XXXXX-XXXXX-XXXXX-XXXXX
        parts = [
            "BAIZE",
            code_id[:4],
            code_id[4:8] + checksum[:1],
            checksum[1:] + code_id[8:12] if len(code_id) > 8 else checksum[1:],
            code_id[12:16] if len(code_id) > 12 else secrets.token_hex(2).upper()
        ]
        
        return "-".join(parts)
    
    def _sign_data(self, data: str) -> str:
        """对数据进行RSA签名"""
        signature = self.private_key.sign(
            data.encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return base64.b64encode(signature).decode()
    
    def _save_activation_record(self, record: Dict[str, Any]):
        """保存激活码记录"""
        records_file = self.keys_dir / "activation_records.json"
        
        # 加载现有记录
        if records_file.exists():
            with open(records_file, 'r', encoding='utf-8') as f:
                records = json.load(f)
        else:
            records = []
        
        # 添加新记录
        records.append({
            "activation_code": record["activation_code"],
            "code_id": record["activation_data"]["code_id"],
            "customer_email": record["activation_data"]["customer_email"],
            "generated_at": record["activation_data"]["generated_at"],
            "expires_at": record["activation_data"]["expires_at"],
            "max_activations": record["activation_data"]["max_activations"],
            "current_activations": record["activation_data"]["current_activations"]
        })
        
        # 保存记录
        with open(records_file, 'w', encoding='utf-8') as f:
            json.dump(records, f, indent=2, ensure_ascii=False)
    
    def verify_activation_code(self, activation_code: str) -> Tuple[bool, Dict[str, Any]]:
        """验证激活码（服务器端验证）"""
        try:
            # 从记录中查找激活码
            records_file = self.keys_dir / "activation_records.json"
            if not records_file.exists():
                return False, {"error": "激活码记录文件不存在"}
            
            with open(records_file, 'r', encoding='utf-8') as f:
                records = json.load(f)
            
            # 查找匹配的激活码
            matching_record = None
            for record in records:
                if record["activation_code"] == activation_code:
                    matching_record = record
                    break
            
            if not matching_record:
                return False, {"error": "激活码无效"}
            
            # 检查过期时间
            if matching_record["expires_at"] and time.time() > matching_record["expires_at"]:
                return False, {"error": "激活码已过期"}
            
            # 检查激活次数
            if matching_record["current_activations"] >= matching_record["max_activations"]:
                return False, {"error": "激活码已达到最大使用次数"}
            
            return True, matching_record
            
        except Exception as e:
            return False, {"error": f"验证激活码时出错: {str(e)}"}
    
    def activate_code(self, activation_code: str, hardware_fingerprint: str) -> Tuple[bool, str]:
        """激活代码（增加使用次数）"""
        is_valid, record = self.verify_activation_code(activation_code)
        
        if not is_valid:
            return False, record.get("error", "激活码验证失败")
        
        # 更新激活次数
        records_file = self.keys_dir / "activation_records.json"
        with open(records_file, 'r', encoding='utf-8') as f:
            records = json.load(f)
        
        # 更新记录
        for i, rec in enumerate(records):
            if rec["activation_code"] == activation_code:
                records[i]["current_activations"] += 1
                records[i]["last_activated_at"] = int(time.time())
                records[i]["hardware_fingerprint"] = hardware_fingerprint
                break
        
        # 保存更新的记录
        with open(records_file, 'w', encoding='utf-8') as f:
            json.dump(records, f, indent=2, ensure_ascii=False)
        
        return True, "激活成功"


def main():
    """主函数 - 命令行工具"""
    import argparse
    
    parser = argparse.ArgumentParser(description='激活码生成器')
    parser.add_argument('--generate', action='store_true', help='生成激活码')
    parser.add_argument('--email', type=str, help='客户邮箱')
    parser.add_argument('--expires', type=int, help='过期天数')
    parser.add_argument('--max-activations', type=int, default=1, help='最大激活次数')
    parser.add_argument('--verify', type=str, help='验证激活码')
    parser.add_argument('--list-keys', action='store_true', help='显示公钥（用于嵌入客户端）')
    
    args = parser.parse_args()
    
    generator = ActivationCodeGenerator()
    
    if args.list_keys:
        print("=== RSA公钥 (嵌入到客户端) ===")
        print(generator.get_public_key_pem())
        return
    
    if args.generate:
        print("=== 生成激活码 ===")
        result = generator.generate_activation_code(
            customer_email=args.email,
            expires_days=args.expires,
            max_activations=args.max_activations
        )
        
        print(f"激活码: {result['activation_code']}")
        print(f"客户邮箱: {result['activation_data']['customer_email']}")
        print(f"生成时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(result['activation_data']['generated_at']))}")
        if result['activation_data']['expires_at']:
            print(f"过期时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(result['activation_data']['expires_at']))}")
        print(f"最大激活次数: {result['activation_data']['max_activations']}")
        return
    
    if args.verify:
        print(f"=== 验证激活码: {args.verify} ===")
        is_valid, data = generator.verify_activation_code(args.verify)
        if is_valid:
            print("✅ 激活码有效")
            print(f"客户邮箱: {data.get('customer_email', 'N/A')}")
            print(f"当前激活次数: {data['current_activations']}/{data['max_activations']}")
        else:
            print("❌ 激活码无效")
            print(f"错误: {data.get('error', '未知错误')}")
        return
    
    print("请使用 --help 查看使用方法")


if __name__ == "__main__":
    main() 