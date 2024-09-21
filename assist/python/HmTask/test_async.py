import asyncio 
from time import time
async def test(i):
    start_time=time()
    print(f'test-{i}')
    await asyncio.sleep(i%5 +1)
    print(f"test-{i} 用时:{time()-start_time}")


async def hello():
    start_time=time()
    print('Hello')
    await asyncio.sleep(1)
    print(f'Hello用时:{time()-start_time}')
    
async def merge():
    tasks = [test(i) for i in range(15)]
    tasks.append(hello())
    
    await asyncio.gather(*tasks)
def main():
    

    start_time=time()
    
    asyncio.run(merge())
    print(f'main:{time()-start_time}')


if __name__ == '__main__':
    main()