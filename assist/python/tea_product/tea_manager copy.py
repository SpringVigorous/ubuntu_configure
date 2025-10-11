import mysql.connector
from mysql.connector import Error,pooling
from typing import Optional, Dict, List, Tuple
import os

from contextlib import contextmanager
from datetime import datetime



import sys

from pathlib import Path








from base import logger_helper,UpdateTimeType,except_stack

"""系统特点
​​完整的CRUD操作​​：所有核心表都有增删改查功能
​​撤销/回滚支持​​：通过操作栈记录所有变更，支持撤销
​​名称-ID转换​​：提供多种辅助函数帮助前端表单填写
​​事务安全​​：所有操作都使用事务确保数据一致性
​​类型提示​​：使用Python类型提示提高代码可读性
​​批量操作支持​​：支持批量入库和配方管理
这个增强版系统可以很好地支持茶包产品的库存管理需求，特别是前端表单填写和操作撤销功能，大大提高了系统的易用性和可靠性。


Returns:
    _type_: _description_
"""
# 1. 数据库连接与基础类
class TeaInventorySystem:
    def __init__(self, host: str, database: str, user: str, password: str,port: int = 3306,  # 添加端口参数，默认3306
                pool_size: int = 5):
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.operation_stack = []  # 用于撤销操作的栈
        self.port = port  # 存储端口参数
        self.pool_size = pool_size
        
        self.logger=logger_helper("数据中心","茶饮数据库")
        
        try:
            self.pool = mysql.connector.pooling.MySQLConnectionPool(
                pool_name="tea_pool",
                pool_size=self.pool_size,
                host=self.host,
                port=self.port,  # 使用端口参数
                database=self.database,
                user=self.user,
                password=self.password,
                pool_reset_session=True
            )
            # 验证连接池
            self._test_pool()
        except Error as e:
            self.logger.error("异常",f"连接池初始化失败: {except_stack()}")
            raise
        self._initialize_database()

    def _test_pool(self):
        """测试连接池是否可用"""
        conn = None
        try:
            conn = self.pool.get_connection()
            conn.ping(reconnect=True)
        finally:
            if conn and conn.is_connected():
                conn.close()

    @contextmanager
    def _get_connection(self):
        """安全获取数据库连接"""
        conn = None
        try:
            conn = self.pool.get_connection()
            if conn is None:
                raise Error("无法从连接池获取连接(可能已耗尽)")
                
            if not conn.is_connected():
                conn.reconnect(attempts=3, delay=0.5)
                
            yield conn
        except Error as e:
            self.logger.error("异常",f"数据库连接错误:  {except_stack()}")
            raise
        finally:
            if conn is not None:
                try:
                    if hasattr(conn, 'is_connected') and conn.is_connected():
                        conn.close()
                except Exception as e:
                     self.logger.error("异常",f"关闭连接时出错::  {except_stack()}")
        
    #数据库操作模版函数
    def def_operate_func(self, body_fun,error_content:str):
        """添加新药材"""
        with self._get_connection() as conn:
            if not conn:
                return None
                
            try:
                cursor = conn.cursor()
                val=body_fun(cursor)
                conn.commit()
                return val
            except Error as e:
                conn.rollback()
                self.logger.warn("失败",f"{error_content}失败:  {except_stack()}")
                return None
            finally:
                if conn.is_connected():
                    cursor.close()
                    conn.close()
        

    def _create_tables_from_sql_file(self):
        """从SQL文件创建表结构"""
        sql_file_path = os.path.join(
            os.path.dirname(__file__), 
            'schema', 
            'medical_tab.sql'
        )
        
        with open(sql_file_path, 'r', encoding='utf-8-sig') as file:
            sql_script = file.read()
        
        # 分割并过滤SQL命令
        commands = [cmd.strip() for cmd in sql_script.split(';') if cmd.strip()]
        
        
        with self._get_connection() as conn:
            if not conn:
                return None
            try:
                
                cursor = conn.cursor()
                for cmd in commands:
                    cursor.execute(cmd)
                conn.commit()
                
            except FileNotFoundError:
                self.logger.error("异常",f"错误: SQL文件不存在 - {sql_file_path}")
                raise
            except Error as e:
                conn.rollback()
                self.logger.error("异常",f"执行建表语句失败:  {except_stack()}")
                raise
            finally:
                if cursor:
                    cursor.close()

    def _initialize_database(self):
        """初始化数据库和表结构"""
        with self._get_connection() as conn:
            try:
            
                cursor = conn.cursor()
                # 创建数据库
                cursor.execute("CREATE DATABASE IF NOT EXISTS medical_product")
                conn.database = 'medical_product'
                # 从文件创建表
                self._create_tables_from_sql_file()
                self.logger.info("成功","数据库初始化完成")
                
            except Error as e:
                self.logger.error("异常",f"数据库初始化失败:  {except_stack()}")
                raise
            finally:
                if cursor:
                    cursor.close()
