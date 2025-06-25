# ComfyUI工作流存储功能说明

## 功能概述

为了解决用户删除本地图片后无法重新生成ComfyUI图片的问题，我们新增了**ComfyUI工作流存储功能**。该功能会自动保存ComfyUI图片的完整工作流数据到数据库中，确保即使原图片丢失，也能通过工具重新生成。

## 核心特性

### 1. 自动工作流存储
- 当导入ComfyUI生成的图片时，自动提取并存储完整的workflow.json数据
- 存储的数据包括：
  - `prompt`：用于执行的节点数据
  - `workflow`：用于界面显示的完整工作流
- 支持所有ComfyUI工作流类型（Flux、SDXL、SD1.5等）

### 2. 数据库结构增强
新增了`workflow_data`字段用于存储工作流JSON数据：

```sql
ALTER TABLE image_records ADD COLUMN workflow_data TEXT;
```

### 3. 一键加载到ComfyUI
在历史记录界面新增"**加载到ComfyUI**"按钮：
- 只有包含workflow数据的ComfyUI记录才会启用此按钮
- 支持WebSocket和HTTP两种加载方式
- 自动验证工作流数据完整性

## 使用方法

### 导入ComfyUI图片
1. 将ComfyUI生成的图片拖拽到工具中
2. 工具会自动提取并存储workflow数据
3. 在历史记录中可以看到"ComfyUI"标识

### 重新生成图片
1. 在历史记录中选择一条ComfyUI记录
2. 点击"**加载到ComfyUI**"按钮
3. 工作流会自动加载到ComfyUI界面
4. 在ComfyUI中点击"Queue Prompt"即可重新生成

## 技术实现

### 数据流程
```
ComfyUI图片 → 提取workflow数据 → 存储到数据库 → 从数据库加载 → 发送到ComfyUI
```

### 核心组件

#### 1. 图片信息读取器增强
```python
# core/image_reader.py
def _parse_parameters(self, raw_text):
    # 检查ComfyUI格式并保存原始workflow数据
    if isinstance(data, dict) and any(key.isdigit() for key in data.keys()):
        parsed_data = self._parse_comfyui_json(data)
        if parsed_data:
            parsed_data['generation_source'] = 'ComfyUI'
            parsed_data['workflow_data'] = data  # 保存原始数据
            return parsed_data
```

#### 2. 数据管理器增强
```python
# core/data_manager.py
def save_record(self, record_data: Dict) -> int:
    # 新增workflow_data字段的存储
    workflow_data = self._serialize_workflow_data(record_data.get('workflow_data'))
```

#### 3. ComfyUI集成增强
```python
# core/comfyui_integration.py
def load_workflow_from_database_record(self, record_data: Dict[str, Any]) -> Tuple[bool, str]:
    # 从数据库记录中加载工作流到ComfyUI
    workflow_data_str = record_data.get('workflow_data', '')
    workflow_data = json.loads(workflow_data_str)
    return self.load_workflow_via_websocket(formatted_workflow)
```

## 兼容性说明

### SD WebUI vs ComfyUI对比

| 特性 | SD WebUI | ComfyUI |
|------|----------|---------|
| 参数存储 | metadata中的文本 | PNG文本块中的JSON |
| 重新生成 | 复制粘贴参数 | 需要完整workflow |
| 数据结构 | 简单键值对 | 复杂节点图 |
| 我们的支持 | ✅ 基础参数提取 | ✅ 完整workflow存储 |

### 数据迁移
- 现有数据库会自动添加`workflow_data`字段
- 历史记录中的SD WebUI图片不受影响
- 新导入的ComfyUI图片会自动包含workflow数据

## 使用场景

### 1. 图片备份恢复
- 本地图片意外删除
- 更换设备后需要恢复工作流
- 分享工作流给其他用户

### 2. 工作流管理
- 收藏优秀的工作流配置
- 对比不同参数的生成效果
- 批量管理复杂工作流

### 3. 协作开发
- 团队成员间分享工作流
- 版本控制和迭代优化
- 标准化生产流程

## 注意事项

### 1. 存储空间
- ComfyUI workflow数据通常较大（几KB到几十KB）
- 建议定期清理不需要的记录
- 可以通过批量导出功能备份重要数据

### 2. ComfyUI版本兼容性
- 不同版本的ComfyUI可能有节点差异
- 加载时会自动验证节点类型
- 建议保持ComfyUI版本相对稳定

### 3. 网络连接
- 需要ComfyUI服务正在运行
- 支持本地和远程ComfyUI实例
- WebSocket连接失败时会自动降级为HTTP

## 故障排除

### 常见问题

1. **按钮不可用**
   - 确认选中的是ComfyUI记录
   - 检查记录是否包含workflow数据

2. **加载失败**
   - 确认ComfyUI正在运行
   - 检查网络连接和端口配置
   - 查看控制台错误信息

3. **数据丢失**
   - 检查数据库文件完整性
   - 使用批量导出功能备份数据
   - 重新导入原始图片

### 调试方法
```python
# 检查记录中的workflow数据
python test_workflow_storage.py

# 查看数据库结构
python -c "
import sqlite3
conn = sqlite3.connect('database/records.db')
cursor = conn.cursor()
cursor.execute('PRAGMA table_info(image_records)')
print([col[1] for col in cursor.fetchall()])
"
```

## 未来规划

1. **工作流编辑器**：内置简单的工作流可视化编辑功能
2. **模板管理**：预设常用工作流模板
3. **版本控制**：支持工作流的版本管理和回滚
4. **云端同步**：支持工作流数据的云端备份和同步

---

*此功能解决了ComfyUI用户的核心痛点，确保重要的工作流数据永不丢失！* 