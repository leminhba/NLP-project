from gensim.models import Word2Vec
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Danh sách các câu cần loại trừ trùng nghĩa
sentences = [
    "Việc cụ thể hóa và tổ chức thực hiện các chính sách hỗ trợ sản xuất kinh doanh, liên kết sản xuất với tiêu thụ nông sản thực phẩm an toàn ở một số địa phương còn chậm, sản lượng và quy mô còn hạn chế.",
    "tổ chức sản xuất liên kết theo chuỗi giá trị giữa doanh nghiệp với nông dân, hợp tác xã chưa phổ biến và tỷ lệ giá trị liên kết còn thấp.",
    "Đổi mới và phát triển các hình thức tổ chức sản xuất có nhiều tiến bộ nhưng vẫn chưa đáp ứng yêu cầu.",
    "Công tác đổi mới, phát triển các hình thức tổ chức sản xuất chưa đáp ứng được yêu cầu, còn nhiều lúng túng.",
    "hoạt động liên kết theo chuỗi giá trị giữa doanh nghiệp với nông dân, hợp tác xã chưa thật sự phổ biến và tỷ lệ giá trị liên kết còn thấp.",
    "Bên cạnh đó đất canh tác bị suy thoái với tốc độ nhanh, diễn biến thời tiết ngày càng phức tạp, dẫn đến sản xuất nông nghiệp nói chung và cây trồng nói riêng gặp nhiều khó khăn",

]

# Preprocess and tokenize the sentences
tokenized_sentences = [sentence.split() for sentence in sentences]

# Train a Word2Vec model on the sentences
model = Word2Vec(tokenized_sentences, vector_size=100, window=5, min_count=1, sg=0)

# Function to calculate cosine similarity between two vectors
def calculate_cosine_similarity(vector1, vector2):
    return cosine_similarity([vector1], [vector2])[0][0]

# Create vectors for each sentence using the Word2Vec model
sentence_vectors = [np.mean([model.wv[word] for word in sentence], axis=0) for sentence in tokenized_sentences]

# Initialize a list to keep track of which sentences to exclude
exclude_indices = []

# Compare each sentence to all other sentences
for i in range(len(sentences)):
    if i in exclude_indices:
        continue
    for j in range(i + 1, len(sentences)):
        if j in exclude_indices:
            continue
        similarity = calculate_cosine_similarity(sentence_vectors[i], sentence_vectors[j])
        # If the similarity is above a certain threshold, mark the sentence for exclusion
        if similarity > 0.7:
            exclude_indices.append(j)

# Create a list of unique sentences
unique_sentences = [sentences[i] for i in range(len(sentences)) if i not in exclude_indices]

# Print the unique sentences
for sentence in unique_sentences:
    print(sentence)

#viết biểu thức regrex để cắt chuỗi số bắt đầu bằng con số 1,2,3,4,5,6,7,8,9,0 hoặc số La Mã và sau đó phải có chữ "điều"
#doc_splitter = re.compile(r'([1-9]+[0-9]*|[MDCLXVI]+)\s*[:]\s*')





