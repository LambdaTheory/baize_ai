#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
单实例管理模块
确保应用程序只运行一个实例，并支持进程间通信
"""

import sys
import os
import socket
import threading
import time
from PyQt5.QtCore import QObject, pyqtSignal, QTimer
from PyQt5.QtWidgets import QApplication


class SingleInstanceServer(QObject):
    """单实例服务器，接收来自其他实例的消息"""
    new_file_received = pyqtSignal(str)  # 新文件路径信号
    
    def __init__(self, port=12345):
        super().__init__()
        self.port = port
        self.server_socket = None
        self.running = False
        
    def start_server(self):
        """启动服务器"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind(('localhost', self.port))
            self.server_socket.listen(1)
            self.running = True
            
            # 在新线程中监听连接
            threading.Thread(target=self._listen_for_connections, daemon=True).start()
            print(f"[单实例] 服务器启动成功，监听端口 {self.port}")
            return True
            
        except Exception as e:
            print(f"[单实例] 服务器启动失败: {e}")
            return False
    
    def _listen_for_connections(self):
        """监听连接"""
        while self.running:
            try:
                client_socket, addr = self.server_socket.accept()
                threading.Thread(target=self._handle_client, args=(client_socket,), daemon=True).start()
            except Exception as e:
                if self.running:
                    print(f"[单实例] 监听连接时出错: {e}")
                break
    
    def _handle_client(self, client_socket):
        """处理客户端连接"""
        try:
            data = client_socket.recv(1024).decode('utf-8')
            if data.startswith('FILE:'):
                file_path = data[5:]  # 去掉 'FILE:' 前缀
                print(f"[单实例] 接收到文件路径: {file_path}")
                self.new_file_received.emit(file_path)
                client_socket.send(b'OK')
            else:
                print(f"[单实例] 接收到未知消息: {data}")
                client_socket.send(b'UNKNOWN')
        except Exception as e:
            print(f"[单实例] 处理客户端时出错: {e}")
        finally:
            client_socket.close()
    
    def stop_server(self):
        """停止服务器"""
        self.running = False
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass


class SingleInstanceClient:
    """单实例客户端，向已运行的实例发送消息"""
    
    def __init__(self, port=12345):
        self.port = port
    
    def send_file_path(self, file_path):
        """向已运行的实例发送文件路径"""
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.settimeout(5)  # 5秒超时
            client_socket.connect(('localhost', self.port))
            
            message = f'FILE:{file_path}'
            client_socket.send(message.encode('utf-8'))
            
            response = client_socket.recv(1024).decode('utf-8')
            client_socket.close()
            
            print(f"[单实例] 发送文件路径成功: {file_path}")
            return response == 'OK'
            
        except Exception as e:
            print(f"[单实例] 发送文件路径失败: {e}")
            return False
    
    def is_instance_running(self):
        """检查是否有实例正在运行"""
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.settimeout(2)  # 2秒超时
            result = client_socket.connect_ex(('localhost', self.port))
            client_socket.close()
            return result == 0
        except:
            return False


class SingleInstanceManager:
    """单实例管理器"""
    
    def __init__(self, app_name="白泽AI", port=12345):
        self.app_name = app_name
        self.port = port
        self.server = None
        self.client = SingleInstanceClient(port)
    
    def ensure_single_instance(self, file_path=None):
        """确保单实例运行
        
        Args:
            file_path: 要处理的文件路径（可选）
            
        Returns:
            tuple: (is_first_instance, should_continue)
                - is_first_instance: 是否为第一个实例
                - should_continue: 是否应该继续运行
        """
        if self.client.is_instance_running():
            # 已有实例在运行
            print(f"[单实例] 检测到已有实例运行")
            
            if file_path:
                # 发送文件路径给已运行的实例
                if self.client.send_file_path(file_path):
                    print(f"[单实例] 文件路径已发送给已运行的实例")
                    return False, False  # 不是第一个实例，不应该继续
                else:
                    print(f"[单实例] 发送失败，将启动新实例")
                    return True, True  # 发送失败，启动新实例
            else:
                # 没有文件路径，只是普通启动，激活已有实例
                print(f"[单实例] 尝试激活已有实例")
                # 发送一个空的激活信号
                self.client.send_file_path("")
                return False, False  # 不是第一个实例，不应该继续
        else:
            # 没有实例在运行，这是第一个实例
            print(f"[单实例] 这是第一个实例")
            return True, True  # 是第一个实例，应该继续
    
    def start_server(self):
        """启动服务器（仅第一个实例调用）"""
        self.server = SingleInstanceServer(self.port)
        return self.server.start_server()
    
    def get_server(self):
        """获取服务器实例"""
        return self.server
    
    def cleanup(self):
        """清理资源"""
        if self.server:
            self.server.stop_server()


# 全局单实例管理器
_instance_manager = None

def get_instance_manager():
    """获取全局单实例管理器"""
    global _instance_manager
    if _instance_manager is None:
        _instance_manager = SingleInstanceManager()
    return _instance_manager 

