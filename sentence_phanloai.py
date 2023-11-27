from main_model.model.pipeline import *
from main_model.config.read_config import *
from main_model.util.general_normalize import _clean_text_remove_token, clean_prefix_and_whitespace
from main_model.util.io_util import *
from main.handle_information import *
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
import numpy as np
import re


# Tải pre-trained Sentence-BERT model cho tiếng Việt
model = SentenceTransformer('distiluse-base-multilingual-cased-v2')
file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)
config = read_config_file()
db = config['test_db']
params = ('20231028_20-52-28')
sp = """SET NOCOUNT ON; EXEC temp_output_by_session_id '{0}'; """.format(params)
df = read_data_type_db2(db, sp)

new_df = extract_sentences(df)
new_df = pre_process_df(new_df)
# Danh sách từ khóa để phân loại
list_of_keywords = ["nông thôn mới", "phá rừng OR vi phạm Luật Lâm nghiệp", "liên kết sản xuất", "dịch bệnh",
                    "giá AND tăng", "tiêm phòng", "sạt lở OR thiên tai OR bão"]

# Tạo một từ điển để theo dõi câu đã được phân loại
classified_sentences = {keyword: {'sentences': [], 'count': 0} for keyword in list_of_keywords}
classified_sentences["khác"] = {'sentences': [], 'count': 0}


# Phân loại câu vào từng nhóm
for index,row in new_df.iterrows():
    sentence = row['sentence_contain_keywords']
    classified = False  # Đánh dấu câu đã được phân loại hay chưa

    for keyword in list_of_keywords:
        # Kiểm tra AND
        if "AND" in keyword:
            and_keywords = keyword.split("AND")
            if all(re.search(fr'\b{kw.strip()}\b', sentence.lower()) for kw in and_keywords):
                classified_sentences[keyword]['sentences'].append(clean_prefix_and_whitespace(sentence))
                classified_sentences[keyword]['count'] += 1
                classified = True
                break
        # Kiểm tra OR
        elif "OR" in keyword:
            or_keywords = keyword.split("OR")
            if any(re.search(fr'\b{kw.strip()}\b', sentence) for kw in or_keywords):
                classified_sentences[keyword]['sentences'].append(clean_prefix_and_whitespace(sentence))
                classified_sentences[keyword]['count'] += 1
                classified = True
                break
        # Kiểm tra từ đơn
        else:
            if re.search(fr'\b{keyword}\b', sentence):
                classified_sentences[keyword]['sentences'].append(clean_prefix_and_whitespace(sentence))
                classified_sentences[keyword]['count'] += 1
                classified = True
                break

    if not classified:
        classified_sentences["khác"]['sentences'].append(clean_prefix_and_whitespace(sentence))
        classified_sentences["khác"]['count'] += 1

# Sắp xếp nhóm theo số câu giảm dần
sorted_classified_sentences = sorted(classified_sentences.items(), key=lambda x: x[1]['count'], reverse=True)

# In kết quả
for keyword, group_info in sorted_classified_sentences:
    print(f"Nhóm '{keyword}': ({group_info['count']} câu)")
    for sentence in group_info['sentences']:
        print("-", sentence)
    print()

