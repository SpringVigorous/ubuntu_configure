def min_bridge_time(times):
    if not times:
        return 0
    time=map(float, times)
    # 按过桥时间升序排序（确保T[0]最快）
    times.sort()
    n = len(times)
    
    # 边界情况处理
    if n == 1:
        return times[0]
    if n == 2:
        return times[1]  # 两人同行取较慢者
    if n == 3:
        return times[0] + times[1] + times[2]  # 最快者接送两次
    
    # 初始化DP数组
    dp = [0.0] * n
    dp[0] = times[0]        # 1人：直接过桥
    dp[1] = times[1]        # 2人：较慢者时间
    dp[2] = times[0] + times[1] + times[2]  # 3人：最快者接送
    
    
    def offset_1(i):
        return dp[i-1] + times[0] + times[i]
    def offset_2(i):
        return dp[i-2] + times[0] + 2*times[1] + times[i]
    
    

    # 状态转移（从第4人开始）
    for i in range(3, n):
        # 策略1：最快者送当前最慢者（T[i]）
        strategy1 = offset_1(i)
        # 策略2：最快和次快配合送最慢两人
        strategy2 = offset_2(i)
        dp[i] = min(strategy1, strategy2)

    return dp[n-1]

# 测试案例
test_cases = [
    ([1, 2, 2.5, 3,3.1,14], 17),    # 经典案例：1,2,5,10 → 17分钟
    ([1, 2, 5, 8], 15),      # 1+2过(2) → 1回(1) → 5+8过(8) → 2回(2) → 1+2过(2) = 15
    ([1, 3, 4, 7], 14),      # 策略2更优：1+3过(3) → 1回(1) → 4+7过(7) → 3回(3) → 1+3过(3) = 14
    ([10, 20, 30], 60),      # 三人场景：10+20过(20) → 10回(10) → 10+30过(30) = 60
    ([1, 100], 100),         # 两人场景：直接过桥取较慢者
    ([5], 5)                 # 单人场景
]

print("测试结果：")
for times, expected in test_cases:
    result = min_bridge_time(times)
    print(f"人员: {times} → 计算时间: {result}分钟 | 预期: {expected}分钟 → {'正确' if result == expected else '错误'}")