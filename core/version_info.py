#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
版本信息模块
"""

VERSION = "1.1.0"

CHANGELOG = {
    "1.1.0": [
        "新增流程调试器功能，包括断点设置、单步执行和变量监视",
        "新增执行状态可视化和性能监控",
        "新增详细的执行日志记录和导出功能",
        "支持条件断点、错误断点和变量断点",
        "优化了多线程执行和异常处理机制"
    ],
    "1.0.0": [
        "初始版本",
        "基本流程编辑和执行功能",
        "支持变量管理和条件控制",
        "内置多种示例流程"
    ]
}

def get_version():
    """获取当前版本号"""
    return VERSION

def get_version_info():
    """获取当前版本详细信息"""
    return {
        "version": VERSION,
        "changes": CHANGELOG.get(VERSION, [])
    }

def get_full_changelog():
    """获取完整的变更日志"""
    return CHANGELOG 