import asyncio

# 定义一个协程函数
async def my_coroutine(i):
    print(f"开始执行协程:{i}")
    await asyncio.sleep(1)
    print(f"协程执行完成:{i}")

async def main():

    
    # 创建一个任务
    task = [asyncio.create_task(my_coroutine(i)) for i in range(10)]
    
    # 执行其他任务
    print("执行其他任务")
    
    # 等待任务完成
    await asyncio.gather(*task)
    
    # 检查任务状态
    # print(f"任务状态: {task.done()}")
    # if task.cancelled():
    #     print("任务被取消")
    # else:
    #     print("任务执行完成")

# 运行主函数
asyncio.run(main())