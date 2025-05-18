from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView, QMenu, QAction, QMessageBox
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QColor
from typing import List, Dict, Any

class FlowViewWidget(QTableWidget):
    """
    A QTableWidget that displays the steps in the automation flow.
    Each row represents a step with its action name and parameters.
    """
    step_selected_for_editing = pyqtSignal(int, dict)  # step_index, step_data
    step_delete_requested = pyqtSignal(int)  # step_index
    flow_delete_requested = pyqtSignal(bool)  # clear_variables

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        # Set up columns
        self.setColumnCount(4)
        self.setHorizontalHeaderLabels(["#", "动作名称", "参数摘要", "已启用"])
        
        # Set column widths
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)  # #
        self.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Action Name
        self.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)  # Parameters
        self.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Enabled
        
        # Set selection behavior
        self.setSelectionBehavior(QTableWidget.SelectRows)
        self.setSelectionMode(QTableWidget.SingleSelection)
        self.setEditTriggers(QTableWidget.NoEditTriggers)  # Not directly editable
        
        # Enable context menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)
        
        # Connect signals
        self.itemClicked.connect(self._on_item_clicked)

    def update_view(self, steps: List[Dict[str, Any]]):
        """
        Updates the table with the current steps in the flow.
        
        Args:
            steps: List of step data dictionaries from FlowController
        """
        self.clearContents()
        self.setRowCount(len(steps))
        
        for row, step_data in enumerate(steps):
            action_id = step_data.get("action_id", "UNKNOWN")
            parameters = step_data.get("parameters", {})
            enabled = step_data.get("enabled", True)
            
            # Step number
            number_item = QTableWidgetItem(str(row + 1))
            self.setItem(row, 0, number_item)
            
            # Action name
            action_name_item = QTableWidgetItem(self._get_display_name(action_id, parameters))
            self.setItem(row, 1, action_name_item)
            
            # Parameters summary
            params_summary = self._generate_params_summary(parameters)
            params_item = QTableWidgetItem(params_summary)
            self.setItem(row, 2, params_item)
            
            # Enabled status
            enabled_item = QTableWidgetItem("✓" if enabled else "")
            enabled_item.setTextAlignment(Qt.AlignCenter)
            self.setItem(row, 3, enabled_item)
            
            # Store full step data for reference
            # We'll store it in the user role of the first cell (number_item)
            number_item.setData(Qt.UserRole, step_data)
    
    def clear_view(self):
        """Clears all steps from the view."""
        self.clearContents()
        self.setRowCount(0)
    
    def _on_item_clicked(self, item):
        """Handles item click event to allow editing of steps."""
        row = item.row()
        number_item = self.item(row, 0)
        if number_item:
            step_data = number_item.data(Qt.UserRole)
            if step_data:
                # Emit a signal to notify that this step should be edited
                self.step_selected_for_editing.emit(row, step_data)
    
    def _show_context_menu(self, position):
        """显示右键菜单"""
        menu = QMenu(self)
        selected_row = self.currentRow()
        
        # 只有选中了行才显示删除步骤选项
        if selected_row >= 0:
            delete_step_action = QAction("删除当前步骤", self)
            delete_step_action.triggered.connect(lambda: self._delete_step(selected_row))
            menu.addAction(delete_step_action)
            menu.addSeparator()
        
        # 删除整个流程的选项
        delete_flow_action = QAction("删除整个流程", self)
        delete_flow_action.triggered.connect(self._delete_flow)
        menu.addAction(delete_flow_action)
        
        # 显示菜单
        menu.exec_(self.viewport().mapToGlobal(position))
    
    def _delete_step(self, row):
        """删除单个步骤"""
        reply = QMessageBox.question(
            self, 
            "确认删除", 
            f"确定要删除步骤 #{row + 1} 吗？", 
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.step_delete_requested.emit(row)
    
    def _delete_flow(self):
        """删除整个流程"""
        # 使用标准QMessageBox，但自定义消息内容
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setWindowTitle("确认删除")
        msg_box.setText("确定要删除整个流程吗？")
        msg_box.setInformativeText("请选择是否同时清除所有变量。")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)
        
        # 在Qt5.5及更高版本中没有setCheckBox方法
        # 所以我们直接创建一个独立的对话框
        clear_vars = False
        
        if msg_box.exec_() == QMessageBox.Yes:
            # 如果用户点击了"是"，弹出另一个对话框询问是否清除变量
            vars_msg_box = QMessageBox(self)
            vars_msg_box.setIcon(QMessageBox.Question)
            vars_msg_box.setWindowTitle("清除变量")
            vars_msg_box.setText("是否同时清除所有变量？")
            vars_msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            vars_msg_box.setDefaultButton(QMessageBox.No)
            
            clear_vars = (vars_msg_box.exec_() == QMessageBox.Yes)
            self.flow_delete_requested.emit(clear_vars)
    
    def _get_display_name(self, action_id: str, parameters: Dict[str, Any]) -> str:
        """
        Gets a display name for the action, potentially using custom name from parameters.
        
        Args:
            action_id: The action identifier
            parameters: The step parameters
            
        Returns:
            A user-friendly display name
        """
        # Look for custom step name in parameters
        custom_name = parameters.get("__custom_step_name__")
        if custom_name:
            return custom_name
        
        # Default to action_id itself, could be improved to look up display name
        display_name = action_id
        
        # Map common action IDs to more readable names
        action_name_map = {
            # 页面导航
            "PAGE_GET": "打开URL",
            "PAGE_REFRESH": "刷新页面",
            "GET_PAGE_INFO": "获取网页信息",
            "OPEN_BROWSER": "打开浏览器",
            "CLOSE_BROWSER": "关闭浏览器",
            
            # 元素操作
            "ELEMENT_CLICK": "点击元素",
            "ELEMENT_INPUT": "输入文本",
            "CLICK_ELEMENT": "点击元素(新版)",
            "INPUT_TEXT": "输入文本(新版)",
            "WAIT_FOR_ELEMENT": "等待元素",
            "DELETE_ELEMENT": "删除元素",
            "GET_ELEMENT_TEXT": "获取元素文本",
            "GET_ELEMENT_ATTR": "获取元素属性",
            "SCROLL_TO_ELEMENT": "滚动到元素",
            "HOVER_ELEMENT": "鼠标悬停在元素上",
            "UPLOAD_FILE": "上传文件",
            "CLEAR_INPUT": "清空输入框",
            
            # 元素信息获取
            "GET_ELEMENT_INFO": "获取元素信息",
            "GET_ELEMENTS_COUNT": "获取元素数量",
            "GET_ELEMENT_PROPERTY": "获取元素属性值",
            "CHECK_ELEMENT_EXISTS": "检查元素是否存在",
            "IS_ELEMENT_VISIBLE": "检查元素是否可见",
            "GET_TEXT_FROM_ELEMENTS": "获取多个元素文本",
            "GET_ATTRIBUTES_FROM_ELEMENTS": "获取多个元素属性",
            
            # 流程控制
            "IF_CONDITION": "如果(条件判断)",
            "ELSE_CONDITION": "否则",
            "END_IF_CONDITION": "结束条件判断",
            "START_LOOP": "开始循环",
            "END_LOOP": "结束循环",
            "FOREACH_LOOP": "遍历循环",
            "END_FOREACH_LOOP": "结束遍历循环",
            "START_INFINITE_LOOP": "开始无限循环",
            "END_INFINITE_LOOP": "结束无限循环",
            "BREAK_LOOP": "跳出循环",
            "CONTINUE_LOOP": "继续循环",
            "TRY_BLOCK": "尝试执行(try)",
            "CATCH_BLOCK": "捕获异常(catch)",
            "FINALLY_BLOCK": "最终执行(finally)",
            "END_TRY_BLOCK": "结束try块",
            "WAIT": "等待",
            "DELETE_FLOW": "删除流程",
            
            # 变量管理
            "SET_VARIABLE": "设置变量",
            "DELETE_VARIABLE": "删除变量",
            "CLEAR_VARIABLES": "清空变量",
            "INCREMENT_VARIABLE": "递增变量",
            "DECREMENT_VARIABLE": "递减变量",
            "CONCAT_VARIABLE": "连接变量",
            
            # 数据处理
            "LOG_MESSAGE": "记录日志",
            "TAKE_SCREENSHOT": "截取屏幕截图",
            "SAVE_DATA": "保存数据",
            "LOAD_DATA": "加载数据",
            "EXECUTE_JAVASCRIPT": "执行JavaScript",
            "EXTRACT_DATA": "提取数据",
            "FORMAT_DATA": "格式化数据",
            "PARSE_JSON": "解析JSON",
            "PARSE_XML": "解析XML",
            "PARSE_HTML": "解析HTML",
            "PARSE_CSV": "解析CSV",
            "GENERATE_REPORT": "生成报告",
            "TRANSFORM_DATA": "转换数据",
            "FILTER_DATA": "筛选数据",
            "SORT_DATA": "排序数据",
            "MERGE_DATA": "合并数据",
            "SPLIT_DATA": "拆分数据",
            "COUNT_DATA": "统计数据",
            "VALIDATE_DATA": "验证数据",
            "EXPORT_DATA": "导出数据",
            "IMPORT_DATA": "导入数据",
            "CLEAN_DATA": "清洗数据",
            "DATA_CLEANUP": "清洗数据",
            "DATA_CLEANSING": "清洗数据",
            
            # 数据导出 - 完全匹配实际ID
            "EXPORT_TO_CSV": "导出CSV",
            "EXPORT_TO_EXCEL": "导出Excel",
            "EXPORT_TO_JSON": "导出JSON",
            "EXPORT_TO_XML": "导出XML",
            
            # 数据统计 - 完全匹配实际ID
            "GENERATE_DATA_STATS": "生成数据统计",
            "CREATE_DATA_STATISTICS": "生成数据统计",
            "DATA_STATISTICS": "生成数据统计",
            
            # 控制台相关 - 完全匹配实际ID
            "GET_CONSOLE_LOGS": "获取控制台日志",
            "CLEAR_CONSOLE": "清空控制台缓存",
            "CLEAR_CONSOLE_CACHE": "清空控制台缓存", 
            "CONSOLE_CLEAR": "清空控制台缓存",
            "CLEAR_CONSOLE_LOGS": "清空控制台缓存",
            "MONITOR_CONSOLE": "监控控制台",
            "FILTER_CONSOLE_LOGS": "筛选控制台日志",
            
            # 高级功能
            "HTTP_REQUEST": "发送HTTP请求",
            "HANDLE_ALERT": "处理弹窗",
            "SWITCH_FRAME": "切换框架",
            "MOUSE_ACTION": "鼠标动作",
            "KEYBOARD_ACTION": "键盘动作",
            "DB_QUERY": "数据库查询",
            "CUSTOM_PYTHON": "自定义Python代码",
            
            # 数据库操作 - 完全匹配实际ID
            "DB_CONNECT": "连接数据库",
            "DB_DISCONNECT": "断开数据库连接",
            "DB_EXECUTE": "执行SQL",
            "DB_EXECUTE_QUERY": "执行数据库查询",
            "DB_EXECUTE_UPDATE": "执行数据库更新",
            "DB_QUERY": "查询数据库",
            "DB_INSERT": "插入数据",
            "DB_UPDATE": "更新数据",
            "DB_DELETE": "删除数据",
            "DB_CLOSE": "关闭数据库连接",
            "DB_BEGIN_TRANSACTION": "开始事务",
            "DB_COMMIT": "提交事务",
            "DB_ROLLBACK": "回滚事务",
            
            # 构建SQL查询 - 完全匹配实际ID
            "DB_BUILD_SELECT": "构建SELECT查询",
            "DB_BUILD_INSERT": "构建INSERT查询",
            "DB_BUILD_UPDATE": "构建UPDATE查询",
            "DB_BUILD_DELETE": "构建DELETE查询",
            "BUILD_SQL_QUERY": "构建SQL查询",
            
            # 其他变体
            "BUILD_MONGODB_QUERY": "构建MongoDB查询",
            "BUILD_ELASTICSEARCH_QUERY": "构建Elasticsearch查询",
            "BUILD_DYNAMODB_QUERY": "构建DynamoDB查询",
            
            # 辅助功能
            "NOTIFICATION": "发送通知",
            "SEND_EMAIL": "发送邮件",
            "SYSTEM_COMMAND": "执行系统命令",
            "READ_FILE": "读取文件",
            "WRITE_FILE": "写入文件",
            "APPEND_FILE": "追加文件",
            "DELETE_FILE": "删除文件",
            "FILE_EXISTS": "检查文件是否存在",
            "CREATE_DIRECTORY": "创建目录",
            "REMOVE_DIRECTORY": "删除目录",
            "LIST_FILES": "列出文件",
            "MOVE_FILE": "移动文件",
            "COPY_FILE": "复制文件",
            "ZIP_FILES": "压缩文件",
            "UNZIP_FILES": "解压文件",
            "GET_FILE_INFO": "获取文件信息",
            
            # 高级交互
            "TAKE_SCREENSHOT": "截图",
            "SCROLL_PAGE": "滚动页面",
            "DRAG_AND_DROP": "拖放元素",
            "MOUSE_HOVER": "鼠标悬停",
            "MOUSE_DRAG_DROP": "拖放操作",
            "MOUSE_DOUBLE_CLICK": "双击操作",
            "MOUSE_RIGHT_CLICK": "右键点击",
            "MOUSE_MOVE_PATH": "鼠标轨迹移动",
            "CLICK_CONTEXT_MENU": "点击上下文菜单项",
            "SWITCH_TO_IFRAME": "切换到iframe",
            "SWITCH_TO_PARENT_FRAME": "切换到父级框架",
            "SWITCH_TO_DEFAULT_CONTENT": "切换到主文档",
            "MANAGE_COOKIES": "管理Cookie",
            
            # 自定义代码
            "EXECUTE_JAVASCRIPT": "执行JavaScript",
            "EXECUTE_JS_WITH_CONSOLE": "执行JS并记录控制台输出",
            
            # 等待操作
            "WAIT_SECONDS": "等待时间",
            "WAIT_FOR_CONDITION": "等待条件满足",
            "WAIT_FOR_NAVIGATION": "等待页面跳转",
            "WAIT_FOR_DOWNLOAD": "等待下载完成",
            
            # 数据处理
            "APPLY_DATA_TEMPLATE": "应用数据模板",
            "DATA_EXTRACTION": "数据提取",
            "REGULAR_EXPRESSION": "正则表达式匹配",
            "STRING_OPERATION": "字符串操作",
            "NUMBER_OPERATION": "数值操作",
            "DATE_OPERATION": "日期操作",
            "LIST_OPERATION": "列表操作",
            "DICT_OPERATION": "字典操作"
        }
        
        if action_id in action_name_map:
            display_name = action_name_map[action_id]
            
        return display_name
    
    def _generate_params_summary(self, parameters: Dict[str, Any]) -> str:
        """
        Generates a summary of the parameters for display in the table.
        
        Args:
            parameters: The step parameters
            
        Returns:
            A concise summary string
        """
        if not parameters:
            return "无参数"
        
        # Skip the custom name parameter for this summary
        filtered_params = {k: v for k, v in parameters.items() if k != "__custom_step_name__"}
        
        # Special handling for common parameters
        if "url" in filtered_params:
            return f"URL: {filtered_params['url']}"
        
        if "locator_value" in filtered_params:
            locator_type = filtered_params.get("locator_strategy", "CSS")
            return f"定位: {locator_type}='{filtered_params['locator_value']}'"
        
        if "text_to_input" in filtered_params:
            return f"文本: {filtered_params['text_to_input']}"
        
        # Generic handling for other parameters
        summaries = []
        for key, value in list(filtered_params.items())[:2]:  # Limit to first 2 params
            summaries.append(f"{key}: {value}")
        
        return ", ".join(summaries)
        
    def highlight_active_step(self, step_index: int):
        """
        高亮显示当前正在执行的步骤
        
        Args:
            step_index: 步骤索引
        """
        # 确保索引有效
        if 0 <= step_index < self.rowCount():
            # 首先清除所有行的高亮
            for row in range(self.rowCount()):
                for col in range(self.columnCount()):
                    item = self.item(row, col)
                    if item:
                        item.setBackground(QColor("white"))
            
            # 高亮显示当前步骤
            for col in range(self.columnCount()):
                item = self.item(step_index, col)
                if item:
                    item.setBackground(QColor("yellow"))
            
            # 自动滚动到当前行
            self.scrollToItem(self.item(step_index, 0))
            
            # 选中当前行
            self.selectRow(step_index)
    
    def update_step_status(self, step_index: int, success: bool):
        """
        更新步骤执行状态显示
        
        Args:
            step_index: 步骤索引
            success: 执行是否成功
        """
        # 确保索引有效
        if 0 <= step_index < self.rowCount():
            # 设置背景颜色表示执行结果
            background_color = QColor("lightgreen") if success else QColor("lightcoral")
            
            for col in range(self.columnCount()):
                item = self.item(step_index, col)
                if item:
                    item.setBackground(background_color)
    
    def get_selected_step_index(self):
        """
        获取当前选中的步骤索引
        
        Returns:
            当前选中行的索引，如果没有选中行则返回-1
        """
        selected_indexes = self.selectedIndexes()
        if selected_indexes:
            return selected_indexes[0].row()
        return -1
    
    def select_step(self, step_index: int):
        """
        选中指定索引的步骤
        
        Args:
            step_index: 步骤索引
        """
        if 0 <= step_index < self.rowCount():
            self.selectRow(step_index)
    
    def highlight_step(self, step_index: int):
        """
        高亮显示指定索引的步骤
        
        Args:
            step_index: 步骤索引
        """
        self.highlight_active_step(step_index)


