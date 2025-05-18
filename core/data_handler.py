#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
数据处理模块，负责处理CSV、Excel等数据源的导入和管理。
"""

import os
import csv
import pandas as pd
from typing import List, Dict, Any, Tuple, Optional

class DataHandler:
    """
    数据处理器，用于从不同数据源导入数据。
    """
    
    @staticmethod
    def import_csv(file_path: str, encoding: str = 'utf-8') -> Tuple[bool, Any]:
        """
        从CSV文件导入数据
        
        Args:
            file_path: CSV文件路径
            encoding: 文件编码，默认为utf-8
            
        Returns:
            (是否成功, 数据或错误消息)
        """
        try:
            # 检查文件是否存在
            if not os.path.exists(file_path):
                return False, f"文件不存在: {file_path}"
            
            # 检查文件扩展名
            if not file_path.lower().endswith('.csv'):
                return False, "不是有效的CSV文件"
            
            # 读取CSV文件
            data = []
            with open(file_path, 'r', encoding=encoding, newline='') as f:
                reader = csv.DictReader(f)
                headers = reader.fieldnames
                
                if not headers:
                    return False, "CSV文件不包含有效的表头"
                
                for row in reader:
                    data.append(row)
                
            if not data:
                return False, "CSV文件不包含数据"
            
            return True, {
                "headers": headers,
                "data": data,
                "source": "csv",
                "file_path": file_path
            }
        
        except UnicodeDecodeError:
            return False, f"无法以 {encoding} 编码读取文件，请尝试不同的编码"
        
        except Exception as e:
            return False, f"导入CSV文件失败: {str(e)}"
    
    @staticmethod
    def import_excel(file_path: str, sheet_name: Optional[str] = None, sheet_index: int = 0) -> Tuple[bool, Any]:
        """
        从Excel文件导入数据
        
        Args:
            file_path: Excel文件路径
            sheet_name: 工作表名称，如果提供则优先使用
            sheet_index: 工作表索引，默认为0（第一个工作表）
            
        Returns:
            (是否成功, 数据或错误消息)
        """
        try:
            # 检查文件是否存在
            if not os.path.exists(file_path):
                return False, f"文件不存在: {file_path}"
            
            # 检查文件扩展名
            if not file_path.lower().endswith(('.xls', '.xlsx')):
                return False, "不是有效的Excel文件"
            
            # 读取Excel文件
            if sheet_name:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
            else:
                df = pd.read_excel(file_path, sheet_index=sheet_index)
            
            # 检查是否有数据
            if df.empty:
                return False, "Excel文件不包含数据"
            
            # 转换为字典列表
            headers = df.columns.tolist()
            data = df.to_dict('records')
            
            available_sheets = pd.ExcelFile(file_path).sheet_names
            
            return True, {
                "headers": headers,
                "data": data,
                "source": "excel",
                "file_path": file_path,
                "sheet_name": sheet_name or available_sheets[sheet_index],
                "available_sheets": available_sheets
            }
        
        except Exception as e:
            return False, f"导入Excel文件失败: {str(e)}"
    
    @staticmethod
    def get_data_preview(data_dict: Dict[str, Any], max_rows: int = 5) -> Dict[str, Any]:
        """
        获取数据预览
        
        Args:
            data_dict: 数据字典
            max_rows: 预览的最大行数
            
        Returns:
            预览数据字典
        """
        if not data_dict or "data" not in data_dict or "headers" not in data_dict:
            return {"error": "无效的数据格式"}
        
        preview_data = data_dict["data"][:max_rows]
        
        return {
            "headers": data_dict["headers"],
            "preview_data": preview_data,
            "total_rows": len(data_dict["data"]),
            "source": data_dict.get("source", "unknown")
        }
    
    @staticmethod
    def import_data_from_file(file_path: str) -> Tuple[bool, Any]:
        """
        根据文件类型自动选择导入方法
        
        Args:
            file_path: 文件路径
            
        Returns:
            (是否成功, 数据或错误消息)
        """
        file_extension = os.path.splitext(file_path)[1].lower()
        
        if file_extension == '.csv':
            return DataHandler.import_csv(file_path)
        
        elif file_extension in ('.xls', '.xlsx'):
            return DataHandler.import_excel(file_path)
        
        else:
            return False, f"不支持的文件类型: {file_extension}"
