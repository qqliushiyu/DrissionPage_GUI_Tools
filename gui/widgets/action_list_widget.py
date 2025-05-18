# Widget to display list of available actions 
from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem
from PyQt5.QtCore import pyqtSignal, Qt
from typing import List, Dict, Any

# 动作定义（基础版）
ACTION_DEFINITIONS = {
    "PAGE_NAV": {
        "display_text": "页面导航",
        "actions": {
            "PAGE_GET": {
                "display_text": "打开URL",
                "parameter_schema": [
                    {"name": "url", "label": "目标网址:", "type": "string", "default_value": "http://"},
                    {"name": "timeout", "label": "超时(秒):", "type": "int", "default_value": 30, "tooltip": "页面加载超时时间"}
                ]
            },
            "PAGE_REFRESH": {
                "display_text": "刷新页面",
                "parameter_schema": []
            },
            "GET_PAGE_INFO": {
                "display_text": "获取网页信息",
                "parameter_schema": [
                    {"name": "save_to_variable", "label": "保存到变量:", "type": "string", "default_value": "page_info", "tooltip": "将页面信息保存到此变量名"}
                ]
            },
            "OPEN_BROWSER": {
                "display_text": "打开浏览器",
                "parameter_schema": [
                    {"name": "url", "label": "初始网址:", "type": "string", "default_value": "https://www.baidu.com"},
                    {"name": "browser_type", "label": "浏览器类型:", "type": "dropdown", "options": ["Chrome", "Edge", "Firefox"], "default_value": "Chrome"},
                    {"name": "headless", "label": "无头模式:", "type": "dropdown", "options": ["是", "否"], "default_value": "否", "tooltip": "无头模式下浏览器窗口不可见，适合服务器运行"},
                    {"name": "window_size", "label": "窗口尺寸:", "type": "string", "default_value": "1280,720", "tooltip": "格式：宽,高 (例如：1280,720)"},
                    {"name": "user_agent", "label": "用户代理(UA):", "type": "string", "tooltip": "自定义浏览器的User-Agent"},
                    {"name": "proxy", "label": "代理服务器:", "type": "string", "tooltip": "格式：协议://地址:端口 (例如：http://127.0.0.1:8080)"},
                    {"name": "incognito", "label": "隐私模式:", "type": "dropdown", "options": ["是", "否"], "default_value": "否", "tooltip": "隐私模式不保存浏览记录和Cookie"},
                    {"name": "load_extension", "label": "扩展程序路径:", "type": "string", "tooltip": "加载扩展程序的本地路径，多个路径用逗号分隔"},
                    {"name": "custom_args", "label": "自定义参数:", "type": "string", "tooltip": "自定义浏览器启动参数，多个参数用逗号分隔"}
                ]
            },
            "CLOSE_BROWSER": {
                "display_text": "关闭浏览器",
                "parameter_schema": []
            }
        }
    },
    "ELEMENT_ACTIONS": {
        "display_text": "元素操作",
        "actions": {
            "ELEMENT_CLICK": {
                "display_text": "点击元素",
                "parameter_schema": [
                    {
                        "name": "locator_strategy",
                        "label": "定位方式:",
                        "type": "dropdown",
                        "options": [
                            "id", "name", "class", "tag",
                            "text", "css", "xpath"
                        ],
                        "default_value": "css",
                        "tooltip": "选择查找元素的方法"
                    },
                    {
                        "name": "locator_value",
                        "label": "定位符值:",
                        "type": "string",
                        "tooltip": "根据所选定位方式填写对应的值（例如：ID值, name属性值, CSS选择器表达式, XPath表达式等）"
                    },
                    {"name": "timeout", "label": "元素等待(秒):", "type": "int", "default_value": 10, "tooltip": "等待元素出现或可交互的最大时间"}
                ]
            },
            "ELEMENT_INPUT": {
                "display_text": "输入文本",
                "parameter_schema": [
                    {
                        "name": "locator_strategy",
                        "label": "定位方式:",
                        "type": "dropdown",
                        "options": [
                            "id", "name", "class", "tag",
                            "text", "css", "xpath"
                        ],
                        "default_value": "css",
                        "tooltip": "选择查找输入框的方法"
                    },
                    {
                        "name": "locator_value",
                        "label": "定位符值:",
                        "type": "string",
                        "tooltip": "根据所选定位方式填写对应的值"
                    },
                    {
                        "name": "text_to_input",
                        "label": "输入内容:",
                        "type": "string",
                        "tooltip": "要输入到元素中的文本"
                    },
                    {"name": "timeout", "label": "元素等待(秒):", "type": "int", "default_value": 10, "tooltip": "等待元素出现或可交互的最大时间"}
                ]
            },
            "CLICK_ELEMENT": {
                "display_text": "点击元素(新版)",
                "parameter_schema": [
                    {
                        "name": "locator_strategy",
                        "label": "定位方式:",
                        "type": "dropdown",
                        "options": [
                            "id", "name", "class", "tag",
                            "text", "css", "xpath"
                        ],
                        "default_value": "css",
                        "tooltip": "选择查找元素的方法"
                    },
                    {
                        "name": "locator_value",
                        "label": "定位符值:",
                        "type": "string",
                        "tooltip": "根据所选定位方式填写对应的值"
                    }
                ]
            },
            "INPUT_TEXT": {
                "display_text": "输入文本(新版)",
                "parameter_schema": [
                    {
                        "name": "locator_strategy",
                        "label": "定位方式:",
                        "type": "dropdown",
                        "options": [
                            "id", "name", "class", "tag",
                            "text", "css", "xpath"
                        ],
                        "default_value": "css",
                        "tooltip": "选择查找元素的方法"
                    },
                    {
                        "name": "locator_value",
                        "label": "定位符值:",
                        "type": "string",
                        "tooltip": "根据所选定位方式填写对应的值"
                    },
                    {
                        "name": "text",
                        "label": "输入内容:",
                        "type": "string",
                        "tooltip": "要输入到元素中的文本"
                    }
                ]
            },
            "WAIT_FOR_ELEMENT": {
                "display_text": "等待元素",
                "parameter_schema": [
                    {
                        "name": "locator_strategy",
                        "label": "定位方式:",
                        "type": "dropdown",
                        "options": [
                            "id", "name", "class", "tag",
                            "text", "css", "xpath"
                        ],
                        "default_value": "css",
                        "tooltip": "选择查找元素的方法"
                    },
                    {
                        "name": "locator_value",
                        "label": "定位符值:",
                        "type": "string",
                        "tooltip": "根据所选定位方式填写对应的值"
                    },
                    {
                        "name": "timeout",
                        "label": "超时(秒):",
                        "type": "int",
                        "default_value": 10,
                        "tooltip": "等待元素出现的最大时间"
                    }
                ]
            },
            "DELETE_ELEMENT": {
                "display_text": "删除元素",
                "parameter_schema": [
                    {
                        "name": "locator_strategy",
                        "label": "定位方式:",
                        "type": "dropdown",
                        "options": [
                            "id", "name", "class", "tag",
                            "text", "css", "xpath"
                        ],
                        "default_value": "css",
                        "tooltip": "选择查找要删除元素的方法"
                    },
                    {
                        "name": "locator_value",
                        "label": "定位符值:",
                        "type": "string",
                        "tooltip": "根据所选定位方式填写对应的值"
                    },
                    {
                        "name": "timeout",
                        "label": "超时(秒):",
                        "type": "int",
                        "default_value": 5,
                        "tooltip": "等待元素出现的最大时间"
                    }
                ]
            },
            "GET_ELEMENT_INFO": {
                "display_text": "获取元素信息",
                "parameter_schema": [
                    {
                        "name": "locator_strategy",
                        "label": "定位方式:",
                        "type": "dropdown",
                        "options": [
                            "id", "name", "class", "tag",
                            "text", "css", "xpath"
                        ],
                        "default_value": "css",
                        "tooltip": "选择查找元素的方法"
                    },
                    {
                        "name": "locator_value",
                        "label": "定位符值:",
                        "type": "string",
                        "tooltip": "根据所选定位方式填写对应的值"
                    },
                    {"name": "save_to_variable", "label": "保存到变量:", "type": "string", "default_value": "element_info", "tooltip": "将元素信息保存到此变量名"}
                ]
            }
        }
    },
    "CONTROL_FLOW": {
        "display_text": "流程控制",
        "actions": {
            "IF_CONDITION": {
                "display_text": "如果 (条件)",
                "parameter_schema": [
                    {
                        "name": "condition_type", 
                        "label": "条件类型:", 
                        "type": "dropdown", 
                        "options": ["element_exists", "element_not_exists", "element_visible", "element_not_visible"], 
                        "default_value": "element_exists",
                        "tooltip": "选择条件判断的类型"
                    },
                    {
                        "name": "if_locator_strategy",
                        "label": "定位方式:",
                        "type": "dropdown",
                        "options": [
                            "id", "name", "class", "tag",
                            "text", "css", "xpath"
                        ],
                        "default_value": "css",
                        "tooltip": "选择查找元素的方法"
                    },
                    {
                        "name": "if_locator_value",
                        "label": "定位符值:",
                        "type": "string",
                        "tooltip": "根据所选定位方式填写对应的值"
                    },
                    {
                        "name": "if_timeout",
                        "label": "元素等待(秒):",
                        "type": "int",
                        "default_value": 3,
                        "tooltip": "检查元素是否存在的等待时间，通常较短"
                    }
                ]
            },
            "ELSE_CONDITION": {
                "display_text": "否则",
                "parameter_schema": []  # 无参数
            },
            "END_IF_CONDITION": {
                "display_text": "结束如果",
                "parameter_schema": []  # 无参数
            },
            "START_LOOP": {
                "display_text": "开始循环 (重复N次)",
                "parameter_schema": [
                    {
                        "name": "loop_count",
                        "label": "循环次数:",
                        "type": "int",
                        "default_value": 3,
                        "tooltip": "指定重复执行循环体的次数"
                    }
                ]
            },
            "START_INFINITE_LOOP": {
                "display_text": "开始无限循环",
                "parameter_schema": [],  # 无参数
                "tooltip": "开始一个会持续执行的循环，直到遇到对应的'结束无限循环'或流程被手动停止"
            },
            "END_LOOP": {
                "display_text": "结束循环",
                "parameter_schema": []  # 无参数
            },
            "FOREACH_LOOP": {
                "display_text": "遍历循环",
                "parameter_schema": [
                    {
                        "name": "collection_variable",
                        "label": "集合变量名:",
                        "type": "string",
                        "tooltip": "包含要遍历的集合的变量名称"
                    },
                    {
                        "name": "item_variable",
                        "label": "元素变量名:",
                        "type": "string",
                        "default_value": "item",
                        "tooltip": "存储当前元素的变量名"
                    },
                    {
                        "name": "index_variable",
                        "label": "索引变量名(可选):",
                        "type": "string",
                        "default_value": "index",
                        "tooltip": "存储当前索引的变量名"
                    }
                ]
            },
            "END_FOREACH_LOOP": {
                "display_text": "结束遍历循环",
                "parameter_schema": []  # 无参数
            },
            "TRY_BLOCK": {
                "display_text": "开始try块",
                "parameter_schema": []  # 无参数
            },
            "CATCH_BLOCK": {
                "display_text": "开始catch块",
                "parameter_schema": []  # 无参数
            },
            "FINALLY_BLOCK": {
                "display_text": "开始finally块",
                "parameter_schema": []  # 无参数
            },
            "END_TRY_BLOCK": {
                "display_text": "结束try块",
                "parameter_schema": []  # 无参数
            }
        }
    },
    "UTILITY": {
        "display_text": "辅助功能",
        "actions": {
            "LOG_MESSAGE": {
                "display_text": "记录日志",
                "parameter_schema": [
                    {
                        "name": "message",
                        "label": "日志消息:",
                        "type": "string",
                        "tooltip": "要记录的消息内容，可以包含变量引用"
                    },
                    {
                        "name": "level",
                        "label": "日志级别:",
                        "type": "dropdown",
                        "options": ["INFO", "WARNING", "ERROR", "SUCCESS", "DEBUG"],
                        "default_value": "INFO",
                        "tooltip": "日志消息的重要程度"
                    }
                ]
            },
            "SET_VARIABLE": {
                "display_text": "设置变量",
                "parameter_schema": [
                    {
                        "name": "variable_name",
                        "label": "变量名:",
                        "type": "string",
                        "tooltip": "要设置的变量名称"
                    },
                    {
                        "name": "variable_value",
                        "label": "变量值:",
                        "type": "string",
                        "tooltip": "变量的值，可以是表达式或变量引用"
                    },
                    {
                        "name": "variable_scope",
                        "label": "变量作用域:",
                        "type": "dropdown",
                        "options": ["global", "local", "temp"],
                        "default_value": "global",
                        "tooltip": "变量的作用域：global(全局), local(局部), temp(临时)"
                    }
                ]
            },
            "DELETE_VARIABLE": {
                "display_text": "删除变量",
                "parameter_schema": [
                    {
                        "name": "variable_name",
                        "label": "变量名:",
                        "type": "string",
                        "tooltip": "要删除的变量名称"
                    },
                    {
                        "name": "variable_scope",
                        "label": "变量作用域:",
                        "type": "dropdown",
                        "options": ["global", "local", "temp", "all"],
                        "default_value": "all",
                        "tooltip": "变量的作用域：global(全局), local(局部), temp(临时), all(所有作用域)"
                    }
                ]
            },
            "DELETE_FLOW": {
                "display_text": "删除流程",
                "parameter_schema": [
                    {
                        "name": "confirm",
                        "label": "确认删除:",
                        "type": "dropdown",
                        "options": ["是", "否"],
                        "default_value": "否",
                        "tooltip": "请确认是否要删除当前流程"
                    },
                    {
                        "name": "clear_variables",
                        "label": "同时清除变量:",
                        "type": "dropdown",
                        "options": ["是", "否"],
                        "default_value": "否",
                        "tooltip": "是否同时清除所有变量"
                    }
                ]
            },
            "GET_CONSOLE_LOGS": {
                "display_text": "获取控制台日志",
                "parameter_schema": [
                    {
                        "name": "mode",
                        "label": "获取模式:",
                        "type": "dropdown",
                        "options": ["wait", "all", "start", "stop"],
                        "default_value": "wait",
                        "tooltip": "控制台日志获取模式: wait(等待一条), all(获取所有), start(开始监听), stop(停止监听)"
                    },
                    {
                        "name": "timeout",
                        "label": "超时时间(秒):",
                        "type": "string",
                        "default_value": "10",
                        "tooltip": "等待控制台日志的最大时间，仅在wait模式下有效，留空表示无限等待"
                    },
                    {
                        "name": "save_to_variable",
                        "label": "保存到变量:",
                        "type": "string",
                        "default_value": "console_logs",
                        "tooltip": "将控制台日志保存到此变量名"
                    }
                ]
            },
            "CLEAR_CONSOLE": {
                "display_text": "清空控制台缓存",
                "parameter_schema": []
            }
        }
    },
    "ADVANCED_INTERACTIONS": {
        "display_text": "高级交互",
        "actions": {
            "TAKE_SCREENSHOT": {
                "display_text": "截图",
                "parameter_schema": [
                    {"name": "save_path", "label": "保存路径:", "type": "string", "default_value": "screenshots/screenshot.png", "tooltip": "截图保存的文件路径，如果目录不存在会自动创建"},
                    {"name": "save_full_page", "label": "全页面截图:", "type": "dropdown", "options": ["是", "否"], "default_value": "否", "tooltip": "是否截取整个页面，而不只是可视区域"},
                    {"name": "locator_strategy", "label": "元素定位方式(可选):", "type": "dropdown", "options": ["", "ID", "NAME", "CLASS_NAME", "TAG_NAME", "CSS_SELECTOR", "XPATH"], "default_value": "", "tooltip": "如需只截取特定元素，选择元素定位方式，留空则截取页面"},
                    {"name": "locator_value", "label": "元素定位值(可选):", "type": "string", "tooltip": "元素定位值，仅当定位方式不为空时需要"}
                ]
            },
            "SCROLL_PAGE": {
                "display_text": "滚动页面",
                "parameter_schema": [
                    {"name": "direction", "label": "滚动方向:", "type": "dropdown", "options": ["down", "up", "left", "right"], "default_value": "down", "tooltip": "页面滚动的方向"},
                    {"name": "distance", "label": "滚动距离(像素):", "type": "int", "default_value": 500, "tooltip": "滚动的像素距离"}
                ]
            },
            "DRAG_AND_DROP": {
                "display_text": "拖放元素",
                "parameter_schema": [
                    {"name": "source_locator_strategy", "label": "源元素定位方式:", "type": "dropdown", "options": ["id", "name", "class", "tag", "text", "css", "xpath"], "default_value": "css", "tooltip": "源元素的定位方式"},
                    {"name": "source_locator_value", "label": "源元素定位值:", "type": "string", "tooltip": "源元素的定位值"},
                    {"name": "target_locator_strategy", "label": "目标元素定位方式:", "type": "dropdown", "options": ["id", "name", "class", "tag", "text", "css", "xpath"], "default_value": "css", "tooltip": "目标元素的定位方式"},
                    {"name": "target_locator_value", "label": "目标元素定位值:", "type": "string", "tooltip": "目标元素的定位值"},
                    {"name": "smooth", "label": "平滑拖放:", "type": "dropdown", "options": ["是", "否"], "default_value": "是", "tooltip": "是否使用平滑拖放效果"},
                    {"name": "speed", "label": "拖放速度:", "type": "dropdown", "options": ["slow", "medium", "fast"], "default_value": "medium", "tooltip": "拖放动作的速度"}
                ]
            },
            "MOUSE_HOVER": {
                "display_text": "鼠标悬停",
                "parameter_schema": [
                    {"name": "locator_strategy", "label": "定位策略:", "type": "dropdown", "options": ["id", "name", "class", "tag", "text", "css", "xpath"], "default_value": "css"},
                    {"name": "locator_value", "label": "定位值:", "type": "string", "default_value": ""},
                    {"name": "duration", "label": "持续时间(秒):", "type": "float", "default_value": 1.0},
                    {"name": "timeout", "label": "超时(秒):", "type": "int", "default_value": 10}
                ]
            },
            "MOUSE_DRAG_DROP": {
                "display_text": "拖放操作",
                "parameter_schema": [
                    {"name": "source_locator_strategy", "label": "源元素定位策略:", "type": "dropdown", "options": ["id", "name", "class", "tag", "text", "css", "xpath"], "default_value": "css"},
                    {"name": "source_locator_value", "label": "源元素定位值:", "type": "string", "default_value": ""},
                    {"name": "target_locator_strategy", "label": "目标元素定位策略:", "type": "dropdown", "options": ["id", "name", "class", "tag", "text", "css", "xpath"], "default_value": "css"},
                    {"name": "target_locator_value", "label": "目标元素定位值:", "type": "string", "default_value": ""},
                    {"name": "smooth", "label": "平滑拖动:", "type": "dropdown", "options": ["是", "否"], "default_value": "是"},
                    {"name": "duration", "label": "拖动时间(秒):", "type": "float", "default_value": 0.5},
                    {"name": "timeout", "label": "超时(秒):", "type": "int", "default_value": 10}
                ]
            },
            "MOUSE_DOUBLE_CLICK": {
                "display_text": "双击操作",
                "parameter_schema": [
                    {"name": "locator_strategy", "label": "定位策略:", "type": "dropdown", "options": ["id", "name", "class", "tag", "text", "css", "xpath"], "default_value": "css"},
                    {"name": "locator_value", "label": "定位值:", "type": "string", "default_value": ""},
                    {"name": "timeout", "label": "超时(秒):", "type": "int", "default_value": 10}
                ]
            },
            "MOUSE_RIGHT_CLICK": {
                "display_text": "右键点击",
                "parameter_schema": [
                    {"name": "locator_strategy", "label": "定位策略:", "type": "dropdown", "options": ["id", "name", "class", "tag", "text", "css", "xpath"], "default_value": "css"},
                    {"name": "locator_value", "label": "定位值:", "type": "string", "default_value": ""},
                    {"name": "timeout", "label": "超时(秒):", "type": "int", "default_value": 10}
                ]
            },
            "MOUSE_MOVE_PATH": {
                "display_text": "鼠标轨迹移动",
                "parameter_schema": [
                    {"name": "path_points", "label": "路径点坐标:", "type": "string", "default_value": "0,0;100,100;200,50", "tooltip": "格式: x1,y1;x2,y2;x3,y3..."},
                    {"name": "duration", "label": "移动时间(秒):", "type": "float", "default_value": 1.0},
                    {"name": "relative_to_element", "label": "相对于元素:", "type": "dropdown", "options": ["是", "否"], "default_value": "否"},
                    {"name": "locator_strategy", "label": "元素定位策略:", "type": "dropdown", "options": ["id", "name", "class", "tag", "text", "css", "xpath"], "default_value": "css"},
                    {"name": "locator_value", "label": "元素定位值:", "type": "string", "default_value": ""},
                    {"name": "timeout", "label": "超时(秒):", "type": "int", "default_value": 10}
                ]
            },
            "CLICK_CONTEXT_MENU": {
                "display_text": "点击上下文菜单项",
                "parameter_schema": [
                    {"name": "context_menu_item", "label": "菜单项:", "type": "string", "default_value": ""},
                    {"name": "use_text_match", "label": "使用文本匹配:", "type": "dropdown", "options": ["是", "否"], "default_value": "是"},
                    {"name": "timeout", "label": "超时(秒):", "type": "int", "default_value": 5}
                ]
            },
            "UPLOAD_FILE": {
                "display_text": "上传文件",
                "parameter_schema": [
                    {"name": "locator_strategy", "label": "文件输入框定位方式:", "type": "dropdown", "options": ["id", "name", "class", "tag", "text", "css", "xpath"], "default_value": "css", "tooltip": "文件输入框的定位方式"},
                    {"name": "locator_value", "label": "文件输入框定位值:", "type": "string", "tooltip": "文件输入框的定位值"},
                    {"name": "file_path", "label": "文件路径:", "type": "string", "tooltip": "要上传的文件的完整路径"}
                ]
            },
            "SWITCH_TO_IFRAME": {
                "display_text": "切换到iframe",
                "parameter_schema": [
                    {"name": "locator_strategy", "label": "iframe定位方式:", "type": "dropdown", "options": ["id", "name", "class", "tag", "text", "css", "xpath"], "default_value": "css", "tooltip": "iframe的定位方式"},
                    {"name": "locator_value", "label": "iframe定位值:", "type": "string", "tooltip": "iframe的定位值"}
                ]
            },
            "SWITCH_TO_PARENT_FRAME": {
                "display_text": "切换到父级框架",
                "parameter_schema": []
            },
            "SWITCH_TO_DEFAULT_CONTENT": {
                "display_text": "切换到主文档",
                "parameter_schema": []
            },
            "MANAGE_COOKIES": {
                "display_text": "管理Cookie",
                "parameter_schema": [
                    {"name": "action", "label": "操作类型:", "type": "dropdown", "options": ["get_all", "get", "set", "delete", "delete_all"], "default_value": "get_all", "tooltip": "要执行的Cookie操作类型"},
                    {"name": "cookie_name", "label": "Cookie名称(可选):", "type": "string", "tooltip": "要获取或删除的Cookie名称，仅当操作类型为get或delete时需要"},
                    {"name": "cookie_data", "label": "Cookie数据(可选):", "type": "string", "tooltip": "要设置的Cookie数据，格式为JSON字符串，仅当操作类型为set时需要"}
                ]
            }
        }
    },
    "CUSTOM_CODE": {
        "display_text": "自定义代码",
        "actions": {
            "EXECUTE_JAVASCRIPT": {
                "display_text": "执行JavaScript",
                "parameter_schema": [
                    {
                        "name": "js_code",
                        "label": "JavaScript代码:",
                        "type": "multiline",
                        "default_value": "",
                        "tooltip": "要执行的JavaScript代码，可以使用return返回结果"
                    },
                    {
                        "name": "return_variable",
                        "label": "返回值变量名:",
                        "type": "string",
                        "tooltip": "如果需要将JavaScript执行结果保存到变量中，请填写变量名"
                    }
                ]
            },
            "EXECUTE_JS_WITH_CONSOLE": {
                "display_text": "执行JS并记录控制台输出",
                "parameter_schema": [
                    {
                        "name": "js_code",
                        "label": "JavaScript代码:",
                        "type": "multiline",
                        "default_value": "console.log('测试输出');",
                        "tooltip": "要执行的JavaScript代码，通常包含console.log()"
                    },
                    {
                        "name": "wait_timeout",
                        "label": "等待控制台超时(秒):",
                        "type": "string",
                        "default_value": "5",
                        "tooltip": "等待控制台输出的最大时间，留空表示无限等待"
                    },
                    {
                        "name": "save_to_variable",
                        "label": "保存日志到变量名:",
                        "type": "string",
                        "default_value": "console_output",
                        "tooltip": "将控制台输出保存到此变量名"
                    }
                ]
            }
        }
    },
    "WAIT_ACTIONS": {
        "display_text": "等待操作",
        "actions": {
            "WAIT_SECONDS": {
                "display_text": "等待时间",
                "parameter_schema": [
                    {
                        "name": "seconds",
                        "label": "等待秒数:",
                        "type": "string",
                        "default_value": "1",
                        "tooltip": "要等待的秒数，可以使用小数表示毫秒级延迟"
                    }
                ]
            }
        }
    },
    "DATA_PROCESSING": {
        "display_text": "数据处理",
        "actions": {
            "APPLY_DATA_TEMPLATE": {
                "display_text": "应用数据模板",
                "parameter_schema": [
                    {
                        "name": "data_variable",
                        "label": "数据变量名:",
                        "type": "string",
                        "tooltip": "包含数据的变量名称，可以是单个数据对象或数据列表"
                    },
                    {
                        "name": "template",
                        "label": "模板内容:",
                        "type": "multiline",
                        "default_value": "这是{field}的值，使用{other_field|upper}进行格式化",
                        "tooltip": "使用{字段名}格式的占位符，可以用|添加过滤器，如{字段|upper}"
                    },
                    {
                        "name": "save_to_variable",
                        "label": "结果变量名:",
                        "type": "string",
                        "default_value": "formatted_data",
                        "tooltip": "保存处理结果的变量名"
                    }
                ]
            },
            "CLEAN_DATA": {
                "display_text": "清洗数据",
                "parameter_schema": [
                    {
                        "name": "data_variable",
                        "label": "数据变量名:",
                        "type": "string",
                        "tooltip": "包含数据的变量名称，可以是单个数据对象或数据列表"
                    },
                    {
                        "name": "cleaning_rules",
                        "label": "清洗规则(JSON):",
                        "type": "multiline",
                        "default_value": "{\n  \"字段名\": [\n    {\"type\": \"trim\"},\n    {\"type\": \"replace\", \"from\": \"旧值\", \"to\": \"新值\"}\n  ]\n}",
                        "tooltip": "JSON格式的清洗规则，支持trim、replace、default、cast、regex等"
                    },
                    {
                        "name": "save_to_variable",
                        "label": "结果变量名:",
                        "type": "string",
                        "default_value": "cleaned_data",
                        "tooltip": "保存处理结果的变量名"
                    }
                ]
            },
            "VALIDATE_DATA": {
                "display_text": "验证数据",
                "parameter_schema": [
                    {
                        "name": "data_variable",
                        "label": "数据变量名:",
                        "type": "string",
                        "tooltip": "包含数据的变量名称，可以是单个数据对象或数据列表"
                    },
                    {
                        "name": "validation_rules",
                        "label": "验证规则(JSON):",
                        "type": "multiline",
                        "default_value": "{\n  \"字段名\": [\n    {\"type\": \"required\", \"message\": \"必填项\"},\n    {\"type\": \"min_length\", \"value\": 5, \"message\": \"最少5个字符\"}\n  ]\n}",
                        "tooltip": "JSON格式的验证规则，支持required、min_length、max_length、regex、range、enum等"
                    },
                    {
                        "name": "save_result_to_variable",
                        "label": "结果变量名:",
                        "type": "string",
                        "default_value": "validation_result",
                        "tooltip": "保存验证结果的变量名，包含is_valid和errors字段"
                    }
                ]
            },
            "EXPORT_TO_CSV": {
                "display_text": "导出CSV",
                "parameter_schema": [
                    {
                        "name": "data_variable",
                        "label": "数据变量名:",
                        "type": "string",
                        "tooltip": "包含数据列表的变量名称"
                    },
                    {
                        "name": "file_path",
                        "label": "文件路径:",
                        "type": "string",
                        "default_value": "export_data.csv",
                        "tooltip": "导出CSV文件的路径"
                    },
                    {
                        "name": "encoding",
                        "label": "文件编码:",
                        "type": "string",
                        "default_value": "utf-8",
                        "tooltip": "CSV文件的编码格式"
                    }
                ]
            },
            "EXPORT_TO_EXCEL": {
                "display_text": "导出Excel",
                "parameter_schema": [
                    {
                        "name": "data_variable",
                        "label": "数据变量名:",
                        "type": "string",
                        "tooltip": "包含数据列表的变量名称"
                    },
                    {
                        "name": "file_path",
                        "label": "文件路径:",
                        "type": "string",
                        "default_value": "export_data.xlsx",
                        "tooltip": "导出Excel文件的路径"
                    }
                ]
            },
            "GENERATE_DATA_STATS": {
                "display_text": "生成数据统计",
                "parameter_schema": [
                    {
                        "name": "data_variable",
                        "label": "数据变量名:",
                        "type": "string",
                        "tooltip": "包含数据列表的变量名称"
                    },
                    {
                        "name": "fields",
                        "label": "字段列表:",
                        "type": "string",
                        "tooltip": "要统计的字段，多个用逗号分隔，留空则统计所有字段"
                    },
                    {
                        "name": "save_to_variable",
                        "label": "结果变量名:",
                        "type": "string",
                        "default_value": "data_stats",
                        "tooltip": "保存统计结果的变量名"
                    }
                ]
            }
        }
    },
    "DATABASE": {
        "display_text": "数据库操作",
        "actions": {
            "DB_CONNECT": {
                "display_text": "连接数据库",
                "parameter_schema": [
                    {
                        "name": "connection_id",
                        "label": "连接标识:",
                        "type": "string",
                        "default_value": "default",
                        "tooltip": "数据库连接的唯一标识"
                    },
                    {
                        "name": "db_type",
                        "label": "数据库类型:",
                        "type": "dropdown",
                        "options": ["mysql", "sqlite", "postgres", "mongodb"],
                        "default_value": "mysql",
                        "tooltip": "数据库类型"
                    },
                    {
                        "name": "host",
                        "label": "主机地址:",
                        "type": "string",
                        "default_value": "localhost",
                        "tooltip": "数据库服务器地址"
                    },
                    {
                        "name": "port",
                        "label": "端口:",
                        "type": "string",
                        "default_value": "3306",
                        "tooltip": "数据库服务器端口"
                    },
                    {
                        "name": "user",
                        "label": "用户名:",
                        "type": "string",
                        "default_value": "root",
                        "tooltip": "数据库用户名"
                    },
                    {
                        "name": "password",
                        "label": "密码:",
                        "type": "password",
                        "default_value": "",
                        "tooltip": "数据库密码"
                    },
                    {
                        "name": "database",
                        "label": "数据库名:",
                        "type": "string",
                        "default_value": "",
                        "tooltip": "数据库名称"
                    },
                    {
                        "name": "database_path",
                        "label": "SQLite数据库路径:",
                        "type": "string",
                        "default_value": "database.db",
                        "tooltip": "SQLite数据库文件路径，仅对SQLite有效"
                    }
                ]
            },
            "DB_DISCONNECT": {
                "display_text": "断开数据库连接",
                "parameter_schema": [
                    {
                        "name": "connection_id",
                        "label": "连接标识:",
                        "type": "string",
                        "default_value": "default",
                        "tooltip": "要断开的数据库连接标识"
                    }
                ]
            },
            "DB_EXECUTE_QUERY": {
                "display_text": "执行数据库查询",
                "parameter_schema": [
                    {
                        "name": "connection_id",
                        "label": "连接标识:",
                        "type": "string",
                        "default_value": "default",
                        "tooltip": "数据库连接标识"
                    },
                    {
                        "name": "query",
                        "label": "SQL查询:",
                        "type": "multiline",
                        "default_value": "SELECT * FROM users WHERE id = :id",
                        "tooltip": "SQL查询语句，可以使用:参数名作为参数占位符"
                    },
                    {
                        "name": "parameters",
                        "label": "查询参数(JSON):",
                        "type": "multiline",
                        "default_value": "{\n  \"id\": 1\n}",
                        "tooltip": "JSON格式的查询参数"
                    },
                    {
                        "name": "save_to_variable",
                        "label": "结果变量名:",
                        "type": "string",
                        "default_value": "query_results",
                        "tooltip": "保存查询结果的变量名"
                    }
                ]
            },
            "DB_EXECUTE_UPDATE": {
                "display_text": "执行数据库更新",
                "parameter_schema": [
                    {
                        "name": "connection_id",
                        "label": "连接标识:",
                        "type": "string",
                        "default_value": "default",
                        "tooltip": "数据库连接标识"
                    },
                    {
                        "name": "query",
                        "label": "SQL更新:",
                        "type": "multiline",
                        "default_value": "UPDATE users SET name = :name WHERE id = :id",
                        "tooltip": "SQL更新语句，可以使用:参数名作为参数占位符"
                    },
                    {
                        "name": "parameters",
                        "label": "更新参数(JSON):",
                        "type": "multiline",
                        "default_value": "{\n  \"id\": 1,\n  \"name\": \"新名称\"\n}",
                        "tooltip": "JSON格式的更新参数"
                    },
                    {
                        "name": "save_to_variable",
                        "label": "结果变量名:",
                        "type": "string",
                        "default_value": "affected_rows",
                        "tooltip": "保存受影响行数的变量名"
                    }
                ]
            },
            "DB_BUILD_SELECT": {
                "display_text": "构建SELECT查询",
                "parameter_schema": [
                    {
                        "name": "table",
                        "label": "表名:",
                        "type": "string",
                        "tooltip": "要查询的表名"
                    },
                    {
                        "name": "fields",
                        "label": "字段列表:",
                        "type": "string",
                        "tooltip": "要查询的字段，多个用逗号分隔，留空则查询所有字段"
                    },
                    {
                        "name": "where_condition",
                        "label": "WHERE条件(JSON):",
                        "type": "multiline",
                        "default_value": "{\n  \"id\": 1,\n  \"status\": \"active\"\n}",
                        "tooltip": "JSON格式的WHERE条件"
                    },
                    {
                        "name": "order_by",
                        "label": "排序:",
                        "type": "string",
                        "tooltip": "排序字段，格式如 name ASC, id DESC，多个用逗号分隔"
                    },
                    {
                        "name": "limit",
                        "label": "结果限制数量:",
                        "type": "string",
                        "tooltip": "限制返回的结果数量"
                    },
                    {
                        "name": "offset",
                        "label": "结果偏移量:",
                        "type": "string",
                        "tooltip": "结果的偏移量，用于分页"
                    },
                    {
                        "name": "save_to_variable",
                        "label": "结果变量名:",
                        "type": "string",
                        "default_value": "select_query",
                        "tooltip": "保存构建的查询语句的变量名"
                    }
                ]
            },
            "DB_BUILD_INSERT": {
                "display_text": "构建INSERT查询",
                "parameter_schema": [
                    {
                        "name": "table",
                        "label": "表名:",
                        "type": "string",
                        "tooltip": "要插入数据的表名"
                    },
                    {
                        "name": "data",
                        "label": "插入数据(JSON):",
                        "type": "multiline",
                        "default_value": "{\n  \"name\": \"测试\",\n  \"email\": \"test@example.com\"\n}",
                        "tooltip": "JSON格式的插入数据"
                    },
                    {
                        "name": "save_to_variable",
                        "label": "结果变量名:",
                        "type": "string",
                        "default_value": "insert_query",
                        "tooltip": "保存构建的插入语句的变量名"
                    }
                ]
            },
            "DB_BUILD_UPDATE": {
                "display_text": "构建UPDATE查询",
                "parameter_schema": [
                    {
                        "name": "table",
                        "label": "表名:",
                        "type": "string",
                        "tooltip": "要更新的表名"
                    },
                    {
                        "name": "data",
                        "label": "更新数据(JSON):",
                        "type": "multiline",
                        "default_value": "{\n  \"name\": \"新名称\",\n  \"status\": \"inactive\"\n}",
                        "tooltip": "JSON格式的更新数据"
                    },
                    {
                        "name": "where_condition",
                        "label": "WHERE条件(JSON):",
                        "type": "multiline",
                        "default_value": "{\n  \"id\": 1\n}",
                        "tooltip": "JSON格式的WHERE条件"
                    },
                    {
                        "name": "save_to_variable",
                        "label": "结果变量名:",
                        "type": "string",
                        "default_value": "update_query",
                        "tooltip": "保存构建的更新语句的变量名"
                    }
                ]
            },
            "DB_BUILD_DELETE": {
                "display_text": "构建DELETE查询",
                "parameter_schema": [
                    {
                        "name": "table",
                        "label": "表名:",
                        "type": "string",
                        "tooltip": "要删除数据的表名"
                    },
                    {
                        "name": "where_condition",
                        "label": "WHERE条件(JSON):",
                        "type": "multiline",
                        "default_value": "{\n  \"id\": 1\n}",
                        "tooltip": "JSON格式的WHERE条件"
                    },
                    {
                        "name": "save_to_variable",
                        "label": "结果变量名:",
                        "type": "string",
                        "default_value": "delete_query",
                        "tooltip": "保存构建的删除语句的变量名"
                    }
                ]
            }
        }
    }
}

