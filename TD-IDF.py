import matplotlib.pyplot as plt
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from main_model.util.general_normalize import _clean_text_remove_token, remove_under_score
import pandas as pd
from nltk.tokenize import word_tokenize
# Bộ sưu tập các tài liệu
documents2 = [
        "Việc cụ thể hóa và tổ chức thực hiện các chính sách hỗ trợ sản xuất kinh doanh, liên kết sản xuất với tiêu thụ nông sản thực phẩm an toàn ở một số địa phương còn chậm, sản lượng và quy mô còn hạn chế",
        "Đổi mới và phát triển các hình thức tổ chức sản xuất có nhiều tiến bộ nhưng vẫn chưa đáp ứng yêu cầu",
        "Đất canh tác bị suy thoái với tốc độ nhanh, diễn biến thời tiết ngày càng phức tạp",
        "Công tác đổi mới, phát triển các hình thức tổ chức sản xuất chưa đáp ứng được yêu cầu, còn nhiều lúng túng",
        "Hoạt động liên kết theo chuỗi giá trị giữa doanh nghiệp với nông dân, hợp tác xã chưa thật sự phổ biến và tỷ lệ giá trị liên kết còn thấp",
        "Sản xuất nông nghiệp 6 tháng đầu năm diễn ra trong điều kiện thời tiết có có nhiều khó khăn",
        "Giá vật tư đầu vào, công lao động có xu hướng tăng cao nên hiệu quả kinh tế trong sản xuất thấp",
        "liên kết giữa người sản xuất và doanh nghiệp thiếu chặt chẽ, thiếu sự hài hòa về lợi ích giữa người sản xuất nên người dân sản xuất cầm chừng đảm bảo phục vụ nhu cầu của gia đình",
        "Do thời tiết đầu vụ xuân khô hạn nên đã ảnh hưởng đến tiến độ gieo trồng các cây trồng vụ xuân tại một số địa phương",
        "Giá thức ăn chăn nuôi, thủy sản thành phẩm có xu hướng giảm, tuy nhiên vẫn còn duy trì ở mức cao trong khi giá bán các sản phẩm chăn nuôi không ổn định",
        "Tình hình thời tiết đầu năm không thuận lợi, đầu vụ xuân xảy ra các đợt rét đậm, rét hại, cuối vụ thời tiết khô hạn kéo dài ảnh hưởng đến sinh trưởng và phát triển của cây trồng dẫn đến sản lượng vụ xuân bị thiếu hụt",
        "Tình hình dịch bệnh trên đàn vật nuôi chưa được kiểm soát triệt để, vẫn xảy ra tình trạng dịch bệnh bùng phát và lây lan tại một số địa phương",
        "Tình hình dịch bệnh trên đàn vật nuôi vẫn sảy ra tại một số địa phương",
        "Trong 6 tháng đầu năm thời tiết diễn biến phức tạp đầu năm rét đậm, rét hại, khô hạn, mưa đá và dông ảnh hưởng đến thời vụ gieo trồng và sinh trưởng của cây trồng",
        "Tình hình dịch bệnh trên đàn vật nuôi chưa được kiểm soát triệt để, vẫn sảy ra tình trạng dịch bệnh bùng phát và lây lan tại một số địa phương",
        "Giá phân bón tăng cao do giá nguyên liệu sản xuất đầu vào phân bón cao",
        "hạnh phúc chính là con đường mà ta đi", "Buổi họp mặt cảm động", "đêm chia tay vui vẻ"
    ]
# Đọc dữ liệu từ file Excel
df = pd.read_excel("cau_kho_khan.xls", usecols=[4])

#_clean_text_remove_token cho từng dòng của df

documents = df['sentence_contain_keywords'].apply(_clean_text_remove_token).tolist()
# Tokenize các từ trong danh sách
tokenized_words = []
for item in documents:
    tokens = word_tokenize(item)
    tokenized_words.extend(tokens)

# Xóa các từ trùng lặp bằng cách chuyển danh sách thành set và sau đó trở lại danh sách
unique_tokenized_words = list(set(tokenized_words))
# Sắp xếp danh sách theo thứ tự abc
sorted_tokenized_words = sorted(unique_tokenized_words)

#documents = [_clean_text_remove_token(doc) for doc in documents]

# Tính TF-IDF
vectorizer = TfidfVectorizer()
# fit_transform cho dataframe documents

tfidf_matrix = vectorizer.fit_transform(documents)

# Lấy danh sách các từ (đặc trưng)
features = vectorizer.get_feature_names_out()

# Chuyển ma trận TF-IDF thành mảng NumPy để dễ xử lý
tfidf_array = tfidf_matrix.toarray()

# Tính giá trị trung bình của TF-IDF cho mỗi từ qua tất cả các tài liệu
average_tfidf_values = np.mean(tfidf_array, axis=0)

# Sắp xếp theo thứ tự giảm dần
sorted_indices = np.argsort(-average_tfidf_values)

# Chọn số lượng từ quan trọng cần trích xuất
num_top_words = 10000
#remove_under_score cho từng từ trong features
features_new = remove_under_score(features)
top_words = [features_new[i] for i in sorted_indices[:num_top_words]]
# Sắp xếp theo thứ tự abc
top_words.sort()
# Lấy chỉ top 15 từ
top_indices = sorted_indices[:15]

# Ghi các từ quan trọng vào một tệp txt
output_file_path = "important_words.txt"
# ghi dạng unicode
with open(output_file_path, "w", encoding="utf-8") as output_file:
    output_file.write("\n".join(sorted_tokenized_words))

# Vẽ biểu đồ bar cho giá trị TF-IDF của top 15 từ
plt.figure(figsize=(10, 6))
plt.bar(np.array(features)[top_indices], average_tfidf_values[top_indices])
plt.title("Top 15 TF-IDF values across all documents")
plt.xlabel("Words")
plt.ylabel("Average TF-IDF Value")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.show()