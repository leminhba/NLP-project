import numpy as np
from kneed import KneeLocator
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
# Tạo dữ liệu giả định
data = np.array([1, 2, 4, 7, 10, 12, 15, 18, 20, 25, 30])

# Tạo danh sách các giá trị k của K để kiểm tra
k_values = range(1, 11)

# Tạo danh sách để lưu giá trị WCSS (Within-Cluster-Sum-of-Squares)
wcss_values = []

# Tính WCSS cho mỗi giá trị k
for k in k_values:
    kmeans = KMeans(n_clusters=k)
    kmeans.fit(data.reshape(-1, 1))
    wcss_values.append(kmeans.inertia_)

# Sử dụng KneeLocator để tìm điểm khuỷu
knee = KneeLocator(k_values, wcss_values, curve='convex', direction='decreasing')

# Vẽ biểu đồ
plt.figure(figsize=(8, 6))
plt.plot(k_values, wcss_values, marker='o', linestyle='-', color='b')
plt.xlabel('K (Number of Clusters)')
plt.ylabel('WCSS (Within-Cluster-Sum-of-Squares)')
plt.title('Elbow Method')
plt.vlines(knee.elbow, plt.ylim()[0], plt.ylim()[1], linestyles='--', colors='r', label='Elbow Point')
plt.legend()
plt.show()

# In ra giá trị khuỷu
print(f"The elbow point is at K = {knee.elbow}")
