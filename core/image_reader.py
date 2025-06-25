#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图片生成信息读取模块
支持从PNG、JPG文件中提取AI生成信息
"""

import json
import re
import os
from PIL import Image
from PIL.PngImagePlugin import PngInfo


class ImageInfoReader:
    """图片信息读取器"""
    
    def __init__(self):
        self.supported_formats = ['.png', '.jpg', '.jpeg']
    
    def extract_info(self, file_path):
        """
        从图片文件中提取生成信息
        
        Args:
            file_path (str): 图片文件路径
            
        Returns:
            dict: 提取的信息字典，如果没有信息则返回None
        """
        try:
            # 检查文件是否存在
            if not os.path.exists(file_path):
                print(f"文件不存在: {file_path}")
                return None
            
            # 获取文件扩展名
            file_ext = file_path.lower().split('.')[-1]
            
            print(f"正在处理文件: {file_path}")
            print(f"文件格式: {file_ext}")
            
            if file_ext == 'png':
                return self._extract_from_png(file_path)
            elif file_ext in ['jpg', 'jpeg']:
                return self._extract_from_jpg(file_path)
            else:
                print(f"不支持的文件格式: {file_ext}")
                return None
                
        except Exception as e:
            print(f"提取图片信息时出错: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _extract_from_png(self, file_path):
        """从PNG文件中提取信息"""
        try:
            with Image.open(file_path) as img:
                print(f"PNG图片格式: {img.format}")
                print(f"PNG图片尺寸: {img.size}")
                
                # 检查PNG文本块
                if hasattr(img, 'text') and img.text:
                    print(f"PNG文本块数量: {len(img.text)}")
                    print(f"PNG文本块键: {list(img.text.keys())}")
                    
                    # 常见的AI生成信息字段
                    info_keys = ['parameters', 'Parameters', 'prompt', 'Prompt', 
                               'workflow', 'Workflow', 'generation_info']
                    
                    for key in info_keys:
                        if key in img.text:
                            raw_text = img.text[key]
                            print(f"找到PNG文本块 '{key}': {raw_text[:100]}...")  # 只显示前100字符
                            result = self._parse_parameters(raw_text)
                            if result:
                                return result
                
                # 检查info字典
                if hasattr(img, 'info') and img.info:
                    print(f"PNG info字典数量: {len(img.info)}")
                    print(f"PNG info字典键: {list(img.info.keys())}")
                    
                    for key in ['parameters', 'Parameters']:
                        if key in img.info:
                            raw_text = img.info[key]
                            print(f"找到PNG info '{key}': {raw_text[:100]}...")  # 只显示前100字符
                            result = self._parse_parameters(raw_text)
                            if result:
                                return result
                
                print("PNG文件中未找到AI生成信息")
                return None
                
        except Exception as e:
            print(f"读取PNG文件出错: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _extract_from_jpg(self, file_path):
        """从JPG文件中提取信息"""
        try:
            with Image.open(file_path) as img:
                # 获取EXIF信息（新版本PIL推荐方式）
                exif_dict = None
                try:
                    from PIL.ExifTags import TAGS
                    if hasattr(img, 'getexif'):
                        exif_dict = img.getexif()
                    elif hasattr(img, '_getexif'):
                        exif_dict = img._getexif()
                except ImportError:
                    pass
                
                if exif_dict:
                    # 用户注释字段(0x9286)可能包含生成信息
                    user_comment = exif_dict.get(0x9286)
                    if user_comment:
                        try:
                            # 尝试解码
                            if isinstance(user_comment, bytes):
                                comment_text = user_comment.decode('utf-8', errors='ignore')
                            else:
                                comment_text = str(user_comment)
                            return self._parse_parameters(comment_text)
                        except:
                            pass
                    
                    # 检查其他可能的字段
                    for tag_id, value in exif_dict.items():
                        if isinstance(value, (str, bytes)):
                            try:
                                if isinstance(value, bytes):
                                    text = value.decode('utf-8', errors='ignore')
                                else:
                                    text = str(value)
                                
                                if any(keyword in text.lower() for keyword in ['prompt', 'steps', 'sampler', 'model']):
                                    result = self._parse_parameters(text)
                                    if result:
                                        return result
                            except:
                                continue
                
                # 尝试其他元数据字段
                if hasattr(img, 'info'):
                    for key, value in img.info.items():
                        if isinstance(value, str) and any(keyword in value.lower() 
                                                        for keyword in ['prompt', 'steps', 'sampler', 'model']):
                            return self._parse_parameters(value)
                
                return None
                
        except Exception as e:
            print(f"读取JPG文件出错: {e}")
            return None
    
    def _parse_parameters(self, raw_text):
        """
        解析参数文本
        
        Args:
            raw_text (str): 原始参数文本
            
        Returns:
            dict: 解析后的参数字典
        """
        if not raw_text:
            return None
        
        try:
            # 尝试解析JSON格式
            if raw_text.strip().startswith('{'):
                try:
                    data = json.loads(raw_text)
                    # 检查是否为ComfyUI格式 (key通常是数字ID)
                    if isinstance(data, dict) and any(key.isdigit() for key in data.keys()):
                        parsed_data = self._parse_comfyui_json(data)
                        if parsed_data:
                            parsed_data['generation_source'] = 'ComfyUI'
                            # 保存原始的workflow数据
                            parsed_data['workflow_data'] = data
                            return parsed_data
                    
                    normalized_data = self._normalize_json_data(data)
                    if normalized_data:
                        normalized_data['generation_source'] = 'Unknown'
                        return normalized_data
                except json.JSONDecodeError:
                    pass
            
            # 解析常见的参数格式
            info = {}
            
            # 处理常见的参数格式（如Stable Diffusion WebUI）
            lines = raw_text.split('\n')
            
            # 第一行通常是prompt
            if lines:
                first_line = lines[0].strip()
                if first_line and not any(keyword in first_line.lower() 
                                        for keyword in ['negative prompt', 'steps:', 'sampler:', 'model:']):
                    info['prompt'] = first_line
            
            # 查找各种参数
            full_text = raw_text.lower()
            
            # Negative prompt
            neg_prompt_match = re.search(r'negative prompt:?\s*([^\n]*?)(?=\n|$|steps:|sampler:|model:|cfg scale:)', 
                                       raw_text, re.IGNORECASE | re.DOTALL)
            if neg_prompt_match:
                info['negative_prompt'] = neg_prompt_match.group(1).strip()
            
            # Steps
            steps_match = re.search(r'steps:?\s*(\d+)', raw_text, re.IGNORECASE)
            if steps_match:
                info['steps'] = int(steps_match.group(1))
            
            # Sampler
            sampler_match = re.search(r'sampler:?\s*([^\n,]*?)(?=,|\n|$|steps:|cfg scale:)', 
                                    raw_text, re.IGNORECASE)
            if sampler_match:
                info['sampler'] = sampler_match.group(1).strip()
            
            # CFG Scale
            cfg_match = re.search(r'cfg scale:?\s*([\d.]+)', raw_text, re.IGNORECASE)
            if cfg_match:
                info['cfg_scale'] = float(cfg_match.group(1))
            
            # Seed
            seed_match = re.search(r'seed:?\s*(\d+)', raw_text, re.IGNORECASE)
            if seed_match:
                info['seed'] = int(seed_match.group(1))
            
            # Model - 优先匹配模型名称，避免hash值
            model_found = False
            
            # 使用更精确的正则表达式来分别匹配model和model hash
            # 先查找完整的model字段，然后排除model hash部分
            
            # 方法1：查找"Model: "后面跟着的完整模型名称（直到遇到", "或换行）
            model_pattern = r'Model:\s*([^,\n]+?)(?=\s*,\s*(?:Denoising|RNG|Lora|vae_name)|\n|$)'
            model_match = re.search(model_pattern, raw_text, re.IGNORECASE)
            
            if model_match:
                model_name = model_match.group(1).strip()
                # 确保不是hash值（检查是否包含中文或文件扩展名）
                if ('.' in model_name and model_name.endswith('.safetensors')) or \
                   any('\u4e00' <= char <= '\u9fff' for char in model_name) or \
                   len(model_name) > 10:  # 真实模型名通常比较长
                    info['model'] = model_name
                    model_found = True
            
            # 方法2：如果上面没找到，尝试其他模式
            if not model_found:
                other_patterns = [
                    r'checkpoint:?\s*([^\n,]*?)(?=,|\n|$)',
                    r'model name:?\s*([^\n,]*?)(?=,|\n|$)'
                ]
                
                for pattern in other_patterns:
                    model_match = re.search(pattern, raw_text, re.IGNORECASE)
                    if model_match:
                        model_name = model_match.group(1).strip()
                        if model_name and len(model_name) > 5:  # 避免短的hash值
                            info['model'] = model_name
                            model_found = True
                            break
            
            # 如果仍然没找到模型名称，才使用hash作为备选
            if not model_found:
                hash_pattern = r'model hash:?\s*([^\n,]+?)(?=,|\n|$)'
                hash_match = re.search(hash_pattern, raw_text, re.IGNORECASE)
                if hash_match:
                    hash_value = hash_match.group(1).strip()
                    info['model'] = f"Hash: {hash_value}"
            
            # Lora信息提取
            lora_info = self._extract_lora_info(raw_text)
            if lora_info:
                info['lora_info'] = lora_info
            
            # 检测生成来源
            if any(keyword in raw_text.lower() for keyword in ['model:', 'steps:', 'sampler:', 'cfg scale:', 'seed:']):
                info['generation_source'] = 'Stable Diffusion WebUI'
            else:
                info['generation_source'] = 'Unknown'
            
            # 如果没有解析到任何信息，返回原始文本作为prompt
            if not info and raw_text.strip():
                info['prompt'] = raw_text.strip()
                info['generation_source'] = 'Unknown'
            
            return info if info else None
            
        except Exception as e:
            print(f"解析参数时出错: {e}")
            return None
    
    def _parse_comfyui_json(self, data):
        """
        专门解析ComfyUI工作流JSON数据
        
        Args:
            data (dict): ComfyUI工作流的JSON内容
            
        Returns:
            dict: 解析后的参数字典
        """
        info = {}
        try:
            # 分析工作流架构类型
            workflow_type = self._detect_comfyui_workflow_type(data)
            info['comfyui_workflow_type'] = workflow_type
            
            if workflow_type == 'flux':
                return self._parse_flux_workflow(data)
            elif workflow_type == 'sdxl':
                return self._parse_sdxl_workflow(data)
            else:
                return self._parse_standard_workflow(data)

        except Exception as e:
            import traceback
            print(f"解析ComfyUI JSON时出错: {e}")
            traceback.print_exc()
            return None
    
    def _detect_comfyui_workflow_type(self, data):
        """
        检测ComfyUI工作流类型
        
        Args:
            data (dict): 工作流数据
            
        Returns:
            str: 工作流类型 ('flux', 'sdxl', 'sd15', 'unknown')
        """
        node_types = []
        for node in data.values():
            if isinstance(node, dict) and 'class_type' in node:
                node_types.append(node['class_type'])
        
        # Flux 特征：UNETLoader, DualCLIPLoader, VAELoader
        flux_indicators = ['UNETLoader', 'DualCLIPLoader', 'FluxGuidance']
        if any(indicator in node_types for indicator in flux_indicators):
            return 'flux'
        
        # SDXL 特征：通常有 CheckpointLoaderSimple 和特定的分辨率
        if 'CheckpointLoaderSimple' in node_types:
            # 检查是否有SDXL特有的节点
            sdxl_indicators = ['SDXLPromptStyler', 'ConditioningConcat']
            if any(indicator in node_types for indicator in sdxl_indicators):
                return 'sdxl'
            
            # 检查模型名称中是否包含SDXL
            for node in data.values():
                if node.get('class_type') == 'CheckpointLoaderSimple':
                    model_name = node.get('inputs', {}).get('ckpt_name', '').lower()
                    if 'xl' in model_name or 'sdxl' in model_name:
                        return 'sdxl'
        
        # SD 1.5 或其他标准工作流
        if 'CheckpointLoaderSimple' in node_types or 'KSampler' in node_types:
            return 'sd15'
        
        return 'unknown'
    
    def _parse_flux_workflow(self, data):
        """解析Flux工作流"""
        info = {'generation_source': 'ComfyUI', 'workflow_type': 'Flux'}
        
        try:
            # 查找关键节点
            unet_node = None
            clip_node = None
            vae_node = None
            sampler_node = None
            guidance_node = None
            noise_node = None
            scheduler_node = None
            
            for node in data.values():
                class_type = node.get("class_type")
                if class_type == "UNETLoader":
                    unet_node = node
                elif class_type == "DualCLIPLoader":
                    clip_node = node
                elif class_type == "VAELoader":
                    vae_node = node
                elif class_type in ["KSampler", "KSamplerAdvanced", "SamplerCustomAdvanced"]:
                    sampler_node = node
                elif class_type == "FluxGuidance":
                    guidance_node = node
                elif class_type == "RandomNoise":
                    noise_node = node
                elif class_type == "BasicScheduler":
                    scheduler_node = node
            
            # 提取模型信息
            if unet_node:
                unet_name = unet_node.get("inputs", {}).get("unet_name", "")
                info['unet_model'] = unet_name
                info['model'] = f"UNET: {unet_name}"  # 为了兼容性
            
            if clip_node:
                clip_name1 = clip_node.get("inputs", {}).get("clip_name1", "")
                clip_name2 = clip_node.get("inputs", {}).get("clip_name2", "")
                info['clip_model'] = f"{clip_name1} + {clip_name2}" if clip_name1 and clip_name2 else clip_name1 or clip_name2
            
            if vae_node:
                vae_name = vae_node.get("inputs", {}).get("vae_name", "")
                info['vae_model'] = vae_name
            
            # 提取采样参数
            if sampler_node:
                inputs = sampler_node.get("inputs", {})
                
                # 对于SamplerCustomAdvanced，需要从引用的节点中获取信息
                if sampler_node.get("class_type") == "SamplerCustomAdvanced":
                    # 从KSamplerSelect节点获取采样器名称
                    sampler_link = inputs.get("sampler")
                    if sampler_link and isinstance(sampler_link, list):
                        sampler_select_node = data.get(str(sampler_link[0]), {})
                        if sampler_select_node.get("class_type") == "KSamplerSelect":
                            sampler_name = sampler_select_node.get("inputs", {}).get("sampler_name")
                            if sampler_name:
                                info['sampler'] = sampler_name
                else:
                    # 传统采样器
                    info['sampler'] = inputs.get("sampler_name")
                
                # 其他采样参数
                info['scheduler'] = inputs.get("scheduler")
                
                # 对于传统采样器，直接获取参数
                if 'steps' in inputs:
                    info['steps'] = inputs.get("steps")
                if 'seed' in inputs:
                    info['seed'] = inputs.get("seed")
                if 'cfg' in inputs:
                    info['cfg_scale'] = inputs.get("cfg")
            
            # 从RandomNoise节点提取seed
            if noise_node:
                noise_inputs = noise_node.get("inputs", {})
                if 'noise_seed' in noise_inputs:
                    info['seed'] = noise_inputs['noise_seed']
                elif 'seed' in noise_inputs:
                    info['seed'] = noise_inputs['seed']
            
            # 从BasicScheduler节点提取steps
            if scheduler_node:
                scheduler_inputs = scheduler_node.get("inputs", {})
                if 'steps' in scheduler_inputs:
                    info['steps'] = scheduler_inputs['steps']
                if 'scheduler' in scheduler_inputs:
                    info['scheduler'] = scheduler_inputs['scheduler']
            
            # 提取Guidance参数
            if guidance_node:
                guidance_inputs = guidance_node.get("inputs", {})
                info['guidance'] = guidance_inputs.get("guidance", 3.5)
            else:
                # 如果没有FluxGuidance节点，检查sampler中是否有guidance相关参数
                if sampler_node:
                    sampler_inputs = sampler_node.get("inputs", {})
                    info['guidance'] = sampler_inputs.get("guidance", sampler_inputs.get("cfg"))
            
            # 提取提示词
            info.update(self._extract_prompts_from_workflow(data))
            
            # 提取LoRA信息
            loras = self._extract_loras_from_workflow(data)
            if loras:
                info["lora_info"] = {"loras": loras}
            
            return {k: v for k, v in info.items() if v is not None}
            
        except Exception as e:
            print(f"解析Flux工作流时出错: {e}")
            return info
    
    def _parse_sdxl_workflow(self, data):
        """解析SDXL工作流"""
        info = {'generation_source': 'ComfyUI', 'workflow_type': 'SDXL'}
        
        try:
            # 查找关键节点
            checkpoint_node = None
            sampler_node = None
            
            for node in data.values():
                class_type = node.get("class_type")
                if class_type in ["CheckpointLoaderSimple", "CheckpointLoader"]:
                    checkpoint_node = node
                elif class_type in ["KSampler", "KSamplerAdvanced"]:
                    sampler_node = node
            
            # 提取模型信息
            if checkpoint_node:
                model_name = checkpoint_node.get("inputs", {}).get("ckpt_name", "")
                info['model'] = model_name
            
            # 提取采样参数
            if sampler_node:
                inputs = sampler_node.get("inputs", {})
                info['steps'] = inputs.get("steps")
                info['cfg_scale'] = inputs.get("cfg")
                info['sampler'] = inputs.get("sampler_name")
                info['scheduler'] = inputs.get("scheduler")
                info['seed'] = inputs.get("seed")
            
            # 提取提示词
            info.update(self._extract_prompts_from_workflow(data))
            
            # 提取LoRA信息
            loras = self._extract_loras_from_workflow(data)
            if loras:
                info["lora_info"] = {"loras": loras}
            
            return {k: v for k, v in info.items() if v is not None}
            
        except Exception as e:
            print(f"解析SDXL工作流时出错: {e}")
            return info
    
    def _parse_standard_workflow(self, data):
        """解析标准工作流（SD 1.5等）"""
        info = {'generation_source': 'ComfyUI', 'workflow_type': 'Standard'}
        
        try:
            # 查找关键节点并提取信息
            sampler_node = None
            for node in data.values():
                if node.get("class_type") in ["KSampler", "KSamplerAdvanced"]:
                    sampler_node = node
                    break
            
            if sampler_node:
                inputs = sampler_node.get("inputs", {})
                info['steps'] = inputs.get("steps")
                info['cfg_scale'] = inputs.get("cfg")
                info['sampler'] = inputs.get("sampler_name")
                info['scheduler'] = inputs.get("scheduler")
                info['seed'] = inputs.get("seed")
                
                # 提取连接的节点信息
                model_link = inputs.get("model")
                
                if model_link and isinstance(model_link, list):
                    model_node_id = str(model_link[0])
                    model_node = data.get(model_node_id, {})
                    if model_node.get("class_type") in ["CheckpointLoader", "CheckpointLoaderSimple"]:
                        info['model'] = model_node.get("inputs", {}).get("ckpt_name")
            
            # 提取提示词
            info.update(self._extract_prompts_from_workflow(data))
            
            # 提取LoRA信息
            loras = self._extract_loras_from_workflow(data)
            if loras:
                info["lora_info"] = {"loras": loras}

            return {k: v for k, v in info.items() if v is not None}

        except Exception as e:
            print(f"解析标准工作流时出错: {e}")
            return info
    
    def _extract_prompts_from_workflow(self, data):
        """从工作流中提取提示词"""
        prompts = {}
        
        def get_prompt_text(link):
            """递归获取提示词文本"""
            if not link or not isinstance(link, list):
                return None
            
            node_id = str(link[0])
            node = data.get(node_id, {})
            
            # 递归查找上游的文本
            visited = set()  # 防止循环引用
            while node and node_id not in visited:
                visited.add(node_id)
                
                # 检查是否是直接包含文本的节点
                if node.get("class_type") == "CLIPTextEncode" and "text" in node.get("inputs", {}):
                    text_input = node["inputs"]["text"]
                    if isinstance(text_input, list):
                        # 如果是引用，继续向上查找
                        node_id = str(text_input[0])
                        node = data.get(node_id, {})
                    else:
                        # 直接文本
                        return str(text_input)
                
                # 检查是否是文本节点（各种类型）
                elif "text" in node.get("inputs", {}):
                    text_input = node["inputs"]["text"]
                    if isinstance(text_input, list):
                        # 如果是引用，继续向上查找
                        node_id = str(text_input[0])
                        node = data.get(node_id, {})
                    else:
                        # 直接文本
                        return str(text_input)
                
                # 检查是否是翻译节点或其他文本处理节点
                elif node.get("class_type") in ["DeepTranslatorTextNode", "StringFunction|pysssss"]:
                    # 这些节点可能有不同的输入字段
                    inputs = node.get("inputs", {})
                    
                    # 查找可能的文本字段
                    text_fields = ["text", "input", "string", "prompt"]
                    for field in text_fields:
                        if field in inputs:
                            text_input = inputs[field]
                            if isinstance(text_input, list):
                                # 如果是引用，继续向上查找
                                node_id = str(text_input[0])
                                node = data.get(node_id, {})
                                break
                            else:
                                # 直接文本
                                return str(text_input)
                    else:
                        # 没有找到文本字段，尝试查找任何输入连接
                        upstream_link = next((v for v in inputs.values() if isinstance(v, list) and len(v) > 0), None)
                        if upstream_link:
                            node_id = str(upstream_link[0])
                            node = data.get(node_id, {})
                        else:
                            break
                
                else:
                    # 其他节点类型，查找任何可能的输入连接
                    inputs = node.get("inputs", {})
                    upstream_link = next((v for v in inputs.values() if isinstance(v, list) and len(v) > 0), None)
                    if upstream_link:
                        node_id = str(upstream_link[0])
                        node = data.get(node_id, {})
                    else:
                        break
            
            return None
        
        # 方法1：查找传统的KSampler节点
        for node in data.values():
            if node.get("class_type") in ["KSampler", "KSamplerAdvanced"]:
                inputs = node.get("inputs", {})
                positive_link = inputs.get("positive")
                negative_link = inputs.get("negative")
                
                if positive_link:
                    prompts['prompt'] = get_prompt_text(positive_link)
                if negative_link:
                    prompts['negative_prompt'] = get_prompt_text(negative_link)
                break
        
        # 方法2：如果没有找到传统采样器，查找Flux风格的采样器
        if not prompts:
            for node in data.values():
                if node.get("class_type") in ["SamplerCustomAdvanced", "SamplerCustom"]:
                    inputs = node.get("inputs", {})
                    
                    # Flux采样器可能有不同的输入结构
                    # 查找guider连接
                    guider_link = inputs.get("guider")
                    if guider_link:
                        guider_node_id = str(guider_link[0])
                        guider_node = data.get(guider_node_id, {})
                        
                        # 从guider节点查找conditioning连接
                        if guider_node and "inputs" in guider_node:
                            guider_inputs = guider_node["inputs"]
                            
                            # 查找positive和negative conditioning
                            positive_link = guider_inputs.get("positive")
                            negative_link = guider_inputs.get("negative")
                            
                            if positive_link:
                                prompts['prompt'] = get_prompt_text(positive_link)
                            if negative_link:
                                prompts['negative_prompt'] = get_prompt_text(negative_link)
                    break
        
        # 方法3：如果还是没有找到，直接查找所有CLIPTextEncode节点
        if not prompts:
            clip_nodes = []
            for node_id, node in data.items():
                if node.get("class_type") == "CLIPTextEncode":
                    clip_nodes.append((node_id, node))
            
            # 如果只有一个CLIPTextEncode节点，假设它是正向提示词
            if len(clip_nodes) == 1:
                node_id, node = clip_nodes[0]
                text_input = node.get("inputs", {}).get("text")
                if text_input:
                    if isinstance(text_input, list):
                        prompts['prompt'] = get_prompt_text(text_input)
                    else:
                        prompts['prompt'] = str(text_input)
            
            # 如果有多个CLIPTextEncode节点，尝试区分正向和负向
            elif len(clip_nodes) > 1:
                for node_id, node in clip_nodes:
                    text_input = node.get("inputs", {}).get("text")
                    if text_input:
                        if isinstance(text_input, list):
                            text_content = get_prompt_text(text_input)
                        else:
                            text_content = str(text_input)
                        
                        if text_content:
                            # 简单的启发式判断：包含负面词汇的可能是负向提示词
                            negative_keywords = ['nsfw', 'bad', 'worst', 'low quality', 'blurry', '糟糕', '模糊', '低质量', '最差']
                            if any(keyword in text_content.lower() for keyword in negative_keywords):
                                if 'negative_prompt' not in prompts:
                                    prompts['negative_prompt'] = text_content
                            else:
                                if 'prompt' not in prompts:
                                    prompts['prompt'] = text_content
        
        # 方法4：如果仍然没有找到，查找所有包含text的节点
        if not prompts:
            text_nodes = []
            for node_id, node in data.items():
                if isinstance(node, dict) and 'inputs' in node:
                    inputs = node['inputs']
                    if 'text' in inputs and not isinstance(inputs['text'], list):
                        text_content = str(inputs['text']).strip()
                        if text_content:
                            text_nodes.append({
                                'id': node_id,
                                'class_type': node.get('class_type'),
                                'text': text_content
                            })
            
            # 如果找到了文本节点，使用第一个作为提示词
            if text_nodes:
                prompts['prompt'] = text_nodes[0]['text']
        
        return prompts
    
    def _extract_loras_from_workflow(self, data):
        """从工作流中提取LoRA信息"""
        loras = []
        for node in data.values():
            if node.get("class_type") == "LoraLoader":
                inputs = node.get("inputs", {})
                loras.append({
                    "name": inputs.get("lora_name"),
                    "weight": inputs.get("strength_model")
                })
        return loras
    
    def _normalize_json_data(self, data):
        """标准化JSON数据格式"""
        normalized = {}
        
        # 常见字段映射
        field_mapping = {
            'prompt': ['prompt', 'positive_prompt', 'text'],
            'negative_prompt': ['negative_prompt', 'negative', 'uncond_prompt'],
            'model': ['model', 'model_name', 'checkpoint', 'model_hash'],
            'sampler': ['sampler', 'sampler_name', 'scheduler'],
            'steps': ['steps', 'num_inference_steps', 'sampling_steps'],
            'cfg_scale': ['cfg_scale', 'guidance_scale', 'scale'],
            'seed': ['seed', 'random_seed']
        }
        
        # 递归查找字段
        def find_value(obj, keys):
            if isinstance(obj, dict):
                for key in keys:
                    if key in obj:
                        return obj[key]
                # 递归搜索
                for value in obj.values():
                    result = find_value(value, keys)
                    if result is not None:
                        return result
            return None
        
        for field, possible_keys in field_mapping.items():
            value = find_value(data, possible_keys)
            if value is not None:
                # 确保所有字段都是字符串或数字，而不是列表
                if isinstance(value, list):
                    if field in ['prompt', 'negative_prompt', 'model', 'sampler']:
                        normalized[field] = ", ".join(map(str, value))
                    elif value:
                        normalized[field] = value[0] # 对于数字字段，取第一个
                else:
                    normalized[field] = value
        
        return normalized if normalized else None 
    
    def _extract_lora_info(self, raw_text):
        """
        提取Lora信息
        
        Args:
            raw_text (str): 原始参数文本
            
        Returns:
            dict: Lora信息字典
        """
        lora_info = {}
        
        try:
            # 匹配各种Lora信息格式
            # 格式1: Lora 1: F.1-韩国网红-时装美女, Lora Hash 1: bc85ee472a, Lora Weight 1: 0.8
            # 格式2: Lora: name:weight
            # 格式3: <lora:name:weight>
            
            # 方法1：匹配详细的Lora信息（Lora X: name, Lora Hash X: hash, Lora Weight X: weight）
            lora_pattern = r'Lora\s+(\d+):\s*([^,]+)(?:,\s*Lora\s+Hash\s+\1:\s*([^,]+))?(?:,\s*Lora\s+Weight\s+\1:\s*([\d.]+))?'
            matches = re.findall(lora_pattern, raw_text, re.IGNORECASE)
            
            if matches:
                lora_list = []
                for match in matches:
                    lora_num, lora_name, lora_hash, lora_weight = match
                    lora_item = {
                        'name': lora_name.strip(),
                        'weight': float(lora_weight) if lora_weight else 1.0
                    }
                    if lora_hash:
                        lora_item['hash'] = lora_hash.strip()
                    lora_list.append(lora_item)
                lora_info['loras'] = lora_list
            
            # 方法2：匹配简单的<lora:name:weight>格式
            if not lora_info:
                simple_pattern = r'<lora:([^:>]+):([^>]+)>'
                simple_matches = re.findall(simple_pattern, raw_text, re.IGNORECASE)
                if simple_matches:
                    lora_list = []
                    for name, weight in simple_matches:
                        try:
                            weight_val = float(weight)
                        except:
                            weight_val = 1.0
                        lora_list.append({
                            'name': name.strip(),
                            'weight': weight_val
                        })
                    lora_info['loras'] = lora_list
            
            # 方法3：匹配其他Lora格式
            if not lora_info:
                # 查找所有包含"lora"的行或段落
                lora_lines = []
                for line in raw_text.split(','):
                    if 'lora' in line.lower():
                        lora_lines.append(line.strip())
                
                if lora_lines:
                    lora_info['raw_lora_text'] = ', '.join(lora_lines)
            
            return lora_info if lora_info else None
            
        except Exception as e:
            print(f"提取Lora信息时出错: {e}")
            return None