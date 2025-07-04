from transitions import Machine, State
import random
import time
import threading

class CoffeeMachine:
    def __init__(self, name):
        self.name = name
        self.water_level = 100  # 百分比
        self.coffee_beans = 100  # 百分比
        self.milk_level = 50  # 百分比
        self.cleanliness = 100  # 清洁度
        self.last_brew_time = None
        self.error_log = []
        self.current_coffee_type = None  # 新增属性，用于存储当前正在制作的咖啡类型
        
        
        # 定义状态
        states = [
            State(name='standby', on_enter=['reset_brew_timer']),
            State(name='brewing', on_enter=['on_brewing_start']),
            State(name='steaming', on_enter=['steam_start'], on_exit=['steam_end']),
            State(name='error', on_enter=['log_error']),
            State(name='maintenance_cleaning'),
            State(name='maintenance_refilling'),
            State(name='self_test'),
        ]
        
        # 定义转换/转移
        transitions = [
            # 基础转换
            {'trigger': 'start_brewing', 'source': 'standby', 'dest': 'brewing', 
             'conditions': 'has_sufficient_resources',
             'before': 'set_coffee_type'},  # 设置当前咖啡类型
            
            {'trigger': 'start_steaming', 'source': 'standby', 'dest': 'steaming', 
             'conditions': 'has_milk'},
            {'trigger': 'brewing_complete', 'source': 'brewing', 'dest': 'standby', 
             'before': 'complete_brewing'},
            {'trigger': 'steaming_complete', 'source': 'steaming', 'dest': 'standby', 
             'before': 'complete_steaming'},
            
            # 带条件的转换
            {'trigger': 'start_brewing', 'source': 'standby', 'dest': 'error', 
             'unless': 'has_sufficient_resources'},
            {'trigger': 'start_steaming', 'source': 'standby', 'dest': 'error', 
             'unless': 'has_milk'},
            
            # 错误处理
            {'trigger': 'detect_problem', 'source': '*', 'dest': 'error'},
            {'trigger': 'error_ack', 'source': 'error', 'dest': 'standby'},
            
            # 维护状态转换
            {'trigger': 'start_cleaning', 'source': 'standby', 'dest': 'maintenance_cleaning',
             'before': 'start_cleaning_process'},
            {'trigger': 'start_refilling', 'source': 'standby', 'dest': 'maintenance_refilling',
             'before': 'start_refilling_process'},
            {'trigger': 'complete_cleaning', 'source': 'maintenance_cleaning', 'dest': 'standby',
             'after': 'finish_maintenance'},
            {'trigger': 'complete_refilling', 'source': 'maintenance_refilling', 'dest': 'standby',
             'after': 'finish_maintenance'},
            
            # 自检状态
            {'trigger': 'daily_check', 'source': 'standby', 'dest': 'self_test',
             'after': 'run_self_test'},
            {'trigger': 'self_test_pass', 'source': 'self_test', 'dest': 'standby'},
            {'trigger': 'self_test_fail', 'source': 'self_test', 'dest': 'maintenance_cleaning'},
        ]
        
        # 创建状态机
        self.machine = Machine(
            model=self,
            states=states,
            transitions=transitions,
            initial='standby',
            ignore_invalid_triggers=True,
            before_state_change='before_any_change',
            after_state_change='after_any_change',
            send_event=True,  # 传递事件对象
            queued=True
        )
    def set_coffee_type(self, event):
        """从事件参数中提取咖啡类型并存储"""
        self.current_coffee_type = event.kwargs.get('coffee_type', '标准咖啡')
        print(f"设置咖啡类型: {self.current_coffee_type}")
    # ============ 回调方法 ============
    def before_any_change(self, event):
        """在任何状态转换前执行"""
        print(f"[准备] 从 {event.transition.source} 到 {event.transition.dest}")
        
    def after_any_change(self, event):
        """在任何状态转换后执行"""
        if event.error:
            print(f"⚠️ 转换失败: {event.error}")
        else:
            print(f"[状态变更] 当前: {self.state}")
    
    def reset_brew_timer(self, event=None):
        """重置上次制作咖啡的时间"""
        self.last_brew_time = None
        print("⏱️ 计时器已重置")
    
    def steam_start(self, event=None):
        """开始制作蒸汽"""
        print("🔥 加热牛奶中...")
        
    def steam_end(self, event=None):
        """结束制作蒸汽"""
        print("🔥 加热结束")
        
    def log_error(self, event):
        """记录错误信息"""
        error_message = event.kwargs.get('message', '未知错误')
        self.error_log.append(error_message)
        print(f"❌ 错误记录: {error_message}")
        
    def complete_brewing(self, event):
        """使用存储的咖啡类型完成制作"""
        if self.current_coffee_type:
            coffee_type = self.current_coffee_type
            self.coffee_beans = max(0, self.coffee_beans - random.randint(10, 20))
            self.water_level = max(0, self.water_level - random.randint(15, 25))
            self.cleanliness = max(0, self.cleanliness - random.randint(3, 8))
            self.last_brew_time = time.time()
            print(f"☕️ 已完成制作: {coffee_type}")
            print(f"🔄 剩余资源: 🫘{self.coffee_beans}% 💧{self.water_level}% 🧼{self.cleanliness}%")
        else:
            print("⚠️ 完成制作时未设置咖啡类型！")
        
    def complete_steaming(self, event):
        """完成蒸汽制作"""
        self.milk_level = max(0, self.milk_level - random.randint(10, 30))
        print("🥛 奶泡制作完成")
        print(f"🔄 剩余牛奶: {self.milk_level}%")
    
    def on_brewing_start(self, event):
        """开始冲煮时的回调"""
        coffee_type = event.kwargs.get('coffee_type', '标准咖啡')
        print(f"⚙️ 开始制作: {coffee_type}")
        
    def start_cleaning_process(self, event):
        """开始清洁过程"""
        print("🧽 清洁咖啡机中...")
        self.clean()
        
    def start_refilling_process(self, event):
        """开始补充资源"""
        print("📦 准备补充资源")
        
    def finish_maintenance(self, event=None):
        """完成维护"""
        print("✅ 维护完成")
        
    # ============ 修正的条件检查方法 ============
    def has_sufficient_resources(self, event=None):
        """检查是否有足够资源制作咖啡"""
        if self.water_level < 20:
            print("⚠️ 水量不足!")
            return False
        if self.coffee_beans < 15:
            print("⚠️ 咖啡豆不足!")
            return False
        return True
    
    def has_milk(self, event=None):
        """检查是否有足够牛奶"""
        if self.milk_level < 20:
            print("⚠️ 牛奶不足!")
            return False
        return True
    
    def run_self_test(self, event):
        """执行自检"""
        print("🔍 运行自检程序...")
        time.sleep(1)  # 模拟自检过程
        if random.random() > 0.3:  # 70%几率通过
            print("✅ 自检通过")
            self.self_test_pass()
        else:
            print("❌ 自检失败，需要清洁")
            self.self_test_fail()
    
    # ============ 操作命令 ============
    def refill(self, resource, amount=100):
        """补充资源"""
        if resource == 'water':
            self.water_level = min(100, self.water_level + amount)
            print(f"💧 加水: +{amount}%")
        elif resource == 'beans':
            self.coffee_beans = min(100, self.coffee_beans + amount)
            print(f"🫘 补充咖啡豆: +{amount}%")
        elif resource == 'milk':
            self.milk_level = min(100, self.milk_level + amount)
            print(f"🥛 补充牛奶: +{amount}%")
    
    def clean(self):
        """清洁咖啡机"""
        self.cleanliness = 100
        print("🧼 清洁完成")
        
    def get_status(self):
        """获取当前状态信息"""
        return {
            'state': self.state,
            'water': self.water_level,
            'beans': self.coffee_beans,
            'milk': self.milk_level,
            'cleanliness': self.cleanliness
        }


