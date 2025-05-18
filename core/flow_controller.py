#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
流程控制器模块，负责管理自动化流程的步骤。
"""

from typing import List, Dict, Any, Optional, Tuple, Callable
import copy

from .drission_engine import DrissionEngine
from .variable_manager import VariableManager, VariableScope
from .condition_evaluator import ConditionEvaluator
from .error_handler import ErrorHandler, ErrorStrategy, TryCatchBlock

# 步骤类型常量
STEP_TYPES = [
    # 浏览器操作
    "OPEN_BROWSER",
    "CLOSE_BROWSER",
    
    # 页面操作
    "PAGE_GET",
    "PAGE_REFRESH",
    "TAKE_SCREENSHOT",
    "SCROLL_PAGE",
    "MOUSE_HOVER",
    
    # 元素操作
    "ELEMENT_CLICK",
    "ELEMENT_INPUT",
    "WAIT_FOR_ELEMENT",
    "SELECT_OPTION",
    
    # 表单操作
    "FILL_FORM",
    "SUBMIT_FORM",
    
    # 数据提取
    "EXTRACT_TEXT",
    "EXTRACT_ATTRIBUTE",
    
    # 条件操作
    "IF_CONDITION",
    "WAIT_SECONDS",
    
    # 文件操作
    "UPLOAD_FILE",
    "DOWNLOAD_FILE",
    
    # 自定义操作
    "EXECUTE_JAVASCRIPT",
    
    # 日志
    "LOG_MESSAGE",
]

# 步骤描述
STEP_DESCRIPTIONS = {
    "OPEN_BROWSER": "打开浏览器",
    "CLOSE_BROWSER": "关闭浏览器",
    "PAGE_GET": "打开网页",
    "PAGE_REFRESH": "刷新页面",
    "ELEMENT_CLICK": "点击元素",
    "ELEMENT_INPUT": "输入文本",
    "WAIT_FOR_ELEMENT": "等待元素",
    "TAKE_SCREENSHOT": "页面截图",
    "SCROLL_PAGE": "滚动页面",
    "MOUSE_HOVER": "鼠标悬停",
    "SELECT_OPTION": "选择下拉选项",
    "FILL_FORM": "填写表单",
    "SUBMIT_FORM": "提交表单",
    "EXTRACT_TEXT": "提取文本",
    "EXTRACT_ATTRIBUTE": "提取属性",
    "IF_CONDITION": "条件判断",
    "WAIT_SECONDS": "等待时间",
    "UPLOAD_FILE": "上传文件",
    "DOWNLOAD_FILE": "下载文件",
    "EXECUTE_JAVASCRIPT": "执行JavaScript",
    "LOG_MESSAGE": "记录日志",
}

class FlowController:
    """
    管理自动化流程步骤的控制器类。
    """
    def __init__(self):
        """初始化流程控制器"""
        self._steps = []  # 存储流程步骤
        self._flow_name = "新建流程"  # 流程名称
        self._current_step_index = -1  # 当前执行步骤索引
        self._engine = DrissionEngine()  # DrissionPage 引擎实例
        self._is_executing = False  # 是否正在执行
        
        # 初始化变量管理器
        self._variable_manager = VariableManager()
        
        # 初始化条件评估器
        self._condition_evaluator = ConditionEvaluator(
            variable_manager=self._variable_manager
        )
        
        # 初始化错误处理器
        self._error_handler = ErrorHandler()
        
        # 当前活动的 try-catch 块列表
        self._active_try_blocks = []
        
        # 挂起的删除流程操作
        self._pending_delete_flow = False
        self._pending_clear_variables = False
    
    def create_new_flow(self, flow_name: str = "新建流程") -> None:
        """创建新的流程，清空现有步骤"""
        self._steps = []
        self._flow_name = flow_name
        self._current_step_index = -1
        
        # 清空变量（仅保留全局变量）
        self._variable_manager.clear_scope(VariableScope.LOCAL)
        self._variable_manager.clear_scope(VariableScope.TEMPORARY)
        
        # 清空错误日志
        self._error_handler.clear_logs()
        
        # 清空活动的 try-catch 块
        self._active_try_blocks = []
    
    def add_step(self, action_id: str, parameters: Dict[str, Any], 
                 at_index: Optional[int] = None, 
                 error_handler: Optional[Dict[str, Any]] = None) -> int:
        """
        添加步骤到流程中
        
        Args:
            action_id: 动作ID
            parameters: 动作参数
            at_index: 插入位置，默认为末尾
            error_handler: 错误处理配置
            
        Returns:
            新步骤的索引
        """
        step_data = {
            "action_id": action_id,
            "parameters": parameters,
            "enabled": True,  # 默认启用
            "error_handler": error_handler or {}  # 错误处理配置
        }
        
        if at_index is None or at_index >= len(self._steps):
            self._steps.append(step_data)
            return len(self._steps) - 1
        else:
            self._steps.insert(at_index, step_data)
            return at_index
    
    def remove_step(self, index: int) -> bool:
        """删除步骤"""
        if 0 <= index < len(self._steps):
            del self._steps[index]
            return True
        return False
    
    def get_steps(self) -> List[Dict[str, Any]]:
        """获取所有步骤"""
        return self._steps
    
    def get_flow_name(self) -> str:
        """获取流程名称"""
        return self._flow_name
    
    def set_flow_name(self, name: str) -> None:
        """设置流程名称"""
        self._flow_name = name
    
    def execute_flow(self, on_step_start: Optional[Callable[[int, Dict[str, Any]], None]] = None,
                    on_step_complete: Optional[Callable[[int, bool, str], None]] = None,
                    on_flow_complete: Optional[Callable[[bool], None]] = None) -> None:
        """
        执行当前流程。
        
        Args:
            on_step_start: 开始执行步骤时的回调函数 (step_index, step_data) -> None
            on_step_complete: 步骤执行完成时的回调函数 (step_index, success, message) -> None
            on_flow_complete: 流程执行完成时的回调函数 (success) -> None
        """
        if self._is_executing:
            if on_flow_complete:
                on_flow_complete(False)
            return
        
        # 检查流程是否为空
        if not self._steps:
            if on_flow_complete:
                on_flow_complete(False)
            return
        
        # 检查是否需要初始化浏览器
        if not self._engine.is_running():
            # 检查第一个步骤是否为OPEN_BROWSER
            first_step_is_open_browser = (self._steps[0].get("action_id") == "OPEN_BROWSER")
            
            # 如果第一个步骤是OPEN_BROWSER，获取其配置先初始化
            if first_step_is_open_browser:
                parameters = self._steps[0].get("parameters", {})
                browser_config = self._prepare_browser_config(parameters)
                success = self._engine.initialize(page_type='chromium', config=browser_config)
            else:
                # 否则使用默认配置初始化
                success = self._engine.initialize(page_type='chromium')
                
            if not success:
                if on_flow_complete:
                    on_flow_complete(False)
                return
        else:
            # 浏览器已初始化，检查连接是否仍然有效
            if not self._engine.check_connection():
                # 连接已断开，重新初始化浏览器
                print("检测到浏览器连接已断开，将重新初始化")
                
                # 先关闭旧的连接
                self._engine.close()
                
                # 检查第一个步骤是否为OPEN_BROWSER
                first_step_is_open_browser = (self._steps[0].get("action_id") == "OPEN_BROWSER")
                
                # 重新初始化浏览器
                if first_step_is_open_browser:
                    parameters = self._steps[0].get("parameters", {})
                    browser_config = self._prepare_browser_config(parameters)
                    success = self._engine.initialize(page_type='chromium', config=browser_config)
                    
                    # 如果成功重新初始化，并且第一个步骤是OPEN_BROWSER，跳过第一个步骤
                    if success and on_step_complete:
                        on_step_complete(0, True, "浏览器已自动重新初始化，跳过OPEN_BROWSER步骤")
                else:
                    # 否则使用默认配置初始化
                    success = self._engine.initialize(page_type='chromium')
                
                if not success:
                    if on_flow_complete:
                        on_flow_complete(False)
                    return
        
        self._is_executing = True
        self._current_step_index = -1
        
        # 执行流程中的每个步骤
        flow_success = True
        
        # 执行指针，用于跳转执行
        execution_pointer = 0
        
        # 执行栈，用于处理条件和循环嵌套
        execution_stack = []
        
        # 清空临时变量
        self._variable_manager.clear_scope(VariableScope.TEMPORARY)
        
        # 初始化错误追踪
        retry_counts = {}  # 记录每个步骤的重试次数
        
        while execution_pointer < len(self._steps) and not self._engine.should_stop() and self._is_executing:
            self._current_step_index = execution_pointer
            step = self._steps[execution_pointer]
            
            # 初始化/获取当前步骤的重试计数
            step_key = f"{execution_pointer}_{step.get('action_id')}"
            retry_counts.setdefault(step_key, 0)
            
            # 检查步骤是否启用
            if not step.get("enabled", True):
                if on_step_complete:
                    on_step_complete(execution_pointer, True, "步骤已禁用，已跳过")
                execution_pointer += 1
                continue
            
            action_id = step.get("action_id")
            parameters = step.get("parameters", {})
            
            # 如果有变量管理器，处理参数中的变量引用
            processed_parameters = self._process_parameters(parameters)
            
            # 通知步骤开始
            if on_step_start:
                on_step_start(execution_pointer, step)
            
            # 处理特殊控制流步骤
            if action_id == "IF_CONDITION":
                # 评估条件
                try:
                    condition_result, condition_message = self._evaluate_condition(processed_parameters)
                    
                    # 通知步骤完成
                    if on_step_complete:
                        on_step_complete(execution_pointer, True, f"条件判断: {condition_message}")
                    
                    # 将条件结果和当前位置压入栈
                    execution_stack.append({
                        "type": "if",
                        "condition_result": condition_result,
                        "if_pointer": execution_pointer,
                        "in_else_branch": False
                    })
                except Exception as e:
                    flow_success = False
                    if on_step_complete:
                        on_step_complete(execution_pointer, False, f"条件评估错误: {str(e)}")
                    # 根据错误处理策略决定下一步操作
                    strategy, jump_to = self._handle_error(e, step, retry_counts[step_key], 3)
                    retry_counts[step_key] += 1
                    
                    if strategy == ErrorStrategy.STOP:
                        break
                    elif strategy == ErrorStrategy.RETRY:
                        continue  # 重试当前步骤
                    elif strategy == ErrorStrategy.JUMP:
                        execution_pointer = jump_to
                        continue
                    # 其他情况（如CONTINUE），跳过当前步骤继续执行
                
                execution_pointer += 1
            
            elif action_id == "ELSE_CONDITION":
                # 检查栈顶是否为 IF
                if execution_stack and execution_stack[-1]["type"] == "if":
                    stack_frame = execution_stack[-1]
                    
                    # 如果条件为真，则跳过 ELSE 块
                    if stack_frame["condition_result"]:
                        # 寻找对应的 END_IF_CONDITION
                        nesting_level = 1
                        temp_pointer = execution_pointer + 1
                        
                        while temp_pointer < len(self._steps) and nesting_level > 0:
                            temp_step = self._steps[temp_pointer]
                            temp_action_id = temp_step.get("action_id")
                            
                            if temp_action_id == "IF_CONDITION":
                                nesting_level += 1
                            elif temp_action_id == "END_IF_CONDITION":
                                nesting_level -= 1
                            
                            temp_pointer += 1
                        
                        if nesting_level == 0:
                            # 找到了 END_IF_CONDITION，跳到那里
                            execution_pointer = temp_pointer
                            # 更新栈帧，表示现在在 ELSE 分支
                            stack_frame["in_else_branch"] = True
                        else:
                            # 没找到匹配的 END_IF_CONDITION
                            if on_step_complete:
                                on_step_complete(execution_pointer, False, "找不到匹配的 END_IF_CONDITION")
                            flow_success = False
                            break
                    else:
                        # 条件为假，继续执行 ELSE 块
                        stack_frame["in_else_branch"] = True
                        execution_pointer += 1
                else:
                    # 栈为空或栈顶不是 IF
                    if on_step_complete:
                        on_step_complete(execution_pointer, False, "ELSE 没有匹配的 IF")
                    flow_success = False
                    break
                
                # 通知步骤完成
                if on_step_complete:
                    on_step_complete(execution_pointer, True, "ELSE 条件处理完成")
            
            elif action_id == "END_IF_CONDITION":
                # 检查栈顶是否为 IF
                if execution_stack and execution_stack[-1]["type"] == "if":
                    # 弹出栈顶 IF
                    execution_stack.pop()
                    execution_pointer += 1
                    if on_step_complete:
                        on_step_complete(execution_pointer, True, "IF 块结束")
                else:
                    # 栈为空或栈顶不是 IF
                    if on_step_complete:
                        on_step_complete(execution_pointer, False, "END_IF 没有匹配的 IF")
                    flow_success = False
                    break
            
            # Try-Catch-Finally 控制流
            elif action_id == "TRY_BLOCK":
                # 创建新的 try 块
                try_block = TryCatchBlock(
                    try_steps=[],  # 将在执行过程中填充
                    catch_steps=processed_parameters.get("catch_steps", []),
                    finally_steps=processed_parameters.get("finally_steps", [])
                )
                self._active_try_blocks.append(try_block)
                execution_pointer += 1
                if on_step_complete:
                    on_step_complete(execution_pointer, True, "进入 TRY 块")
            
            elif action_id == "CATCH_BLOCK":
                # 如果没有活动的try块，或未捕获异常，则跳过catch块
                if not self._active_try_blocks or not self._active_try_blocks[-1].exception:
                    # 寻找对应的 END_CATCH_BLOCK 或 FINALLY_BLOCK
                    nesting_level = 1
                    temp_pointer = execution_pointer + 1
                    
                    while temp_pointer < len(self._steps) and nesting_level > 0:
                        temp_step = self._steps[temp_pointer]
                        temp_action_id = temp_step.get("action_id")
                        
                        if temp_action_id in ["FINALLY_BLOCK", "END_TRY_BLOCK"]:
                            break
                        
                        temp_pointer += 1
                    
                    execution_pointer = temp_pointer
                else:
                    # 有捕获的异常，执行catch块
                    self._active_try_blocks[-1].catch_executed = True
                    # 将异常信息存储为变量
                    if self._active_try_blocks[-1].exception:
                        error_type = type(self._active_try_blocks[-1].exception).__name__
                        error_message = str(self._active_try_blocks[-1].exception)
                        
                        self._variable_manager.create_variable(
                            "error_type", error_type, "string", VariableScope.TEMPORARY
                        )
                        self._variable_manager.create_variable(
                            "error_message", error_message, "string", VariableScope.TEMPORARY
                        )
                    
                    execution_pointer += 1
                
                if on_step_complete:
                    on_step_complete(execution_pointer, True, "CATCH 块处理")
            
            elif action_id == "FINALLY_BLOCK":
                # 标记finally块已执行
                if self._active_try_blocks:
                    self._active_try_blocks[-1].finally_executed = True
                
                execution_pointer += 1
                if on_step_complete:
                    on_step_complete(execution_pointer, True, "进入 FINALLY 块")
            
            elif action_id == "END_TRY_BLOCK":
                # 结束try-catch-finally块
                if self._active_try_blocks:
                    # 如果有finally块但未执行，应执行finally
                    try_block = self._active_try_blocks[-1]
                    if try_block.finally_steps and not try_block.finally_executed:
                        # 执行finally块
                        # 这里需要流程控制器支持跳转到指定步骤列表
                        # 暂时简化处理，实际实现需要更复杂的逻辑
                        pass
                    
                    # 弹出当前try块
                    self._active_try_blocks.pop()
                
                execution_pointer += 1
                if on_step_complete:
                    on_step_complete(execution_pointer, True, "TRY-CATCH-FINALLY 块结束")
            
            # 变量操作步骤
            elif action_id == "SET_VARIABLE":
                try:
                    var_name = processed_parameters.get("variable_name", "")
                    var_value = processed_parameters.get("variable_value")
                    var_type = processed_parameters.get("variable_type")
                    var_scope = processed_parameters.get("variable_scope", VariableScope.GLOBAL)
                    var_description = processed_parameters.get("variable_description", "")
                    
                    # 检查变量是否已存在
                    existing_var = self._variable_manager.get_variable(var_name)
                    if existing_var is not None:
                        # 更新变量
                        success, message = self._variable_manager.set_variable(var_name, var_value)
                    else:
                        # 创建新变量
                        success, message = self._variable_manager.create_variable(
                            var_name, var_value, var_type, var_scope, var_description
                        )
                    
                    if on_step_complete:
                        on_step_complete(execution_pointer, success, message)
                    
                    if not success:
                        flow_success = False
                except Exception as e:
                    flow_success = False
                    if on_step_complete:
                        on_step_complete(execution_pointer, False, f"设置变量错误: {str(e)}")
                
                execution_pointer += 1
            
            elif action_id == "DELETE_VARIABLE":
                try:
                    var_name = processed_parameters.get("variable_name", "")
                    var_scope = processed_parameters.get("variable_scope")
                    
                    success, message = self._variable_manager.delete_variable(var_name, var_scope)
                    
                    if on_step_complete:
                        on_step_complete(execution_pointer, success, message)
                    
                    if not success:
                        flow_success = False
                except Exception as e:
                    flow_success = False
                    if on_step_complete:
                        on_step_complete(execution_pointer, False, f"删除变量错误: {str(e)}")
                
                execution_pointer += 1
            
            elif action_id == "DELETE_FLOW":
                try:
                    confirm = processed_parameters.get("confirm", "否")
                    clear_variables = processed_parameters.get("clear_variables", "否")
                    
                    if confirm == "是":
                        # 记录操作，但实际删除操作将在流程执行完成后进行
                        self._pending_delete_flow = True
                        self._pending_clear_variables = (clear_variables == "是")
                        
                        if on_step_complete:
                            on_step_complete(execution_pointer, True, "流程将在执行完成后删除")
                    else:
                        if on_step_complete:
                            on_step_complete(execution_pointer, True, "流程删除操作已取消")
                except Exception as e:
                    flow_success = False
                    if on_step_complete:
                        on_step_complete(execution_pointer, False, f"删除流程错误: {str(e)}")
                
                execution_pointer += 1
            
            elif action_id == "CLEAR_VARIABLES":
                try:
                    var_scope = processed_parameters.get("variable_scope", VariableScope.TEMPORARY)
                    
                    self._variable_manager.clear_scope(var_scope)
                    
                    if on_step_complete:
                        on_step_complete(execution_pointer, True, f"已清空作用域 {var_scope} 的所有变量")
                except Exception as e:
                    flow_success = False
                    if on_step_complete:
                        on_step_complete(execution_pointer, False, f"清空变量错误: {str(e)}")
                
                execution_pointer += 1
            
            # 循环控制
            elif action_id == "FOR_LOOP":
                # 循环参数
                loop_variable = processed_parameters.get("loop_variable", "i")
                start_value = processed_parameters.get("start_value", 0)
                end_value = processed_parameters.get("end_value", 10)
                step_value = processed_parameters.get("step_value", 1)
                
                # 创建或更新循环变量
                if isinstance(start_value, str):
                    try:
                        start_value = int(start_value)
                    except ValueError:
                        if on_step_complete:
                            on_step_complete(execution_pointer, False, f"无效的循环起始值: {start_value}")
                        flow_success = False
                        break
                
                self._variable_manager.create_variable(
                    loop_variable, start_value, "integer", VariableScope.LOCAL
                )
                
                # 将循环状态压入栈
                execution_stack.append({
                    "type": "for_loop",
                    "loop_variable": loop_variable,
                    "current_value": start_value,
                    "end_value": end_value,
                    "step_value": step_value,
                    "loop_start": execution_pointer
                })
                
                execution_pointer += 1
                if on_step_complete:
                    on_step_complete(execution_pointer, True, 
                                    f"开始循环: {loop_variable}={start_value} 到 {end_value}, 步长={step_value}")
            
            elif action_id == "END_FOR_LOOP":
                # 检查栈顶是否为 FOR_LOOP
                if execution_stack and execution_stack[-1]["type"] == "for_loop":
                    loop_frame = execution_stack[-1]
                    
                    # 更新循环变量
                    new_value = loop_frame["current_value"] + loop_frame["step_value"]
                    self._variable_manager.set_variable(
                        loop_frame["loop_variable"], new_value, VariableScope.LOCAL
                    )
                    loop_frame["current_value"] = new_value
                    
                    # 检查循环是否结束
                    step_is_positive = loop_frame["step_value"] > 0
                    if (step_is_positive and new_value <= loop_frame["end_value"]) or \
                       (not step_is_positive and new_value >= loop_frame["end_value"]):
                        # 继续循环，跳回循环开始处
                        execution_pointer = loop_frame["loop_start"] + 1
                    else:
                        # 循环结束，弹出栈帧
                        execution_stack.pop()
                        execution_pointer += 1
                    
                    if on_step_complete:
                        on_step_complete(execution_pointer, True, 
                                        f"循环迭代: {loop_frame['loop_variable']}={new_value}")
                else:
                    # 栈为空或栈顶不是 FOR_LOOP
                    if on_step_complete:
                        on_step_complete(execution_pointer, False, "END_FOR_LOOP 没有匹配的 FOR_LOOP")
                    flow_success = False
                    break
            
            elif action_id == "FOREACH_LOOP":
                # 遍历集合的循环
                item_variable = processed_parameters.get("item_variable", "item")
                collection_variable = processed_parameters.get("collection_variable", "")
                index_variable = processed_parameters.get("index_variable")
                
                # 获取要遍历的集合
                collection = self._variable_manager.get_variable(collection_variable)
                if collection is None:
                    if on_step_complete:
                        on_step_complete(execution_pointer, False, f"集合变量不存在: {collection_variable}")
                    flow_success = False
                    break
                
                if not isinstance(collection, (list, tuple, dict, str)):
                    if on_step_complete:
                        on_step_complete(execution_pointer, False, 
                                        f"变量 {collection_variable} 不是可遍历的集合")
                    flow_success = False
                    break
                
                # 创建循环框架并直接加入栈中
                loop_frame = {
                    "type": "foreach",  # 直接使用foreach类型，不用pending状态
                    "item_variable": item_variable,
                    "collection_variable": collection_variable,
                    "index_variable": index_variable,
                    "loop_start": execution_pointer,
                    "collection": collection,
                    "current_index": 0
                }
                execution_stack.append(loop_frame)
                
                # 设置第一个项目
                if isinstance(collection, (list, tuple, str)):
                    if collection:  # 集合非空
                        self._variable_manager.create_variable(
                            item_variable, collection[0], None, VariableScope.LOCAL
                        )
                        if index_variable:
                            self._variable_manager.create_variable(
                                index_variable, 0, "integer", VariableScope.LOCAL
                            )
                    else:  # 空集合，跳过循环体
                        # 寻找对应的 END_FOREACH_LOOP
                        nesting_level = 1
                        temp_pointer = execution_pointer + 1
                        
                        while temp_pointer < len(self._steps) and nesting_level > 0:
                            temp_step = self._steps[temp_pointer]
                            temp_action_id = temp_step.get("action_id")
                            
                            if temp_action_id == "FOREACH_LOOP":
                                nesting_level += 1
                            elif temp_action_id == "END_FOREACH_LOOP":
                                nesting_level -= 1
                            
                            temp_pointer += 1
                        
                        if nesting_level == 0:
                            execution_stack.pop()  # 移除循环帧
                            execution_pointer = temp_pointer
                            if on_step_complete:
                                on_step_complete(execution_pointer, True, "跳过空集合的循环")
                            continue
                elif isinstance(collection, dict):
                    keys = list(collection.keys())
                    if keys:  # 字典非空
                        first_key = keys[0]
                        self._variable_manager.create_variable(
                            item_variable, collection[first_key], None, VariableScope.LOCAL
                        )
                        if index_variable:
                            self._variable_manager.create_variable(
                                index_variable, first_key, None, VariableScope.LOCAL
                            )
                    else:  # 空字典，跳过循环体
                        # 寻找对应的 END_FOREACH_LOOP
                        nesting_level = 1
                        temp_pointer = execution_pointer + 1
                        
                        while temp_pointer < len(self._steps) and nesting_level > 0:
                            temp_step = self._steps[temp_pointer]
                            temp_action_id = temp_step.get("action_id")
                            
                            if temp_action_id == "FOREACH_LOOP":
                                nesting_level += 1
                            elif temp_action_id == "END_FOREACH_LOOP":
                                nesting_level -= 1
                            
                            temp_pointer += 1
                        
                        if nesting_level == 0:
                            execution_stack.pop()  # 移除循环帧
                            execution_pointer = temp_pointer
                            if on_step_complete:
                                on_step_complete(execution_pointer, True, "跳过空字典的循环")
                            continue
                
                execution_pointer += 1
                if on_step_complete:
                    on_step_complete(execution_pointer, True, f"开始遍历: {collection_variable}")
            
            elif action_id == "END_FOREACH_LOOP":
                # 检查栈顶是否为 FOREACH
                if execution_stack and execution_stack[-1]["type"] == "foreach":
                    loop_frame = execution_stack[-1]
                    collection = loop_frame["collection"]
                    
                    # 增加索引
                    new_index = loop_frame["current_index"] + 1
                    
                    # 检查是否已遍历完所有元素
                    if isinstance(collection, (list, tuple, str)) and new_index < len(collection):
                        # 更新项目变量和索引变量
                        self._variable_manager.set_variable(
                            loop_frame["item_variable"], collection[new_index], VariableScope.LOCAL
                        )
                        if loop_frame["index_variable"]:
                            self._variable_manager.set_variable(
                                loop_frame["index_variable"], new_index, VariableScope.LOCAL
                            )
                        
                        loop_frame["current_index"] = new_index
                        execution_pointer = loop_frame["loop_start"] + 1
                    elif isinstance(collection, dict):
                        keys = list(collection.keys())
                        if new_index < len(keys):
                            key = keys[new_index]
                            self._variable_manager.set_variable(
                                loop_frame["item_variable"], collection[key], VariableScope.LOCAL
                            )
                            if loop_frame["index_variable"]:
                                self._variable_manager.set_variable(
                                    loop_frame["index_variable"], key, VariableScope.LOCAL
                                )
                            
                            loop_frame["current_index"] = new_index
                            execution_pointer = loop_frame["loop_start"] + 1
                        else:
                            # 遍历完成，弹出栈帧
                            execution_stack.pop()
                            execution_pointer += 1
                    else:
                        # 列表、元组或字符串遍历结束，弹出栈帧
                        execution_stack.pop()
                        execution_pointer += 1
                    
                    if on_step_complete:
                        on_step_complete(execution_pointer, True, "FOREACH 循环迭代")
                else:
                    # 栈为空或栈顶不是 FOREACH
                    if on_step_complete:
                        on_step_complete(execution_pointer, False, "END_FOREACH_LOOP 没有匹配的 FOREACH_LOOP")
                    flow_success = False
                    break
            
            # 常规动作
            else:
                try:
                    # 执行动作
                    success, message = self._engine.execute_action(action_id, processed_parameters)
                    
                    # 检查是否为信息获取操作，如果是则保存结果到变量
                    if success and isinstance(message, dict) and "save_to_variable" in message:
                        variable_name = message["save_to_variable"]
                        if "info" in message:
                            self._variable_manager.set_variable(variable_name, message["info"])
                            # 更新消息为更友好的提示
                            message = message.get("message", f"信息已保存到变量: {variable_name}")
                    
                    # 通知步骤完成
                    if on_step_complete:
                        on_step_complete(execution_pointer, success, message)
                    
                    if not success:
                        flow_success = False
                    
                    # 处理try-catch
                    execution_pointer += 1
                    
                except Exception as e:
                    # 错误处理
                    flow_success = False
                    
                    # 检查是否是连接断开的错误，如果是则重新初始化浏览器
                    error_str = str(e)
                    connection_lost = any(msg in error_str for msg in [
                        "连接已断开", "Connection lost", "Target closed", 
                        "Page crashed", "Session closed", "WebSocketClosed"
                    ])
                    
                    if connection_lost:
                        if on_step_complete:
                            on_step_complete(execution_pointer, False, f"浏览器连接已断开，尝试重新初始化")
                        
                        # 关闭现有连接
                        self._engine.close()
                        
                        # 重新初始化浏览器
                        success = self._engine.initialize(page_type='chromium')
                        
                        if success:
                            if on_step_complete:
                                on_step_complete(execution_pointer, True, "浏览器已成功重新初始化，继续执行")
                            continue  # 重试当前步骤
                        else:
                            if on_step_complete:
                                on_step_complete(execution_pointer, False, "浏览器重新初始化失败，停止执行")
                            break  # 停止执行
                    
                    # 检查是否在try块中
                    in_try_block = False
                    for try_block in reversed(self._active_try_blocks):
                        if not try_block.catch_executed and not try_block.exception:
                            try_block.exception = e
                            in_try_block = True
                            break
                    
                    if in_try_block:
                        # 如果在try块中发生异常，记录异常但不中断执行
                        self._error_handler.record_error(execution_pointer, action_id, str(e))
                        return False, f"步骤执行错误: {str(e)}"
                    else:
                        raise  # 否则向上传递异常
        
        # 流程执行完成
        self._is_executing = False
        
        # 处理挂起的删除流程操作
        if hasattr(self, '_pending_delete_flow') and self._pending_delete_flow:
            success, message = self.delete_flow(self._pending_clear_variables)
            self._pending_delete_flow = False
            self._pending_clear_variables = False
            if not success:
                # 记录删除失败但不影响流程执行结果
                self._error_handler.log_error("ERROR", f"流程删除失败: {message}")
        
        if on_flow_complete:
            on_flow_complete(flow_success)
    
    def stop_execution(self) -> None:
        """停止执行"""
        self._engine.request_stop()
        # 不要在这里设置 _is_executing = False，让它在 execute_flow 方法结束时设置
    
    def cleanup(self) -> None:
        """清理资源"""
        if hasattr(self._engine, 'close'):
            self._engine.close()
    
    def is_executing(self) -> bool:
        """是否正在执行"""
        return self._is_executing
    
    def get_current_step_index(self) -> int:
        """获取当前执行的步骤索引"""
        return self._current_step_index
    
    # 变量管理相关方法
    def get_variable(self, name: str, default_value: Any = None) -> Any:
        """获取变量值"""
        return self._variable_manager.get_variable(name, default_value)
    
    def set_variable(self, name: str, value: Any, scope: Optional[str] = None) -> Tuple[bool, str]:
        """设置变量值"""
        return self._variable_manager.set_variable(name, value, scope)
    
    def create_variable(self, name: str, value: Any, var_type: str = None, 
                      scope: str = VariableScope.GLOBAL) -> Tuple[bool, str]:
        """创建新变量"""
        return self._variable_manager.create_variable(name, value, var_type, scope)
    
    def delete_variable(self, name: str, scope: Optional[str] = None) -> Tuple[bool, str]:
        """删除变量"""
        return self._variable_manager.delete_variable(name, scope)
    
    def get_all_variables(self, scope: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
        """获取所有变量"""
        return self._variable_manager.get_all_variables(scope)
    
    def import_variables(self, json_str: str, scope: str = VariableScope.GLOBAL) -> Tuple[bool, str]:
        """从JSON导入变量"""
        return self._variable_manager.import_variables(json_str, scope)
    
    def export_variables(self, scope: Optional[str] = None) -> str:
        """将变量导出为JSON"""
        return self._variable_manager.export_variables(scope)
    
    # 错误处理相关方法
    def get_error_logs(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """获取错误日志"""
        return self._error_handler.get_error_logs(limit)
    
    def get_error_statistics(self) -> Dict[str, int]:
        """获取错误统计信息"""
        return self._error_handler.get_error_statistics()
    
    # 内部辅助方法
    def _process_parameters(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """处理参数中的变量引用"""
        processed = copy.deepcopy(parameters)
        
        for key, value in processed.items():
            if isinstance(value, str) and "${" in value:
                processed[key] = self._variable_manager.process_template(value)
        
        return processed
    
    def _evaluate_condition(self, condition_params: Dict[str, Any]) -> Tuple[bool, str]:
        """评估条件表达式"""
        condition_type = condition_params.get("condition_type")
        if not condition_type:
            return False, "缺少条件类型"
        
        return self._condition_evaluator.evaluate_condition(condition_params)
    
    def _handle_error(self, error: Exception, step_data: Dict[str, Any], 
                     retry_count: int, max_retries: int) -> Tuple[ErrorStrategy, Optional[int]]:
        """处理执行错误"""
        return self._error_handler.handle_error(error, step_data, retry_count, max_retries)
    
    def _log_error(self, level: str, message: str) -> None:
        """记录错误日志（回调函数）"""
        # 在这里可以将日志转发到UI或其他地方
        pass
    
    def delete_flow(self, clear_variables: bool = False) -> Tuple[bool, str]:
        """
        删除当前流程
        
        Args:
            clear_variables: 是否同时清除所有变量
            
        Returns:
            (成功标志, 消息)
        """
        try:
            # 如果正在执行，先停止
            if self._is_executing:
                self.stop_execution()
            
            # 清空步骤
            self._steps = []
            self._current_step_index = -1
            
            # 清空活动的 try-catch 块
            self._active_try_blocks = []
            
            # 如果需要，清空变量
            if clear_variables:
                self._variable_manager.clear_scope(VariableScope.GLOBAL)
                self._variable_manager.clear_scope(VariableScope.LOCAL)
                self._variable_manager.clear_scope(VariableScope.TEMPORARY)
            
            # 重置流程名称
            self._flow_name = "新建流程"
            
            # 清空错误日志
            self._error_handler.clear_logs()
            
            return True, "流程已删除"
        except Exception as e:
            return False, f"删除流程失败: {str(e)}"
    
    def _prepare_browser_config(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        根据步骤参数准备浏览器配置。
        
        Args:
            parameters: OPEN_BROWSER步骤参数
            
        Returns:
            DrissionPage的浏览器配置字典，包含options键
        """
        # 导入ChromiumOptions
        from DrissionPage import ChromiumOptions
        
        # 处理参数中的变量引用
        processed_parameters = self._process_parameters(parameters)
        
        # 创建ChromiumOptions对象
        options = ChromiumOptions()
        
        # 设置浏览器类型
        browser_type = processed_parameters.get("browser_type", "Chrome")
        if browser_type == "Edge":
            options.set_browser_path("edge")
        elif browser_type == "Firefox":
            options.set_browser_path("firefox")
        # Chrome是默认值，不需要特别设置
        
        # 设置无头模式
        headless = processed_parameters.get("headless", "否") == "是"
        if headless:
            options.headless(True)
        
        # 设置窗口尺寸
        window_size = processed_parameters.get("window_size", "1280,720")
        if window_size:
            try:
                width, height = map(int, window_size.split(','))
                options.set_argument('--window-size', f'{width},{height}')
            except ValueError:
                # 使用默认值
                options.set_argument('--window-size', '1280,720')
        
        # 设置用户代理
        user_agent = processed_parameters.get("user_agent", "")
        if user_agent:
            options.set_user_agent(user_agent)
        
        # 设置代理服务器
        proxy = processed_parameters.get("proxy", "")
        if proxy:
            options.set_proxy(proxy)
        
        # 设置隐私模式
        incognito = processed_parameters.get("incognito", "否") == "是"
        if incognito:
            options.incognito(True)
        
        # 设置扩展程序
        load_extension = processed_parameters.get("load_extension", "")
        if load_extension:
            extensions = [path.strip() for path in load_extension.split(',')]
            for ext in extensions:
                options.add_extension(ext)
        
        # 设置自定义参数
        custom_args = processed_parameters.get("custom_args", "")
        if custom_args:
            args = [arg.strip() for arg in custom_args.split(',')]
            for arg in args:
                if arg.startswith('--'):
                    options.set_argument(arg)
                else:
                    options.set_argument(f'--{arg}')
        
        # 返回包含options的配置字典
        return {'options': options}
    
    def clear_variables(self) -> None:
        """清空所有作用域的变量"""
        self._variable_manager.clear_scope(VariableScope.LOCAL)
        self._variable_manager.clear_scope(VariableScope.TEMPORARY)
        self._variable_manager.clear_scope(VariableScope.GLOBAL)
    
    def create_advanced_interactions_demo(self) -> bool:
        """
        创建演示高级页面交互功能的示例流程
        
        Returns:
            是否成功创建示例流程
        """
        try:
            # 清空现有流程
            self.delete_flow(False)
            self.clear_variables()
            
            # 创建流程需要的变量
            self.create_variable("search_term", "DrissionPage 自动化", "string", VariableScope.GLOBAL)
            self.create_variable("search_term2", "Python编程", "string", VariableScope.GLOBAL)
            self.create_variable("screenshot_dir", "screenshots", "string", VariableScope.GLOBAL)
            self.create_variable("scroll_distance", 300, "integer", VariableScope.GLOBAL)
            
            # 步骤1: 打开浏览器访问百度
            self.add_step("OPEN_BROWSER", {
                "url": "https://www.baidu.com",
                "browser_type": "Chrome",
                "headless": "否",
                "window_size": "1280,720"
            })
            
            # 步骤2: 输入搜索关键词（使用变量）
            self.add_step("ELEMENT_INPUT", {
                "locator_strategy": "ID",
                "locator_value": "kw",
                "text_to_input": "${search_term}",  # 使用变量
                "timeout": 10
            })
            
            # 步骤3: 点击搜索按钮
            self.add_step("ELEMENT_CLICK", {
                "locator_strategy": "ID",
                "locator_value": "su",
                "timeout": 10
            })
            
            # 等待搜索加载
            self.add_step("LOG_MESSAGE", {
                "message": "等待搜索 '${search_term}' 的结果加载中..."
            })
            
            # 步骤4: 等待搜索结果加载
            self.add_step("WAIT_FOR_ELEMENT", {
                "locator_strategy": "css",
                "locator_value": "#content_left",
                "timeout": 15
            })
            
            # 添加短暂等待，确保页面渲染完成
            self.add_step("LOG_MESSAGE", {
                "message": "等待页面渲染完成..."
            })
            
            # 步骤5: 滚动页面（使用变量）
            self.add_step("SCROLL_PAGE", {
                "direction": "down",
                "distance": "${scroll_distance}"  # 使用变量
            })
            
            # 步骤6: 截图保存搜索结果（使用变量构建路径）
            self.add_step("TAKE_SCREENSHOT", {
                "save_path": "${screenshot_dir}/search_results.png",  # 使用变量构建路径
                "save_full_page": "是"
            })
            
            # 步骤7: 滚动回顶部（使用变量）
            self.add_step("SCROLL_PAGE", {
                "direction": "up",
                "distance": "${scroll_distance}"  # 使用变量
            })
            
            # 步骤8: 鼠标悬停在百度Logo上
            self.add_step("MOUSE_HOVER", {
                "locator_strategy": "ID",
                "locator_value": "s_lg_img",
                "duration": 1.0
            })
            
            # 创建一个临时变量来存储当前搜索词
            self.add_step("SET_VARIABLE", {
                "variable_name": "current_search",
                "variable_value": "${search_term2}",
                "variable_scope": VariableScope.TEMPORARY
            })
            
            # 步骤9: 再次搜索不同关键词（使用临时变量）
            self.add_step("ELEMENT_INPUT", {
                "locator_strategy": "ID",
                "locator_value": "kw",
                "text_to_input": "${current_search}",  # 使用临时变量
                "timeout": 10
            })
            
            # 步骤10: 点击搜索按钮
            self.add_step("ELEMENT_CLICK", {
                "locator_strategy": "ID",
                "locator_value": "su",
                "timeout": 10
            })
            
            # 记录搜索内容
            self.add_step("LOG_MESSAGE", {
                "message": "已完成两次搜索：'${search_term}' 和 '${current_search}'"
            })
            
            # 流程创建成功
            self._flow_modified = True
            self._current_file_path = None
            return True
            
        except Exception as e:
            print(f"创建高级交互演示流程失败: {str(e)}")
            return False
    
    def create_basic_demo(self) -> bool:
        """
        创建基本演示流程
        
        Returns:
            是否成功创建示例流程
        """
        try:
            # 清空现有流程
            self.delete_flow(False)
            self.clear_variables()
            
            # 步骤1: 打开浏览器访问百度
            self.add_step("OPEN_BROWSER", {
                "url": "https://www.baidu.com",
                "browser_type": "Chrome",
                "headless": "否",
                "window_size": "1280,720"
            })
            
            # 步骤2: 输入搜索关键词
            self.add_step("ELEMENT_INPUT", {
                "locator_strategy": "ID",
                "locator_value": "kw",
                "text_to_input": "Python 编程"
            })
            
            # 步骤3: 点击搜索按钮
            self.add_step("ELEMENT_CLICK", {
                "locator_strategy": "ID",
                "locator_value": "su"
            })
            
            # 步骤4: 等待结果加载
            self.add_step("LOG_MESSAGE", {
                "message": "等待搜索结果加载..."
            })
            
            # 步骤5: 截图保存结果
            self.add_step("TAKE_SCREENSHOT", {
                "save_path": "screenshots/search_results.png"
            })
            
            # 步骤6: 记录完成日志
            self.add_step("LOG_MESSAGE", {
                "message": "基础演示完成"
            })
            
            return True
            
        except Exception as e:
            print(f"创建基本演示失败: {str(e)}")
            return False
            
    def create_javascript_demo(self) -> bool:
        """
        创建JavaScript演示流程
        
        Returns:
            是否成功创建示例流程
        """
        try:
            # 清空现有流程
            self.delete_flow(False)
            self.clear_variables()
            
            # 步骤1: 打开浏览器访问百度
            self.add_step("OPEN_BROWSER", {
                "url": "https://www.baidu.com",
                "browser_type": "Chrome",
                "headless": "否",
                "window_size": "1280,720"
            })
            
            # 步骤2: 执行JS修改页面标题
            self.add_step("EXECUTE_JAVASCRIPT", {
                "js_code": "document.title = 'DrissionPage自动化工具 - 修改的标题'; return document.title;"
            })
            
            # 步骤3: 记录日志
            self.add_step("LOG_MESSAGE", {
                "message": "已通过JavaScript修改页面标题"
            })
            
            # 步骤4: 使用JS输入搜索关键词
            self.add_step("EXECUTE_JAVASCRIPT", {
                "js_code": "document.getElementById('kw').value = 'DrissionPage JavaScript自动化'; return true;"
            })
            
            # 步骤5: 使用JS点击搜索按钮
            self.add_step("EXECUTE_JAVASCRIPT", {
                "js_code": "document.getElementById('su').click(); return true;"
            })
            
            # 步骤6: 等待搜索结果加载
            self.add_step("WAIT_SECONDS", {
                "seconds": "3"
            })
            
            # 步骤7: 使用JS获取搜索结果数量
            self.add_step("EXECUTE_JAVASCRIPT", {
                "js_code": "let results = document.querySelectorAll('#content_left .c-container'); return `找到 ${results.length} 个搜索结果`;"
            })
            
            # 步骤8: 截图保存结果
            self.add_step("TAKE_SCREENSHOT", {
                "save_path": "screenshots/js_modified_page.png"
            })
            
            # 步骤9: 使用JS修改页面样式
            self.add_step("EXECUTE_JAVASCRIPT", {
                "js_code": "document.body.style.backgroundColor = '#f0f8ff'; document.querySelectorAll('#content_left .c-container').forEach(item => { item.style.border = '2px solid #4682b4'; item.style.margin = '10px'; item.style.padding = '10px'; item.style.borderRadius = '8px'; item.style.backgroundColor = 'white'; }); return 'CSS样式已修改';"
            })
            
            # 步骤10: 记录完成日志
            self.add_step("LOG_MESSAGE", {
                "message": "JavaScript演示完成"
            })
            
            # 步骤11: 截图保存修改后的页面
            self.add_step("TAKE_SCREENSHOT", {
                "save_path": "screenshots/js_styled_page.png"
            })
            
            return True
            
        except Exception as e:
            print(f"创建JavaScript演示失败: {str(e)}")
            return False

    def _execute_step(self, step_index: int) -> Tuple[bool, Any]:
        """
        执行指定的步骤。
        
        Args:
            step_index: 步骤索引
            
        Returns:
            (是否成功, 结果或错误信息)
        """
        if not 0 <= step_index < len(self._steps):
            return False, f"无效的步骤索引: {step_index}"
        
        # 检查是否应该停止执行
        if self._engine.should_stop():
            return False, "执行已被用户停止"
        
        step = self._steps[step_index]
        action_id = step.get("action_id")
        parameters = step.get("parameters", {})
        
        # 处理变量表达式（如果有）
        processed_parameters = self._variable_manager.process_parameter_variables(parameters)
        
        try:
            # 执行动作
            success, message = self._engine.execute_action(action_id, processed_parameters)
            
            # 检查是否为信息获取操作，如果是则保存结果到变量
            if success and isinstance(message, dict) and "save_to_variable" in message:
                variable_name = message["save_to_variable"]
                if "info" in message:
                    self._variable_manager.set_variable(variable_name, message["info"])
                    # 更新消息为更友好的提示
                    message = message.get("message", f"信息已保存到变量: {variable_name}")
            
            return success, message
            
        except Exception as e:
            if hasattr(self, '_in_try_block') and self._in_try_block:
                # 如果在try块中发生异常，记录异常但不中断执行
                self._error_handler.record_error(step_index, action_id, str(e))
                return False, f"步骤执行错误: {str(e)}"
            else:
                raise  # 否则向上传递异常

    def get_variable_manager(self) -> 'VariableManager':
        """
        获取变量管理器实例
        
        Returns:
            变量管理器对象
        """
        return self._variable_manager

    def create_advanced_mouse_demo(self) -> bool:
        """
        创建演示高级鼠标操作的示例流程
        
        Returns:
            是否成功创建示例流程
        """
        try:
            # 清空现有流程
            self.delete_flow(False)
            self.clear_variables()
            
            # 创建流程需要的变量
            self.create_variable("test_url", "https://www.w3schools.com/html/html5_draganddrop.asp", "string", VariableScope.GLOBAL)
            
            # 步骤1: 打开浏览器访问拖放测试页面
            self.add_step("OPEN_BROWSER", {
                "url": "${test_url}",
                "browser_type": "Chrome",
                "headless": "否",
                "window_size": "1280,720"
            })
            
            # 步骤2: 等待元素加载
            self.add_step("WAIT_FOR_ELEMENT", {
                "locator_strategy": "id",
                "locator_value": "div1",
                "timeout": 10
            })
            
            # 记录日志
            self.add_step("LOG_MESSAGE", {
                "message": "准备演示拖放操作..."
            })
            
            # 步骤3: 拖放操作
            self.add_step("MOUSE_DRAG_DROP", {
                "source_locator_strategy": "id",
                "source_locator_value": "drag1",
                "target_locator_strategy": "id",
                "target_locator_value": "div2",
                "smooth": "是",
                "duration": 1.0
            })
            
            # 记录日志
            self.add_step("LOG_MESSAGE", {
                "message": "拖放操作完成，准备进行双击操作"
            })
            
            # 等待一下
            self.add_step("WAIT_SECONDS", {
                "seconds": "2"
            })
            
            # 步骤4: 右键点击操作
            self.add_step("MOUSE_RIGHT_CLICK", {
                "locator_strategy": "id",
                "locator_value": "div1",
                "timeout": 10
            })
            
            # 记录日志
            self.add_step("LOG_MESSAGE", {
                "message": "右键点击完成，准备演示鼠标轨迹移动"
            })
            
            # 步骤5: 鼠标轨迹移动
            self.add_step("MOUSE_MOVE_PATH", {
                "path_points": "50,50;200,100;100,150;300,50",
                "duration": 1.5,
                "relative_to_element": "是",
                "locator_strategy": "id",
                "locator_value": "div1"
            })
            
            # 记录日志
            self.add_step("LOG_MESSAGE", {
                "message": "鼠标轨迹移动完成，演示双击操作"
            })
            
            # 等待一下
            self.add_step("WAIT_SECONDS", {
                "seconds": "1"
            })
            
            # 步骤6: 双击操作
            self.add_step("MOUSE_DOUBLE_CLICK", {
                "locator_strategy": "id",
                "locator_value": "div2",
                "timeout": 10
            })
            
            # 记录日志
            self.add_step("LOG_MESSAGE", {
                "message": "高级鼠标操作演示完成！"
            })
            
            # 流程创建成功
            self._flow_modified = True
            self._current_file_path = None
            return True
            
        except Exception as e:
            print(f"创建高级鼠标操作演示流程失败: {str(e)}")
            return False

    def create_console_demo_flow(self) -> bool:
        """
        创建演示控制台监听功能的示例流程
        
        Returns:
            是否成功创建示例流程
        """
        try:
            # 清空现有流程
            self.delete_flow(False)
            self.clear_variables()
            
            # 创建流程需要的变量
            self.create_variable("log_content", "这是来自DrissionPage GUI工具的测试日志", "string", VariableScope.GLOBAL)
            
            # 步骤1: 打开浏览器访问百度
            self.add_step("OPEN_BROWSER", {
                "url": "https://www.baidu.com",
                "browser_type": "Chrome",
                "headless": "否",
                "window_size": "1280,720"
            })
            
            # 步骤2: 启动控制台监听
            self.add_step("GET_CONSOLE_LOGS", {
                "mode": "start",
                "save_to_variable": "console_logs"
            })
            
            # 步骤3: 执行JavaScript输出到控制台
            self.add_step("EXECUTE_JAVASCRIPT", {
                "js_code": """
console.log('控制台日志测试');
console.warn('这是一条警告信息');
console.error('这是一条错误信息');
console.log('${log_content}');  // 使用变量
return "JavaScript执行完成";
"""
            })
            
            # 步骤4: 等待一下确保日志输出
            self.add_step("WAIT_SECONDS", {
                "seconds": "1"
            })
            
            # 步骤5: 获取所有控制台日志
            self.add_step("GET_CONSOLE_LOGS", {
                "mode": "all",
                "save_to_variable": "all_console_logs"
            })
            
            # 步骤6: 记录获取到的日志
            self.add_step("LOG_MESSAGE", {
                "message": "成功获取控制台日志: ${all_console_logs}",
                "level": "INFO"
            })
            
            # 步骤7: 清空控制台缓存
            self.add_step("CLEAR_CONSOLE", {})
            
            # 步骤8: 使用组合方法执行JS并获取控制台输出
            self.add_step("EXECUTE_JS_WITH_CONSOLE", {
                "js_code": """
// 输出多种类型的信息
console.log('普通日志');
console.info('信息日志');
console.warn('警告日志');
console.error('错误日志');
console.log('包含变量: ' + 'DrissionPage');
console.log({name: 'DrissionPage', type: 'Browser Automation'});
return "组合方法执行完成";
""",
                "wait_timeout": "3",
                "save_to_variable": "combined_output"
            })
            
            # 步骤9: 记录组合方法的结果
            self.add_step("LOG_MESSAGE", {
                "message": "JS执行结果: {combined_output.info.js_result}, 控制台日志数量: {combined_output.info.logs_count}",
                "level": "INFO"
            })
            
            # 步骤10: 停止控制台监听
            self.add_step("GET_CONSOLE_LOGS", {
                "mode": "stop"
            })
            
            # 步骤11: 记录完成
            self.add_step("LOG_MESSAGE", {
                "message": "控制台监听演示完成",
                "level": "SUCCESS"
            })
            
            return True
            
        except Exception as e:
            print(f"创建控制台监听演示流程失败: {str(e)}")
            return False

    def create_data_processing_demo_flow(self) -> bool:
        """
        创建演示数据处理功能的示例流程
        
        Returns:
            是否成功创建示例流程
        """
        try:
            # 清空现有流程
            self.delete_flow(False)
            self.clear_variables()
            
            # 创建流程需要的变量
            self.create_variable("sample_data", [
                {"name": "张三", "age": "25", "email": " user1@example.com ", "active": "TRUE"},
                {"name": "李四", "age": "30", "email": "user2@example.com", "active": "False"},
                {"name": "王五", "age": "20 ", "email": "invalid-email", "active": "yes"}
            ], "json", VariableScope.GLOBAL)
            
            # 步骤1: 记录原始数据
            self.add_step("LOG_MESSAGE", {
                "message": "原始数据: {sample_data}",
                "level": "INFO"
            })
            
            # 步骤2: 数据清洗
            self.add_step("CLEAN_DATA", {
                "data_variable": "sample_data",
                "cleaning_rules": """
                {
                    "name": [
                        {"type": "trim"}
                    ],
                    "age": [
                        {"type": "trim"},
                        {"type": "cast", "to": "int"}
                    ],
                    "email": [
                        {"type": "trim"},
                        {"type": "lowercase"}
                    ],
                    "active": [
                        {"type": "cast", "to": "bool"}
                    ]
                }
                """,
                "save_to_variable": "cleaned_data"
            })
            
            # 步骤3: 记录清洗后的数据
            self.add_step("LOG_MESSAGE", {
                "message": "清洗后的数据: {cleaned_data}",
                "level": "INFO"
            })
            
            # 步骤4: 验证数据
            self.add_step("VALIDATE_DATA", {
                "data_variable": "cleaned_data",
                "validation_rules": """
                {
                    "name": [
                        {"type": "required", "message": "姓名是必填项"}
                    ],
                    "age": [
                        {"type": "required", "message": "年龄是必填项"},
                        {"type": "range", "min": 18, "max": 100, "message": "年龄必须在18-100之间"}
                    ],
                    "email": [
                        {"type": "required", "message": "邮箱是必填项"},
                        {"type": "regex", "pattern": "^[\\w.-]+@[\\w.-]+\\.[a-zA-Z]{2,}$", "message": "邮箱格式不正确"}
                    ]
                }
                """,
                "save_result_to_variable": "validation_result"
            })
            
            # 步骤5: 记录验证结果
            self.add_step("LOG_MESSAGE", {
                "message": "验证结果: {validation_result}",
                "level": "INFO"
            })
            
            # 步骤6: 应用模板
            self.add_step("APPLY_DATA_TEMPLATE", {
                "data_variable": "cleaned_data",
                "template": "姓名:{name}, 年龄:{age}岁, 邮箱:{email}, 是否活跃:{active}",
                "save_to_variable": "formatted_data"
            })
            
            # 步骤7: 记录格式化后的数据
            self.add_step("LOG_MESSAGE", {
                "message": "格式化后的数据: {formatted_data}",
                "level": "INFO"
            })
            
            # 步骤8: 生成数据统计
            self.add_step("GENERATE_DATA_STATS", {
                "data_variable": "cleaned_data",
                "fields": "name,age,email,active",
                "save_to_variable": "data_stats"
            })
            
            # 步骤9: 记录统计结果
            self.add_step("LOG_MESSAGE", {
                "message": "数据统计: {data_stats}",
                "level": "INFO"
            })
            
            # 步骤10: 导出CSV
            self.add_step("EXPORT_TO_CSV", {
                "data_variable": "cleaned_data",
                "file_path": "data_export.csv",
                "encoding": "utf-8"
            })
            
            return True
            
        except Exception as e:
            print(f"创建数据处理演示流程失败: {str(e)}")
            return False
    
    def create_database_demo_flow(self) -> bool:
        """
        创建演示数据库操作功能的示例流程
        
        Returns:
            是否成功创建示例流程
        """
        try:
            # 清空现有流程
            self.delete_flow(False)
            self.clear_variables()
            
            # 创建流程需要的变量
            self.create_variable("user_data", [
                {"name": "张三", "age": 25, "email": "user1@example.com"},
                {"name": "李四", "age": 30, "email": "user2@example.com"},
                {"name": "王五", "age": 20, "email": "user3@example.com"}
            ], "json", VariableScope.GLOBAL)
            
            # 步骤1: 连接SQLite数据库
            self.add_step("DB_CONNECT", {
                "connection_id": "sqlite_demo",
                "db_type": "sqlite",
                "database_path": "demo_database.db"
            })
            
            # 步骤2: 创建表
            self.add_step("DB_EXECUTE_UPDATE", {
                "connection_id": "sqlite_demo",
                "query": """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    age INTEGER,
                    email TEXT
                )
                """,
                "save_to_variable": "create_table_result"
            })
            
            # 步骤3: 记录创建表结果
            self.add_step("LOG_MESSAGE", {
                "message": "创建表结果: {create_table_result}",
                "level": "INFO"
            })
            
            # 步骤4: 清空表数据
            self.add_step("DB_EXECUTE_UPDATE", {
                "connection_id": "sqlite_demo",
                "query": "DELETE FROM users",
                "save_to_variable": "clear_table_result"
            })
            
            # 步骤5: 构建插入查询
            self.add_step("DB_BUILD_INSERT", {
                "table": "users",
                "data": "{\"name\": \"张三\", \"age\": 25, \"email\": \"user1@example.com\"}",
                "save_to_variable": "insert_query"
            })
            
            # 步骤6: 记录构建的插入查询
            self.add_step("LOG_MESSAGE", {
                "message": "构建的插入查询: {insert_query}",
                "level": "INFO"
            })
            
            # 步骤7: 批量插入数据
            self.add_step("FOREACH", {
                "collection_variable": "user_data",
                "item_variable": "user",
                "index_variable": "index"
            })
            
            # 步骤8: 构建每条数据的插入语句
            self.add_step("DB_EXECUTE_UPDATE", {
                "connection_id": "sqlite_demo",
                "query": "INSERT INTO users (name, age, email) VALUES (:name, :age, :email)",
                "parameters": "{\"name\": \"{user.name}\", \"age\": {user.age}, \"email\": \"{user.email}\"}",
                "save_to_variable": "insert_result"
            })
            
            # 步骤9: 记录插入结果
            self.add_step("LOG_MESSAGE", {
                "message": "插入第 {index} 条数据结果: {insert_result}",
                "level": "INFO"
            })
            
            # 步骤10: 结束循环
            self.add_step("END_FOREACH", {})
            
            # 步骤11: 构建查询
            self.add_step("DB_BUILD_SELECT", {
                "table": "users",
                "fields": "id,name,age,email",
                "where_condition": "{\"age\": 25}",
                "save_to_variable": "select_query"
            })
            
            # 步骤12: 记录构建的查询
            self.add_step("LOG_MESSAGE", {
                "message": "构建的查询: {select_query}",
                "level": "INFO"
            })
            
            # 步骤13: 执行查询
            self.add_step("DB_EXECUTE_QUERY", {
                "connection_id": "sqlite_demo",
                "query": "SELECT * FROM users",
                "save_to_variable": "query_results"
            })
            
            # 步骤14: 记录查询结果
            self.add_step("LOG_MESSAGE", {
                "message": "查询结果: {query_results}",
                "level": "INFO"
            })
            
            # 步骤15: 构建更新查询
            self.add_step("DB_BUILD_UPDATE", {
                "table": "users",
                "data": "{\"age\": 26}",
                "where_condition": "{\"name\": \"张三\"}",
                "save_to_variable": "update_query"
            })
            
            # 步骤16: 记录构建的更新查询
            self.add_step("LOG_MESSAGE", {
                "message": "构建的更新查询: {update_query}",
                "level": "INFO"
            })
            
            # 步骤17: 执行更新
            self.add_step("DB_EXECUTE_UPDATE", {
                "connection_id": "sqlite_demo",
                "query": "UPDATE users SET age = :age WHERE name = :name",
                "parameters": "{\"age\": 26, \"name\": \"张三\"}",
                "save_to_variable": "update_result"
            })
            
            # 步骤18: 记录更新结果
            self.add_step("LOG_MESSAGE", {
                "message": "更新结果: {update_result}",
                "level": "INFO"
            })
            
            # 步骤19: 再次查询结果
            self.add_step("DB_EXECUTE_QUERY", {
                "connection_id": "sqlite_demo",
                "query": "SELECT * FROM users",
                "save_to_variable": "updated_results"
            })
            
            # 步骤20: 记录更新后的查询结果
            self.add_step("LOG_MESSAGE", {
                "message": "更新后的数据: {updated_results}",
                "level": "INFO"
            })
            
            # 步骤21: 导出结果到CSV
            self.add_step("EXPORT_TO_CSV", {
                "data_variable": "updated_results",
                "file_path": "database_export.csv",
                "encoding": "utf-8"
            })
            
            # 步骤22: 断开数据库连接
            self.add_step("DB_DISCONNECT", {
                "connection_id": "sqlite_demo"
            })
            
            return True
            
        except Exception as e:
            print(f"创建数据库演示流程失败: {str(e)}")
            return False
