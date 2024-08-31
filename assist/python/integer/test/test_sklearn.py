from sklearn.cluster import KMeans
from sklearn.datasets import make_blobs
import matplotlib.pyplot as plt

# 生成模拟数据
X, _ = make_blobs(n_samples=300, centers=4, random_state=0, cluster_std=0.999)
print(X)
# 创建 K-means 模型
kmeans = KMeans(n_clusters=8)

# 训练模型
kmeans.fit(X)

# 预测聚类标签
labels = kmeans.predict(X)

# 绘制结果
plt.scatter(X[:, 0], X[:, 1], c=labels, s=20, cmap='viridis')
centers = kmeans.cluster_centers_
plt.scatter(centers[:, 0], centers[:, 1], c='red', s=200, alpha=0.5)
plt.show()
print("done")