# 2. 增删改查(CRUD)功能

    # ---- 药材管理 ----
    def add_herb_func(self, name: str , specification: str = "",scientific_name: str = "", 
                unit: str = "g", quality_standard: str = "高级",is_active:int=1,is_default:int =0,shelf_life:int=365) -> Optional[int]:
        """添加新药材"""
        
        def body_fun(cursor):
            if not scientific_name:
                scientific_name = name
                self.logger.warn("警告",f"未输入学名，使用通用名({name})作为学名")
            cursor.execute(
                "INSERT INTO herbs (herb_name, scientific_name, specification, unit, quality_standard ,is_active,is_default,shelf_life) "
                "VALUES (%s, %s, %s, %s, %s)",
                (name, scientific_name, specification, unit, quality_standard,is_active,is_default,shelf_life)
            )
            return  cursor.lastrowid
        return self.def_operate_func(body_fun,"添加药材")

    # ---- 药材管理 ----
    def add_herb(self, name: str , specification: str = "",scientific_name: str = "", 
                unit: str = "g", quality_standard: str = "高级",is_active:int=1,is_default:int =0,shelf_life:int=365) -> Optional[int]:
        """添加新药材"""
        with self._get_connection() as conn:
            if not conn:
                return None
                
            try:
                cursor = conn.cursor()
                if not scientific_name:
                    scientific_name = name
                    self.logger.warn("警告",f"未输入学名，使用通用名({name})作为学名")
                cursor.execute(
                    "INSERT INTO herbs (herb_name, scientific_name, specification, unit, quality_standard ,is_active,is_default,shelf_life) "
                    "VALUES (%s, %s, %s, %s, %s)",
                    (name, scientific_name, specification, unit, quality_standard,is_active,is_default,shelf_life)
                )
                herb_id = cursor.lastrowid
                conn.commit()
                return herb_id
            except Error as e:
                conn.rollback()
                self.logger.warn("失败",f"添加药材失败:  {except_stack()}")
                return None
            finally:
                if conn.is_connected():
                    cursor.close()
                    conn.close()

            # ---- 药材管理 ----
    def add_herbs_batch(self, herbs: List[dict]) -> int:
        """批量添加药材"""
        with self._get_connection() as conn:
            if not conn:
                return 0
            cursor = None
            try:
                cursor = conn.cursor()
                params = []
                missing_sci_names = set()  # 记录未提供学名的药材名
                
                # 处理每条药材数据
                for herb in herbs:
                    # 校验必要字段
                    name = herb.get("name")
                    if not name:
                        continue  # 跳过无药材名的记录
                    
                    # 处理学名默认值
                    sci_name = herb.get("scientific_name", "")
                    if not sci_name:
                        sci_name = name
                        missing_sci_names.add(name)
                    
                    # 填充其他字段的默认值
                    spec = herb.get("specification", "")
                    unit = herb.get("unit", "g")
                    quality = herb.get("quality_standard", "高级")
                    is_active = herb.get("is_active", 1)
                    is_default = herb.get("is_default", 0)
                    shelf_life = herb.get("shelf_life", 365)
                    
                    # 添加参数列表
                    params.append((
                        name, sci_name, spec, unit, quality, 
                        is_active, is_default, shelf_life
                    ))
                
                # 无有效数据时直接返回
                if not params:
                    return 0
                
                # 统一提示未提供学名的记录
                if missing_sci_names:
                    names = "、".join(missing_sci_names)
                    self.logger.warn("警告", f"以下药材未输入学名，已自动填充通用名: {names}")
                
                # 执行批量插入
                cursor.executemany(
                    """
                    INSERT INTO herbs (
                        herb_name, scientific_name, specification, 
                        unit, quality_standard, is_active, is_default, shelf_life
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    params
                )
                conn.commit()
                return cursor.rowcount  # 返回成功插入的行数
            
            except Error as e:
                conn.rollback()
                self.logger.error("失败", f"批量插入药材失败: {e}\n{except_stack()}")
                return 0
            
            finally:
                if cursor and conn.is_connected():
                    cursor.close()
                    conn.close()
        
    def get_herb_id_by_name(self, name: str, specification: str = "") -> Optional[int]:
        """根据药材名称和规格获取ID"""
        with self._get_connection() as conn:
            if not conn:
                return None
                
            try:
                cursor = conn.cursor()
                query = "SELECT herb_id FROM herbs WHERE herb_name = %s"
                params = [name]
                
                if specification:
                    query += " AND specification = %s"
                    params.append(specification)
                    
                cursor.execute(query, params)
                result = cursor.fetchone()
                return result[0] if result else None
            except Error as e:
                self.logger.warn("失败",f"查询药材ID失败:  {except_stack()}")
                return None
            finally:
                if conn.is_connected():
                    cursor.close()
                    conn.close()

    def update_herb(self, herb_id: int, **kwargs) -> bool:
        """更新药材信息"""
        if not kwargs:
            return False
            
        with self._get_connection() as conn:
            if not conn:
                return False
                
            try:
                cursor = conn.cursor()
                set_clause = ", ".join([f"{k} = %s" for k in kwargs])
                query = f"UPDATE herbs SET {set_clause} WHERE herb_id = %s"
                params = list(kwargs.values()) + [herb_id]
                
                cursor.execute(query, params)
                conn.commit()
                return cursor.rowcount > 0
            except Error as e:
                conn.rollback()
                self.logger.warn("失败",f"更新药材失败:  {except_stack()}")
                return False
            finally:
                if conn.is_connected():
                    cursor.close()
                    conn.close()

    def delete_herb(self, herb_id: int) -> bool:
        """删除药材（逻辑删除）"""
        return self.update_herb(herb_id, is_active=False)

    # ---- 配方管理 ----
    def add_formula(self, name: str, code: str, total_weight: float, 
                   description: str = "") -> Optional[int]:
        """添加新配方"""
        with self._get_connection() as conn:
            if not conn:
                return None
                
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO tea_bag_formulas (formula_name, formula_code, total_weight, description) "
                    "VALUES (%s, %s, %s, %s)",
                    (name, code, total_weight, description)
                )
                formula_id = cursor.lastrowid
                conn.commit()
                return formula_id
            except Error as e:
                conn.rollback()
                self.logger.warn("失败",f"添加配方失败:  {except_stack()}")
                return None
            finally:
                if conn.is_connected():
                    cursor.close()
                    conn.close()

    def add_formula_component(self, formula_id: int, herb_id: int, 
                            weight: float, requirements: str = "") -> bool:
        """添加配方成分"""
        with self._get_connection() as conn:
            if not conn:
                return False
                
            try:
                cursor = conn.cursor()
                # 计算百分比
                cursor.execute(
                    "SELECT total_weight FROM tea_bag_formulas WHERE formula_id = %s", 
                    (formula_id,)
                )
                total_weight = cursor.fetchone()[0]
                percentage = (weight / total_weight) * 100
                
                cursor.execute(
                    "INSERT INTO formula_components (formula_id, herb_id, weight, percentage, processing_requirements) "
                    "VALUES (%s, %s, %s, %s, %s)",
                    (formula_id, herb_id, weight, percentage, requirements)
                )
                conn.commit()
                return True
            except Error as e:
                conn.rollback()
                self.logger.warn("失败",f"添加配方成分失败:  {except_stack()}")
                return False
            finally:
                if conn.is_connected():
                    cursor.close()
                    conn.close()

# 3. 撤销/回滚功能
    def _record_operation(self, operation_type: str, table: str, record_id: int, 
                        data_before: dict, data_after: dict) -> bool:
        """记录操作以便撤销"""
        self.operation_stack.append({
            'operation_type': operation_type,
            'table': table,
            'record_id': record_id,
            'data_before': data_before,
            'data_after': data_after,
            'timestamp': datetime.now()
        })
        return True

    def undo_last_operation(self) -> bool:
        """撤销最后一次操作"""
        if not self.operation_stack:
            return False
            
        last_op = self.operation_stack.pop()
        with self._get_connection() as conn:
            if not conn:
                return False
                
            try:
                cursor = conn.cursor()
                
                if last_op['operation_type'] == 'INSERT':
                    # 撤销插入操作 = 删除记录
                    cursor.execute(
                        f"DELETE FROM {last_op['table']} WHERE id = %s",
                        (last_op['record_id'],)
                    )
                elif last_op['operation_type'] == 'UPDATE':
                    # 撤销更新操作 = 恢复旧数据
                    set_clause = ", ".join([f"{k} = %s" for k in last_op['data_before']])
                    query = f"UPDATE {last_op['table']} SET {set_clause} WHERE id = %s"
                    params = list(last_op['data_before'].values()) + [last_op['record_id']]
                    cursor.execute(query, params)
                elif last_op['operation_type'] == 'DELETE':
                    # 撤销删除操作 = 重新插入记录
                    columns = ", ".join(last_op['data_before'].keys())
                    placeholders = ", ".join(["%s"] * len(last_op['data_before']))
                    cursor.execute(
                        f"INSERT INTO {last_op['table']} ({columns}) VALUES ({placeholders})",
                        list(last_op['data_before'].values())
                    )
                
                conn.commit()
                return True
            except Error as e:
                conn.rollback()
                self.logger.warn("失败",f"撤销操作失败:  {except_stack()}")
                return False
            finally:
                if conn.is_connected():
                    cursor.close()
                    conn.close()
# 4. 入库操作辅助功能
    # ---- 入库辅助功能 ----
    def get_all_herbs(self) -> List[Dict]:
        """获取所有药材信息（用于下拉选择）"""
        with self._get_connection() as conn:
            if not conn:
                return []
                
            try:
                cursor = conn.cursor(dictionary=True)
                cursor.execute(
                    "SELECT herb_id, herb_name, specification, unit FROM herbs WHERE is_active = TRUE"
                )
                return cursor.fetchall()
            except Error as e:
                self.logger.warn("失败",f"获取药材列表失败:  {except_stack()}")
                return []
            finally:
                if conn.is_connected():
                    cursor.close()
                    conn.close()

    def get_all_formulas(self) -> List[Dict]:
        """获取所有配方信息（用于下拉选择）"""
        with self._get_connection() as conn:
            if not conn:
                return []
                
            try:
                cursor = conn.cursor(dictionary=True)
                cursor.execute(
                    "SELECT formula_id, formula_name, formula_code FROM tea_bag_formulas WHERE is_active = TRUE"
                )
                return cursor.fetchall()
            except Error as e:
                self.logger.warn("失败",f"获取配方列表失败:  {except_stack()}")
                return []
            finally:
                if conn.is_connected():
                    cursor.close()
                    conn.close()

    def stock_in_herb(self, herb_id: int, quantity: float, batch_number: str, 
                     operator: str, production_date: str, expiry_date: str) -> bool:
        """药材入库"""
        with self._get_connection() as conn:
            if not conn:
                return False
                
            try:
                cursor = conn.cursor()
                
                # 记录操作前的库存状态（用于撤销）
                cursor.execute(
                    "SELECT quantity FROM herb_inventory WHERE herb_id = %s AND batch_number = %s",
                    (herb_id, batch_number)
                )
                existing = cursor.fetchone()
                old_quantity = existing[0] if existing else 0
                
                # 执行入库操作
                if existing:
                    cursor.execute(
                        "UPDATE herb_inventory SET quantity = quantity + %s "
                        "WHERE herb_id = %s AND batch_number = %s",
                        (quantity, herb_id, batch_number)
                    )
                else:
                    cursor.execute(
                        "INSERT INTO herb_inventory "
                        "(herb_id, batch_number, quantity, production_date, expiry_date) "
                        "VALUES (%s, %s, %s, %s, %s)",
                        (herb_id, batch_number, quantity, production_date, expiry_date)
                    )
                
                # 记录操作
                self._record_operation(
                    operation_type='INSERT' if not existing else 'UPDATE',
                    table='herb_inventory',
                    record_id=herb_id,
                    data_before={'quantity': old_quantity},
                    data_after={'quantity': old_quantity + quantity}
                )
                
                conn.commit()
                return True
            except Error as e:
                conn.rollback()
                self.logger.warn("失败",f"药材入库失败:  {except_stack()}")
                return False
            finally:
                if conn.is_connected():
                    cursor.close()
                    conn.close()







