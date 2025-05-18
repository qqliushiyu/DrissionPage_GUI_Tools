#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
任务调度器模块，负责计划任务的调度和执行。
"""

import os
import json
import time
import datetime
import threading
import logging
from typing import Dict, List, Tuple, Any, Optional, Union, Callable

try:
    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.triggers.cron import CronTrigger
    from apscheduler.triggers.interval import IntervalTrigger
    from apscheduler.triggers.date import DateTrigger
    SCHEDULER_AVAILABLE = True
except ImportError:
    SCHEDULER_AVAILABLE = False

from .flow_execution_thread import FlowExecutionThread
from common.constants import (
    SCHEDULER_DIRECTORY, TASK_FILE_EXTENSION, 
    HISTORY_DIRECTORY, HISTORY_FILE_EXTENSION
)


class TaskScheduler:
    """
    任务调度器类，提供计划任务的调度和执行功能。
    """
    
    def __init__(self, flow_controller=None):
        """
        初始化任务调度器
        
        Args:
            flow_controller: 流程控制器实例，用于执行流程
        """
        self._flow_controller = flow_controller
        self._scheduler = None
        self._tasks = {}  # {task_id: task_data}
        self._is_running = False
        self._execution_history = {}  # {task_id: [execution_records]}
        
        # 初始化日志
        self._logger = logging.getLogger(__name__)
        
        # 确保目录存在
        self._ensure_directories()
        
        # 加载任务列表
        self._load_tasks()
        self._load_history()
    
    def _ensure_directories(self) -> None:
        """确保相关目录存在"""
        os.makedirs(SCHEDULER_DIRECTORY, exist_ok=True)
        os.makedirs(HISTORY_DIRECTORY, exist_ok=True)
    
    def start(self) -> bool:
        """
        启动任务调度器
        
        Returns:
            是否成功启动
        """
        if not SCHEDULER_AVAILABLE:
            self._logger.error("未安装apscheduler库，无法启动任务调度器")
            return False
        
        if self._is_running:
            self._logger.warning("任务调度器已经在运行")
            return True
        
        try:
            # 创建调度器
            self._scheduler = BackgroundScheduler()
            
            # 添加所有启用的任务
            for task_id, task in self._tasks.items():
                if task.get("enabled", True):
                    self._add_task_to_scheduler(task_id)
            
            # 启动调度器
            self._scheduler.start()
            self._is_running = True
            self._logger.info("任务调度器已启动")
            return True
        
        except Exception as e:
            self._logger.error(f"启动任务调度器失败: {str(e)}")
            return False
    
    def stop(self) -> bool:
        """
        停止任务调度器
        
        Returns:
            是否成功停止
        """
        if not self._is_running or not self._scheduler:
            self._logger.warning("任务调度器未运行")
            return True
        
        try:
            # 关闭调度器
            self._scheduler.shutdown()
            self._scheduler = None
            self._is_running = False
            self._logger.info("任务调度器已停止")
            return True
        
        except Exception as e:
            self._logger.error(f"停止任务调度器失败: {str(e)}")
            return False
    
    def restart(self) -> bool:
        """
        重启任务调度器
        
        Returns:
            是否成功重启
        """
        self.stop()
        return self.start()
    
    def is_running(self) -> bool:
        """
        检查调度器是否正在运行
        
        Returns:
            是否正在运行
        """
        return self._is_running
    
    def _load_tasks(self) -> None:
        """加载所有任务"""
        self._tasks = {}
        
        if not os.path.exists(SCHEDULER_DIRECTORY):
            return
        
        for file_name in os.listdir(SCHEDULER_DIRECTORY):
            if file_name.endswith(TASK_FILE_EXTENSION):
                file_path = os.path.join(SCHEDULER_DIRECTORY, file_name)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        task_data = json.load(f)
                    
                    task_id = file_name.replace(TASK_FILE_EXTENSION, "")
                    self._tasks[task_id] = task_data
                except Exception as e:
                    self._logger.error(f"加载任务失败: {file_path} - {str(e)}")
    
    def _load_history(self) -> None:
        """加载执行历史"""
        self._execution_history = {}
        
        if not os.path.exists(HISTORY_DIRECTORY):
            return
        
        for file_name in os.listdir(HISTORY_DIRECTORY):
            if file_name.endswith(HISTORY_FILE_EXTENSION):
                file_path = os.path.join(HISTORY_DIRECTORY, file_name)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        history_data = json.load(f)
                    
                    task_id = file_name.replace(HISTORY_FILE_EXTENSION, "")
                    self._execution_history[task_id] = history_data
                except Exception as e:
                    self._logger.error(f"加载历史记录失败: {file_path} - {str(e)}")
    
    def _save_task(self, task_id: str) -> bool:
        """
        保存单个任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            是否保存成功
        """
        if task_id not in self._tasks:
            return False
        
        task_data = self._tasks[task_id]
        file_path = os.path.join(SCHEDULER_DIRECTORY, f"{task_id}{TASK_FILE_EXTENSION}")
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(task_data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            self._logger.error(f"保存任务失败: {file_path} - {str(e)}")
            return False
    
    def _save_history(self, task_id: str) -> bool:
        """
        保存单个任务的历史记录
        
        Args:
            task_id: 任务ID
            
        Returns:
            是否保存成功
        """
        if task_id not in self._execution_history:
            return False
        
        history_data = self._execution_history[task_id]
        file_path = os.path.join(HISTORY_DIRECTORY, f"{task_id}{HISTORY_FILE_EXTENSION}")
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(history_data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            self._logger.error(f"保存历史记录失败: {file_path} - {str(e)}")
            return False
    
    def _add_task_to_scheduler(self, task_id: str) -> bool:
        """
        将任务添加到调度器
        
        Args:
            task_id: 任务ID
            
        Returns:
            是否添加成功
        """
        if not self._scheduler:
            self._logger.error("调度器未初始化")
            return False
        
        if task_id not in self._tasks:
            self._logger.error(f"任务不存在: {task_id}")
            return False
        
        task = self._tasks[task_id]
        trigger_type = task.get("trigger_type", "")
        trigger_args = task.get("trigger_args", {})
        
        try:
            # 创建触发器
            trigger = None
            
            if trigger_type == "cron":
                # Cron触发器
                trigger = CronTrigger(
                    year=trigger_args.get("year", "*"),
                    month=trigger_args.get("month", "*"),
                    day=trigger_args.get("day", "*"),
                    week=trigger_args.get("week", "*"),
                    day_of_week=trigger_args.get("day_of_week", "*"),
                    hour=trigger_args.get("hour", "*"),
                    minute=trigger_args.get("minute", "*"),
                    second=trigger_args.get("second", "0")
                )
            
            elif trigger_type == "interval":
                # 间隔触发器
                trigger = IntervalTrigger(
                    weeks=trigger_args.get("weeks", 0),
                    days=trigger_args.get("days", 0),
                    hours=trigger_args.get("hours", 0),
                    minutes=trigger_args.get("minutes", 0),
                    seconds=trigger_args.get("seconds", 0)
                )
            
            elif trigger_type == "date":
                # 日期触发器
                run_date = trigger_args.get("run_date", "")
                if run_date:
                    # 将字符串转换为datetime对象
                    if isinstance(run_date, str):
                        run_date = datetime.datetime.fromisoformat(run_date)
                    trigger = DateTrigger(run_date=run_date)
                else:
                    self._logger.error(f"日期触发器缺少run_date参数: {task_id}")
                    return False
            
            else:
                self._logger.error(f"不支持的触发器类型: {trigger_type}")
                return False
            
            # 添加任务
            self._scheduler.add_job(
                self._execute_task,
                trigger=trigger,
                id=task_id,
                args=[task_id],
                replace_existing=True
            )
            
            return True
        
        except Exception as e:
            self._logger.error(f"添加任务到调度器失败: {task_id} - {str(e)}")
            return False
    
    def _execute_task(self, task_id: str) -> None:
        """
        执行任务
        
        Args:
            task_id: 任务ID
        """
        if task_id not in self._tasks:
            self._logger.error(f"任务不存在: {task_id}")
            return
        
        task = self._tasks[task_id]
        task_name = task.get("task_name", "未命名任务")
        flow_file_path = task.get("flow_file_path", "")
        
        # 记录开始时间
        start_time = time.time()
        start_time_str = datetime.datetime.fromtimestamp(start_time).isoformat()
        
        self._logger.info(f"开始执行任务: {task_name} ({task_id})")
        
        # 创建执行记录
        execution_record = {
            "task_id": task_id,
            "start_time": start_time_str,
            "end_time": "",
            "status": "running",
            "result": "",
            "error": ""
        }
        
        # 添加到历史记录
        if task_id not in self._execution_history:
            self._execution_history[task_id] = []
        
        self._execution_history[task_id].append(execution_record)
        self._save_history(task_id)
        
        # 更新任务上次执行时间
        task["last_run"] = start_time_str
        self._save_task(task_id)
        
        # 执行流程
        result = False
        error_message = ""
        
        try:
            if not self._flow_controller:
                raise ValueError("流程控制器未配置")
            
            # 加载流程文件
            if not flow_file_path or not os.path.exists(flow_file_path):
                raise ValueError(f"流程文件不存在: {flow_file_path}")
            
            # 检查是否有参数
            task_params = task.get("parameters", {})
            
            # 执行流程
            execution_thread = FlowExecutionThread(self._flow_controller, flow_file_path)
            execution_thread.start()
            execution_thread.join()  # 等待执行完成
            
            result = execution_thread.is_success()
            if not result:
                error_message = execution_thread.get_error_message() or "未知错误"
        
        except Exception as e:
            result = False
            error_message = str(e)
            self._logger.error(f"任务执行异常: {task_id} - {str(e)}")
        
        # 记录结束时间
        end_time = time.time()
        end_time_str = datetime.datetime.fromtimestamp(end_time).isoformat()
        
        # 更新执行记录
        execution_record["end_time"] = end_time_str
        execution_record["status"] = "success" if result else "failed"
        execution_record["error"] = error_message
        
        # 记录执行时间
        execution_time = end_time - start_time
        execution_record["execution_time"] = execution_time
        
        # 保存历史记录
        self._save_history(task_id)
        
        # 更新任务状态
        task["last_result"] = "success" if result else "failed"
        task["last_error"] = error_message
        task["execution_count"] = task.get("execution_count", 0) + 1
        self._save_task(task_id)
        
        if result:
            self._logger.info(f"任务执行成功: {task_name} ({task_id}), 耗时: {execution_time:.2f}秒")
        else:
            self._logger.error(f"任务执行失败: {task_name} ({task_id}), 错误: {error_message}")
    
    def create_task(self, task_data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        创建任务
        
        Args:
            task_data: 任务数据
            
        Returns:
            (成功标志, 任务ID或错误消息)
        """
        # 验证必要字段
        task_name = task_data.get("task_name", "")
        flow_file_path = task_data.get("flow_file_path", "")
        trigger_type = task_data.get("trigger_type", "")
        
        if not task_name:
            return False, "缺少任务名称"
        
        if not flow_file_path:
            return False, "缺少流程文件路径"
        
        if not os.path.exists(flow_file_path):
            return False, f"流程文件不存在: {flow_file_path}"
        
        if not trigger_type:
            return False, "缺少触发器类型"
        
        # 生成任务ID
        task_id = task_data.get("task_id", "")
        if not task_id:
            # 根据任务名生成ID
            task_id = "".join(c.lower() for c in task_name if c.isalnum())
            if not task_id:
                task_id = f"task_{int(time.time())}"
            
            # 确保ID唯一
            original_task_id = task_id
            counter = 1
            while task_id in self._tasks:
                task_id = f"{original_task_id}_{counter}"
                counter += 1
            
            task_data["task_id"] = task_id
        elif task_id in self._tasks:
            return False, f"任务ID已存在: {task_id}"
        
        # 添加创建时间和默认字段
        if "created_at" not in task_data:
            task_data["created_at"] = datetime.datetime.now().isoformat()
        
        task_data["updated_at"] = datetime.datetime.now().isoformat()
        task_data["execution_count"] = 0
        task_data["enabled"] = task_data.get("enabled", True)
        
        # 保存任务
        self._tasks[task_id] = task_data
        if not self._save_task(task_id):
            return False, f"保存任务文件失败: {task_id}"
        
        # 如果调度器正在运行且任务启用，添加到调度器
        if self._is_running and task_data.get("enabled", True):
            self._add_task_to_scheduler(task_id)
        
        # 创建空历史记录
        self._execution_history[task_id] = []
        self._save_history(task_id)
        
        return True, task_id
    
    def update_task(self, task_id: str, task_data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        更新任务
        
        Args:
            task_id: 任务ID
            task_data: 新的任务数据
            
        Returns:
            (成功标志, 消息)
        """
        if task_id not in self._tasks:
            return False, f"任务不存在: {task_id}"
        
        # 保留创建时间和执行计数
        task_data["created_at"] = self._tasks[task_id].get("created_at", "")
        task_data["execution_count"] = self._tasks[task_id].get("execution_count", 0)
        
        # 更新修改时间
        task_data["updated_at"] = datetime.datetime.now().isoformat()
        
        # 更新任务
        old_enabled = self._tasks[task_id].get("enabled", True)
        new_enabled = task_data.get("enabled", True)
        
        self._tasks[task_id] = task_data
        
        # 保存任务
        if not self._save_task(task_id):
            return False, f"保存任务文件失败: {task_id}"
        
        # 如果调度器正在运行，更新调度器中的任务
        if self._is_running:
            if old_enabled and not new_enabled:
                # 如果任务从启用变为禁用，从调度器中移除
                try:
                    self._scheduler.remove_job(task_id)
                except:
                    pass
            elif new_enabled:
                # 如果任务启用，更新或添加到调度器
                self._add_task_to_scheduler(task_id)
        
        return True, f"任务已更新: {task_id}"
    
    def delete_task(self, task_id: str) -> Tuple[bool, str]:
        """
        删除任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            (成功标志, 消息)
        """
        if task_id not in self._tasks:
            return False, f"任务不存在: {task_id}"
        
        # 从调度器中移除
        if self._is_running:
            try:
                self._scheduler.remove_job(task_id)
            except:
                pass
        
        # 删除任务文件
        task_file = os.path.join(SCHEDULER_DIRECTORY, f"{task_id}{TASK_FILE_EXTENSION}")
        if os.path.exists(task_file):
            try:
                os.remove(task_file)
            except Exception as e:
                return False, f"删除任务文件失败: {str(e)}"
        
        # 从内存中移除
        del self._tasks[task_id]
        
        # 保留历史记录，但从内存中移除
        if task_id in self._execution_history:
            del self._execution_history[task_id]
        
        return True, f"任务已删除: {task_id}"
    
    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        获取任务信息
        
        Args:
            task_id: 任务ID
            
        Returns:
            任务数据，如果不存在则返回None
        """
        return self._tasks.get(task_id)
    
    def get_all_tasks(self) -> Dict[str, Dict[str, Any]]:
        """
        获取所有任务
        
        Returns:
            所有任务的字典 {task_id: task_data}
        """
        return self._tasks.copy()
    
    def enable_task(self, task_id: str) -> Tuple[bool, str]:
        """
        启用任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            (成功标志, 消息)
        """
        if task_id not in self._tasks:
            return False, f"任务不存在: {task_id}"
        
        # 如果已经启用，直接返回
        if self._tasks[task_id].get("enabled", True):
            return True, f"任务已经启用: {task_id}"
        
        # 启用任务
        self._tasks[task_id]["enabled"] = True
        self._tasks[task_id]["updated_at"] = datetime.datetime.now().isoformat()
        
        # 保存任务
        if not self._save_task(task_id):
            return False, f"保存任务文件失败: {task_id}"
        
        # 如果调度器正在运行，添加到调度器
        if self._is_running:
            self._add_task_to_scheduler(task_id)
        
        return True, f"任务已启用: {task_id}"
    
    def disable_task(self, task_id: str) -> Tuple[bool, str]:
        """
        禁用任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            (成功标志, 消息)
        """
        if task_id not in self._tasks:
            return False, f"任务不存在: {task_id}"
        
        # 如果已经禁用，直接返回
        if not self._tasks[task_id].get("enabled", True):
            return True, f"任务已经禁用: {task_id}"
        
        # 禁用任务
        self._tasks[task_id]["enabled"] = False
        self._tasks[task_id]["updated_at"] = datetime.datetime.now().isoformat()
        
        # 保存任务
        if not self._save_task(task_id):
            return False, f"保存任务文件失败: {task_id}"
        
        # 如果调度器正在运行，从调度器中移除
        if self._is_running:
            try:
                self._scheduler.remove_job(task_id)
            except:
                pass
        
        return True, f"任务已禁用: {task_id}"
    
    def run_task_now(self, task_id: str) -> Tuple[bool, str]:
        """
        立即执行任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            (成功标志, 消息)
        """
        if task_id not in self._tasks:
            return False, f"任务不存在: {task_id}"
        
        # 启动一个新线程执行任务
        threading.Thread(target=self._execute_task, args=(task_id,)).start()
        
        return True, f"任务执行已启动: {task_id}"
    
    def get_execution_history(self, task_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        获取任务执行历史
        
        Args:
            task_id: 任务ID
            limit: 返回的最大记录数
            
        Returns:
            执行历史记录列表
        """
        if task_id not in self._execution_history:
            return []
        
        # 按时间倒序排序
        history = sorted(
            self._execution_history[task_id],
            key=lambda x: x.get("start_time", ""),
            reverse=True
        )
        
        # 限制返回数量
        return history[:limit]
    
    def get_next_run_time(self, task_id: str) -> Optional[datetime.datetime]:
        """
        获取任务下次执行时间
        
        Args:
            task_id: 任务ID
            
        Returns:
            下次执行时间，如果任务不存在或不在调度器中则返回None
        """
        if not self._is_running or not self._scheduler:
            return None
        
        try:
            job = self._scheduler.get_job(task_id)
            if job:
                return job.next_run_time
        except:
            pass
        
        return None
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        获取任务状态
        
        Args:
            task_id: 任务ID
            
        Returns:
            任务状态信息
        """
        status = {
            "exists": task_id in self._tasks,
            "enabled": False,
            "last_run": None,
            "last_result": None,
            "next_run": None,
            "execution_count": 0
        }
        
        if task_id in self._tasks:
            task = self._tasks[task_id]
            status["enabled"] = task.get("enabled", True)
            status["last_run"] = task.get("last_run")
            status["last_result"] = task.get("last_result")
            status["execution_count"] = task.get("execution_count", 0)
            
            # 获取下次执行时间
            next_run = self.get_next_run_time(task_id)
            if next_run:
                status["next_run"] = next_run.isoformat()
        
        return status 