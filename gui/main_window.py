from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QSplitter, QMessageBox, QAction, QActionGroup,
    QHBoxLayout, QVBoxLayout, QStatusBar, QToolBar, QMenu, QInputDialog,
    QFileDialog, QTabWidget, QCheckBox, QComboBox, QDockWidget, QDialog, QPushButton, QLabel,
    QApplication
)
from PyQt5.QtCore import Qt, pyqtSlot, QSettings
from PyQt5.QtGui import QIcon
from typing import Dict, Any, Optional
import logging
import time
import datetime
import traceback

# 修改相对导入为绝对导入
from drission_gui_tool.gui.widgets.action_list_widget import ActionListWidget
from drission_gui_tool.gui.widgets.parameter_panel import ParameterPanel
from drission_gui_tool.gui.widgets.flow_view_widget import FlowViewWidget
from drission_gui_tool.gui.widgets.control_buttons_widget import ControlButtonsWidget
from drission_gui_tool.gui.widgets.log_display_widget import LogDisplayWidget
from drission_gui_tool.core.flow_controller import FlowController
from drission_gui_tool.core.variable_manager import VariableScope
from drission_gui_tool.core.project_manager import ProjectManager
from drission_gui_tool.common.constants import FLOW_FILE_FILTER, FLOW_FILE_EXTENSION
from drission_gui_tool.core.flow_execution_thread import FlowExecutionThread
from .widgets.debug_panel_widget import DebugPanelWidget
from ..core.debug_manager import DebugManager, ExecutionMode
from ..core.debug_flow_execution_thread import DebugFlowExecutionThread
from .widgets.flow_graph_widget import FlowGraphWidget
from drission_gui_tool.gui.dialogs.template_manager_dialog import TemplateManagerDialog
from drission_gui_tool.gui.dialogs.template_detail_dialog import TemplateDetailDialog
from drission_gui_tool.core.template_manager import TemplateManager

# 添加常量定义
APP_NAME = "DrissionPage 自动化 GUI 工具"
DEFAULT_WINDOW_WIDTH = 1200
DEFAULT_WINDOW_HEIGHT = 800

