import matplotlib.pyplot as plt
import numpy as np
from scipy.spatial.distance import cdist

def rolling_ball_concave_hull(points, R=1.0):
    points = sorted(points, key=lambda p: (p[1], p[0]))  # 按Y升序，X升序排序
    hull = [points[0]]  # 起点
    used = [False] * len(points)
    used[0] = True
    current_index = 0
    
    while True:
        candidates = []
        for i, (p, u) in enumerate(zip(points, used)):
            if not u and np.linalg.norm(np.array(p) - np.array(points[current_index])) <= R:
                candidates.append((i, p))
        
        if not candidates:  # 无候选点则增大半径
            R *= 1.5
            continue
        
        # 计算角度增量并选择最小增量点
        angles = []
        for i, p in candidates:
            vector = np.array(p) - np.array(points[current_index])
            angle = np.arctan2(vector[1], vector[0])  # 向量角度
            angles.append(angle)
        next_index = candidates[np.argmin(angles)][0]
        
        hull.append(points[next_index])
        used[next_index] = True
        current_index = next_index
        
        if current_index == 0:  # 回到起点，闭合凹包
            break
    return hull


def angle_binning_concave_hull(points, k=30):
    center = np.mean(points, axis=0)  # 参考点
    bins = np.linspace(0, 2*np.pi, k, endpoint=False)  # 角度区间
    
    hull_points = []
    for i in range(k):
        bin_start = bins[i]
        bin_end = bins[(i+1) % k]
        
        candidates = []
        for p in points:
            dx, dy = p[0] - center[0], p[1] - center[1]
            angle = np.arctan2(dy, dx) % (2*np.pi)
            if bin_start <= angle < bin_end or (i == k-1 and angle >= bin_end):
                dist = dx**2 + dy**2
                candidates.append((dist, p))
        
        if candidates:
            hull_points.append(max(candidates, key=lambda x: x[0])[1])
    
    return hull_points



# 测试样例1：规则矩形
points1 = [(0, 0), (0, 5), (5, 5), (5, 0), (2, 2), (3, 3)]
hull1 = rolling_ball_concave_hull(points1, R=1.5)
print("测试1-凹包点:", hull1)  # 预期: [(0,0), (0,5), (5,5), (5,0)]

# 测试样例2：带凹陷
points2 = [(0, 0), (0, 6), (3, 6), (4, 4), (6, 6), (6, 0), (3, 2)]
hull2 = rolling_ball_concave_hull(points2, R=2.0)
print("测试2-凹包点:", hull2)  # 预期包含凹陷点(4,4)

# 测试样例3：稀疏分布
points3 = [(1, 1), (1, 10), (10, 10), (10, 1), (5, 5)]
hull3 = rolling_ball_concave_hull(points3, R=6.0)
print("测试3-凹包点:", hull3)  # 预期: 外部矩形点

# 可视化验证
def plot_hull(points, hull, title):
    plt.figure(figsize=(8, 6))
    x, y = zip(*points)
    plt.scatter(x, y, c='blue', label='原始点')
    hx, hy = zip(*hull)
    plt.plot(hx + (hx[0],), hy + (hy[0],), 'ro-', label='凹包边界')
    plt.title(title)
    plt.legend()
    plt.grid(True)
    plt.show()

plot_hull(points2, hull2, "带凹陷的凹包测试")