class AsyncCoffeeMachine(CoffeeMachine):
    def __init__(self, name):
        super().__init__(name)
        # 创建任务队列和工作线程
        self.task_queue = []
        self.active = True
        self.worker_thread = threading.Thread(target=self.process_queue, daemon=True)
        self.worker_thread.start()
        
    def process_queue(self):
        """处理队列中的任务"""
        while self.active:
            if self.task_queue:
                task = self.task_queue.pop(0)
                name, args, kwargs = task
                print(f"⌛ 开始处理任务: {name}")
                try:
                    # 执行任务
                    if name == 'start_brewing':
                        coffee_type = kwargs.get('coffee_type', '标准咖啡')
                        self.start_brewing(coffee_type=coffee_type)
                    elif name == 'start_steaming':
                        self.start_steaming()
                    print(f"✅ 任务完成: {name}")
                except Exception as e:
                    print(f"❌ 任务失败: {name} - {e}")
            time.sleep(0.1)
            
    def async_start_brewing(self, coffee_type='标准咖啡'):
        """添加制作咖啡任务到队列"""
        if self.state == 'standby':
            self.task_queue.append(('start_brewing', (), {'coffee_type': coffee_type}))
            print(f"📥 已添加咖啡制作任务: {coffee_type}")
        else:
            print("⚠️ 机器忙碌中，无法开始制作咖啡")
            
    def async_start_steaming(self):
        """添加制作蒸汽任务到队列"""
        if self.state == 'standby':
            self.task_queue.append(('start_steaming', (), {}))
            print("📥 已添加奶泡制作任务")
        else:
            print("⚠️ 机器忙碌中，无法开始制作奶泡")
            
    def close(self):
        """关闭咖啡机"""
        self.active = False
        self.worker_thread.join()
        print("🛑 咖啡机已关闭")

