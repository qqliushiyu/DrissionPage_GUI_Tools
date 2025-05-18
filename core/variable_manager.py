#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
变量管理器模块，负责管理自动化流程中的变量。
"""

from typing import Dict, Any, List, Optional, Union, Tuple
import re
import json

class VariableScope:
    """
    变量作用域类型
    """
    GLOBAL = "global"  # 全局变量
    LOCAL = "local"    # 局部变量（如循环内）
    TEMPORARY = "temp" # 临时变量（仅在步骤中使用）


class VariableManager:
    """
    变量管理器，负责管理自动化流程中的变量。
    支持不同作用域的变量、变量类型、变量模板替换等功能。
    """
    
    def __init__(self):
        """初始化变量管理器"""
        # 不同作用域的变量存储
        self._variables = {
            VariableScope.GLOBAL: {},    # 全局变量
            VariableScope.LOCAL: {},     # 局部变量
            VariableScope.TEMPORARY: {}  # 临时变量
        }
        
        # 变量作用域栈，用于处理嵌套作用域
        self._scope_stack = []
        
        # 变量类型定义
        self._variable_types = {
            "string": str,
            "number": float,
            "integer": int,
            "boolean": bool,
            "list": list,
            "dict": dict
        }
    
    def create_variable(self, name: str, value: Any, var_type: str = None, 
                        scope: str = VariableScope.GLOBAL, description: str = "") -> Tuple[bool, str]:
        """
        创建新变量
        
        Args:
            name: 变量名称
            value: 变量值
            var_type: 变量类型（如果为None，则自动推断）
            scope: 变量作用域
            description: 变量描述
            
        Returns:
            (成功标志, 消息)
        """
        # 验证变量名
        if not self._is_valid_variable_name(name):
            return False, f"无效的变量名: {name}。变量名只能包含字母、数字和下划线，且不能以数字开头。"
        
        # 如果未指定类型，自动推断
        if var_type is None:
            var_type = self._infer_type(value)
        
        # 验证值类型是否匹配指定类型
        if not self._validate_type(value, var_type):
            return False, f"值 '{value}' 与指定类型 '{var_type}' 不匹配"
        
        # 转换值为指定类型
        try:
            typed_value = self._convert_value(value, var_type)
        except ValueError as e:
            return False, f"无法将值转换为指定类型: {str(e)}"
        
        # 存储变量
        if scope not in self._variables:
            return False, f"无效的作用域: {scope}"
        
        # 创建变量对象
        variable_data = {
            "name": name,
            "value": typed_value,
            "type": var_type,
            "description": description,
            "modified_at": None  # 将在修改时填充
        }
        
        self._variables[scope][name] = variable_data
        return True, f"已创建变量 '{name}' (类型: {var_type}, 作用域: {scope})"
    
    def get_variable(self, name: str, default_value: Any = None) -> Any:
        """
        按优先级获取变量值（临时>局部>全局）
        
        Args:
            name: 变量名称
            default_value: 如果变量不存在则返回此默认值
            
        Returns:
            变量值或默认值
        """
        # 按优先级检查各作用域
        for scope in [VariableScope.TEMPORARY, VariableScope.LOCAL, VariableScope.GLOBAL]:
            if name in self._variables[scope]:
                return self._variables[scope][name]["value"]
        
        return default_value
    
    def set_variable(self, name: str, value: Any, scope: Optional[str] = None) -> Tuple[bool, str]:
        """
        设置变量值
        
        Args:
            name: 变量名称
            value: 新的变量值
            scope: 指定作用域（如果为None，则在现有变量中查找）
            
        Returns:
            (成功标志, 消息)
        """
        # 如果未指定作用域，查找现有变量
        if scope is None:
            for s in [VariableScope.TEMPORARY, VariableScope.LOCAL, VariableScope.GLOBAL]:
                if name in self._variables[s]:
                    scope = s
                    break
            
            if scope is None:
                return False, f"变量 '{name}' 不存在于任何作用域中"
        
        # 如果指定了作用域，但变量不存在于该作用域
        if name not in self._variables[scope]:
            return False, f"变量 '{name}' 不存在于作用域 '{scope}' 中"
        
        # 获取变量的类型
        var_type = self._variables[scope][name]["type"]
        
        # 验证并转换值
        if not self._validate_type(value, var_type):
            return False, f"值 '{value}' 与变量类型 '{var_type}' 不匹配"
        
        try:
            typed_value = self._convert_value(value, var_type)
        except ValueError as e:
            return False, f"无法将值转换为变量类型: {str(e)}"
        
        # 更新变量值
        self._variables[scope][name]["value"] = typed_value
        # 更新修改时间戳（此处可添加实际时间戳）
        self._variables[scope][name]["modified_at"] = "updated"
        
        return True, f"已更新变量 '{name}' 的值为 '{typed_value}'"
    
    def delete_variable(self, name: str, scope: Optional[str] = None) -> Tuple[bool, str]:
        """
        删除变量
        
        Args:
            name: 变量名称
            scope: 变量作用域（如果为None，则删除所有作用域中的该变量）
            
        Returns:
            (成功标志, 消息)
        """
        deleted = False
        
        if scope is not None:
            # 从指定作用域删除
            if name in self._variables[scope]:
                del self._variables[scope][name]
                deleted = True
        else:
            # 从所有作用域删除
            for s in self._variables:
                if name in self._variables[s]:
                    del self._variables[s][name]
                    deleted = True
        
        if deleted:
            return True, f"已删除变量 '{name}'"
        else:
            return False, f"变量 '{name}' 不存在"
    
    def get_all_variables(self, scope: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
        """
        获取所有变量
        
        Args:
            scope: 如果指定，则仅返回该作用域的变量
            
        Returns:
            变量字典
        """
        if scope is not None:
            return self._variables.get(scope, {})
        
        # 合并所有作用域的变量
        all_vars = {}
        for scope, vars_dict in self._variables.items():
            for name, var_data in vars_dict.items():
                all_vars[f"{scope}.{name}"] = var_data
        
        return all_vars
    
    def push_scope(self, scope_name: str) -> None:
        """
        将新的作用域压入栈（如进入循环）
        
        Args:
            scope_name: 作用域名称（如 "loop_1"）
        """
        self._scope_stack.append(scope_name)
    
    def pop_scope(self) -> str:
        """
        弹出当前作用域（如退出循环）
        
        Returns:
            弹出的作用域名称
        """
        if self._scope_stack:
            return self._scope_stack.pop()
        return ""
    
    def clear_scope(self, scope: str) -> None:
        """
        清除指定作用域的所有变量
        
        Args:
            scope: 要清除的作用域
        """
        if scope in self._variables:
            self._variables[scope] = {}
    
    def process_template(self, template: str) -> str:
        """
        处理包含变量的模板字符串，替换其中的变量引用和表达式
        例如: 
        - "Hello ${name}" 将被替换为 "Hello World"（如果name="World"）
        - "Count: ${counter + 1}" 将被替换为 "Count: 6"（如果counter=5）
        - "Items: ${items[0]}" 将被替换为 "Items: apple"（如果items=['apple', 'banana']）
        
        Args:
            template: 包含变量引用的模板字符串
            
        Returns:
            替换变量后的字符串
        """
        if not template or "${" not in template:
            return template
        
        # 匹配 ${...} 格式的变量引用或表达式
        pattern = r'\${([^{}]+)}'
        
        def replace_var(match):
            expr = match.group(1).strip()
            
            # 检查是否为简单变量引用（不含运算符）
            if re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', expr):
                var_value = self.get_variable(expr, f"${{{expr}}}")
                return str(var_value)
            
            # 检查是否包含不安全的字符或关键字
            unsafe_patterns = [
                r'import\s+', r'eval\s*\(', r'exec\s*\(', r'compile\s*\(',
                r'__\w+__', r'open\s*\(', r'file\s*\(', r'globals\s*\(', 
                r'locals\s*\(', r'getattr\s*\(', r'setattr\s*\('
            ]
            
            for pattern in unsafe_patterns:
                if re.search(pattern, expr):
                    return f"${{{expr}}}"  # 发现可能不安全的表达式，返回原始字符串
            
            # 处理表达式
            try:
                # 创建一个局部变量环境，将变量名映射到其值
                variables = {}
                
                # 提取表达式中所有可能的变量名
                var_names = re.findall(r'[a-zA-Z_][a-zA-Z0-9_]*', expr)
                
                # 收集所有变量
                for var_name in var_names:
                    # 跳过Python关键字和函数名
                    python_keywords = ['and', 'or', 'not', 'is', 'in', 'if', 'else', 'for', 'while', 
                                     'True', 'False', 'None', 'return', 'def', 'class', 'len', 'str', 
                                     'int', 'float', 'bool', 'abs', 'max', 'min', 'round']
                    if var_name in python_keywords:
                        continue
                    
                    var_value = self.get_variable(var_name)
                    if var_value is not None:
                        variables[var_name] = var_value
                
                # 构建允许的函数和变量环境
                allowed_names = {
                    'True': True, 'False': False, 'None': None,
                    'abs': abs, 'round': round, 'min': min, 'max': max,
                    'int': int, 'float': float, 'str': str, 'len': len
                }
                
                # 合并变量到允许的名称中
                allowed_names.update(variables)
                
                # 计算表达式
                result = eval(expr, {"__builtins__": {}}, allowed_names)
                return str(result)
            except Exception as e:
                # 如果表达式计算失败，返回原始模板
                return f"${{{expr}}}"  # 无法计算的表达式保持原样
        
        # 替换所有变量引用和表达式
        return re.sub(pattern, replace_var, template)
    
    def export_variables(self, scope: Optional[str] = None) -> str:
        """
        导出变量为JSON字符串
        
        Args:
            scope: 如果指定，则仅导出该作用域的变量
            
        Returns:
            JSON字符串
        """
        vars_to_export = self.get_all_variables(scope)
        return json.dumps(vars_to_export, ensure_ascii=False, indent=2)
    
    def import_variables(self, json_str: str, scope: str = VariableScope.GLOBAL) -> Tuple[bool, str]:
        """
        从JSON字符串导入变量
        
        Args:
            json_str: JSON字符串
            scope: 导入到的作用域
            
        Returns:
            (成功标志, 消息)
        """
        try:
            variables = json.loads(json_str)
            if not isinstance(variables, dict):
                return False, "JSON必须是对象格式"
            
            for name, var_data in variables.items():
                if not isinstance(var_data, dict):
                    continue
                
                # 提取变量数据
                value = var_data.get("value")
                var_type = var_data.get("type")
                description = var_data.get("description", "")
                
                # 创建变量
                self.create_variable(name, value, var_type, scope, description)
            
            return True, f"已导入 {len(variables)} 个变量"
        
        except json.JSONDecodeError:
            return False, "无效的JSON格式"
        except Exception as e:
            return False, f"导入变量失败: {str(e)}"
    
    def _is_valid_variable_name(self, name: str) -> bool:
        """
        检查变量名是否有效
        
        Args:
            name: 变量名
            
        Returns:
            是否有效
        """
        return bool(re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', name))
    
    def _infer_type(self, value: Any) -> str:
        """
        推断值的类型
        
        Args:
            value: 要推断类型的值
            
        Returns:
            类型名称
        """
        if isinstance(value, bool):
            return "boolean"
        elif isinstance(value, int):
            return "integer"
        elif isinstance(value, float):
            return "number"
        elif isinstance(value, list):
            return "list"
        elif isinstance(value, dict):
            return "dict"
        else:
            return "string"
    
    def _validate_type(self, value: Any, var_type: str) -> bool:
        """
        验证值是否可以转换为指定类型
        
        Args:
            value: 要验证的值
            var_type: 目标类型
            
        Returns:
            是否可以转换
        """
        try:
            self._convert_value(value, var_type)
            return True
        except Exception:
            return False
    
    def _convert_value(self, value: Any, var_type: str) -> Any:
        """
        将值转换为指定类型
        
        Args:
            value: 要转换的值
            var_type: 目标类型
            
        Returns:
            转换后的值
            
        Raises:
            ValueError: 如果值无法转换为指定类型
        """
        if var_type == "string":
            return str(value)
        
        elif var_type == "integer":
            if isinstance(value, str):
                value = value.strip()
            return int(value)
        
        elif var_type == "number":
            if isinstance(value, str):
                value = value.strip()
            return float(value)
        
        elif var_type == "boolean":
            if isinstance(value, str):
                value = value.strip().lower()
                if value in ("true", "yes", "1"):
                    return True
                elif value in ("false", "no", "0"):
                    return False
                raise ValueError(f"无法将字符串 '{value}' 转换为布尔值")
            return bool(value)
        
        elif var_type == "list":
            if isinstance(value, str):
                try:
                    return json.loads(value)
                except:
                    return value.split(",")
            elif isinstance(value, list):
                return value
            else:
                return [value]
        
        elif var_type == "dict":
            if isinstance(value, str):
                return json.loads(value)
            elif isinstance(value, dict):
                return value
            else:
                raise ValueError(f"无法将类型 '{type(value).__name__}' 转换为字典")
        
        else:
            raise ValueError(f"未知的变量类型: {var_type}") 