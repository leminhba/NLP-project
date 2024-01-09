from main_model.model.pipeline import *
from main_model.config.read_config import *
from main_model.util.general_normalize import _clean_text_remove_token
from main_model.util.io_util import *
from main.handle_information import *
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import pairwise_distances_argmin_min
from kneed import KneeLocator


file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)
config = read_config_file()
db = config['test_db']
params = ('20231129_15-04-27')
sp = """SET NOCOUNT ON; EXEC temp_output_by_session_id '{0}'; """.format(params)
df = read_data_type_db2(db, sp)

# Load the Excel file
#file_path = 'D:/cau_kho_khan.xls'  # Replace with your file path
#df = pd.read_excel(file_path)
#new_df = df
#new_df['clean_content'] = new_df.apply(lambda row: _clean_text_remove_token(row['sentence_contain_keywords']), axis=1)
new_df = pre_process_df2(df)
# Gán tên cho mỗi nhóm bằng cách so sánh với tên mẫu
sentences = new_df['clean_content']
# Convert text to numerical data using TF-IDF
vectorizer = TfidfVectorizer(max_features=1000)
sentence_vectors = vectorizer.fit_transform(sentences)

# Tìm số lượng nhóm tối ưu bằng phương pháp Elbow

num_clusters_range = range(3, 15)
inertia_values = []

for num_clusters in num_clusters_range:
    kmeans = KMeans(n_clusters=num_clusters)
    kmeans.fit(sentence_vectors)
    inertia_values.append(kmeans.inertia_)

# Use the KneeLocator to find the elbow point
knee_locator = KneeLocator(num_clusters_range, inertia_values, curve='convex', direction='decreasing')
n_clusters_optimal = knee_locator.elbow

# Vẽ biểu đồ Elbow
plt.plot(num_clusters_range, inertia_values, marker='o')
plt.title('Elbow Method for Optimal k')
plt.xlabel('Number of Clusters (k)')
plt.ylabel('Inertia')
plt.vlines(n_clusters_optimal, plt.ylim()[0], plt.ylim()[1], linestyles='--', colors='r', label='Elbow Point')
plt.legend()
plt.show()

# Sử dụng K-Means để nhóm các câu
if n_clusters_optimal is None:
    num_clusters = 8
else:
    num_clusters = n_clusters_optimal

kmeans = KMeans(n_clusters=num_clusters)
kmeans.fit(sentence_vectors)

# Gán nhóm cho mỗi câu
new_df['cluster'] = kmeans.labels_


# Find the closest sentence to the centroid of each cluster
closest, _ = pairwise_distances_argmin_min(kmeans.cluster_centers_, sentence_vectors)
new_df['representative_sentence'] = new_df['cluster'].apply(lambda x: new_df['sentence_contain_keywords'].iloc[closest[x]])

# Count sentences in each cluster and sort clusters by this count
cluster_counts = new_df['cluster'].value_counts().sort_values(ascending=False)
sorted_clusters = cluster_counts.index.tolist()

# Group data by cluster and print the representative sentence and all sentences in each cluster
for cluster in sorted_clusters:
    cluster_sentences = new_df[new_df['cluster'] == cluster]['sentence_contain_keywords'].tolist()
    representative_sentence = new_df[new_df['cluster'] == cluster]['representative_sentence'].iloc[0]
    num_sentences = len(cluster_sentences)
    print(f"Nhóm {cluster}:  {representative_sentence} ({num_sentences} câu):")
    for sentence in cluster_sentences:
        print(f" - {sentence}")
    print("\n" + "-"*50 + "\n")

# Optionally, save the dataframe with cluster labels to an Excel file
#output_file_path = 'D:/cau_kho_khan_ket_qua_2.xlsx'  # Replace with your desired output file path
#new_df.to_excel(output_file_path, index=False)

