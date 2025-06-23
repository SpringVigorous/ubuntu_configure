class PrintInfo:
    _instance = None
    
    def __new__(cls, file_path=r"F:\hg\BJY\drawing_recogniton_dispatch\dwg_to_image\dwgs\entity.log"):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance.file_path = file_path
            cls._instance._file = open(file_path, "w", encoding="utf-8-sig")
        return cls._instance
    
    def print_info(self, *args):
        self._file.write(f'{" ".join(map(str, args))}\n')
        self._file.flush()  # 确保立即写入磁盘
    
    def close(self):
        if not self._file.closed:
            self._file.close()
    
    def __del__(self):
        self.close()

def print_info(*args):
    PrintInfo().print_info(*args)
def close_print():
    PrintInfo().close()
# 使用示例
if __name__ == "__main__":
    # 获取单例实例
    logger = PrintInfo()
    
    # 打印信息
    logger.print_info("视口信息:")
    logger.print_info("中心点坐标:", (100.5, 200.3))
    logger.print_info("尺寸:", "800x600")
    
    # 获取相同实例
    same_logger = PrintInfo()
    same_logger.print_info("缩放比例:", "1:100")
    
    # 关闭日志
    logger.close()