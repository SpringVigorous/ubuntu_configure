import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import ConvexHull

# 生成随机点
np.random.seed(42)
points = np.random.rand(50, 2)  # 50个二维点

# 计算凸包
hull = ConvexHull(points)
vertices = points[hull.vertices]  # 凸包顶点坐标

# 可视化
plt.figure(figsize=(8, 6))
plt.plot(points[:, 0], points[:, 1], 'o', label='原始点')
for index,point in enumerate(points):  # 绘制点编号
    plt.text(point[0], point[1], str(index))

plt.plot(vertices[:, 0], vertices[:, 1], 'r--', marker='o', label='凸包边界')
plt.fill(vertices[:, 0], vertices[:, 1], alpha=0.1)  # 填充凸包
plt.legend()
plt.title("SciPy 凸包计算")
plt.grid(True)
plt.show()