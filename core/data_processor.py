#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
数据处理器模块，提供数据转换、清洗、验证和模板处理功能。
"""

import re
import json
import csv
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Union, Tuple, Optional, Callable
from datetime import datetime


class DataProcessor:
    """
    数据处理器，提供数据转换、清洗、验证和模板功能。
    """
    
    @staticmethod
    def apply_template(data: Dict[str, Any], template: str) -> str:
        """
        使用数据字典应用模板
        
        Args:
            data: 数据字典
            template: 包含占位符的模板字符串，例如"用户名: {username}, 年龄: {age}"
            
        Returns:
            替换后的字符串
        """
        result = template
        
        # 使用正则表达式查找 {key} 或 {key|filter} 格式的占位符
        pattern = r'{([^{}|]+)(?:\|([^{}]+))?}'
        
        # 查找所有匹配项
        matches = re.findall(pattern, template)
        
        for match in matches:
            key = match[0].strip()
            filters = match[1].strip() if len(match) > 1 and match[1] else None
            
            # 获取数据值
            value = data.get(key)
            
            # 如果有过滤器，应用过滤器
            if filters and value is not None:
                filter_parts = filters.split('|')
                for filter_part in filter_parts:
                    filter_name = filter_part.strip()
                    
                    # 应用过滤器
                    if filter_name == 'upper':
                        value = str(value).upper()
                    elif filter_name == 'lower':
                        value = str(value).lower()
                    elif filter_name == 'capitalize':
                        value = str(value).capitalize()
                    elif filter_name == 'title':
                        value = str(value).title()
                    elif filter_name.startswith('default:'):
                        default_value = filter_name.split(':', 1)[1]
                        if value is None or value == '':
                            value = default_value
                    elif filter_name.startswith('date:'):
                        date_format = filter_name.split(':', 1)[1]
                        if isinstance(value, (datetime, str, int, float)):
                            try:
                                if isinstance(value, str):
                                    # 尝试解析日期字符串
                                    value = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
                                elif isinstance(value, (int, float)):
                                    # 尝试解析时间戳
                                    value = datetime.fromtimestamp(value)
                                
                                # 格式化日期
                                value = value.strftime(date_format)
                            except Exception:
                                value = f"无效的日期格式: {value}"
                    elif filter_name.startswith('slice:'):
                        slice_params = filter_name.split(':', 1)[1]
                        try:
                            params = slice_params.split(',')
                            if len(params) == 1:
                                end = int(params[0])
                                value = str(value)[:end]
                            elif len(params) == 2:
                                start, end = int(params[0]), int(params[1])
                                value = str(value)[start:end]
                        except Exception:
                            value = f"无效的切片参数: {slice_params}"
            
            # 替换占位符
            placeholder = f"{{{key}}}" if not filters else f"{{{key}|{filters}}}"
            result = result.replace(placeholder, str(value) if value is not None else '')
            
        return result
    
    @staticmethod
    def clean_data(data: Dict[str, Any], cleaning_rules: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """
        根据清洗规则清洗数据
        
        Args:
            data: 数据字典
            cleaning_rules: 清洗规则，格式为 {"字段名": [{"type": "规则类型", ...规则参数}]}
            
        Returns:
            清洗后的数据字典
        """
        result = data.copy()
        
        for field, rules in cleaning_rules.items():
            if field in result:
                value = result[field]
                
                for rule in rules:
                    rule_type = rule.get("type", "").lower()
                    
                    # 字符串处理规则
                    if isinstance(value, str):
                        if rule_type == "trim":
                            value = value.strip()
                        elif rule_type == "replace":
                            from_str = rule.get("from", "")
                            to_str = rule.get("to", "")
                            value = value.replace(from_str, to_str)
                        elif rule_type == "uppercase":
                            value = value.upper()
                        elif rule_type == "lowercase":
                            value = value.lower()
                        elif rule_type == "capitalize":
                            value = value.capitalize()
                        elif rule_type == "regex_replace":
                            import re
                            pattern = rule.get("pattern", "")
                            replacement = rule.get("replacement", "")
                            if pattern:
                                try:
                                    value = re.sub(pattern, replacement, value)
                                except Exception:
                                    pass
                    
                    # 类型转换规则
                    if rule_type == "cast":
                        cast_type = rule.get("to", "")
                        try:
                            if cast_type == "int":
                                value = int(float(value))
                            elif cast_type == "float":
                                value = float(value)
                            elif cast_type == "str":
                                value = str(value)
                            elif cast_type == "bool":
                                if isinstance(value, str):
                                    value = value.lower() in ("true", "1", "yes", "y")
                                else:
                                    value = bool(value)
                        except Exception:
                            pass
                    
                    # 默认值规则
                    elif rule_type == "default":
                        if value is None or (isinstance(value, str) and not value):
                            value = rule.get("value")
                
                # 更新字段值
                result[field] = value
        
        return result
    
    @staticmethod
    def validate_data(data: Dict[str, Any], validation_rules: Dict[str, List[Dict[str, Any]]]) -> Tuple[bool, List[str]]:
        """
        根据验证规则验证数据
        
        Args:
            data: 数据字典
            validation_rules: 验证规则，格式为 {"字段名": [{"type": "规则类型", ...规则参数}]}
            
        Returns:
            (是否验证通过, 错误消息列表)
        """
        errors = []
        
        for field, rules in validation_rules.items():
            value = data.get(field)
            
            for rule in rules:
                rule_type = rule.get("type", "").lower()
                error_message = rule.get("message", f"{field} 验证失败")
                
                # 必填规则
                if rule_type == "required":
                    if value is None or (isinstance(value, str) and not value.strip()):
                        errors.append(error_message)
                        break  # 如果必填验证失败，不再继续验证该字段的其他规则
                
                # 如果值为空且不是必填，则跳过其他验证
                if value is None or (isinstance(value, str) and not value.strip()):
                    continue
                
                # 字符串长度规则
                if isinstance(value, str):
                    if rule_type == "min_length":
                        min_length = rule.get("value", 0)
                        if len(value) < min_length:
                            errors.append(error_message)
                    
                    elif rule_type == "max_length":
                        max_length = rule.get("value", float("inf"))
                        if len(value) > max_length:
                            errors.append(error_message)
                    
                    elif rule_type == "regex":
                        import re
                        pattern = rule.get("pattern", "")
                        if pattern:
                            try:
                                if not re.match(pattern, value):
                                    errors.append(error_message)
                            except Exception:
                                errors.append(error_message)
                
                # 数值范围规则
                if isinstance(value, (int, float)):
                    if rule_type == "min":
                        min_value = rule.get("value", float("-inf"))
                        if value < min_value:
                            errors.append(error_message)
                    
                    elif rule_type == "max":
                        max_value = rule.get("value", float("inf"))
                        if value > max_value:
                            errors.append(error_message)
                    
                    elif rule_type == "range":
                        min_value = rule.get("min", float("-inf"))
                        max_value = rule.get("max", float("inf"))
                        if value < min_value or value > max_value:
                            errors.append(error_message)
                
                # 枚举验证规则
                if rule_type == "enum":
                    allowed_values = rule.get("values", [])
                    if value not in allowed_values:
                        errors.append(error_message)
                
                # 类型验证规则
                elif rule_type == "type":
                    expected_type = rule.get("value", "")
                    valid = False
                    
                    if expected_type == "string" and isinstance(value, str):
                        valid = True
                    elif expected_type == "number" and isinstance(value, (int, float)):
                        valid = True
                    elif expected_type == "integer" and isinstance(value, int):
                        valid = True
                    elif expected_type == "boolean" and isinstance(value, bool):
                        valid = True
                    elif expected_type == "object" and isinstance(value, dict):
                        valid = True
                    elif expected_type == "array" and isinstance(value, list):
                        valid = True
                    
                    if not valid:
                        errors.append(error_message)
                
                # 自定义验证规则
                elif rule_type == "custom":
                    expression = rule.get("expression", "")
                    if expression:
                        try:
                            # 构建安全的本地环境
                            local_vars = {
                                "value": value,
                                "data": data
                            }
                            
                            # 执行表达式
                            if not eval(expression, {"__builtins__": {}}, local_vars):
                                errors.append(error_message)
                        except Exception:
                            errors.append(error_message)
        
        return len(errors) == 0, errors
    
    @staticmethod
    def batch_process(data_list: List[Dict[str, Any]], 
                      template: Optional[str] = None, 
                      cleaning_rules: Optional[Dict[str, List[Dict[str, Any]]]] = None,
                      validation_rules: Optional[Dict[str, List[Dict[str, Any]]]] = None) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[str]]:
        """
        批量处理数据列表
        
        Args:
            data_list: 数据字典列表
            template: 可选，使用的模板字符串
            cleaning_rules: 可选，清洗规则
            validation_rules: 可选，验证规则
            
        Returns:
            (处理后的合法数据列表, 处理后的非法数据列表, 错误消息列表)
        """
        processed_valid = []
        processed_invalid = []
        all_errors = []
        
        for index, item in enumerate(data_list):
            # 深拷贝数据项
            processed_item = item.copy()
            
            # 应用清洗规则
            if cleaning_rules:
                processed_item = DataProcessor.clean_data(processed_item, cleaning_rules)
            
            # 验证数据
            is_valid = True
            item_errors = []
            
            if validation_rules:
                is_valid, item_errors = DataProcessor.validate_data(processed_item, validation_rules)
                
                if not is_valid:
                    all_errors.append(f"第 {index + 1} 条数据验证失败: {'; '.join(item_errors)}")
            
            # 处理模板
            if template:
                processed_item["_formatted"] = DataProcessor.apply_template(processed_item, template)
            
            # 根据验证结果分类
            if is_valid:
                processed_valid.append(processed_item)
            else:
                processed_invalid.append(processed_item)
        
        return processed_valid, processed_invalid, all_errors
    
    @staticmethod
    def export_to_csv(data: List[Dict[str, Any]], file_path: str, encoding: str = "utf-8") -> Tuple[bool, str]:
        """
        将数据导出为CSV文件
        
        Args:
            data: 数据列表
            file_path: 导出文件路径
            encoding: 文件编码
            
        Returns:
            (是否成功, 消息)
        """
        try:
            import csv
            import os
            
            if not data:
                return False, "数据为空，无法导出"
            
            # 确保目录存在
            directory = os.path.dirname(file_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
            
            # 获取所有字段
            all_fields = set()
            for item in data:
                all_fields.update(item.keys())
            
            fieldnames = sorted(list(all_fields))
            
            # 写入CSV文件
            with open(file_path, "w", newline="", encoding=encoding) as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
            
            return True, f"成功导出 {len(data)} 条数据到 {file_path}"
        
        except Exception as e:
            return False, f"导出CSV失败: {str(e)}"
    
    @staticmethod
    def export_to_excel(data: List[Dict[str, Any]], file_path: str) -> Tuple[bool, str]:
        """
        将数据导出为Excel文件
        
        Args:
            data: 数据列表
            file_path: 导出文件路径
            
        Returns:
            (是否成功, 消息)
        """
        try:
            import pandas as pd
            import os
            
            if not data:
                return False, "数据为空，无法导出"
            
            # 确保目录存在
            directory = os.path.dirname(file_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
            
            # 将数据转换为DataFrame
            df = pd.DataFrame(data)
            
            # 写入Excel文件
            with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
                df.to_excel(writer, index=False, sheet_name="数据")
            
            return True, f"成功导出 {len(data)} 条数据到 {file_path}"
        
        except ImportError:
            return False, "缺少必要的库，请安装 pandas 和 openpyxl: pip install pandas openpyxl"
        except Exception as e:
            return False, f"导出Excel失败: {str(e)}"
    
    @staticmethod
    def generate_stats(data: List[Dict[str, Any]], fields: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        生成数据统计信息
        
        Args:
            data: 数据列表
            fields: 字段列表
            
        Returns:
            统计结果字典
        """
        try:
            import numpy as np
            from collections import Counter
        except ImportError:
            # 如果没有numpy，使用内置函数代替
            np = None
        
        if not data or not fields:
            return {}
        
        stats = {}
        
        for field in fields:
            # 提取字段值
            values = [item.get(field) for item in data if field in item]
            
            if not values:
                continue
            
            # 初始化字段统计
            field_stats = {
                "count": len(values),
                "missing": len(data) - len(values),
                "missing_percent": round((len(data) - len(values)) / len(data) * 100, 2) if data else 0
            }
            
            # 数值类型统计
            numeric_values = [v for v in values if isinstance(v, (int, float)) and not isinstance(v, bool)]
            
            if numeric_values:
                if np:
                    field_stats.update({
                        "min": np.min(numeric_values),
                        "max": np.max(numeric_values),
                        "mean": round(np.mean(numeric_values), 2),
                        "median": round(np.median(numeric_values), 2),
                        "std": round(np.std(numeric_values), 2) if len(numeric_values) > 1 else 0
                    })
                else:
                    numeric_values.sort()
                    n = len(numeric_values)
                    field_stats.update({
                        "min": min(numeric_values),
                        "max": max(numeric_values),
                        "mean": round(sum(numeric_values) / n, 2),
                        "median": numeric_values[n // 2] if n % 2 == 1 else (numeric_values[n // 2 - 1] + numeric_values[n // 2]) / 2,
                    })
            
            # 字符串类型统计
            string_values = [v for v in values if isinstance(v, str)]
            
            if string_values:
                # 字符串长度统计
                lengths = [len(v) for v in string_values]
                
                if np:
                    field_stats.update({
                        "min_length": min(lengths) if lengths else 0,
                        "max_length": max(lengths) if lengths else 0,
                        "mean_length": round(np.mean(lengths), 2) if lengths else 0
                    })
                else:
                    field_stats.update({
                        "min_length": min(lengths) if lengths else 0,
                        "max_length": max(lengths) if lengths else 0,
                        "mean_length": round(sum(lengths) / len(lengths), 2) if lengths else 0
                    })
                
                # 最常见的值
                counter = Counter(string_values)
                most_common = counter.most_common(5)
                field_stats["most_common"] = most_common
            
            # 布尔类型统计
            bool_values = [v for v in values if isinstance(v, bool)]
            
            if bool_values:
                true_count = sum(1 for v in bool_values if v)
                field_stats.update({
                    "true_count": true_count,
                    "false_count": len(bool_values) - true_count,
                    "true_percent": round(true_count / len(bool_values) * 100, 2) if bool_values else 0
                })
            
            # 保存字段统计
            stats[field] = field_stats
        
        return stats 