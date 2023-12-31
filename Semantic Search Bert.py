
import torch
from transformers import AutoModel, AutoTokenizer

model = AutoModel.from_pretrained("vinai/phobert-base-v2")
tokenizer = AutoTokenizer.from_pretrained("vinai/phobert-base-v2")

from main_model.model.pipeline import *
from main_model.config.read_config import *
from main_model.util.general_normalize import _clean_text,__remove_token
from main_model.util.io_util import *


config = read_config_file()
df_extract = read_data(type_data='sql_server', config=config, path_data=None,
                       where_stm='WHERE session_id = \'20230502_22-17-06\'')
df_extract = pre_process_df(df_extract)
documents = [
    "hân hoan",
    "hạnh phúc",
    "công thức",
    "xét nghiệm",
    "vui vẻ",
    # Add more documents as needed
]
# Tokenize and encode the documents
document_embeddings = []
#for document in df_extract['clean_content']:
for document in documents:
    inputs = tokenizer(document, return_tensors="pt", padding=True, truncation=True)
    with torch.no_grad():
        outputs = model(**inputs)
    document_embedding = outputs.last_hidden_state.mean(dim=1)  # Average over tokens
    document_embeddings.append(document_embedding)
document_embeddings = torch.cat(document_embeddings)

user_query = "vui vẻ"
user_query = _clean_text(user_query)
user_query = __remove_token(user_query)
user_query_inputs = tokenizer(user_query, return_tensors="pt", padding=True, truncation=True)
with torch.no_grad():
    user_query_outputs = model(**user_query_inputs)
user_query_embedding = user_query_outputs.last_hidden_state.mean(dim=1)

from sklearn.metrics.pairwise import cosine_similarity

# Calculate cosine similarity between the user query and all documents
similarities = cosine_similarity(user_query_embedding, document_embeddings)
df = pd.DataFrame(similarities.T, columns=['score'])
df = df.join(df_extract['sentence_contain_keywords'])
# cắt các dòng có cột nhỏ hơn 0.5
df = df[df['score'] > 0.5]
# sắp xếp theo score giảm dần
df = df.sort_values(by=['score'], ascending=False)
# reset index sau khi sắp xếp để có giá trị index liên tục
df = df.reset_index(drop=True)

# Print the document and the similarity score
for index, row in df.iterrows():
    print("Document: {}, Similarity score: {}".format(row['sentence_contain_keywords'], row['score']))


# Find the index of the most similar document
#most_similar_document_index = similarities.argmax()
#most_similar_document = df_extract['sentence_contain_keywords'][most_similar_document_index]
#print("Most similar document:", most_similar_document)

