from contextlib import contextmanager
from typing import Optional

class AutoCommitManager:
    """事务管理器：自动管理autocommit状态及事务提交/回滚"""
    
    def __init__(self, conn):
        self.conn = conn
        self.original_autocommit: Optional[bool] = None
    
    def __enter__(self):
        if self.conn and self.conn.is_connected():
            # 保存原始autocommit状态，并关闭自动提交
            self.original_autocommit = self.conn.autocommit
            self.conn.autocommit = False
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn and self.conn.is_connected():
            try:
                if exc_type is None:
                    self.conn.commit()  # 无异常，提交事务
                else:
                    self.conn.rollback()  # 有异常，回滚事务
            finally:
                # 恢复原始autocommit状态
                if self.original_autocommit is not None:
                    self.conn.autocommit = self.original_autocommit