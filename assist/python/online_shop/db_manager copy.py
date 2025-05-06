import mysql.connector
from mysql.connector import Error
from datetime import datetime
import os
import threading
from threading import Lock
import random



class InventoryManager:
    def __init__(self, batch_size=50, flush_interval=10):
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self.cache_queue = []
        self.cache_lock = Lock()
        self.connection = None
        self._initialize_database()
        self._start_flush_timer()

    def _initialize_database(self):
        """初始化数据库和表结构"""
        try:
            # 连接到MySQL服务器（不指定数据库）
            self.connection = mysql.connector.connect(
                host='localhost',
                port= 3306,
                user='SpringFlourish',
                password='137098',
            )
            cursor = self.connection.cursor()
            
            # 创建数据库
            cursor.execute("CREATE DATABASE IF NOT EXISTS medical_product")
            self.connection.database = 'medical_product'
            
            # 从文件创建表
            self._create_tables_from_sql_file()
            print("数据库初始化完成")
            
        except Error as e:
            print(f"数据库初始化失败: {e}")
            raise
        finally:
            if cursor:
                cursor.close()

    def _create_tables_from_sql_file(self):
        """从SQL文件创建表结构"""
        sql_file_path = os.path.join(
            os.path.dirname(__file__), 
            'schema', 
            'tables.sql'
        )
        
        try:
            with open(sql_file_path, 'r', encoding='utf-8') as file:
                sql_script = file.read()
            
            # 分割并过滤SQL命令
            commands = [cmd.strip() for cmd in sql_script.split(';') if cmd.strip()]
            
            cursor = self.connection.cursor()
            for cmd in commands:
                cursor.execute(cmd)
            self.connection.commit()
            
        except FileNotFoundError:
            print(f"错误: SQL文件不存在 - {sql_file_path}")
            raise
        except Error as e:
            self.connection.rollback()
            print(f"执行建表语句失败: {e}")
            raise
        finally:
            if cursor:
                cursor.close()

    def _start_flush_timer(self):
        """启动定时刷新缓存"""
        self.timer = threading.Timer(self.flush_interval, self.flush_cache)
        self.timer.daemon = True
        self.timer.start()

    def add_to_cache(self, query, params):
        """添加操作到缓存队列"""
        with self.cache_lock:
            self.cache_queue.append((query, params))
            if len(self.cache_queue) >= self.batch_size:
                self.flush_cache()

    def flush_cache(self):
        """批量执行缓存中的操作"""
        if not self.cache_queue:
            return

        with self.cache_lock:
            queue_copy = self.cache_queue.copy()
            self.cache_queue.clear()

        try:
            self.begin_transaction()
            cursor = self.connection.cursor()
            for query, params in queue_copy:
                cursor.execute(query, params)
            self.commit()
            print(f"批量提交成功，共 {len(queue_copy)} 条记录")
        except Error as e:
            self.rollback()
            print(f"批量操作失败，已回滚: {e}")
            # 将失败的操作重新加入队列
            with self.cache_lock:
                self.cache_queue.extend(queue_copy)
        finally:
            if cursor:
                cursor.close()
            self._start_flush_timer()
    def get_product_id_by_name(self, product_name):
        """根据产品名称获取product_id"""
        query = "SELECT product_id FROM products WHERE name = %s"
        result = self.execute_query(query, (product_name,), fetch=True)
        if not result:
            return None
        elif len(result) > 1:
            raise ValueError(f"存在多个同名产品: {product_name}")
        return result[0]['product_id']

    def get_supplier_id_by_name(self, supplier_name):
        """根据供应商名称获取supplier_id"""
        query = "SELECT supplier_id FROM suppliers WHERE name = %s"
        result = self.execute_query(query, (supplier_name,), fetch=True)
        if not result:
            return None
        elif len(result) > 1:
            raise ValueError(f"存在多个同名供应商: {supplier_name}")
        return result[0]['supplier_id']
    # ----------------- 事务控制 -----------------
    def begin_transaction(self):
        if self.connection.is_connected():
            self.connection.start_transaction()

    def commit(self):
        if self.connection.is_connected():
            self.connection.commit()

    def rollback(self):
        if self.connection.is_connected():
            self.connection.rollback()

    # ----------------- 核心功能 -----------------
    def execute_query(self, query, params=None, fetch=False, auto_commit=True):
        """通用查询执行方法"""
        cursor = self.connection.cursor(dictionary=True)
        try:
            cursor.execute(query, params or ())
            
            if fetch:
                result = cursor.fetchall()
                return result
            else:
                if auto_commit:
                    self.connection.commit()
                return cursor.rowcount
        except Error as e:
            print(f"执行查询失败: {e}")
            if not auto_commit:
                self.rollback()
            return None
        finally:
            cursor.close()

    def add_product(self, name, description, unit, min_quantity=0):
        query = """
                INSERT INTO products (name, description, unit, min_quantity)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                description = IFNULL(%s, description),
                unit = IFNULL(%s, unit),
                min_quantity = IFNULL(%s, min_quantity)
            """
        return self.execute_query(query, (name, description, unit, min_quantity, description, unit, min_quantity))


    def all_product_names(self):
        query = "SELECT name FROM products"
        return [item["name"]  for item in  self.execute_query(query, fetch=True)]
    
    def all_supplier_names(self):
        query = "SELECT name FROM suppliers"
        return [item["name"]  for item in self.execute_query(query, fetch=True)]
    
    def add_supplier(self, name, contact, phone, address):
        query = """
            INSERT INTO suppliers (name, contact, phone, address)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
            contact = IFNULL(%s, contact),
            phone = IFNULL(%s, phone),
            address = IFNULL(%s, address)
        """
        return self.execute_query(query, (name, contact, phone, address, contact, phone, address))

    def stock_in(self, product_id=None, supplier_id=None, quantity=None, unit_price=None, 
                    product_name=None, supplier_name=None, transaction_date=None, 
                    notes=None, use_cache=False):
            # 参数验证与ID查找逻辑
            if product_id is None and product_name is None:
                raise ValueError("必须提供 product_id 或 product_name")
            if supplier_id is None and supplier_name is None:
                raise ValueError("必须提供 supplier_id 或 supplier_name")
            
            if product_id is None:
                product_id = self.get_product_id_by_name(product_name)
                if product_id is None:
                    raise ValueError(f"产品不存在: {product_name}")
            
            if supplier_id is None:
                supplier_id = self.get_supplier_id_by_name(supplier_name)
                if supplier_id is None:
                    raise ValueError(f"供应商不存在: {supplier_name}")
            
            # 原有入库逻辑
            if transaction_date is None:
                transaction_date = datetime.now().date()
            
            total_price = quantity * unit_price
            query = """
            INSERT INTO stock_in 
            (product_id, supplier_id, quantity, unit_price, total_price, transaction_date, notes)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            params = (product_id, supplier_id, quantity, unit_price, total_price, transaction_date, notes)
            
            if use_cache:
                self.add_to_cache(query, params)
            else:
                result = self.execute_query(query, params)
                if not result:
                    return False
            
            return self.update_product_quantity(product_id, quantity)

    def stock_out(self, product_id, quantity, recipient, purpose, 
                 transaction_date=None, notes=None, use_cache=False):
        """出库操作（支持批量模式）"""
        # 库存实时检查
        product = self.get_product_by_id(product_id)
        if not product or product[0]['current_quantity'] < quantity:
            print("错误: 库存不足")
            return False
        
        if transaction_date is None:
            transaction_date = datetime.now().date()
        
        query = """
        INSERT INTO stock_out 
        (product_id, quantity, recipient, purpose, transaction_date, notes)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        params = (product_id, quantity, recipient, purpose, transaction_date, notes)
        
        # 实时更新库存
        update_result = self.update_product_quantity(product_id, -quantity)
        if update_result is None:
            return False
        
        # 记录插入选择模式
        if use_cache:
            self.add_to_cache(query, params)
            return True
        else:
            return self.execute_query(query, params) is not None

    def update_product_quantity(self, product_id, quantity_change):
        """实时更新库存（强制立即执行）"""
        query = "UPDATE products SET current_quantity = current_quantity + %s WHERE product_id = %s"
        return self.execute_query(query, (quantity_change, product_id), auto_commit=True)

    # ----------------- 查询方法 -----------------
    def get_product_by_id(self, product_id):
        query = "SELECT * FROM products WHERE product_id = %s"
        return self.execute_query(query, (product_id,), fetch=True)

    def get_inventory_status(self, low_stock_only=False):
        query = "SELECT * FROM products"
        if low_stock_only:
            query += " WHERE current_quantity <= min_quantity"
        return self.execute_query(query, fetch=True)

