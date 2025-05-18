# Widget for configuring parameters of a selected action 
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QSpinBox, 
    QCheckBox, QComboBox, QPushButton, QFormLayout, QGroupBox,
    QScrollArea, QTextEdit # For potentially many parameters
)
from PyQt5.QtCore import pyqtSignal, Qt
from typing import List, Dict, Any, Optional

class ParameterPanel(QWidget):
    """
    A widget that dynamically displays input fields for configuring
    parameters of a selected action. Emits a signal when parameters are submitted.
    """
    # Signal: action_id (str), parameters (Dict[str, Any])
    parameters_submitted = pyqtSignal(str, dict)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._current_action_id: Optional[str] = None
        self._parameter_widgets: Dict[str, QWidget] = {} # To store a reference to input widgets
        self._init_ui()

    def _init_ui(self) -> None:
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setAlignment(Qt.AlignTop)

        self.group_box = QGroupBox("参数配置")
        self.main_layout.addWidget(self.group_box)

        # Use QScrollArea in case of many parameters
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True) # Important for the layout within scroll area
        self.scroll_content_widget = QWidget() # Widget to hold the form_layout
        self.form_layout = QFormLayout(self.scroll_content_widget)
        self.scroll_area.setWidget(self.scroll_content_widget)
        
        layout_for_groupbox = QVBoxLayout(self.group_box) # Layout for the group box
        layout_for_groupbox.addWidget(self.scroll_area)

        self.submit_button = QPushButton("添加到流程")
        self.submit_button.clicked.connect(self._on_submit_clicked)
        self.submit_button.setEnabled(False) # Disabled until an action is selected
        layout_for_groupbox.addWidget(self.submit_button)

        self.setLayout(self.main_layout) # Set main_layout to the ParameterPanel itself

    def display_action_parameters(self, action_id: str, parameter_schema: List[Dict[str, Any]], current_params: Optional[Dict[str, Any]] = None) -> None:
        """
        Clears existing parameter fields and creates new ones based on the
        provided action_id and parameter_schema.

        Args:
            action_id: The unique ID of the selected action.
            parameter_schema: A list of dictionaries, each defining a parameter.
            current_params: Optional dictionary of current values (for editing an existing step).
        """
        self._current_action_id = action_id
        self._parameter_widgets.clear()

        # Clear previous widgets from form_layout
        while self.form_layout.count():
            child = self.form_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        if not parameter_schema:
            self.form_layout.addRow(QLabel("此操作无需配置参数。"))
            self.submit_button.setText("添加到流程 (无参数)")
            self.submit_button.setEnabled(True)
            self.group_box.setTitle(f"参数配置: {action_id}")
            return

        self.group_box.setTitle(f"参数配置: {action_id}")

        for param_def in parameter_schema:
            name = param_def.get("name")
            label_text = param_def.get("label", name)
            param_type = param_def.get("type", "string")
            default_value = param_def.get("default_value")
            tooltip = param_def.get("tooltip", "")

            # Use current_params if provided (for editing), otherwise default_value
            value_to_set = default_value
            if current_params and name in current_params:
                value_to_set = current_params[name]
            
            label = QLabel(label_text)
            if tooltip:
                label.setToolTip(tooltip)

            input_widget: Optional[QWidget] = None

            if param_type == "string":
                widget = QLineEdit()
                if value_to_set is not None: widget.setText(str(value_to_set))
                input_widget = widget
            elif param_type == "int":
                widget = QSpinBox()
                widget.setRange(-999999, 999999) # Example range
                if value_to_set is not None: widget.setValue(int(value_to_set))
                input_widget = widget
            elif param_type == "bool":
                widget = QCheckBox()
                if value_to_set is not None: widget.setChecked(bool(value_to_set))
                input_widget = widget
            elif param_type == "dropdown":
                widget = QComboBox()
                options = param_def.get("options", [])
                widget.addItems(options)
                if value_to_set is not None and value_to_set in options:
                    widget.setCurrentText(str(value_to_set))
                input_widget = widget
            elif param_type == "multiline":  # 添加对多行文本输入的支持
                widget = QTextEdit()
                if value_to_set is not None: 
                    widget.setText(str(value_to_set))
                widget.setMinimumHeight(150)  # 设置最小高度
                input_widget = widget
            # Add more types as needed (e.g., "css_selector", "xpath_selector" might just be strings for now)
            else: # Default to string if type is unknown
                widget = QLineEdit()
                if value_to_set is not None: widget.setText(str(value_to_set))
                input_widget = widget
                print(f"ParameterPanel: Unknown param type '{param_type}' for '{name}', using QLineEdit.")

            if input_widget:
                if tooltip: input_widget.setToolTip(tooltip)
                self.form_layout.addRow(label, input_widget)
                self._parameter_widgets[name] = input_widget
        
        # Update submit button text based on whether we are editing
        if current_params is not None:
            self.submit_button.setText("更新步骤")
        else:
            self.submit_button.setText("添加到流程")
        self.submit_button.setEnabled(True)

    def _on_submit_clicked(self) -> None:
        """
        Collects parameter values from input fields and emits the
        parameters_submitted signal.
        """
        if not self._current_action_id:
            return

        collected_params: Dict[str, Any] = {}
        for name, widget in self._parameter_widgets.items():
            if isinstance(widget, QLineEdit):
                collected_params[name] = widget.text()
            elif isinstance(widget, QTextEdit):  # 处理多行文本输入
                collected_params[name] = widget.toPlainText()
            elif isinstance(widget, QSpinBox):
                collected_params[name] = widget.value()
            elif isinstance(widget, QCheckBox):
                collected_params[name] = widget.isChecked()
            elif isinstance(widget, QComboBox):
                collected_params[name] = widget.currentText()
            # Add more widget types if necessary
        
        self.parameters_submitted.emit(self._current_action_id, collected_params)
        print(f"ParameterPanel: Submitted action '{self._current_action_id}' with params: {collected_params}")

    def clear_panel(self) -> None:
        """Clears the panel and resets it to an initial state."""
        self._current_action_id = None
        self._parameter_widgets.clear()
        while self.form_layout.count():
            child = self.form_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        self.group_box.setTitle("参数配置")
        self.submit_button.setText("添加到流程")
        self.submit_button.setEnabled(False)


if __name__ == '__main__': # For testing this widget directly
    from PyQt5.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    panel = ParameterPanel()

    # Example schema for testing
    test_action_id = "PAGE_GET"
    test_schema = [
        {"name": "url", "label": "目标网址:", "type": "string", "default_value": "https://www.google.com"},
        {"name": "timeout", "label": "超时(秒):", "type": "int", "default_value": 20, "tooltip": "加载超时"},
        {"name": "use_proxy", "label": "使用代理:", "type": "bool", "default_value": True},
        {"name": "mode", "label": "模式:", "type": "dropdown", "options": ["fast", "normal", "slow"], "default_value": "normal"},
    ]
    panel.display_action_parameters(test_action_id, test_schema)

    def on_params_submitted_test(action_id, params):
        print(f"Test: Parameters submitted for '{action_id}': {params}")

    panel.parameters_submitted.connect(on_params_submitted_test)
    panel.setWindowTitle("Test Parameter Panel")
    panel.show()
    sys.exit(app.exec_())
