import threading
import time

def task(name, event):
    print(f"Starting task {name}")
    time.sleep(2)
    print(f"Finished task {name}")
    event.set()
    print(f"Event set for task {name}")

def main():
    events = []
    threads = []
    
    for i in range(10):
        event = threading.Event()
        t = threading.Thread(target=task, args=(f"task_{i}", event))
        t.start()
        threads.append(t)
        events.append(event)
    
    # 等待所有事件被设置
    for index,event in   enumerate(events):
        print(f"Waiting for event {index}")
        event.wait()
    
    # 等待所有线程完成
    for thread in threads:
        thread.join()

if __name__ == '__main__':
    main()