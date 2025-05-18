# DrissionPage 自动化 GUI 工具

这是一个基于 PyQt5 和 DrissionPage 的自动化操作图形界面工具。本工具旨在让用户无需编写代码，即可通过可视化界面配置和执行基于 DrissionPage 的 Web 自动化操作。

## 主要功能

- **可视化流程编辑器**：拖拽式操作，直观构建自动化流程
- **内置常用自动化操作**：点击、输入、等待、截图等
- **动态变量支持**：变量定义、使用和管理
- **条件控制和循环**：支持分支逻辑和循环操作
- **代码导出功能**：可将流程导出为Python脚本或Python包
- **参数化执行**：支持运行时参数配置
- **日志和调试支持**：流程执行过程可视化和错误排查
- **模板系统**：常用流程的保存与重用

## 屏幕截图

_此处建议添加应用截图_

## 安装与使用

### 依赖项

- Python 3.8+
- DrissionPage 4.0.0+
- PyQt5 5.15.0+
- pandas (用于数据处理)
- openpyxl (Excel文件处理)
- Pillow (图像处理)

### 安装方式

#### 方法1：使用预编译的可执行程序

访问[Releases页面](#)下载最新的预编译版本，无需安装Python环境。

#### 方法2：从源码安装

```bash
# 克隆仓库
git clone https://github.com/yourusername/drission-gui-tool.git
cd drission-gui-tool

# 安装依赖
pip install -r requirements.txt
```

### 运行

从源码安装后，执行以下命令启动程序：

```bash
python run_gui_tool.py
```

## 快速入门指南

1. **创建新流程**：点击主界面上的"新建"按钮
2. **添加操作步骤**：从左侧操作面板拖拽操作到中间的流程编辑区
3. **配置操作参数**：在右侧参数面板设置各步骤的详细参数
4. **保存流程**：点击"保存"按钮将流程保存为.dgflow文件
5. **运行流程**：点击"执行"按钮开始运行自动化流程
6. **导出Python代码**：点击菜单"导出" > "导出为Python脚本"

## 自定义打包

本工具支持打包成独立的可执行程序，无需Python环境即可运行。

### 打包前准备

1. 安装打包工具：`pip install pyinstaller pillow`
2. 可选：准备应用图标（PNG格式，命名为app_icon.png）

### 打包方法

项目根目录下提供了多种打包脚本：

```bash
# 基本打包（推荐初次使用）
python build.py

# 高级打包（使用spec文件，提供更多控制）
python build_advanced.py

# 使用Nuitka打包（可能生成更小更快的可执行文件）
pip install nuitka
python build_with_nuitka.py
```

详细的打包说明请参阅[打包说明.md](打包说明.md)。

## 常见问题解答

### Q: 如何处理网页元素定位问题？
A: 工具支持多种定位方式，包括CSS选择器、XPath、ID等，可在元素操作的参数面板中选择合适的定位方式。

### Q: 流程中可以使用条件判断吗？
A: 可以，从"流程控制"面板中拖入"条件判断"操作，可以基于元素状态、变量值等设置条件。

### Q: 如何在不同步骤之间传递数据？
A: 使用变量功能，可在"变量管理器"中定义变量，然后在步骤参数中引用。

### Q: 如何解决"导出Python包"时卡住的问题？
A: 这是一个已知问题，导出可能需要较长时间。如果UI显示卡住，实际上导出过程可能已经完成，可以检查输出目录确认。也可以尝试使用"导出为Python脚本"功能作为替代。

### Q: 使用Nuitka打包时遇到lxml相关错误如何解决？
A: 这是Nuitka在处理lxml模块时的已知问题。解决方法：
1. 尝试使用更新版本的Nuitka（0.9.0+）
2. 使用`--include-module=lxml.etree`和`--include-module=lxml.sax`参数
3. 如果问题仍存在，建议改用PyInstaller打包：`python build.py`

## 项目结构

```
drission_gui_tool/         # 主程序包
├── core/                  # 核心功能模块
│   ├── code_generator.py  # 代码生成器
│   ├── project_manager.py # 项目管理器
│   └── ...
├── gui/                   # 图形界面相关代码
├── resources/             # 资源文件
└── utils/                 # 工具函数
run_gui_tool.py            # 程序入口
build.py                   # 基本打包脚本
build_advanced.py          # 高级打包脚本
build_with_nuitka.py       # Nuitka打包脚本
requirements.txt           # 依赖项
```

## 开发状态

该项目正在积极开发中，欢迎贡献代码和提出建议。

## 贡献指南

1. Fork本仓库
2. 创建你的特性分支：`git checkout -b feature/amazing-feature`
3. 提交你的更改：`git commit -m 'Add some amazing feature'`
4. 推送到分支：`git push origin feature/amazing-feature`
5. 创建一个Pull Request

## 许可证

此项目采用MIT许可证 - 详见LICENSE文件

## 联系方式

有问题或建议？请提交GitHub Issues或联系项目维护者。 