class ActionListWidget(QTreeWidget):
    """
    A QTreeWidget that displays available DrissionPage actions, categorized.
    Emits a signal when a specific action (leaf node) is selected.
    """
    # Signal: action_id (str), parameter_schema (List[Dict[str, Any]])
    action_selected = pyqtSignal(str, list)

    def __init__(self, parent = None):
        super().__init__(parent)
        self.setHeaderHidden(True) # Hide the default header
        self._populate_actions()
        self.itemClicked.connect(self._on_item_clicked)

    def _populate_actions(self):
        """
        Populates the tree widget with actions defined in ACTION_DEFINITIONS.
        """
        self.clear() # Clear existing items
        
        for category_id, category_data in ACTION_DEFINITIONS.items():
            category_item = QTreeWidgetItem(self, [category_data.get("display_text", category_id)])
            category_item.setData(0, Qt.UserRole, {"id": category_id, "type": "category"}) # Store data

            if "actions" in category_data:
                for action_id, action_info in category_data["actions"].items():
                    action_display_text = action_info.get("display_text", action_id)
                    action_item = QTreeWidgetItem(category_item, [action_display_text])
                    # Store action_id and its parameter_schema in the item's data
                    action_item.setData(0, Qt.UserRole, {
                        "id": action_id,
                        "type": "action",
                        "schema": action_info.get("parameter_schema", [])
                    })
        self.expandAll() # Optionally expand all categories initially

    def _on_item_clicked(self, item, column):
        """
        Handles item click events. If an action item (leaf node) is clicked,
        it emits the action_selected signal.
        """
        item_data = item.data(0, Qt.UserRole)
        if item_data and item_data.get("type") == "action":
            action_id = item_data.get("id")
            parameter_schema = item_data.get("schema", [])
            if action_id:
                self.action_selected.emit(action_id, parameter_schema)
                print(f"ActionListWidget: Selected action '{action_id}'") # Debug print

if __name__ == '__main__': # For testing this widget directly
    from PyQt5.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    widget = ActionListWidget()
    
    def on_action_selected_test(action_id, schema):
        print(f"Test: Action '{action_id}' selected. Schema: {schema}")

    widget.action_selected.connect(on_action_selected_test)
    widget.setWindowTitle("Test Action List Widget")
    widget.show()
    sys.exit(app.exec_())
