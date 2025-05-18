#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
流程执行线程模块，用于在后台线程中执行流程，避免阻塞UI。
"""

from PyQt5.QtCore import QThread, pyqtSignal
from typing import Dict, Any, Optional, Callable, List

class FlowExecutionThread(QThread):
    """
    用于后台执行流程的线程类
    """
    # 信号定义，用于通知UI更新
    step_started = pyqtSignal(int, dict)  # step_index, step_data
    step_completed = pyqtSignal(int, bool, str)  # step_index, success, message
    flow_completed = pyqtSignal(bool)  # success
    
    def __init__(self, flow_controller):
        """
        初始化执行线程
        
        Args:
            flow_controller: FlowController实例
        """
        super().__init__()
        self._flow_controller = flow_controller
        self._is_stopped = False
    
    def run(self):
        """
        线程执行方法，运行流程
        """
        try:
            # 绑定信号到回调函数
            self._flow_controller.execute_flow(
                on_step_start=self._on_step_start,
                on_step_complete=self._on_step_complete,
                on_flow_complete=self._on_flow_complete
            )
        except Exception as e:
            # 发送执行失败信号
            self.flow_completed.emit(False)
            print(f"流程执行异常: {str(e)}")
        finally:
            # 确保流程控制器的执行状态被重置，无论执行成功还是失败
            self._flow_controller._is_executing = False

    def stop(self):
        """
        请求停止执行
        """
        self._is_stopped = True
        self._flow_controller.stop_execution()
    
    def _on_step_start(self, step_index, step_data):
        """步骤开始执行回调"""
        self.step_started.emit(step_index, step_data)
    
    def _on_step_complete(self, step_index, success, message):
        """步骤完成回调"""
        # 将字典类型的消息转换为字符串
        if isinstance(message, dict) and "message" in message:
            message = message["message"]
        elif isinstance(message, dict):
            message = str(message)
        
        self.step_completed.emit(step_index, success, message)
    
    def _on_flow_complete(self, success):
        """流程完成回调"""
        self.flow_completed.emit(success) 