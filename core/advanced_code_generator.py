#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
高级代码生成器模块，提供增强的代码生成能力。
"""

import os
import time
from typing import Dict, List, Any, Tuple, Optional, Union

from .code_generator import CodeGenerator

class AdvancedCodeGenerator(CodeGenerator):
    """
    高级代码生成器，提供增强的代码生成功能
    """
    
    def __init__(self):
        """初始化高级代码生成器"""
        super().__init__()
        # 记录已经生成的辅助函数
        self._generated_helpers = set()
        # 代码风格配置
        self._style_config = {}
    
    def generate_code(self, flow_data: Dict[str, Any], 
                     output_path: Optional[str] = None,
                     code_style: str = "standard",
                     style_config: Optional[Dict[str, Any]] = None) -> Tuple[bool, Union[str, List[str]]]:
        """
        生成Python代码
        
        Args:
            flow_data: 流程数据
            output_path: 输出文件路径，如果为None则返回代码行列表
            code_style: 代码风格，可选值: "standard", "compact", "verbose", "production"
            style_config: 风格配置，用于自定义代码风格
            
        Returns:
            (成功标志, 文件路径或代码行列表)
        """
        # 重置辅助函数记录
        self._generated_helpers = set()
        
        # 设置代码风格配置
        self._style_config = style_config or {}
        
        # 调用父类方法生成代码
        return super().generate_code(flow_data, output_path, code_style)
    
    def export_to_package(self, flow_data: Dict[str, Any], 
                        output_dir: str,
                        include_readme: bool = True,
                        include_requirements: bool = True,
                        include_config: bool = True,
                        code_style: str = "production") -> Tuple[bool, str]:
        """
        将流程导出为完整Python包
        
        Args:
            flow_data: 流程数据
            output_dir: 输出目录
            include_readme: 是否包含README文件
            include_requirements: 是否包含requirements.txt
            include_config: 是否包含配置文件
            code_style: 代码风格
            
        Returns:
            (成功标志, 消息)
        """
        try:
            flow_name = flow_data.get("flow_name", "未命名流程")
            
            # 创建包目录
            package_name = "".join(c.lower() for c in flow_name if c.isalnum() or c == "_")
            if not package_name:
                package_name = "drission_auto"
            
            package_dir = os.path.join(output_dir, package_name)
            os.makedirs(package_dir, exist_ok=True)
            
            # 创建__init__.py
            with open(os.path.join(package_dir, "__init__.py"), "w", encoding="utf-8") as f:
                f.write('"""DrissionPage自动化包"""\n\n')
                f.write(f'__version__ = "0.1.0"\n')
                f.write(f'__author__ = "DrissionPage GUI Tool"\n')
            
            # 生成主代码文件
            main_code_path = os.path.join(package_dir, "main.py")
            success, result = self.generate_code(flow_data, main_code_path, code_style)
            
            if not success:
                return False, f"生成主代码失败: {result}"
            
            # 生成utils.py
            utils_code = self._generate_utils_module(flow_data)
            with open(os.path.join(package_dir, "utils.py"), "w", encoding="utf-8") as f:
                f.write("\n".join(utils_code))
            
            # 生成config.py
            if include_config:
                config_code = self._generate_config_module(flow_data)
                with open(os.path.join(package_dir, "config.py"), "w", encoding="utf-8") as f:
                    f.write("\n".join(config_code))
            
            # 生成README.md
            if include_readme:
                readme_content = self._generate_readme(flow_data)
                with open(os.path.join(package_dir, "README.md"), "w", encoding="utf-8") as f:
                    f.write(readme_content)
            
            # 生成requirements.txt
            if include_requirements:
                requirements = [
                    "DrissionPage>=4.0.0",
                    "pandas>=1.3.0",
                    "openpyxl>=3.0.0",
                    "requests>=2.25.0",
                    "Pillow>=8.0.0"
                ]
                with open(os.path.join(package_dir, "requirements.txt"), "w", encoding="utf-8") as f:
                    f.write("\n".join(requirements))
            
            # 创建启动脚本
            run_script = [
                "#!/usr/bin/env python3",
                "# -*- coding: utf-8 -*-",
                "",
                f"# 启动脚本 - {flow_name}",
                "",
                "from main import main",
                "",
                "if __name__ == '__main__':",
                "    main()"
            ]
            
            with open(os.path.join(package_dir, "run.py"), "w", encoding="utf-8") as f:
                f.write("\n".join(run_script))
            
            return True, f"已成功导出为Python包: {package_dir}"
            
        except Exception as e:
            return False, f"导出为Python包失败: {str(e)}"
    
    def _generate_utils_module(self, flow_data: Dict[str, Any]) -> List[str]:
        """
        生成工具模块代码
        
        Args:
            flow_data: 流程数据
            
        Returns:
            代码行列表
        """
        code_lines = [
            "#!/usr/bin/env python3",
            "# -*- coding: utf-8 -*-",
            "",
            '"""',
            "工具函数模块",
            '"""',
            "",
            "import os",
            "import time",
            "import logging",
            "import random",
            "import json",
            "import re",
            "from typing import Dict, List, Any, Tuple, Optional, Union",
            "",
            "from DrissionPage import WebPage, ChromiumPage",
            "",
            "logger = logging.getLogger(__name__)",
            ""
        ]
        
        # 添加等待元素函数
        code_lines.extend([
            "def wait_for_element(page, selector: str, selector_type: str = 'css', timeout: int = 10, visible: bool = False) -> bool:",
            '    """',
            "    等待元素出现或可见",
            "",
            "    Args:",
            "        page: 页面对象",
            "        selector: 选择器",
            "        selector_type: 选择器类型",
            "        timeout: 超时时间（秒）",
            "        visible: 是否等待元素可见",
            "",
            "    Returns:",
            "        是否等待成功",
            '    """',
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
        
        # 添加元素提取函数
        code_lines.extend([
            "def extract_data_from_elements(page, selector: str, selector_type: str = 'css', extract_type: str = 'text', attribute_name: str = '') -> List[str]:",
            '    """',
            "    从元素中提取数据",
            "",
            "    Args:",
            "        page: 页面对象",
            "        selector: 选择器",
            "        selector_type: 选择器类型",
            "        extract_type: 提取类型，可选值: 'text', 'attribute'",
            "        attribute_name: 属性名称，当extract_type为'attribute'时使用",
            "",
            "    Returns:",
            "        提取的数据列表",
            '    """',
            "    result = []",
            "    try:",
            "        # 根据选择器类型动态构建参数字典",
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
        
        # 添加截图函数
        code_lines.extend([
            "def take_screenshot(page, file_path: str, element_selector: Optional[Dict[str, str]] = None) -> bool:",
            '    """',
            "    对页面或元素进行截图",
            "",
            "    Args:",
            "        page: 页面对象",
            "        file_path: 截图保存路径",
            "        element_selector: 元素选择器，格式为 {strategy: value}，如果为None则截取整个页面",
            "",
            "    Returns:",
            "        是否截图成功",
            '    """',
            "    try:",
            "        # 确保目录存在",
            "        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)",
            "",
            "        # 进行截图",
            "        if element_selector:",
            "            # 获取元素",
            "            strategy = list(element_selector.keys())[0]",
            "            value = element_selector[strategy]",
            "            element = page.ele(**{strategy: value})",
            "            element.screenshot(path=file_path)",
            "        else:",
            "            # 对整个页面截图",
            "            page.get_screenshot(path=file_path)",
            "        return True",
            "    except Exception as e:",
            "        logging.error(f'截图失败: {e}')",
            "        return False",
            ""
        ])
        
        # 添加随机延迟函数
        code_lines.extend([
            "def random_delay(min_seconds: float = 1.0, max_seconds: float = 3.0) -> None:",
            '    """',
            "    随机延迟一段时间",
            "",
            "    Args:",
            "        min_seconds: 最小延迟时间（秒）",
            "        max_seconds: 最大延迟时间（秒）",
            '    """',
            "    delay_time = random.uniform(min_seconds, max_seconds)",
            "    time.sleep(delay_time)",
            ""
        ])
        
        return code_lines
    
    def _generate_config_module(self, flow_data: Dict[str, Any]) -> List[str]:
        """
        生成配置模块代码
        
        Args:
            flow_data: 流程数据
            
        Returns:
            代码行列表
        """
        # 从流程数据中提取配置信息
        flow_name = flow_data.get("flow_name", "未命名流程")
        steps = flow_data.get("steps", [])
        
        # 发现可配置项
        urls = []
        selectors = {}
        
        for step in steps:
            action_id = step.get("action_id", "")
            parameters = step.get("parameters", {})
            
            # 收集URL
            if action_id == "PAGE_GET":
                url = parameters.get("url", "")
                if url and url not in urls:
                    urls.append(url)
            
            # 收集选择器
            if action_id in ["ELEMENT_CLICK", "ELEMENT_INPUT", "WAIT_FOR_ELEMENT"]:
                locator_strategy = parameters.get("locator_strategy", "css")
                locator_value = parameters.get("locator_value", "")
                
                if locator_value:
                    step_name = parameters.get("__custom_step_name__", action_id)
                    selectors[f"{step_name}_{locator_strategy}"] = locator_value
        
        code_lines = [
            "#!/usr/bin/env python3",
            "# -*- coding: utf-8 -*-",
            "",
            '"""',
            "配置模块",
            '"""',
            "",
            "import os",
            "import json",
            "from typing import Dict, Any",
            "",
            "# 基础配置",
            f"APP_NAME = \"{flow_name}\"",
            "VERSION = \"0.1.0\"",
            "",
            "# 超时配置",
            "DEFAULT_TIMEOUT = 30",
            "RETRY_TIMES = 3",
            "",
            "# 浏览器配置",
            "BROWSER_HEADLESS = False",
            "BROWSER_EXECUTABLE_PATH = \"\"  # 留空使用默认路径",
            ""
        ]
        
        # 添加URL配置
        if urls:
            code_lines.append("# URL配置")
            for i, url in enumerate(urls):
                var_name = f"URL_{i+1}" if i > 0 else "BASE_URL"
                code_lines.append(f"{var_name} = \"{url}\"")
            code_lines.append("")
        
        # 添加选择器配置
        if selectors:
            code_lines.append("# 选择器配置")
            code_lines.append("SELECTORS = {")
            for name, value in selectors.items():
                code_lines.append(f"    \"{name}\": \"{value}\",")
            code_lines.append("}")
            code_lines.append("")
        
        # 添加配置加载函数
        code_lines.extend([
            "def load_config(config_file: str = None) -> Dict[str, Any]:",
            '    """',
            "    加载配置文件",
            "",
            "    Args:",
            "        config_file: 配置文件路径，如果为None则使用默认配置",
            "",
            "    Returns:",
            "        配置字典",
            '    """',
            "    config = {",
            "        \"app_name\": APP_NAME,",
            "        \"version\": VERSION,",
            "        \"timeout\": DEFAULT_TIMEOUT,",
            "        \"retry_times\": RETRY_TIMES,",
            "        \"browser\": {",
            "            \"headless\": BROWSER_HEADLESS,",
            "            \"executable_path\": BROWSER_EXECUTABLE_PATH",
            "        }",
            "    }",
            "",
            "    # 加载URL配置",
            "    config[\"urls\"] = {}"
        ])
        
        # 添加URL配置加载
        if urls:
            for i, url in enumerate(urls):
                var_name = f"URL_{i+1}" if i > 0 else "BASE_URL"
                code_lines.append(f"    config[\"urls\"][\"{var_name.lower()}\"] = {var_name}")
        
        # 添加选择器配置加载
        if selectors:
            code_lines.append("    # 加载选择器配置")
            code_lines.append("    config[\"selectors\"] = SELECTORS")
        
        # 添加外部配置文件加载
        code_lines.extend([
            "",
            "    # 如果指定了配置文件，加载它",
            "    if config_file and os.path.exists(config_file):",
            "        try:",
            "            with open(config_file, 'r', encoding='utf-8') as f:",
            "                file_config = json.load(f)",
            "            # 更新配置",
            "            for key, value in file_config.items():",
            "                if isinstance(value, dict) and key in config and isinstance(config[key], dict):",
            "                    # 合并字典",
            "                    config[key].update(value)",
            "                else:",
            "                    # 直接替换",
            "                    config[key] = value",
            "        except Exception as e:",
            "            print(f\"配置文件加载失败: {e}\")",
            "",
            "    return config"
        ])
        
        return code_lines
    
    def _generate_readme(self, flow_data: Dict[str, Any]) -> str:
        """
        生成README文件内容
        
        Args:
            flow_data: 流程数据
            
        Returns:
            README文件内容
        """
        flow_name = flow_data.get("flow_name", "未命名流程")
        description = flow_data.get("description", "")
        
        readme = f"""# {flow_name}

此项目由DrissionPage自动化GUI工具生成，用于执行自动化Web任务。

## 项目描述

{description if description else "自动化Web任务"}

## 功能特点

- 基于DrissionPage框架实现Web自动化
- 包含完整的错误处理和日志记录
- 支持自定义配置

## 安装

1. 克隆或下载此仓库
2. 安装依赖：`pip install -r requirements.txt`

## 使用方法

直接运行主程序：

```bash
python run.py
```

## 配置

修改`config.py`文件以自定义配置。

## 注意事项

- 确保已安装Chrome或Edge浏览器
- 在首次运行前安装所有依赖

## 依赖

- DrissionPage>=4.0.0
- pandas>=1.3.0
- openpyxl>=3.0.0
- requests>=2.25.0
- Pillow>=8.0.0

## 联系方式

如有问题，请联系项目作者。

## 许可

MIT License
"""
        
        return readme
    
    def _override_step_code(self, action_id: str, parameters: Dict[str, Any], 
                          step_index: int, code_style: str) -> List[str]:
        """
        重写步骤代码生成方法，支持更多操作类型
        
        Args:
            action_id: 动作ID
            parameters: 动作参数
            step_index: 步骤索引
            code_style: 代码风格
            
        Returns:
            代码行列表
        """
        # 先尝试使用父类方法
        parent_code = super()._generate_step_code(action_id, parameters, step_index, code_style)
        
        # 如果父类能处理，或者是不支持的操作，直接返回
        if action_id in ["PAGE_GET", "ELEMENT_CLICK", "ELEMENT_INPUT", "WAIT", "LOG_MESSAGE"]:
            return parent_code
        
        # 根据不同操作类型生成代码
        code_lines = []
        
        if action_id == "EXTRACT_TEXT":
            locator_strategy = parameters.get("locator_strategy", "css")
            locator_value = parameters.get("locator_value", "")
            variable_name = parameters.get("variable_name", f"extracted_text_{step_index}")
            
            # 导入extract_data_from_elements函数
            self._generated_helpers.add("extract_data_from_elements")
            
            if code_style == "verbose":
                code_lines.append(f"# 提取元素文本: {locator_strategy}='{locator_value}'")
            
            code_lines.append(f"{variable_name} = extract_data_from_elements(page, '{locator_value}', '{locator_strategy}', 'text')")
            code_lines.append(f"logger.info(f\"已提取文本到变量 {variable_name}: {{len({variable_name})}} 个结果\")")
        
        elif action_id == "EXTRACT_ATTRIBUTE":
            locator_strategy = parameters.get("locator_strategy", "css")
            locator_value = parameters.get("locator_value", "")
            attribute_name = parameters.get("attribute_name", "")
            variable_name = parameters.get("variable_name", f"extracted_attr_{step_index}")
            
            # 导入extract_data_from_elements函数
            self._generated_helpers.add("extract_data_from_elements")
            
            if code_style == "verbose":
                code_lines.append(f"# 提取元素属性 '{attribute_name}': {locator_strategy}='{locator_value}'")
            
            code_lines.append(f"{variable_name} = extract_data_from_elements(page, '{locator_value}', '{locator_strategy}', 'attribute', '{attribute_name}')")
            code_lines.append(f"logger.info(f\"已提取属性到变量 {variable_name}: {{len({variable_name})}} 个结果\")")
        
        elif action_id == "TAKE_SCREENSHOT":
            screenshot_path = parameters.get("screenshot_path", f"screenshot_{step_index}.png")
            element_only = parameters.get("element_only", False)
            
            if element_only:
                locator_strategy = parameters.get("locator_strategy", "css")
                locator_value = parameters.get("locator_value", "")
                
                if code_style == "verbose":
                    code_lines.append(f"# 对元素截图: {locator_strategy}='{locator_value}'")
                
                code_lines.append(f"# 动态构建选择器参数")
                code_lines.append(f"selector_dict = {{'{locator_strategy}': '{locator_value}'}}")
                code_lines.append(f"element = page.ele(**selector_dict)")
                code_lines.append(f"element.screenshot(path='{screenshot_path}')")
            else:
                if code_style == "verbose":
                    code_lines.append("# 对页面截图")
                
                code_lines.append(f"page.get_screenshot(path='{screenshot_path}')")
            
            code_lines.append(f"logger.info(f\"截图已保存到: {screenshot_path}\")")
        
        elif action_id == "EXECUTE_JAVASCRIPT":
            js_code = parameters.get("js_code", "")
            variable_name = parameters.get("save_to_variable", "")
            
            if code_style == "verbose":
                code_lines.append("# 执行JavaScript代码")
                code_lines.append(f"# 代码: {js_code}")
            
            if variable_name:
                code_lines.append(f"{variable_name} = page.run_js(\"\"\"{js_code}\"\"\")")
                code_lines.append(f"logger.info(f\"JavaScript执行结果已保存到变量: {variable_name}\")")
            else:
                code_lines.append(f"page.run_js(\"\"\"{js_code}\"\"\")")
        
        elif action_id == "RANDOM_DELAY":
            min_seconds = parameters.get("min_seconds", 1)
            max_seconds = parameters.get("max_seconds", 3)
            
            # 使用工具函数
            self._generated_helpers.add("random_delay")
            
            if code_style == "verbose":
                code_lines.append(f"# 随机延迟 {min_seconds}-{max_seconds} 秒")
            
            code_lines.append(f"random_delay({min_seconds}, {max_seconds})")
        
        else:
            # 未实现的操作，使用通用代码
            code_lines.append(f"# 未实现的操作: {action_id}")
            code_lines.append("pass")
        
        return code_lines
    
    def _generate_utility_functions(self, flow_data: Dict[str, Any], code_style: str) -> None:
        """
        根据步骤需要生成工具函数
        
        Args:
            flow_data: 流程数据
            code_style: 代码风格
        """
        # 如果是生产环境代码风格，不在主文件中生成工具函数
        if code_style == "production":
            self._add_line("# 工具函数在utils.py模块中")
            self._add_line("from utils import wait_for_element, extract_data_from_elements, take_screenshot, random_delay")
            self._add_line()
            return
        
        # 调用父类方法
        super()._generate_utility_functions(flow_data, code_style) 