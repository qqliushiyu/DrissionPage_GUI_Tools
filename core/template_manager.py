#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
模板管理器模块，负责流程模板的保存、加载、分类和参数化。
"""

import os
import json
import time
import shutil
from typing import Dict, List, Tuple, Any, Optional, Union

from common.constants import TEMPLATE_DIRECTORY, TEMPLATE_FILE_EXTENSION


class TemplateManager:
    """
    模板管理器类，提供模板的保存、加载和管理功能。
    """
    
    def __init__(self):
        """初始化模板管理器"""
        self._ensure_template_directory()
        self._categories = self._load_categories()
    
    def _ensure_template_directory(self) -> None:
        """确保模板目录存在"""
        if not os.path.exists(TEMPLATE_DIRECTORY):
            os.makedirs(TEMPLATE_DIRECTORY)
            
        # 确保分类目录存在
        categories_file = os.path.join(TEMPLATE_DIRECTORY, "categories.json")
        if not os.path.exists(categories_file):
            default_categories = {
                "login": "登录模板",
                "form": "表单操作",
                "scrape": "数据抓取",
                "navigation": "页面导航",
                "custom": "自定义模板"
            }
            with open(categories_file, 'w', encoding='utf-8') as f:
                json.dump(default_categories, f, ensure_ascii=False, indent=2)
    
    def _load_categories(self) -> Dict[str, str]:
        """加载模板分类"""
        categories_file = os.path.join(TEMPLATE_DIRECTORY, "categories.json")
        try:
            with open(categories_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {
                "login": "登录模板",
                "form": "表单操作",
                "scrape": "数据抓取",
                "navigation": "页面导航",
                "custom": "自定义模板"
            }
    
    def save_categories(self) -> None:
        """保存模板分类"""
        categories_file = os.path.join(TEMPLATE_DIRECTORY, "categories.json")
        with open(categories_file, 'w', encoding='utf-8') as f:
            json.dump(self._categories, f, ensure_ascii=False, indent=2)
    
    def get_categories(self) -> Dict[str, str]:
        """获取模板分类"""
        return self._categories.copy()
    
    def add_category(self, category_id: str, display_name: str) -> Tuple[bool, str]:
        """
        添加模板分类
        
        Args:
            category_id: 分类ID
            display_name: 显示名称
            
        Returns:
            (成功标志, 消息)
        """
        if category_id in self._categories:
            return False, f"分类ID '{category_id}' 已存在"
        
        self._categories[category_id] = display_name
        self.save_categories()
        
        # 创建分类目录
        category_dir = os.path.join(TEMPLATE_DIRECTORY, category_id)
        if not os.path.exists(category_dir):
            os.makedirs(category_dir)
        
        return True, f"已添加分类: {display_name}"
    
    def rename_category(self, category_id: str, new_display_name: str) -> Tuple[bool, str]:
        """
        重命名模板分类
        
        Args:
            category_id: 分类ID
            new_display_name: 新显示名称
            
        Returns:
            (成功标志, 消息)
        """
        if category_id not in self._categories:
            return False, f"分类ID '{category_id}' 不存在"
        
        self._categories[category_id] = new_display_name
        self.save_categories()
        return True, f"已重命名分类为: {new_display_name}"
    
    def delete_category(self, category_id: str) -> Tuple[bool, str]:
        """
        删除模板分类
        
        Args:
            category_id: 分类ID
            
        Returns:
            (成功标志, 消息)
        """
        if category_id not in self._categories:
            return False, f"分类ID '{category_id}' 不存在"
        
        # 获取分类目录中的模板数量
        category_dir = os.path.join(TEMPLATE_DIRECTORY, category_id)
        if os.path.exists(category_dir):
            templates = [f for f in os.listdir(category_dir) if f.endswith(TEMPLATE_FILE_EXTENSION)]
            if templates:
                return False, f"分类 '{self._categories[category_id]}' 包含 {len(templates)} 个模板，无法删除"
            
            # 删除空目录
            os.rmdir(category_dir)
        
        del self._categories[category_id]
        self.save_categories()
        return True, f"已删除分类: {category_id}"
    
    def get_templates_in_category(self, category_id: str) -> List[Dict[str, Any]]:
        """
        获取分类中的所有模板
        
        Args:
            category_id: 分类ID
            
        Returns:
            模板信息列表
        """
        result = []
        
        if category_id not in self._categories:
            return result
        
        category_dir = os.path.join(TEMPLATE_DIRECTORY, category_id)
        if not os.path.exists(category_dir):
            return result
        
        for file_name in os.listdir(category_dir):
            if file_name.endswith(TEMPLATE_FILE_EXTENSION):
                file_path = os.path.join(category_dir, file_name)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        template_data = json.load(f)
                    
                    # 提取模板信息
                    template_info = {
                        "id": file_name.replace(TEMPLATE_FILE_EXTENSION, ""),
                        "name": template_data.get("template_name", "未命名模板"),
                        "description": template_data.get("description", ""),
                        "category": category_id,
                        "parameters": template_data.get("parameters", []),
                        "created_at": template_data.get("created_at", 0),
                        "updated_at": template_data.get("updated_at", 0),
                        "file_path": file_path
                    }
                    result.append(template_info)
                except Exception:
                    # 忽略无效的模板文件
                    pass
        
        # 按更新时间排序
        result.sort(key=lambda x: x.get("updated_at", 0), reverse=True)
        return result
    
    def get_all_templates(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        获取所有模板，按分类组织
        
        Returns:
            按分类组织的模板字典
        """
        result = {}
        
        for category_id in self._categories:
            templates = self.get_templates_in_category(category_id)
            if templates:
                result[category_id] = templates
        
        return result
    
    def save_template(self, template_data: Dict[str, Any], category_id: str = "custom") -> Tuple[bool, str]:
        """
        保存模板
        
        Args:
            template_data: 模板数据
            category_id: 分类ID
            
        Returns:
            (成功标志, 消息或模板ID)
        """
        # 确保分类存在
        if category_id not in self._categories:
            category_id = "custom"  # 默认使用自定义分类
        
        # 确保模板包含必要字段
        if "template_name" not in template_data or "steps" not in template_data:
            return False, "无效的模板数据: 缺少必要字段"
        
        # 添加或更新时间戳
        template_data["created_at"] = template_data.get("created_at", time.time())
        template_data["updated_at"] = time.time()
        
        # 生成模板ID
        template_id = template_data.get("template_id", "")
        if not template_id:
            # 从模板名称生成ID
            template_name = template_data["template_name"]
            template_id = "".join(c.lower() for c in template_name if c.isalnum())
            
            # 确保ID唯一
            category_dir = os.path.join(TEMPLATE_DIRECTORY, category_id)
            if os.path.exists(os.path.join(category_dir, f"{template_id}{TEMPLATE_FILE_EXTENSION}")):
                template_id = f"{template_id}_{int(time.time())}"
            
            template_data["template_id"] = template_id
        
        # 确保分类目录存在
        category_dir = os.path.join(TEMPLATE_DIRECTORY, category_id)
        if not os.path.exists(category_dir):
            os.makedirs(category_dir)
        
        # 保存模板文件
        file_path = os.path.join(category_dir, f"{template_id}{TEMPLATE_FILE_EXTENSION}")
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(template_data, f, ensure_ascii=False, indent=2)
            
            return True, template_id
        except Exception as e:
            return False, f"保存模板失败: {str(e)}"
    
    def load_template(self, template_id: str, category_id: str) -> Tuple[bool, Union[Dict[str, Any], str]]:
        """
        加载模板
        
        Args:
            template_id: 模板ID
            category_id: 分类ID
            
        Returns:
            (成功标志, 模板数据或错误消息)
        """
        if category_id not in self._categories:
            return False, f"分类 '{category_id}' 不存在"
        
        file_path = os.path.join(TEMPLATE_DIRECTORY, category_id, f"{template_id}{TEMPLATE_FILE_EXTENSION}")
        
        if not os.path.exists(file_path):
            return False, f"模板文件不存在: {file_path}"
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                template_data = json.load(f)
            
            return True, template_data
        except json.JSONDecodeError:
            return False, f"无效的JSON格式: {file_path}"
        except Exception as e:
            return False, f"加载模板失败: {str(e)}"
    
    def delete_template(self, template_id: str, category_id: str) -> Tuple[bool, str]:
        """
        删除模板
        
        Args:
            template_id: 模板ID
            category_id: 分类ID
            
        Returns:
            (成功标志, 消息)
        """
        if category_id not in self._categories:
            return False, f"分类 '{category_id}' 不存在"
        
        file_path = os.path.join(TEMPLATE_DIRECTORY, category_id, f"{template_id}{TEMPLATE_FILE_EXTENSION}")
        
        if not os.path.exists(file_path):
            return False, f"模板文件不存在: {file_path}"
        
        try:
            os.remove(file_path)
            return True, f"已删除模板: {template_id}"
        except Exception as e:
            return False, f"删除模板失败: {str(e)}"
    
    def export_template(self, template_id: str, category_id: str, export_path: str) -> Tuple[bool, str]:
        """
        导出模板
        
        Args:
            template_id: 模板ID
            category_id: 分类ID
            export_path: 导出路径
            
        Returns:
            (成功标志, 消息)
        """
        # 加载模板
        success, result = self.load_template(template_id, category_id)
        if not success:
            return False, result
        
        template_data = result
        
        # 确保导出路径存在
        export_dir = os.path.dirname(export_path)
        if export_dir and not os.path.exists(export_dir):
            os.makedirs(export_dir)
        
        # 如果导出路径没有扩展名，添加扩展名
        if not export_path.endswith(TEMPLATE_FILE_EXTENSION):
            export_path += TEMPLATE_FILE_EXTENSION
        
        # 写入导出文件
        try:
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(template_data, f, ensure_ascii=False, indent=2)
            
            return True, f"模板已成功导出到: {export_path}"
        except Exception as e:
            return False, f"导出模板失败: {str(e)}"
    
    def import_template(self, import_path: str, category_id: str = "custom") -> Tuple[bool, str]:
        """
        导入模板
        
        Args:
            import_path: 导入路径
            category_id: 分类ID
            
        Returns:
            (成功标志, 消息或模板ID)
        """
        # 确保导入文件存在
        if not os.path.exists(import_path):
            return False, f"导入文件不存在: {import_path}"
        
        # 加载导入文件
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                template_data = json.load(f)
        except json.JSONDecodeError:
            return False, f"无效的JSON格式: {import_path}"
        except Exception as e:
            return False, f"加载导入文件失败: {str(e)}"
        
        # 验证模板数据
        if "template_name" not in template_data or "steps" not in template_data:
            return False, "无效的模板数据: 缺少必要字段"
        
        # 保存导入的模板
        return self.save_template(template_data, category_id)
    
    def apply_template_parameters(self, template_data: Dict[str, Any], 
                                parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        应用模板参数
        
        Args:
            template_data: 模板数据
            parameters: 参数值
            
        Returns:
            处理后的模板数据
        """
        # 创建新的模板数据副本
        processed_data = template_data.copy()
        
        # 如果模板不包含参数定义，则直接返回
        param_definitions = template_data.get("parameters", [])
        if not param_definitions:
            return processed_data
        
        # 处理步骤中的参数引用
        steps = processed_data.get("steps", [])
        for step in steps:
            step_params = step.get("parameters", {})
            
            # 遍历步骤的所有参数
            for param_key, param_value in step_params.items():
                if isinstance(param_value, str):
                    # 替换模板参数引用 {{param_name}}
                    for param_def in param_definitions:
                        param_name = param_def.get("name", "")
                        if not param_name:
                            continue
                        
                        # 获取参数值，如果未提供则使用默认值
                        param_value_to_use = parameters.get(param_name, param_def.get("default_value", ""))
                        
                        # 替换模板中的参数引用
                        placeholder = f"{{{{{param_name}}}}}"
                        step_params[param_key] = step_params[param_key].replace(placeholder, str(param_value_to_use))
        
        return processed_data 