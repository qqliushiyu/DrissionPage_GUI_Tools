#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
数据库管理器模块，提供多种数据库连接和操作功能。
"""

import json
import logging
from typing import Dict, List, Any, Union, Tuple, Optional, Callable

# 数据库连接器类
class DatabaseConnector:
    """
    数据库连接器基类，定义通用接口
    """
    def __init__(self, connection_params: Dict[str, Any]):
        """
        初始化连接器
        
        Args:
            connection_params: 连接参数字典
        """
        self.connection_params = connection_params
        self.connection = None
        self.is_connected = False
    
    def connect(self) -> Tuple[bool, str]:
        """
        建立数据库连接
        
        Returns:
            (是否成功, 消息)
        """
        raise NotImplementedError("子类必须实现此方法")
    
    def disconnect(self) -> None:
        """关闭数据库连接"""
        raise NotImplementedError("子类必须实现此方法")
    
    def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> Tuple[bool, Union[List[Dict[str, Any]], str]]:
        """
        执行查询操作
        
        Args:
            query: SQL查询语句
            params: 查询参数
            
        Returns:
            (是否成功, 结果列表或错误消息)
        """
        raise NotImplementedError("子类必须实现此方法")
    
    def execute_update(self, query: str, params: Optional[Dict[str, Any]] = None) -> Tuple[bool, Union[int, str]]:
        """
        执行更新操作
        
        Args:
            query: SQL更新语句
            params: 更新参数
            
        Returns:
            (是否成功, 受影响行数或错误消息)
        """
        raise NotImplementedError("子类必须实现此方法")
    
    def test_connection(self) -> Tuple[bool, str]:
        """
        测试数据库连接
        
        Returns:
            (是否成功, 消息)
        """
        try:
            success, _ = self.connect()
            if success:
                self.disconnect()
                return True, "连接测试成功"
            else:
                return False, "连接测试失败"
        except Exception as e:
            return False, f"连接测试失败: {str(e)}"


# MySQL连接器
class MySQLConnector(DatabaseConnector):
    """MySQL数据库连接器"""
    
    def connect(self) -> Tuple[bool, str]:
        """建立MySQL连接"""
        try:
            import mysql.connector
            
            # 获取连接参数
            host = self.connection_params.get("host", "localhost")
            port = self.connection_params.get("port", 3306)
            user = self.connection_params.get("user", "root")
            password = self.connection_params.get("password", "")
            database = self.connection_params.get("database", "")
            
            # 建立连接
            self.connection = mysql.connector.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                database=database
            )
            
            self.is_connected = self.connection.is_connected()
            
            if self.is_connected:
                return True, "已成功连接到MySQL数据库"
            else:
                return False, "无法连接到MySQL数据库"
                
        except ImportError:
            return False, "缺少MySQL连接器库，请安装: pip install mysql-connector-python"
        except Exception as e:
            return False, f"连接MySQL失败: {str(e)}"
    
    def disconnect(self) -> None:
        """关闭MySQL连接"""
        if self.connection and self.is_connected:
            self.connection.close()
            self.is_connected = False
    
    def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> Tuple[bool, Union[List[Dict[str, Any]], str]]:
        """执行MySQL查询"""
        try:
            if not self.is_connected:
                success, message = self.connect()
                if not success:
                    return False, message
            
            cursor = self.connection.cursor(dictionary=True)
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            results = cursor.fetchall()
            cursor.close()
            
            return True, results
            
        except Exception as e:
            return False, f"执行查询失败: {str(e)}"
    
    def execute_update(self, query: str, params: Optional[Dict[str, Any]] = None) -> Tuple[bool, Union[int, str]]:
        """执行MySQL更新"""
        try:
            if not self.is_connected:
                success, message = self.connect()
                if not success:
                    return False, message
            
            cursor = self.connection.cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            self.connection.commit()
            affected_rows = cursor.rowcount
            cursor.close()
            
            return True, affected_rows
            
        except Exception as e:
            return False, f"执行更新失败: {str(e)}"


# SQLite连接器
class SQLiteConnector(DatabaseConnector):
    """SQLite数据库连接器"""
    
    def connect(self) -> Tuple[bool, str]:
        """建立SQLite连接"""
        try:
            import sqlite3
            
            # 获取连接参数
            database_path = self.connection_params.get("database_path", ":memory:")
            
            # 建立连接
            self.connection = sqlite3.connect(database_path)
            # 设置行工厂，返回字典格式结果
            self.connection.row_factory = sqlite3.Row
            
            self.is_connected = True
            return True, "已成功连接到SQLite数据库"
                
        except ImportError:
            return False, "缺少SQLite库，请检查Python安装"
        except Exception as e:
            return False, f"连接SQLite失败: {str(e)}"
    
    def disconnect(self) -> None:
        """关闭SQLite连接"""
        if self.connection:
            self.connection.close()
            self.is_connected = False
    
    def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> Tuple[bool, Union[List[Dict[str, Any]], str]]:
        """执行SQLite查询"""
        try:
            if not self.is_connected:
                success, message = self.connect()
                if not success:
                    return False, message
            
            cursor = self.connection.cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            # 获取查询结果
            rows = cursor.fetchall()
            results = []
            
            for row in rows:
                # 将Row对象转换为字典
                item = {key: row[key] for key in row.keys()}
                results.append(item)
                
            cursor.close()
            
            return True, results
            
        except Exception as e:
            return False, f"执行查询失败: {str(e)}"
    
    def execute_update(self, query: str, params: Optional[Dict[str, Any]] = None) -> Tuple[bool, Union[int, str]]:
        """执行SQLite更新"""
        try:
            if not self.is_connected:
                success, message = self.connect()
                if not success:
                    return False, message
            
            cursor = self.connection.cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            self.connection.commit()
            affected_rows = cursor.rowcount
            cursor.close()
            
            return True, affected_rows
            
        except Exception as e:
            return False, f"执行更新失败: {str(e)}"


# PostgreSQL连接器
class PostgreSQLConnector(DatabaseConnector):
    """PostgreSQL数据库连接器"""
    
    def connect(self) -> Tuple[bool, str]:
        """建立PostgreSQL连接"""
        try:
            import psycopg2
            import psycopg2.extras
            
            # 获取连接参数
            host = self.connection_params.get("host", "localhost")
            port = self.connection_params.get("port", 5432)
            user = self.connection_params.get("user", "postgres")
            password = self.connection_params.get("password", "")
            database = self.connection_params.get("database", "")
            
            # 建立连接
            self.connection = psycopg2.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                dbname=database
            )
            
            self.is_connected = True
            return True, "已成功连接到PostgreSQL数据库"
                
        except ImportError:
            return False, "缺少PostgreSQL连接器库，请安装: pip install psycopg2-binary"
        except Exception as e:
            return False, f"连接PostgreSQL失败: {str(e)}"
    
    def disconnect(self) -> None:
        """关闭PostgreSQL连接"""
        if self.connection:
            self.connection.close()
            self.is_connected = False
    
    def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> Tuple[bool, Union[List[Dict[str, Any]], str]]:
        """执行PostgreSQL查询"""
        try:
            if not self.is_connected:
                success, message = self.connect()
                if not success:
                    return False, message
            
            # 使用DictCursor获取字典格式结果
            cursor = self.connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            results = [dict(row) for row in cursor.fetchall()]
            cursor.close()
            
            return True, results
            
        except Exception as e:
            return False, f"执行查询失败: {str(e)}"
    
    def execute_update(self, query: str, params: Optional[Dict[str, Any]] = None) -> Tuple[bool, Union[int, str]]:
        """执行PostgreSQL更新"""
        try:
            if not self.is_connected:
                success, message = self.connect()
                if not success:
                    return False, message
            
            cursor = self.connection.cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            self.connection.commit()
            affected_rows = cursor.rowcount
            cursor.close()
            
            return True, affected_rows
            
        except Exception as e:
            return False, f"执行更新失败: {str(e)}"


# MongoDB连接器
class MongoDBConnector(DatabaseConnector):
    """MongoDB数据库连接器"""
    
    def connect(self) -> Tuple[bool, str]:
        """建立MongoDB连接"""
        try:
            import pymongo
            
            # 获取连接参数
            host = self.connection_params.get("host", "localhost")
            port = self.connection_params.get("port", 27017)
            user = self.connection_params.get("user", "")
            password = self.connection_params.get("password", "")
            database = self.connection_params.get("database", "")
            auth_source = self.connection_params.get("auth_source", "admin")
            
            # 构建连接URI
            uri = f"mongodb://"
            if user and password:
                uri += f"{user}:{password}@"
            uri += f"{host}:{port}/{database}"
            if auth_source:
                uri += f"?authSource={auth_source}"
            
            # 建立连接
            self.client = pymongo.MongoClient(uri)
            self.db = self.client[database] if database else None
            
            # 验证连接
            self.client.server_info()
            self.is_connected = True
            
            return True, "已成功连接到MongoDB数据库"
                
        except ImportError:
            return False, "缺少MongoDB连接器库，请安装: pip install pymongo"
        except Exception as e:
            return False, f"连接MongoDB失败: {str(e)}"
    
    def disconnect(self) -> None:
        """关闭MongoDB连接"""
        if hasattr(self, 'client'):
            self.client.close()
            self.is_connected = False
    
    def execute_query(self, collection_name: str, query: Dict[str, Any], projection: Optional[Dict[str, Any]] = None, 
                     limit: int = 0, skip: int = 0, sort: Optional[List[Tuple[str, int]]] = None) -> Tuple[bool, Union[List[Dict[str, Any]], str]]:
        """
        执行MongoDB查询
        
        Args:
            collection_name: 集合名称
            query: 查询条件
            projection: 字段投影
            limit: 结果限制数量
            skip: 跳过的文档数量
            sort: 排序字段和方向
            
        Returns:
            (是否成功, 结果列表或错误消息)
        """
        try:
            if not self.is_connected:
                success, message = self.connect()
                if not success:
                    return False, message
            
            if not self.db:
                return False, "未指定数据库"
            
            collection = self.db[collection_name]
            
            # 转换查询条件为MongoDB格式（如果是字符串）
            if isinstance(query, str):
                try:
                    query = json.loads(query)
                except Exception:
                    return False, "查询条件必须是有效的JSON格式"
            
            # 转换投影条件为MongoDB格式（如果是字符串）
            if isinstance(projection, str):
                try:
                    projection = json.loads(projection)
                except Exception:
                    return False, "投影条件必须是有效的JSON格式"
            
            # 构建查询
            cursor = collection.find(query, projection)
            
            # 应用分页
            if skip > 0:
                cursor = cursor.skip(skip)
            if limit > 0:
                cursor = cursor.limit(limit)
            
            # 应用排序
            if sort:
                cursor = cursor.sort(sort)
            
            # 获取结果
            results = list(cursor)
            
            # 转换ObjectId为字符串，使其可JSON序列化
            for doc in results:
                if '_id' in doc and hasattr(doc['_id'], '__str__'):
                    doc['_id'] = str(doc['_id'])
            
            return True, results
            
        except Exception as e:
            return False, f"执行查询失败: {str(e)}"
    
    def execute_update(self, collection_name: str, filter_query: Dict[str, Any], 
                      update_data: Dict[str, Any], upsert: bool = False) -> Tuple[bool, Union[int, str]]:
        """
        执行MongoDB更新
        
        Args:
            collection_name: 集合名称
            filter_query: 筛选条件
            update_data: 更新数据
            upsert: 是否插入不存在的文档
            
        Returns:
            (是否成功, 受影响文档数或错误消息)
        """
        try:
            if not self.is_connected:
                success, message = self.connect()
                if not success:
                    return False, message
            
            if not self.db:
                return False, "未指定数据库"
            
            collection = self.db[collection_name]
            
            # 转换查询条件为MongoDB格式（如果是字符串）
            if isinstance(filter_query, str):
                try:
                    filter_query = json.loads(filter_query)
                except Exception:
                    return False, "筛选条件必须是有效的JSON格式"
            
            # 转换更新数据为MongoDB格式（如果是字符串）
            if isinstance(update_data, str):
                try:
                    update_data = json.loads(update_data)
                except Exception:
                    return False, "更新数据必须是有效的JSON格式"
            
            # 确保更新数据包含操作符
            if not any(key.startswith('$') for key in update_data.keys()):
                update_data = {'$set': update_data}
            
            # 执行更新
            result = collection.update_many(filter_query, update_data, upsert=upsert)
            
            return True, result.modified_count
            
        except Exception as e:
            return False, f"执行更新失败: {str(e)}"


# SQL查询构建器
class SQLQueryBuilder:
    """SQL查询构建器，提供简单的SQL查询构建功能"""
    
    @staticmethod
    def select(table: str, fields: List[str] = None, where: Dict[str, Any] = None, 
              order_by: List[str] = None, limit: int = None, offset: int = None) -> str:
        """
        构建SELECT查询
        
        Args:
            table: 表名
            fields: 要查询的字段列表，None表示所有字段
            where: 条件字典
            order_by: 排序字段列表，格式如 ["name ASC", "id DESC"]
            limit: 限制结果数量
            offset: 结果偏移量
            
        Returns:
            SQL查询字符串
        """
        # 构建SELECT部分
        field_str = "*"
        if fields:
            field_str = ", ".join(fields)
        
        query = f"SELECT {field_str} FROM {table}"
        
        # 构建WHERE部分
        if where:
            conditions = []
            for field, value in where.items():
                if value is None:
                    conditions.append(f"{field} IS NULL")
                else:
                    conditions.append(f"{field} = %s")
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
        
        # 构建ORDER BY部分
        if order_by:
            query += " ORDER BY " + ", ".join(order_by)
        
        # 构建LIMIT和OFFSET部分
        if limit is not None:
            query += f" LIMIT {limit}"
            
            if offset is not None:
                query += f" OFFSET {offset}"
                
        return query
    
    @staticmethod
    def insert(table: str, data: Dict[str, Any]) -> str:
        """
        构建INSERT查询
        
        Args:
            table: 表名
            data: 要插入的数据字典
            
        Returns:
            SQL查询字符串
        """
        fields = list(data.keys())
        placeholders = ["%s"] * len(fields)
        
        query = f"INSERT INTO {table} ({', '.join(fields)}) VALUES ({', '.join(placeholders)})"
        
        return query
    
    @staticmethod
    def update(table: str, data: Dict[str, Any], where: Dict[str, Any]) -> str:
        """
        构建UPDATE查询
        
        Args:
            table: 表名
            data: 要更新的数据字典
            where: 条件字典
            
        Returns:
            SQL查询字符串
        """
        # 构建SET部分
        set_parts = []
        for field in data.keys():
            set_parts.append(f"{field} = %s")
        
        query = f"UPDATE {table} SET {', '.join(set_parts)}"
        
        # 构建WHERE部分
        if where:
            conditions = []
            for field, value in where.items():
                if value is None:
                    conditions.append(f"{field} IS NULL")
                else:
                    conditions.append(f"{field} = %s")
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
        
        return query
    
    @staticmethod
    def delete(table: str, where: Dict[str, Any]) -> str:
        """
        构建DELETE查询
        
        Args:
            table: 表名
            where: 条件字典
            
        Returns:
            SQL查询字符串
        """
        query = f"DELETE FROM {table}"
        
        # 构建WHERE部分
        if where:
            conditions = []
            for field, value in where.items():
                if value is None:
                    conditions.append(f"{field} IS NULL")
                else:
                    conditions.append(f"{field} = %s")
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
        
        return query


# 数据库管理器
class DatabaseManager:
    """
    数据库管理器，集成多种数据库连接和操作功能
    """
    
    def __init__(self):
        """初始化数据库管理器"""
        self.connectors = {}
        self.query_builder = SQLQueryBuilder()
        self.logger = logging.getLogger("DatabaseManager")
    
    def add_connection(self, connection_id: str, db_type: str, connection_params: Dict[str, Any]) -> Tuple[bool, str]:
        """
        添加数据库连接
        
        Args:
            connection_id: 连接标识
            db_type: 数据库类型，支持 "mysql", "sqlite", "postgres", "mongodb"
            connection_params: 连接参数
            
        Returns:
            (是否成功, 消息)
        """
        try:
            # 创建连接器
            if db_type.lower() == "mysql":
                connector = MySQLConnector(connection_params)
            elif db_type.lower() == "sqlite":
                connector = SQLiteConnector(connection_params)
            elif db_type.lower() in ("postgres", "postgresql"):
                connector = PostgreSQLConnector(connection_params)
            elif db_type.lower() == "mongodb":
                connector = MongoDBConnector(connection_params)
            else:
                return False, f"不支持的数据库类型: {db_type}"
            
            # 测试连接
            success, message = connector.test_connection()
            if not success:
                return False, message
            
            # 保存连接器
            self.connectors[connection_id] = {
                "type": db_type.lower(),
                "connector": connector,
                "params": connection_params
            }
            
            return True, f"已成功添加 {db_type} 连接: {connection_id}"
            
        except Exception as e:
            return False, f"添加数据库连接失败: {str(e)}"
    
    def remove_connection(self, connection_id: str) -> Tuple[bool, str]:
        """
        移除数据库连接
        
        Args:
            connection_id: 连接标识
            
        Returns:
            (是否成功, 消息)
        """
        if connection_id not in self.connectors:
            return False, f"找不到连接: {connection_id}"
        
        try:
            # 关闭连接
            self.connectors[connection_id]["connector"].disconnect()
            
            # 移除连接
            del self.connectors[connection_id]
            
            return True, f"已移除连接: {connection_id}"
            
        except Exception as e:
            return False, f"移除连接失败: {str(e)}"
    
    def get_connections(self) -> Dict[str, Dict[str, Any]]:
        """
        获取所有连接信息
        
        Returns:
            连接信息字典
        """
        connections = {}
        
        for conn_id, conn_info in self.connectors.items():
            connections[conn_id] = {
                "type": conn_info["type"],
                "params": {
                    k: v for k, v in conn_info["params"].items() if k != "password"
                },
                "is_connected": conn_info["connector"].is_connected
            }
        
        return connections
    
    def execute_query(self, connection_id: str, query: str, params: Optional[Dict[str, Any]] = None) -> Tuple[bool, Union[List[Dict[str, Any]], str]]:
        """
        执行SQL查询
        
        Args:
            connection_id: 连接标识
            query: SQL查询语句
            params: 查询参数
            
        Returns:
            (是否成功, 结果列表或错误消息)
        """
        if connection_id not in self.connectors:
            return False, f"找不到连接: {connection_id}"
        
        conn_info = self.connectors[connection_id]
        connector = conn_info["connector"]
        
        # MongoDB需要特殊处理
        if conn_info["type"] == "mongodb":
            try:
                # 解析参数
                if isinstance(query, str):
                    try:
                        query_params = json.loads(query)
                    except:
                        return False, "MongoDB查询必须是有效的JSON格式"
                else:
                    query_params = query
                
                collection = query_params.get("collection", "")
                filter_query = query_params.get("query", {})
                projection = query_params.get("projection", None)
                limit = query_params.get("limit", 0)
                skip = query_params.get("skip", 0)
                sort = query_params.get("sort", None)
                
                return connector.execute_query(collection, filter_query, projection, limit, skip, sort)
            except Exception as e:
                return False, f"执行MongoDB查询失败: {str(e)}"
        else:
            # SQL数据库
            return connector.execute_query(query, params)
    
    def execute_update(self, connection_id: str, query: str, params: Optional[Dict[str, Any]] = None) -> Tuple[bool, Union[int, str]]:
        """
        执行SQL更新
        
        Args:
            connection_id: 连接标识
            query: SQL更新语句
            params: 更新参数
            
        Returns:
            (是否成功, 受影响行数或错误消息)
        """
        if connection_id not in self.connectors:
            return False, f"找不到连接: {connection_id}"
        
        conn_info = self.connectors[connection_id]
        connector = conn_info["connector"]
        
        # MongoDB需要特殊处理
        if conn_info["type"] == "mongodb":
            try:
                # 解析参数
                if isinstance(query, str):
                    try:
                        query_params = json.loads(query)
                    except:
                        return False, "MongoDB更新必须是有效的JSON格式"
                else:
                    query_params = query
                
                collection = query_params.get("collection", "")
                filter_query = query_params.get("filter", {})
                update_data = query_params.get("update", {})
                upsert = query_params.get("upsert", False)
                
                return connector.execute_update(collection, filter_query, update_data, upsert)
            except Exception as e:
                return False, f"执行MongoDB更新失败: {str(e)}"
        else:
            # SQL数据库
            return connector.execute_update(query, params)
    
    def build_select_query(self, table: str, fields: List[str] = None, where: Dict[str, Any] = None, 
                         order_by: List[str] = None, limit: int = None, offset: int = None) -> str:
        """构建SELECT查询"""
        return self.query_builder.select(table, fields, where, order_by, limit, offset)
    
    def build_insert_query(self, table: str, data: Dict[str, Any]) -> str:
        """构建INSERT查询"""
        return self.query_builder.insert(table, data)
    
    def build_update_query(self, table: str, data: Dict[str, Any], where: Dict[str, Any]) -> str:
        """构建UPDATE查询"""
        return self.query_builder.update(table, data, where)
    
    def build_delete_query(self, table: str, where: Dict[str, Any]) -> str:
        """构建DELETE查询"""
        return self.query_builder.delete(table, where) 