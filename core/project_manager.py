#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
项目管理器模块，负责自动化项目的保存、加载和管理。
"""

import os
import json
import time
from typing import Dict, List, Tuple, Any, Optional, Union

from drission_gui_tool.common.constants import FLOW_FILE_EXTENSION

class ProjectManager:
    """
    项目管理器类，提供项目保存、加载和管理功能。
    """
    
    @staticmethod
    def save_flow(file_path: str, flow_name: str, steps: List[Dict[str, Any]]) -> Tuple[bool, str]:
        """
        保存流程到文件
        
        Args:
            file_path: 文件路径
            flow_name: 流程名称
            steps: 流程步骤列表
            
        Returns:
            (成功标志, 消息)
        """
        try:
            # 创建保存数据
            flow_data = {
                "flow_name": flow_name,
                "steps": steps,
                "created_at": time.time(),
                "updated_at": time.time(),
                "version": "1.0.0"
            }
            
            # 确保目录存在
            directory = os.path.dirname(file_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
            
            # 写入文件
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(flow_data, f, ensure_ascii=False, indent=2)
            
            return True, f"流程已成功保存到: {file_path}"
            
        except Exception as e:
            return False, f"保存流程失败: {str(e)}"
    
    @staticmethod
    def load_flow(file_path: str) -> Tuple[bool, Union[Dict[str, Any], str]]:
        """
        从文件加载流程
        
        Args:
            file_path: 文件路径
            
        Returns:
            (成功标志, 流程数据或错误消息)
        """
        try:
            # 检查文件是否存在
            if not os.path.exists(file_path):
                return False, f"文件不存在: {file_path}"
            
            # 读取文件
            with open(file_path, 'r', encoding='utf-8') as f:
                flow_data = json.load(f)
            
            # 验证必要字段
            if "flow_name" not in flow_data or "steps" not in flow_data:
                return False, "无效的流程文件格式: 缺少必要字段"
            
            return True, flow_data
            
        except json.JSONDecodeError:
            return False, f"无效的JSON格式: {file_path}"
        except Exception as e:
            return False, f"加载流程失败: {str(e)}"
    
    @staticmethod
    def export_to_script(file_path: str, flow_data: Dict[str, Any], code_style: str = "standard") -> Tuple[bool, str]:
        """
        将流程导出为Python脚本
        
        Args:
            file_path: 导出文件路径
            flow_data: 流程数据
            code_style: 代码风格，可选值: "standard", "compact", "verbose"
            
        Returns:
            (成功标志, 消息)
        """
        try:
            flow_name = flow_data.get("flow_name", "未命名流程")
            steps = flow_data.get("steps", [])
            description = flow_data.get("description", "")
            
            # 生成Python脚本
            python_code = [
                "#!/usr/bin/env python3",
                "# -*- coding: utf-8 -*-",
                "",
                f"# 自动生成的DrissionPage自动化脚本: {flow_name}",
                f"# 生成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}",
                "",
            ]
            
            # 添加详细说明（如果是verbose模式）
            if code_style == "verbose":
                python_code.extend([
                    "#",
                    "# 本脚本由DrissionPage自动化GUI工具生成",
                    f"# 流程名称: {flow_name}",
                    f"# 步骤数量: {len(steps)}",
                    "#",
                ])
                
                # 添加流程描述
                if description:
                    python_code.append("# 流程描述:")
                    for line in description.split("\n"):
                        python_code.append(f"# {line}")
                    python_code.append("#")
                
            python_code.append("")
            
            # 添加导入语句
            python_code.extend([
                "from typing import Dict, Any, List, Tuple, Optional",
                "import time",
                "import os",
                "import sys",
                "import logging",
                "",
                "# DrissionPage相关导入",
                "from DrissionPage import WebPage, ChromiumPage",
            ])
            
            # 分析步骤，确定需要导入的其他模块
            needs_regex = any(step.get("action_id") in ["ELEMENT_TEXT_MATCHES", "EXTRACT_TEXT_WITH_REGEX"] for step in steps)
            needs_pandas = any(step.get("action_id") in ["EXPORT_TABLE", "IMPORT_CSV", "IMPORT_EXCEL"] for step in steps)
            needs_random = any("random" in str(step.get("parameters", {})) for step in steps)
            
            if needs_regex:
                python_code.append("import re")
            
            if needs_pandas:
                python_code.append("import pandas as pd")
            
            if needs_random:
                python_code.append("import random")
                
            python_code.append("")
            
            # 添加工具函数
            if any(step.get("action_id") in ["WAIT_FOR_ELEMENT", "WAIT_FOR_ELEMENT_VISIBLE"] for step in steps):
                python_code.extend([
                    "def wait_for_element(page, selector: str, selector_type: str = 'css', timeout: int = 10, visible: bool = False) -> bool:",
                    "    \"\"\"",
                    "    等待元素出现或可见",
                    "    ",
                    "    Args:",
                    "        page: 页面对象",
                    "        selector: 选择器",
                    "        selector_type: 选择器类型",
                    "        timeout: 超时时间（秒）",
                    "        visible: 是否等待元素可见",
                    "    ",
                    "    Returns:",
                    "        是否等待成功",
                    "    \"\"\"",
                    "    start_time = time.time()",
                    "    while time.time() - start_time < timeout:",
                    "        try:",
                    "            # 动态构建参数字典",
                    "            selector_dict = {selector_type: selector}",
                    "            element = page.ele(**selector_dict)",
                    "            if element:",
                    "                if not visible or element.is_displayed():",
                    "                    return True",
                    "            time.sleep(0.5)",
                    "        except Exception:",
                    "            time.sleep(0.5)",
                    "    return False",
                    ""
                ])
            
            # 检查是否需要元素提取函数
            if any(step.get("action_id") in ["EXTRACT_TEXT", "EXTRACT_ATTRIBUTE"] for step in steps):
                python_code.extend([
                    "def extract_data_from_elements(page, selector: str, selector_type: str = 'css', extract_type: str = 'text', attribute_name: str = '') -> List[str]:",
                    "    \"\"\"",
                    "    从元素中提取数据",
                    "    ",
                    "    Args:",
                    "        page: 页面对象",
                    "        selector: 选择器",
                    "        selector_type: 选择器类型",
                    "        extract_type: 提取类型，可选值: 'text', 'attribute'",
                    "        attribute_name: 属性名称，当extract_type为'attribute'时使用",
                    "    ",
                    "    Returns:",
                    "        提取的数据列表",
                    "    \"\"\"",
                    "    result = []",
                    "    try:",
                    "        # 动态构建参数字典",
                    "        selector_dict = {selector_type: selector}",
                    "        elements = page.eles(**selector_dict)",
                    "        for element in elements:",
                    "            if extract_type == 'text':",
                    "                result.append(element.text)",
                    "            elif extract_type == 'attribute' and attribute_name:",
                    "                result.append(element.attr(attribute_name))",
                    "    except Exception as e:",
                    "        logging.error(f'提取数据失败: {e}')",
                    "    return result",
                    ""
                ])
            
            # 主函数开始
            python_code.append("def main():")
            
            # 函数文档字符串
            if code_style in ["standard", "verbose"]:
                python_code.extend([
                    "    \"\"\"",
                    f"    执行 '{flow_name}' 自动化流程",
                    "    "
                ])
                
                if code_style == "verbose":
                    python_code.append("    流程包含以下步骤:")
                    for i, step in enumerate(steps):
                        action_id = step.get("action_id", "")
                        parameters = step.get("parameters", {})
                        step_name = parameters.get("__custom_step_name__", action_id)
                        python_code.append(f"    - 步骤 {i+1}: {step_name}")
                
                python_code.extend([
                    "    \"\"\"",
                    ""
                ])
            
            # 设置日志
            python_code.extend([
                "    # 设置日志",
                "    logging.basicConfig(",
                "        level=logging.INFO,",
                "        format='[%(asctime)s] [%(levelname)s] %(message)s',",
                "        datefmt='%Y-%m-%d %H:%M:%S'",
                "    )",
                "    logger = logging.getLogger(__name__)",
                "",
                f"    logger.info('开始执行流程: {flow_name}')",
                "",
                "    # 创建浏览器实例",
                "    try:",
                "        page = WebPage(timeout=20)",
                "        page.set.timeouts(10, 10, 10)",
                "    except Exception as e:",
                "        logger.error(f'浏览器初始化失败: {e}')",
                "        return False",
                "",
                "    # 执行流程步骤",
                "    try:",
            ])
            
            # 添加每个步骤的代码
            for i, step in enumerate(steps):
                action_id = step.get("action_id", "")
                parameters = step.get("parameters", {})
                
                # 生成步骤注释
                step_name = parameters.get("__custom_step_name__", action_id)
                python_code.append(f"        # 步骤 {i+1}: {step_name}")
                
                # 根据不同操作类型生成代码
                code_lines = ProjectManager._generate_step_code(action_id, parameters, i, code_style)
                python_code.extend([f"        {line}" for line in code_lines])
                python_code.append("")
            
            # 结束代码
            python_code.extend([
                "        # 关闭浏览器",
                "        page.quit()",
                "        logger.info('流程执行完成')",
                "        return True",
                "    except Exception as e:",
                "        logger.error(f'流程执行失败: {e}')",
                "        try:",
                "            page.quit()",
                "        except:",
                "            pass",
                "        return False",
                "",
                "if __name__ == '__main__':",
                "    success = main()",
                "    sys.exit(0 if success else 1)",
                ""
            ])
            
            # 写入文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write("\n".join(python_code))
            
            return True, f"流程已成功导出为Python脚本: {file_path}"
            
        except Exception as e:
            return False, f"导出Python脚本失败: {str(e)}"
    
    @staticmethod
    def _generate_step_code(action_id: str, parameters: Dict[str, Any], step_index: int, code_style: str = "standard") -> List[str]:
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
        
        elif action_id in ["IF_CONDITION", "ELSE_CONDITION", "END_IF_CONDITION"]:
            # 处理条件语句
            if action_id == "IF_CONDITION":
                condition_type = parameters.get("condition_type", "")
                if condition_type == "element_exists":
                    locator_strategy = parameters.get("if_locator_strategy", "css")
                    locator_value = parameters.get("if_locator_value", "")
                    code_lines.append(f"# 检查元素是否存在: {locator_strategy}='{locator_value}'")
                    code_lines.append(f"selector_dict = {{'{locator_strategy}': '{locator_value}', 'timeout': 0.5}}")
                    code_lines.append(f"if page.ele(**selector_dict):")
                elif condition_type == "element_visible":
                    locator_strategy = parameters.get("if_locator_strategy", "css")
                    locator_value = parameters.get("if_locator_value", "")
                    code_lines.append(f"# 检查元素是否可见: {locator_strategy}='{locator_value}'")
                    code_lines.append(f"selector_dict = {{'{locator_strategy}': '{locator_value}', 'timeout': 0.5}}")
                    code_lines.append(f"element = page.ele(**selector_dict)")
                    code_lines.append("if element and element.is_displayed():")
                else:
                    code_lines.append("# 条件判断")
                    code_lines.append("if True:  # 请根据实际条件修改")
            elif action_id == "ELSE_CONDITION":
                code_lines.append("else:")
            elif action_id == "END_IF_CONDITION":
                code_lines.append("# 条件判断结束")
        
        elif action_id in ["START_LOOP", "END_LOOP"]:
            # 处理循环
            if action_id == "START_LOOP":
                loop_count = parameters.get("loop_count", 1)
                code_lines.append(f"# 开始循环 {loop_count} 次")
                code_lines.append(f"for iteration in range({loop_count}):")
            elif action_id == "END_LOOP":
                code_lines.append("# 循环结束")
        
        elif action_id == "SET_VARIABLE":
            var_name = parameters.get("variable_name", "")
            var_value = parameters.get("variable_value", "")
            if isinstance(var_value, str):
                var_value = f'"{var_value}"'
            code_lines.append(f"# 设置变量 {var_name}")
            code_lines.append(f"{var_name} = {var_value}")
        
        elif action_id == "PAGE_REFRESH":
            if code_style == "verbose":
                code_lines.append("# 刷新页面")
            
            code_lines.append("page.refresh()")
            code_lines.append("logger.info(\"页面已刷新\")")
            
        elif action_id == "WAIT_FOR_ELEMENT" or action_id == "WAIT_FOR_ELEMENT_VISIBLE":
            locator_strategy = parameters.get("locator_strategy", "css")
            locator_value = parameters.get("locator_value", "")
            timeout = parameters.get("timeout", 10)
            visible = action_id == "WAIT_FOR_ELEMENT_VISIBLE"
            
            code_lines.append(f"# 等待元素{'可见' if visible else '存在'}: {locator_strategy}='{locator_value}'")
            code_lines.append(f"wait_success = wait_for_element(page, '{locator_value}', '{locator_strategy}', {timeout}, {str(visible).lower()})")
            code_lines.append(f"if wait_success:")
            code_lines.append(f"    logger.info(\"元素{'可见' if visible else '存在'}\")")
            code_lines.append(f"else:")
            code_lines.append(f"    logger.warning(\"等待元素{'可见' if visible else '存在'}超时\")")
            
        elif action_id == "EXTRACT_TEXT" or action_id == "EXTRACT_ATTRIBUTE":
            locator_strategy = parameters.get("locator_strategy", "css")
            locator_value = parameters.get("locator_value", "")
            variable_name = parameters.get("save_to_variable", "result_data")
            
            if action_id == "EXTRACT_TEXT":
                extract_type = "text"
                attribute_name = ""
                code_lines.append(f"# 提取元素文本: {locator_strategy}='{locator_value}'")
            else:
                extract_type = "attribute"
                attribute_name = parameters.get("attribute_name", "")
                code_lines.append(f"# 提取元素属性 {attribute_name}: {locator_strategy}='{locator_value}'")
                
            code_lines.append(f"{variable_name} = extract_data_from_elements(page, '{locator_value}', '{locator_strategy}', '{extract_type}', '{attribute_name}')")
            code_lines.append(f"logger.info(f\"提取的数据数量: {{len({variable_name})}}\")")
        
        else:
            # 默认代码
            code_lines.append(f"# 未实现的操作: {action_id}")
            code_lines.append("pass")
        
        return code_lines
