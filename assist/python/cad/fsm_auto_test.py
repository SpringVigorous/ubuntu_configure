from transitions import Machine, State
import threading
import time
import random

class AutoCoffeeMachine:
    def __init__(self, name):
        self.name = name
        self.running = False
        self.coffee_type = "美式咖啡"
        self.water_level = 100
        self.coffee_beans = 100
        self.error_log = []
        self._pending_completions = {}  # 存储待处理的状态完成回调
        
        # 状态定义
        states = [
            State('standby'),
            State('grinding', on_enter='start_grinding'),
            State('brewing', on_enter='start_brewing'),
            State('dispensing', on_enter='start_dispensing'),
            State('cleaning', on_enter='start_cleaning'),
            State('error', on_enter='log_error')
        ]
        
        # 状态转移
        transitions = [
            # 主流程
            {'trigger': 'start_process', 'source': 'standby', 'dest': 'grinding'},
            {'trigger': 'grinding_complete', 'source': 'grinding', 'dest': 'brewing'},
            {'trigger': 'brewing_complete', 'source': 'brewing', 'dest': 'dispensing'},
            {'trigger': 'dispensing_complete', 'source': 'dispensing', 'dest': 'cleaning'},
            {'trigger': 'cleaning_complete', 'source': 'cleaning', 'dest': 'standby'},
            
            # 错误处理
            {'trigger': 'detect_problem', 'source': '*', 'dest': 'error'},
            {'trigger': 'error_ack', 'source': 'error', 'dest': 'standby'},
        ]
        
        # 创建状态机
        self.machine = Machine(
            model=self,
            states=states,
            transitions=transitions,
            initial='standby',
            ignore_invalid_triggers=True
        )
    
    # ===== 状态完成回调管理 =====
    def _register_completion(self, state, callback, timeout):
        """注册状态完成回调"""
        # 取消该状态之前的任何待处理回调
        if state in self._pending_completions:
            self._pending_completions[state].cancel()
        
        # 创建新定时器
        timer = threading.Timer(timeout, self._state_completion_handler, args=(state, callback))
        timer.start()
        
        # 存储定时器引用
        self._pending_completions[state] = timer
    
    def _state_completion_handler(self, state, callback):
        """处理状态完成回调"""
        # 检查是否仍在原始状态
        if self.state == state:
            try:
                callback()
            except Exception as e:
                self.detect_problem(message=f"状态完成回调失败: {str(e)}")
        
        # 清理定时器引用
        if state in self._pending_completions:
            del self._pending_completions[state]
    
    def cancel_pending_completions(self):
        """取消所有待处理的状态完成回调"""
        for state, timer in list(self._pending_completions.items()):
            timer.cancel()
            del self._pending_completions[state]
    
    # ===== 状态回调方法 =====
    def start_grinding(self):
        """研磨咖啡豆阶段"""
        print(f"⏲️ 正在研磨 {self.coffee_type} 的咖啡豆...")
        self._register_completion(
            state='grinding',
            callback=self.grinding_complete,
            timeout=2.0
        )
    
    def start_brewing(self):
        """冲泡咖啡阶段"""
        print(f"♨️ 正在冲泡 {self.coffee_type}...")
        self._register_completion(
            state='brewing',
            callback=self.brewing_complete,
            timeout=3.0
        )
    
    def start_dispensing(self):
        """出品咖啡阶段"""
        print(f"☕️ 正在出品 {self.coffee_type}...")
        self._register_completion(
            state='dispensing',
            callback=self.dispensing_complete,
            timeout=1.5
        )
    
    def start_cleaning(self):
        """清洁机器阶段"""
        print("🧼 正在清洁咖啡机...")
        self._register_completion(
            state='cleaning',
            callback=self.cleaning_complete,
            timeout=2.5
        )
    
    # ===== 错误处理 =====
    def detect_problem(self, message):
        """检测到问题时取消所有待处理回调"""
        self.cancel_pending_completions()
        self.error_log.append(message)
        super().detect_problem()
        print(f"❌ 检测到问题: {message}")
    
    def log_error(self):
        """记录错误信息"""
        if self.error_log:
            print(f"❌ 当前错误: {self.error_log[-1]}")
    
    # ===== 公共接口 =====
    def start_auto_process(self, coffee_type="美式咖啡"):
        """启动自动制作流程"""
        if self.state != 'standby':
            print("⚠️ 机器正在运行中，无法开始新任务")
            return
            
        self.coffee_type = coffee_type
        self.running = True
        self.start_process()
        print(f"🚀 开始自动制作 {coffee_type} 咖啡...")
    
    def emergency_stop(self):
        """紧急停止"""
        if self.running:
            self.running = False
            self.cancel_pending_completions()
            print("🛑 紧急停止！")
            
            # 如果不在待机状态，直接返回待机
            if self.state != 'standby':
                self.machine.set_state('standby')
    
    def error_ack(self):
        """确认错误并返回待机"""
        self.cancel_pending_completions()
        super().error_ack()
        print("✅ 错误已确认，返回待机状态")

# 使用示例
if __name__ == "__main__":
    print("===== 全自动咖啡机演示 =====")
    machine = AutoCoffeeMachine("自动咖啡大师")
    
    # 启动自动制作流程
    machine.start_auto_process(coffee_type="卡布奇诺")
    
    # 监控状态变化
    states = []
    start_time = time.time()
    
    while time.time() - start_time < 35:  # 最多运行15秒
        time.sleep(0.5)
        print(f"当前状态{machine.state}")
        # 记录状态变化
        if not states or states[-1] != machine.state:
            states.append(machine.state)
            print(f"状态变更 → {machine.state}")
            
        # # 20%概率模拟紧急停止
        # if random.random() < 0.01 and machine.running:
        #     print("\n⚠️ 用户启动紧急停止！")
        #     machine.emergency_stop()
        #     break
        elif 'standby' == machine.state:
            break
    
    # 输出最终状态
    print("\n===== 最终状态报告 =====")
    print(f"当前状态: {machine.state}")
    print(f"剩余水量: {machine.water_level}%")
    print(f"剩余咖啡豆: {machine.coffee_beans}%")
    
    if machine.error_log:
        print("\n错误记录:")
        for error in machine.error_log:
            print(f" - {error}")