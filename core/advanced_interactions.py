#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
高级交互操作模块，提供超出基本点击、输入之外的复杂交互功能。
支持拖放操作、高级鼠标事件、键盘组合键和特殊表单元素处理等。
"""

from typing import Dict, List, Optional, Tuple, Any, Union
import time
import json
import os
from pathlib import Path


class AdvancedInteractions:
    """
    高级交互操作类，提供复杂的页面交互功能。
    """
    
    def __init__(self, drission_engine=None):
        """
        初始化高级交互操作实例
        
        Args:
            drission_engine: DrissionPage引擎实例，用于页面交互
        """
        self._engine = drission_engine
    
    def drag_and_drop(self, source_selector: Dict[str, str], target_selector: Dict[str, str], 
                      smooth: bool = True, speed: str = "medium") -> Tuple[bool, str]:
        """
        执行拖放操作
        
        Args:
            source_selector: 源元素选择器，格式为 {strategy: value}
            target_selector: 目标元素选择器，格式为 {strategy: value}
            smooth: 是否使用平滑拖动（默认为True）
            speed: 拖动速度，可选值为 "slow", "medium", "fast"
            
        Returns:
            (成功标志, 消息)
        """
        if not self._engine:
            return False, "未配置DrissionPage引擎"
        
        try:
            # 执行拖放操作的详细步骤
            # 1. 定位源元素和目标元素
            source_strategy = list(source_selector.keys())[0]
            source_value = source_selector[source_strategy]
            
            target_strategy = list(target_selector.keys())[0]
            target_value = target_selector[target_strategy]
            
            # 2. 获取源元素和目标元素
            source_element = self._engine.get_element(source_strategy, source_value)
            target_element = self._engine.get_element(target_strategy, target_value)
            
            if not source_element:
                return False, f"未找到源元素: {source_strategy}='{source_value}'"
            if not target_element:
                return False, f"未找到目标元素: {target_strategy}='{target_value}'"
            
            # 3. 执行拖放操作
            # 根据DrissionPage实际API调整
            speed_ms = {
                "slow": 1000,
                "medium": 500,
                "fast": 200
            }.get(speed.lower(), 500)
            
            if smooth:
                # 平滑拖放
                self._engine.execute_js("""
                    (function(source, target, duration) {
                        // 获取源元素和目标元素的位置
                        var sourceRect = source.getBoundingClientRect();
                        var targetRect = target.getBoundingClientRect();
                        
                        // 计算起点和终点
                        var startX = sourceRect.left + sourceRect.width / 2;
                        var startY = sourceRect.top + sourceRect.height / 2;
                        var endX = targetRect.left + targetRect.width / 2;
                        var endY = targetRect.top + targetRect.height / 2;
                        
                        // 创建鼠标事件
                        function createMouseEvent(type, x, y) {
                            var event = new MouseEvent(type, {
                                bubbles: true,
                                cancelable: true,
                                view: window,
                                clientX: x,
                                clientY: y
                            });
                            return event;
                        }
                        
                        // 执行拖放操作
                        source.dispatchEvent(createMouseEvent('mousedown', startX, startY));
                        
                        // 平滑移动
                        var steps = duration / 10;
                        var deltaX = (endX - startX) / steps;
                        var deltaY = (endY - startY) / steps;
                        
                        var currentX = startX;
                        var currentY = startY;
                        
                        var moveInterval = setInterval(function() {
                            currentX += deltaX;
                            currentY += deltaY;
                            document.elementFromPoint(currentX, currentY).dispatchEvent(
                                createMouseEvent('mousemove', currentX, currentY)
                            );
                            
                            if ((deltaX > 0 && currentX >= endX) || 
                                (deltaX <= 0 && currentX <= endX)) {
                                clearInterval(moveInterval);
                                target.dispatchEvent(createMouseEvent('mouseup', endX, endY));
                            }
                        }, 10);
                    })(arguments[0], arguments[1], arguments[2]);
                """, source_element, target_element, speed_ms)
            else:
                # 直接拖放
                self._engine.execute_js("""
                    (function(source, target) {
                        // 创建拖放事件
                        var dragStartEvent = new MouseEvent('dragstart', {
                            bubbles: true,
                            cancelable: true,
                            view: window
                        });
                        
                        var dragEnterEvent = new MouseEvent('dragenter', {
                            bubbles: true,
                            cancelable: true,
                            view: window
                        });
                        
                        var dragOverEvent = new MouseEvent('dragover', {
                            bubbles: true,
                            cancelable: true,
                            view: window
                        });
                        
                        var dropEvent = new MouseEvent('drop', {
                            bubbles: true,
                            cancelable: true,
                            view: window
                        });
                        
                        var dragEndEvent = new MouseEvent('dragend', {
                            bubbles: true,
                            cancelable: true,
                            view: window
                        });
                        
                        // 设置拖放数据
                        source.setAttribute('draggable', 'true');
                        
                        // 执行拖放
                        source.dispatchEvent(dragStartEvent);
                        target.dispatchEvent(dragEnterEvent);
                        target.dispatchEvent(dragOverEvent);
                        target.dispatchEvent(dropEvent);
                        source.dispatchEvent(dragEndEvent);
                    })(arguments[0], arguments[1]);
                """, source_element, target_element)
            
            return True, "拖放操作执行成功"
            
        except Exception as e:
            return False, f"拖放操作执行失败: {str(e)}"
    
    def mouse_hover(self, selector: Dict[str, str], duration: float = 0.5) -> Tuple[bool, str]:
        """
        鼠标悬停在元素上
        
        Args:
            selector: 元素选择器，格式为 {strategy: value}
            duration: 悬停时间（秒）
            
        Returns:
            (成功标志, 消息)
        """
        if not self._engine:
            return False, "未配置DrissionPage引擎"
        
        try:
            strategy = list(selector.keys())[0]
            value = selector[strategy]
            
            element = self._engine.get_element(strategy, value)
            if not element:
                return False, f"未找到元素: {strategy}='{value}'"
            
            # 移动鼠标到元素上
            self._engine.execute_js("""
                (function(element) {
                    var rect = element.getBoundingClientRect();
                    var x = rect.left + rect.width / 2;
                    var y = rect.top + rect.height / 2;
                    
                    var event = new MouseEvent('mouseover', {
                        bubbles: true,
                        cancelable: true,
                        view: window,
                        clientX: x,
                        clientY: y
                    });
                    
                    element.dispatchEvent(event);
                })(arguments[0]);
            """, element)
            
            # 等待指定时间
            time.sleep(duration)
            
            return True, "鼠标悬停操作执行成功"
            
        except Exception as e:
            return False, f"鼠标悬停操作执行失败: {str(e)}"
    
    def double_click(self, selector: Dict[str, str]) -> Tuple[bool, str]:
        """
        双击元素
        
        Args:
            selector: 元素选择器，格式为 {strategy: value}
            
        Returns:
            (成功标志, 消息)
        """
        if not self._engine:
            return False, "未配置DrissionPage引擎"
        
        try:
            strategy = list(selector.keys())[0]
            value = selector[strategy]
            
            element = self._engine.get_element(strategy, value)
            if not element:
                return False, f"未找到元素: {strategy}='{value}'"
            
            # 执行双击操作
            self._engine.execute_js("""
                (function(element) {
                    var rect = element.getBoundingClientRect();
                    var x = rect.left + rect.width / 2;
                    var y = rect.top + rect.height / 2;
                    
                    var event = new MouseEvent('dblclick', {
                        bubbles: true,
                        cancelable: true,
                        view: window,
                        clientX: x,
                        clientY: y
                    });
                    
                    element.dispatchEvent(event);
                })(arguments[0]);
            """, element)
            
            return True, "双击操作执行成功"
            
        except Exception as e:
            return False, f"双击操作执行失败: {str(e)}"
    
    def right_click(self, selector: Dict[str, str]) -> Tuple[bool, str]:
        """
        右键点击元素
        
        Args:
            selector: 元素选择器，格式为 {strategy: value}
            
        Returns:
            (成功标志, 消息)
        """
        if not self._engine:
            return False, "未配置DrissionPage引擎"
        
        try:
            strategy = list(selector.keys())[0]
            value = selector[strategy]
            
            element = self._engine.get_element(strategy, value)
            if not element:
                return False, f"未找到元素: {strategy}='{value}'"
            
            # 执行右键点击操作
            self._engine.execute_js("""
                (function(element) {
                    var rect = element.getBoundingClientRect();
                    var x = rect.left + rect.width / 2;
                    var y = rect.top + rect.height / 2;
                    
                    var event = new MouseEvent('contextmenu', {
                        bubbles: true,
                        cancelable: true,
                        view: window,
                        button: 2,
                        buttons: 2,
                        clientX: x,
                        clientY: y
                    });
                    
                    element.dispatchEvent(event);
                })(arguments[0]);
            """, element)
            
            return True, "右键点击操作执行成功"
            
        except Exception as e:
            return False, f"右键点击操作执行失败: {str(e)}"
    
    def press_key_combination(self, selector: Dict[str, str], keys: List[str]) -> Tuple[bool, str]:
        """
        在元素上按下键盘组合键
        
        Args:
            selector: 元素选择器，格式为 {strategy: value}
            keys: 键盘按键列表，如 ["Control", "c"] 表示Ctrl+C
            
        Returns:
            (成功标志, 消息)
        """
        if not self._engine:
            return False, "未配置DrissionPage引擎"
        
        try:
            strategy = list(selector.keys())[0]
            value = selector[strategy]
            
            element = self._engine.get_element(strategy, value)
            if not element:
                return False, f"未找到元素: {strategy}='{value}'"
            
            # 将键盘按键列表转换为JavaScript可识别的格式
            js_keys = json.dumps(keys, ensure_ascii=False)
            
            # 执行键盘组合键
            self._engine.execute_js(f"""
                (function(element, keys) {{
                    // 聚焦元素
                    element.focus();
                    
                    // 按下所有按键
                    keys.forEach(function(key) {{
                        var downEvent = new KeyboardEvent('keydown', {{
                            bubbles: true,
                            cancelable: true,
                            key: key
                        }});
                        element.dispatchEvent(downEvent);
                    }});
                    
                    // 松开所有按键（逆序）
                    for (var i = keys.length - 1; i >= 0; i--) {{
                        var upEvent = new KeyboardEvent('keyup', {{
                            bubbles: true,
                            cancelable: true,
                            key: keys[i]
                        }});
                        element.dispatchEvent(upEvent);
                    }}
                }})(arguments[0], {js_keys});
            """, element)
            
            return True, "键盘组合键操作执行成功"
            
        except Exception as e:
            return False, f"键盘组合键操作执行失败: {str(e)}"
    
    def handle_rich_text_editor(self, selector: Dict[str, str], content: str, 
                               editor_type: str = "generic") -> Tuple[bool, str]:
        """
        处理富文本编辑器
        
        Args:
            selector: 编辑器元素选择器，格式为 {strategy: value}
            content: 要输入的内容，可以包含HTML标记
            editor_type: 编辑器类型，支持 "generic", "tinymce", "ckeditor", "quill"
            
        Returns:
            (成功标志, 消息)
        """
        if not self._engine:
            return False, "未配置DrissionPage引擎"
        
        try:
            strategy = list(selector.keys())[0]
            value = selector[strategy]
            
            element = self._engine.get_element(strategy, value)
            if not element:
                return False, f"未找到元素: {strategy}='{value}'"
            
            # 转义内容中的引号，防止注入
            escaped_content = content.replace("'", "\\'").replace('"', '\\"')
            
            # 根据不同类型的编辑器执行相应的脚本
            if editor_type.lower() == "tinymce":
                # TinyMCE编辑器
                self._engine.execute_js(f"""
                    (function() {{
                        // 查找TinyMCE实例
                        if (typeof tinymce !== 'undefined') {{
                            var editors = tinymce.editors;
                            for (var i = 0; i < editors.length; i++) {{
                                editors[i].setContent('{escaped_content}');
                            }}
                        }}
                    }})();
                """)
                
            elif editor_type.lower() == "ckeditor":
                # CKEditor编辑器
                self._engine.execute_js(f"""
                    (function() {{
                        // 查找CKEditor实例
                        if (typeof CKEDITOR !== 'undefined') {{
                            for (var name in CKEDITOR.instances) {{
                                CKEDITOR.instances[name].setData('{escaped_content}');
                            }}
                        }}
                    }})();
                """)
                
            elif editor_type.lower() == "quill":
                # Quill编辑器
                self._engine.execute_js(f"""
                    (function(element) {{
                        // 查找Quill实例
                        var quill = element.__quill;
                        if (quill) {{
                            quill.clipboard.dangerouslyPasteHTML('{escaped_content}');
                        }}
                    }})(arguments[0]);
                """, element)
                
            else:
                # 通用方法，适用于contenteditable元素
                self._engine.execute_js(f"""
                    (function(element) {{
                        // 检查是否为contenteditable元素
                        if (element.isContentEditable) {{
                            element.innerHTML = '{escaped_content}';
                            
                            // 触发input和change事件
                            var inputEvent = new Event('input', {{ bubbles: true }});
                            var changeEvent = new Event('change', {{ bubbles: true }});
                            
                            element.dispatchEvent(inputEvent);
                            element.dispatchEvent(changeEvent);
                        }}
                    }})(arguments[0]);
                """, element)
            
            return True, "富文本编辑器内容设置成功"
            
        except Exception as e:
            return False, f"富文本编辑器操作失败: {str(e)}"
    
    def handle_custom_dropdown(self, selector: Dict[str, str], option_text: str) -> Tuple[bool, str]:
        """
        处理自定义下拉框
        
        Args:
            selector: 下拉框元素选择器，格式为 {strategy: value}
            option_text: 要选择的选项文本
            
        Returns:
            (成功标志, 消息)
        """
        if not self._engine:
            return False, "未配置DrissionPage引擎"
        
        try:
            strategy = list(selector.keys())[0]
            value = selector[strategy]
            
            dropdown_element = self._engine.get_element(strategy, value)
            if not dropdown_element:
                return False, f"未找到下拉框元素: {strategy}='{value}'"
            
            # 点击下拉框以展开选项
            self._engine.execute_js("""
                (function(element) {
                    // 触发点击事件以展开下拉框
                    element.click();
                })(arguments[0]);
            """, dropdown_element)
            
            # 等待选项加载（可能是动态加载的）
            time.sleep(0.5)
            
            # 查找并点击指定的选项
            escaped_option_text = option_text.replace("'", "\\'").replace('"', '\\"')
            option_selected = self._engine.execute_js(f"""
                (function() {{
                    // 查找所有可能的选项元素
                    var options = document.querySelectorAll('li, div[role="option"], div.option, .dropdown-item, .select-option');
                    
                    for (var i = 0; i < options.length; i++) {{
                        var option = options[i];
                        if (option.innerText.includes('{escaped_option_text}')) {{
                            // 找到匹配的选项，点击它
                            option.click();
                            return true;
                        }}
                    }}
                    
                    // 没有找到匹配的选项
                    return false;
                }})();
            """)
            
            if option_selected:
                return True, f"在自定义下拉框中选择了选项: {option_text}"
            else:
                return False, f"在下拉框中未找到选项: {option_text}"
            
        except Exception as e:
            return False, f"处理自定义下拉框失败: {str(e)}"
    
    def scroll_to_element(self, selector: Dict[str, str], 
                          align: str = "center") -> Tuple[bool, str]:
        """
        滚动到元素位置
        
        Args:
            selector: 元素选择器，格式为 {strategy: value}
            align: 对齐方式，可选值为 "start", "center", "end"
            
        Returns:
            (成功标志, 消息)
        """
        if not self._engine:
            return False, "未配置DrissionPage引擎"
        
        try:
            strategy = list(selector.keys())[0]
            value = selector[strategy]
            
            element = self._engine.get_element(strategy, value)
            if not element:
                return False, f"未找到元素: {strategy}='{value}'"
            
            # 滚动到元素
            self._engine.execute_js(f"""
                arguments[0].scrollIntoView({{
                    behavior: 'smooth',
                    block: '{align}'
                }});
            """, element)
            
            # 等待滚动完成
            time.sleep(0.5)
            
            return True, "滚动到元素位置成功"
            
        except Exception as e:
            return False, f"滚动到元素位置失败: {str(e)}"
    
    def take_screenshot(self, save_path: str, 
                        element_selector: Optional[Dict[str, str]] = None,
                        save_full_page: bool = False) -> Tuple[bool, str]:
        """
        对页面或指定元素进行截图
        
        Args:
            save_path: 截图保存路径
            element_selector: 元素选择器，格式为 {strategy: value}，如果不提供则截取可视区域
            save_full_page: 是否截取整个页面（仅当element_selector为None时有效）
            
        Returns:
            (成功标志, 消息或保存的截图路径)
        """
        if not self._engine:
            return False, "未配置DrissionPage引擎"
        
        try:
            # 确保保存路径的目录存在
            save_dir = os.path.dirname(save_path)
            os.makedirs(save_dir, exist_ok=True)
            
            # 处理文件后缀
            if not save_path.lower().endswith(('.png', '.jpg', '.jpeg')):
                save_path += '.png'
            
            # 截图处理
            if element_selector:
                # 获取元素
                strategy = list(element_selector.keys())[0]
                value = element_selector[strategy]
                
                element = self._engine.get_element(strategy, value)
                if not element:
                    return False, f"未找到元素: {strategy}='{value}'"
                
                # 对元素进行截图
                try:
                    element.screenshot(path=save_path)
                    return True, f"元素截图已保存到: {save_path}"
                except Exception as e:
                    return False, f"元素截图失败: {str(e)}"
            else:
                # 对页面进行截图
                try:
                    if save_full_page:
                        # 截取整个页面
                        self._engine.screenshot_full_page(save_path)
                        return True, f"整页截图已保存到: {save_path}"
                    else:
                        # 截取可视区域
                        self._engine.screenshot(save_path)
                        return True, f"可视区域截图已保存到: {save_path}"
                except Exception as e:
                    return False, f"页面截图失败: {str(e)}"
                
        except Exception as e:
            return False, f"截图操作失败: {str(e)}"
    
    def switch_to_iframe(self, iframe_selector: Dict[str, str]) -> Tuple[bool, str]:
        """
        切换到指定的iframe中进行操作
        
        Args:
            iframe_selector: iframe元素选择器，格式为 {strategy: value}
            
        Returns:
            (成功标志, 消息)
        """
        if not self._engine:
            return False, "未配置DrissionPage引擎"
        
        try:
            # 获取iframe元素
            strategy = list(iframe_selector.keys())[0]
            value = iframe_selector[strategy]
            
            iframe_element = self._engine.get_element(strategy, value)
            if not iframe_element:
                return False, f"未找到iframe元素: {strategy}='{value}'"
            
            # 切换到iframe
            try:
                self._engine.switch_to_frame(iframe_element)
                return True, f"已切换到iframe: {strategy}='{value}'"
            except Exception as e:
                return False, f"切换到iframe失败: {str(e)}"
                
        except Exception as e:
            return False, f"iframe操作失败: {str(e)}"
    
    def switch_to_parent_frame(self) -> Tuple[bool, str]:
        """
        从iframe切换回父级框架
        
        Returns:
            (成功标志, 消息)
        """
        if not self._engine:
            return False, "未配置DrissionPage引擎"
        
        try:
            self._engine.switch_to_parent_frame()
            return True, "已切换回父级框架"
        except Exception as e:
            return False, f"切换回父级框架失败: {str(e)}"
    
    def switch_to_default_content(self) -> Tuple[bool, str]:
        """
        从iframe切换回主文档
        
        Returns:
            (成功标志, 消息)
        """
        if not self._engine:
            return False, "未配置DrissionPage引擎"
        
        try:
            self._engine.switch_to_default_content()
            return True, "已切换回主文档"
        except Exception as e:
            return False, f"切换回主文档失败: {str(e)}"
    
    def upload_file(self, file_input_selector: Dict[str, str], 
                   file_path: str) -> Tuple[bool, str]:
        """
        向文件输入框上传文件
        
        Args:
            file_input_selector: 文件输入框元素选择器，格式为 {strategy: value}
            file_path: 要上传的文件路径
            
        Returns:
            (成功标志, 消息)
        """
        if not self._engine:
            return False, "未配置DrissionPage引擎"
        
        try:
            # 检查文件是否存在
            if not os.path.isfile(file_path):
                return False, f"文件不存在: {file_path}"
            
            # 获取文件输入元素
            strategy = list(file_input_selector.keys())[0]
            value = file_input_selector[strategy]
            
            file_input = self._engine.get_element(strategy, value)
            if not file_input:
                return False, f"未找到文件输入框: {strategy}='{value}'"
            
            # 上传文件
            try:
                # DrissionPage中，设置文件输入框的值就是上传文件
                file_input.input(file_path)
                return True, f"文件已上传: {file_path}"
            except Exception as e:
                return False, f"文件上传失败: {str(e)}"
                
        except Exception as e:
            return False, f"文件上传操作失败: {str(e)}"
    
    def scroll_page(self, direction: str = "down", distance: int = 500) -> Tuple[bool, str]:
        """
        滚动页面
        
        Args:
            direction: 滚动方向，可选值为 "up", "down", "left", "right"
            distance: 滚动距离（像素）
            
        Returns:
            (成功标志, 消息)
        """
        if not self._engine:
            return False, "未配置DrissionPage引擎"
        
        try:
            # 根据方向确定滚动的JavaScript代码
            scroll_script = ""
            if direction == "down":
                scroll_script = f"window.scrollBy(0, {distance});"
            elif direction == "up":
                scroll_script = f"window.scrollBy(0, -{distance});"
            elif direction == "right":
                scroll_script = f"window.scrollBy({distance}, 0);"
            elif direction == "left":
                scroll_script = f"window.scrollBy(-{distance}, 0);"
            else:
                return False, f"不支持的滚动方向: {direction}"
            
            # 执行滚动脚本
            self._engine.execute_js(scroll_script)
            return True, f"页面向{direction}滚动了{distance}像素"
            
        except Exception as e:
            return False, f"页面滚动失败: {str(e)}"
    
    def manage_cookies(self, action: str, cookie_data: Optional[Dict[str, Any]] = None,
                      cookie_name: Optional[str] = None) -> Tuple[bool, Any]:
        """
        管理浏览器Cookie
        
        Args:
            action: 操作类型，可选值为 "get_all", "get", "set", "delete", "delete_all"
            cookie_data: 要设置的Cookie数据，格式为 {name: value, ...}，仅当action="set"时需要
            cookie_name: 要获取或删除的Cookie名称，仅当action="get"或action="delete"时需要
            
        Returns:
            (成功标志, Cookie数据或消息)
        """
        if not self._engine:
            return False, "未配置DrissionPage引擎"
        
        try:
            if action == "get_all":
                # 获取所有Cookie
                cookies = self._engine.get_cookies()
                return True, cookies
            
            elif action == "get":
                # 获取指定Cookie
                if not cookie_name:
                    return False, "获取Cookie时需要提供Cookie名称"
                
                cookie = self._engine.get_cookie(cookie_name)
                if cookie:
                    return True, cookie
                else:
                    return False, f"Cookie不存在: {cookie_name}"
            
            elif action == "set":
                # 设置Cookie
                if not cookie_data:
                    return False, "设置Cookie时需要提供Cookie数据"
                
                self._engine.set_cookies(cookie_data)
                return True, f"Cookie已设置: {cookie_data}"
            
            elif action == "delete":
                # 删除指定Cookie
                if not cookie_name:
                    return False, "删除Cookie时需要提供Cookie名称"
                
                self._engine.delete_cookie(cookie_name)
                return True, f"Cookie已删除: {cookie_name}"
            
            elif action == "delete_all":
                # 删除所有Cookie
                self._engine.delete_all_cookies()
                return True, "所有Cookie已删除"
            
            else:
                return False, f"不支持的Cookie操作: {action}"
                
        except Exception as e:
            return False, f"Cookie操作失败: {str(e)}" 