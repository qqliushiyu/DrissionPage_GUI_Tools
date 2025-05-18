#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
代码生成器模块，提供流程到代码的转换功能。
"""

import os
import time
from typing import Dict, List, Any, Tuple, Optional, Union

class CodeGenerator:
    """
    代码生成器基类，提供基本代码生成功能
    """
    
    def __init__(self):
        """初始化代码生成器"""
        # 代码行缓存
        self._code_lines = []
        # 缩进级别
        self._indent_level = 0
        # 缩进字符
        self._indent_char = "    "  # 4个空格
    
    def generate_code(self, flow_data: Dict[str, Any], 
                     output_path: Optional[str] = None,
                     code_style: str = "standard") -> Tuple[bool, Union[str, List[str]]]:
        """
        生成Python代码
        
        Args:
            flow_data: 流程数据
            output_path: 输出文件路径，如果为None则返回代码行列表
            code_style: 代码风格，可选值: "standard", "compact", "verbose"
            
        Returns:
            (成功标志, 文件路径或代码行列表)
        """
        try:
            # 清空代码缓存
            self._code_lines = []
            self._indent_level = 0
            
            # 生成代码头部
            self._generate_header(flow_data, code_style)
            
            # 生成导入语句
            self._generate_imports(flow_data, code_style)
            
            # 生成主函数
            self._generate_main_function(flow_data, code_style)
            
            # 生成工具函数
            self._generate_utility_functions(flow_data, code_style)
            
            # 生成程序入口
            self._generate_entry_point(flow_data, code_style)
            
            # 如果指定了输出路径，写入文件
            if output_path:
                directory = os.path.dirname(output_path)
                if directory and not os.path.exists(directory):
                    os.makedirs(directory)
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write("\n".join(self._code_lines))
                
                return True, output_path
            else:
                # 否则返回代码行列表
                return True, self._code_lines
                
        except Exception as e:
            return False, f"代码生成失败: {str(e)}"
    
    def _add_line(self, line: str = "") -> None:
        """
        添加代码行
        
        Args:
            line: 代码行内容，不包含缩进
        """
        indented_line = self._indent_char * self._indent_level + line if line else ""
        self._code_lines.append(indented_line)
    
    def _increase_indent(self) -> None:
        """增加缩进级别"""
        self._indent_level += 1
    
    def _decrease_indent(self) -> None:
        """减少缩进级别"""
        if self._indent_level > 0:
            self._indent_level -= 1
    
    def _generate_header(self, flow_data: Dict[str, Any], code_style: str) -> None:
        """
        生成代码头部
        
        Args:
            flow_data: 流程数据
            code_style: 代码风格
        """
        flow_name = flow_data.get("flow_name", "未命名流程")
        
        self._add_line("#!/usr/bin/env python3")
        self._add_line("# -*- coding: utf-8 -*-")
        self._add_line()
        self._add_line(f"# 自动生成的DrissionPage自动化脚本: {flow_name}")
        self._add_line(f"# 生成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        if code_style == "verbose":
            self._add_line("#")
            self._add_line("# 本脚本由DrissionPage自动化GUI工具生成")
            self._add_line("# 流程名称: " + flow_name)
            self._add_line("# 步骤数量: " + str(len(flow_data.get("steps", []))))
            self._add_line("#")
            
            # 添加流程描述
            description = flow_data.get("description", "")
            if description:
                self._add_line("# 流程描述:")
                for line in description.split("\n"):
                    self._add_line(f"# {line}")
                self._add_line("#")
        
        self._add_line()
    
    def _generate_imports(self, flow_data: Dict[str, Any], code_style: str) -> None:
        """
        生成导入语句
        
        Args:
            flow_data: 流程数据
            code_style: 代码风格
        """
        # 基础导入
        self._add_line("from typing import Dict, Any, List, Tuple, Optional")
        self._add_line("import time")
        self._add_line("import os")
        self._add_line("import sys")
        self._add_line("import logging")
        self._add_line()
        
        # DrissionPage导入
        self._add_line("# DrissionPage相关导入")
        self._add_line("from DrissionPage import WebPage, ChromiumPage")
        
        # 分析步骤，确定需要导入的其他模块
        steps = flow_data.get("steps", [])
        needs_regex = any(step.get("action_id") in ["ELEMENT_TEXT_MATCHES", "EXTRACT_TEXT_WITH_REGEX"] for step in steps)
        needs_pandas = any(step.get("action_id") in ["EXPORT_TABLE", "IMPORT_CSV", "IMPORT_EXCEL"] for step in steps)
        needs_random = any("random" in str(step.get("parameters", {})) for step in steps)
        
        if needs_regex:
            self._add_line("import re")
        
        if needs_pandas:
            self._add_line("import pandas as pd")
        
        if needs_random:
            self._add_line("import random")
        
        self._add_line()
    
    def _generate_main_function(self, flow_data: Dict[str, Any], code_style: str) -> None:
        """
        生成主函数
        
        Args:
            flow_data: 流程数据
            code_style: 代码风格
        """
        flow_name = flow_data.get("flow_name", "未命名流程")
        steps = flow_data.get("steps", [])
        
        # 函数声明
        self._add_line("def main():")
        self._increase_indent()
        
        # 函数文档字符串
        if code_style in ["standard", "verbose"]:
            self._add_line('"""')
            self._add_line(f"执行 '{flow_name}' 自动化流程")
            self._add_line()
            
            if code_style == "verbose":
                self._add_line("流程包含以下步骤:")
                for i, step in enumerate(steps):
                    action_id = step.get("action_id", "")
                    parameters = step.get("parameters", {})
                    step_name = parameters.get("__custom_step_name__", action_id)
                    self._add_line(f"- 步骤 {i+1}: {step_name}")
            
            self._add_line('"""')
            self._add_line()
        
        # 设置日志
        self._add_line("# 设置日志")
        self._add_line("logging.basicConfig(")
        self._add_line("    level=logging.INFO,")
        self._add_line("    format='[%(asctime)s] [%(levelname)s] %(message)s',")
        self._add_line("    datefmt='%Y-%m-%d %H:%M:%S'")
        self._add_line(")")
        self._add_line("logger = logging.getLogger(__name__)")
        self._add_line()
        
        # 记录开始日志
        self._add_line(f"logger.info('开始执行流程: {flow_name}')")
        self._add_line()
        
        # 创建浏览器实例
        self._add_line("# 创建浏览器实例")
        self._add_line("try:")
        self._increase_indent()
        self._add_line("page = WebPage(timeout=20)")
        self._add_line("page.set.timeouts(10, 10, 10)")
        self._decrease_indent()
        self._add_line("except Exception as e:")
        self._increase_indent()
        self._add_line("logger.error(f'浏览器初始化失败: {e}')")
        self._add_line("return False")
        self._decrease_indent()
        self._add_line()
        
        # 处理每个步骤
        self._add_line("# 执行流程步骤")
        self._add_line("try:")
        self._increase_indent()
        
        for i, step in enumerate(steps):
            action_id = step.get("action_id", "")
            parameters = step.get("parameters", {})
            
            # 获取步骤名称
            step_name = parameters.get("__custom_step_name__", action_id)
            
            # 添加步骤注释
            self._add_line(f"# 步骤 {i+1}: {step_name}")
            
            # 生成步骤代码
            step_code = self._generate_step_code(action_id, parameters, i, code_style)
            for line in step_code:
                self._add_line(line)
            
            self._add_line()
        
        # 关闭浏览器
        self._add_line("# 关闭浏览器")
        self._add_line("page.quit()")
        self._add_line("logger.info('流程执行完成')")
        self._add_line("return True")
        
        self._decrease_indent()
        self._add_line("except Exception as e:")
        self._increase_indent()
        self._add_line("logger.error(f'流程执行失败: {e}')")
        self._add_line("try:")
        self._increase_indent()
        self._add_line("page.quit()")
        self._decrease_indent()
        self._add_line("except:")
        self._increase_indent()
        self._add_line("pass")
        self._decrease_indent()
        self._add_line("return False")
        self._decrease_indent()
        
        # 结束主函数
        self._decrease_indent()
        self._add_line()
    
    def _generate_utility_functions(self, flow_data: Dict[str, Any], code_style: str) -> None:
        """
        生成工具函数
        
        Args:
            flow_data: 流程数据
            code_style: 代码风格
        """
        # 根据流程步骤确定需要生成哪些工具函数
        steps = flow_data.get("steps", [])
        
        # 检查是否需要等待元素函数
        if any(step.get("action_id") in ["WAIT_FOR_ELEMENT", "WAIT_FOR_ELEMENT_VISIBLE"] for step in steps):
            self._add_line("def wait_for_element(page, selector: str, selector_type: str = 'css', timeout: int = 10, visible: bool = False) -> bool:")
            self._increase_indent()
            self._add_line('"""')
            self._add_line("等待元素出现或可见")
            self._add_line()
            self._add_line("Args:")
            self._add_line("    page: 页面对象")
            self._add_line("    selector: 选择器")
            self._add_line("    selector_type: 选择器类型")
            self._add_line("    timeout: 超时时间（秒）")
            self._add_line("    visible: 是否等待元素可见")
            self._add_line()
            self._add_line("Returns:")
            self._add_line("    是否等待成功")
            self._add_line('"""')
            self._add_line("start_time = time.time()")
            self._add_line("while time.time() - start_time < timeout:")
            self._increase_indent()
            self._add_line("try:")
            self._increase_indent()
            self._add_line("# 动态构建参数字典")
            self._add_line("selector_dict = {selector_type: selector}")
            self._add_line("element = page.ele(**selector_dict)")
            self._add_line("if element:")
            self._increase_indent()
            self._add_line("if not visible or element.is_displayed():")
            self._increase_indent()
            self._add_line("return True")
            self._decrease_indent()
            self._decrease_indent()
            self._add_line("time.sleep(0.5)")
            self._decrease_indent()
            self._add_line("except Exception:")
            self._increase_indent()
            self._add_line("time.sleep(0.5)")
            self._decrease_indent()
            self._decrease_indent()
            self._add_line("return False")
            self._decrease_indent()
            self._add_line()
        
        # 检查是否需要元素提取函数
        if any(step.get("action_id") in ["EXTRACT_TEXT", "EXTRACT_ATTRIBUTE"] for step in steps):
            self._add_line("def extract_data_from_elements(page, selector: str, selector_type: str = 'css', extract_type: str = 'text', attribute_name: str = '') -> List[str]:")
            self._increase_indent()
            self._add_line('"""')
            self._add_line("从元素中提取数据")
            self._add_line()
            self._add_line("Args:")
            self._add_line("    page: 页面对象")
            self._add_line("    selector: 选择器")
            self._add_line("    selector_type: 选择器类型")
            self._add_line("    extract_type: 提取类型，可选值: 'text', 'attribute'")
            self._add_line("    attribute_name: 属性名称，当extract_type为'attribute'时使用")
            self._add_line()
            self._add_line("Returns:")
            self._add_line("    提取的数据列表")
            self._add_line('"""')
            self._add_line("result = []")
            self._add_line("try:")
            self._increase_indent()
            self._add_line("# 动态构建参数字典")
            self._add_line("selector_dict = {selector_type: selector}")
            self._add_line("elements = page.eles(**selector_dict)")
            self._add_line("for element in elements:")
            self._increase_indent()
            self._add_line("if extract_type == 'text':")
            self._increase_indent()
            self._add_line("result.append(element.text)")
            self._decrease_indent()
            self._add_line("elif extract_type == 'attribute' and attribute_name:")
            self._increase_indent()
            self._add_line("result.append(element.attr(attribute_name))")
            self._decrease_indent()
            self._decrease_indent()
            self._decrease_indent()
            self._add_line("except Exception as e:")
            self._increase_indent()
            self._add_line("logging.error(f'提取数据失败: {e}')")
            self._decrease_indent()
            self._add_line("return result")
            self._decrease_indent()
            self._add_line()
    
    def _generate_entry_point(self, flow_data: Dict[str, Any], code_style: str) -> None:
        """
        生成程序入口
        
        Args:
            flow_data: 流程数据
            code_style: 代码风格
        """
        self._add_line("if __name__ == '__main__':")
        self._increase_indent()
        self._add_line("success = main()")
        self._add_line("sys.exit(0 if success else 1)")
        self._decrease_indent()
    
    def _generate_step_code(self, action_id: str, parameters: Dict[str, Any], 
                          step_index: int, code_style: str) -> List[str]:
        """
        为步骤生成Python代码
        
        Args:
            action_id: 动作ID
            parameters: 动作参数
            step_index: 步骤索引
            code_style: 代码风格
            
        Returns:
            代码行列表
        """
        code_lines = []
        
        # 根据不同操作类型生成代码
        if action_id == "PAGE_GET":
            url = parameters.get("url", "")
            code_lines.append(f"url = \"{url}\"")
            code_lines.append("logger.info(f\"正在访问: {url}\")")
            code_lines.append("page.get(url)")
            
        elif action_id == "OPEN_BROWSER":
            url = parameters.get("url", "")
            browser_type = parameters.get("browser_type", "Chrome")
            headless = parameters.get("headless", False)
            
            if code_style == "verbose":
                code_lines.append(f"# 打开浏览器访问: {url}")
                
            code_lines.append(f"url = \"{url}\"")
            code_lines.append("logger.info(f\"正在打开浏览器访问: {url}\")")
            
            # 根据浏览器类型生成不同的初始化代码
            if browser_type.lower() == "chrome":
                code_lines.append(f"page = ChromiumPage(headless={str(headless).lower()})")
            else:
                code_lines.append(f"page = WebPage(headless={str(headless).lower()})")
                
            if url:
                code_lines.append("page.get(url)")
        
        elif action_id == "ELEMENT_CLICK":
            locator_strategy = parameters.get("locator_strategy", "css")
            locator_value = parameters.get("locator_value", "")
            
            if code_style == "verbose":
                code_lines.append(f"# 点击元素: {locator_strategy}='{locator_value}'")
            
            code_lines.append(f"# 构建选择器参数字典")
            code_lines.append(f"selector_dict = {{'{locator_strategy}': '{locator_value}'}}")
            code_lines.append(f"element = page.ele(**selector_dict)")
            code_lines.append("element.click()")
        
        elif action_id == "ELEMENT_INPUT":
            locator_strategy = parameters.get("locator_strategy", "css")
            locator_value = parameters.get("locator_value", "")
            text = parameters.get("text_to_input", "")
            
            if code_style == "verbose":
                code_lines.append(f"# 输入文本: {locator_strategy}='{locator_value}'")
            
            code_lines.append(f"# 构建选择器参数字典")
            code_lines.append(f"selector_dict = {{'{locator_strategy}': '{locator_value}'}}")
            code_lines.append(f"element = page.ele(**selector_dict)")
            code_lines.append(f"element.input(\"{text}\")")
        
        elif action_id == "WAIT" or action_id == "WAIT_SECONDS":
            wait_time = parameters.get("wait_time", 1)
            
            if code_style == "verbose":
                code_lines.append(f"# 等待 {wait_time} 秒")
            
            code_lines.append(f"time.sleep({wait_time})")
        
        elif action_id == "LOG_MESSAGE":
            message = parameters.get("message", "")
            level = parameters.get("level", "INFO").upper()
            
            log_level = {
                "DEBUG": "debug",
                "INFO": "info",
                "WARNING": "warning",
                "ERROR": "error",
                "CRITICAL": "critical"
            }.get(level, "info")
            
            code_lines.append(f"logger.{log_level}(\"{message}\")")
            
        elif action_id == "EXECUTE_JAVASCRIPT":
            js_code = parameters.get("js_code", "")
            variable_name = parameters.get("save_to_variable", "")
            
            if code_style == "verbose":
                code_lines.append("# 执行JavaScript代码")
                code_lines.append(f"# 代码: {js_code}")
            
            # 处理多行JavaScript代码
            if "\n" in js_code:
                code_lines.append(f"js_code = \"\"\"")
                code_lines.append(f"{js_code}")
                code_lines.append(f"\"\"\"")
                
                if variable_name:
                    code_lines.append(f"{variable_name} = page.run_js(js_code)")
                    code_lines.append(f"logger.info(f\"JavaScript执行结果已保存到变量: {variable_name}\")")
                else:
                    code_lines.append(f"page.run_js(js_code)")
                    code_lines.append(f"logger.info(\"JavaScript代码已执行\")")
            else:
                # 单行JavaScript代码
                if variable_name:
                    code_lines.append(f"{variable_name} = page.run_js(\"{js_code}\")")
                    code_lines.append(f"logger.info(f\"JavaScript执行结果已保存到变量: {variable_name}\")")
                else:
                    code_lines.append(f"page.run_js(\"{js_code}\")")
                    code_lines.append(f"logger.info(\"JavaScript代码已执行\")")
        
        elif action_id == "TAKE_SCREENSHOT":
            screenshot_path = parameters.get("screenshot_path", f"screenshot_{step_index}.png")
            element_only = parameters.get("element_only", False)
            
            if element_only:
                locator_strategy = parameters.get("locator_strategy", "css")
                locator_value = parameters.get("locator_value", "")
                
                if code_style == "verbose":
                    code_lines.append(f"# 对元素截图: {locator_strategy}='{locator_value}'")
                
                code_lines.append(f"# 构建选择器参数字典并定位元素")
                code_lines.append(f"selector_dict = {{'{locator_strategy}': '{locator_value}'}}")
                code_lines.append(f"element = page.ele(**selector_dict)")
                code_lines.append(f"element.screenshot(path='{screenshot_path}')")
            else:
                if code_style == "verbose":
                    code_lines.append("# 对页面截图")
                
                code_lines.append(f"page.get_screenshot(path='{screenshot_path}')")
            
            code_lines.append(f"logger.info(f\"截图已保存到: {screenshot_path}\")")
        
        elif action_id == "CLOSE_BROWSER":
            if code_style == "verbose":
                code_lines.append("# 关闭浏览器")
            
            code_lines.append("page.quit()")
            code_lines.append("logger.info(\"浏览器已关闭\")")
        
        elif action_id == "PAGE_REFRESH":
            if code_style == "verbose":
                code_lines.append("# 刷新页面")
            
            code_lines.append("page.refresh()")
            code_lines.append("logger.info(\"页面已刷新\")")
        
        else:
            # 默认代码
            code_lines.append(f"# 未实现的操作: {action_id}")
            code_lines.append("pass")
        
        return code_lines 