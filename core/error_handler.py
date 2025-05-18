#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
错误处理器模块，负责管理自动化流程中的异常处理策略。
"""

import time
import traceback
from enum import Enum
from typing import Dict, Any, List, Tuple, Optional, Callable, Union


class ErrorStrategy(Enum):
    """错误处理策略枚举"""
    CONTINUE = "continue"  # 忽略错误并继续执行
    RETRY = "retry"  # 重试当前步骤
    STOP = "stop"  # 停止执行
    JUMP = "jump"  # 跳转到指定步骤
    CUSTOM = "custom"  # 自定义处理策略（执行特定步骤）


class ErrorHandler:
    """
    错误处理器类，负责处理自动化流程执行过程中的异常。
    """
    
    def __init__(self, log_callback: Optional[Callable[[str, str], None]] = None):
        """
        初始化错误处理器
        
        Args:
            log_callback: 日志记录回调函数，签名为 (log_level, message) -> None
        """
        self._log_callback = log_callback
        self._error_log = []  # 存储错误日志
        self._error_counts = {}  # 统计每种错误类型的出现次数
        self._max_error_logs = 1000  # 最大错误日志存储数量
    
    def handle_error(self, error: Exception, step_data: Dict[str, Any], 
                    retry_count: int, max_retries: int) -> Tuple[ErrorStrategy, Optional[int]]:
        """
        处理错误，根据错误类型和步骤配置返回处理策略
        
        Args:
            error: 异常对象
            step_data: 步骤数据
            retry_count: 当前重试次数
            max_retries: 最大重试次数
            
        Returns:
            (错误处理策略, 跳转步骤索引(可选))
        """
        # 记录错误
        self._log_error(error, step_data)
        
        # 获取步骤的错误处理配置
        error_handler_config = step_data.get("error_handler", {})
        strategy_name = error_handler_config.get("strategy", "stop")  # 默认停止执行
        
        try:
            strategy = ErrorStrategy(strategy_name)
        except ValueError:
            # 未知策略名称，默认为停止
            strategy = ErrorStrategy.STOP
            self._log("WARNING", f"未知的错误处理策略: {strategy_name}，将使用默认策略(停止)")
        
        # 处理特定策略
        if strategy == ErrorStrategy.RETRY:
            # 检查是否超过最大重试次数
            if retry_count >= max_retries:
                self._log("WARNING", f"步骤重试次数已达到上限({max_retries}次)，将停止执行")
                return ErrorStrategy.STOP, None
            
            # 获取重试延迟时间
            retry_delay = error_handler_config.get("retry_delay", 1)  # 默认1秒
            if retry_delay > 0:
                time.sleep(retry_delay)
            
            return ErrorStrategy.RETRY, None
        
        elif strategy == ErrorStrategy.JUMP:
            # 获取跳转的步骤索引
            jump_to_step = error_handler_config.get("jump_to_step")
            if jump_to_step is None:
                self._log("ERROR", "缺少jump_to_step参数，无法跳转")
                return ErrorStrategy.STOP, None
            
            return ErrorStrategy.JUMP, jump_to_step
        
        elif strategy == ErrorStrategy.CUSTOM:
            # 获取自定义处理步骤
            custom_steps = error_handler_config.get("custom_steps", [])
            if not custom_steps:
                self._log("ERROR", "缺少custom_steps参数，无法执行自定义处理")
                return ErrorStrategy.STOP, None
            
            # 这里实际返回策略仍为JUMP，跳转步骤索引为一个特殊标记，
            # 流程控制器需要根据此标记执行自定义步骤
            return ErrorStrategy.CUSTOM, custom_steps
        
        # 对于CONTINUE或其他策略，直接返回策略和None
        return strategy, None
    
    def get_error_logs(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        获取错误日志
        
        Args:
            limit: 返回的最大日志数量，如果为None则返回全部
            
        Returns:
            错误日志列表
        """
        if limit is None:
            return self._error_log
        return self._error_log[-limit:]
    
    def get_error_statistics(self) -> Dict[str, int]:
        """
        获取错误统计信息
        
        Returns:
            错误类型及其出现次数的字典
        """
        return self._error_counts
    
    def clear_logs(self) -> None:
        """清空错误日志"""
        self._error_log = []
        self._error_counts = {}
    
    def _log_error(self, error: Exception, step_data: Dict[str, Any]) -> None:
        """
        记录错误信息
        
        Args:
            error: 异常对象
            step_data: 步骤数据
        """
        # 获取错误的类型名称和消息
        error_type = type(error).__name__
        error_message = str(error)
        
        # 获取异常的堆栈跟踪
        stack_trace = traceback.format_exc()
        
        # 获取步骤信息
        action_id = step_data.get("action_id", "unknown")
        parameters = step_data.get("parameters", {})
        
        # 创建错误日志项
        error_log_entry = {
            "timestamp": time.time(),
            "error_type": error_type,
            "error_message": error_message,
            "stack_trace": stack_trace,
            "action_id": action_id,
            "parameters": parameters
        }
        
        # 添加到错误日志列表
        self._error_log.append(error_log_entry)
        
        # 限制错误日志大小
        if len(self._error_log) > self._max_error_logs:
            self._error_log = self._error_log[-self._max_error_logs:]
        
        # 更新错误计数
        self._error_counts[error_type] = self._error_counts.get(error_type, 0) + 1
        
        # 记录错误日志
        self._log("ERROR", f"{error_type}: {error_message}")
    
    def _log(self, level: str, message: str) -> None:
        """
        记录日志
        
        Args:
            level: 日志级别
            message: 日志消息
        """
        if self._log_callback:
            self._log_callback(level, message)
    
    def log_error(self, level: str, message: str) -> None:
        """
        直接记录错误日志（供外部调用）
        
        Args:
            level: 日志级别
            message: 日志消息
        """
        # 记录到内部日志
        timestamp = time.time()
        error_log_entry = {
            "timestamp": timestamp,
            "error_type": "Custom",
            "error_message": message,
            "stack_trace": "",
            "action_id": "CUSTOM_LOG",
            "parameters": {}
        }
        
        # 添加到错误日志列表
        self._error_log.append(error_log_entry)
        
        # 限制错误日志大小
        if len(self._error_log) > self._max_error_logs:
            self._error_log = self._error_log[-self._max_error_logs:]
        
        # 使用内部日志方法
        self._log(level, message)


class TryCatchBlock:
    """
    表示一个Try-Catch代码块，用于在流程中实现异常处理。
    """
    
    def __init__(self, try_steps: List[int], catch_steps: List[int], finally_steps: List[int]):
        """
        初始化Try-Catch代码块
        
        Args:
            try_steps: try块中的步骤索引列表
            catch_steps: catch块中的步骤索引列表
            finally_steps: finally块中的步骤索引列表
        """
        self.try_steps = try_steps
        self.catch_steps = catch_steps
        self.finally_steps = finally_steps
        self.exception = None  # 捕获的异常
        self.catch_executed = False  # 是否已执行catch块
        self.finally_executed = False  # 是否已执行finally块 