# 测试函数
def test_coffee_machine():
    print("\n" + "="*50)
    print("测试咖啡机".center(50))
    print("="*50)
    
    # 创建咖啡机实例
    cm = CoffeeMachine("咖啡大师")
    print(f"初始状态: {cm.state}")
    print(f"状态信息: {cm.get_status()}")
    
    # 1. 制作咖啡
    print("\n➡️ 测试1: 制作咖啡")
    cm.start_brewing(coffee_type='浓缩咖啡')
    cm.brewing_complete()
    
    # 2. 资源不足
    print("\n➡️ 测试2: 资源不足测试")
    cm.water_level = 10
    cm.start_brewing(coffee_type='拿铁')  # 应触发错误
    cm.error_ack()  # 返回待机状态
    
    # 3. 补充资源
    print("\n➡️ 测试3: 补充资源")
    cm.refill('water', 50)
    cm.refill('beans', 30)
    cm.start_brewing(coffee_type='卡布奇诺')
    cm.brewing_complete()
    
    # 4. 制作奶泡
    print("\n➡️ 测试4: 制作奶泡")
    cm.start_steaming()
    cm.steaming_complete()
    
    # 5. 维护
    print("\n➡️ 测试5: 维护模式")
    cm.start_cleaning()
    cm.complete_cleaning()
    
    # 6. 自检
    print("\n➡️ 测试6: 自检功能")
    cm.daily_check()
    
    # 7. 测试异步咖啡机
    print("\n" + "="*50)
    print("测试异步咖啡机".center(50))
    print("="*50)
    async_cm = AsyncCoffeeMachine("异步咖啡机")
    async_cm.start_brewing('美式咖啡')
    async_cm.start_brewing('摩卡')  # 进入队列
    async_cm.start_steaming()      # 进入队列
    
    # 等待任务处理
    print("\n等待任务执行...")
    time.sleep(5)
    
    # 清理
    async_cm.close()
    print("测试完成")

if __name__ == "__main__":
    test_coffee_machine()