#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
DrissionPage 引擎模块，封装对 DrissionPage 库的操作。
"""

from typing import Dict, Any, Optional, Union, Tuple, List
import time
from DrissionPage import ChromiumPage, WebPage

class DrissionEngine:
    """
    封装 DrissionPage 操作的引擎类，用于执行各种浏览器自动化任务。
    """
    
    def __init__(self):
        self._page = None  # 保存当前页面对象（ChromiumPage 或 WebPage）
        self._page_type = None  # 'chromium' 或 'web'
        self._running = False
        self._stop_requested = False
    
    def initialize(self, page_type: str = 'chromium', config: Dict[str, Any] = None) -> bool:
        """
        初始化 DrissionPage 实例。
        
        Args:
            page_type: 页面类型，'chromium' 或 'web'
            config: 初始化配置，可以包含options键，值为ChromiumOptions对象
            
        Returns:
            初始化是否成功
        """
        # 先关闭现有实例，防止内存泄漏
        self.close()
        
        config = config or {}
        self._stop_requested = False
        
        try:
            if page_type.lower() == 'chromium':
                # 打印调试信息
                print(f"初始化浏览器，配置: {config}")
                
                # 检查是否有传入ChromiumOptions对象
                if 'options' in config and config['options'] is not None:
                    options = config['options']
                    # 使用配置初始化ChromiumPage
                    self._page = ChromiumPage(options)
                else:
                    # 使用默认配置初始化
                    self._page = ChromiumPage()
                
                self._page_type = 'chromium'
            elif page_type.lower() == 'web':
                self._page = WebPage(**config)
                self._page_type = 'web'
            else:
                raise ValueError(f"不支持的页面类型: {page_type}")
            
            self._running = True
            return True
        except Exception as e:
            print(f"初始化 DrissionPage 失败: {str(e)}")
            self._running = False
            return False
    
    def close(self) -> None:
        """关闭当前页面对象"""
        if self._page:
            try:
                if self._page_type == 'chromium':
                    self._page.quit()
                # WebPage 不需要特别关闭
                self._page = None
                self._running = False
            except Exception as e:
                print(f"关闭页面失败: {str(e)}")
    
    def is_running(self) -> bool:
        """返回引擎是否正在运行"""
        return self._running
    
    def request_stop(self) -> None:
        """请求停止执行"""
        self._stop_requested = True
    
    def should_stop(self) -> bool:
        """返回是否应该停止执行"""
        return self._stop_requested
    
    def execute_action(self, action_id: str, parameters: Dict[str, Any]) -> Tuple[bool, Any]:
        """
        执行指定的动作。
        
        Args:
            action_id: 动作ID
            parameters: 动作参数
            
        Returns:
            (是否成功, 结果或错误信息)
        """
        if not self._running and action_id != "OPEN_BROWSER":
            return False, "DrissionPage 未初始化"
        
        if self._stop_requested:
            return False, "执行已被用户停止"
        
        # 页面导航操作
        if action_id == "PAGE_GET":
            return self._execute_page_get(parameters)
        elif action_id == "PAGE_REFRESH":
            return self._execute_page_refresh(parameters)
        elif action_id == "OPEN_BROWSER":
            return self._execute_open_browser(parameters)
        elif action_id == "CLOSE_BROWSER":
            return self._execute_close_browser(parameters)
        elif action_id == "GET_PAGE_INFO":
            return self._execute_get_page_info(parameters)
        
        # 元素操作
        elif action_id == "ELEMENT_CLICK":
            return self._execute_element_click(parameters)
        elif action_id == "ELEMENT_INPUT":
            return self._execute_element_input(parameters)
        elif action_id == "CLICK_ELEMENT":
            return self._execute_element_click(parameters)
        elif action_id == "INPUT_TEXT":
            return self._execute_input_text(parameters)
        elif action_id == "WAIT_FOR_ELEMENT":
            return self._execute_wait_for_element(parameters)
        elif action_id == "DELETE_ELEMENT":
            return self._execute_delete_element(parameters)
        elif action_id == "GET_ELEMENT_INFO":
            return self._execute_get_element_info(parameters)
        
        # 日志操作
        elif action_id == "LOG_MESSAGE":
            return self._execute_log_message(parameters)
        
        # 自定义JavaScript操作
        elif action_id == "EXECUTE_JAVASCRIPT":
            return self._execute_custom_javascript(parameters)
        elif action_id == "EXECUTE_JS_WITH_CONSOLE":
            return self._execute_js_with_console(parameters)
        
        # 等待操作
        elif action_id == "WAIT_SECONDS":
            return self._execute_wait_seconds(parameters)
        
        # 控制台操作
        elif action_id == "GET_CONSOLE_LOGS":
            return self._execute_get_console_logs(parameters)
        elif action_id == "CLEAR_CONSOLE":
            return self._execute_clear_console(parameters)
        
        # 数据处理操作
        elif action_id == "APPLY_DATA_TEMPLATE":
            return self._execute_apply_data_template(parameters)
        elif action_id == "CLEAN_DATA":
            return self._execute_clean_data(parameters)
        elif action_id == "VALIDATE_DATA":
            return self._execute_validate_data(parameters)
        elif action_id == "EXPORT_TO_CSV":
            return self._execute_export_to_csv(parameters)
        elif action_id == "EXPORT_TO_EXCEL":
            return self._execute_export_to_excel(parameters)
        elif action_id == "GENERATE_DATA_STATS":
            return self._execute_generate_data_stats(parameters)
        
        # 数据库操作
        elif action_id == "DB_CONNECT":
            return self._execute_db_connect(parameters)
        elif action_id == "DB_DISCONNECT":
            return self._execute_db_disconnect(parameters)
        elif action_id == "DB_EXECUTE_QUERY":
            return self._execute_db_execute_query(parameters)
        elif action_id == "DB_EXECUTE_UPDATE":
            return self._execute_db_execute_update(parameters)
        elif action_id == "DB_BUILD_SELECT":
            return self._execute_db_build_select(parameters)
        elif action_id == "DB_BUILD_INSERT":
            return self._execute_db_build_insert(parameters)
        elif action_id == "DB_BUILD_UPDATE":
            return self._execute_db_build_update(parameters)
        elif action_id == "DB_BUILD_DELETE":
            return self._execute_db_build_delete(parameters)
        
        # 条件判断操作
        elif action_id == "IF_CONDITION":
            return self._execute_if_condition(parameters)
        
        # 新增高级交互操作
        elif action_id == "TAKE_SCREENSHOT":
            return self._execute_take_screenshot(parameters)
        elif action_id == "SWITCH_TO_IFRAME":
            return self._execute_switch_to_iframe(parameters)
        elif action_id == "SWITCH_TO_PARENT_FRAME":
            return self._execute_switch_to_parent_frame(parameters)
        elif action_id == "SWITCH_TO_DEFAULT_CONTENT":
            return self._execute_switch_to_default_content(parameters)
        elif action_id == "UPLOAD_FILE":
            return self._execute_upload_file(parameters)
        elif action_id == "SCROLL_PAGE":
            return self._execute_scroll_page(parameters)
        elif action_id == "MANAGE_COOKIES":
            return self._execute_manage_cookies(parameters)
        elif action_id == "DRAG_AND_DROP":
            return self._execute_drag_and_drop(parameters)
        elif action_id == "MOUSE_HOVER":
            return self._execute_mouse_hover(parameters)
        elif action_id == "DOUBLE_CLICK":
            return self._execute_double_click(parameters)
        elif action_id == "RIGHT_CLICK":
            return self._execute_right_click(parameters)
        elif action_id == "PRESS_KEY_COMBINATION":
            return self._execute_press_key_combination(parameters)
        
        # 控制流操作 - 这些操作实际上由FlowController处理，这里只需返回成功
        elif action_id in ["TRY_BLOCK", "CATCH_BLOCK", "FINALLY_BLOCK", "END_TRY_BLOCK", 
                          "FOREACH_LOOP", "END_FOREACH_LOOP", "SET_VARIABLE", "DELETE_VARIABLE",
                          "DELETE_FLOW", "CLEAR_VARIABLES", "START_LOOP", "END_LOOP", 
                          "START_INFINITE_LOOP", "ELSE_CONDITION", "END_IF_CONDITION"]:
            return True, f"控制流操作: {action_id} 已处理"
            
        # 新增高级鼠标操作
        elif action_id == "MOUSE_DRAG_DROP":
            return self._execute_mouse_drag_drop(parameters)
        elif action_id == "MOUSE_DOUBLE_CLICK":
            return self._execute_mouse_double_click(parameters)
        elif action_id == "MOUSE_RIGHT_CLICK":
            return self._execute_mouse_right_click(parameters)
        elif action_id == "MOUSE_MOVE_PATH":
            return self._execute_mouse_move_by_path(parameters)
        elif action_id == "CLICK_CONTEXT_MENU":
            return self._execute_click_context_menu_item(parameters)
        
        # 未知操作
        else:
            return False, f"未知的动作: {action_id}"
    
    def _get_element(self, parameters: Dict[str, Any]) -> Tuple[bool, Union[Any, str]]:
        """
        根据参数查找元素。
        
        Args:
            parameters: 包含定位参数的字典
            
        Returns:
            (是否成功, 元素对象或错误信息)
        """
        if not self._page:
            return False, "页面未初始化"
        
        locator_strategy = parameters.get("locator_strategy", "css")
        locator_value = parameters.get("locator_value", "")
        timeout = parameters.get("timeout", 10)
        
        if not locator_value:
            return False, "未提供定位符值"
        
        try:
            # 使用统一的定位策略转换方法
            selector = self._convert_to_drission_selector(locator_strategy, locator_value)
            
            # 直接尝试获取元素
            try:
                element = self._page.ele(selector, timeout=timeout)
                # 如果能获取到元素且不抛出异常，则元素存在
                return True, element
            except Exception as find_error:
                return False, f"未找到元素: {locator_strategy}={locator_value}: {str(find_error)}"
            
        except Exception as e:
            return False, f"查找元素失败: {str(e)}"
    
    def _execute_page_get(self, parameters: Dict[str, Any]) -> Tuple[bool, str]:
        """执行打开URL操作"""
        url = parameters.get("url", "")
        timeout = parameters.get("timeout", 30)
        
        if not url:
            return False, "未提供URL"
        
        try:
            self._page.get(url, timeout=timeout)
            return True, f"成功打开URL: {url}"
        except Exception as e:
            return False, f"打开URL失败: {str(e)}"
    
    def _execute_page_refresh(self, parameters: Dict[str, Any]) -> Tuple[bool, str]:
        """执行刷新页面操作"""
        try:
            self._page.refresh()
            return True, "页面刷新成功"
        except Exception as e:
            return False, f"刷新页面失败: {str(e)}"
    
    def _execute_element_click(self, parameters: Dict[str, Any]) -> Tuple[bool, str]:
        """执行点击元素操作(新版)"""
        locator_strategy = parameters.get("locator_strategy", "css")
        locator_value = parameters.get("locator_value", "")
        
        if not locator_value:
            return False, "未提供定位符值"
        
        try:
            # 调试信息
            print(f"尝试点击元素，定位策略: {locator_strategy}, 定位值: {locator_value}")
            
            # 兼容百度搜索按钮的常见XPath和ID
            if locator_value == "//*[@id=\"su\"]" or locator_value == "/html/body/div[1]/div[1]/div[5]/div/div/form/span[2]/input":
                # 尝试多种定位方式
                selectors = [
                    'xpath://*[@id="su"]',  # 标准XPath
                    'xpath://input[@type="submit"]',  # 通用提交按钮XPath
                    '#su',  # ID选择器
                    'input[type="submit"]'  # CSS选择器
                ]
                
                for selector in selectors:
                    try:
                        print(f"尝试使用选择器: {selector}")
                        element = self._page.ele(selector, timeout=5)
                        element.click()
                        return True, f"已点击元素(兼容模式): {selector}"
                    except Exception as inner_error:
                        print(f"使用选择器 {selector} 失败: {str(inner_error)}")
                        continue
                
                # 如果所有选择器都失败，尝试执行JS点击
                try:
                    print("尝试使用JavaScript点击")
                    self._page.run_js('document.querySelector("#su") && document.querySelector("#su").click()')
                    return True, "已使用JavaScript点击搜索按钮"
                except Exception as js_error:
                    print(f"JavaScript点击失败: {str(js_error)}")
                    pass
                
                return False, "所有定位方式都失败，无法点击百度搜索按钮"
            
            # 常规点击逻辑
            selector = self._convert_to_drission_selector(locator_strategy, locator_value)
            
            try:
                # 先尝试等待元素可点击
                print(f"等待元素可点击: {selector}")
                element = self._page.ele(selector, timeout=10)
                
                # 检查元素是否可见
                try:
                    is_displayed = False
                    if hasattr(element, 'is_displayed'):
                        is_displayed = element.is_displayed()
                    else:
                        rect = element.rect
                        is_displayed = rect['width'] > 0 and rect['height'] > 0
                    
                    if not is_displayed:
                        print(f"警告: 元素 {selector} 不可见，但仍将尝试点击")
                except Exception:
                    print(f"警告: 无法确定元素 {selector} 的可见性")
                
                # 执行点击
                element.click()
                return True, f"已点击元素: {selector}"
            except Exception as click_error:
                error_msg = str(click_error)
                print(f"点击失败: {error_msg}")
                
                # 如果常规点击失败，尝试JavaScript点击
                try:
                    print(f"尝试使用JavaScript点击元素: {selector}")
                    # 不同的定位方式需要不同的JS查询
                    if locator_strategy.lower() == "id":
                        js = f'document.getElementById("{locator_value}") && document.getElementById("{locator_value}").click()'
                    elif locator_strategy.lower() == "xpath":
                        # XPath需要特殊处理
                        js = f'''
                        (function() {{
                            var result = document.evaluate('{locator_value}', document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
                            var element = result.singleNodeValue;
                            if(element) {{
                                element.click();
                                return true;
                            }}
                            return false;
                        }})()
                        '''
                    else:
                        # CSS选择器
                        js = f'document.querySelector("{locator_value}") && document.querySelector("{locator_value}").click()'
                    
                    result = self._page.run_js(js)
                    if result:
                        return True, f"已使用JavaScript点击元素: {selector}"
                    else:
                        return False, f"JavaScript无法找到元素: {selector}"
                except Exception as js_error:
                    return False, f"点击元素失败: 常规点击: {error_msg}; JavaScript点击: {str(js_error)}"
        except Exception as e:
            return False, f"点击元素失败: {str(e)}"
    
    def _execute_element_input(self, parameters: Dict[str, Any]) -> Tuple[bool, str]:
        """执行输入文本操作"""
        success, result = self._get_element(parameters)
        if not success:
            return False, result
        
        text_to_input = parameters.get("text_to_input", "")
        
        try:
            element = result
            element.input(text_to_input)
            return True, f"已输入文本: {text_to_input}"
        except Exception as e:
            return False, f"输入文本失败: {str(e)}"
    
    def _execute_if_condition(self, parameters: Dict[str, Any]) -> Tuple[bool, str]:
        """
        执行条件判断操作
        
        Returns:
            (条件是否为真, 结果消息)
        """
        condition_type = parameters.get("condition_type", "")
        
        if not condition_type:
            return False, "未指定条件类型"
        
        try:
            if condition_type == "element_exists":
                return self._check_element_exists(parameters)
            elif condition_type == "element_not_exists":
                success, message = self._check_element_exists(parameters)
                return not success, message
            elif condition_type == "element_visible":
                return self._check_element_visible(parameters)
            elif condition_type == "element_not_visible":
                success, message = self._check_element_visible(parameters)
                return not success, message
            else:
                return False, f"不支持的条件类型: {condition_type}"
        except Exception as e:
            return False, f"条件判断失败: {str(e)}"
    
    def _check_element_exists(self, parameters: Dict[str, Any]) -> Tuple[bool, str]:
        """
        检查元素是否存在
        
        Returns:
            (元素是否存在, 结果消息)
        """
        locator_strategy = parameters.get("if_locator_strategy", "css")
        locator_value = parameters.get("if_locator_value", "")
        timeout = parameters.get("if_timeout", 3)  # 默认较短的超时时间
        
        if not locator_value:
            return False, "未提供定位符值"
        
        try:
            print(f"检查元素是否存在，策略: {locator_strategy}, 值: {locator_value}")
            
            # 使用DrissionPage的新式定位器语法
            selector = self._convert_to_drission_selector(locator_strategy, locator_value)
            
            # 尝试获取元素
            try:
                self._page.ele(selector, timeout=timeout)
                return True, f"元素存在: {selector}"
            except Exception as find_error:
                print(f"元素不存在: {selector}, 错误: {str(find_error)}")
                
                # 尝试使用JavaScript检查元素是否存在
                try:
                    if locator_strategy.lower() == "id":
                        js = f'!!document.getElementById("{locator_value}")'
                    elif locator_strategy.lower() == "xpath":
                        js = f'''
                        (function() {{
                            var result = document.evaluate('{locator_value}', document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
                            return !!result.singleNodeValue;
                        }})()
                        '''
                    else:
                        # CSS选择器
                        js = f'!!document.querySelector("{locator_value}")'
                    
                    result = self._page.run_js(js)
                    if result:
                        return True, f"元素通过JavaScript检测存在: {selector}"
                
                except Exception:
                    pass
                
                return False, f"元素不存在: {selector}"
        except Exception as e:
            return False, f"检查元素存在性失败: {str(e)}"
    
    def _check_element_visible(self, parameters: Dict[str, Any]) -> Tuple[bool, str]:
        """
        检查元素是否可见
        
        Returns:
            (元素是否可见, 结果消息)
        """
        locator_strategy = parameters.get("if_locator_strategy", "css")
        locator_value = parameters.get("if_locator_value", "")
        timeout = parameters.get("if_timeout", 3)
        
        if not locator_value:
            return False, "未提供定位符值"
        
        try:
            print(f"检查元素是否可见，策略: {locator_strategy}, 值: {locator_value}")
            
            # 使用DrissionPage的新式定位器语法
            selector = self._convert_to_drission_selector(locator_strategy, locator_value)
            
            # 首先检查元素是否存在
            try:
                element = self._page.ele(selector, timeout=timeout)
            except Exception as find_error:
                print(f"元素不存在，无法检查可见性: {selector}, 错误: {str(find_error)}")
                return False, f"元素不存在: {selector}"
            
            # 再检查元素是否可见
            try:
                # 尝试使用is_displayed方法
                if hasattr(element, 'is_displayed'):
                    is_visible = element.is_displayed()
                else:
                    # 通过rect判断
                    rect = element.rect
                    is_visible = rect['width'] > 0 and rect['height'] > 0
                
                if is_visible:
                    return True, f"元素可见: {selector}"
                else:
                    return False, f"元素不可见: {selector}"
            except Exception as visibility_error:
                print(f"无法确定元素可见性: {selector}, 错误: {str(visibility_error)}")
                
                # 尝试使用JavaScript检查元素可见性
                try:
                    js = f'''
                    (function() {{
                        var selector = "{selector.replace('xpath:', '')}";
                        var element;
                        
                        if (selector.startsWith('#')) {{
                            // ID选择器
                            element = document.getElementById(selector.substring(1));
                        }} else if (selector.startsWith('xpath:')) {{
                            // XPath选择器
                            var xpath = selector.substring(6);
                            var result = document.evaluate(xpath, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
                            element = result.singleNodeValue;
                        }} else {{
                            // CSS选择器
                            element = document.querySelector(selector);
                        }}
                        
                        if (!element) return false;
                        
                        var rect = element.getBoundingClientRect();
                        var style = window.getComputedStyle(element);
                        return (
                            rect.width > 0 &&
                            rect.height > 0 &&
                            style.display !== 'none' &&
                            style.visibility !== 'hidden' &&
                            parseFloat(style.opacity) > 0
                        );
                    }})()
                    '''
                    
                    is_visible = self._page.run_js(js)
                    if is_visible:
                        return True, f"元素通过JavaScript检测可见: {selector}"
                    else:
                        return False, f"元素通过JavaScript检测不可见: {selector}"
                except Exception:
                    # 如果无法确定可见性，假设元素可见
                    return True, f"无法确定元素可见性，假设可见: {selector}"
                
        except Exception as e:
            return False, f"检查元素可见性失败: {str(e)}"

    # 添加新的动作执行方法
    def _execute_open_browser(self, parameters: Dict[str, Any]) -> Tuple[bool, str]:
        """执行打开浏览器操作"""
        url = parameters.get("url", "https://www.baidu.com")
        
        try:
            # 如果浏览器已经初始化，直接导航到URL
            if self._running and self._page:
                # 导航到URL
                self._page.get(url)
                return True, f"已打开页面: {url}"
            
            # 如果浏览器未初始化，执行初始化
            browser_type = parameters.get("browser_type", "Chrome")
            headless = parameters.get("headless", "否") == "是"
            window_size = parameters.get("window_size", "1280,720")
            user_agent = parameters.get("user_agent", "")
            proxy = parameters.get("proxy", "")
            incognito = parameters.get("incognito", "否") == "是"
            load_extension = parameters.get("load_extension", "")
            custom_args = parameters.get("custom_args", "")
            
            # 导入ChromiumOptions
            from DrissionPage import ChromiumOptions
            
            # 创建ChromiumOptions对象
            options = ChromiumOptions()
            
            # 设置浏览器类型
            if browser_type == "Edge":
                options.set_browser_path("edge")
            elif browser_type == "Firefox":
                options.set_browser_path("firefox")
            # Chrome是默认值，不需要特别设置
            
            # 设置无头模式
            if headless:
                options.headless(True)
            
            # 设置窗口尺寸
            if window_size:
                try:
                    width, height = map(int, window_size.split(','))
                    options.set_argument('--window-size', f'{width},{height}')
                except ValueError:
                    print(f"无效的窗口尺寸格式: {window_size}，使用默认值")
            
            # 设置用户代理
            if user_agent:
                options.set_user_agent(user_agent)
            
            # 设置代理服务器
            if proxy:
                options.set_proxy(proxy)
            
            # 设置隐私模式
            if incognito:
                options.incognito(True)
            
            # 设置扩展程序
            if load_extension:
                extensions = [path.strip() for path in load_extension.split(',')]
                for ext in extensions:
                    options.add_extension(ext)
            
            # 设置自定义参数
            if custom_args:
                args = [arg.strip() for arg in custom_args.split(',')]
                for arg in args:
                    if arg.startswith('--'):
                        options.set_argument(arg)
                    else:
                        options.set_argument(f'--{arg}')
            
            # 关闭现有浏览器实例
            self.close()
            
            # 重新初始化浏览器
            print(f"使用ChromiumOptions初始化浏览器")
            success = self.initialize('chromium', {'options': options})
            if not success:
                return False, "初始化浏览器失败"
            
            # 导航到URL
            self._page.get(url)
            
            return True, f"已打开浏览器并导航到: {url}"
        except Exception as e:
            return False, f"打开浏览器失败: {str(e)}"
    
    def _execute_close_browser(self, parameters: Dict[str, Any]) -> Tuple[bool, str]:
        """执行关闭浏览器操作"""
        try:
            self.close()
            return True, "已关闭浏览器"
        except Exception as e:
            return False, f"关闭浏览器失败: {str(e)}"
    
    def _execute_input_text(self, parameters: Dict[str, Any]) -> Tuple[bool, str]:
        """执行输入文本操作(新版)"""
        locator_strategy = parameters.get("locator_strategy", "css")
        locator_value = parameters.get("locator_value", "")
        text = parameters.get("text", "")
        
        if not locator_value:
            return False, "未提供定位符值"
        
        try:
            # 调试信息
            print(f"尝试输入文本，定位策略: {locator_strategy}, 定位值: {locator_value}, 文本: {text}")
            
            # 百度搜索框的特殊处理
            if "form/span[1]/input" in locator_value or "kw" in locator_value:
                # 尝试多种定位方式
                selectors = [
                    'xpath://*[@id="kw"]',  # 标准XPath
                    'xpath://input[@type="text"]',  # 通用文本输入框XPath
                    '#kw',  # ID选择器
                    'input[name="wd"]'  # CSS选择器
                ]
                
                for selector in selectors:
                    try:
                        print(f"尝试使用选择器: {selector}")
                        element = self._page.ele(selector, timeout=5)
                        element.input(text)
                        return True, f"已输入文本(兼容模式): {text}"
                    except Exception as inner_error:
                        print(f"使用选择器 {selector} 失败: {str(inner_error)}")
                        continue
                
                # 如果所有选择器都失败，尝试执行JS输入
                try:
                    print("尝试使用JavaScript输入")
                    self._page.run_js(f'document.querySelector("#kw") && (document.querySelector("#kw").value = "{text}")')
                    return True, "已使用JavaScript输入文本"
                except Exception as js_error:
                    print(f"JavaScript输入失败: {str(js_error)}")
                    
                return False, "所有定位方式都失败，无法输入文本"
            
            # 常规输入逻辑
            selector = self._convert_to_drission_selector(locator_strategy, locator_value)
            
            try:
                # 等待元素可交互
                print(f"等待元素可交互: {selector}")
                element = self._page.ele(selector, timeout=10)
                
                # 尝试先清空文本
                try:
                    element.clear()
                except Exception as clear_error:
                    print(f"清空文本失败: {str(clear_error)}")
                
                # 输入文本
                element.input(text)
                return True, f"已输入文本: {text}"
            except Exception as input_error:
                error_msg = str(input_error)
                print(f"输入文本失败: {error_msg}")
                
                # 如果常规输入失败，尝试JavaScript输入
                try:
                    print(f"尝试使用JavaScript输入文本: {selector}")
                    # 不同的定位方式需要不同的JS查询
                    if locator_strategy.lower() == "id":
                        js = f'document.getElementById("{locator_value}") && (document.getElementById("{locator_value}").value = "{text}")'
                    elif locator_strategy.lower() == "xpath":
                        # XPath需要特殊处理
                        js = f'''
                        (function() {{
                            var result = document.evaluate('{locator_value}', document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
                            var element = result.singleNodeValue;
                            if(element) {{
                                element.value = "{text}";
                                return true;
                            }}
                            return false;
                        }})()
                        '''
                    else:
                        # CSS选择器
                        js = f'document.querySelector("{locator_value}") && (document.querySelector("{locator_value}").value = "{text}")'
                    
                    result = self._page.run_js(js)
                    if result:
                        return True, f"已使用JavaScript输入文本: {text}"
                    else:
                        return False, f"JavaScript无法找到元素: {selector}"
                except Exception as js_error:
                    return False, f"输入文本失败: 常规输入: {error_msg}; JavaScript输入: {str(js_error)}"
        except Exception as e:
            return False, f"输入文本失败: {str(e)}"
    
    def _execute_wait_for_element(self, parameters: Dict[str, Any]) -> Tuple[bool, str]:
        """执行等待元素操作"""
        locator_strategy = parameters.get("locator_strategy", "css")
        locator_value = parameters.get("locator_value", "")
        timeout = parameters.get("timeout", 10)
        
        if not locator_value:
            return False, "未提供定位符值"
        
        try:
            # 使用DrissionPage的新式定位器语法
            selector = self._convert_to_drission_selector(locator_strategy, locator_value)
            
            # 在DrissionPage 4.1中，直接尝试获取元素
            try:
                element = self._page.ele(selector, timeout=timeout)
                return True, f"元素已出现: {selector}"
            except Exception as wait_error:
                return False, f"等待超时，元素未出现: {selector}: {str(wait_error)}"
                
        except Exception as e:
            return False, f"等待元素失败: {str(e)}"
    
    def _execute_log_message(self, parameters: Dict[str, Any]) -> Tuple[bool, str]:
        """执行记录日志操作"""
        message = parameters.get("message", "")
        level = parameters.get("level", "INFO")
        
        # 实际的日志记录由FlowController处理，这里只需返回成功
        return True, f"已记录日志[{level}]: {message}"
    
    def _convert_to_drission_selector(self, strategy: str, value: str) -> str:
        """将UI中的定位策略转换为DrissionPage兼容的选择器"""
        # 处理不同的策略大小写形式
        strategy = strategy.lower()
        
        # 处理特殊情况：百度搜索相关元素
        if "su" in value and ("id" in strategy or "xpath" in strategy):
            return "#su"  # 返回最简单可靠的CSS选择器
        
        if "kw" in value and ("id" in strategy or "xpath" in strategy):
            return "#kw"  # 返回最简单可靠的CSS选择器
        
        # 常规选择器转换
        if strategy == "id":
            return f'#{value}'
        elif strategy == "name":
            return f'@name="{value}"'
        elif strategy == "class" or strategy == "class_name":
            return f'.{value}'
        elif strategy == "tag" or strategy == "tag_name":
            return f'<{value}>'
        elif strategy == "text" or strategy == "link_text":
            return f'@text="{value}"'
        elif strategy == "partial_link_text":
            return f'@text*="{value}"'
        elif strategy == "css" or strategy == "css_selector":
            return value  # CSS选择器可以直接使用
        elif strategy == "xpath":
            # DrissionPage 4.1版本中XPath需要特殊处理
            # 确保XPath以"xpath:"前缀开始
            if value.startswith("xpath:"):
                return value
            elif value.startswith("//") or value.startswith("(//") or value.startswith("/"):
                return f'xpath:{value}'
            else:
                return f'xpath:{value}'
        else:
            # 默认尝试使用CSS选择器，或者直接使用原值
            print(f"警告: 未知的定位策略 '{strategy}'，尝试使用原始值作为选择器")
            return value

    def _execute_delete_element(self, parameters: Dict[str, Any]) -> Tuple[bool, str]:
        """执行删除元素操作"""
        locator_strategy = parameters.get("locator_strategy", "css")
        locator_value = parameters.get("locator_value", "")
        timeout = parameters.get("timeout", 5)
        
        if not locator_value:
            return False, "未提供定位符值"
        
        try:
            # 调试信息
            print(f"尝试删除元素，定位策略: {locator_strategy}, 定位值: {locator_value}")
            
            # 使用DrissionPage的新式定位器语法
            selector = self._convert_to_drission_selector(locator_strategy, locator_value)
            
            # 尝试查找和删除元素
            try:
                print(f"查找要删除的元素: {selector}")
                element = self._page.ele(selector, timeout=timeout)
                
                # 检查元素是否存在且可操作
                if element:
                    try:
                        # 尝试使用DrissionPage的delete方法
                        if hasattr(element, 'delete'):
                            element.delete()
                            return True, f"已删除元素: {selector}"
                        else:
                            # 如果没有delete方法，尝试使用remove方法
                            if hasattr(element, 'remove'):
                                element.remove()
                                return True, f"已移除元素: {selector}"
                            else:
                                # 都不支持，使用JavaScript删除
                                raise AttributeError("元素对象不支持delete或remove方法")
                    except Exception as method_error:
                        print(f"使用DOM方法删除元素失败: {str(method_error)}，尝试使用JavaScript")
                        # 使用JavaScript删除元素
                        js = '''
                        (function() {
                            var element = arguments[0];
                            if (element && element.parentNode) {
                                element.parentNode.removeChild(element);
                                return true;
                            }
                            return false;
                        })()
                        '''
                        result = self._page.run_js(js, element)
                        if result:
                            return True, f"已使用JavaScript删除元素: {selector}"
                        else:
                            return False, f"JavaScript删除元素失败: {selector}"
                else:
                    return False, f"未找到要删除的元素: {selector}"
                    
            except Exception as find_error:
                print(f"查找元素失败: {str(find_error)}")
                # 尝试使用JavaScript直接定位并删除元素
                try:
                    print(f"尝试使用JavaScript定位并删除元素: {selector}")
                    
                    # 根据不同的定位策略构造JavaScript选择器
                    if locator_strategy.lower() == "id":
                        js = f'''
                        (function() {{
                            var element = document.getElementById("{locator_value}");
                            if (element && element.parentNode) {{
                                element.parentNode.removeChild(element);
                                return true;
                            }}
                            return false;
                        }})()
                        '''
                    elif locator_strategy.lower() == "xpath":
                        js = f'''
                        (function() {{
                            var result = document.evaluate('{locator_value}', document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
                            var element = result.singleNodeValue;
                            if (element && element.parentNode) {{
                                element.parentNode.removeChild(element);
                                return true;
                            }}
                            return false;
                        }})()
                        '''
                    else:
                        # CSS选择器
                        js = f'''
                        (function() {{
                            var element = document.querySelector("{locator_value}");
                            if (element && element.parentNode) {{
                                element.parentNode.removeChild(element);
                                return true;
                            }}
                            return false;
                        }})()
                        '''
                    
                    result = self._page.run_js(js)
                    if result:
                        return True, f"已使用JavaScript查找并删除元素: {selector}"
                    else:
                        return False, f"JavaScript查找或删除元素失败: {selector}"
                        
                except Exception as js_error:
                    return False, f"查找并删除元素失败: {str(find_error)}; JavaScript错误: {str(js_error)}"
                    
        except Exception as e:
            return False, f"删除元素操作失败: {str(e)}"

    @staticmethod
    def get_browser_config_options() -> Dict[str, Dict[str, str]]:
        """
        获取支持的浏览器配置选项及其说明。
        
        Returns:
            配置选项字典，格式为 {选项名: {类型: 类型, 说明: 说明}}
        """
        return {
            "browser_path": {
                "type": "string",
                "description": "浏览器可执行文件路径，可以是'chrome'、'edge'、'firefox'或具体路径"
            },
            "headless": {
                "type": "boolean",
                "description": "无头模式，不显示浏览器窗口，适合服务器运行"
            },
            "size": {
                "type": "tuple(width, height)",
                "description": "浏览器窗口大小，例如(1280, 720)"
            },
            "user_agent": {
                "type": "string",
                "description": "自定义User-Agent字符串"
            },
            "proxy": {
                "type": "string",
                "description": "代理服务器地址，例如'http://127.0.0.1:8080'"
            },
            "incognito": {
                "type": "boolean",
                "description": "隐私模式，不保存浏览记录和Cookie"
            },
            "load_extensions": {
                "type": "list[str]",
                "description": "要加载的扩展程序路径列表"
            },
            "arguments": {
                "type": "list[str]",
                "description": "自定义浏览器启动参数列表"
            }
        }

    # 新增高级交互功能执行方法
    def _execute_take_screenshot(self, parameters: Dict[str, Any]) -> Tuple[bool, str]:
        """
        执行截图操作
        
        Args:
            parameters: 包含截图参数的字典
            
        Returns:
            (是否成功, 结果或错误信息)
        """
        save_path = parameters.get("save_path", "")
        if not save_path:
            # 生成默认保存路径
            import time
            import os
            timestamp = int(time.time())
            save_path = f"screenshots/screenshot_{timestamp}.png"
            # 确保目录存在
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            
        element_selector = None
        if "locator_strategy" in parameters and "locator_value" in parameters:
            element_selector = {
                parameters["locator_strategy"]: parameters["locator_value"]
            }
            
        save_full_page = parameters.get("save_full_page", False)
        
        # 使用高级交互类执行截图
        from drission_gui_tool.core.advanced_interactions import AdvancedInteractions
        interactions = AdvancedInteractions(self)
        return interactions.take_screenshot(save_path, element_selector, save_full_page)
    
    def _execute_switch_to_iframe(self, parameters: Dict[str, Any]) -> Tuple[bool, str]:
        """
        执行切换到iframe的操作
        
        Args:
            parameters: 包含iframe选择器的字典
            
        Returns:
            (是否成功, 结果或错误信息)
        """
        if "locator_strategy" not in parameters or "locator_value" not in parameters:
            return False, "切换iframe需要提供定位策略和值"
            
        iframe_selector = {
            parameters["locator_strategy"]: parameters["locator_value"]
        }
        
        # 使用高级交互类执行iframe切换
        from drission_gui_tool.core.advanced_interactions import AdvancedInteractions
        interactions = AdvancedInteractions(self)
        return interactions.switch_to_iframe(iframe_selector)
    
    def _execute_switch_to_parent_frame(self, parameters: Dict[str, Any]) -> Tuple[bool, str]:
        """
        执行切换到父级框架的操作
        
        Args:
            parameters: 参数字典（此操作不需要参数）
            
        Returns:
            (是否成功, 结果或错误信息)
        """
        # 使用高级交互类执行iframe切换
        from drission_gui_tool.core.advanced_interactions import AdvancedInteractions
        interactions = AdvancedInteractions(self)
        return interactions.switch_to_parent_frame()
    
    def _execute_switch_to_default_content(self, parameters: Dict[str, Any]) -> Tuple[bool, str]:
        """
        执行切换到主文档的操作
        
        Args:
            parameters: 参数字典（此操作不需要参数）
            
        Returns:
            (是否成功, 结果或错误信息)
        """
        # 使用高级交互类执行iframe切换
        from drission_gui_tool.core.advanced_interactions import AdvancedInteractions
        interactions = AdvancedInteractions(self)
        return interactions.switch_to_default_content()
    
    def _execute_upload_file(self, parameters: Dict[str, Any]) -> Tuple[bool, str]:
        """
        执行文件上传操作
        
        Args:
            parameters: 包含文件输入框选择器和文件路径的字典
            
        Returns:
            (是否成功, 结果或错误信息)
        """
        if "locator_strategy" not in parameters or "locator_value" not in parameters:
            return False, "文件上传需要提供定位策略和值"
            
        if "file_path" not in parameters:
            return False, "文件上传需要提供文件路径"
            
        file_input_selector = {
            parameters["locator_strategy"]: parameters["locator_value"]
        }
        file_path = parameters["file_path"]
        
        # 使用高级交互类执行文件上传
        from drission_gui_tool.core.advanced_interactions import AdvancedInteractions
        interactions = AdvancedInteractions(self)
        return interactions.upload_file(file_input_selector, file_path)
    
    def _execute_scroll_page(self, parameters: Dict[str, Any]) -> Tuple[bool, str]:
        """
        执行页面滚动操作
        
        Args:
            parameters: 包含滚动方向和距离的字典
            
        Returns:
            (是否成功, 结果或错误信息)
        """
        direction = parameters.get("direction", "down")
        distance = int(parameters.get("distance", 500))
        
        # 使用高级交互类执行页面滚动
        from drission_gui_tool.core.advanced_interactions import AdvancedInteractions
        interactions = AdvancedInteractions(self)
        return interactions.scroll_page(direction, distance)
    
    def _execute_manage_cookies(self, parameters: Dict[str, Any]) -> Tuple[bool, Any]:
        """
        执行Cookie管理操作
        
        Args:
            parameters: 包含Cookie操作类型和相关数据的字典
            
        Returns:
            (是否成功, Cookie数据或结果信息)
        """
        action = parameters.get("action", "")
        if not action:
            return False, "Cookie管理需要提供操作类型"
            
        cookie_data = parameters.get("cookie_data", None)
        cookie_name = parameters.get("cookie_name", None)
        
        # 使用高级交互类执行Cookie管理
        from drission_gui_tool.core.advanced_interactions import AdvancedInteractions
        interactions = AdvancedInteractions(self)
        return interactions.manage_cookies(action, cookie_data, cookie_name)
    
    def _execute_drag_and_drop(self, parameters: Dict[str, Any]) -> Tuple[bool, str]:
        """
        执行拖放操作
        
        Args:
            parameters: 包含源元素和目标元素选择器的字典
            
        Returns:
            (是否成功, 结果信息)
        """
        if "source_locator_strategy" not in parameters or "source_locator_value" not in parameters:
            return False, "拖放操作需要提供源元素的定位策略和值"
            
        if "target_locator_strategy" not in parameters or "target_locator_value" not in parameters:
            return False, "拖放操作需要提供目标元素的定位策略和值"
            
        source_selector = {
            parameters["source_locator_strategy"]: parameters["source_locator_value"]
        }
        target_selector = {
            parameters["target_locator_strategy"]: parameters["target_locator_value"]
        }
        
        smooth = parameters.get("smooth", True)
        speed = parameters.get("speed", "medium")
        
        # 使用高级交互类执行拖放操作
        from drission_gui_tool.core.advanced_interactions import AdvancedInteractions
        interactions = AdvancedInteractions(self)
        return interactions.drag_and_drop(source_selector, target_selector, smooth, speed)
    
    def _execute_mouse_hover(self, parameters: Dict[str, Any]) -> Tuple[bool, str]:
        """
        执行鼠标悬停操作
        
        Args:
            parameters: 包含元素选择器的字典
            
        Returns:
            (是否成功, 结果信息)
        """
        if "locator_strategy" not in parameters or "locator_value" not in parameters:
            return False, "鼠标悬停需要提供元素的定位策略和值"
            
        element_selector = {
            parameters["locator_strategy"]: parameters["locator_value"]
        }
        
        duration = float(parameters.get("duration", 0.5))
        
        # 使用高级交互类执行鼠标悬停
        from drission_gui_tool.core.advanced_interactions import AdvancedInteractions
        interactions = AdvancedInteractions(self)
        return interactions.mouse_hover(element_selector, duration)
    
    def _execute_double_click(self, parameters: Dict[str, Any]) -> Tuple[bool, str]:
        """
        执行双击操作
        
        Args:
            parameters: 包含元素选择器的字典
            
        Returns:
            (是否成功, 结果信息)
        """
        if "locator_strategy" not in parameters or "locator_value" not in parameters:
            return False, "双击操作需要提供元素的定位策略和值"
            
        element_selector = {
            parameters["locator_strategy"]: parameters["locator_value"]
        }
        
        # 使用高级交互类执行双击
        from drission_gui_tool.core.advanced_interactions import AdvancedInteractions
        interactions = AdvancedInteractions(self)
        return interactions.double_click(element_selector)
    
    def _execute_right_click(self, parameters: Dict[str, Any]) -> Tuple[bool, str]:
        """
        执行右键点击操作
        
        Args:
            parameters: 包含元素选择器的字典
            
        Returns:
            (是否成功, 结果信息)
        """
        if "locator_strategy" not in parameters or "locator_value" not in parameters:
            return False, "右键点击需要提供元素的定位策略和值"
            
        element_selector = {
            parameters["locator_strategy"]: parameters["locator_value"]
        }
        
        # 使用高级交互类执行右键点击
        from drission_gui_tool.core.advanced_interactions import AdvancedInteractions
        interactions = AdvancedInteractions(self)
        return interactions.right_click(element_selector)
    
    def _execute_press_key_combination(self, parameters: Dict[str, Any]) -> Tuple[bool, str]:
        """
        执行按键组合操作
        
        Args:
            parameters: 包含元素选择器和按键列表的字典
            
        Returns:
            (是否成功, 结果信息)
        """
        if "locator_strategy" not in parameters or "locator_value" not in parameters:
            return False, "按键组合需要提供元素的定位策略和值"
            
        if "keys" not in parameters:
            return False, "按键组合需要提供按键列表"
            
        element_selector = {
            parameters["locator_strategy"]: parameters["locator_value"]
        }
        
        keys = parameters["keys"]
        if isinstance(keys, str):
            # 如果是字符串，按逗号分隔
            keys = [k.strip() for k in keys.split(",")]
        
        # 使用高级交互类执行按键组合
        from drission_gui_tool.core.advanced_interactions import AdvancedInteractions
        interactions = AdvancedInteractions(self)
        return interactions.press_key_combination(element_selector, keys)

    # 新增高级鼠标操作
    def _execute_mouse_drag_drop(self, parameters: Dict[str, Any]) -> Tuple[bool, str]:
        """
        执行鼠标拖放操作
        
        Args:
            parameters: 包含参数的字典
                - source_locator_strategy: 源元素定位策略
                - source_locator_value: 源元素定位值
                - target_locator_strategy: 目标元素定位策略
                - target_locator_value: 目标元素定位值
                - smooth: 是否平滑拖动(否则直接拖放)
                - duration: 拖动持续时间(秒)
                
        Returns:
            (是否成功, 结果信息)
        """
        if not self._page:
            return False, "页面未初始化"
        
        try:
            # 获取源元素和目标元素
            source_locator_strategy = parameters.get("source_locator_strategy", "css")
            source_locator_value = parameters.get("source_locator_value", "")
            source_element = self._get_element({
                "locator_strategy": source_locator_strategy,
                "locator_value": source_locator_value,
                "timeout": parameters.get("timeout", 10)
            })
            
            target_locator_strategy = parameters.get("target_locator_strategy", "css")
            target_locator_value = parameters.get("target_locator_value", "")
            target_element = self._get_element({
                "locator_strategy": target_locator_strategy,
                "locator_value": target_locator_value,
                "timeout": parameters.get("timeout", 10)
            })
            
            if not source_element or not target_element:
                return False, f"找不到拖放的元素: {'源' if not source_element else '目标'}"
            
            # 执行拖放操作
            smooth = parameters.get("smooth", "是") == "是"
            duration = float(parameters.get("duration", 0.5))
            
            if smooth:
                # 使用平滑拖动
                chain = source_element[1].new_actions()
                chain.drag_to(target_element[1], duration=duration).run()
            else:
                # 直接拖放
                chain = source_element[1].new_actions()
                chain.drag_to(target_element[1]).run()
            
            return True, f"已成功将元素从 {source_locator_value} 拖放到 {target_locator_value}"
        except Exception as e:
            return False, f"执行拖放操作失败: {str(e)}"

    def _execute_mouse_double_click(self, parameters: Dict[str, Any]) -> Tuple[bool, str]:
        """
        执行鼠标双击操作
        
        Args:
            parameters: 包含参数的字典
                - locator_strategy: 元素定位策略
                - locator_value: 元素定位值
                - timeout: 等待元素出现的超时时间(秒)
                
        Returns:
            (是否成功, 结果信息)
        """
        if not self._page:
            return False, "页面未初始化"
        
        try:
            # 获取要双击的元素
            locator_strategy = parameters.get("locator_strategy", "css")
            locator_value = parameters.get("locator_value", "")
            element = self._get_element({
                "locator_strategy": locator_strategy,
                "locator_value": locator_value,
                "timeout": parameters.get("timeout", 10)
            })
            
            if not element[0]:
                return False, f"找不到要双击的元素: {locator_value}"
            
            # 执行双击操作
            chain = element[1].new_actions()
            chain.double_click().run()
            
            return True, f"已成功双击元素: {locator_value}"
        except Exception as e:
            return False, f"执行双击操作失败: {str(e)}"

    def _execute_mouse_right_click(self, parameters: Dict[str, Any]) -> Tuple[bool, str]:
        """
        执行鼠标右键点击操作
        
        Args:
            parameters: 包含参数的字典
                - locator_strategy: 元素定位策略
                - locator_value: 元素定位值
                - timeout: 等待元素出现的超时时间(秒)
                
        Returns:
            (是否成功, 结果信息)
        """
        if not self._page:
            return False, "页面未初始化"
        
        try:
            # 获取要右键点击的元素
            locator_strategy = parameters.get("locator_strategy", "css")
            locator_value = parameters.get("locator_value", "")
            element = self._get_element({
                "locator_strategy": locator_strategy,
                "locator_value": locator_value,
                "timeout": parameters.get("timeout", 10)
            })
            
            if not element[0]:
                return False, f"找不到要右键点击的元素: {locator_value}"
            
            # 执行右键点击操作
            chain = element[1].new_actions()
            chain.context_click().run()
            
            return True, f"已成功右键点击元素: {locator_value}"
        except Exception as e:
            return False, f"执行右键点击操作失败: {str(e)}"

    def _execute_mouse_move_by_path(self, parameters: Dict[str, Any]) -> Tuple[bool, str]:
        """
        执行鼠标按轨迹移动操作
        
        Args:
            parameters: 包含参数的字典
                - path_points: 轨迹点列表，格式为 "x1,y1;x2,y2;x3,y3"
                - duration: 整个移动过程的持续时间(秒)
                - relative_to_element: 是否相对于元素（否则相对于页面）
                - locator_strategy: 元素定位策略（如果相对于元素）
                - locator_value: 元素定位值（如果相对于元素）
                
        Returns:
            (是否成功, 结果信息)
        """
        if not self._page:
            return False, "页面未初始化"
        
        try:
            # 解析路径点
            path_points_str = parameters.get("path_points", "")
            if not path_points_str:
                return False, "未提供有效的路径点"
            
            points = []
            for point_str in path_points_str.split(";"):
                if "," in point_str:
                    x, y = map(int, point_str.split(","))
                    points.append((x, y))
            
            if len(points) < 2:
                return False, "路径点数量不足，至少需要2个点"
            
            # 确定是否相对于元素
            relative_to_element = parameters.get("relative_to_element", "否") == "是"
            duration = float(parameters.get("duration", 1.0))
            
            if relative_to_element:
                # 获取相对元素
                locator_strategy = parameters.get("locator_strategy", "css")
                locator_value = parameters.get("locator_value", "")
                element = self._get_element({
                    "locator_strategy": locator_strategy,
                    "locator_value": locator_value,
                    "timeout": parameters.get("timeout", 10)
                })
                
                if not element[0]:
                    return False, f"找不到参考元素: {locator_value}"
                
                # 获取元素位置并调整路径点
                rect = element[1].rect
                base_x, base_y = rect["x"], rect["y"]
                
                # 创建动作链并执行移动
                chain = element[1].new_actions()
                
                # 移动到第一个点
                first_x, first_y = points[0]
                chain.move_to(x=first_x, y=first_y)
                
                # 依次移动到后面的点
                for x, y in points[1:]:
                    chain.move_by(x=x-first_x, y=y-first_y)
                    first_x, first_y = x, y
                
                # 执行动作链
                chain.run()
            else:
                # 相对于页面的移动
                chain = self._page.new_actions()
                
                # 移动到第一个点
                first_x, first_y = points[0]
                chain.move_to(x=first_x, y=first_y)
                
                # 依次移动到后面的点
                for x, y in points[1:]:
                    chain.move_by(x=x-first_x, y=y-first_y)
                    first_x, first_y = x, y
                
                # 执行动作链
                chain.run()
            
            return True, f"已成功按轨迹移动鼠标，共{len(points)}个点"
        except Exception as e:
            return False, f"执行鼠标轨迹移动失败: {str(e)}"

    def _execute_click_context_menu_item(self, parameters: Dict[str, Any]) -> Tuple[bool, str]:
        """
        点击上下文菜单项
        
        Args:
            parameters: 包含参数的字典
                - context_menu_item: 上下文菜单项的文本或CSS选择器
                - use_text_match: 是否使用文本匹配（否则使用CSS选择器）
                - timeout: 等待菜单项出现的超时时间(秒)
                
        Returns:
            (是否成功, 结果信息)
        """
        if not self._page:
            return False, "页面未初始化"
        
        try:
            # 获取菜单项参数
            context_menu_item = parameters.get("context_menu_item", "")
            use_text_match = parameters.get("use_text_match", "是") == "是"
            timeout = parameters.get("timeout", 5)
            
            if not context_menu_item:
                return False, "未提供上下文菜单项"
            
            # 查找并点击菜单项
            if use_text_match:
                # 使用文本匹配
                menu_item = self._page.ele(text=context_menu_item, timeout=timeout)
            else:
                # 使用CSS选择器
                menu_item = self._page.ele(context_menu_item, timeout=timeout)
            
            if not menu_item:
                return False, f"找不到上下文菜单项: {context_menu_item}"
            
            # 点击菜单项
            menu_item.click()
            
            return True, f"已成功点击上下文菜单项: {context_menu_item}"
        except Exception as e:
            return False, f"点击上下文菜单项失败: {str(e)}"

    # 为AdvancedInteractions类添加缺失的方法
    def get_element(self, strategy: str, value: str) -> Any:
        """
        获取指定的元素
        
        Args:
            strategy: 定位策略
            value: 定位值
            
        Returns:
            元素对象或None
        """
        parameters = {
            "locator_strategy": strategy,
            "locator_value": value,
            "timeout": 10
        }
        
        success, result = self._get_element(parameters)
        if success:
            return result
        else:
            print(f"获取元素失败: {result}")
            return None
    
    def execute_js(self, script: str, *args) -> Any:
        """
        执行JavaScript代码
        
        Args:
            script: JavaScript代码
            *args: 传递给JavaScript的参数
            
        Returns:
            JavaScript执行结果
        """
        if not self._page:
            print("页面未初始化，无法执行JavaScript")
            return None
        
        try:
            # 使用DrissionPage的run_js方法执行JavaScript
            result = self._page.run_js(script, *args)
            return result
        except Exception as e:
            print(f"执行JavaScript失败: {str(e)}")
            return None
    
    def screenshot_full_page(self, save_path: str) -> bool:
        """
        截取整个页面的截图
        
        Args:
            save_path: 保存截图的路径
            
        Returns:
            是否成功
        """
        if not self._page:
            print("页面未初始化，无法截图")
            return False
        
        try:
            # 使用DrissionPage的截图方法
            self._page.get_screenshot(save_path, full_page=True)
            return True
        except Exception as e:
            print(f"截图失败: {str(e)}")
            return False

    def screenshot(self, save_path: str, element=None) -> bool:
        """
        截取页面可视区域或指定元素的截图
        
        Args:
            save_path: 保存截图的路径
            element: 要截图的元素对象，None表示截取可视区域
            
        Returns:
            是否成功
        """
        if not self._page:
            print("页面未初始化，无法截图")
            return False
        
        try:
            if element is not None:
                # 如果提供了元素，截取元素的截图
                element.get_screenshot(save_path)
            else:
                # 否则截取可视区域
                self._page.get_screenshot(save_path)
            return True
        except Exception as e:
            print(f"截图失败: {str(e)}")
            return False

    def _execute_custom_javascript(self, parameters: Dict[str, Any]) -> Tuple[bool, Any]:
        """
        执行自定义JavaScript代码
        
        Args:
            parameters: 包含JavaScript代码的字典
                - js_code: 要执行的JavaScript代码
                - return_variable: (可选) 存储返回值的变量名
            
        Returns:
            (是否成功, 执行结果或错误信息)
        """
        js_code = parameters.get("js_code", "")
        
        if not js_code:
            return False, "未提供JavaScript代码"
        
        try:
            # 执行JavaScript代码
            result = self._page.run_js(js_code)
            
            # 如果需要返回结果，包装在字典中
            return_value = {"return_value": result}
            
            # 将结果转换为字符串，用于显示
            result_str = str(result)
            if len(result_str) > 100:
                result_str = result_str[:100] + "..."
                
            return True, {"message": f"JavaScript执行成功，结果: {result_str}", "return_value": result}
            
        except Exception as e:
            return False, f"执行JavaScript失败: {str(e)}"

    def _execute_wait_seconds(self, parameters: Dict[str, Any]) -> Tuple[bool, str]:
        """
        等待指定的秒数
        
        Args:
            parameters: 包含等待时间的字典
                - seconds: 要等待的秒数
            
        Returns:
            (是否成功, 结果或错误信息)
        """
        try:
            seconds = float(parameters.get("seconds", "1"))
            time.sleep(seconds)
            return True, f"等待了 {seconds} 秒"
        except Exception as e:
            return False, f"等待失败: {str(e)}"

    def get_element_info(self, element: Any) -> Dict[str, Any]:
        """
        获取元素的详细信息
        
        Args:
            element: 元素对象
            
        Returns:
            包含元素信息的字典，包括标签名、属性、文本等
        """
        if not self._page or not element:
            return {}
        
        try:
            # 获取元素基本信息
            info = {
                "tag": None,
                "id": None,
                "class": None,
                "name": None,
                "text": None,
                "html": None,
                "attributes": {},
                "rect": None,
                "is_displayed": None,
                "is_enabled": None,
            }
            
            # 获取标签名
            try:
                info["tag"] = element.tag
            except:
                pass
                
            # 获取元素ID
            try:
                info["id"] = element.attr("id")
            except:
                pass
                
            # 获取元素类名
            try:
                info["class"] = element.attr("class")
            except:
                pass
                
            # 获取name属性
            try:
                info["name"] = element.attr("name")
            except:
                pass
                
            # 获取元素文本
            try:
                info["text"] = element.text
            except:
                pass
                
            # 获取元素HTML
            try:
                info["html"] = element.html
            except:
                pass
                
            # 获取元素位置和大小
            try:
                info["rect"] = element.rect
            except:
                pass
                
            # 检查元素是否可见
            try:
                if hasattr(element, "is_displayed"):
                    info["is_displayed"] = element.is_displayed()
                else:
                    rect = element.rect
                    info["is_displayed"] = rect and rect["width"] > 0 and rect["height"] > 0
            except:
                pass
                
            # 检查元素是否启用
            try:
                info["is_enabled"] = self._page.run_js("return !arguments[0].disabled", element)
            except:
                pass
                
            # 获取所有属性
            try:
                attrs_js = """
                (function(el) {
                    var attrs = {};
                    if (el && el.attributes) {
                        for (var i = 0; i < el.attributes.length; i++) {
                            var attr = el.attributes[i];
                            attrs[attr.name] = attr.value;
                        }
                    }
                    return attrs;
                })(arguments[0]);
                """
                info["attributes"] = self._page.run_js(attrs_js, element) or {}
            except:
                pass
                
            return info
            
        except Exception as e:
            print(f"获取元素信息失败: {str(e)}")
            return {}
    
    def get_page_info(self) -> Dict[str, Any]:
        """
        获取当前页面的信息
        
        Returns:
            包含页面信息的字典，包括标题、URL、HTML等
        """
        if not self._page:
            return {}
        
        try:
            info = {
                "title": None,
                "url": None,
                "html": None,
                "text": None,
                "cookies": None,
                "window_size": None,
                "page_source": None
            }
            
            # 获取页面标题
            try:
                info["title"] = self._page.title
            except:
                pass
                
            # 获取页面URL
            try:
                info["url"] = self._page.url
            except:
                pass
                
            # 获取页面HTML
            try:
                info["html"] = self._page.html
            except:
                pass
                
            # 获取页面文本
            try:
                info["text"] = self._page.run_js("return document.body.textContent")
            except:
                pass
                
            # 获取页面Cookies
            try:
                info["cookies"] = self.get_cookies()
            except:
                pass
                
            # 获取窗口大小
            try:
                info["window_size"] = self._page.run_js("return {width: window.innerWidth, height: window.innerHeight}")
            except:
                pass
                
            # 获取页面源码
            try:
                info["page_source"] = self._page.html
            except:
                pass
                
            return info
            
        except Exception as e:
            print(f"获取页面信息失败: {str(e)}")
            return {}
    
    def get_cookies(self) -> List[Dict[str, Any]]:
        """
        获取当前页面的所有Cookies
        
        Returns:
            Cookie列表
        """
        if not self._page:
            return []
        
        try:
            # DrissionPage提供了获取Cookies的方法
            if hasattr(self._page, "get_cookies"):
                return self._page.get_cookies()
            else:
                # 如果没有直接方法，使用JavaScript获取
                return self._page.run_js("""
                    (function() {
                        var cookies = document.cookie.split(';');
                        var result = [];
                        for (var i = 0; i < cookies.length; i++) {
                            var cookie = cookies[i].trim();
                            if (cookie) {
                                var parts = cookie.split('=');
                                var name = parts.shift();
                                var value = parts.join('=');
                                result.push({name: name, value: value});
                            }
                        }
                        return result;
                    })();
                """) or []
        except Exception as e:
            print(f"获取Cookies失败: {str(e)}")
            return []
    
    def get_cookie(self, name: str) -> Optional[Dict[str, Any]]:
        """
        获取指定名称的Cookie
        
        Args:
            name: Cookie名称
            
        Returns:
            Cookie字典或None
        """
        if not self._page:
            return None
        
        try:
            cookies = self.get_cookies()
            for cookie in cookies:
                if cookie.get("name") == name:
                    return cookie
            return None
        except Exception as e:
            print(f"获取Cookie失败: {str(e)}")
            return None
    
    def set_cookies(self, cookies: Union[Dict[str, Any], List[Dict[str, Any]]]) -> bool:
        """
        设置Cookies
        
        Args:
            cookies: Cookie字典或列表
            
        Returns:
            是否成功
        """
        if not self._page:
            return False
        
        try:
            # 处理单个Cookie字典的情况
            if isinstance(cookies, dict):
                cookies = [cookies]
                
            # 设置每个Cookie
            for cookie in cookies:
                if "name" not in cookie or "value" not in cookie:
                    continue
                    
                # 使用JavaScript设置Cookie
                js = f"""
                document.cookie = "{cookie['name']}={cookie['value']}; path=/";
                return true;
                """
                self._page.run_js(js)
                
            return True
        except Exception as e:
            print(f"设置Cookies失败: {str(e)}")
            return False
    
    def delete_cookie(self, name: str) -> bool:
        """
        删除指定名称的Cookie
        
        Args:
            name: Cookie名称
            
        Returns:
            是否成功
        """
        if not self._page or not name:
            return False
        
        try:
            # 使用JavaScript删除Cookie
            js = f"""
            document.cookie = "{name}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
            return true;
            """
            self._page.run_js(js)
            return True
        except Exception as e:
            print(f"删除Cookie失败: {str(e)}")
            return False

    def _execute_get_page_info(self, parameters: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """
        执行获取页面信息操作
        
        Args:
            parameters: 包含参数的字典
                - save_to_variable: 保存结果的变量名
                
        Returns:
            (是否成功, 页面信息或错误信息)
        """
        if not self._page:
            return False, "页面未初始化"
        
        try:
            # 获取页面信息
            page_info = self.get_page_info()
            
            # 返回成功和页面信息
            return True, {
                "message": "成功获取页面信息",
                "info": page_info,
                "save_to_variable": parameters.get("save_to_variable", "page_info")
            }
        except Exception as e:
            return False, f"获取页面信息失败: {str(e)}"
    
    def _execute_get_element_info(self, parameters: Dict[str, Any]) -> Tuple[bool, Union[Dict[str, Any], str]]:
        """
        执行获取元素信息操作
        
        Args:
            parameters: 包含参数的字典
                - locator_strategy: 定位策略
                - locator_value: 定位值
                - save_to_variable: 保存结果的变量名
                
        Returns:
            (是否成功, 元素信息或错误信息)
        """
        if not self._page:
            return False, "页面未初始化"
        
        locator_strategy = parameters.get("locator_strategy", "css")
        locator_value = parameters.get("locator_value", "")
        
        if not locator_value:
            return False, "未提供定位符值"
        
        try:
            # 使用DrissionPage的新式定位器语法
            selector = self._convert_to_drission_selector(locator_strategy, locator_value)
            
            # 尝试获取元素
            try:
                element = self._page.ele(selector, timeout=10)
                
                # 获取元素信息
                element_info = self.get_element_info(element)
                
                # 返回成功和元素信息
                return True, {
                    "message": f"成功获取元素信息: {selector}",
                    "info": element_info,
                    "save_to_variable": parameters.get("save_to_variable", "element_info")
                }
            except Exception as find_error:
                return False, f"未找到元素: {selector}: {str(find_error)}"
                
        except Exception as e:
            return False, f"获取元素信息失败: {str(e)}"

    # 新增获取控制台信息相关方法
    def _execute_get_console_logs(self, parameters: Dict[str, Any]) -> Tuple[bool, Any]:
        """
        执行获取浏览器控制台日志的操作
        
        Args:
            parameters: 包含参数的字典
                - mode: 获取模式，可选 "wait"(等待一条)、"all"(获取所有)、"start"(开始监听)、"stop"(停止监听)
                - timeout: 等待超时时间（秒），可选，仅在mode为"wait"时有效
                - save_to_variable: 保存结果的变量名
                
        Returns:
            (是否成功, 控制台信息或错误信息)
        """
        if not self._page:
            return False, "页面未初始化"
        
        # 确保页面对象支持控制台操作
        if not hasattr(self._page, 'console'):
            return False, "当前页面对象不支持控制台操作，请确保使用Chromium/ChromiumPage"
        
        mode = parameters.get("mode", "wait")
        timeout = parameters.get("timeout")
        save_to_variable = parameters.get("save_to_variable", "console_logs")
        
        try:
            if mode == "start":
                # 开始监听控制台
                self._page.console.start()
                return True, "已开始监听控制台信息"
                
            elif mode == "stop":
                # 停止监听控制台
                self._page.console.stop()
                return True, "已停止监听控制台信息"
                
            elif mode == "wait":
                # 等待一条控制台信息
                if timeout is not None:
                    timeout = float(timeout)
                result = self._page.console.wait(timeout=timeout)
                
                # 如果等待超时，返回False
                if result is False:
                    return True, {"message": "等待控制台信息超时", "save_to_variable": save_to_variable, "info": []}
                
                # 将结果转换为可序列化的字典
                log_info = {
                    "source": result.source,
                    "level": result.level,
                    "text": result.text,
                    "url": result.url,
                    "line": result.line,
                    "column": result.column
                }
                
                # 尝试解析body
                try:
                    import json
                    if hasattr(result, 'body') and result.body:
                        log_info["body"] = result.body
                except Exception:
                    log_info["body"] = None
                
                return True, {"message": "成功获取控制台信息", "save_to_variable": save_to_variable, "info": [log_info]}
                
            elif mode == "all":
                # 获取所有已监听到的控制台信息
                messages = self._page.console.messages
                
                # 将结果转换为可序列化的字典列表
                logs_info = []
                for msg in messages:
                    log_info = {
                        "source": msg.source,
                        "level": msg.level,
                        "text": msg.text,
                        "url": msg.url,
                        "line": msg.line,
                        "column": msg.column
                    }
                    
                    # 尝试解析body
                    try:
                        if hasattr(msg, 'body') and msg.body:
                            log_info["body"] = msg.body
                    except Exception:
                        log_info["body"] = None
                    
                    logs_info.append(log_info)
                
                return True, {"message": f"成功获取{len(logs_info)}条控制台信息", "save_to_variable": save_to_variable, "info": logs_info}
                
            else:
                return False, f"不支持的控制台操作模式: {mode}"
            
        except Exception as e:
            return False, f"获取控制台信息失败: {str(e)}"
            
    def _execute_clear_console(self, parameters: Dict[str, Any]) -> Tuple[bool, str]:
        """
        执行清空控制台信息缓存的操作
        
        Args:
            parameters: 参数字典(无需参数)
            
        Returns:
            (是否成功, 结果信息)
        """
        if not self._page:
            return False, "页面未初始化"
        
        # 确保页面对象支持控制台操作
        if not hasattr(self._page, 'console'):
            return False, "当前页面对象不支持控制台操作，请确保使用Chromium/ChromiumPage"
        
        try:
            self._page.console.clear()
            return True, "已清空控制台信息缓存"
        except Exception as e:
            return False, f"清空控制台信息缓存失败: {str(e)}"

    def _execute_js_with_console(self, parameters: Dict[str, Any]) -> Tuple[bool, Any]:
        """
        执行JavaScript代码并记录控制台输出
        
        Args:
            parameters: 包含参数的字典
                - js_code: JavaScript代码
                - wait_timeout: 等待控制台输出的超时时间
                - save_to_variable: 保存控制台输出的变量名
                
        Returns:
            (是否成功, 执行结果和控制台输出)
        """
        if not self._page:
            return False, "页面未初始化"
        
        # 确保页面对象支持控制台操作
        if not hasattr(self._page, 'console'):
            return False, "当前页面对象不支持控制台操作，请确保使用Chromium/ChromiumPage"
        
        js_code = parameters.get("js_code", "")
        wait_timeout = parameters.get("wait_timeout", "5")
        save_to_variable = parameters.get("save_to_variable", "console_output")
        
        if not js_code:
            return False, "未提供JavaScript代码"
        
        try:
            # 先启动控制台监听
            self._page.console.start()
            
            # 执行JavaScript代码
            js_result = self._page.run_js(js_code)
            
            # 尝试获取控制台输出
            try:
                timeout = None if not wait_timeout else float(wait_timeout)
                console_result = self._page.console.wait(timeout=timeout)
                
                # 如果等待超时
                if console_result is False:
                    self._page.console.stop()
                    return True, {
                        "message": "JavaScript执行成功，但等待控制台输出超时",
                        "save_to_variable": save_to_variable,
                        "info": {
                            "js_result": js_result,
                            "console_logs": []
                        }
                    }
                
                # 将结果转换为可序列化的字典
                log_info = {
                    "source": console_result.source,
                    "level": console_result.level,
                    "text": console_result.text,
                    "url": console_result.url,
                    "line": console_result.line,
                    "column": console_result.column
                }
                
                # 尝试获取所有其他日志
                all_logs = [log_info]
                for msg in self._page.console.messages:
                    # 将结果转换为可序列化的字典
                    other_log = {
                        "source": msg.source,
                        "level": msg.level,
                        "text": msg.text,
                        "url": msg.url,
                        "line": msg.line,
                        "column": msg.column
                    }
                    all_logs.append(other_log)
                
                # 停止控制台监听
                self._page.console.stop()
                
                return True, {
                    "message": f"JavaScript执行成功，结果: {js_result}，已获取 {len(all_logs)} 条控制台输出",
                    "save_to_variable": save_to_variable,
                    "info": {
                        "js_result": js_result,
                        "console_logs": all_logs,
                        "logs_count": len(all_logs)
                    }
                }
                
            except Exception as console_error:
                # 停止控制台监听
                self._page.console.stop()
                return True, {
                    "message": f"JavaScript执行成功，结果: {js_result}，但获取控制台输出失败: {str(console_error)}",
                    "save_to_variable": save_to_variable,
                    "info": {
                        "js_result": js_result,
                        "console_logs": [],
                        "logs_count": 0
                    }
                }
            
        except Exception as e:
            # 确保停止控制台监听
            try:
                self._page.console.stop()
            except:
                pass
            return False, f"执行JavaScript失败: {str(e)}"

    def check_connection(self) -> bool:
        """
        检查与浏览器的连接是否有效
        
        Returns:
            连接是否有效
        """
        if not self._page:
            return False
        
        try:
            # 尝试执行简单的JavaScript操作来检查连接
            self._page.run_js("return true;")
            return True
        except Exception as e:
            error_msg = str(e)
            # 检查是否包含连接已断开的错误信息
            connection_lost_msgs = [
                "连接已断开",
                "Connection lost",
                "Target closed",
                "Page crashed",
                "Session closed",
                "WebSocketClosed",
                "Failed to fetch"
            ]
            
            for msg in connection_lost_msgs:
                if msg in error_msg:
                    print(f"浏览器连接已断开: {error_msg}")
                    self._running = False
                    return False
                    
            # 其他错误
            print(f"浏览器连接检查出错，但不是连接断开问题: {error_msg}")
            return False

    # 数据处理相关方法
    def _execute_apply_data_template(self, parameters: Dict[str, Any]) -> Tuple[bool, Any]:
        """
        执行应用数据模板操作
        
        Args:
            parameters: 包含操作参数的字典
                - data_variable: 数据变量名
                - template: 模板内容
                - save_to_variable: 保存结果的变量名
                
        Returns:
            (是否成功, 处理结果或错误信息)
        """
        try:
            from drission_gui_tool.core.data_processor import DataProcessor
            
            data_variable = parameters.get("data_variable", "")
            template = parameters.get("template", "")
            save_to_variable = parameters.get("save_to_variable", "formatted_data")
            
            # 检查参数
            if not data_variable:
                return False, "未提供数据变量名"
            if not template:
                return False, "未提供模板内容"
            
            # 获取数据变量的值
            # 这里依赖流程控制器中的变量管理器，在流程控制器执行时会将变量值传递给参数
            data = parameters.get(data_variable)
            
            if data is None:
                return False, f"找不到变量: {data_variable}"
            
            # 根据数据类型处理
            if isinstance(data, dict):
                # 单个数据对象
                result = DataProcessor.apply_template(data, template)
                return True, {
                    "message": "成功应用模板到数据对象",
                    "info": result,
                    "save_to_variable": save_to_variable
                }
            elif isinstance(data, list):
                # 数据列表
                results = []
                for item in data:
                    if isinstance(item, dict):
                        formatted = DataProcessor.apply_template(item, template)
                        results.append(formatted)
                
                return True, {
                    "message": f"成功应用模板到 {len(results)} 条数据",
                    "info": results,
                    "save_to_variable": save_to_variable
                }
            else:
                return False, f"不支持的数据类型: {type(data).__name__}"
        
        except Exception as e:
            return False, f"应用数据模板失败: {str(e)}"
    
    def _execute_clean_data(self, parameters: Dict[str, Any]) -> Tuple[bool, Any]:
        """
        执行数据清洗操作
        
        Args:
            parameters: 包含操作参数的字典
                - data_variable: 数据变量名
                - cleaning_rules: 清洗规则(JSON)
                - save_to_variable: 保存结果的变量名
                
        Returns:
            (是否成功, 处理结果或错误信息)
        """
        try:
            import json
            from drission_gui_tool.core.data_processor import DataProcessor
            
            data_variable = parameters.get("data_variable", "")
            cleaning_rules_str = parameters.get("cleaning_rules", "")
            save_to_variable = parameters.get("save_to_variable", "cleaned_data")
            
            # 检查参数
            if not data_variable:
                return False, "未提供数据变量名"
            if not cleaning_rules_str:
                return False, "未提供清洗规则"
            
            # 解析清洗规则
            try:
                cleaning_rules = json.loads(cleaning_rules_str)
            except Exception as json_error:
                return False, f"清洗规则格式错误: {str(json_error)}"
            
            # 获取数据变量的值
            data = parameters.get(data_variable)
            
            if data is None:
                return False, f"找不到变量: {data_variable}"
            
            # 根据数据类型处理
            if isinstance(data, dict):
                # 单个数据对象
                result = DataProcessor.clean_data(data, cleaning_rules)
                return True, {
                    "message": "成功清洗数据对象",
                    "info": result,
                    "save_to_variable": save_to_variable
                }
            elif isinstance(data, list):
                # 数据列表
                results = []
                for item in data:
                    if isinstance(item, dict):
                        cleaned = DataProcessor.clean_data(item, cleaning_rules)
                        results.append(cleaned)
                
                return True, {
                    "message": f"成功清洗 {len(results)} 条数据",
                    "info": results,
                    "save_to_variable": save_to_variable
                }
            else:
                return False, f"不支持的数据类型: {type(data).__name__}"
        
        except Exception as e:
            return False, f"数据清洗失败: {str(e)}"
    
    def _execute_validate_data(self, parameters: Dict[str, Any]) -> Tuple[bool, Any]:
        """
        执行数据验证操作
        
        Args:
            parameters: 包含操作参数的字典
                - data_variable: 数据变量名
                - validation_rules: 验证规则(JSON)
                - save_result_to_variable: 保存结果的变量名
                
        Returns:
            (是否成功, 验证结果或错误信息)
        """
        try:
            import json
            from drission_gui_tool.core.data_processor import DataProcessor
            
            data_variable = parameters.get("data_variable", "")
            validation_rules_str = parameters.get("validation_rules", "")
            save_to_variable = parameters.get("save_result_to_variable", "validation_result")
            
            # 检查参数
            if not data_variable:
                return False, "未提供数据变量名"
            if not validation_rules_str:
                return False, "未提供验证规则"
            
            # 解析验证规则
            try:
                validation_rules = json.loads(validation_rules_str)
            except Exception as json_error:
                return False, f"验证规则格式错误: {str(json_error)}"
            
            # 获取数据变量的值
            data = parameters.get(data_variable)
            
            if data is None:
                return False, f"找不到变量: {data_variable}"
            
            # 根据数据类型处理
            if isinstance(data, dict):
                # 单个数据对象
                is_valid, errors = DataProcessor.validate_data(data, validation_rules)
                result = {
                    "is_valid": is_valid,
                    "errors": errors
                }
                
                return True, {
                    "message": "数据验证" + ("通过" if is_valid else "失败"),
                    "info": result,
                    "save_to_variable": save_to_variable
                }
            elif isinstance(data, list):
                # 数据列表
                valid_items = []
                invalid_items = []
                all_errors = []
                
                for i, item in enumerate(data):
                    if isinstance(item, dict):
                        is_valid, errors = DataProcessor.validate_data(item, validation_rules)
                        if is_valid:
                            valid_items.append(item)
                        else:
                            invalid_items.append(item)
                            all_errors.append(f"第 {i+1} 条数据验证失败: {'; '.join(errors)}")
                
                result = {
                    "is_valid": len(invalid_items) == 0,
                    "total": len(data),
                    "valid_count": len(valid_items),
                    "invalid_count": len(invalid_items),
                    "errors": all_errors
                }
                
                return True, {
                    "message": f"数据验证完成，{len(valid_items)}/{len(data)} 条数据有效",
                    "info": result,
                    "save_to_variable": save_to_variable
                }
            else:
                return False, f"不支持的数据类型: {type(data).__name__}"
        
        except Exception as e:
            return False, f"数据验证失败: {str(e)}"
    
    def _execute_export_to_csv(self, parameters: Dict[str, Any]) -> Tuple[bool, str]:
        """
        执行导出CSV操作
        
        Args:
            parameters: 包含操作参数的字典
                - data_variable: 数据变量名
                - file_path: 导出文件路径
                - encoding: 文件编码
                
        Returns:
            (是否成功, 结果消息)
        """
        try:
            from drission_gui_tool.core.data_processor import DataProcessor
            
            data_variable = parameters.get("data_variable", "")
            file_path = parameters.get("file_path", "export_data.csv")
            encoding = parameters.get("encoding", "utf-8")
            
            # 检查参数
            if not data_variable:
                return False, "未提供数据变量名"
            if not file_path:
                return False, "未提供文件路径"
            
            # 获取数据变量的值
            data = parameters.get(data_variable)
            
            if data is None:
                return False, f"找不到变量: {data_variable}"
            
            # 确保数据是列表
            if not isinstance(data, list):
                data = [data] if isinstance(data, dict) else []
            
            # 导出CSV
            success, message = DataProcessor.export_to_csv(data, file_path, encoding)
            return success, message
        
        except Exception as e:
            return False, f"导出CSV失败: {str(e)}"
    
    def _execute_export_to_excel(self, parameters: Dict[str, Any]) -> Tuple[bool, str]:
        """
        执行导出Excel操作
        
        Args:
            parameters: 包含操作参数的字典
                - data_variable: 数据变量名
                - file_path: 导出文件路径
                
        Returns:
            (是否成功, 结果消息)
        """
        try:
            from drission_gui_tool.core.data_processor import DataProcessor
            
            data_variable = parameters.get("data_variable", "")
            file_path = parameters.get("file_path", "export_data.xlsx")
            
            # 检查参数
            if not data_variable:
                return False, "未提供数据变量名"
            if not file_path:
                return False, "未提供文件路径"
            
            # 获取数据变量的值
            data = parameters.get(data_variable)
            
            if data is None:
                return False, f"找不到变量: {data_variable}"
            
            # 确保数据是列表
            if not isinstance(data, list):
                data = [data] if isinstance(data, dict) else []
            
            # 导出Excel
            success, message = DataProcessor.export_to_excel(data, file_path)
            return success, message
        
        except Exception as e:
            return False, f"导出Excel失败: {str(e)}"
    
    def _execute_generate_data_stats(self, parameters: Dict[str, Any]) -> Tuple[bool, Any]:
        """
        执行生成数据统计操作
        
        Args:
            parameters: 包含操作参数的字典
                - data_variable: 数据变量名
                - fields: 要统计的字段列表
                - save_to_variable: 保存结果的变量名
                
        Returns:
            (是否成功, 统计结果或错误信息)
        """
        try:
            from drission_gui_tool.core.data_processor import DataProcessor
            
            data_variable = parameters.get("data_variable", "")
            fields_str = parameters.get("fields", "")
            save_to_variable = parameters.get("save_to_variable", "data_stats")
            
            # 检查参数
            if not data_variable:
                return False, "未提供数据变量名"
            
            # 获取数据变量的值
            data = parameters.get(data_variable)
            
            if data is None:
                return False, f"找不到变量: {data_variable}"
            
            # 确保数据是列表
            if not isinstance(data, list):
                data = [data] if isinstance(data, dict) else []
            
            # 解析字段列表
            fields = []
            if fields_str:
                fields = [field.strip() for field in fields_str.split(",")]
            else:
                # 如果没有指定字段，则使用数据中的所有字段
                if data:
                    if isinstance(data[0], dict):
                        fields = list(data[0].keys())
            
            # 生成统计
            stats = DataProcessor.generate_stats(data, fields)
            
            return True, {
                "message": f"成功生成 {len(stats)} 个字段的统计信息",
                "info": stats,
                "save_to_variable": save_to_variable
            }
        
        except Exception as e:
            return False, f"生成数据统计失败: {str(e)}"
    
    # 数据库操作相关方法
    def _execute_db_connect(self, parameters: Dict[str, Any]) -> Tuple[bool, str]:
        """
        执行连接数据库操作
        
        Args:
            parameters: 包含操作参数的字典
                - connection_id: 连接标识
                - db_type: 数据库类型
                - 其他连接参数...
                
        Returns:
            (是否成功, 结果消息)
        """
        try:
            from drission_gui_tool.core.database_manager import DatabaseManager
            
            # 获取或创建全局数据库管理器
            if not hasattr(self, '_db_manager'):
                self._db_manager = DatabaseManager()
            
            # 获取连接参数
            connection_id = parameters.get("connection_id", "default")
            db_type = parameters.get("db_type", "mysql")
            
            # 构建连接参数字典
            connection_params = {}
            
            # 根据数据库类型设置不同的参数
            if db_type.lower() == "sqlite":
                # SQLite参数
                connection_params["database_path"] = parameters.get("database_path", "database.db")
            else:
                # MySQL, PostgreSQL, MongoDB通用参数
                connection_params["host"] = parameters.get("host", "localhost")
                connection_params["port"] = int(parameters.get("port", 0)) if parameters.get("port") else 0
                connection_params["user"] = parameters.get("user", "")
                connection_params["password"] = parameters.get("password", "")
                connection_params["database"] = parameters.get("database", "")
            
            # 添加连接
            success, message = self._db_manager.add_connection(connection_id, db_type, connection_params)
            return success, message
        
        except Exception as e:
            return False, f"连接数据库失败: {str(e)}"
    
    def _execute_db_disconnect(self, parameters: Dict[str, Any]) -> Tuple[bool, str]:
        """
        执行断开数据库连接操作
        
        Args:
            parameters: 包含操作参数的字典
                - connection_id: 连接标识
                
        Returns:
            (是否成功, 结果消息)
        """
        try:
            # 检查数据库管理器是否存在
            if not hasattr(self, '_db_manager'):
                return False, "数据库管理器未初始化"
            
            connection_id = parameters.get("connection_id", "default")
            
            # 移除连接
            success, message = self._db_manager.remove_connection(connection_id)
            return success, message
        
        except Exception as e:
            return False, f"断开数据库连接失败: {str(e)}"
    
    def _execute_db_execute_query(self, parameters: Dict[str, Any]) -> Tuple[bool, Any]:
        """
        执行数据库查询操作
        
        Args:
            parameters: 包含操作参数的字典
                - connection_id: 连接标识
                - query: SQL查询
                - parameters: 查询参数(JSON)
                - save_to_variable: 保存结果的变量名
                
        Returns:
            (是否成功, 查询结果或错误信息)
        """
        try:
            import json
            
            # 检查数据库管理器是否存在
            if not hasattr(self, '_db_manager'):
                return False, "数据库管理器未初始化"
            
            connection_id = parameters.get("connection_id", "default")
            query = parameters.get("query", "")
            params_str = parameters.get("parameters", "")
            save_to_variable = parameters.get("save_to_variable", "query_results")
            
            # 检查参数
            if not query:
                return False, "未提供查询语句"
            
            # 解析查询参数
            params = None
            if params_str:
                try:
                    params = json.loads(params_str)
                except Exception as json_error:
                    return False, f"查询参数格式错误: {str(json_error)}"
            
            # 执行查询
            success, results = self._db_manager.execute_query(connection_id, query, params)
            
            if success:
                return True, {
                    "message": f"查询成功，返回 {len(results) if isinstance(results, list) else 0} 条结果",
                    "info": results,
                    "save_to_variable": save_to_variable
                }
            else:
                return False, results
        
        except Exception as e:
            return False, f"执行数据库查询失败: {str(e)}"
    
    def _execute_db_execute_update(self, parameters: Dict[str, Any]) -> Tuple[bool, Any]:
        """
        执行数据库更新操作
        
        Args:
            parameters: 包含操作参数的字典
                - connection_id: 连接标识
                - query: SQL更新
                - parameters: 更新参数(JSON)
                - save_to_variable: 保存结果的变量名
                
        Returns:
            (是否成功, 更新结果或错误信息)
        """
        try:
            import json
            
            # 检查数据库管理器是否存在
            if not hasattr(self, '_db_manager'):
                return False, "数据库管理器未初始化"
            
            connection_id = parameters.get("connection_id", "default")
            query = parameters.get("query", "")
            params_str = parameters.get("parameters", "")
            save_to_variable = parameters.get("save_to_variable", "affected_rows")
            
            # 检查参数
            if not query:
                return False, "未提供更新语句"
            
            # 解析更新参数
            params = None
            if params_str:
                try:
                    params = json.loads(params_str)
                except Exception as json_error:
                    return False, f"更新参数格式错误: {str(json_error)}"
            
            # 执行更新
            success, affected_rows = self._db_manager.execute_update(connection_id, query, params)
            
            if success:
                return True, {
                    "message": f"更新成功，影响了 {affected_rows} 行",
                    "info": affected_rows,
                    "save_to_variable": save_to_variable
                }
            else:
                return False, affected_rows
        
        except Exception as e:
            return False, f"执行数据库更新失败: {str(e)}"
    
    def _execute_db_build_select(self, parameters: Dict[str, Any]) -> Tuple[bool, Any]:
        """
        执行构建SELECT查询操作
        
        Args:
            parameters: 包含操作参数的字典
                - table: 表名
                - fields: 字段列表
                - where_condition: WHERE条件(JSON)
                - order_by: 排序
                - limit: 结果限制数量
                - offset: 结果偏移量
                - save_to_variable: 保存结果的变量名
                
        Returns:
            (是否成功, 查询语句或错误信息)
        """
        try:
            import json
            
            # 检查数据库管理器是否存在
            if not hasattr(self, '_db_manager'):
                return False, "数据库管理器未初始化"
            
            table = parameters.get("table", "")
            fields_str = parameters.get("fields", "")
            where_condition_str = parameters.get("where_condition", "")
            order_by_str = parameters.get("order_by", "")
            limit_str = parameters.get("limit", "")
            offset_str = parameters.get("offset", "")
            save_to_variable = parameters.get("save_to_variable", "select_query")
            
            # 检查参数
            if not table:
                return False, "未提供表名"
            
            # 解析字段列表
            fields = None
            if fields_str:
                fields = [field.strip() for field in fields_str.split(",")]
            
            # 解析WHERE条件
            where_condition = None
            if where_condition_str:
                try:
                    where_condition = json.loads(where_condition_str)
                except Exception as json_error:
                    return False, f"WHERE条件格式错误: {str(json_error)}"
            
            # 解析排序
            order_by = None
            if order_by_str:
                order_by = [item.strip() for item in order_by_str.split(",")]
            
            # 解析限制和偏移
            limit = int(limit_str) if limit_str and limit_str.isdigit() else None
            offset = int(offset_str) if offset_str and offset_str.isdigit() else None
            
            # 构建查询
            query = self._db_manager.build_select_query(table, fields, where_condition, order_by, limit, offset)
            
            return True, {
                "message": "成功构建SELECT查询",
                "info": query,
                "save_to_variable": save_to_variable
            }
        
        except Exception as e:
            return False, f"构建SELECT查询失败: {str(e)}"
    
    def _execute_db_build_insert(self, parameters: Dict[str, Any]) -> Tuple[bool, Any]:
        """
        执行构建INSERT查询操作
        
        Args:
            parameters: 包含操作参数的字典
                - table: 表名
                - data: 插入数据(JSON)
                - save_to_variable: 保存结果的变量名
                
        Returns:
            (是否成功, 查询语句或错误信息)
        """
        try:
            import json
            
            # 检查数据库管理器是否存在
            if not hasattr(self, '_db_manager'):
                return False, "数据库管理器未初始化"
            
            table = parameters.get("table", "")
            data_str = parameters.get("data", "")
            save_to_variable = parameters.get("save_to_variable", "insert_query")
            
            # 检查参数
            if not table:
                return False, "未提供表名"
            if not data_str:
                return False, "未提供插入数据"
            
            # 解析插入数据
            try:
                data = json.loads(data_str)
            except Exception as json_error:
                return False, f"插入数据格式错误: {str(json_error)}"
            
            # 构建查询
            query = self._db_manager.build_insert_query(table, data)
            
            return True, {
                "message": "成功构建INSERT查询",
                "info": query,
                "save_to_variable": save_to_variable
            }
        
        except Exception as e:
            return False, f"构建INSERT查询失败: {str(e)}"
    
    def _execute_db_build_update(self, parameters: Dict[str, Any]) -> Tuple[bool, Any]:
        """
        执行构建UPDATE查询操作
        
        Args:
            parameters: 包含操作参数的字典
                - table: 表名
                - data: 更新数据(JSON)
                - where_condition: WHERE条件(JSON)
                - save_to_variable: 保存结果的变量名
                
        Returns:
            (是否成功, 查询语句或错误信息)
        """
        try:
            import json
            
            # 检查数据库管理器是否存在
            if not hasattr(self, '_db_manager'):
                return False, "数据库管理器未初始化"
            
            table = parameters.get("table", "")
            data_str = parameters.get("data", "")
            where_condition_str = parameters.get("where_condition", "")
            save_to_variable = parameters.get("save_to_variable", "update_query")
            
            # 检查参数
            if not table:
                return False, "未提供表名"
            if not data_str:
                return False, "未提供更新数据"
            
            # 解析更新数据
            try:
                data = json.loads(data_str)
            except Exception as json_error:
                return False, f"更新数据格式错误: {str(json_error)}"
            
            # 解析WHERE条件
            where_condition = {}
            if where_condition_str:
                try:
                    where_condition = json.loads(where_condition_str)
                except Exception as json_error:
                    return False, f"WHERE条件格式错误: {str(json_error)}"
            
            # 构建查询
            query = self._db_manager.build_update_query(table, data, where_condition)
            
            return True, {
                "message": "成功构建UPDATE查询",
                "info": query,
                "save_to_variable": save_to_variable
            }
        
        except Exception as e:
            return False, f"构建UPDATE查询失败: {str(e)}"
    
    def _execute_db_build_delete(self, parameters: Dict[str, Any]) -> Tuple[bool, Any]:
        """
        执行构建DELETE查询操作
        
        Args:
            parameters: 包含操作参数的字典
                - table: 表名
                - where_condition: WHERE条件(JSON)
                - save_to_variable: 保存结果的变量名
                
        Returns:
            (是否成功, 查询语句或错误信息)
        """
        try:
            import json
            
            # 检查数据库管理器是否存在
            if not hasattr(self, '_db_manager'):
                return False, "数据库管理器未初始化"
            
            table = parameters.get("table", "")
            where_condition_str = parameters.get("where_condition", "")
            save_to_variable = parameters.get("save_to_variable", "delete_query")
            
            # 检查参数
            if not table:
                return False, "未提供表名"
            
            # 解析WHERE条件
            where_condition = {}
            if where_condition_str:
                try:
                    where_condition = json.loads(where_condition_str)
                except Exception as json_error:
                    return False, f"WHERE条件格式错误: {str(json_error)}"
            
            # 构建查询
            query = self._db_manager.build_delete_query(table, where_condition)
            
            return True, {
                "message": "成功构建DELETE查询",
                "info": query,
                "save_to_variable": save_to_variable
            }
        
        except Exception as e:
            return False, f"构建DELETE查询失败: {str(e)}"
