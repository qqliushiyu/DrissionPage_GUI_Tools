#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
元素等待策略模块，提供灵活的元素等待机制。
支持多种等待条件，如元素存在、可见、可点击等，以及智能等待策略。
"""

from typing import Dict, List, Optional, Tuple, Any, Union, Callable
import time
from enum import Enum


class WaitCondition(Enum):
    """等待条件枚举"""
    EXISTS = "exists"                  # 元素存在
    VISIBLE = "visible"                # 元素可见
    CLICKABLE = "clickable"            # 元素可点击
    INVISIBLE = "invisible"            # 元素不可见
    TEXT_CONTAINS = "text_contains"    # 文本包含
    TEXT_EQUALS = "text_equals"        # 文本等于
    TEXT_MATCHES = "text_matches"      # 文本匹配正则
    ATTR_CONTAINS = "attr_contains"    # 属性包含
    ATTR_EQUALS = "attr_equals"        # 属性等于
    ATTR_MATCHES = "attr_matches"      # 属性匹配正则
    CUSTOM = "custom"                  # 自定义条件


class ElementWaiter:
    """
    元素等待器，提供高级的元素等待机制。
    """
    
    def __init__(self, drission_engine=None):
        """
        初始化元素等待器
        
        Args:
            drission_engine: DrissionPage引擎实例，用于页面交互
        """
        self._engine = drission_engine
    
    def wait_for_element(self, selector: Dict[str, str], condition: Union[str, WaitCondition],
                        timeout: float = 10.0, 
                        check_interval: float = 0.5,
                        condition_params: Optional[Dict[str, Any]] = None) -> Tuple[bool, Any]:
        """
        等待元素满足指定条件
        
        Args:
            selector: 元素选择器，格式为 {strategy: value}
            condition: 等待条件，可以是字符串或WaitCondition枚举
            timeout: 超时时间（秒）
            check_interval: 检查间隔（秒）
            condition_params: 条件参数字典
            
        Returns:
            (成功标志, 元素对象或错误消息)
        """
        if not self._engine:
            return False, "未配置DrissionPage引擎"
        
        # 如果condition是字符串，转换为枚举
        if isinstance(condition, str):
            try:
                condition = WaitCondition(condition.lower())
            except ValueError:
                return False, f"无效的等待条件: {condition}"
        
        # 初始化参数
        params = condition_params or {}
        strategy = list(selector.keys())[0]
        value = selector[strategy]
        start_time = time.time()
        
        # 持续检查直到条件满足或超时
        while time.time() - start_time < timeout:
            # 尝试获取元素（对于某些条件可能不需要元素存在）
            try:
                if condition == WaitCondition.INVISIBLE:
                    # 对于INVISIBLE条件，元素不存在也是满足条件
                    element = self._engine.get_element(strategy, value, timeout=0)
                    if not element or not self._check_element_visible(element):
                        return True, None
                else:
                    element = self._engine.get_element(strategy, value, timeout=0)
                    if not element:
                        time.sleep(check_interval)
                        continue
                    
                    # 检查条件
                    if self._check_condition(element, condition, params):
                        return True, element
            except Exception as e:
                # 检查失败，继续等待
                pass
            
            time.sleep(check_interval)
        
        # 超时
        return False, f"等待元素超时: {strategy}='{value}', 条件={condition.value}"
    
    def wait_for_all_elements(self, selectors: List[Dict[str, str]], 
                             condition: Union[str, WaitCondition],
                             timeout: float = 10.0,
                             check_interval: float = 0.5,
                             condition_params: Optional[Dict[str, Any]] = None) -> Tuple[bool, List[Any]]:
        """
        等待所有指定的元素都满足条件
        
        Args:
            selectors: 元素选择器列表
            condition: 等待条件
            timeout: 超时时间（秒）
            check_interval: 检查间隔（秒）
            condition_params: 条件参数字典
            
        Returns:
            (成功标志, 元素列表或错误消息)
        """
        if not self._engine:
            return False, "未配置DrissionPage引擎"
        
        # 如果condition是字符串，转换为枚举
        if isinstance(condition, str):
            try:
                condition = WaitCondition(condition.lower())
            except ValueError:
                return False, f"无效的等待条件: {condition}"
        
        # 初始化参数
        params = condition_params or {}
        start_time = time.time()
        elements = []
        
        # 持续检查直到所有元素都满足条件或超时
        while time.time() - start_time < timeout:
            all_satisfied = True
            elements = []
            
            for selector in selectors:
                strategy = list(selector.keys())[0]
                value = selector[strategy]
                
                try:
                    element = self._engine.get_element(strategy, value, timeout=0)
                    if not element or not self._check_condition(element, condition, params):
                        all_satisfied = False
                        break
                    elements.append(element)
                except Exception:
                    all_satisfied = False
                    break
            
            if all_satisfied:
                return True, elements
            
            time.sleep(check_interval)
        
        # 超时
        return False, "等待元素列表超时，未能满足条件"
    
    def wait_for_any_element(self, selectors: List[Dict[str, str]], 
                            condition: Union[str, WaitCondition],
                            timeout: float = 10.0,
                            check_interval: float = 0.5,
                            condition_params: Optional[Dict[str, Any]] = None) -> Tuple[bool, Any]:
        """
        等待任何一个元素满足条件
        
        Args:
            selectors: 元素选择器列表
            condition: 等待条件
            timeout: 超时时间（秒）
            check_interval: 检查间隔（秒）
            condition_params: 条件参数字典
            
        Returns:
            (成功标志, 第一个满足条件的元素或错误消息)
        """
        if not self._engine:
            return False, "未配置DrissionPage引擎"
        
        # 如果condition是字符串，转换为枚举
        if isinstance(condition, str):
            try:
                condition = WaitCondition(condition.lower())
            except ValueError:
                return False, f"无效的等待条件: {condition}"
        
        # 初始化参数
        params = condition_params or {}
        start_time = time.time()
        
        # 持续检查直到任一元素满足条件或超时
        while time.time() - start_time < timeout:
            for selector in selectors:
                strategy = list(selector.keys())[0]
                value = selector[strategy]
                
                try:
                    element = self._engine.get_element(strategy, value, timeout=0)
                    if element and self._check_condition(element, condition, params):
                        return True, element
                except Exception:
                    continue
            
            time.sleep(check_interval)
        
        # 超时
        return False, "等待任一元素超时，未能满足条件"
    
    def wait_with_custom_condition(self, selector: Dict[str, str], 
                                  condition_func: Callable[[Any], bool],
                                  timeout: float = 10.0,
                                  check_interval: float = 0.5) -> Tuple[bool, Any]:
        """
        使用自定义条件函数等待元素
        
        Args:
            selector: 元素选择器，格式为 {strategy: value}
            condition_func: 条件函数，接受元素对象作为参数，返回布尔值
            timeout: 超时时间（秒）
            check_interval: 检查间隔（秒）
            
        Returns:
            (成功标志, 元素对象或错误消息)
        """
        if not self._engine:
            return False, "未配置DrissionPage引擎"
        
        strategy = list(selector.keys())[0]
        value = selector[strategy]
        start_time = time.time()
        
        # 持续检查直到条件满足或超时
        while time.time() - start_time < timeout:
            try:
                element = self._engine.get_element(strategy, value, timeout=0)
                if element and condition_func(element):
                    return True, element
            except Exception:
                pass
            
            time.sleep(check_interval)
        
        # 超时
        return False, f"等待元素自定义条件超时: {strategy}='{value}'"
    
    def smart_wait(self, selector: Dict[str, str], action_type: str, 
                  timeout: float = 10.0) -> Tuple[bool, Any]:
        """
        智能等待策略，根据操作类型自动选择合适的等待条件
        
        Args:
            selector: 元素选择器，格式为 {strategy: value}
            action_type: 操作类型，如 "click", "input", "hover", "drag", "select"
            timeout: 超时时间（秒）
            
        Returns:
            (成功标志, 元素对象或错误消息)
        """
        if not self._engine:
            return False, "未配置DrissionPage引擎"
        
        # 根据操作类型选择合适的等待条件
        if action_type.lower() in ["click", "double_click", "right_click"]:
            # 点击操作需要元素可点击
            return self.wait_for_element(
                selector, WaitCondition.CLICKABLE, timeout
            )
        
        elif action_type.lower() in ["input", "type", "send_keys"]:
            # 输入操作需要元素可见且可交互
            return self.wait_for_element(
                selector, WaitCondition.VISIBLE, timeout
            )
        
        elif action_type.lower() in ["hover", "mouse_over"]:
            # 悬停操作只需要元素可见
            return self.wait_for_element(
                selector, WaitCondition.VISIBLE, timeout
            )
        
        elif action_type.lower() in ["select", "dropdown"]:
            # 选择操作需要元素可见
            return self.wait_for_element(
                selector, WaitCondition.VISIBLE, timeout
            )
        
        elif action_type.lower() in ["drag", "drag_and_drop"]:
            # 拖放操作需要元素可见并可交互
            return self.wait_for_element(
                selector, WaitCondition.CLICKABLE, timeout
            )
        
        else:
            # 默认等待元素存在
            return self.wait_for_element(
                selector, WaitCondition.EXISTS, timeout
            )
    
    def _check_condition(self, element: Any, condition: WaitCondition, 
                        params: Dict[str, Any]) -> bool:
        """
        检查元素是否满足指定条件
        
        Args:
            element: 元素对象
            condition: 等待条件
            params: 条件参数
            
        Returns:
            是否满足条件
        """
        if condition == WaitCondition.EXISTS:
            # 元素存在
            return True
        
        elif condition == WaitCondition.VISIBLE:
            # 元素可见
            return self._check_element_visible(element)
        
        elif condition == WaitCondition.CLICKABLE:
            # 元素可点击
            return self._check_element_clickable(element)
        
        elif condition == WaitCondition.INVISIBLE:
            # 元素不可见
            return not self._check_element_visible(element)
        
        elif condition == WaitCondition.TEXT_CONTAINS:
            # 文本包含
            expected_text = params.get("text", "")
            return expected_text in self._get_element_text(element)
        
        elif condition == WaitCondition.TEXT_EQUALS:
            # 文本等于
            expected_text = params.get("text", "")
            return expected_text == self._get_element_text(element)
        
        elif condition == WaitCondition.TEXT_MATCHES:
            # 文本匹配正则
            import re
            pattern = params.get("pattern", "")
            if not pattern:
                return False
            return bool(re.search(pattern, self._get_element_text(element)))
        
        elif condition == WaitCondition.ATTR_CONTAINS:
            # 属性包含
            attr_name = params.get("attr_name", "")
            expected_value = params.get("value", "")
            if not attr_name:
                return False
            attr_value = self._get_element_attribute(element, attr_name)
            return expected_value in (attr_value or "")
        
        elif condition == WaitCondition.ATTR_EQUALS:
            # 属性等于
            attr_name = params.get("attr_name", "")
            expected_value = params.get("value", "")
            if not attr_name:
                return False
            attr_value = self._get_element_attribute(element, attr_name)
            return expected_value == attr_value
        
        elif condition == WaitCondition.ATTR_MATCHES:
            # 属性匹配正则
            import re
            attr_name = params.get("attr_name", "")
            pattern = params.get("pattern", "")
            if not attr_name or not pattern:
                return False
            attr_value = self._get_element_attribute(element, attr_name)
            return bool(re.search(pattern, attr_value or ""))
        
        elif condition == WaitCondition.CUSTOM:
            # 自定义条件，使用JavaScript表达式
            js_condition = params.get("js_condition", "")
            if not js_condition:
                return False
            result = self._engine.execute_js(
                f"return (function(el) {{ return Boolean({js_condition}); }})(arguments[0]);",
                element
            )
            return bool(result)
        
        return False
    
    def _check_element_visible(self, element: Any) -> bool:
        """
        检查元素是否可见
        
        Args:
            element: 元素对象
            
        Returns:
            是否可见
        """
        try:
            return self._engine.execute_js("""
                (function(el) {
                    if (!el) return false;
                    
                    const style = window.getComputedStyle(el);
                    if (style.display === 'none' || style.visibility === 'hidden' || style.opacity === '0') {
                        return false;
                    }
                    
                    const rect = el.getBoundingClientRect();
                    return rect.width > 0 && rect.height > 0;
                })(arguments[0]);
            """, element)
        except Exception:
            return False
    
    def _check_element_clickable(self, element: Any) -> bool:
        """
        检查元素是否可点击
        
        Args:
            element: 元素对象
            
        Returns:
            是否可点击
        """
        try:
            return self._engine.execute_js("""
                (function(el) {
                    if (!el) return false;
                    
                    // 首先检查可见性
                    const style = window.getComputedStyle(el);
                    if (style.display === 'none' || style.visibility === 'hidden' || style.opacity === '0') {
                        return false;
                    }
                    
                    const rect = el.getBoundingClientRect();
                    if (rect.width === 0 || rect.height === 0) {
                        return false;
                    }
                    
                    // 检查是否被禁用
                    if (el.disabled) {
                        return false;
                    }
                    
                    // 检查是否被覆盖
                    const centerX = rect.left + rect.width / 2;
                    const centerY = rect.top + rect.height / 2;
                    const elementAtPoint = document.elementFromPoint(centerX, centerY);
                    
                    return el.contains(elementAtPoint) || el === elementAtPoint;
                })(arguments[0]);
            """, element)
        except Exception:
            return False
    
    def _get_element_text(self, element: Any) -> str:
        """
        获取元素文本
        
        Args:
            element: 元素对象
            
        Returns:
            元素文本
        """
        try:
            return self._engine.execute_js("""
                (function(el) {
                    return el ? (el.textContent || el.innerText || '').trim() : '';
                })(arguments[0]);
            """, element)
        except Exception:
            return ""
    
    def _get_element_attribute(self, element: Any, attr_name: str) -> Optional[str]:
        """
        获取元素属性值
        
        Args:
            element: 元素对象
            attr_name: 属性名
            
        Returns:
            属性值或None
        """
        try:
            return self._engine.execute_js(f"""
                (function(el, attr) {{
                    return el ? el.getAttribute(attr) : null;
                }})(arguments[0], '{attr_name}');
            """, element)
        except Exception:
            return None 