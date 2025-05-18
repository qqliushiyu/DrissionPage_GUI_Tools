#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
条件评估器模块，用于处理高级条件表达式。
"""

import re
import json
from typing import Dict, Any, List, Tuple, Optional, Callable, Union
from enum import Enum

# 如果有需要，可以集成JavaScript引擎
try:
    import js2py
    JS_AVAILABLE = True
except ImportError:
    JS_AVAILABLE = False


class ConditionType(Enum):
    """条件类型枚举"""
    # 元素相关条件
    ELEMENT_EXISTS = "element_exists"  # 元素是否存在
    ELEMENT_NOT_EXISTS = "element_not_exists"  # 元素是否不存在
    ELEMENT_VISIBLE = "element_visible"  # 元素是否可见
    ELEMENT_NOT_VISIBLE = "element_not_visible"  # 元素是否不可见
    ELEMENT_ENABLED = "element_enabled"  # 元素是否启用
    ELEMENT_DISABLED = "element_disabled"  # 元素是否禁用
    ELEMENT_TEXT_EQUALS = "element_text_equals"  # 元素文本是否等于
    ELEMENT_TEXT_CONTAINS = "element_text_contains"  # 元素文本是否包含
    ELEMENT_TEXT_MATCHES = "element_text_matches"  # 元素文本是否匹配正则表达式
    ELEMENT_ATTR_EQUALS = "element_attr_equals"  # 元素属性是否等于
    ELEMENT_ATTR_CONTAINS = "element_attr_contains"  # 元素属性是否包含
    ELEMENT_ATTR_MATCHES = "element_attr_matches"  # 元素属性是否匹配正则表达式
    
    # 变量相关条件
    VARIABLE_EQUALS = "variable_equals"  # 变量是否等于
    VARIABLE_NOT_EQUALS = "variable_not_equals"  # 变量是否不等于
    VARIABLE_GREATER_THAN = "variable_greater_than"  # 变量是否大于
    VARIABLE_LESS_THAN = "variable_less_than"  # 变量是否小于
    VARIABLE_GREATER_EQUALS = "variable_greater_equals"  # 变量是否大于等于
    VARIABLE_LESS_EQUALS = "variable_less_equals"  # 变量是否小于等于
    VARIABLE_CONTAINS = "variable_contains"  # 变量是否包含
    VARIABLE_MATCHES = "variable_matches"  # 变量是否匹配正则表达式
    VARIABLE_IS_EMPTY = "variable_is_empty"  # 变量是否为空
    VARIABLE_IS_NOT_EMPTY = "variable_is_not_empty"  # 变量是否不为空
    
    # 复合条件
    AND = "and"  # 逻辑与
    OR = "or"    # 逻辑或
    NOT = "not"  # 逻辑非
    
    # JavaScript 条件
    JAVASCRIPT = "javascript"  # JavaScript表达式
    
    # 其他条件
    ALWAYS_TRUE = "always_true"  # 始终为真
    ALWAYS_FALSE = "always_false"  # 始终为假
    
    @classmethod
    def from_string(cls, condition_str: str):
        """从字符串获取枚举值"""
        try:
            return cls(condition_str)
        except ValueError:
            # 如果不是有效的枚举值，尝试匹配部分名称
            for member in cls:
                if member.value == condition_str:
                    return member
            raise ValueError(f"未知的条件类型: {condition_str}")


class ConditionEvaluator:
    """
    条件评估器，用于处理和评估高级条件表达式。
    """
    
    def __init__(self, drission_engine=None, variable_manager=None):
        """
        初始化条件评估器
        
        Args:
            drission_engine: DrissionPage引擎，用于元素定位和交互
            variable_manager: 变量管理器，用于获取和处理变量
        """
        self._engine = drission_engine
        self._variable_manager = variable_manager
        
        # 条件处理函数映射
        self._condition_handlers = {
            # 元素相关条件
            ConditionType.ELEMENT_EXISTS: self._evaluate_element_exists,
            ConditionType.ELEMENT_NOT_EXISTS: self._evaluate_element_not_exists,
            ConditionType.ELEMENT_VISIBLE: self._evaluate_element_visible,
            ConditionType.ELEMENT_NOT_VISIBLE: self._evaluate_element_not_visible,
            ConditionType.ELEMENT_ENABLED: self._evaluate_element_enabled,
            ConditionType.ELEMENT_DISABLED: self._evaluate_element_disabled,
            ConditionType.ELEMENT_TEXT_EQUALS: self._evaluate_element_text_equals,
            ConditionType.ELEMENT_TEXT_CONTAINS: self._evaluate_element_text_contains,
            ConditionType.ELEMENT_TEXT_MATCHES: self._evaluate_element_text_matches,
            ConditionType.ELEMENT_ATTR_EQUALS: self._evaluate_element_attr_equals,
            ConditionType.ELEMENT_ATTR_CONTAINS: self._evaluate_element_attr_contains,
            ConditionType.ELEMENT_ATTR_MATCHES: self._evaluate_element_attr_matches,
            
            # 变量相关条件
            ConditionType.VARIABLE_EQUALS: self._evaluate_variable_equals,
            ConditionType.VARIABLE_NOT_EQUALS: self._evaluate_variable_not_equals,
            ConditionType.VARIABLE_GREATER_THAN: self._evaluate_variable_greater_than,
            ConditionType.VARIABLE_LESS_THAN: self._evaluate_variable_less_than,
            ConditionType.VARIABLE_GREATER_EQUALS: self._evaluate_variable_greater_equals,
            ConditionType.VARIABLE_LESS_EQUALS: self._evaluate_variable_less_equals,
            ConditionType.VARIABLE_CONTAINS: self._evaluate_variable_contains,
            ConditionType.VARIABLE_MATCHES: self._evaluate_variable_matches,
            ConditionType.VARIABLE_IS_EMPTY: self._evaluate_variable_is_empty,
            ConditionType.VARIABLE_IS_NOT_EMPTY: self._evaluate_variable_is_not_empty,
            
            # 复合条件
            ConditionType.AND: self._evaluate_and,
            ConditionType.OR: self._evaluate_or,
            ConditionType.NOT: self._evaluate_not,
            
            # JavaScript 条件
            ConditionType.JAVASCRIPT: self._evaluate_javascript,
            
            # 其他条件
            ConditionType.ALWAYS_TRUE: lambda params: (True, "条件始终为真"),
            ConditionType.ALWAYS_FALSE: lambda params: (False, "条件始终为假"),
        }
    
    def evaluate_condition(self, condition: Dict[str, Any]) -> Tuple[bool, str]:
        """
        评估条件表达式
        
        Args:
            condition: 条件参数字典，必须包含 "condition_type" 字段
            
        Returns:
            (评估结果, 消息)
        """
        condition_type_str = condition.get("condition_type")
        if not condition_type_str:
            return False, "条件缺少 'condition_type' 字段"
        
        try:
            condition_type = ConditionType.from_string(condition_type_str)
        except ValueError as e:
            return False, str(e)
        
        # 获取处理函数
        handler = self._condition_handlers.get(condition_type)
        if not handler:
            return False, f"未实现的条件类型: {condition_type.value}"
        
        # 处理变量引用
        if self._variable_manager:
            self._process_variable_references(condition)
        
        # 评估条件
        try:
            result, message = handler(condition)
            return result, message
        except Exception as e:
            return False, f"条件评估失败: {str(e)}"
    
    def _process_variable_references(self, params: Dict[str, Any]) -> None:
        """
        处理参数中的变量引用
        
        Args:
            params: 参数字典
        """
        for key, value in params.items():
            if isinstance(value, str) and "${" in value:
                params[key] = self._variable_manager.process_template(value)
    
    # 元素相关条件处理函数
    def _evaluate_element_exists(self, params: Dict[str, Any]) -> Tuple[bool, str]:
        """评估元素是否存在"""
        if not self._engine:
            return False, "未配置DrissionPage引擎"
        
        locator_strategy = params.get("locator_strategy")
        locator_value = params.get("locator_value")
        timeout = params.get("timeout", 3)
        
        if not locator_strategy or not locator_value:
            return False, "缺少元素定位参数"
        
        element_exists = self._engine.check_element_exists(
            locator_strategy, locator_value, timeout
        )
        
        if element_exists:
            return True, f"元素存在: {locator_strategy}='{locator_value}'"
        else:
            return False, f"元素不存在: {locator_strategy}='{locator_value}'"
    
    def _evaluate_element_not_exists(self, params: Dict[str, Any]) -> Tuple[bool, str]:
        """评估元素是否不存在"""
        exists_result, exists_message = self._evaluate_element_exists(params)
        return not exists_result, f"元素不存在检查: {exists_message}"
    
    def _evaluate_element_visible(self, params: Dict[str, Any]) -> Tuple[bool, str]:
        """评估元素是否可见"""
        if not self._engine:
            return False, "未配置DrissionPage引擎"
        
        locator_strategy = params.get("locator_strategy")
        locator_value = params.get("locator_value")
        timeout = params.get("timeout", 3)
        
        if not locator_strategy or not locator_value:
            return False, "缺少元素定位参数"
        
        element_visible = self._engine.check_element_visible(
            locator_strategy, locator_value, timeout
        )
        
        if element_visible:
            return True, f"元素可见: {locator_strategy}='{locator_value}'"
        else:
            return False, f"元素不可见: {locator_strategy}='{locator_value}'"
    
    def _evaluate_element_not_visible(self, params: Dict[str, Any]) -> Tuple[bool, str]:
        """评估元素是否不可见"""
        visible_result, visible_message = self._evaluate_element_visible(params)
        return not visible_result, f"元素不可见检查: {visible_message}"
    
    def _evaluate_element_enabled(self, params: Dict[str, Any]) -> Tuple[bool, str]:
        """评估元素是否启用"""
        if not self._engine:
            return False, "未配置DrissionPage引擎"
        
        locator_strategy = params.get("locator_strategy")
        locator_value = params.get("locator_value")
        timeout = params.get("timeout", 3)
        
        if not locator_strategy or not locator_value:
            return False, "缺少元素定位参数"
        
        element_enabled = self._engine.check_element_enabled(
            locator_strategy, locator_value, timeout
        )
        
        if element_enabled:
            return True, f"元素已启用: {locator_strategy}='{locator_value}'"
        else:
            return False, f"元素已禁用: {locator_strategy}='{locator_value}'"
    
    def _evaluate_element_disabled(self, params: Dict[str, Any]) -> Tuple[bool, str]:
        """评估元素是否禁用"""
        enabled_result, enabled_message = self._evaluate_element_enabled(params)
        return not enabled_result, f"元素禁用检查: {enabled_message}"
    
    def _evaluate_element_text_equals(self, params: Dict[str, Any]) -> Tuple[bool, str]:
        """评估元素文本是否等于指定值"""
        if not self._engine:
            return False, "未配置DrissionPage引擎"
        
        locator_strategy = params.get("locator_strategy")
        locator_value = params.get("locator_value")
        expected_text = params.get("expected_text", "")
        timeout = params.get("timeout", 3)
        
        if not locator_strategy or not locator_value:
            return False, "缺少元素定位参数"
        
        element_text = self._engine.get_element_text(
            locator_strategy, locator_value, timeout
        )
        
        if element_text == expected_text:
            return True, f"元素文本等于 '{expected_text}'"
        else:
            return False, f"元素文本 '{element_text}' 不等于 '{expected_text}'"
    
    def _evaluate_element_text_contains(self, params: Dict[str, Any]) -> Tuple[bool, str]:
        """评估元素文本是否包含指定值"""
        if not self._engine:
            return False, "未配置DrissionPage引擎"
        
        locator_strategy = params.get("locator_strategy")
        locator_value = params.get("locator_value")
        expected_text = params.get("expected_text", "")
        timeout = params.get("timeout", 3)
        
        if not locator_strategy or not locator_value:
            return False, "缺少元素定位参数"
        
        element_text = self._engine.get_element_text(
            locator_strategy, locator_value, timeout
        )
        
        if expected_text in element_text:
            return True, f"元素文本包含 '{expected_text}'"
        else:
            return False, f"元素文本 '{element_text}' 不包含 '{expected_text}'"
    
    def _evaluate_element_text_matches(self, params: Dict[str, Any]) -> Tuple[bool, str]:
        """评估元素文本是否匹配正则表达式"""
        if not self._engine:
            return False, "未配置DrissionPage引擎"
        
        locator_strategy = params.get("locator_strategy")
        locator_value = params.get("locator_value")
        regex_pattern = params.get("regex_pattern", "")
        timeout = params.get("timeout", 3)
        
        if not locator_strategy or not locator_value or not regex_pattern:
            return False, "缺少元素定位参数或正则表达式"
        
        element_text = self._engine.get_element_text(
            locator_strategy, locator_value, timeout
        )
        
        try:
            matches = bool(re.search(regex_pattern, element_text))
            if matches:
                return True, f"元素文本匹配正则表达式 '{regex_pattern}'"
            else:
                return False, f"元素文本 '{element_text}' 不匹配正则表达式 '{regex_pattern}'"
        except re.error as e:
            return False, f"正则表达式错误: {str(e)}"
    
    def _evaluate_element_attr_equals(self, params: Dict[str, Any]) -> Tuple[bool, str]:
        """评估元素属性是否等于指定值"""
        if not self._engine:
            return False, "未配置DrissionPage引擎"
        
        locator_strategy = params.get("locator_strategy")
        locator_value = params.get("locator_value")
        attribute_name = params.get("attribute_name")
        expected_value = params.get("expected_value", "")
        timeout = params.get("timeout", 3)
        
        if not locator_strategy or not locator_value or not attribute_name:
            return False, "缺少元素定位参数或属性名"
        
        attribute_value = self._engine.get_element_attribute(
            locator_strategy, locator_value, attribute_name, timeout
        )
        
        if attribute_value == expected_value:
            return True, f"元素属性 {attribute_name} 等于 '{expected_value}'"
        else:
            return False, f"元素属性 {attribute_name} 值为 '{attribute_value}'，不等于 '{expected_value}'"
    
    def _evaluate_element_attr_contains(self, params: Dict[str, Any]) -> Tuple[bool, str]:
        """评估元素属性是否包含指定值"""
        if not self._engine:
            return False, "未配置DrissionPage引擎"
        
        locator_strategy = params.get("locator_strategy")
        locator_value = params.get("locator_value")
        attribute_name = params.get("attribute_name")
        expected_value = params.get("expected_value", "")
        timeout = params.get("timeout", 3)
        
        if not locator_strategy or not locator_value or not attribute_name:
            return False, "缺少元素定位参数或属性名"
        
        attribute_value = self._engine.get_element_attribute(
            locator_strategy, locator_value, attribute_name, timeout
        )
        
        if attribute_value and expected_value in attribute_value:
            return True, f"元素属性 {attribute_name} 包含 '{expected_value}'"
        else:
            return False, f"元素属性 {attribute_name} 值为 '{attribute_value}'，不包含 '{expected_value}'"
    
    def _evaluate_element_attr_matches(self, params: Dict[str, Any]) -> Tuple[bool, str]:
        """评估元素属性是否匹配正则表达式"""
        if not self._engine:
            return False, "未配置DrissionPage引擎"
        
        locator_strategy = params.get("locator_strategy")
        locator_value = params.get("locator_value")
        attribute_name = params.get("attribute_name")
        regex_pattern = params.get("regex_pattern", "")
        timeout = params.get("timeout", 3)
        
        if not locator_strategy or not locator_value or not attribute_name or not regex_pattern:
            return False, "缺少元素定位参数、属性名或正则表达式"
        
        attribute_value = self._engine.get_element_attribute(
            locator_strategy, locator_value, attribute_name, timeout
        )
        
        try:
            if attribute_value and re.search(regex_pattern, attribute_value):
                return True, f"元素属性 {attribute_name} 匹配正则表达式 '{regex_pattern}'"
            else:
                return False, f"元素属性 {attribute_name} 值为 '{attribute_value}'，不匹配正则表达式 '{regex_pattern}'"
        except re.error as e:
            return False, f"正则表达式错误: {str(e)}"
    
    # 变量相关条件处理函数
    def _evaluate_variable_equals(self, params: Dict[str, Any]) -> Tuple[bool, str]:
        """评估变量是否等于指定值"""
        if not self._variable_manager:
            return False, "未配置变量管理器"
        
        variable_name = params.get("variable_name")
        expected_value = params.get("expected_value")
        
        if not variable_name:
            return False, "缺少变量名"
        
        if expected_value is None:
            return False, "缺少期望值"
        
        variable_value = self._variable_manager.get_variable(variable_name)
        
        if variable_value == expected_value:
            return True, f"变量 '{variable_name}' 等于 '{expected_value}'"
        else:
            return False, f"变量 '{variable_name}' 值为 '{variable_value}'，不等于 '{expected_value}'"
    
    def _evaluate_variable_not_equals(self, params: Dict[str, Any]) -> Tuple[bool, str]:
        """评估变量是否不等于指定值"""
        equals_result, equals_message = self._evaluate_variable_equals(params)
        return not equals_result, f"变量不等于检查: {equals_message}"
    
    def _evaluate_variable_greater_than(self, params: Dict[str, Any]) -> Tuple[bool, str]:
        """评估变量是否大于指定值"""
        if not self._variable_manager:
            return False, "未配置变量管理器"
        
        variable_name = params.get("variable_name")
        compare_value = params.get("compare_value")
        
        if not variable_name:
            return False, "缺少变量名"
        
        if compare_value is None:
            return False, "缺少比较值"
        
        variable_value = self._variable_manager.get_variable(variable_name)
        
        # 尝试进行数值比较
        try:
            if isinstance(compare_value, str):
                compare_value = float(compare_value)
            if isinstance(variable_value, str):
                variable_value = float(variable_value)
            
            if variable_value > compare_value:
                return True, f"变量 '{variable_name}' 大于 {compare_value}"
            else:
                return False, f"变量 '{variable_name}' 值为 {variable_value}，不大于 {compare_value}"
        except (ValueError, TypeError):
            return False, f"无法比较：变量 '{variable_name}' 值为 '{variable_value}'，比较值为 '{compare_value}'"
    
    def _evaluate_variable_less_than(self, params: Dict[str, Any]) -> Tuple[bool, str]:
        """评估变量是否小于指定值"""
        if not self._variable_manager:
            return False, "未配置变量管理器"
        
        variable_name = params.get("variable_name")
        compare_value = params.get("compare_value")
        
        if not variable_name:
            return False, "缺少变量名"
        
        if compare_value is None:
            return False, "缺少比较值"
        
        variable_value = self._variable_manager.get_variable(variable_name)
        
        # 尝试进行数值比较
        try:
            if isinstance(compare_value, str):
                compare_value = float(compare_value)
            if isinstance(variable_value, str):
                variable_value = float(variable_value)
            
            if variable_value < compare_value:
                return True, f"变量 '{variable_name}' 小于 {compare_value}"
            else:
                return False, f"变量 '{variable_name}' 值为 {variable_value}，不小于 {compare_value}"
        except (ValueError, TypeError):
            return False, f"无法比较：变量 '{variable_name}' 值为 '{variable_value}'，比较值为 '{compare_value}'"
    
    def _evaluate_variable_greater_equals(self, params: Dict[str, Any]) -> Tuple[bool, str]:
        """评估变量是否大于等于指定值"""
        if not self._variable_manager:
            return False, "未配置变量管理器"
        
        variable_name = params.get("variable_name")
        compare_value = params.get("compare_value")
        
        if not variable_name:
            return False, "缺少变量名"
        
        if compare_value is None:
            return False, "缺少比较值"
        
        variable_value = self._variable_manager.get_variable(variable_name)
        
        # 尝试进行数值比较
        try:
            if isinstance(compare_value, str):
                compare_value = float(compare_value)
            if isinstance(variable_value, str):
                variable_value = float(variable_value)
            
            if variable_value >= compare_value:
                return True, f"变量 '{variable_name}' 大于等于 {compare_value}"
            else:
                return False, f"变量 '{variable_name}' 值为 {variable_value}，小于 {compare_value}"
        except (ValueError, TypeError):
            return False, f"无法比较：变量 '{variable_name}' 值为 '{variable_value}'，比较值为 '{compare_value}'"
    
    def _evaluate_variable_less_equals(self, params: Dict[str, Any]) -> Tuple[bool, str]:
        """评估变量是否小于等于指定值"""
        if not self._variable_manager:
            return False, "未配置变量管理器"
        
        variable_name = params.get("variable_name")
        compare_value = params.get("compare_value")
        
        if not variable_name:
            return False, "缺少变量名"
        
        if compare_value is None:
            return False, "缺少比较值"
        
        variable_value = self._variable_manager.get_variable(variable_name)
        
        # 尝试进行数值比较
        try:
            if isinstance(compare_value, str):
                compare_value = float(compare_value)
            if isinstance(variable_value, str):
                variable_value = float(variable_value)
            
            if variable_value <= compare_value:
                return True, f"变量 '{variable_name}' 小于等于 {compare_value}"
            else:
                return False, f"变量 '{variable_name}' 值为 {variable_value}，大于 {compare_value}"
        except (ValueError, TypeError):
            return False, f"无法比较：变量 '{variable_name}' 值为 '{variable_value}'，比较值为 '{compare_value}'"
    
    def _evaluate_variable_contains(self, params: Dict[str, Any]) -> Tuple[bool, str]:
        """评估变量是否包含指定值"""
        if not self._variable_manager:
            return False, "未配置变量管理器"
        
        variable_name = params.get("variable_name")
        search_value = params.get("search_value", "")
        
        if not variable_name:
            return False, "缺少变量名"
        
        variable_value = self._variable_manager.get_variable(variable_name)
        
        if variable_value is None:
            return False, f"变量 '{variable_name}' 不存在"
        
        # 容器类型检查（字符串、列表、字典）
        if isinstance(variable_value, str):
            if search_value in variable_value:
                return True, f"变量 '{variable_name}' 包含 '{search_value}'"
            else:
                return False, f"变量 '{variable_name}' 值为 '{variable_value}'，不包含 '{search_value}'"
        elif isinstance(variable_value, (list, tuple)):
            if search_value in variable_value:
                return True, f"变量 '{variable_name}' 列表包含 '{search_value}'"
            else:
                return False, f"变量 '{variable_name}' 列表不包含 '{search_value}'"
        elif isinstance(variable_value, dict):
            if search_value in variable_value:
                return True, f"变量 '{variable_name}' 字典包含键 '{search_value}'"
            else:
                return False, f"变量 '{variable_name}' 字典不包含键 '{search_value}'"
        else:
            return False, f"变量 '{variable_name}' 类型为 {type(variable_value).__name__}，不支持包含检查"
    
    def _evaluate_variable_matches(self, params: Dict[str, Any]) -> Tuple[bool, str]:
        """评估变量是否匹配正则表达式"""
        if not self._variable_manager:
            return False, "未配置变量管理器"
        
        variable_name = params.get("variable_name")
        regex_pattern = params.get("regex_pattern", "")
        
        if not variable_name or not regex_pattern:
            return False, "缺少变量名或正则表达式"
        
        variable_value = self._variable_manager.get_variable(variable_name)
        
        if variable_value is None:
            return False, f"变量 '{variable_name}' 不存在"
        
        # 正则表达式匹配
        try:
            if not isinstance(variable_value, str):
                variable_value = str(variable_value)
            
            matches = bool(re.search(regex_pattern, variable_value))
            if matches:
                return True, f"变量 '{variable_name}' 匹配正则表达式 '{regex_pattern}'"
            else:
                return False, f"变量 '{variable_name}' 值为 '{variable_value}'，不匹配正则表达式 '{regex_pattern}'"
        except re.error as e:
            return False, f"正则表达式错误: {str(e)}"
    
    def _evaluate_variable_is_empty(self, params: Dict[str, Any]) -> Tuple[bool, str]:
        """评估变量是否为空"""
        if not self._variable_manager:
            return False, "未配置变量管理器"
        
        variable_name = params.get("variable_name")
        
        if not variable_name:
            return False, "缺少变量名"
        
        variable_value = self._variable_manager.get_variable(variable_name)
        
        # 检查是否为空（None、空字符串、空列表、空字典等）
        is_empty = (
            variable_value is None or 
            variable_value == "" or 
            (isinstance(variable_value, (list, tuple, dict)) and len(variable_value) == 0)
        )
        
        if is_empty:
            return True, f"变量 '{variable_name}' 为空"
        else:
            return False, f"变量 '{variable_name}' 值为 '{variable_value}'，不为空"
    
    def _evaluate_variable_is_not_empty(self, params: Dict[str, Any]) -> Tuple[bool, str]:
        """评估变量是否不为空"""
        empty_result, empty_message = self._evaluate_variable_is_empty(params)
        return not empty_result, f"变量非空检查: {empty_message}"
    
    # 复合条件处理函数
    def _evaluate_and(self, params: Dict[str, Any]) -> Tuple[bool, str]:
        """评估逻辑与条件"""
        conditions = params.get("conditions", [])
        
        if not conditions:
            return False, "缺少子条件"
        
        results = []
        messages = []
        
        for condition in conditions:
            result, message = self.evaluate_condition(condition)
            results.append(result)
            messages.append(message)
            
            # 短路评估 - 如果任一条件为假，则整个AND条件为假
            if not result:
                return False, f"AND条件失败: {message}"
        
        # 所有条件都为真
        return True, f"AND条件全部满足: {'; '.join(messages)}"
    
    def _evaluate_or(self, params: Dict[str, Any]) -> Tuple[bool, str]:
        """评估逻辑或条件"""
        conditions = params.get("conditions", [])
        
        if not conditions:
            return False, "缺少子条件"
        
        all_messages = []
        
        for condition in conditions:
            result, message = self.evaluate_condition(condition)
            all_messages.append(message)
            
            # 短路评估 - 如果任一条件为真，则整个OR条件为真
            if result:
                return True, f"OR条件满足: {message}"
        
        # 所有条件都为假
        return False, f"OR条件全部不满足: {'; '.join(all_messages)}"
    
    def _evaluate_not(self, params: Dict[str, Any]) -> Tuple[bool, str]:
        """评估逻辑非条件"""
        condition = params.get("condition", {})
        
        if not condition:
            return False, "缺少子条件"
        
        result, message = self.evaluate_condition(condition)
        
        # 取反结果
        return not result, f"NOT条件: {message}"
    
    # JavaScript 条件处理函数
    def _evaluate_javascript(self, params: Dict[str, Any]) -> Tuple[bool, str]:
        """评估 JavaScript 表达式"""
        if not JS_AVAILABLE:
            return False, "未安装js2py库，无法执行JavaScript条件"
        
        js_code = params.get("js_code", "")
        
        if not js_code:
            return False, "缺少JavaScript代码"
        
        try:
            # 如果有变量管理器，将变量注入到JavaScript上下文
            if self._variable_manager:
                # 获取所有变量
                variables = {}
                for scope in self._variable_manager._variables:
                    for name, data in self._variable_manager._variables[scope].items():
                        variables[name] = data["value"]
                
                # 将变量转换为JSON字符串
                variables_json = json.dumps(variables, ensure_ascii=False)
                
                # 构建包含变量的JavaScript代码
                js_with_vars = f"""
                var variables = {variables_json};
                function evaluate() {{
                    {js_code}
                }}
                evaluate();
                """
                
                result = js2py.eval_js(js_with_vars)
            else:
                result = js2py.eval_js(js_code)
            
            # 确保结果为布尔值
            bool_result = bool(result)
            
            if bool_result:
                return True, f"JavaScript条件评估为真: {result}"
            else:
                return False, f"JavaScript条件评估为假: {result}"
        
        except Exception as e:
            return False, f"JavaScript评估错误: {str(e)}" 