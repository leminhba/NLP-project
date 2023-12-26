from rank_bm25 import BM25Okapi
import pandas as pd

# Tập dữ liệu văn bản
documents = [
    "Machine learning is a subfield of artificial intelligence.",
    "Natural language processing deals with the interaction between computers and humans using natural language.",
    "Deep learning is a subset of machine learning that focuses on neural networks.",
    "Reinforcement learning is a type of machine learning where an agent learns to make decisions by interacting with an environment.",
    "The Internet of Things (IoT) connects devices and allows them to communicate with each other over the internet."
]

# Tạo mô hình BM25 từ tập dữ liệu
bm25 = BM25Okapi([document.split() for document in documents])

# Truy vấn
query = "what is deep learning"

# Tìm kiếm thông tin với BM25
scores = bm25.get_scores(query.split())
# Create a DataFrame to store results
result_df = pd.DataFrame({'sentence_contain_keywords': "a", 'score': scores})

# Xếp hạng các văn bản dựa trên điểm số BM25
ranked_documents = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)

# Hiển thị kết quả
print("Search results for query '{}':".format(query))
for i, score in ranked_documents:
    print(f"Document {i+1}: {documents[i]} - BM25 Score: {score:.4f}")
