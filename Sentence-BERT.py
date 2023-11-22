from main_model.model.pipeline import *
from main_model.config.read_config import *
from main_model.util.general_normalize import _clean_text_remove_token
from main_model.util.io_util import *
from main.handle_information import *
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
import numpy as np
import matplotlib.pyplot as plt



# Tải pre-trained Sentence-BERT model cho tiếng Việt
model = SentenceTransformer('distiluse-base-multilingual-cased-v2')
file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)
config = read_config_file()
db = config['test_db']
params = ('20231028_20-52-28')
sp = """SET NOCOUNT ON; EXEC temp_output_by_session_id '{0}'; """.format(params)
df = read_data_type_db2(db, sp)

#viết hàm đọc một danh sách gồm 10 câu. Nếu câu nào thuộc một trong các từ khóa thì lấy câu đó
def extract_sentences(df):
    # Lấy danh sách các từ khóa
    keywords = get_keywords()
    # Tạo một cột mới để lưu các câu chứa từ khóa
    df['paragraph_contain_keywords'] = df.apply(lambda row: get_paragraph_contain_keywords(row['ind_name_vn'], keywords), axis=1)
    # Lấy các câu chứa từ khóa
    df = df[df['paragraph_contain_keywords'] != '']
    df = df.reset_index(drop=True)
    return df


def split_paragraph_to_sentences(df):
    # Phân tích cột  'paragraph_contain_keywords' thành từng câu dựa trên dấu . hoặc dấu ;
    df['sentence_contain_keywords'] = df['paragraph_contain_keywords'].apply(lambda x: sent_tokenize(x))
    # nếu câu có chiều dài < 10 thì bỏ, vì câu ngắn quá thì không có ý nghĩa
    df['sentence_contain_keywords'] = df['sentence_contain_keywords'].apply(lambda x: [i for i in x if len(i) > 10])
    df = df.explode('sentence_contain_keywords')
    df = df.reset_index(drop=True)
    return df


#new_df = split_paragraph_to_sentences(df)
new_df = extract_sentences(df)
new_df = pre_process_df(new_df)
cluster_names_samples = {
    0: "Giá vật tư đầu vào tăng",
    1: "Thời tiết",
    2: "Dịch bệnh",
    3: "Liên kết sản xuất",
    4: "Tổ chức sản xuất",
    5: "vi phạm về phá rừng",
    6: "ứng dụng công nghệ",
    7: "văn bản hướng dẫn",
    8: "kinh phí chưa đáp ứng",
}
# Gán tên cho mỗi nhóm bằng cách so sánh với tên mẫu
cluster_names = {}
sentences = new_df['sentence_contain_keywords']
# Biểu diễn vector của các câu
sentence_vectors = model.encode(sentences.tolist())
# Sử dụng K-Means để nhóm các câu
num_clusters = 8 # Số lượng nhóm mong muốn
kmeans = KMeans(n_clusters=num_clusters)
kmeans.fit(sentence_vectors)

# Gán nhóm cho mỗi câu
labels = kmeans.labels_


for i in range(num_clusters):
    cluster_sentences = [sentences[j] for j in range(len(sentences)) if labels[j] == i]

    # Tính toán tương đồng cosine giữa tên mẫu và các câu trong nhóm
    name_sample_vector = model.encode([cluster_names_samples[i]])[0]
    similarity_scores = np.inner(name_sample_vector, model.encode(cluster_sentences))

    # Chọn câu có tương đồng lớn nhất làm tên cho nhóm
    best_match_index = np.argmax(similarity_scores)
    cluster_names[i] = cluster_sentences[best_match_index]

# Đếm số lượng câu trong mỗi nhóm
#num_sentences_in_cluster = {i: sum(labels == i) for i in range(num_clusters)}

# Đếm số lượng câu trong mỗi nhóm
num_sentences_in_cluster = {}
for label in labels:
    num_sentences_in_cluster[label] = num_sentences_in_cluster.get(label, 0) + 1

# Sắp xếp nhóm theo số lượng câu giảm dần
sorted_clusters = sorted(num_sentences_in_cluster.items(), key=lambda x: x[1], reverse=True)

# Hiển thị kết quả sắp xếp
for cluster_label, num_sentences in sorted_clusters:
    cluster_name = cluster_names[cluster_label]
    cluster_sentences = [sentences[j] for j in range(len(sentences)) if labels[j] == cluster_label]

    print(f"Nhóm: {cluster_name} ({num_sentences} câu):")
    for sentence in cluster_sentences:
        print(f"  --- {sentence}")
    print()

# Thử nghiệm số lượng nhóm từ 1 đến 10
num_clusters_range = range(1, 11)
inertia_values = []

for num_clusters in num_clusters_range:
    kmeans = KMeans(n_clusters=num_clusters)
    kmeans.fit(sentence_vectors)
    inertia_values.append(kmeans.inertia_)

# Vẽ biểu đồ Elbow
plt.plot(num_clusters_range, inertia_values, marker='o')
plt.title('Elbow Method for Optimal k')
plt.xlabel('Number of Clusters (k)')
plt.ylabel('Inertia')
plt.show()