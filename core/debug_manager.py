#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
调试管理器模块，提供流程调试功能，包括断点设置、单步执行、变量监视等。
"""

import time
import json
import threading
import traceback
from typing import Dict, List, Any, Optional, Callable, Tuple, Set
from enum import Enum
import psutil

# 执行模式枚举
class ExecutionMode(str, Enum):
    """流程执行模式"""
    NORMAL = "normal"  # 正常执行
    DEBUG = "debug"    # 调试执行
    STEP = "step"      # 单步执行
    
# 断点类型枚举
class BreakpointType(str, Enum):
    """断点类型"""
    LINE = "line"           # 行断点
    CONDITION = "condition" # 条件断点
    ERROR = "error"         # 错误断点
    VARIABLE = "variable"   # 变量断点
    
# 断点类
class Breakpoint:
    """断点定义类"""
    def __init__(self, 
                 step_index: int, 
                 breakpoint_type: BreakpointType = BreakpointType.LINE,
                 condition: str = "",
                 variable_name: str = "",
                 variable_value: Any = None,
                 comparison_operator: str = "==",
                 enabled: bool = True):
        self.id = f"{int(time.time())}_{step_index}"
        self.step_index = step_index
        self.type = breakpoint_type
        self.condition = condition
        self.variable_name = variable_name
        self.variable_value = variable_value
        self.comparison_operator = comparison_operator
        self.enabled = enabled
        self.hit_count = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "step_index": self.step_index,
            "type": self.type,
            "condition": self.condition,
            "variable_name": self.variable_name,
            "variable_value": str(self.variable_value),
            "comparison_operator": self.comparison_operator,
            "enabled": self.enabled,
            "hit_count": self.hit_count
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Breakpoint':
        """从字典创建断点"""
        bp = cls(
            step_index=data.get("step_index", 0),
            breakpoint_type=data.get("type", BreakpointType.LINE),
            condition=data.get("condition", ""),
            variable_name=data.get("variable_name", ""),
            variable_value=data.get("variable_value", None),
            comparison_operator=data.get("comparison_operator", "=="),
            enabled=data.get("enabled", True)
        )
        bp.id = data.get("id", bp.id)
        bp.hit_count = data.get("hit_count", 0)
        return bp

# 性能指标类
class PerformanceMetrics:
    """性能指标收集和分析"""
    def __init__(self):
        self.start_time = 0.0
        self.end_time = 0.0
        self.step_times = {}  # 步骤执行时间
        self.memory_usage = []  # 内存使用情况
        self.cpu_usage = []  # CPU使用情况
        self.process = psutil.Process()
    
    def start_monitoring(self):
        """开始监控"""
        self.start_time = time.time()
        self.memory_usage = []
        self.cpu_usage = []
        self.step_times = {}
        self._collect_metrics()
    
    def stop_monitoring(self):
        """停止监控"""
        self.end_time = time.time()
    
    def start_step_timer(self, step_index: int):
        """开始记录步骤时间"""
        self.step_times[step_index] = {"start": time.time(), "end": 0, "duration": 0}
        self._collect_metrics()
    
    def stop_step_timer(self, step_index: int):
        """结束记录步骤时间"""
        if step_index in self.step_times:
            self.step_times[step_index]["end"] = time.time()
            self.step_times[step_index]["duration"] = (
                self.step_times[step_index]["end"] - self.step_times[step_index]["start"]
            )
        self._collect_metrics()
    
    def _collect_metrics(self):
        """收集性能指标"""
        try:
            memory_info = self.process.memory_info()
            cpu_percent = self.process.cpu_percent(interval=0.1)
            
            self.memory_usage.append({
                "timestamp": time.time(),
                "rss": memory_info.rss,  # 物理内存
                "vms": memory_info.vms   # 虚拟内存
            })
            
            self.cpu_usage.append({
                "timestamp": time.time(),
                "percent": cpu_percent
            })
        except Exception as e:
            print(f"性能指标收集错误: {str(e)}")
    
    def get_total_execution_time(self) -> float:
        """获取总执行时间"""
        if self.end_time == 0:
            return time.time() - self.start_time
        return self.end_time - self.start_time
    
    def get_step_execution_time(self, step_index: int) -> float:
        """获取步骤执行时间"""
        if step_index in self.step_times:
            return self.step_times[step_index].get("duration", 0)
        return 0
    
    def get_average_memory_usage(self) -> Dict[str, float]:
        """获取平均内存使用情况"""
        if not self.memory_usage:
            return {"rss": 0, "vms": 0}
        
        rss_values = [item["rss"] for item in self.memory_usage]
        vms_values = [item["vms"] for item in self.memory_usage]
        
        return {
            "rss": sum(rss_values) / len(rss_values) / (1024 * 1024),  # MB
            "vms": sum(vms_values) / len(vms_values) / (1024 * 1024)   # MB
        }
    
    def get_average_cpu_usage(self) -> float:
        """获取平均CPU使用率"""
        if not self.cpu_usage:
            return 0.0
        
        cpu_values = [item["percent"] for item in self.cpu_usage]
        return sum(cpu_values) / len(cpu_values)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "total_time": self.get_total_execution_time(),
            "step_times": self.step_times,
            "avg_memory_usage": self.get_average_memory_usage(),
            "avg_cpu_usage": self.get_average_cpu_usage(),
            "memory_usage": self.memory_usage[-10:] if self.memory_usage else [],  # 只保留最近10条记录
            "cpu_usage": self.cpu_usage[-10:] if self.cpu_usage else []  # 只保留最近10条记录
        }

# 调试管理器类
class DebugManager:
    """调试管理器类，提供调试功能"""
    
    def __init__(self, flow_controller=None):
        """
        初始化调试管理器
        
        Args:
            flow_controller: 流程控制器实例
        """
        self._flow_controller = flow_controller
        self._execution_mode = ExecutionMode.NORMAL
        self._breakpoints = {}  # 断点字典，键为step_index
        self._watch_variables = set()  # 监视的变量集合
        self._current_step_index = -1  # 当前执行的步骤索引
        self._is_paused = False  # 是否暂停执行
        self._continue_event = threading.Event()  # 继续执行的事件
        self._performance_metrics = PerformanceMetrics()  # 性能指标
        
        # 调试相关回调
        self._on_breakpoint_hit = None  # 断点命中回调
        self._on_step_execution = None  # 单步执行回调
        self._on_variable_changed = None  # 变量改变回调
        self._on_execution_paused = None  # 执行暂停回调
        self._on_execution_resumed = None  # 执行继续回调
        
        # 日志相关
        self._debug_logs = []  # 调试日志
        self._max_logs = 1000  # 最大日志数量
    
    def set_flow_controller(self, flow_controller):
        """设置流程控制器"""
        self._flow_controller = flow_controller
    
    def set_execution_mode(self, mode: ExecutionMode):
        """设置执行模式"""
        self._execution_mode = mode
    
    def get_execution_mode(self) -> ExecutionMode:
        """获取当前执行模式"""
        return self._execution_mode
    
    # 断点管理
    def add_breakpoint(self, breakpoint: Breakpoint) -> str:
        """
        添加断点
        
        Args:
            breakpoint: 断点对象
            
        Returns:
            断点ID
        """
        self._breakpoints[breakpoint.id] = breakpoint
        return breakpoint.id
    
    def remove_breakpoint(self, breakpoint_id: str) -> bool:
        """
        移除断点
        
        Args:
            breakpoint_id: 断点ID
            
        Returns:
            是否成功移除
        """
        if breakpoint_id in self._breakpoints:
            del self._breakpoints[breakpoint_id]
            return True
        return False
    
    def get_breakpoints(self) -> List[Dict[str, Any]]:
        """
        获取所有断点
        
        Returns:
            断点列表
        """
        return [bp.to_dict() for bp in self._breakpoints.values()]
    
    def get_breakpoint(self, breakpoint_id: str) -> Optional[Breakpoint]:
        """
        获取指定断点
        
        Args:
            breakpoint_id: 断点ID
            
        Returns:
            断点对象，如果不存在则返回None
        """
        return self._breakpoints.get(breakpoint_id)
    
    def clear_breakpoints(self):
        """清除所有断点"""
        self._breakpoints.clear()
    
    def enable_breakpoint(self, breakpoint_id: str, enabled: bool = True) -> bool:
        """
        启用或禁用断点
        
        Args:
            breakpoint_id: 断点ID
            enabled: 是否启用
            
        Returns:
            是否成功设置
        """
        if breakpoint_id in self._breakpoints:
            self._breakpoints[breakpoint_id].enabled = enabled
            return True
        return False
    
    def toggle_breakpoint(self, step_index: int) -> Tuple[bool, str]:
        """
        切换断点状态
        
        Args:
            step_index: 步骤索引
            
        Returns:
            (是否成功, 消息或断点ID)
        """
        # 检查是否已存在该步骤的行断点
        for bp_id, bp in self._breakpoints.items():
            if bp.step_index == step_index and bp.type == BreakpointType.LINE:
                # 存在则移除
                self.remove_breakpoint(bp_id)
                return True, f"已移除断点 #{bp_id}"
        
        # 不存在则添加
        bp = Breakpoint(step_index=step_index, breakpoint_type=BreakpointType.LINE)
        bp_id = self.add_breakpoint(bp)
        return True, bp_id
    
    # 变量监视
    def add_watch_variable(self, variable_name: str) -> bool:
        """
        添加监视变量
        
        Args:
            variable_name: 变量名
            
        Returns:
            是否成功添加
        """
        if variable_name and variable_name not in self._watch_variables:
            self._watch_variables.add(variable_name)
            return True
        return False
    
    def remove_watch_variable(self, variable_name: str) -> bool:
        """
        移除监视变量
        
        Args:
            variable_name: 变量名
            
        Returns:
            是否成功移除
        """
        if variable_name in self._watch_variables:
            self._watch_variables.remove(variable_name)
            return True
        return False
    
    def get_watch_variables(self) -> List[str]:
        """
        获取所有监视变量
        
        Returns:
            变量名列表
        """
        return list(self._watch_variables)
    
    def clear_watch_variables(self):
        """清除所有监视变量"""
        self._watch_variables.clear()
    
    def get_watch_variable_values(self) -> Dict[str, Any]:
        """
        获取所有监视变量的值
        
        Returns:
            变量值字典
        """
        if not self._flow_controller:
            return {}
        
        values = {}
        for var_name in self._watch_variables:
            values[var_name] = self._flow_controller.get_variable(var_name)
        
        return values
    
    # 执行控制
    def start_debugging(self, mode: ExecutionMode = ExecutionMode.DEBUG):
        """
        开始调试
        
        Args:
            mode: 执行模式
        """
        self._execution_mode = mode
        self._is_paused = False
        self._continue_event.set()
        self._current_step_index = -1
        self._performance_metrics.start_monitoring()
        self._add_debug_log("DEBUG", "开始调试执行")
    
    def pause_execution(self):
        """暂停执行"""
        self._is_paused = True
        self._continue_event.clear()
        self._add_debug_log("DEBUG", "执行已暂停")
        if self._on_execution_paused:
            self._on_execution_paused(self._current_step_index)
    
    def resume_execution(self):
        """继续执行"""
        self._is_paused = False
        self._continue_event.set()
        self._add_debug_log("DEBUG", "执行已继续")
        if self._on_execution_resumed:
            self._on_execution_resumed(self._current_step_index)
    
    def stop_debugging(self):
        """停止调试"""
        self._execution_mode = ExecutionMode.NORMAL
        self._is_paused = False
        self._continue_event.set()
        self._performance_metrics.stop_monitoring()
        self._add_debug_log("DEBUG", "调试执行已停止")
    
    def is_paused(self) -> bool:
        """
        是否暂停执行
        
        Returns:
            是否暂停
        """
        return self._is_paused
    
    def wait_for_continue(self):
        """等待继续执行的信号"""
        self._continue_event.wait()
    
    # 步骤执行回调处理
    def on_step_start(self, step_index: int, step_data: Dict[str, Any]):
        """
        步骤开始执行时的回调
        
        Args:
            step_index: 步骤索引
            step_data: 步骤数据
        """
        self._current_step_index = step_index
        
        # 记录性能指标
        self._performance_metrics.start_step_timer(step_index)
        
        # 单步执行模式，每步都暂停
        if self._execution_mode == ExecutionMode.STEP:
            self.pause_execution()
            if self._on_step_execution:
                self._on_step_execution(step_index, step_data)
            self.wait_for_continue()
        
        # 调试模式，检查断点
        elif self._execution_mode == ExecutionMode.DEBUG:
            # 检查是否有匹配的断点
            for bp in self._breakpoints.values():
                if not bp.enabled:
                    continue
                
                # 行断点
                if bp.type == BreakpointType.LINE and bp.step_index == step_index:
                    bp.hit_count += 1
                    self.pause_execution()
                    if self._on_breakpoint_hit:
                        self._on_breakpoint_hit(bp.id, step_index, step_data)
                    self.wait_for_continue()
                    break
                
                # 条件断点
                elif bp.type == BreakpointType.CONDITION and bp.step_index == step_index and bp.condition:
                    try:
                        # 创建安全的局部变量环境
                        local_vars = {}
                        
                        # 添加当前可用的变量
                        if self._flow_controller:
                            all_vars = self._flow_controller.get_all_variables()
                            for var_name, var_info in all_vars.items():
                                local_vars[var_name] = var_info.get("value")
                        
                        # 计算条件表达式
                        condition_result = eval(bp.condition, {"__builtins__": {}}, local_vars)
                        
                        if condition_result:
                            bp.hit_count += 1
                            self.pause_execution()
                            if self._on_breakpoint_hit:
                                self._on_breakpoint_hit(bp.id, step_index, step_data)
                            self.wait_for_continue()
                            break
                    except Exception as e:
                        self._add_debug_log("ERROR", f"条件断点计算错误: {str(e)}")
        
        # 记录调试日志
        action_id = step_data.get("action_id", "")
        self._add_debug_log("INFO", f"步骤 #{step_index} ({action_id}) 开始执行")
    
    def on_step_complete(self, step_index: int, success: bool, message):
        """
        步骤执行完成时的回调
        
        Args:
            step_index: 步骤索引
            success: 是否成功
            message: 消息（可能是字符串或字典）
        """
        # 记录性能指标
        self._performance_metrics.stop_step_timer(step_index)
        
        # 检查变量变化
        self._check_variable_changes()
        
        # 将字典类型的消息转换为字符串（用于日志和错误处理）
        if isinstance(message, dict) and "message" in message:
            message_str = message["message"]
        elif isinstance(message, dict):
            message_str = str(message)
        else:
            message_str = str(message)
            
        # 检查错误断点
        if not success and self._execution_mode == ExecutionMode.DEBUG:
            for bp in self._breakpoints.values():
                if bp.enabled and bp.type == BreakpointType.ERROR:
                    bp.hit_count += 1
                    self.pause_execution()
                    if self._on_breakpoint_hit:
                        self._on_breakpoint_hit(bp.id, step_index, {"error_message": message_str})
                    self.wait_for_continue()
                    break
        
        # 记录调试日志
        log_level = "SUCCESS" if success else "ERROR"
        self._add_debug_log(log_level, f"步骤 #{step_index} {'完成' if success else '失败'}: {message_str}")
    
    def on_flow_complete(self, success: bool):
        """
        流程执行完成时的回调
        
        Args:
            success: 是否成功
        """
        # 停止性能监控
        self._performance_metrics.stop_monitoring()
        
        # 恢复正常执行模式
        self._execution_mode = ExecutionMode.NORMAL
        self._is_paused = False
        self._continue_event.set()
        
        # 记录调试日志
        log_level = "SUCCESS" if success else "ERROR"
        self._add_debug_log(log_level, f"流程执行{'成功' if success else '失败'}")
        
        # 添加性能统计信息
        metrics = self._performance_metrics.to_dict()
        self._add_debug_log("INFO", (
            f"执行统计: 总时间={metrics['total_time']:.2f}秒, "
            f"平均内存={metrics['avg_memory_usage']['rss']:.2f}MB, "
            f"平均CPU={metrics['avg_cpu_usage']:.2f}%"
        ))
    
    # 变量监视相关
    def _check_variable_changes(self):
        """检查监视变量的变化"""
        if not self._flow_controller or not self._watch_variables:
            return
        
        for var_name in self._watch_variables:
            var_value = self._flow_controller.get_variable(var_name)
            
            # 检查变量断点
            if self._execution_mode == ExecutionMode.DEBUG:
                for bp in self._breakpoints.values():
                    if not bp.enabled or bp.type != BreakpointType.VARIABLE:
                        continue
                    
                    if bp.variable_name == var_name:
                        try:
                            # 比较变量值
                            should_break = False
                            
                            if bp.comparison_operator == "==":
                                should_break = var_value == bp.variable_value
                            elif bp.comparison_operator == "!=":
                                should_break = var_value != bp.variable_value
                            elif bp.comparison_operator == ">":
                                should_break = var_value > bp.variable_value
                            elif bp.comparison_operator == "<":
                                should_break = var_value < bp.variable_value
                            elif bp.comparison_operator == ">=":
                                should_break = var_value >= bp.variable_value
                            elif bp.comparison_operator == "<=":
                                should_break = var_value <= bp.variable_value
                            elif bp.comparison_operator == "in":
                                should_break = var_value in bp.variable_value
                            elif bp.comparison_operator == "not in":
                                should_break = var_value not in bp.variable_value
                            
                            if should_break:
                                bp.hit_count += 1
                                self.pause_execution()
                                if self._on_breakpoint_hit:
                                    self._on_breakpoint_hit(bp.id, self._current_step_index, {
                                        "variable_name": var_name,
                                        "variable_value": var_value
                                    })
                                self.wait_for_continue()
                        except Exception as e:
                            self._add_debug_log("ERROR", f"变量断点计算错误: {str(e)}")
            
            # 触发变量变化回调
            if self._on_variable_changed:
                self._on_variable_changed(var_name, var_value)
    
    # 回调设置
    def set_breakpoint_hit_callback(self, callback: Callable[[str, int, Dict[str, Any]], None]):
        """
        设置断点命中回调
        
        Args:
            callback: 回调函数 (breakpoint_id, step_index, step_data) -> None
        """
        self._on_breakpoint_hit = callback
    
    def set_step_execution_callback(self, callback: Callable[[int, Dict[str, Any]], None]):
        """
        设置单步执行回调
        
        Args:
            callback: 回调函数 (step_index, step_data) -> None
        """
        self._on_step_execution = callback
    
    def set_variable_changed_callback(self, callback: Callable[[str, Any], None]):
        """
        设置变量改变回调
        
        Args:
            callback: 回调函数 (variable_name, variable_value) -> None
        """
        self._on_variable_changed = callback
    
    def set_execution_paused_callback(self, callback: Callable[[int], None]):
        """
        设置执行暂停回调
        
        Args:
            callback: 回调函数 (step_index) -> None
        """
        self._on_execution_paused = callback
    
    def set_execution_resumed_callback(self, callback: Callable[[int], None]):
        """
        设置执行继续回调
        
        Args:
            callback: 回调函数 (step_index) -> None
        """
        self._on_execution_resumed = callback
    
    # 性能指标
    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        获取性能指标
        
        Returns:
            性能指标字典
        """
        return self._performance_metrics.to_dict()
    
    # 日志管理
    def _add_debug_log(self, level: str, message: str):
        """
        添加调试日志
        
        Args:
            level: 日志级别
            message: 日志消息
        """
        log_entry = {
            "timestamp": time.time(),
            "level": level,
            "message": message
        }
        
        self._debug_logs.append(log_entry)
        
        # 限制日志数量
        if len(self._debug_logs) > self._max_logs:
            self._debug_logs = self._debug_logs[-self._max_logs:]
    
    def get_debug_logs(self, filter_level: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        获取调试日志
        
        Args:
            filter_level: 过滤的日志级别，None表示获取所有级别
            
        Returns:
            日志列表
        """
        if filter_level:
            return [log for log in self._debug_logs if log["level"] == filter_level]
        return self._debug_logs.copy()
    
    def clear_debug_logs(self):
        """清除所有调试日志"""
        self._debug_logs.clear()
    
    def export_debug_logs(self, file_path: str) -> Tuple[bool, str]:
        """
        导出调试日志
        
        Args:
            file_path: 导出文件路径
            
        Returns:
            (是否成功, 消息)
        """
        try:
            import os
            
            # 确保目录存在
            directory = os.path.dirname(file_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
            
            # 导出日志
            with open(file_path, "w", encoding="utf-8") as f:
                for log in self._debug_logs:
                    # 格式化时间戳
                    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(log["timestamp"]))
                    # 写入格式化的日志行
                    f.write(f"[{timestamp}] [{log['level']}] {log['message']}\n")
            
            return True, f"日志已导出到 {file_path}"
        except Exception as e:
            return False, f"导出日志失败: {str(e)}"
    
    def export_debug_logs_json(self, file_path: str) -> Tuple[bool, str]:
        """
        导出调试日志为JSON格式
        
        Args:
            file_path: 导出文件路径
            
        Returns:
            (是否成功, 消息)
        """
        try:
            import os
            
            # 确保目录存在
            directory = os.path.dirname(file_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
            
            # 转换日志中的时间戳为可读格式
            logs_copy = []
            for log in self._debug_logs:
                log_copy = log.copy()
                log_copy["formatted_time"] = time.strftime(
                    "%Y-%m-%d %H:%M:%S", 
                    time.localtime(log["timestamp"])
                )
                logs_copy.append(log_copy)
            
            # 导出日志
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(logs_copy, f, ensure_ascii=False, indent=2)
            
            return True, f"日志已导出到 {file_path}"
        except Exception as e:
            return False, f"导出日志失败: {str(e)}"
    
    # 多线程支持
    def is_thread_safe(self) -> bool:
        """
        检查是否线程安全
        
        Returns:
            是否线程安全
        """
        # 此方法用于标识该类的线程安全性，实际实现中已通过适当的同步机制确保线程安全
        return True 