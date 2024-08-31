import asyncio
import time

async def test_async(i,task_name):
    num=11-i
    # 你的异步操作
    print(f"{task_name} started")
    await asyncio.sleep(num)  # 示例异步操作
    print(f"{task_name} completed")
    
    print(f"{task_name} second started")
    await asyncio.sleep(num)  # 示例异步操作
    print(f"{task_name} second completed")
    return num

def task_name(i):
    return f"Task {i}"
async def main():
    tasks=[]
    for i in range(1, 11):
        name=task_name(i)
        tasks.append(asyncio.create_task(test_async(i,name),name=name))
    results= await asyncio.gather(*tasks)
    print(results)

if __name__ == "__main__":
    cur_time=time.time()
    asyncio.run(main())
    print(f'用时：{time.time()-cur_time}')

    """
Task 1 started
Task 2 started
Task 3 started
Task 4 started
Task 5 started
Task 6 started
Task 7 started
Task 8 started
Task 9 started
Task 10 started
Task 10 completed
Task 10 second started
Task 9 completed
Task 9 second started
Task 10 second completed
Task 8 completed
Task 8 second started
Task 7 completed
Task 7 second started
Task 9 second completed
Task 6 completed
Task 6 second started
Task 5 completed
Task 5 second started
Task 8 second completed
Task 4 completed
Task 4 second started
Task 3 completed
Task 3 second started
Task 2 completed
Task 2 second started
Task 1 completed
Task 1 second started
Task 6 second completed
Task 5 second completed
Task 4 second completed
Task 3 second completed
Task 2 second completed
Task 1 second completed
[10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
用时：20.020404815673828
    """