class MainWindow(QMainWindow):
    """
    主窗口类，集成所有UI组件和主要控制逻辑。
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.resize(DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT)
        
        # 初始化控制器
        self._flow_controller = FlowController()
        
        # 添加调试相关成员
        self._debug_manager = DebugManager()
        self._debug_execution_thread = None
        
        # 初始化UI组件
        self._init_ui()
        
        # 文件状态
        self._current_file_path = None
        self._is_modified = False
        self._unsaved_changes = False  # 添加此变量
        self._editing_step_index = -1  # 添加此变量
        
        # 执行线程
        self._execution_thread = None
        
        # 添加调试组件初始化（移到这里）
        self._setup_debug_components()
        
        # 创建工具栏
        self._create_toolbars()
        
        # 创建状态栏
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        
        # 更新窗口标题
        self._update_window_title()
        
        # 连接信号和槽
        self._connect_signals_slots()
        
        # 设置默认状态
        self.control_buttons.reset_state()
        
        # 根据设置恢复窗口大小和位置
        settings = QSettings("DrissionPage", "GUI Tool")
    
    def _init_ui(self):
        """初始化UI组件和布局"""
        self.setWindowTitle("DrissionPage 自动化 GUI 工具")
        self.resize(1200, 800)
        
        # 创建中央小部件
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        
        # 创建主分割器（顶部工作区和底部日志区）
        main_splitter = QSplitter(Qt.Vertical)
        main_layout.addWidget(main_splitter)
        
        # 创建工作区选项卡
        self.workspace_tabs = QTabWidget()
        
        # 创建经典视图选项卡
        classic_tab = QWidget()
        classic_layout = QVBoxLayout(classic_tab)
        classic_layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建工作区分割器
        workspace_splitter = QSplitter(Qt.Horizontal)
        
        # 创建左侧动作列表
        self.action_list_widget = ActionListWidget()
        workspace_splitter.addWidget(self.action_list_widget)
        
        # 创建中间面板（参数和流程视图的垂直分割）
        center_splitter = QSplitter(Qt.Vertical)
        
        # 创建参数面板
        self.parameter_panel = ParameterPanel()
        center_splitter.addWidget(self.parameter_panel)
        
        # 创建流程视图
        flow_view_container = QWidget()
        flow_view_layout = QVBoxLayout(flow_view_container)
        flow_view_layout.setContentsMargins(0, 0, 0, 0)
        
        self.flow_view_widget = FlowViewWidget()
        flow_view_layout.addWidget(self.flow_view_widget)
        
        # 添加控制按钮
        self.control_buttons = ControlButtonsWidget()
        flow_view_layout.addWidget(self.control_buttons)
        
        center_splitter.addWidget(flow_view_container)
        
        # 设置中间面板的尺寸比例
        center_splitter.setSizes([300, 500])
        
        workspace_splitter.addWidget(center_splitter)
        
        # 设置工作区分割器的尺寸比例
        workspace_splitter.setSizes([250, 950])
        
        # 添加经典视图到选项卡
        classic_layout.addWidget(workspace_splitter)
        self.workspace_tabs.addTab(classic_tab, "经典视图")
        
        # 创建流程图视图选项卡
        self.flow_graph_widget = FlowGraphWidget()
        self.workspace_tabs.addTab(self.flow_graph_widget, "流程图视图")
        
        # 添加工作区选项卡到主分割器
        main_splitter.addWidget(self.workspace_tabs)
        
        # 创建日志显示区域
        self.log_display_widget = LogDisplayWidget()
        main_splitter.addWidget(self.log_display_widget)
        
        # 设置主分割器的尺寸比例
        main_splitter.setSizes([600, 200])
        
        # 设置中央小部件
        self.setCentralWidget(central_widget)
        
        # 创建状态栏
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        
        # 创建菜单栏
        self._create_menus()
        
        # 显示欢迎信息
        self.log_display_widget.add_message("欢迎使用 DrissionPage 自动化 GUI 工具！")
        self.statusBar.showMessage("就绪", 3000)
    
    def _create_menus(self):
        """创建菜单栏"""
        # 文件菜单
        file_menu = self.menuBar().addMenu("文件")
        
        new_action = QAction("新建", self)
        new_action.triggered.connect(self._handle_new_flow)
        file_menu.addAction(new_action)
        
        open_action = QAction("打开", self)
        open_action.triggered.connect(self._handle_open_flow)
        file_menu.addAction(open_action)
        
        save_action = QAction("保存", self)
        save_action.triggered.connect(self._handle_save_flow)
        file_menu.addAction(save_action)
        
        save_as_action = QAction("另存为", self)
        save_as_action.triggered.connect(self._handle_save_flow_as)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        # 添加代码生成相关菜单项
        export_menu = file_menu.addMenu("导出")
        
        export_python_action = QAction("导出为Python脚本", self)
        export_python_action.triggered.connect(self._handle_export_to_python)
        export_menu.addAction(export_python_action)
        
        export_adv_python_action = QAction("导出为高级Python脚本", self)
        export_adv_python_action.triggered.connect(self._handle_export_advanced_python)
        export_menu.addAction(export_adv_python_action)
        
        export_python_package_action = QAction("导出为Python包", self)
        export_python_package_action.triggered.connect(self._handle_export_python_package)
        export_menu.addAction(export_python_package_action)
        
        export_menu.addSeparator()
        
        export_doc_action = QAction("导出文档", self)
        export_doc_action.triggered.connect(self._handle_generate_documentation)
        export_menu.addAction(export_doc_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("退出", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 编辑菜单
        edit_menu = self.menuBar().addMenu("编辑")
        
        add_step_action = QAction("添加步骤", self)
        add_step_action.triggered.connect(self._handle_add_step)
        edit_menu.addAction(add_step_action)
        
        edit_step_action = QAction("编辑步骤", self)
        edit_step_action.triggered.connect(self._handle_edit_step)
        edit_menu.addAction(edit_step_action)
        
        edit_menu.addSeparator()
        
        manage_variables_action = QAction("管理变量", self)
        manage_variables_action.triggered.connect(self._handle_variable_manager)
        edit_menu.addAction(manage_variables_action)
        
        # 代码生成菜单 - 添加专门的代码生成菜单
        code_gen_menu = self.menuBar().addMenu("代码生成")
        
        gen_basic_python_action = QAction("生成基础Python脚本", self)
        gen_basic_python_action.triggered.connect(self._handle_export_to_python)
        code_gen_menu.addAction(gen_basic_python_action)
        
        gen_adv_python_action = QAction("生成高级Python脚本", self)
        gen_adv_python_action.triggered.connect(self._handle_export_advanced_python)
        code_gen_menu.addAction(gen_adv_python_action)
        
        gen_python_package_action = QAction("生成完整Python包", self)
        gen_python_package_action.triggered.connect(self._handle_export_python_package)
        code_gen_menu.addAction(gen_python_package_action)
        
        code_gen_menu.addSeparator()
        
        gen_doc_action = QAction("生成流程文档", self)
        gen_doc_action.triggered.connect(self._handle_generate_documentation)
        code_gen_menu.addAction(gen_doc_action)
        
        # 模板菜单 - 添加新的模板菜单
        template_menu = self.menuBar().addMenu("模板")
        
        manage_templates_action = QAction("管理模板", self)
        manage_templates_action.triggered.connect(self._handle_manage_templates)
        template_menu.addAction(manage_templates_action)
        
        template_menu.addSeparator()
        
        save_as_template_action = QAction("保存为模板", self)
        save_as_template_action.triggered.connect(self._handle_save_as_template)
        template_menu.addAction(save_as_template_action)
        
        apply_template_action = QAction("应用模板", self)
        apply_template_action.triggered.connect(self._handle_apply_template)
        template_menu.addAction(apply_template_action)
        
        # 示例菜单
        examples_menu = self.menuBar().addMenu("示例")
        
        basic_demo_action = QAction("基础示例", self)
        basic_demo_action.triggered.connect(self._create_basic_demo_flow)
        examples_menu.addAction(basic_demo_action)
        
        baidu_demo_action = QAction("百度搜索示例", self)
        baidu_demo_action.triggered.connect(self._create_baidu_demo_flow)
        examples_menu.addAction(baidu_demo_action)
        
        condition_loop_demo_action = QAction("条件和循环示例", self)
        condition_loop_demo_action.triggered.connect(self._create_condition_loop_demo_flow)
        examples_menu.addAction(condition_loop_demo_action)
        
        examples_menu.addSeparator()
        
        js_demo_action = QAction("JavaScript示例", self)
        js_demo_action.triggered.connect(self._create_javascript_demo_flow)
        examples_menu.addAction(js_demo_action)
        
        adv_mouse_demo_action = QAction("高级鼠标操作示例", self)
        adv_mouse_demo_action.triggered.connect(self._create_advanced_mouse_demo_flow)
        examples_menu.addAction(adv_mouse_demo_action)
        
        adv_inter_demo_action = QAction("高级交互示例", self)
        adv_inter_demo_action.triggered.connect(self._create_advanced_interactions_demo_flow)
        examples_menu.addAction(adv_inter_demo_action)
        
        examples_menu.addSeparator()
        
        console_demo_action = QAction("控制台示例", self)
        console_demo_action.triggered.connect(self._create_console_demo_flow)
        examples_menu.addAction(console_demo_action)
        
        data_proc_demo_action = QAction("数据处理示例", self)
        data_proc_demo_action.triggered.connect(self._create_data_processing_demo_flow)
        examples_menu.addAction(data_proc_demo_action)
        
        db_demo_action = QAction("数据库示例", self)
        db_demo_action.triggered.connect(self._create_database_demo_flow)
        examples_menu.addAction(db_demo_action)
        
        adv_demo_action = QAction("高级综合示例", self)
        adv_demo_action.triggered.connect(self._create_advanced_demo_flow)
        examples_menu.addAction(adv_demo_action)
        
        # 视图菜单
        view_menu = self.menuBar().addMenu("视图")
        
        toggle_classic_view_action = QAction("经典视图", self)
        toggle_classic_view_action.setCheckable(True)
        toggle_classic_view_action.setChecked(True)
        toggle_classic_view_action.triggered.connect(lambda: self.workspace_tabs.setCurrentIndex(0))
        view_menu.addAction(toggle_classic_view_action)
        
        toggle_flow_graph_view_action = QAction("流程图视图", self)
        toggle_flow_graph_view_action.setCheckable(True)
        toggle_flow_graph_view_action.triggered.connect(lambda: self.workspace_tabs.setCurrentIndex(1))
        view_menu.addAction(toggle_flow_graph_view_action)
        
        # 设置视图切换组
        view_group = QActionGroup(self)
        view_group.addAction(toggle_classic_view_action)
        view_group.addAction(toggle_flow_graph_view_action)
        view_group.setExclusive(True)
        
        view_menu.addSeparator()
        
        toggle_debug_panel_action = QAction("调试面板", self)
        toggle_debug_panel_action.setCheckable(True)
        toggle_debug_panel_action.triggered.connect(self._toggle_debug_panel)
        view_menu.addAction(toggle_debug_panel_action)
        
        # 调试菜单
        debug_menu = self.menuBar().addMenu("调试")
        
        self.toggle_breakpoint_action = QAction("添加/移除断点", self)
        self.toggle_breakpoint_action.triggered.connect(self._handle_toggle_breakpoint)
        debug_menu.addAction(self.toggle_breakpoint_action)
        
        debug_menu.addSeparator()
        
        self.debug_action = QAction("开始调试", self)
        self.debug_action.triggered.connect(lambda: self._handle_debug_start("normal"))
        debug_menu.addAction(self.debug_action)
        
        self.continue_action = QAction("继续", self)
        self.continue_action.setEnabled(False)
        self.continue_action.triggered.connect(self._handle_debug_resume)
        debug_menu.addAction(self.continue_action)
        
        self.step_over_action = QAction("单步执行", self)
        self.step_over_action.setEnabled(False)
        self.step_over_action.triggered.connect(self._handle_debug_step_over)
        debug_menu.addAction(self.step_over_action)
        
        self.stop_debug_action = QAction("停止调试", self)
        self.stop_debug_action.setEnabled(False)
        self.stop_debug_action.triggered.connect(self._handle_debug_stop)
        debug_menu.addAction(self.stop_debug_action)
        
        # 帮助菜单
        help_menu = self.menuBar().addMenu("帮助")
        
        about_action = QAction("关于", self)
        about_action.triggered.connect(self._show_about_dialog)
        help_menu.addAction(about_action)
        
        # 将视图菜单动作保存为实例变量，以便后续更新
        self._debug_panel_action = toggle_debug_panel_action
    
    def _create_toolbars(self):
        """创建工具栏"""
        # 创建工具栏对象
        self.toolbar = QToolBar("主工具栏")
        self.toolbar.setMovable(False)
        self.addToolBar(self.toolbar)
        
        # 创建工具栏按钮
        self.new_flow_action = QAction("新建", self)
        self.new_flow_action.triggered.connect(self._handle_new_flow)
        
        self.open_flow_action = QAction("打开", self)
        self.open_flow_action.triggered.connect(self._handle_open_flow)
        
        self.save_flow_action = QAction("保存", self)
        self.save_flow_action.triggered.connect(self._handle_save_flow)
        
        self.run_flow_action = QAction("运行", self)
        self.run_flow_action.triggered.connect(self._handle_start_execution)
        
        self.stop_flow_action = QAction("停止", self)
        self.stop_flow_action.triggered.connect(self._handle_stop_execution)
        
        # 创建模板相关按钮
        self.templates_action = QAction("模板", self)
        template_menu = QMenu(self)
        
        self.manage_templates_action = QAction("管理模板", self)
        self.manage_templates_action.triggered.connect(self._handle_manage_templates)
        template_menu.addAction(self.manage_templates_action)
        
        self.save_as_template_action = QAction("保存为模板", self)
        self.save_as_template_action.triggered.connect(self._handle_save_as_template)
        template_menu.addAction(self.save_as_template_action)
        
        self.apply_template_action = QAction("应用模板", self)
        self.apply_template_action.triggered.connect(self._handle_apply_template)
        template_menu.addAction(self.apply_template_action)
        
        self.templates_action.setMenu(template_menu)
        
        # 创建代码生成相关按钮
        self.code_gen_action = QAction("代码生成", self)
        code_gen_menu = QMenu(self)
        
        self.gen_python_action = QAction("生成Python脚本", self)
        self.gen_python_action.triggered.connect(self._handle_export_to_python)
        code_gen_menu.addAction(self.gen_python_action)
        
        self.gen_adv_python_action = QAction("生成高级Python脚本", self)
        self.gen_adv_python_action.triggered.connect(self._handle_export_advanced_python)
        code_gen_menu.addAction(self.gen_adv_python_action)
        
        self.gen_python_package_action = QAction("生成Python包", self)
        self.gen_python_package_action.triggered.connect(self._handle_export_python_package)
        code_gen_menu.addAction(self.gen_python_package_action)
        
        code_gen_menu.addSeparator()
        
        self.gen_doc_action = QAction("生成文档", self)
        self.gen_doc_action.triggered.connect(self._handle_generate_documentation)
        code_gen_menu.addAction(self.gen_doc_action)
        
        self.code_gen_action.setMenu(code_gen_menu)
        
        # 添加按钮到工具栏
        self.toolbar.addAction(self.new_flow_action)
        self.toolbar.addAction(self.open_flow_action)
        self.toolbar.addAction(self.save_flow_action)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.run_flow_action)
        self.toolbar.addAction(self.stop_flow_action)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.templates_action)
        self.toolbar.addAction(self.code_gen_action)
    
    def _connect_signals_slots(self):
        """连接信号和槽"""
        # 动作列表选择
        self.action_list_widget.action_selected.connect(self._handle_action_selected)
        
        # 参数提交
        self.parameter_panel.parameters_submitted.connect(self._handle_parameters_submitted)
        
        # 流程视图选择
        self.flow_view_widget.step_selected_for_editing.connect(self._handle_step_selected_for_editing)
        
        # 连接FlowViewWidget中的删除信号
        self.flow_view_widget.step_delete_requested.connect(self._handle_step_delete_requested)
        self.flow_view_widget.flow_delete_requested.connect(self._handle_flow_delete_requested)
        
        # 控制按钮
        self.control_buttons.start_clicked.connect(self._handle_start_execution)
        self.control_buttons.stop_clicked.connect(self._handle_stop_execution)
        
        # 流程图编辑器信号
        self.flow_graph_widget.graph_changed.connect(self._handle_flow_graph_changed)
        self.flow_graph_widget.node_selected.connect(self._handle_flow_graph_node_selected)
        
        # 工作区选项卡切换信号
        self.workspace_tabs.currentChanged.connect(self._handle_workspace_tab_changed)
    
    def _handle_action_selected(self, action_id, parameter_schema):
        """处理从ActionListWidget选择动作的事件"""
        # 清除编辑模式
        self._editing_step_index = -1
        
        # 在参数面板中显示所选动作的参数
        self.parameter_panel.display_action_parameters(action_id, parameter_schema)
        
        self.statusBar.showMessage(f"已选择动作: {action_id}")
    
    def _handle_parameters_submitted(self, action_id, parameters):
        """处理从ParameterPanel提交的参数"""
        if self._editing_step_index >= 0:
            # 编辑现有步骤
            try:
                steps = self._flow_controller.get_steps()
                
                if 0 <= self._editing_step_index < len(steps):
                    # 更新步骤数据
                    steps[self._editing_step_index] = {
                        "action_id": action_id,
                        "parameters": parameters,
                        "enabled": True,  # 保持启用状态
                        "error_handler": steps[self._editing_step_index].get("error_handler", {})  # 保留原有的错误处理配置
                    }
                    
                    # 更新UI
                    self.flow_view_widget.update_view(steps)
                    self._unsaved_changes = True
                    self._update_window_title()
                    
                    self.log_display_widget.add_success(f"已更新步骤 #{self._editing_step_index + 1}: {action_id}")
                    self.statusBar.showMessage(f"已更新步骤 #{self._editing_step_index + 1}")
                else:
                    self.log_display_widget.add_error(f"无效的步骤索引: {self._editing_step_index + 1}")
            except Exception as e:
                self.log_display_widget.add_error(f"更新步骤失败: {str(e)}")
            
            # 重置编辑状态
            self._editing_step_index = -1
        else:
            # 添加新步骤
            step_index = self._flow_controller.add_step(action_id, parameters)
            self._unsaved_changes = True
            self._update_window_title()
            
            # 更新流程视图
            self.flow_view_widget.update_view(self._flow_controller.get_steps())
            
            self.log_display_widget.add_success(f"已添加步骤 #{step_index + 1}: {action_id}")
            self.statusBar.showMessage(f"已添加步骤 #{step_index + 1}")
    
    def _handle_step_selected_for_editing(self, step_index, step_data):
        """处理从FlowViewWidget选择步骤进行编辑的事件"""
        self._editing_step_index = step_index
        
        action_id = step_data.get("action_id")
        parameters = step_data.get("parameters", {})
        
        # 通过ActionListWidget查找参数架构
        parameter_schema = self._get_parameter_schema_for_action(action_id)
        
        if parameter_schema is not None:
            # 在参数面板中显示选中步骤的参数
            self.parameter_panel.display_action_parameters(action_id, parameter_schema, parameters)
            self.statusBar.showMessage(f"正在编辑步骤 #{step_index + 1}")
        else:
            self.log_display_widget.add_error(f"无法找到动作 '{action_id}' 的参数架构")
    
    def _get_parameter_schema_for_action(self, action_id):
        """从ActionListWidget的ACTION_DEFINITIONS查找动作的参数架构"""
        # 直接从 action_list_widget 模块导入 ACTION_DEFINITIONS
        from drission_gui_tool.gui.widgets.action_list_widget import ACTION_DEFINITIONS
        
        for category_data in ACTION_DEFINITIONS.values():
            if "actions" in category_data and action_id in category_data["actions"]:
                return category_data["actions"][action_id].get("parameter_schema", [])
        return None
    
    def _handle_new_flow(self):
        """处理新建流程操作"""
        if self._unsaved_changes:
            reply = QMessageBox.question(
                self, "确认新建",
                "当前流程有未保存的更改，确定要创建新流程吗？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.No:
                return
        
        # 获取流程名称
        flow_name, ok = QInputDialog.getText(self, "新建流程", "请输入流程名称:", text="新建流程")
        if not ok:
            return
        
        # 创建新流程
        self._flow_controller.create_new_flow(flow_name)
        self._current_file_path = ""
        self._unsaved_changes = False
        
        # 更新UI
        self.flow_view_widget.update_view(self._flow_controller.get_steps())
        self._update_window_title()
        
        self.log_display_widget.add_success(f"已创建新流程: {flow_name}")
        self.statusBar.showMessage(f"已创建新流程: {flow_name}")
    
    def _handle_open_flow(self):
        """处理打开流程操作"""
        if self._unsaved_changes:
            reply = QMessageBox.question(
                self, "确认打开",
                "当前流程有未保存的更改，确定要打开其他流程吗？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.No:
                return
        
        # 显示文件对话框
        file_path, _ = QFileDialog.getOpenFileName(
            self, "打开流程", "", FLOW_FILE_FILTER
        )
        
        if not file_path:
            return
        
        # 加载流程
        success, result = ProjectManager.load_flow(file_path)
        
        if not success:
            QMessageBox.critical(self, "错误", f"加载流程失败: {result}")
            return
        
        # 更新控制器
        self._flow_controller.create_new_flow(result["flow_name"])
        for step in result["steps"]:
            self._flow_controller.add_step(step["action_id"], step["parameters"])
        
        # 更新UI状态
        self._current_file_path = file_path
        self._unsaved_changes = False
        self.flow_view_widget.update_view(self._flow_controller.get_steps())
        self._update_window_title()
        
        self.log_display_widget.add_success(f"已加载流程: {result['flow_name']}")
        self.statusBar.showMessage(f"已加载流程: {result['flow_name']}")
    
    def _handle_save_flow(self):
        """处理保存流程操作"""
        # 如果没有当前文件路径，则执行"另存为"
        if not self._current_file_path:
            self._handle_save_flow_as()
            return
        
        # 获取当前流程数据
        flow_name = self._flow_controller.get_flow_name()
        steps = self._flow_controller.get_steps()
        
        # 保存流程
        success, message = ProjectManager.save_flow(self._current_file_path, flow_name, steps)
        
        if not success:
            QMessageBox.critical(self, "错误", f"保存流程失败: {message}")
            return
        
        # 更新UI状态
        self._unsaved_changes = False
        self._update_window_title()
        
        self.log_display_widget.add_success(f"流程已保存到: {self._current_file_path}")
        self.statusBar.showMessage(f"流程已保存到: {self._current_file_path}")
    
    def _handle_save_flow_as(self):
        """处理流程另存为操作"""
        # 显示文件对话框
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存流程", "", FLOW_FILE_FILTER
        )
        
        if not file_path:
            return
        
        # 确保文件扩展名正确
        if not file_path.endswith(FLOW_FILE_EXTENSION):
            file_path += FLOW_FILE_EXTENSION
        
        # 获取当前流程数据
        flow_name = self._flow_controller.get_flow_name()
        steps = self._flow_controller.get_steps()
        
        # 保存流程
        success, message = ProjectManager.save_flow(file_path, flow_name, steps)
        
        if not success:
            QMessageBox.critical(self, "错误", f"保存流程失败: {message}")
            return
        
        # 更新UI状态
        self._current_file_path = file_path
        self._unsaved_changes = False
        self._update_window_title()
        
        self.log_display_widget.add_success(f"流程已保存到: {file_path}")
        self.statusBar.showMessage(f"流程已保存到: {file_path}")
    
    def _handle_import_data(self):
        """处理导入数据操作"""
        # 修改相对导入为绝对导入
        from drission_gui_tool.gui.dialogs.data_import_dialog import DataImportDialog
        
        # 显示数据导入对话框
        dialog = DataImportDialog(self)
        result = dialog.exec_()
        
        if result == dialog.Accepted:
            # 获取导入的数据
            imported_data = dialog.get_imported_data()
            usage_settings = dialog.get_data_usage_settings()
            
            if not imported_data:
                self.log_display_widget.add_warning("未成功导入任何数据")
                return
            
            # 记录导入信息
            source = imported_data.get("source", "未知")
            source_text = "CSV" if source == "csv" else "Excel"
            total_rows = len(imported_data.get("data", []))
            
            self.log_display_widget.add_success(
                f"已成功导入{source_text}数据，共{total_rows}行，"
                f"{len(usage_settings.get('mappings', {}))}个字段"
            )
            
            # 根据使用方式处理数据
            usage_type = usage_settings.get("usage_type", "")
            
            if "循环遍历" in usage_type:
                # 创建循环遍历数据的步骤
                self._create_data_loop_steps(imported_data, usage_settings)
            else:
                # 将数据设置到当前步骤
                self.statusBar.showMessage("数据已导入，可在参数设置中使用")
                # TODO: 实现将数据传递给参数面板的功能
                self.log_display_widget.add_message(
                    "提示：导入数据功能将在下一版本完全实现，敬请期待"
                )
        else:
            self.log_display_widget.add_message("已取消数据导入")
    
    def _create_data_loop_steps(self, imported_data, usage_settings):
        """创建数据循环步骤"""
        # 获取要遍历的数据
        data = imported_data.get("data", [])
        if not data:
            self.log_display_widget.add_warning("导入的数据为空，无法创建循环")
            return
        
        # 获取列映射关系
        mappings = usage_settings.get("mappings", {})
        
        # 创建循环步骤
        self._flow_controller.add_step("START_LOOP", {
            "loop_count": len(data),
            "data_source": "imported",
            "data": data,
            "mappings": mappings
        })
        
        # 添加循环结束步骤
        self._flow_controller.add_step("END_LOOP", {})
        
        # 更新UI
        self._unsaved_changes = True
        self._update_window_title()
        self.flow_view_widget.update_view(self._flow_controller.get_steps())
        
        self.log_display_widget.add_success(
            f"已创建数据循环步骤，可在循环中使用导入的{len(data)}行数据"
        )
        self.statusBar.showMessage("已创建数据循环步骤")
    
    def _handle_start_execution(self):
        """处理开始执行流程的事件"""
        steps = self._flow_controller.get_steps()
        if not steps:
            self.log_display_widget.add_warning("流程为空，无法执行")
            self.control_buttons.reset_state()
            return
        
        # 检查流程控制器状态和线程状态
        if self._flow_controller.is_executing():
            self.log_display_widget.add_warning("流程正在执行中，请等待完成或停止当前执行")
            return
            
        # 如果已经有线程在运行，则不启动新线程
        if (self._execution_thread and self._execution_thread.isRunning()) or \
           (self._debug_execution_thread and self._debug_execution_thread.isRunning()):
            self.log_display_widget.add_warning("流程已在执行中，请等待完成或停止当前执行")
            return
        
        # 禁用相关UI控件
        self.action_list_widget.setEnabled(False)
        self.parameter_panel.setEnabled(False)
        self.flow_view_widget.setEnabled(False)
        
        self.log_display_widget.add_message("开始执行流程")
        self.statusBar.showMessage("正在执行...")
        
        # 创建并启动执行线程
        self._execution_thread = FlowExecutionThread(self._flow_controller)
        
        # 连接线程信号到槽函数
        self._execution_thread.step_started.connect(self._on_step_execution_start)
        self._execution_thread.step_completed.connect(self._on_step_execution_complete)
        self._execution_thread.flow_completed.connect(self._on_flow_execution_complete)
        
        # 启动线程
        self._execution_thread.start()
    
    def _handle_stop_execution(self):
        """处理停止执行流程的事件"""
        # 常规执行线程
        if self._execution_thread and self._execution_thread.isRunning():
            self._execution_thread.stop()
            self.log_display_widget.add_warning("已请求停止执行流程")
            self.statusBar.showMessage("正在停止...")
            return
        
        # 调试执行线程
        if self._debug_execution_thread and self._debug_execution_thread.isRunning():
            self._debug_execution_thread.stop()
            self.log_display_widget.add_warning("已请求停止调试执行流程")
            self.statusBar.showMessage("正在停止...")
            return
            
        # 如果没有执行线程在运行，提示用户
        self.log_display_widget.add_message("当前没有正在执行的流程")
    
    def _on_step_execution_start(self, step_index, step_data):
        """步骤开始执行回调"""
        action_id = step_data.get("action_id", "")
        self.log_display_widget.add_message(f"开始执行步骤 #{step_index}: {action_id}")
        
        # 安全地调用高亮方法
        if hasattr(self.flow_view_widget, 'highlight_active_step'):
            self.flow_view_widget.highlight_active_step(step_index)
        elif hasattr(self.flow_view_widget, 'highlight_step'):
            self.flow_view_widget.highlight_step(step_index)
        elif hasattr(self.flow_view_widget, 'select_step'):
            self.flow_view_widget.select_step(step_index)
        
        # 如果是调试执行，添加调试日志
        if self._debug_execution_thread and isinstance(self._debug_execution_thread, DebugFlowExecutionThread):
            self._safe_debug_panel_call('add_debug_log', {
                "timestamp": time.time(),
                "level": "INFO",
                "message": f"步骤 #{step_index} ({action_id}) 开始执行"
            })
    
    def _on_step_execution_complete(self, step_index, success, message):
        """步骤执行完成回调"""
        if success:
            self.log_display_widget.add_success(f"步骤 #{step_index} 执行成功: {message}")
        else:
            self.log_display_widget.add_error(f"步骤 #{step_index} 执行失败: {message}")
        
        self.flow_view_widget.update_step_status(step_index, success)
        
        # 如果是调试执行，添加调试日志
        if self._debug_execution_thread and isinstance(self._debug_execution_thread, DebugFlowExecutionThread):
            self._safe_debug_panel_call('add_debug_log', {
                "timestamp": time.time(),
                "level": "SUCCESS" if success else "ERROR",
                "message": f"步骤 #{step_index} {'完成' if success else '失败'}: {message}"
            })
    
    def _on_flow_execution_complete(self, success):
        """流程执行完成回调"""
        # 重新启用UI控件
        self.action_list_widget.setEnabled(True)
        self.parameter_panel.setEnabled(True)
        self.flow_view_widget.setEnabled(True)
        
        # 显示执行结果
        if success:
            self.log_display_widget.add_success("流程执行完成")
            self.statusBar.showMessage("执行完成", 3000)
        else:
            self.log_display_widget.add_error("流程执行失败")
            self.statusBar.showMessage("执行失败", 3000)
        
        # 重置控制按钮状态
        self.control_buttons.reset_state()
        
        # 如果是调试执行，添加调试日志并更新UI状态
        if self._debug_execution_thread and isinstance(self._debug_execution_thread, DebugFlowExecutionThread):
            self._safe_debug_panel_call('add_debug_log', {
                "timestamp": time.time(),
                "level": "SUCCESS" if success else "ERROR",
                "message": f"流程执行{'成功' if success else '失败'}"
            })
            
            # 更新UI状态
            self._update_debug_menu_state(False, False)
            
        # 断开执行线程的连接，以避免内存泄漏
        if self._execution_thread:
            self._execution_thread.disconnect()
            self._execution_thread = None
            
        if self._debug_execution_thread:
            self._debug_execution_thread.disconnect()
            self._debug_execution_thread = None
    
    def _update_window_title(self):
        """更新窗口标题"""
        title = "DrissionPage 自动化 GUI 工具"
        
        flow_name = self._flow_controller.get_flow_name()
        if flow_name:
            title += f" - {flow_name}"
        
        if self._current_file_path:
            title += f" [{self._current_file_path}]"
        
        if self._unsaved_changes:
            title += " *"
        
        self.setWindowTitle(title)
    
    def _show_about_dialog(self):
        """显示关于对话框"""
        QMessageBox.about(
            self,
            "关于 DrissionPage 自动化 GUI 工具",
            "DrissionPage 自动化 GUI 工具\n\n"
            "一个用于图形化创建和执行 DrissionPage 自动化操作的工具。\n\n"
            "基于 PyQt5 和 DrissionPage 构建。"
        )
    
    def closeEvent(self, event):
        """处理窗口关闭事件"""
        # 询问是否保存当前流程
        if self._flow_controller.get_steps():
            reply = QMessageBox.question(
                self, 
                "保存流程", 
                "是否保存当前流程？", 
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
            )
            
            if reply == QMessageBox.Save:
                # 保存流程
                success = self._handle_save_flow()
                if not success:
                    # 如果保存失败，取消关闭
                    event.ignore()
                    return
            elif reply == QMessageBox.Cancel:
                # 取消关闭
                event.ignore()
                return
        
        # 保存应用程序设置
        self._save_settings()
        
        # 接受关闭事件
        event.accept()
    
    def _save_settings(self):
        """保存应用程序设置"""
        settings = QSettings("DrissionPage", "GUITool")
        
        # 保存窗口几何信息
        settings.setValue("geometry", self.saveGeometry())
        settings.setValue("windowState", self.saveState())
        
        # 保存工作区选项卡索引
        settings.setValue("workspaceTabIndex", self.workspace_tabs.currentIndex())
        
        # 保存流程图状态
        self.flow_graph_widget.save_state(settings, "flowGraph")
    
    def _restore_settings(self):
        """恢复应用程序设置"""
        settings = QSettings("DrissionPage", "GUITool")
        
        # 恢复窗口几何信息
        geometry = settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)
        
        window_state = settings.value("windowState")
        if window_state:
            self.restoreState(window_state)
        
        # 恢复工作区选项卡索引
        tab_index = settings.value("workspaceTabIndex", 0, type=int)
        self.workspace_tabs.setCurrentIndex(tab_index)
        
        # 恢复流程图状态
        self.flow_graph_widget.restore_state(settings, "flowGraph")

    def _create_demo_flow(self):
        """创建一个演示流程"""
        if self._unsaved_changes:
            reply = QMessageBox.question(
                self, "未保存的更改",
                "当前流程有未保存的更改，确定要创建演示流程吗？",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            if reply == QMessageBox.No:
                return
        
        # 创建流程选择对话框
        flow_types = ["百度搜索演示", "条件和循环演示"]
        selected_flow, ok = QInputDialog.getItem(
            self, "选择演示流程", "请选择要创建的演示流程类型:", 
            flow_types, 0, False
        )
        
        if not ok:
            return
        
        if selected_flow == "百度搜索演示":
            self._create_baidu_demo_flow()
        elif selected_flow == "条件和循环演示":
            self._create_condition_loop_demo_flow()
    
    def _create_baidu_demo_flow(self):
        """创建百度搜索演示流程"""
        # 创建新流程
        self._flow_controller.create_new_flow("百度搜索演示")
        
        # 添加步骤1: 打开百度
        self._flow_controller.add_step("PAGE_GET", {
            "url": "https://www.baidu.com",
            "timeout": 30,
            "__custom_step_name__": "打开百度首页"
        })
        
        # 添加步骤2: 在搜索框中输入文本
        self._flow_controller.add_step("ELEMENT_INPUT", {
            "locator_strategy": "ID",
            "locator_value": "kw",
            "text_to_input": "DrissionPage Python",
            "timeout": 10,
            "__custom_step_name__": "输入搜索关键词"
        })
        
        # 添加步骤3: 点击搜索按钮
        self._flow_controller.add_step("ELEMENT_CLICK", {
            "locator_strategy": "ID",
            "locator_value": "su",
            "timeout": 10,
            "__custom_step_name__": "点击搜索按钮"
        })
        
        # 更新UI
        self._unsaved_changes = True
        self.flow_view_widget.update_view(self._flow_controller.get_steps())
        self._update_window_title()
        
        self.log_display_widget.add_success("已创建百度搜索演示流程")
        self.statusBar.showMessage("已创建演示流程")
    
    def _create_condition_loop_demo_flow(self):
        """创建条件和循环示例流程"""
        # 创建新流程
        self._flow_controller.create_new_flow("条件和循环演示")
        
        # 添加步骤1: 打开百度
        self._flow_controller.add_step("PAGE_GET", {
            "url": "https://www.baidu.com",
            "timeout": 30,
            "__custom_step_name__": "打开百度首页"
        })
        
        # 添加步骤2: 重复3次的循环
        self._flow_controller.add_step("START_LOOP", {
            "loop_count": 3,
            "__custom_step_name__": "重复3次: 输入搜索和清空"
        })
        
        # 添加步骤3: 在搜索框中输入文本
        self._flow_controller.add_step("ELEMENT_INPUT", {
            "locator_strategy": "ID",
            "locator_value": "kw",
            "text_to_input": "DrissionPage 迭代 ${iteration}",
            "timeout": 10,
            "__custom_step_name__": "输入搜索关键词"
        })
        
        # 添加步骤4: 条件判断 - 如果搜索按钮存在
        self._flow_controller.add_step("IF_CONDITION", {
            "condition_type": "element_exists",
            "if_locator_strategy": "ID",
            "if_locator_value": "su",
            "if_timeout": 3,
            "__custom_step_name__": "检查搜索按钮是否存在"
        })
        
        # 添加步骤5: 条件为真时的操作 - 点击搜索按钮
        self._flow_controller.add_step("ELEMENT_CLICK", {
            "locator_strategy": "ID",
            "locator_value": "su",
            "timeout": 10,
            "__custom_step_name__": "点击搜索按钮"
        })
        
        # 添加步骤6: ELSE - 条件为假的情况
        self._flow_controller.add_step("ELSE_CONDITION", {
            "__custom_step_name__": "如果按钮不存在"
        })
        
        # 添加步骤7: 打印错误消息
        self._flow_controller.add_step("PAGE_REFRESH", {
            "__custom_step_name__": "刷新页面(因为找不到按钮)"
        })
        
        # 添加步骤8: 结束条件判断
        self._flow_controller.add_step("END_IF_CONDITION", {
            "__custom_step_name__": "结束条件判断"
        })
        
        # 添加步骤9: 清空搜索框
        self._flow_controller.add_step("ELEMENT_INPUT", {
            "locator_strategy": "ID",
            "locator_value": "kw",
            "text_to_input": "",
            "timeout": 10,
            "__custom_step_name__": "清空搜索框"
        })
        
        # 添加步骤10: 结束循环
        self._flow_controller.add_step("END_LOOP", {
            "__custom_step_name__": "结束循环"
        })
        
        # 更新UI
        self._unsaved_changes = True
        self.flow_view_widget.update_view(self._flow_controller.get_steps())
        self._update_window_title()
        
        self.log_display_widget.add_success("已创建条件和循环演示流程")
        self.statusBar.showMessage("已创建演示流程")

    def _handle_variable_manager(self):
        """打开变量管理器对话框"""
        from drission_gui_tool.gui.dialogs.variable_manager_dialog import VariableManagerDialog
        
        # 创建变量管理器对话框，传入流程控制器的变量管理器实例
        dialog = VariableManagerDialog(self, self._flow_controller._variable_manager)
        
        # 显示对话框
        dialog.exec_()
        
        # 变量可能已被修改，更新流程视图中的变量引用
        self.flow_view_widget.update()
    
    def _show_condition_editor(self, initial_condition=None):
        """
        显示条件编辑器对话框
        
        Args:
            initial_condition: 初始条件数据
            
        Returns:
            用户编辑后的条件数据或None（如果取消）
        """
        from drission_gui_tool.gui.dialogs.condition_editor_dialog import ConditionEditorDialog
        
        # 创建条件编辑器对话框
        dialog = ConditionEditorDialog(self, initial_condition)
        
        # 显示对话框
        if dialog.exec_():
            # 返回编辑后的条件
            return dialog.get_condition()
        
        return None

    def _create_advanced_demo_flow(self):
        """创建高级演示流程，展示变量和条件功能"""
        # 先清空现有流程
        self._flow_controller.create_new_flow("高级演示流程")
        
        # 设置一些全局变量
        self._flow_controller.create_variable("counter", 0, "integer", VariableScope.GLOBAL)
        self._flow_controller.create_variable("max_count", 5, "integer", VariableScope.GLOBAL)
        self._flow_controller.create_variable("website", "https://baidu.com", "string", VariableScope.GLOBAL)
        self._flow_controller.create_variable("search_keywords", ["Python", "自动化", "编程"], "list", VariableScope.GLOBAL)
        
        # 步骤1: 打开浏览器并访问网站
        self._flow_controller.add_step(
            "OPEN_BROWSER", 
            {
                "url": "${website}",  # 使用变量引用
                "browser_type": "Chrome"
            }
        )
        
        # 步骤2: 开始循环搜索
        self._flow_controller.add_step(
            "FOREACH_LOOP",
            {
                "collection_variable": "search_keywords",
                "item_variable": "keyword",
                "index_variable": "keyword_index"
            }
        )
        
        # 步骤3: 设置一个临时变量
        self._flow_controller.add_step(
            "SET_VARIABLE",
            {
                "variable_name": "current_search",
                "variable_value": "正在搜索: ${keyword} (${keyword_index}/${search_keywords.length})",
                "variable_scope": VariableScope.TEMPORARY
            }
        )
        
        # 步骤4: 记录日志
        self._flow_controller.add_step(
            "LOG_MESSAGE",
            {
                "message": "${current_search}",
                "level": "INFO"
            }
        )
        
        # 步骤5: 尝试使用 try-catch-finally 结构
        self._flow_controller.add_step(
            "TRY_BLOCK",
            {}
        )
        
        # 步骤6: try块中的步骤 - 输入搜索词
        self._flow_controller.add_step(
            "INPUT_TEXT",
            {
                "locator_strategy": "id",
                "locator_value": "kw",
                "text": "${keyword}"
            },
            error_handler={
                "strategy": "retry",
                "retry_delay": 1
            }
        )
        
        # 步骤7: 点击搜索按钮
        self._flow_controller.add_step(
            "CLICK_ELEMENT",
            {
                "locator_strategy": "id",
                "locator_value": "su"
            }
        )
        
        # 步骤8: 添加一个可能会出错的步骤
        self._flow_controller.add_step(
            "WAIT_FOR_ELEMENT",
            {
                "locator_strategy": "css",
                "locator_value": ".non_existent_element_to_trigger_error",
                "timeout": 2
            }
        )
        
        # 步骤9: catch块
        self._flow_controller.add_step(
            "CATCH_BLOCK",
            {}
        )
        
        # 步骤10: 在catch块中处理错误
        self._flow_controller.add_step(
            "LOG_MESSAGE",
            {
                "message": "捕获到错误: ${error_message}",
                "level": "WARNING"
            }
        )
        
        # 步骤11: 增加计数器
        self._flow_controller.add_step(
            "SET_VARIABLE",
            {
                "variable_name": "counter",
                "variable_value": "${counter + 1}"
            }
        )
        
        # 步骤12: finally块
        self._flow_controller.add_step(
            "FINALLY_BLOCK",
            {}
        )
        
        # 步骤13: 在finally块中执行清理操作
        self._flow_controller.add_step(
            "LOG_MESSAGE",
            {
                "message": "清理资源，当前计数: ${counter}",
                "level": "INFO"
            }
        )
        
        # 步骤14: 结束try-catch-finally
        self._flow_controller.add_step(
            "END_TRY_BLOCK",
            {}
        )
        
        # 步骤15: 使用高级条件表达式
        self._flow_controller.add_step(
            "IF_CONDITION",
            {
                "condition_type": "variable_greater_than",
                "variable_name": "counter",
                "compare_value": "${max_count / 2}"
            }
        )
        
        # 步骤16: 条件为真时的操作
        self._flow_controller.add_step(
            "LOG_MESSAGE",
            {
                "message": "计数器超过一半最大值: ${counter} > ${max_count/2}",
                "level": "WARNING"
            }
        )
        
        # 步骤17: else条件
        self._flow_controller.add_step(
            "ELSE_CONDITION",
            {}
        )
        
        # 步骤18: 条件为假时的操作
        self._flow_controller.add_step(
            "LOG_MESSAGE",
            {
                "message": "计数器在合理范围内: ${counter} <= ${max_count/2}",
                "level": "INFO"
            }
        )
        
        # 步骤19: 结束if-else
        self._flow_controller.add_step(
            "END_IF_CONDITION",
            {}
        )
        
        # 步骤20: 结束foreach循环
        self._flow_controller.add_step(
            "END_FOREACH_LOOP",
            {}
        )
        
        # 步骤21: 复合条件判断
        condition_data = {
            "condition_type": "and",
            "conditions": [
                {
                    "condition_type": "variable_greater_equals",
                    "variable_name": "counter",
                    "compare_value": 3
                },
                {
                    "condition_type": "variable_less_than",
                    "variable_name": "counter",
                    "compare_value": "${max_count}"
                }
            ]
        }
        
        self._flow_controller.add_step(
            "IF_CONDITION",
            condition_data
        )
        
        # 步骤22: 复合条件为真时的操作
        self._flow_controller.add_step(
            "LOG_MESSAGE",
            {
                "message": "计数器在目标范围内: 3 <= ${counter} < ${max_count}",
                "level": "SUCCESS"
            }
        )
        
        # 步骤23: 结束复合条件
        self._flow_controller.add_step(
            "END_IF_CONDITION",
            {}
        )
        
        # 步骤24: 关闭浏览器
        self._flow_controller.add_step(
            "CLOSE_BROWSER",
            {}
        )
        
        # 更新UI
        self.flow_view_widget.update_view(self._flow_controller.get_steps())
        self.log_display_widget.add_success("已创建高级演示流程，包含变量、条件和错误处理")
        self.statusBar.showMessage("已创建高级演示流程")

    def _handle_add_step(self):
        """处理添加步骤操作"""
        # 这里可以实现具体的添加步骤逻辑
        # 例如：打开步骤选择对话框等
        self.log_display_widget.add_message("请从左侧动作列表选择要添加的步骤")

    def _handle_edit_step(self):
        """处理编辑步骤操作"""
        # 获取选中的步骤进行编辑
        selected_row = self.flow_view_widget.currentRow()
        if selected_row >= 0:
            steps = self._flow_controller.get_steps()
            if 0 <= selected_row < len(steps):
                step_data = steps[selected_row]
                self._handle_step_selected_for_editing(selected_row, step_data)
            else:
                self.log_display_widget.add_warning("无效的步骤索引")
        else:
            self.log_display_widget.add_warning("请先选择要编辑的步骤")

    def _handle_delete_step(self):
        """处理删除步骤操作"""
        selected_row = self.flow_view_widget.currentRow()
        if selected_row >= 0:
            reply = QMessageBox.question(
                self, "确认删除",
                f"确定要删除步骤 #{selected_row + 1} 吗？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                success = self._flow_controller.remove_step(selected_row)
                if success:
                    self._unsaved_changes = True
                    self._update_window_title()
                    self.flow_view_widget.update_view(self._flow_controller.get_steps())
                    self.log_display_widget.add_success(f"已删除步骤 #{selected_row + 1}")
                else:
                    self.log_display_widget.add_error("删除步骤失败")
        else:
            self.log_display_widget.add_warning("请先选择要删除的步骤")

    def _handle_step_delete_requested(self, step_index):
        """处理从FlowViewWidget请求删除步骤的信号"""
        if 0 <= step_index < len(self._flow_controller.get_steps()):
            success = self._flow_controller.remove_step(step_index)
            if success:
                self._unsaved_changes = True
                self._update_window_title()
                self.flow_view_widget.update_view(self._flow_controller.get_steps())
                self.log_display_widget.add_success(f"已删除步骤 #{step_index + 1}")
            else:
                self.log_display_widget.add_error("删除步骤失败")
    
    def _handle_flow_delete_requested(self, clear_variables):
        """处理从FlowViewWidget请求删除整个流程的信号"""
        # 创建新的空流程
        flow_name = self._flow_controller.get_flow_name() + " (清空)"
        self._flow_controller.create_new_flow(flow_name)
        
        # 如果需要，清除变量
        if clear_variables:
            # 清除所有变量
            self._flow_controller.get_variable_manager().clear_scope(VariableScope.GLOBAL)
            self._flow_controller.get_variable_manager().clear_scope(VariableScope.LOCAL)
            self.log_display_widget.add_message("已清除所有变量")
        
        # 更新UI
        self._unsaved_changes = True
        self._update_window_title()
        self.flow_view_widget.update_view(self._flow_controller.get_steps())
        self.log_display_widget.add_success(f"流程已清空")
        self.statusBar.showMessage("流程已清空")

    def _handle_run(self):
        """处理运行流程操作"""
        self._handle_start_execution()

    def _handle_stop(self):
        """处理停止流程操作"""
        self._handle_stop_execution()

    def _handle_about(self):
        """显示关于对话框"""
        QMessageBox.about(
            self,
            "关于 DrissionPage 自动化 GUI 工具",
            "DrissionPage 自动化 GUI 工具\n\n"
            "一个用于图形化创建和执行 DrissionPage 自动化操作的工具。\n\n"
            "基于 PyQt5 和 DrissionPage 构建。"
        )

    def _handle_export_data(self):
        """处理导出数据操作"""
        # 暂时是一个空的实现
        self.log_display_widget.add_message("导出数据功能还未实现")

    def _handle_save_as(self):
        """处理另存为操作"""
        self._handle_save_flow_as()

    def _create_advanced_interactions_demo_flow(self):
        """创建高级交互演示流程"""
        # 询问用户是否确定创建新的演示流程
        if self._unsaved_changes:
            reply = QMessageBox.question(
                self,
                "确认",
                "当前流程有未保存的更改，是否继续创建演示流程？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.No:
                return
                
        # 创建高级交互演示流程
        success = self._flow_controller.create_advanced_interactions_demo()
        
        if success:
            # 更新流程视图
            flow_steps = self._flow_controller.get_steps()
            self.flow_view_widget.update_view(flow_steps)
                
            # 更新窗口标题和状态
            self._current_file_path = None
            self._unsaved_changes = True
            self._update_window_title()
            
            # 提示用户
            self.log_display_widget.add_message("已创建高级交互演示流程，可以点击运行按钮执行")
            QMessageBox.information(
                self,
                "演示流程创建成功",
                "高级交互演示流程已创建，该流程演示了截图、滚动页面、鼠标悬停等高级交互功能。您可以通过点击运行按钮来执行此流程。",
                QMessageBox.Ok
            )
        else:
            # 提示用户创建失败
            QMessageBox.warning(
                self,
                "演示流程创建失败",
                "创建高级交互演示流程时发生错误。",
                QMessageBox.Ok
            )

    def _create_basic_demo_flow(self):
        """创建基本演示流程"""
        # 询问用户是否确定创建新的演示流程
        if self._unsaved_changes:
            reply = QMessageBox.question(
                self,
                "确认",
                "当前流程有未保存的更改，是否继续创建演示流程？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.No:
                return
                
        # 创建基本演示流程
        success = self._flow_controller.create_basic_demo()
        
        if success:
            # 更新流程视图
            flow_steps = self._flow_controller.get_steps()
            self.flow_view_widget.update_view(flow_steps)
                
            # 更新编辑器
            self._current_file_path = None
            self._update_window_title()
            
            self._unsaved_changes = True
            self.statusBar.showMessage("已创建基本演示流程，可以点击运行按钮执行")
            logging.info("已创建基本演示流程，可以点击运行按钮执行")
        else:
            QMessageBox.critical(self, "错误", "创建演示流程失败")
            
    def _create_javascript_demo_flow(self):
        """创建JavaScript演示流程"""
        # 询问用户是否确定创建新的演示流程
        if self._unsaved_changes:
            reply = QMessageBox.question(
                self,
                "确认",
                "当前流程有未保存的更改，是否继续创建演示流程？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.No:
                return
                
        # 创建JavaScript演示流程
        success = self._flow_controller.create_javascript_demo()
        
        if success:
            # 更新流程视图
            flow_steps = self._flow_controller.get_steps()
            self.flow_view_widget.update_view(flow_steps)
                
            # 更新编辑器
            self._current_file_path = None
            self._update_window_title()
            
            self._unsaved_changes = True
            self.statusBar.showMessage("已创建JavaScript演示流程，可以点击运行按钮执行")
            logging.info("已创建JavaScript演示流程，可以点击运行按钮执行")
        else:
            QMessageBox.critical(self, "错误", "创建JavaScript演示流程失败")

    def _create_advanced_mouse_demo_flow(self):
        """创建高级鼠标操作演示流程"""
        # 询问用户是否确定创建新的演示流程
        if self._unsaved_changes:
            reply = QMessageBox.question(
                self,
                "确认",
                "当前流程有未保存的更改，是否继续创建演示流程？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.No:
                return
                
        # 创建高级鼠标操作演示流程
        success = self._flow_controller.create_advanced_mouse_demo()
        
        if success:
            # 更新流程视图
            flow_steps = self._flow_controller.get_steps()
            self.flow_view_widget.update_view(flow_steps)
                
            # 更新编辑器
            self._current_file_path = None
            self._update_window_title()
            
            self._unsaved_changes = True
            self.statusBar.showMessage("已创建高级鼠标操作演示流程，可以点击运行按钮执行")
            logging.info("已创建高级鼠标操作演示流程，可以点击运行按钮执行")
        else:
            QMessageBox.critical(self, "错误", "创建高级鼠标操作演示流程失败")

    def _create_console_demo_flow(self):
        """创建控制台监听演示流程"""
        # 询问用户是否确定创建新的演示流程
        if self._unsaved_changes:
            reply = QMessageBox.question(
                self,
                "确认",
                "当前流程有未保存的更改，是否继续创建演示流程？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.No:
                return
                
        # 创建控制台监听演示流程
        success = self._flow_controller.create_console_demo_flow()
        
        if success:
            # 更新流程视图
            flow_steps = self._flow_controller.get_steps()
            self.flow_view_widget.update_view(flow_steps)
                
            # 更新编辑器
            self._current_file_path = None
            self._update_window_title()
            
            self._unsaved_changes = True
            self.statusBar.showMessage("已创建控制台监听演示流程，可以点击运行按钮执行")
            logging.info("已创建控制台监听演示流程，可以点击运行按钮执行")
            
            # 显示提示对话框
            QMessageBox.information(
                self,
                "演示流程创建成功",
                "控制台监听演示流程已创建，该流程演示了如何获取和处理浏览器控制台的信息。\n\n"
                "您可以点击运行按钮执行此流程，在日志面板中查看获取的控制台信息。",
                QMessageBox.Ok
            )
        else:
            QMessageBox.critical(self, "错误", "创建控制台监听演示流程失败")

    def _create_data_processing_demo_flow(self):
        """创建数据处理演示流程"""
        # 询问用户是否确定创建新的演示流程
        if self._unsaved_changes:
            reply = QMessageBox.question(
                self,
                "确认",
                "当前流程有未保存的更改，是否继续创建演示流程？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.No:
                return
                
        # 创建数据处理演示流程
        success = self._flow_controller.create_data_processing_demo_flow()
        
        if success:
            # 更新流程视图
            flow_steps = self._flow_controller.get_steps()
            self.flow_view_widget.update_view(flow_steps)
                
            # 更新编辑器
            self._current_file_path = None
            self._update_window_title()
            
            self._unsaved_changes = True
            QMessageBox.information(self, "成功", "数据处理演示流程已创建")
        else:
            QMessageBox.warning(self, "错误", "创建数据处理演示流程失败")
    
    def _create_database_demo_flow(self):
        """创建数据库操作演示流程"""
        # 询问用户是否确定创建新的演示流程
        if self._unsaved_changes:
            reply = QMessageBox.question(
                self,
                "确认",
                "当前流程有未保存的更改，是否继续创建演示流程？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.No:
                return
                
        # 创建数据库操作演示流程
        success = self._flow_controller.create_database_demo_flow()
        
        if success:
            # 更新流程视图
            flow_steps = self._flow_controller.get_steps()
            self.flow_view_widget.update_view(flow_steps)
                
            # 更新编辑器
            self._current_file_path = None
            self._update_window_title()
            
            self._unsaved_changes = True
            QMessageBox.information(self, "成功", "数据库操作演示流程已创建")
        else:
            QMessageBox.warning(self, "错误", "创建数据库操作演示流程失败")

    def _setup_debug_components(self):
        """设置调试组件"""
        # 创建调试面板
        self.debug_panel = DebugPanelWidget(self)
        
        # 创建调试停靠窗口
        self.debug_dock = QDockWidget("调试面板", self)
        self.debug_dock.setWidget(self.debug_panel)
        self.debug_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea | Qt.BottomDockWidgetArea)
        
        # 添加到主窗口
        self.addDockWidget(Qt.RightDockWidgetArea, self.debug_dock)
        
        # 初始状态隐藏
        self.debug_dock.hide()
        
        # 将调试管理器与流程控制器关联
        self._debug_manager.set_flow_controller(self._flow_controller)
        
        # 连接调试面板信号
        self._connect_debug_signals()
    
    def _connect_debug_signals(self):
        """连接调试面板信号"""
        # 断点相关
        self.debug_panel.breakpoint_toggled.connect(self._handle_breakpoint_toggled)
        self.debug_panel.breakpoint_added.connect(self._handle_breakpoint_added)
        self.debug_panel.breakpoint_removed.connect(self._handle_breakpoint_removed)
        self.debug_panel.breakpoint_enabled.connect(self._handle_breakpoint_enabled)
        self.debug_panel.breakpoint_condition_changed.connect(self._handle_breakpoint_condition_changed)
        
        # 执行控制
        self.debug_panel.debug_started.connect(self._handle_debug_start)
        self.debug_panel.debug_stopped.connect(self._handle_debug_stop)
        self.debug_panel.debug_paused.connect(self._handle_debug_pause)
        self.debug_panel.debug_resumed.connect(self._handle_debug_resume)
        self.debug_panel.debug_step_over.connect(self._handle_debug_step_over)
        self.debug_panel.debug_step_into.connect(self._handle_debug_step_into)
        self.debug_panel.debug_step_out.connect(self._handle_debug_step_out)
        self.debug_panel.debug_run_to_cursor.connect(self._handle_debug_run_to_cursor)
        
        # 变量监视
        self.debug_panel.variable_watch_added.connect(self._handle_variable_watch_added)
        self.debug_panel.variable_watch_removed.connect(self._handle_variable_watch_removed)

    def _toggle_debug_panel(self):
        """切换调试面板的显示状态"""
        if hasattr(self, 'debug_dock'):
            if self.debug_dock.isVisible():
                self.debug_dock.hide()
            else:
                self.debug_dock.show()
    
    def _update_debug_menu_state(self, is_debugging: bool, is_paused: bool):
        """更新调试菜单项状态"""
        self.debug_start_action.setEnabled(not is_debugging)
        self.debug_start_step_action.setEnabled(not is_debugging)
        self.debug_stop_action.setEnabled(is_debugging)
        self.debug_pause_action.setEnabled(is_debugging and not is_paused)
        self.debug_resume_action.setEnabled(is_debugging and is_paused)
        self.debug_step_over_action.setEnabled(is_debugging and is_paused)
        self.debug_step_into_action.setEnabled(is_debugging and is_paused)
        self.debug_step_out_action.setEnabled(is_debugging and is_paused)
        
        # 同时更新调试面板状态（如果已经初始化）
        if hasattr(self, 'debug_panel'):
            self.debug_panel.update_ui_state(is_debugging, is_paused)
    
    # 断点处理函数
    def _handle_breakpoint_toggled(self, step_index: int):
        """处理断点切换"""
        success, result = self._debug_manager.toggle_breakpoint(step_index)
        if success:
            # 更新断点列表（如果调试面板已初始化）
            if hasattr(self, 'debug_panel'):
                self.debug_panel.update_breakpoints(self._debug_manager.get_breakpoints())
            
            # 可以添加高亮显示等效果
            self.flow_view_widget.highlight_step(step_index)
    
    def _handle_breakpoint_added(self, step_index: int, bp_type: str, condition: str):
        """处理添加断点"""
        from ..core.debug_manager import Breakpoint, BreakpointType
        
        # 根据类型创建断点
        bp = None
        if bp_type == BreakpointType.LINE:
            bp = Breakpoint(step_index=step_index, breakpoint_type=BreakpointType.LINE)
        elif bp_type == BreakpointType.CONDITION:
            bp = Breakpoint(step_index=step_index, breakpoint_type=BreakpointType.CONDITION, condition=condition)
        elif bp_type == BreakpointType.ERROR:
            bp = Breakpoint(step_index=step_index, breakpoint_type=BreakpointType.ERROR)
        elif bp_type == BreakpointType.VARIABLE:
            # 变量断点需要额外参数，这里简化处理
            var_parts = condition.split()
            if len(var_parts) >= 3:
                var_name = var_parts[0]
                operator = var_parts[1]
                var_value = " ".join(var_parts[2:])
                bp = Breakpoint(
                    step_index=step_index, 
                    breakpoint_type=BreakpointType.VARIABLE,
                    variable_name=var_name,
                    variable_value=var_value,
                    comparison_operator=operator
                )
        
        if bp:
            self._debug_manager.add_breakpoint(bp)
            self._safe_debug_panel_call('update_breakpoints', self._debug_manager.get_breakpoints())
    
    def _handle_breakpoint_removed(self, breakpoint_id: str):
        """处理移除断点"""
        if self._debug_manager.remove_breakpoint(breakpoint_id):
            self._safe_debug_panel_call('update_breakpoints', self._debug_manager.get_breakpoints())
    
    def _handle_breakpoint_enabled(self, breakpoint_id: str, enabled: bool):
        """处理启用/禁用断点"""
        if self._debug_manager.enable_breakpoint(breakpoint_id, enabled):
            self._safe_debug_panel_call('update_breakpoints', self._debug_manager.get_breakpoints())
    
    def _handle_toggle_breakpoint(self):
        """处理切换当前选中步骤的断点"""
        # 获取当前选中的步骤
        selected_step = self.flow_view_widget.get_selected_step_index()
        if selected_step >= 0:
            self._handle_breakpoint_toggled(selected_step)
    
    def _handle_clear_breakpoints(self):
        """处理清除所有断点"""
        self._debug_manager.clear_breakpoints()
        self._safe_debug_panel_call('update_breakpoints', [])
    
    # 调试执行控制函数
    def _handle_debug_start(self, mode: str):
        """处理开始调试"""
        steps = self._flow_controller.get_steps()
        if not steps:
            self.log_display_widget.add_warning("流程为空，无法执行")
            return
        
        # 检查流程控制器状态
        if self._flow_controller.is_executing():
            self.log_display_widget.add_warning("流程正在执行中，请等待完成或停止当前执行")
            return
            
        # 如果已经有线程在运行，则不启动新线程
        if (self._debug_execution_thread and self._debug_execution_thread.isRunning()) or \
           (self._execution_thread and self._execution_thread.isRunning()):
            self.log_display_widget.add_warning("流程已在执行中，请等待完成或停止当前执行")
            return
        
        # 显示调试面板
        if hasattr(self, 'debug_dock') and not self.debug_dock.isVisible():
            self.debug_dock.show()
        
        # 禁用相关UI控件
        self.action_list_widget.setEnabled(False)
        self.parameter_panel.setEnabled(False)
        self.flow_view_widget.setEnabled(True)  # 调试时允许选择步骤
        
        self.log_display_widget.add_message(f"开始{mode}调试执行流程")
        self.statusBar.showMessage("正在执行...")
        
        # 创建并启动调试执行线程
        self._debug_execution_thread = DebugFlowExecutionThread(self._flow_controller, self._debug_manager)
        
        # 连接线程信号到槽函数
        self._debug_execution_thread.step_started.connect(self._on_step_execution_start)
        self._debug_execution_thread.step_completed.connect(self._on_step_execution_complete)
        self._debug_execution_thread.flow_completed.connect(self._on_flow_execution_complete)
        
        # 连接调试相关信号
        self._debug_execution_thread.breakpoint_hit.connect(self._on_breakpoint_hit)
        self._debug_execution_thread.execution_paused.connect(self._on_execution_paused)
        self._debug_execution_thread.execution_resumed.connect(self._on_execution_resumed)
        self._debug_execution_thread.variable_changed.connect(self._on_variable_changed)
        self._debug_execution_thread.metrics_updated.connect(self._on_metrics_updated)
        
        # 启动线程
        self._debug_execution_thread.start()
        
        # 更新UI状态
        self._update_debug_menu_state(True, False)
    
    def _handle_debug_stop(self):
        """处理停止调试"""
        if self._debug_execution_thread and self._debug_execution_thread.isRunning():
            self._debug_execution_thread.stop()
            self.log_display_widget.add_warning("已请求停止调试执行流程")
            self.statusBar.showMessage("正在停止...")
            
            # 更新UI状态
            self._update_debug_menu_state(False, False)
    
    def _handle_debug_pause(self):
        """处理暂停调试"""
        if self._debug_execution_thread and self._debug_execution_thread.isRunning():
            self._debug_execution_thread.pause()
            self.log_display_widget.add_message("已暂停调试执行")
    
    def _handle_debug_resume(self):
        """处理继续调试"""
        if self._debug_execution_thread and self._debug_execution_thread.isRunning():
            self._debug_execution_thread.resume()
            self.log_display_widget.add_message("已继续调试执行")
    
    def _handle_debug_step_over(self):
        """处理单步跳过"""
        if self._debug_execution_thread and self._debug_execution_thread.isRunning():
            self._debug_execution_thread.step_over()
            self.log_display_widget.add_message("单步执行 - 跳过")
    
    def _handle_debug_step_into(self):
        """处理单步进入"""
        if self._debug_execution_thread and self._debug_execution_thread.isRunning():
            self._debug_execution_thread.step_into()
            self.log_display_widget.add_message("单步执行 - 进入")
    
    def _handle_debug_step_out(self):
        """处理单步跳出"""
        if self._debug_execution_thread and self._debug_execution_thread.isRunning():
            self._debug_execution_thread.step_out()
            self.log_display_widget.add_message("单步执行 - 跳出")
    
    def _handle_debug_run_to_cursor(self, step_index: int):
        """处理运行到光标处"""
        if self._debug_execution_thread and self._debug_execution_thread.isRunning():
            self._debug_execution_thread.run_to_cursor(step_index)
            self.log_display_widget.add_message(f"运行到步骤 #{step_index}")
    
    # 变量监视处理函数
    def _handle_variable_watch_added(self, variable_name: str):
        """处理添加变量监视"""
        if self._debug_manager.add_watch_variable(variable_name):
            # 更新变量监视列表
            values = self._debug_manager.get_watch_variable_values()
            self._safe_debug_panel_call('update_variables', values)
    
    def _handle_variable_watch_removed(self, variable_name: str):
        """处理移除变量监视"""
        if self._debug_manager.remove_watch_variable(variable_name):
            # 更新变量监视列表
            values = self._debug_manager.get_watch_variable_values()
            self._safe_debug_panel_call('update_variables', values)
    
    # 调试事件处理
    def _on_breakpoint_hit(self, breakpoint_id: str, step_index: int, context_data: dict):
        """处理断点命中事件"""
        bp = self._debug_manager.get_breakpoint(breakpoint_id)
        if bp:
            bp_type_names = {
                "line": "行断点",
                "condition": "条件断点",
                "error": "错误断点",
                "variable": "变量断点"
            }
            bp_type = bp_type_names.get(bp.type, bp.type)
            
            self.log_display_widget.add_message(
                f"命中{bp_type} #{breakpoint_id} 在步骤 #{step_index}"
            )
            
            # 高亮显示断点所在步骤
            self.flow_view_widget.select_step(step_index)
            # 如果有highlight_step方法，则调用它
            if hasattr(self.flow_view_widget, 'highlight_step'):
                self.flow_view_widget.highlight_step(step_index)
            
            # 更新断点列表（更新命中次数）
            self._safe_debug_panel_call('update_breakpoints', self._debug_manager.get_breakpoints())
            
            # 更新UI状态
            self._update_debug_menu_state(True, True)
    
    def _on_execution_paused(self, step_index: int):
        """处理执行暂停事件"""
        self.log_display_widget.add_message(f"执行已暂停在步骤 #{step_index}")
        
        # 高亮显示当前步骤
        self.flow_view_widget.select_step(step_index)
        # 如果有highlight_step方法，则调用它
        if hasattr(self.flow_view_widget, 'highlight_step'):
            self.flow_view_widget.highlight_step(step_index)
        
        # 更新变量监视列表
        values = self._debug_manager.get_watch_variable_values()
        self._safe_debug_panel_call('update_variables', values)
        
        # 更新UI状态
        self._update_debug_menu_state(True, True)
    
    def _on_execution_resumed(self, step_index: int):
        """处理执行继续事件"""
        self.log_display_widget.add_message(f"执行已从步骤 #{step_index} 继续")
        
        # 更新UI状态
        self._update_debug_menu_state(True, False)
    
    def _on_variable_changed(self, variable_name: str, variable_value):
        """处理变量改变事件"""
        # 更新变量监视列表
        values = self._debug_manager.get_watch_variable_values()
        self._safe_debug_panel_call('update_variables', values)
    
    def _on_metrics_updated(self, metrics: dict):
        """处理性能指标更新事件"""
        self._safe_debug_panel_call('update_performance_metrics', metrics)

    def _safe_debug_panel_call(self, method_name, *args, **kwargs):
        """安全地调用调试面板的方法
        
        Args:
            method_name: 方法名称
            *args: 位置参数
            **kwargs: 关键字参数
            
        Returns:
            方法调用结果，如果方法不存在或调试面板未初始化则返回None
        """
        if hasattr(self, 'debug_panel'):
            panel_method = getattr(self.debug_panel, method_name, None)
            if panel_method and callable(panel_method):
                return panel_method(*args, **kwargs)
        return None

    def _handle_breakpoint_condition_changed(self, breakpoint_id: str, condition: str):
        """处理断点条件变更"""
        bp = self._debug_manager.get_breakpoint(breakpoint_id)
        if bp:
            # 更新断点类型和条件
            from ..core.debug_manager import BreakpointType
            bp.type = BreakpointType.CONDITION
            bp.condition = condition
            
            # 更新断点列表
            self._safe_debug_panel_call('update_breakpoints', self._debug_manager.get_breakpoints())
            
            self.log_display_widget.add_message(f"已更新断点 #{breakpoint_id} 的条件")
            self.statusBar.showMessage(f"已更新断点条件", 3000)

    def _handle_flow_graph_changed(self):
        """处理流程图变化事件"""
        # 如果在流程图视图中编辑了流程，需要同步回经典视图
        if self.workspace_tabs.currentIndex() == 1:
            self._sync_graph_to_flow()
    
    def _handle_flow_graph_node_selected(self, node_id, node_data):
        """处理流程图节点选择事件"""
        # 显示节点信息
        self.statusBar.showMessage(f"已选择节点：{node_data.get('title', '未命名')}")
    
    def _sync_flow_to_graph(self):
        """将经典视图的流程数据同步到流程图视图"""
        # 获取流程控制器中的流程数据
        steps = self._flow_controller.get_steps()
        
        # 转换为流程图数据格式
        flow_data = {
            "steps": [],
            "connections": []
        }
        
        # 添加节点数据
        for i, step in enumerate(steps):
            step_data = {
                "id": f"step_{i}",
                "type": "normal",  # 默认为普通节点
                "title": step.get("action_id", "未知动作"),
                "data": step,
                "position": {"x": 100, "y": 100 + i * 150}  # 简单排列
            }
            
            # 根据动作类型设置节点类型
            action_id = step.get("action_id", "")
            if action_id.startswith("IF_"):
                step_data["type"] = "condition"
            elif action_id.startswith("LOOP_") or "FOREACH" in action_id:
                step_data["type"] = "loop"
            
            flow_data["steps"].append(step_data)
        
        # 添加连接数据，简单线性连接
        for i in range(len(steps) - 1):
            connection_data = {
                "id": f"conn_{i}",
                "source": f"step_{i}",
                "source_port": "out",
                "target": f"step_{i + 1}",
                "target_port": "in"
            }
            flow_data["connections"].append(connection_data)
        
        # 导入流程数据到流程图
        self.flow_graph_widget.import_flow_data(flow_data)
    
    def _sync_graph_to_flow(self):
        """将流程图视图的流程数据同步到经典视图"""
        # 获取流程图数据
        flow_data = self.flow_graph_widget.export_flow_data()
        
        # 转换为流程控制器所需的步骤数据
        steps = []
        
        # 创建节点ID到索引的映射
        node_to_index = {}
        
        # 首先收集所有节点数据，并根据连接关系排序
        nodes = {}
        for step in flow_data.get("steps", []):
            nodes[step.get("id")] = step
        
        # 找到起始节点（没有输入连接的节点）
        start_nodes = set(nodes.keys())
        for conn in flow_data.get("connections", []):
            if conn.get("target") in start_nodes:
                start_nodes.remove(conn.get("target"))
        
        # 如果有多个起始节点，使用第一个
        current_node = next(iter(start_nodes)) if start_nodes else None
        
        # 沿着连接关系构建有序步骤列表
        visited = set()
        while current_node and current_node not in visited:
            # 防止循环
            visited.add(current_node)
            
            # 获取节点数据
            node_data = nodes.get(current_node)
            if node_data:
                # 将节点数据转换为步骤数据
                step_data = node_data.get("data", {})
                steps.append(step_data)
                
                # 记录节点ID到索引的映射
                node_to_index[current_node] = len(steps) - 1
            
            # 查找下一个节点
            next_node = None
            for conn in flow_data.get("connections", []):
                if conn.get("source") == current_node and conn.get("target") not in visited:
                    next_node = conn.get("target")
                    break
            
            current_node = next_node
        
        # 更新流程控制器
        if steps:
            # 清除当前流程
            self._flow_controller.create_new_flow(self._flow_controller.get_flow_name())
            
            # 添加步骤
            for step in steps:
                action_id = step.get("action_id", "")
                parameters = step.get("parameters", {})
                self._flow_controller.add_step(action_id, parameters)
            
            # 更新视图
            self.flow_view_widget.update_view(self._flow_controller.get_steps())
            
            self.log_display_widget.add_success("已从流程图同步流程数据")
        else:
            self.log_display_widget.add_warning("流程图中没有有效的步骤数据")

    def _handle_workspace_tab_changed(self, index):
        """处理工作区标签页变更事件"""
        # 处理切换到流程图视图
        if index == 1:  # 流程图视图
            # 同步流程到图形
            self._sync_flow_to_graph()
        # 处理切换到经典视图
        elif index == 0:  # 经典视图
            # 同步图形到流程
            self._sync_graph_to_flow()
        
        self.log_display_widget.add_message(f"切换到{self.workspace_tabs.tabText(index)}视图")

    def _handle_manage_templates(self):
        """处理管理模板操作"""
        # 创建模板管理对话框
        dialog = TemplateManagerDialog(self)
        result = dialog.exec_()
        
        # 如果用户选择了应用模板，则应用它
        if result == dialog.Accepted:
            template_data = dialog.get_selected_template()
            if template_data:
                self._apply_template_data(template_data)

    def _handle_save_as_template(self):
        """处理保存为模板操作"""
        # 如果流程为空，提示用户
        steps = self._flow_controller.get_steps()
        if not steps:
            QMessageBox.warning(self, "空流程", "当前流程为空，无法保存为模板")
            return
        
        # 获取模板名称
        template_name, ok = QInputDialog.getText(self, "保存为模板", "请输入模板名称:")
        if not ok or not template_name:
            return
        
        # 获取模板描述
        template_description, ok = QInputDialog.getText(self, "保存为模板", "请输入模板描述:")
        if not ok:
            return  # 用户取消了操作
        
        # 创建模板管理器
        template_manager = TemplateManager()
        
        # 创建模板数据
        template_data = {
            "template_name": template_name,
            "description": template_description,
            "steps": steps,
            "parameters": []  # 可以在此处添加参数
        }
        
        # 打开模板参数设置对话框（如果需要）
        # 这里可以添加参数设置逻辑，暂时省略
        
        # 保存模板
        # 获取分类（默认为custom）
        categories = template_manager.get_categories()
        category_items = list(categories.items())
        category_names = [f"{cat_id}: {name}" for cat_id, name in category_items]
        
        selected_category, ok = QInputDialog.getItem(
            self, "选择分类", "请选择模板分类:", category_names, 0, False
        )
        
        if not ok or not selected_category:
            category_id = "custom"  # 默认使用自定义分类
        else:
            category_id = selected_category.split(":")[0].strip()
        
        # 保存模板
        success, result = template_manager.save_template(template_data, category_id)
        
        if success:
            QMessageBox.information(self, "保存成功", f"模板已保存，ID: {result}")
            self.log_display_widget.add_success(f"流程已保存为模板: {template_name}")
        else:
            QMessageBox.warning(self, "保存失败", result)
            self.log_display_widget.add_error(f"保存模板失败: {result}")

    def _handle_apply_template(self):
        """处理应用模板操作"""
        # 创建模板管理对话框
        dialog = TemplateManagerDialog(self)
        result = dialog.exec_()
        
        # 如果用户选择了应用模板，则应用它
        if result == dialog.Accepted:
            template_data = dialog.get_selected_template()
            if template_data:
                self._apply_template_data(template_data)

    def _apply_template_data(self, template_data: Dict[str, Any]):
        """
        应用模板数据到当前流程
        
        Args:
            template_data: 模板数据
        """
        # 如果当前流程不为空，询问用户是否替换
        current_steps = self._flow_controller.get_steps()
        if current_steps:
            reply = QMessageBox.question(
                self, "替换确认",
                "当前流程不为空，应用模板将替换现有流程。是否继续？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.No:
                return
        
        # 从模板数据中获取模板ID和分类ID
        template_id = template_data.get("id")
        category_id = template_data.get("category")
        
        if not template_id or not category_id:
            QMessageBox.warning(self, "数据错误", "模板数据不完整")
            return
        
        # 创建模板管理器
        template_manager = TemplateManager()
        
        # 加载完整模板数据
        success, result = template_manager.load_template(template_id, category_id)
        
        if not success:
            QMessageBox.warning(self, "加载失败", f"加载模板失败: {result}")
            return
        
        # 获取模板的步骤数据
        template_steps = result.get("steps", [])
        
        # 显示模板详情对话框，以配置参数
        detail_dialog = TemplateDetailDialog(result, self, template_manager)
        detail_result = detail_dialog.exec_()
        
        if detail_result != detail_dialog.Accepted:
            return  # 用户取消了应用模板
        
        # 获取用户配置的参数值
        parameter_values = detail_dialog.get_parameter_values()
        
        # 应用参数到模板步骤
        processed_template = template_manager.apply_template_parameters(result, parameter_values)
        template_steps = processed_template.get("steps", [])
        
        # 创建新流程
        self._flow_controller.create_new_flow(result.get("template_name", "未命名模板"))
        
        # 添加模板步骤
        for step in template_steps:
            action_id = step.get("action_id", "")
            parameters = step.get("parameters", {})
            self._flow_controller.add_step(action_id, parameters)
        
        # 更新UI
        self._unsaved_changes = True
        self.flow_view_widget.update_view(self._flow_controller.get_steps())
        self._update_window_title()
        
        self.log_display_widget.add_success(f"已应用模板: {result.get('template_name')}")
        self.statusBar.showMessage(f"已应用模板: {result.get('template_name')}")

    def _handle_export_to_python(self):
        """处理导出为Python脚本操作"""
        # 如果流程为空，提示用户
        steps = self._flow_controller.get_steps()
        if not steps:
            QMessageBox.warning(self, "空流程", "当前流程为空，无法导出为Python脚本")
            return
        
        # 获取导出文件路径
        flow_name = self._flow_controller.get_flow_name()
        file_name = f"{flow_name.replace(' ', '_')}.py" if flow_name else "drission_script.py"
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出为Python脚本", file_name, "Python文件 (*.py);;所有文件 (*.*)"
        )
        
        if not file_path:
            return  # 用户取消了操作
        
        # 确保文件扩展名正确
        if not file_path.endswith(".py"):
            file_path += ".py"
        
        # 准备流程数据
        flow_data = {
            "flow_name": flow_name,
            "steps": steps
        }
        
        # 导出为Python脚本
        from drission_gui_tool.core.project_manager import ProjectManager
        success, message = ProjectManager.export_to_script(file_path, flow_data)
        
        if success:
            QMessageBox.information(self, "导出成功", message)
            self.log_display_widget.add_success(message)
        else:
            QMessageBox.warning(self, "导出失败", message)
            self.log_display_widget.add_error(message)
    
    def _handle_export_advanced_python(self):
        """处理导出为高级Python脚本操作"""
        # 如果流程为空，提示用户
        steps = self._flow_controller.get_steps()
        if not steps:
            QMessageBox.warning(self, "空流程", "当前流程为空，无法导出为Python脚本")
            return
        
        # 选择代码风格
        code_styles = ["标准风格", "精简风格", "详细风格", "生产环境风格"]
        selected_style, ok = QInputDialog.getItem(
            self, "选择代码风格", "请选择导出代码的风格:", code_styles, 0, False
        )
        
        if not ok:
            return  # 用户取消了操作
        
        # 映射代码风格
        style_map = {
            "标准风格": "standard",
            "精简风格": "compact",
            "详细风格": "verbose",
            "生产环境风格": "production"
        }
        code_style = style_map.get(selected_style, "standard")
        
        # 获取导出文件路径
        flow_name = self._flow_controller.get_flow_name()
        file_name = f"{flow_name.replace(' ', '_')}.py" if flow_name else "drission_script.py"
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出为Python脚本", file_name, "Python文件 (*.py);;所有文件 (*.*)"
        )
        
        if not file_path:
            return  # 用户取消了操作
        
        # 确保文件扩展名正确
        if not file_path.endswith(".py"):
            file_path += ".py"
        
        # 准备流程数据
        flow_data = {
            "flow_name": flow_name,
            "steps": steps,
            "description": f"DrissionPage自动化脚本 - {flow_name}",
            "created_at": time.time()
        }
        
        # 使用高级代码生成器导出
        from drission_gui_tool.core.advanced_code_generator import AdvancedCodeGenerator
        code_generator = AdvancedCodeGenerator()
        success, result = code_generator.generate_code(flow_data, file_path, code_style)
        
        if success:
            QMessageBox.information(self, "导出成功", f"高级Python脚本已成功导出到: {file_path}")
            self.log_display_widget.add_success(f"高级Python脚本已成功导出到: {file_path}")
        else:
            QMessageBox.warning(self, "导出失败", f"导出失败: {result}")
            self.log_display_widget.add_error(f"导出失败: {result}")
    
    def _handle_export_python_package(self):
        """处理导出为Python包操作"""
        # 如果流程为空，提示用户
        steps = self._flow_controller.get_steps()
        if not steps:
            QMessageBox.warning(self, "空流程", "当前流程为空，无法导出为Python包")
            return
        
        # 获取导出目录
        export_dir = QFileDialog.getExistingDirectory(
            self, "选择导出目录", "", QFileDialog.ShowDirsOnly
        )
        
        if not export_dir:
            return  # 用户取消了操作
        
        # 准备流程数据
        flow_name = self._flow_controller.get_flow_name()
        flow_data = {
            "flow_name": flow_name,
            "steps": steps,
            "description": f"DrissionPage自动化脚本 - {flow_name}",
            "created_at": time.time()
        }
        
        # 显示选项对话框
        options_dialog = QDialog(self)
        options_dialog.setWindowTitle("导出选项")
        options_layout = QVBoxLayout(options_dialog)
        
        # 添加选项
        include_readme_checkbox = QCheckBox("包含README文档")
        include_readme_checkbox.setChecked(True)
        options_layout.addWidget(include_readme_checkbox)
        
        include_requirements_checkbox = QCheckBox("包含requirements.txt")
        include_requirements_checkbox.setChecked(True)
        options_layout.addWidget(include_requirements_checkbox)
        
        include_config_checkbox = QCheckBox("包含配置文件")
        include_config_checkbox.setChecked(True)
        options_layout.addWidget(include_config_checkbox)
        
        # 代码风格选择
        style_layout = QHBoxLayout()
        style_label = QLabel("代码风格:")
        style_combo = QComboBox()
        style_combo.addItems(["标准风格", "详细风格", "生产环境风格"])
        style_combo.setCurrentIndex(2)  # 默认生产环境风格
        
        style_layout.addWidget(style_label)
        style_layout.addWidget(style_combo)
        options_layout.addLayout(style_layout)
        
        # 按钮
        buttons_layout = QHBoxLayout()
        cancel_button = QPushButton("取消")
        export_button = QPushButton("导出")
        export_button.setDefault(True)
        
        cancel_button.clicked.connect(options_dialog.reject)
        export_button.clicked.connect(options_dialog.accept)
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(cancel_button)
        buttons_layout.addWidget(export_button)
        
        options_layout.addStretch()
        options_layout.addLayout(buttons_layout)
        
        # 显示对话框
        if options_dialog.exec_() != QDialog.Accepted:
            return
        
        # 获取选项
        include_readme = include_readme_checkbox.isChecked()
        include_requirements = include_requirements_checkbox.isChecked()
        include_config = include_config_checkbox.isChecked()
        
        # 映射代码风格
        style_map = {
            0: "standard",  # 标准风格
            1: "verbose",   # 详细风格
            2: "production" # 生产环境风格
        }
        code_style = style_map.get(style_combo.currentIndex(), "production")
        
        # 使用高级代码生成器导出为包
        from drission_gui_tool.core.advanced_code_generator import AdvancedCodeGenerator
        code_generator = AdvancedCodeGenerator()
        
        # 显示进度对话框
        progress_dialog = QMessageBox(self)
        progress_dialog.setWindowTitle("导出中")
        progress_dialog.setText("正在导出Python包，请稍候...")
        progress_dialog.setStandardButtons(QMessageBox.NoButton)
        progress_dialog.show()
        QApplication.processEvents()
        
        try:
            success, message = code_generator.export_to_package(
                flow_data, export_dir,
                include_readme=include_readme,
                include_requirements=include_requirements,
                include_config=include_config,
                code_style=code_style
            )
            
            # 关闭进度对话框
            progress_dialog.close()
            
            if success:
                QMessageBox.information(self, "导出成功", f"Python包已成功导出到: {message}")
                self.log_display_widget.add_success(f"Python包已成功导出到: {message}")
            else:
                QMessageBox.warning(self, "导出失败", f"导出失败: {message}")
                self.log_display_widget.add_error(f"导出失败: {message}")
                
        except Exception as e:
            progress_dialog.close()
            QMessageBox.critical(self, "导出错误", f"导出过程中发生错误: {str(e)}")
            self.log_display_widget.add_error(f"导出错误: {str(e)}")

    def _handle_generate_documentation(self):
        """处理生成文档操作"""
        # 如果流程为空，提示用户
        steps = self._flow_controller.get_steps()
        if not steps:
            QMessageBox.warning(self, "空流程", "当前流程为空，无法生成文档")
            return
        
        # 获取导出文件路径
        flow_name = self._flow_controller.get_flow_name()
        file_name = f"{flow_name.replace(' ', '_')}_文档.md" if flow_name else "drission_script_文档.md"
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出文档", file_name, "Markdown文件 (*.md);;所有文件 (*.*)"
        )
        
        if not file_path:
            return  # 用户取消了操作
        
        # 确保文件扩展名正确
        if not file_path.endswith(".md"):
            file_path += ".md"
        
        # 准备流程数据
        flow_data = {
            "flow_name": flow_name,
            "steps": steps,
            "description": f"DrissionPage自动化脚本 - {flow_name}",
            "created_at": time.time()
        }
        
        # 使用高级代码生成器生成文档
        from drission_gui_tool.core.advanced_code_generator import AdvancedCodeGenerator
        code_generator = AdvancedCodeGenerator()
        
        try:
            # 生成README文档
            readme_content = code_generator._generate_readme(flow_data)
            
            # 生成步骤描述
            steps_doc = ["## 流程步骤\n"]
            for i, step in enumerate(steps):
                action_id = step.get("action_id", "未知操作")
                params = step.get("parameters", {})
                step_name = params.get("__custom_step_name__", action_id)
                steps_doc.append(f"### 步骤 {i+1}: {step_name}\n")
                steps_doc.append(f"- 操作类型: {action_id}\n")
                
                # 添加参数描述
                if params:
                    steps_doc.append("- 参数:\n")
                    for key, value in params.items():
                        if key != "__custom_step_name__":  # 跳过自定义名称
                            steps_doc.append(f"  - {key}: {value}\n")
                
                steps_doc.append("\n")
            
            # 合并文档内容
            doc_content = readme_content + "\n\n" + "".join(steps_doc)
            
            # 写入文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(doc_content)
            
            QMessageBox.information(self, "导出成功", f"文档已成功导出到: {file_path}")
            self.log_display_widget.add_success(f"文档已成功导出到: {file_path}")
            
        except Exception as e:
            QMessageBox.critical(self, "导出错误", f"文档生成过程中发生错误: {str(e)}")
            self.log_display_widget.add_error(f"导出错误: {str(e)}")
