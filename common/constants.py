"""
项目常量定义
"""

import os
from pathlib import Path

# 应用程序信息
APP_NAME = "DrissionPage 自动化 GUI 工具"
APP_VERSION = "0.1.0"
APP_AUTHOR = "Your Name"

# 文件类型和扩展名
FLOW_FILE_EXTENSION = ".dgflow"  # DrissionPage GUI Flow
FLOW_FILE_FILTER = f"DrissionPage流程文件 (*{FLOW_FILE_EXTENSION})"

# 模板相关常量
TEMPLATE_DIRECTORY = os.path.join(str(Path.home()), ".drission_gui_tool", "templates")
TEMPLATE_FILE_EXTENSION = ".dgtmpl"  # DrissionPage GUI Template
TEMPLATE_FILE_FILTER = f"DrissionPage模板文件 (*{TEMPLATE_FILE_EXTENSION})"

# 计划任务相关常量
SCHEDULER_DIRECTORY = os.path.join(str(Path.home()), ".drission_gui_tool", "scheduler")
TASK_FILE_EXTENSION = ".dgtask"  # DrissionPage GUI Task
TASK_FILE_FILTER = f"DrissionPage任务文件 (*{TASK_FILE_EXTENSION})"

# 任务执行历史记录
HISTORY_DIRECTORY = os.path.join(str(Path.home()), ".drission_gui_tool", "history")
HISTORY_FILE_EXTENSION = ".dghist"  # DrissionPage GUI History

# 数据文件类型
CSV_FILE_FILTER = "CSV文件 (*.csv)"
EXCEL_FILE_FILTER = "Excel文件 (*.xlsx *.xls)"
DATA_FILE_FILTER = "数据文件 (*.csv *.xlsx *.xls)"

# GUI常量
DEFAULT_WINDOW_WIDTH = 1200
DEFAULT_WINDOW_HEIGHT = 800

# 操作执行相关常量
DEFAULT_TIMEOUT = 30  # 秒
DEFAULT_RETRY_TIMES = 3

# 日志相关常量
LOG_LEVELS = {
    "DEBUG": 10,
    "INFO": 20,
    "WARNING": 30,
    "ERROR": 40,
    "CRITICAL": 50
}

# DrissionPage配置相关常量
CHROMIUM_BROWSER_TYPES = ["Chrome", "Edge", "Chromium"]
DEFAULT_BROWSER_TYPE = "Chrome"

# 任务触发器类型
TRIGGER_TYPES = {
    "cron": "定时触发",
    "interval": "间隔触发",
    "date": "日期触发",
    "startup": "启动时触发",
    "file_change": "文件变更触发",
    "condition": "条件触发"
}
