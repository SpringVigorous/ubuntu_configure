import mysql.connector
from mysql.connector import Error,pooling
from typing import Optional, Dict, List, Tuple
import os

from contextlib import contextmanager
from datetime import datetime



import sys

from pathlib import Path



root_path=Path(__file__).parent.parent.resolve()
sys.path.append(str(root_path ))
sys.path.append( os.path.join(root_path,'base') )


from base import logger_helper,UpdateTimeType,except_stack


from transact_tools import AutoCommitManager

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
                val=body_fun(conn)
                conn.commit()
                return val
            except Error as e:
                conn.rollback()
                self.logger.warn("失败",f"{error_content}失败:  {except_stack()}")
                return None
            finally:
                if conn.is_connected():
                    cursor = conn.cursor()
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
    def add_herb(self, name: str , specification: str = "",scientific_name: str = "", 
                unit: str = "g", quality_standard: str = "高级",is_active:int=1,is_default:int =0,shelf_life:int=365) -> Optional[int]:
        """添加新药材"""
        
        def body_fun(conn):
            cursor = conn.cursor()
            if not scientific_name:
                scientific_name = name
                self.logger.warn("警告",f"未输入学名，使用通用名({name})作为学名")
            cursor.execute(
                "INSERT INTO herbs (herb_name, scientific_name, specification, unit, quality_standard ,is_active,is_default,shelf_life) "
                "VALUES (%s, %s, %s, %s, %s)",
                (name, scientific_name, specification, unit, quality_standard,is_active,is_default,shelf_life)
            )
            conn.commit()
            return  cursor.lastrowid
        return self.def_operate_func(body_fun,"添加药材")


        # ---- 药材管理 ----
    def add_herbs_batch(self, herbs: List[dict]) -> int:
        def body_fun(conn):
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
        return self.def_operate_func(body_fun,"批量添加药材")
        
    def get_herb_id_by_name(self, name: str, specification: str = "") -> Optional[int]:
        """根据药材名称和规格获取ID"""
        def body_fun(conn):
            cursor = conn.cursor()
            query = "SELECT herb_id FROM herbs WHERE herb_name = %s"
            params = [name]
            
            if specification:
                query += " AND specification = %s"
                params.append(specification)
                
            cursor.execute(query, params)
            result = cursor.fetchone()
            return result[0] if result else None
        return self.def_operate_func(body_fun,"查询药材ID")

    def update_herb(self, herb_id: int, **kwargs) -> bool:
        """更新药材信息"""
        
        def body_fun(conn):
            cursor = conn.cursor()
        
            if not kwargs:
                return False
            set_clause = ", ".join([f"{k} = %s" for k in kwargs])
            query = f"UPDATE herbs SET {set_clause} WHERE herb_id = %s"
            params = list(kwargs.values()) + [herb_id]
            cursor.execute(query, params)
            conn.commit()
            return cursor.rowcount > 0

        return self.def_operate_func(body_fun,"更新药材")
    
    def delete_herb(self, herb_id: int) -> bool:
        """删除药材（逻辑删除）"""
        return self.update_herb(herb_id, is_active=False)
    def update_herbs_batch(self, updates: List[dict]) -> int:
        """批量更新药材信息（自动事务管理）"""
        def body_fun(conn):
            
            with AutoCommitManager(conn) as tm:
                cursor = conn.cursor()
                updated_count = 0
                for herb_update in updates:
                    herb_id = herb_update.get("herb_id")
                    if not herb_id:
                        continue
                    
                    fields = {k: v for k, v in herb_update.items() if k != "herb_id"}
                    if not fields:
                        continue
                    
                    set_clause = ", ".join([f"{k} = %s" for k in fields])
                    params = list(fields.values()) + [herb_id]
                    cursor.execute(
                        f"UPDATE herbs SET {set_clause} WHERE herb_id = %s", 
                        params
                    )
                    updated_count += cursor.rowcount
                
                return updated_count
                
            self.def_operate_func(body_fun,"批量更新药材") 
            
    def delete_herbs_batch(self, herb_ids: List[int]) -> int:
        """批量逻辑删除（自动事务管理）"""
        if not herb_ids:
            return 0
        def body_fun(conn):
            with AutoCommitManager(conn) as tm:
                cursor = conn.cursor()
                placeholders = ", ".join(["%s"] * len(herb_ids))
                cursor.execute(
                    f"UPDATE herbs SET is_active = FALSE WHERE herb_id IN ({placeholders})",
                    herb_ids
                )
                return cursor.rowcount
        self.def_operate_func(body_fun,"批量删除")        
                        


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
        def body_fun(conn):
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT herb_id, herb_name, specification, unit FROM herbs WHERE is_active = TRUE"
            )
            return cursor.fetchall()
     
        return self.def_operate_func(body_fun,"获取所有药材信息")

    def stock_in_herb(self, herb_id: int, quantity: float, batch_number: str, 
                     operator: str, production_date: str, expiry_date: str) -> bool:
        
        def body_fun(conn):
            
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

        self.def_operate_func(body_fun,"药材入库")





    # ===== 药材库存管理 =====
    def add_inventory(self, herb_id: int, batch_number: str, quantity: float, 
                    production_date: str = None, expiry_date: str = None,
                    quality_status: str = '待检', warehouse_location: str = None,
                    locked_quantity: float = 0) -> Optional[int]:
        """添加单条库存记录"""
        def body_fun(conn):
            cursor = conn.cursor()
            # 参数校验
            if not all([herb_id, batch_number, quantity >= 0]):
                self.logger.error("错误", "herb_id/batch_number/quantity为必填且合法参数")
                return None
            
            # 处理日期格式
            prod_date = datetime.strptime(production_date, "%Y-%m-%d").date() if production_date else None
            exp_date = datetime.strptime(expiry_date, "%Y-%m-%d").date() if expiry_date else None
            
            cursor.execute(
                """
                INSERT INTO herb_inventory 
                (herb_id, batch_number, quantity, production_date, expiry_date, 
                quality_status, warehouse_location, locked_quantity)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (herb_id, batch_number, quantity, prod_date, exp_date, 
                quality_status, warehouse_location, locked_quantity)
            )
            conn.commit()
            return cursor.lastrowid
        return self.def_operate_func(body_fun, "添加库存记录")

    def add_inventory_batch(self, inventory_list: List[dict]) -> int:
        """批量添加库存记录"""
        def body_fun(conn):
            cursor = conn.cursor()
            valid_params = []
            error_count = 0
            
            for item in inventory_list:
                # 校验必填字段
                if not all([item.get('herb_id'), item.get('batch_number'), item.get('quantity', 0) >= 0]):
                    error_count += 1
                    continue
                
                # 处理日期
                prod_date = datetime.strptime(item['production_date'], "%Y-%m-%d").date() if 'production_date' in item else None
                exp_date = datetime.strptime(item['expiry_date'], "%Y-%m-%d").date() if 'expiry_date' in item else None
                
                # 填充默认值
                quality_status = item.get('quality_status', '待检')
                warehouse_location = item.get('warehouse_location')
                locked_quantity = item.get('locked_quantity', 0.0)
                
                valid_params.append((
                    item['herb_id'], item['batch_number'], item['quantity'],
                    prod_date, exp_date, quality_status, warehouse_location, locked_quantity
                ))
            
            # 记录错误数据
            if error_count > 0:
                self.logger.warn("警告", f"跳过{error_count}条无效库存记录")
            
            # 执行批量插入
            if valid_params:
                cursor.executemany(
                    """
                    INSERT INTO herb_inventory 
                    (herb_id, batch_number, quantity, production_date, expiry_date, 
                    quality_status, warehouse_location, locked_quantity)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    valid_params
                )
                conn.commit()
                return cursor.rowcount
            return 0
        return self.def_operate_func(body_fun, "批量添加库存")

    def get_inventory_id(self, herb_id: int = None, batch_number: str = None) -> Optional[int]:
        """根据条件查询库存ID"""
        def body_fun(conn):
            cursor = conn.cursor()
            query = "SELECT inventory_id FROM herb_inventory WHERE 1=1"
            params = []
            
            if herb_id:
                query += " AND herb_id = %s"
                params.append(herb_id)
            if batch_number:
                query += " AND batch_number = %s"
                params.append(batch_number)
                
            cursor.execute(query, params)
            result = cursor.fetchone()
            return result[0] if result else None
        return self.def_operate_func(body_fun, "查询库存ID")

    def update_inventory(self, inventory_id: int, **kwargs) -> bool:
        """更新库存信息"""
        def body_fun(conn):
            cursor = conn.cursor()
            if not kwargs:
                return False
            
            # 过滤非法字段
            allowed_fields = {'quantity', 'production_date', 'expiry_date', 'quality_status', 
                            'warehouse_location', 'locked_quantity'}
            update_data = {k: v for k, v in kwargs.items() if k in allowed_fields}
            
            # 处理日期字段
            if 'production_date' in update_data:
                update_data['production_date'] = datetime.strptime(update_data['production_date'], "%Y-%m-%d").date()
            if 'expiry_date' in update_data:
                update_data['expiry_date'] = datetime.strptime(update_data['expiry_date'], "%Y-%m-%d").date()
            
            set_clause = ", ".join([f"{k} = %s" for k in update_data])
            params = list(update_data.values()) + [inventory_id]
            
            cursor.execute(
                f"UPDATE herb_inventory SET {set_clause} WHERE inventory_id = %s",
                params
            )
            conn.commit()
            return cursor.rowcount > 0
        return self.def_operate_func(body_fun, "更新库存")

    def delete_inventory(self, inventory_id: int) -> bool:
        """删除库存记录（物理删除）"""
        def body_fun(conn):
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM herb_inventory WHERE inventory_id = %s",
                (inventory_id,)
            )
            conn.commit()
            return cursor.rowcount > 0
        return self.def_operate_func(body_fun, "删除库存")

    def update_inventory_batch(self, updates: List[dict]) -> int:
        """批量更新库存（如调整库存数量/状态）"""
        def body_fun(conn):
            cursor = conn.cursor()
            updated_count = 0
            
            for update_item in updates:
                inventory_id = update_item.get('inventory_id')
                if not inventory_id:
                    continue
                
                # 过滤合法字段
                allowed_fields = {'quantity', 'quality_status', 'locked_quantity'}
                valid_fields = {k: v for k, v in update_item.items() 
                            if k in allowed_fields and v is not None}
                
                if not valid_fields:
                    continue
                    
                set_clause = ", ".join([f"{k} = %s" for k in valid_fields])
                params = list(valid_fields.values()) + [inventory_id]
                
                cursor.execute(
                    f"UPDATE herb_inventory SET {set_clause} WHERE inventory_id = %s",
                    params
                )
                updated_count += cursor.rowcount
            
            conn.commit()
            return updated_count
        return self.def_operate_func(body_fun, "批量更新库存")

    def delete_inventory_batch(self, inventory_ids: List[int]) -> int:
        """批量删除库存"""
        def body_fun(conn):
            if not inventory_ids:
                return 0
                
            cursor = conn.cursor()
            placeholders = ", ".join(["%s"] * len(inventory_ids))
            cursor.execute(
                f"DELETE FROM herb_inventory WHERE inventory_id IN ({placeholders})",
                inventory_ids
            )
            conn.commit()
            return cursor.rowcount
        return self.def_operate_func(body_fun, "批量删除库存")

    # ===== 药材库存管理 =====
    def get_all_inventory(self, herb_id: int = None) -> List[Dict]:
        """获取库存列表（可过滤药材ID）"""
        def body_fun(conn):
            cursor = conn.cursor(dictionary=True)
            query = """
                SELECT inventory_id, herb_id, batch_number, quantity, 
                    DATE_FORMAT(production_date, '%%Y-%%m-%%d') AS production_date,
                    DATE_FORMAT(expiry_date, '%%Y-%%m-%%d') AS expiry_date,
                    quality_status, warehouse_location, locked_quantity
                FROM herb_inventory
                WHERE 1=1
            """
            params = []
            if herb_id is not None:
                query += " AND herb_id = %s"
                params.append(herb_id)
            cursor.execute(query, params)
            return cursor.fetchall()
        return self.def_operate_func(body_fun, "获取库存列表")


    # ---- 耗材管理 ----
    def add_consumable(self, name: str, consumable_type: str, specification: str = "", 
                    unit: str = "个", standard_quantity: int = None, remark: str = "",
                    is_active: int = 1, is_default: int = 0) -> Optional[int]:
        """添加新耗材"""
        def body_fun(conn):
            cursor = conn.cursor()
            # 检查必要字段
            if not all([name, consumable_type]):
                self.logger.error("错误", "耗材名称和类型为必填项")
                return None
                
            cursor.execute(
                """
                INSERT INTO consumables 
                (consumable_name, consumable_type, specification, unit, 
                standard_quantity, remark, is_active, is_default)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (name, consumable_type, specification, unit, 
                standard_quantity, remark, is_active, is_default)
            )
            conn.commit()
            return cursor.lastrowid
        return self.def_operate_func(body_fun, "添加耗材")

    def add_consumables_batch(self, consumables: List[dict]) -> int:
        """批量添加耗材"""
        def body_fun(conn):
            cursor = conn.cursor()
            valid_params = []
            error_count = 0
            
            for item in consumables:
                # 校验必要字段
                name = item.get("consumable_name")
                c_type = item.get("consumable_type")
                if not all([name, c_type]):
                    error_count += 1
                    continue
                
                # 填充默认值
                spec = item.get("specification", "")
                unit = item.get("unit", "个")
                std_qty = item.get("standard_quantity")
                remark = item.get("remark", "")
                is_active = item.get("is_active", 1)
                is_default = item.get("is_default", 0)
                
                valid_params.append((
                    name, c_type, spec, unit, std_qty, 
                    remark, is_active, is_default
                ))
            
            # 记录错误数据
            if error_count > 0:
                self.logger.warn("警告", f"跳过{error_count}条无效耗材记录")
            
            # 执行批量插入
            if valid_params:
                cursor.executemany(
                    """
                    INSERT INTO consumables 
                    (consumable_name, consumable_type, specification, unit, 
                    standard_quantity, remark, is_active, is_default)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    valid_params
                )
                conn.commit()
                return cursor.rowcount
            return 0
        return self.def_operate_func(body_fun, "批量添加耗材")

    def get_consumable_id(self, name: str, specification: str = "") -> Optional[int]:
        """根据名称和规格获取耗材ID"""
        def body_fun(conn):
            cursor = conn.cursor()
            query = """
                SELECT consumable_id 
                FROM consumables 
                WHERE consumable_name = %s
            """
            params = [name]
            
            if specification:
                query += " AND specification = %s"
                params.append(specification)
                
            cursor.execute(query, params)
            result = cursor.fetchone()
            return result[0] if result else None
        return self.def_operate_func(body_fun, "查询耗材ID")

    def update_consumable(self, consumable_id: int, **kwargs) -> bool:
        """更新耗材信息"""
        def body_fun(conn):
            cursor = conn.cursor()
            if not kwargs:
                return False
                
            # 过滤合法字段
            allowed_fields = {
                'consumable_name', 'consumable_type', 'specification',
                'unit', 'standard_quantity', 'remark', 'is_active', 'is_default'
            }
            update_data = {k: v for k, v in kwargs.items() if k in allowed_fields}
            
            if not update_data:
                self.logger.error("错误", "无有效更新字段")
                return False
                
            set_clause = ", ".join([f"{k} = %s" for k in update_data])
            params = list(update_data.values()) + [consumable_id]
            
            cursor.execute(
                f"UPDATE consumables SET {set_clause} WHERE consumable_id = %s",
                params
            )
            conn.commit()
            return cursor.rowcount > 0
        return self.def_operate_func(body_fun, "更新耗材")

    def delete_consumable(self, consumable_id: int) -> bool:
        """逻辑删除耗材"""
        return self.update_consumable(consumable_id, is_active=False)

    def update_consumables_batch(self, updates: List[dict]) -> int:
        """批量更新耗材信息"""
        def body_fun(conn):
            cursor = conn.cursor()
            updated_count = 0
            
            for update_item in updates:
                c_id = update_item.get("consumable_id")
                if not c_id:
                    continue
                    
                # 过滤合法字段
                allowed_fields = {
                    'consumable_name', 'consumable_type', 'specification',
                    'unit', 'standard_quantity', 'remark', 'is_active', 'is_default'
                }
                valid_fields = {k: v for k, v in update_item.items() 
                            if k in allowed_fields and k != "consumable_id"}
                
                if not valid_fields:
                    continue
                    
                set_clause = ", ".join([f"{k} = %s" for k in valid_fields])
                params = list(valid_fields.values()) + [c_id]
                
                cursor.execute(
                    f"UPDATE consumables SET {set_clause} WHERE consumable_id = %s",
                    params
                )
                updated_count += cursor.rowcount
            
            conn.commit()
            return updated_count
        return self.def_operate_func(body_fun, "批量更新耗材")

    def delete_consumables_batch(self, consumable_ids: List[int]) -> int:
        """批量逻辑删除耗材"""
        def body_fun(conn):
            if not consumable_ids:
                return 0
                
            cursor = conn.cursor()
            placeholders = ", ".join(["%s"] * len(consumable_ids))
            cursor.execute(
                f"UPDATE consumables SET is_active = FALSE WHERE consumable_id IN ({placeholders})",
                consumable_ids
            )
            conn.commit()
            return cursor.rowcount
        return self.def_operate_func(body_fun, "批量删除耗材")

    def get_all_consumables(self, include_inactive: bool = False) -> List[Dict]:
        """获取所有耗材列表"""
        def body_fun(conn):
            cursor = conn.cursor(dictionary=True)
            query = """
                SELECT consumable_id, consumable_name, consumable_type, 
                    specification, unit, standard_quantity, remark, 
                    is_active, is_default
                FROM consumables
            """
            if not include_inactive:
                query += " WHERE is_active = TRUE"
            cursor.execute(query)
            return cursor.fetchall()
        return self.def_operate_func(body_fun, "获取耗材列表")
    
    
