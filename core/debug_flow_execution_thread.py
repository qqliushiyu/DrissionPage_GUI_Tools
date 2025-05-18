#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
调试流程执行线程模块，提供带调试功能的流程执行线程。
"""

from PyQt5.QtCore import QThread, pyqtSignal
from typing import Dict, Any, Optional, List

from .debug_manager import DebugManager, ExecutionMode
from .flow_controller import FlowController

class DebugFlowExecutionThread(QThread):
    """
    带调试功能的流程执行线程类
    """
    # 基本执行信号
    step_started = pyqtSignal(int, dict)  # step_index, step_data
    step_completed = pyqtSignal(int, bool, str)  # step_index, success, message
    flow_completed = pyqtSignal(bool)  # success
    
    # 调试相关信号
    breakpoint_hit = pyqtSignal(str, int, dict)  # breakpoint_id, step_index, context_data
    execution_paused = pyqtSignal(int)  # step_index
    execution_resumed = pyqtSignal(int)  # step_index
    variable_changed = pyqtSignal(str, object)  # variable_name, variable_value
    metrics_updated = pyqtSignal(dict)  # performance_metrics
    debug_log_added = pyqtSignal(dict)  # log_entry
    
    def __init__(self, flow_controller: FlowController, debug_manager: DebugManager):
        """
        初始化调试流程执行线程
        
        Args:
            flow_controller: 流程控制器实例
            debug_manager: 调试管理器实例
        """
        super().__init__()
        self._flow_controller = flow_controller
        self._debug_manager = debug_manager
        self._is_stopped = False
        
        # 设置调试回调
        self._setup_debug_callbacks()
        
        # 性能指标更新计时器
        self._metrics_update_interval = 1.0  # 秒
    
    def _setup_debug_callbacks(self):
        """设置调试管理器回调"""
        self._debug_manager.set_breakpoint_hit_callback(self._on_breakpoint_hit)
        self._debug_manager.set_step_execution_callback(self._on_step_execution)
        self._debug_manager.set_variable_changed_callback(self._on_variable_changed)
        self._debug_manager.set_execution_paused_callback(self._on_execution_paused)
        self._debug_manager.set_execution_resumed_callback(self._on_execution_resumed)
    
    def run(self):
        """
        线程执行方法，运行流程
        """
        try:
            # 设置调试模式
            self._debug_manager.start_debugging()
            
            # 性能指标更新定时器
            metrics_timer = 0
            
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
            # 结束调试模式
            self._debug_manager.stop_debugging()
    
    def stop(self):
        """
        请求停止执行
        """
        self._is_stopped = True
        self._flow_controller.stop_execution()
        self._debug_manager.stop_debugging()
    
    def pause(self):
        """
        暂停执行
        """
        if not self._debug_manager.is_paused():
            self._debug_manager.pause_execution()
    
    def resume(self):
        """
        继续执行
        """
        if self._debug_manager.is_paused():
            self._debug_manager.resume_execution()
    
    def step_over(self):
        """
        单步执行（跳过）
        """
        # 首先设置为单步模式
        self._debug_manager.set_execution_mode(ExecutionMode.STEP)
        # 继续执行当前步骤
        self._debug_manager.resume_execution()
    
    def step_into(self):
        """
        单步执行（进入）
        """
        # 对于普通步骤，这与step_over相同
        # 对于函数调用等复杂步骤，实现更复杂的逻辑
        self.step_over()  # 简化版实现
    
    def step_out(self):
        """
        单步执行（跳出）
        """
        # 继续执行直到当前代码块结束
        # 这需要对流程结构有更深入的理解
        # 简化版直接恢复执行
        self._debug_manager.set_execution_mode(ExecutionMode.DEBUG)
        self._debug_manager.resume_execution()
    
    def run_to_cursor(self, target_step_index: int):
        """
        运行到光标处
        
        Args:
            target_step_index: 目标步骤索引
        """
        # 添加临时断点
        from .debug_manager import Breakpoint, BreakpointType
        temp_bp = Breakpoint(step_index=target_step_index, breakpoint_type=BreakpointType.LINE)
        bp_id = self._debug_manager.add_breakpoint(temp_bp)
        
        # 继续执行
        self._debug_manager.set_execution_mode(ExecutionMode.DEBUG)
        self._debug_manager.resume_execution()
        
        # 执行后自动删除临时断点
        # 注意：这里会在不同线程执行，需要考虑线程安全
        def remove_temp_bp():
            self._debug_manager.remove_breakpoint(bp_id)
        
        # 使用信号连接，确保在正确的线程中执行
        self.breakpoint_hit.connect(lambda *args: remove_temp_bp())
    
    # 调试回调
    def _on_breakpoint_hit(self, breakpoint_id: str, step_index: int, context_data: Dict[str, Any]):
        """断点命中回调"""
        self.breakpoint_hit.emit(breakpoint_id, step_index, context_data)
    
    def _on_step_execution(self, step_index: int, step_data: Dict[str, Any]):
        """单步执行回调"""
        # 这里可以添加额外的单步执行逻辑
        pass
    
    def _on_variable_changed(self, variable_name: str, variable_value: Any):
        """变量改变回调"""
        self.variable_changed.emit(variable_name, variable_value)
    
    def _on_execution_paused(self, step_index: int):
        """执行暂停回调"""
        self.execution_paused.emit(step_index)
        
        # 发送当前性能指标
        metrics = self._debug_manager.get_performance_metrics()
        self.metrics_updated.emit(metrics)
    
    def _on_execution_resumed(self, step_index: int):
        """执行继续回调"""
        self.execution_resumed.emit(step_index)
    
    # 流程执行回调
    def _on_step_start(self, step_index: int, step_data: Dict[str, Any]):
        """步骤开始执行回调"""
        # 转发到调试管理器
        self._debug_manager.on_step_start(step_index, step_data)
        # 发送原始信号
        self.step_started.emit(step_index, step_data)
    
    def _on_step_complete(self, step_index: int, success: bool, message):
        """步骤执行完成回调"""
        # 转发到调试管理器
        self._debug_manager.on_step_complete(step_index, success, message)
        
        # 将字典类型的消息转换为字符串
        if isinstance(message, dict) and "message" in message:
            message_str = message["message"]
        elif isinstance(message, dict):
            message_str = str(message)
        else:
            message_str = str(message)
            
        # 发送原始信号
        self.step_completed.emit(step_index, success, message_str)
        
        # 更新并发送性能指标
        metrics = self._debug_manager.get_performance_metrics()
        self.metrics_updated.emit(metrics)
    
    def _on_flow_complete(self, success: bool):
        """流程执行完成回调"""
        try:
            # 转发到调试管理器
            self._debug_manager.on_flow_complete(success)
            # 发送原始信号
            self.flow_completed.emit(success)
            
            # 发送最终性能指标
            metrics = self._debug_manager.get_performance_metrics()
            self.metrics_updated.emit(metrics)
        except Exception as e:
            print(f"流程完成回调处理异常: {str(e)}")
            # 确保即使出现异常，信号也能发出
            self.flow_completed.emit(success)
    
    # 辅助方法
    def get_debug_manager(self) -> DebugManager:
        """获取调试管理器"""
        return self._debug_manager
    
    def is_debugging(self) -> bool:
        """是否在调试模式"""
        return self._debug_manager.get_execution_mode() != ExecutionMode.NORMAL
    
    def is_paused(self) -> bool:
        """是否暂停执行"""
        return self._debug_manager.is_paused() 