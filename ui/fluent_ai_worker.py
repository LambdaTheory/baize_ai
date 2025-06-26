#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI工作线程
"""

from PyQt5.QtCore import QObject, pyqtSignal


class AITagWorker(QObject):
    """AI标签异步工作类"""
    finished = pyqtSignal(bool, dict)  # 完成信号(成功, 结果数据)
    
    def __init__(self, ai_tagger, image_path, existing_tags):
        super().__init__()
        self.ai_tagger = ai_tagger
        self.image_path = image_path
        self.existing_tags = existing_tags
    
    def run(self):
        """执行AI标签分析"""
        try:
            print(f"[异步工作线程] 开始处理图片: {self.image_path}")
            success, result = self.ai_tagger.auto_tag_image(
                image_path=self.image_path,
                existing_tags=self.existing_tags,
                similarity_threshold=0.8
            )
            print(f"[异步工作线程] 处理完成，成功: {success}")
            self.finished.emit(success, result)
        except Exception as e:
            print(f"[异步工作线程] 处理异常: {e}")
            import traceback
            traceback.print_exc()
            self.finished.emit(False, {"error": str(e)}) 