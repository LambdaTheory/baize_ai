#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ComfyUI集成模块
实现与本地ComfyUI的集成功能，支持一键导入工作流
"""

import json
import requests
import base64
import os
import time
import uuid
import threading
from PIL import Image
from typing import Optional, Dict, Any, Tuple

try:
    import websocket
    WEBSOCKET_AVAILABLE = True
except ImportError:
    WEBSOCKET_AVAILABLE = False
    print("警告: websocket-client 未安装，WebSocket功能将不可用")


class ComfyUIIntegration:
    """ComfyUI集成器"""
    
    def __init__(self, host="127.0.0.1", port=8188, client_id=None):
        """
        初始化ComfyUI集成器
        
        Args:
            host: ComfyUI服务器地址
            port: ComfyUI服务器端口
            client_id: 客户端ID，如果为None则自动生成。建议使用浏览器的client_id以确保工作流能在浏览器中显示
        """
        self.host = host
        self.port = port
        self.base_url = f"http://{host}:{port}"
        
        # 使用提供的client_id或生成新的
        if client_id:
            self.client_id = client_id
        else:
            self.client_id = str(uuid.uuid4())
        
        # WebSocket URL包含client_id参数
        self.ws_url = f"ws://{host}:{port}/ws?clientId={self.client_id}"
        
        self.ws = None
        self.ws_connected = False
        self.ws_thread = None
        
        print(f"ComfyUI集成器初始化:")
        print(f"  服务器: {self.base_url}")
        print(f"  WebSocket: {self.ws_url}")
        print(f"  客户端ID: {self.client_id}")
        
    def check_comfyui_status(self) -> Tuple[bool, str]:
        """
        检查ComfyUI是否在运行
        
        Returns:
            Tuple[bool, str]: (是否运行, 状态消息)
        """
        try:
            response = requests.get(f"{self.base_url}/system_stats", timeout=3)
            if response.status_code == 200:
                stats = response.json()
                return True, f"ComfyUI运行中 (系统: {stats.get('system', {}).get('os', '未知')})"
            else:
                return False, f"ComfyUI响应异常 (状态码: {response.status_code})"
        except requests.exceptions.ConnectionError:
            return False, f"无法连接到ComfyUI ({self.base_url})"
        except requests.exceptions.Timeout:
            return False, "ComfyUI连接超时"
        except Exception as e:
            return False, f"检查ComfyUI状态时出错: {str(e)}"
    
    def extract_comfyui_workflow(self, image_path: str) -> Optional[Dict[str, Any]]:
        """
        从图片中提取ComfyUI工作流数据
        
        Args:
            image_path: 图片文件路径
            
        Returns:
            Dict: 包含 'prompt' 和 'workflow' 数据的字典，如果没有找到则返回None
        """
        try:
            with Image.open(image_path) as img:
                # 检查PNG文本块中的工作流数据
                if hasattr(img, 'text') and img.text:
                    print(f"PNG文本块键: {list(img.text.keys())}")
                    
                    result = {}
                    
                    # 查找 prompt 数据（用于执行工作流）
                    if 'prompt' in img.text:
                        try:
                            prompt_data = json.loads(img.text['prompt'])
                            if self._validate_workflow_data(prompt_data):
                                result['prompt'] = prompt_data
                                print(f"成功提取 prompt 数据")
                        except json.JSONDecodeError as e:
                            print(f"prompt 数据解析失败: {e}")
                    
                    # 查找 workflow 数据（用于界面展示）
                    if 'workflow' in img.text:
                        try:
                            workflow_data = json.loads(img.text['workflow'])
                            if isinstance(workflow_data, dict):
                                result['workflow'] = workflow_data
                                print(f"成功提取 workflow 数据")
                        except json.JSONDecodeError as e:
                            print(f"workflow 数据解析失败: {e}")
                    
                    # 如果找到了任何数据，返回结果
                    if result:
                        return result
                    
                    # 如果没有找到标准的 prompt/workflow，尝试其他键名
                    workflow_keys = ['Workflow', 'ComfyUI_Workflow']
                    for key in workflow_keys:
                        if key in img.text:
                            try:
                                raw_data = img.text[key]
                                print(f"从PNG文本块 '{key}' 中找到数据，长度: {len(raw_data)}")
                                
                                # 尝试解析JSON
                                workflow_data = json.loads(raw_data)
                                
                                # 验证工作流数据格式
                                if self._validate_workflow_data(workflow_data):
                                    print(f"成功从PNG文本块 '{key}' 中提取有效工作流数据")
                                    # 如果是 prompt 格式的数据，同时作为 prompt 和 workflow 使用
                                    return {'prompt': workflow_data, 'workflow': workflow_data}
                                else:
                                    print(f"PNG文本块 '{key}' 中的数据不是有效的ComfyUI工作流")
                                    
                            except json.JSONDecodeError as e:
                                print(f"PNG文本块 '{key}' JSON解析失败: {e}")
                                continue
                
                # 检查info字典
                if hasattr(img, 'info') and img.info:
                    print(f"PNG info键: {list(img.info.keys())}")
                    
                    for key in ['workflow', 'Workflow', 'prompt']:
                        if key in img.info:
                            try:
                                raw_data = img.info[key]
                                
                                if isinstance(raw_data, str):
                                    workflow_data = json.loads(raw_data)
                                else:
                                    workflow_data = raw_data
                                
                                # 验证工作流数据格式
                                if self._validate_workflow_data(workflow_data):
                                    print(f"成功从PNG info '{key}' 中提取有效工作流数据")
                                    return {'prompt': workflow_data, 'workflow': workflow_data}
                                else:
                                    print(f"PNG info '{key}' 中的数据不是有效的ComfyUI工作流")
                                    
                            except (json.JSONDecodeError, TypeError) as e:
                                print(f"PNG info '{key}' 解析失败: {e}")
                                continue
                
                print("图片中未找到有效的ComfyUI工作流数据")
                return None
                
        except Exception as e:
            print(f"提取工作流数据时出错: {e}")
            return None
    
    def _validate_workflow_data(self, data: Any) -> bool:
        """
        验证工作流数据是否为有效的ComfyUI格式
        
        Args:
            data: 待验证的数据
            
        Returns:
            bool: 是否为有效的工作流数据
        """
        try:
            if not isinstance(data, dict):
                return False
            
            # 检查是否包含节点数据
            node_count = 0
            for key, value in data.items():
                # 节点ID应该是数字字符串或数字
                if isinstance(key, (str, int)):
                    # 尝试将key转换为数字（ComfyUI节点ID格式）
                    try:
                        int(str(key))
                    except ValueError:
                        continue
                    
                    # 检查节点数据格式
                    if isinstance(value, dict):
                        # 必须包含class_type
                        if 'class_type' in value:
                            node_count += 1
                        # 如果有inputs，也要检查格式
                        if 'inputs' in value and not isinstance(value['inputs'], dict):
                            return False
            
            # 至少要有一个有效节点
            return node_count > 0
            
        except Exception as e:
            print(f"验证工作流数据时出错: {e}")
            return False
    
    def upload_image_to_comfyui(self, image_path: str) -> Optional[Dict[str, Any]]:
        """
        上传图片到ComfyUI
        
        Args:
            image_path: 图片文件路径
            
        Returns:
            Dict: 上传结果，包含image name等信息
        """
        try:
            url = f"{self.base_url}/upload/image"
            
            with open(image_path, 'rb') as f:
                files = {
                    'image': (os.path.basename(image_path), f, 'image/png'),
                    'type': (None, 'input'),
                    'subfolder': (None, ''),
                }
                
                response = requests.post(url, files=files, timeout=10)
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"图片上传成功: {result}")
                    return result
                else:
                    print(f"图片上传失败: {response.status_code} - {response.text}")
                    return None
                    
        except Exception as e:
            print(f"上传图片时出错: {e}")
            return None
    
    def queue_workflow(self, workflow: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        将工作流加入ComfyUI队列
        
        Args:
            workflow: 工作流数据
            
        Returns:
            Dict: 队列结果
        """
        try:
            url = f"{self.base_url}/prompt"
            
            payload = {
                "client_id": self.client_id,
                "prompt": workflow
            }
            
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                print(f"工作流加入队列成功: {result}")
                return result
            else:
                print(f"工作流加入队列失败: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"提交工作流时出错: {e}")
            return None
    
    def load_workflow_from_image(self, image_path: str) -> Tuple[bool, str]:
        """
        从图片文件中加载工作流到ComfyUI
        
        Args:
            image_path: 图片文件路径
            
        Returns:
            Tuple[bool, str]: (是否成功, 结果消息)
        """
        # 1. 检查ComfyUI状态
        is_running, status_msg = self.check_comfyui_status()
        if not is_running:
            return False, status_msg
        
        # 2. 提取工作流数据
        workflow_data = self.extract_comfyui_workflow(image_path)
        
        if not workflow_data:
            # 如果没有找到工作流，尝试从图片元数据生成基础工作流
            print("未找到工作流数据，尝试从图片参数生成基础工作流...")
            
            # 使用我们的图片信息读取器提取参数
            from .image_reader import ImageInfoReader
            reader = ImageInfoReader()
            image_info = reader.extract_info(image_path)
            
            if image_info:
                # 转换为ComfyUI工作流
                workflow = self.convert_sd_webui_to_comfyui_workflow(image_info)
                if workflow:
                    print("成功从图片参数生成基础ComfyUI工作流")
                    workflow_data = {'prompt': workflow}  # 转换为新格式
                else:
                    return False, "无法从图片参数生成ComfyUI工作流"
            else:
                return False, "图片中未找到任何AI生成参数"
        
        # 3. 上传图片（可选，某些工作流可能需要）
        upload_result = self.upload_image_to_comfyui(image_path)
        if upload_result:
            print(f"图片已上传到ComfyUI: {upload_result.get('name', '')}")
        
        # 4. 提交工作流（使用 prompt 数据）
        if 'prompt' in workflow_data:
            queue_result = self.queue_workflow(workflow_data['prompt'])
            if queue_result:
                prompt_id = queue_result.get('prompt_id', '')
                return True, f"工作流已成功导入ComfyUI (ID: {prompt_id})"
            else:
                return False, "工作流导入失败"
        else:
            return False, "工作流数据中缺少 prompt 信息，无法执行"
    
    def get_queue_status(self) -> Optional[Dict[str, Any]]:
        """
        获取ComfyUI队列状态
        
        Returns:
            Dict: 队列状态信息
        """
        try:
            response = requests.get(f"{self.base_url}/queue", timeout=5)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"获取队列状态时出错: {e}")
            return None
    
    def get_history(self, prompt_id: str = None) -> Optional[Dict[str, Any]]:
        """
        获取ComfyUI历史记录
        
        Args:
            prompt_id: 特定的prompt ID，如果为None则获取所有历史
            
        Returns:
            Dict: 历史记录
        """
        try:
            url = f"{self.base_url}/history"
            if prompt_id:
                url += f"/{prompt_id}"
                
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"获取历史记录时出错: {e}")
            return None
    
    def open_comfyui_in_browser(self):
        """在浏览器中打开ComfyUI界面"""
        import webbrowser
        try:
            webbrowser.open(self.base_url)
            return True, f"已在浏览器中打开ComfyUI ({self.base_url})"
        except Exception as e:
            return False, f"打开浏览器失败: {str(e)}"
    
    def convert_sd_webui_to_comfyui_workflow(self, sd_params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        尝试将Stable Diffusion WebUI参数转换为ComfyUI工作流
        这是一个基础的转换函数，可能需要根据具体需求调整
        
        Args:
            sd_params: SD WebUI参数
            
        Returns:
            Dict: ComfyUI工作流（基础模板）
        """
        try:
            # 创建一个基础的ComfyUI工作流模板
            workflow = {
                "1": {
                    "inputs": {
                        "text": sd_params.get('prompt', ''),
                        "clip": ["4", 1]
                    },
                    "class_type": "CLIPTextEncode",
                    "_meta": {"title": "CLIP Text Encode (Prompt)"}
                },
                "2": {
                    "inputs": {
                        "text": sd_params.get('negative_prompt', ''),
                        "clip": ["4", 1]
                    },
                    "class_type": "CLIPTextEncode",
                    "_meta": {"title": "CLIP Text Encode (Negative)"}
                },
                "3": {
                    "inputs": {
                        "seed": int(sd_params.get('seed', -1)),
                        "steps": int(sd_params.get('steps', 20)),
                        "cfg": float(sd_params.get('cfg_scale', 7.0)),
                        "sampler_name": sd_params.get('sampler', 'euler'),
                        "scheduler": "normal",
                        "positive": ["1", 0],
                        "negative": ["2", 0],
                        "latent_image": ["5", 0],
                        "model": ["4", 0]
                    },
                    "class_type": "KSampler",
                    "_meta": {"title": "KSampler"}
                },
                "4": {
                    "inputs": {
                        "ckpt_name": sd_params.get('model', 'sd_xl_base_1.0.safetensors')
                    },
                    "class_type": "CheckpointLoaderSimple",
                    "_meta": {"title": "Load Checkpoint"}
                },
                "5": {
                    "inputs": {
                        "width": int(sd_params.get('width', 1024)),
                        "height": int(sd_params.get('height', 1024)),
                        "batch_size": 1
                    },
                    "class_type": "EmptyLatentImage",
                    "_meta": {"title": "Empty Latent Image"}
                },
                "6": {
                    "inputs": {
                        "samples": ["3", 0],
                        "vae": ["4", 2]
                    },
                    "class_type": "VAEDecode",
                    "_meta": {"title": "VAE Decode"}
                },
                "7": {
                    "inputs": {
                        "filename_prefix": "ComfyUI",
                        "images": ["6", 0]
                    },
                    "class_type": "SaveImage",
                    "_meta": {"title": "Save Image"}
                }
            }
            
            return workflow
            
        except Exception as e:
            print(f"转换工作流时出错: {e}")
            return None
    
    def connect_websocket(self) -> bool:
        """
        连接到ComfyUI的WebSocket
        
        Returns:
            bool: 连接是否成功
        """
        if not WEBSOCKET_AVAILABLE:
            print("WebSocket功能不可用，请安装 websocket-client")
            return False
        
        try:
            def on_open(ws):
                print("WebSocket连接已建立")
                self.ws_connected = True
            
            def on_close(ws, close_status_code, close_msg):
                print("WebSocket连接已关闭")
                self.ws_connected = False
            
            def on_error(ws, error):
                print(f"WebSocket错误: {error}")
                self.ws_connected = False
            
            def on_message(ws, message):
                # 处理来自ComfyUI的消息
                try:
                    data = json.loads(message)
                    print(f"收到消息: {data.get('type', 'unknown')}")
                except:
                    pass
            
            # 创建WebSocket连接
            self.ws = websocket.WebSocketApp(
                self.ws_url,
                on_open=on_open,
                on_close=on_close,
                on_error=on_error,
                on_message=on_message
            )
            
            # 在后台线程中运行WebSocket
            def run_ws():
                self.ws.run_forever()
            
            ws_thread = threading.Thread(target=run_ws, daemon=True)
            ws_thread.start()
            
            # 等待连接建立
            for _ in range(50):  # 等待最多5秒
                if self.ws_connected:
                    return True
                time.sleep(0.1)
            
            print("WebSocket连接超时")
            return False
            
        except Exception as e:
            print(f"WebSocket连接失败: {e}")
            return False
    
    def disconnect_websocket(self):
        """断开WebSocket连接"""
        try:
            if self.ws:
                self.ws.close()
            self.ws_connected = False
            if self.ws_thread and self.ws_thread.is_alive():
                self.ws_thread.join(timeout=2)
            print("WebSocket连接已断开")
        except Exception as e:
            print(f"断开WebSocket连接时出错: {e}")
    
    def load_workflow_via_websocket(self, workflow_data: Dict[str, Any]) -> bool:
        """
        通过WebSocket加载工作流到ComfyUI
        
        Args:
            workflow_data: 包含 'prompt' 和 'workflow' 数据的字典
            
        Returns:
            bool: 是否成功发送
        """
        if not WEBSOCKET_AVAILABLE:
            print("WebSocket功能不可用")
            return False
        
        try:
            print(f"开始通过WebSocket加载工作流，当前client_id: {self.client_id}")
            
            # 确保WebSocket连接
            if not self.ws_connected:
                print("WebSocket未连接，尝试重新连接...")
                if not self.connect_websocket():
                    print("WebSocket连接失败")
                    return False
                    
            print("WebSocket连接正常")
            
            # 优先使用workflow数据（用于界面展示）
            if 'workflow' in workflow_data and workflow_data['workflow']:
                workflow_json = workflow_data['workflow']
                print(f"使用workflow数据，节点数量: {len(workflow_json) if isinstance(workflow_json, dict) else 'unknown'}")
                
                # 发送load_workflow消息（使用ComfyUI标准格式）
                load_message = {
                    "type": "execution",
                    "data": {
                        "type": "load_workflow",
                        "workflow": workflow_json,
                        "client_id": self.client_id
                    }
                }
                
                print(f"发送工作流加载消息到client_id: {self.client_id}")
                print(f"工作流数据大小: {len(json.dumps(workflow_json))} 字符")
                
                self.ws.send(json.dumps(load_message))
                print("工作流数据已通过WebSocket发送到ComfyUI")
                
                # 发送一个额外的消息来确保界面更新
                refresh_message = {
                    "type": "client_update",
                    "client_id": self.client_id,
                    "data": {
                        "workflow": workflow_json
                    }
                }
                time.sleep(0.1)  # 稍等一下
                self.ws.send(json.dumps(refresh_message))
                print("发送界面刷新消息")
                
                return True
                
            # 如果没有workflow数据，使用prompt数据
            elif 'prompt' in workflow_data and workflow_data['prompt']:
                prompt_json = workflow_data['prompt']
                print(f"使用prompt数据，节点数量: {len(prompt_json) if isinstance(prompt_json, dict) else 'unknown'}")
                
                # 对于prompt数据，尝试转换为workflow格式或直接使用
                # ComfyUI的prompt格式通常可以直接作为workflow使用
                load_message = {
                    "type": "execution", 
                    "data": {
                        "type": "load_workflow",
                        "workflow": prompt_json,
                        "client_id": self.client_id
                    }
                }
                
                print(f"发送prompt工作流到client_id: {self.client_id}")
                self.ws.send(json.dumps(load_message))
                print("Prompt数据已通过WebSocket发送到ComfyUI")
                return True
            
            else:
                print("错误: 工作流数据中没有找到有效的workflow或prompt数据")
                print(f"可用的键: {list(workflow_data.keys())}")
                return False
                
        except Exception as e:
            print(f"通过WebSocket加载工作流时出错: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def load_workflow_from_image_via_websocket(self, image_path: str) -> Tuple[bool, str]:
        """
        从图片提取工作流并通过WebSocket加载到ComfyUI
        
        Args:
            image_path: 图片文件路径
            
        Returns:
            Tuple[bool, str]: (是否成功, 状态消息)
        """
        try:
            # 1. 检查ComfyUI状态
            is_running, status_msg = self.check_comfyui_status()
            if not is_running:
                return False, f"ComfyUI未运行: {status_msg}"
            
            # 2. 提取工作流数据
            workflow_data = self.extract_comfyui_workflow(image_path)
            if not workflow_data:
                return False, "图片中未找到有效的ComfyUI工作流数据"
            
            # 3. 通过WebSocket加载工作流
            if self.load_workflow_via_websocket(workflow_data):
                return True, "工作流已成功加载到ComfyUI界面"
            else:
                return False, "WebSocket加载工作流失败"
                
        except Exception as e:
            return False, f"加载工作流时出错: {str(e)}"

    def get_browser_client_id(self) -> Optional[str]:
        """
        尝试获取浏览器当前使用的client_id
        
        Returns:
            str: 浏览器的client_id，如果获取失败则返回None
        """
        try:
            print("正在尝试获取浏览器的client_id...")
            
            # 方法1：通过WebSocket连接监听获取活跃的client_id
            # 创建一个临时的WebSocket连接来监听活跃的客户端
            import websocket
            import threading
            import time
            
            active_clients = set()
            monitor_complete = False
            
            def on_message_monitor(ws, message):
                nonlocal active_clients, monitor_complete
                try:
                    data = json.loads(message)
                    # 查找包含client_id的消息
                    if isinstance(data, dict) and 'client_id' in data:
                        client_id = data['client_id']
                        active_clients.add(client_id)
                        print(f"监听到活跃client_id: {client_id}")
                except:
                    pass
            
            def on_error_monitor(ws, error):
                print(f"WebSocket监听出错: {error}")
            
            def on_close_monitor(ws, close_status_code, close_msg):
                nonlocal monitor_complete
                monitor_complete = True
            
            def on_open_monitor(ws):
                print("WebSocket监听连接已建立")
                # 发送一个测试消息来触发响应
                test_message = {
                    "type": "get_queue",
                    "client_id": "monitor_temp"
                }
                ws.send(json.dumps(test_message))
            
            # 创建监听WebSocket连接
            monitor_ws_url = f"ws://{self.host}:{self.port}/ws"
            monitor_ws = websocket.WebSocketApp(
                monitor_ws_url,
                on_message=on_message_monitor,
                on_error=on_error_monitor,
                on_close=on_close_monitor,
                on_open=on_open_monitor
            )
            
            # 在后台线程中运行监听，设置超时
            monitor_thread = threading.Thread(target=monitor_ws.run_forever)
            monitor_thread.daemon = True
            monitor_thread.start()
            
            # 等待2秒收集活跃客户端
            time.sleep(2)
            monitor_ws.close()
            
            # 如果监听到活跃客户端，返回最新的
            if active_clients:
                latest_client = max(active_clients)  # 获取最新的client_id
                print(f"通过WebSocket监听获取到client_id: {latest_client}")
                return latest_client
            
            # 方法2：通过/system_stats API获取活跃连接信息
            print("WebSocket监听未获取到client_id，尝试API方式...")
            response = requests.get(f"{self.base_url}/system_stats", timeout=5)
            if response.status_code == 200:
                stats = response.json()
                print(f"系统状态: {stats}")
                # 检查是否有活跃的WebSocket连接
                if 'websocket_connections' in stats and stats['websocket_connections'] > 0:
                    print(f"检测到 {stats['websocket_connections']} 个活跃的WebSocket连接")
            
            # 方法3：通过/queue API获取最近的client_id
            queue_response = requests.get(f"{self.base_url}/queue", timeout=5)
            if queue_response.status_code == 200:
                queue_data = queue_response.json()
                print(f"队列数据: {queue_data}")
                
                # 检查运行中的任务
                if 'queue_running' in queue_data and queue_data['queue_running']:
                    for item in queue_data['queue_running']:
                        if isinstance(item, list) and len(item) > 1 and isinstance(item[1], dict):
                            client_id = item[1].get('client_id')
                            if client_id:
                                print(f"从运行队列中找到client_id: {client_id}")
                                return client_id
                
                # 检查等待中的任务
                if 'queue_pending' in queue_data and queue_data['queue_pending']:
                    for item in queue_data['queue_pending']:
                        if isinstance(item, list) and len(item) > 1 and isinstance(item[1], dict):
                            client_id = item[1].get('client_id')
                            if client_id:
                                print(f"从等待队列中找到client_id: {client_id}")
                                return client_id
            
            # 方法4：通过/history API获取最近的client_id
            history_response = requests.get(f"{self.base_url}/history", timeout=5)
            if history_response.status_code == 200:
                history_data = history_response.json()
                if history_data:
                    # 获取最新的历史记录
                    latest_key = max(history_data.keys())
                    latest_item = history_data[latest_key]
                    if 'client_id' in latest_item:
                        client_id = latest_item['client_id']
                        print(f"从历史记录中找到client_id: {client_id}")
                        return client_id
            
            print("未能自动获取浏览器的client_id")
            return None
            
        except Exception as e:
            print(f"获取浏览器client_id时出错: {e}")
            import traceback
            traceback.print_exc()
            return None

    def set_client_id(self, client_id: str):
        """
        设置客户端ID并更新WebSocket URL
        
        Args:
            client_id: 新的客户端ID
        """
        self.client_id = client_id
        self.ws_url = f"ws://{self.host}:{self.port}/ws?clientId={self.client_id}"
        print(f"客户端ID已更新: {self.client_id}")
        print(f"WebSocket URL已更新: {self.ws_url}")
        
        # 如果当前有WebSocket连接，需要重新连接
        if self.ws_connected:
            print("检测到活跃的WebSocket连接，将重新连接...")
            self.disconnect_websocket()
            time.sleep(1)  # 等待断开完成
            self.connect_websocket()

    def clear_workflow(self) -> bool:
        """
        清空当前工作流
        
        Returns:
            bool: 是否成功发送清空消息
        """
        if not WEBSOCKET_AVAILABLE:
            print("WebSocket功能不可用")
            return False
        
        try:
            # 确保WebSocket连接
            if not self.ws_connected:
                if not self.connect_websocket():
                    return False
            
            message = {
                "type": "clear_workflow",
                "client_id": self.client_id
            }
            
            self.ws.send(json.dumps(message))
            print(f"已发送清空工作流消息到client_id: {self.client_id}")
            return True
            
        except Exception as e:
            print(f"清空工作流时出错: {e}")
            return False

    def verify_client_id(self, client_id: str) -> Tuple[bool, str]:
        """
        验证指定的client_id是否有效
        
        Args:
            client_id: 要验证的客户端ID
            
        Returns:
            Tuple[bool, str]: (是否有效, 验证结果信息)
        """
        try:
            # 临时设置client_id进行测试
            original_client_id = self.client_id
            self.set_client_id(client_id)
            
            # 尝试连接WebSocket并发送测试消息
            if not self.ws_connected:
                if not self.connect_websocket():
                    self.client_id = original_client_id
                    return False, "无法建立WebSocket连接"
            
            # 发送一个测试消息
            test_message = {
                "type": "client_test",
                "client_id": client_id,
                "data": "ping"
            }
            
            self.ws.send(json.dumps(test_message))
            print(f"已向client_id {client_id} 发送测试消息")
            
            # 恢复原来的client_id
            self.client_id = original_client_id
            
            return True, f"client_id {client_id} 验证成功，WebSocket连接正常"
            
        except Exception as e:
            # 恢复原来的client_id
            self.client_id = original_client_id
            return False, f"验证client_id时出错: {str(e)}"
    
    def send_workflow_with_multiple_formats(self, workflow_data: Dict[str, Any]) -> bool:
        """
        使用多种格式发送工作流数据，提高成功率
        
        Args:
            workflow_data: 工作流数据
            
        Returns:
            bool: 是否成功发送
        """
        if not WEBSOCKET_AVAILABLE or not self.ws_connected:
            return False
            
        try:
            workflow_json = workflow_data.get('workflow') or workflow_data.get('prompt')
            if not workflow_json:
                return False
            
            # 格式1：标准的load_workflow格式
            format1_message = {
                "type": "load_workflow",
                "workflow": workflow_json,
                "client_id": self.client_id
            }
            
            # 格式2：execution格式
            format2_message = {
                "type": "execution",
                "data": {
                    "type": "load_workflow", 
                    "workflow": workflow_json,
                    "client_id": self.client_id
                }
            }
            
            # 格式3：直接发送工作流数据
            format3_message = {
                "type": "workflow_data",
                "client_id": self.client_id,
                "workflow": workflow_json
            }
            
            print(f"尝试发送工作流数据 (格式1: load_workflow)")
            self.ws.send(json.dumps(format1_message))
            time.sleep(0.2)
            
            print(f"尝试发送工作流数据 (格式2: execution)")
            self.ws.send(json.dumps(format2_message))
            time.sleep(0.2)
            
            print(f"尝试发送工作流数据 (格式3: workflow_data)")
            self.ws.send(json.dumps(format3_message))
            
            print("已尝试使用3种格式发送工作流数据")
            return True
            
        except Exception as e:
            print(f"发送工作流时出错: {e}")
            return False

    def load_workflow_from_database_record(self, record_data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        从数据库记录中加载工作流到ComfyUI
        
        Args:
            record_data: 数据库记录数据，包含workflow_data字段
            
        Returns:
            Tuple[bool, str]: (是否成功, 结果消息)
        """
        try:
            # 1. 检查ComfyUI状态
            is_running, status_msg = self.check_comfyui_status()
            if not is_running:
                return False, status_msg
            
            # 2. 从记录中获取workflow数据
            workflow_data_str = record_data.get('workflow_data', '')
            if not workflow_data_str:
                return False, "该记录中未找到ComfyUI工作流数据"
            
            try:
                # 解析workflow数据
                import json
                workflow_data = json.loads(workflow_data_str)
                
                # 验证工作流数据格式
                if not self._validate_workflow_data(workflow_data):
                    return False, "工作流数据格式无效"
                
                # 构造标准格式的workflow数据
                formatted_workflow = {
                    'prompt': workflow_data,
                    'workflow': workflow_data
                }
                
                # 3. 通过WebSocket加载工作流
                if self.load_workflow_via_websocket(formatted_workflow):
                    return True, "工作流已成功从数据库记录加载到ComfyUI界面"
                else:
                    # 如果WebSocket失败，尝试HTTP方式
                    queue_result = self.queue_workflow(workflow_data)
                    if queue_result:
                        prompt_id = queue_result.get('prompt_id', '')
                        return True, f"工作流已成功导入ComfyUI队列 (ID: {prompt_id})"
                    else:
                        return False, "工作流加载失败"
                        
            except json.JSONDecodeError as e:
                return False, f"工作流数据解析失败: {str(e)}"
                
        except Exception as e:
            return False, f"加载工作流时出错: {str(e)}"


# 全局实例 - 移除全局实例初始化
# comfyui_integration = ComfyUIIntegration() 