# ================= 使用示例 =================
if __name__ == "__main__":
    # 初始化（自动建表）
    manager = InventoryManager()
    
    # 添加测试数据
    manager.add_product("笔记本电脑", "高性能游戏本", "台", 5)
    manager.add_product("无线鼠标", "蓝牙5.0", "个", 10)
    
    
    manager.add_supplier("华为", "中国","86","上海")
    manager.add_supplier("小米", "中国","86","上海")
    manager.add_supplier("oppo", "中国","86","上海")
    manager.add_supplier("vivo", "中国","86","上海")
    
    product_names=manager.all_product_names()
    supplier_names=manager.all_supplier_names()
    
    product_count=len(product_names)
    supplier_count=len(supplier_names)
    
    # 批量入库操作
    for i in range(1,100):
        product_index=random.randint(0, product_count-1)
        suppler_index=random.randint(0, supplier_count-1)
        
        manager.stock_in(product_name=product_names[product_index],supplier_name=supplier_names[suppler_index] , quantity=2,unit_price=5000.0, use_cache=True)
    
    # 实时出库操作
    for i in range(1,100):
        product_index=random.randint(0, product_count-1)
        manager.stock_out(product_names[product_index], 2, "销售部", "客户订单")
    
    # 手动触发缓存刷新
    manager.flush_cache()
    
    # 查看库存
    print("当前库存:")
    for product in manager.get_inventory_status():
        print(f"{product['name']}: {product['current_quantity']}{product['unit']}")