if __name__ == "__main__":
    """Test the FlowViewWidget directly."""
    import sys
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    widget = FlowViewWidget()
    
    # Sample steps for testing
    test_steps = [
        {
            "action_id": "PAGE_GET",
            "parameters": {"url": "https://www.google.com", "timeout": 30},
            "enabled": True
        },
        {
            "action_id": "ELEMENT_CLICK",
            "parameters": {
                "locator_strategy": "CSS_SELECTOR",
                "locator_value": "input[name='q']",
                "timeout": 10
            },
            "enabled": True
        },
        {
            "action_id": "ELEMENT_INPUT",
            "parameters": {
                "locator_strategy": "NAME",
                "locator_value": "q",
                "text_to_input": "DrissionPage Python",
                "timeout": 5
            },
            "enabled": True
        },
        {
            "action_id": "CUSTOM_ACTION",
            "parameters": {"__custom_step_name__": "我的自定义步骤", "param1": "value1", "param2": 42},
            "enabled": False
        }
    ]
    
    widget.update_view(test_steps)
    
    def on_step_selected(index, data):
        print(f"Selected step #{index + 1}: {data}")
    
    widget.step_selected_for_editing.connect(on_step_selected)
    widget.setWindowTitle("Flow View Test")
    widget.show()
    
    sys.exit(app.exec_())
