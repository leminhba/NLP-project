#importing required libraries

from gensim import corpora
from collections import defaultdict
from gensim import similarities
from gensim import models
#documents

docs = ["đề_xuất ubnd tỉnh bố_trí kinh_phí để tu_sửa khắc_phục các công_trình bị hư_hỏng xuống_cấp",
       "việc xây_dựng numbertoken chuỗi giá_trị sản_phẩm nằm trong đề_án tái_cơ_cấu ngành nông_nghiệp tiến_độ còn chậm",
       "việc lồng_ghép nguồn vốn thực_hiện còn khó_khăn hạn_chế dẫn đến tiến_độ triển_khai trên toàn tỉnh nhìn_chung đến nay còn chậm",
       "tình_hình vi phạm_luật bảo_vệ rừng còn diễn_biến phức_tạp phát_sinh điểm_nóng nhất là các khu rừng đặc_dụng còn nhiều nhóm gỗ quý_hiếm"]
#creating a list of stopwords
stoplist = set('for a of the and to in'.split())
#removing the stop words
txts = [[word for word in document.lower().split() if word not in stoplist]for document in docs]
#calculating frequency of each text
frequency = defaultdict(int)
for text in txts:
    for token in text:
        frequency[token] += 1

# removing words that appear only once
txts = [[token for token in text if frequency[token] > 1] for text in txts]
#creating a dictionary
gensim_dictionary = corpora.Dictionary(txts)
#vectorizing the corpus
gensim_corpus = [gensim_dictionary.doc2bow(text) for text in txts]
#creating LSI model
lsi = models.LsiModel(gensim_corpus, id2word=gensim_dictionary, num_topics=4)
#query

doc = "lồng_ghép công_tác quản_lý bảo_vệ rừng còn hạn_chế"
#creating bow vector
vec_bow = gensim_dictionary.doc2bow(doc.lower().split())
#converting the query to LSI space
vec_lsi = lsi[vec_bow]
print("LSI vector\n",vec_lsi)
#transforming corpus to LSI space and index it
index = similarities.MatrixSimilarity(lsi[gensim_corpus])
#performing a similarity query against the corpus
simil = index[vec_lsi]
simil=sorted(list(enumerate(simil)),key=lambda item: -item[1])
#printing (document_number, document_similarity)
print("Similarity scores for each document\n", simil)
print("Similarity scores with document")

for doc_position, doc_score in simil:
    print(doc_score, docs[doc_position])