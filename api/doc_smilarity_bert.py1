from flask import Blueprint, request
import torch
import urllib.parse
from transformers import AutoModel, AutoTokenizer
from main_model.model.pipeline import *
from main_model.config.read_config import *
from main_model.util.general_normalize import _clean_text_remove_token
from main_model.util.io_util import *
from main.handle_information import *
from sklearn.metrics.pairwise import cosine_similarity
model = AutoModel.from_pretrained("vinai/phobert-base-v2")
tokenizer = AutoTokenizer.from_pretrained("vinai/phobert-base-v2")

# Biến lưu câu hỏi và ngữ cảnh trước đó
previous_question = None
previous_context = None
loaded_df = None

file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)
config = read_config_file()
doc_similarity_blueprint = Blueprint('doc_similarity', __name__)

def pre_process_table(df):
    content_col = 'ind_name_vn'
    df['clean_content'] = df.apply(lambda row: _clean_text(row[content_col]), axis=1)
    df.rename(columns={'ind_name_vn':'sentence_contain_keywords'}, inplace=True)
    return df

def load_df():
    db = config['test_db']
    params = ('20230502_22-17-06')
    sp = """SET NOCOUNT ON; EXEC temp_output_by_session_id '{0}'; """.format(params)
    df = read_data_type_db2(db, sp)
    return pre_process_df(df)


def embedding(df):
    # Tokenize and encode the documents
    document_embeddings = []
    for document in df['clean_content']:
        inputs = tokenizer(document, return_tensors="pt", padding=True, truncation=True)
        with torch.no_grad():
            outputs = model(**inputs)
        document_embedding = outputs.last_hidden_state.mean(dim=1)  # Average over tokens
        document_embeddings.append(document_embedding)
    document_embeddings = torch.cat(document_embeddings)
    return document_embeddings

def embedding_query(user_query):
    user_query = _clean_text_remove_token(user_query)
    # Tokenize and encode the documents
    user_query_inputs = tokenizer(user_query, return_tensors="pt", padding=True, truncation=True)
    with torch.no_grad():
        user_query_outputs = model(**user_query_inputs)
    user_query_embedding = user_query_outputs.last_hidden_state.mean(dim=1)
    return user_query_embedding

def bert_simi(question):
    global loaded_df
    # Kiểm tra xem đã load dữ liệu chưa
    if loaded_df is None:
        # Nếu chưa load, thực hiện load và lưu vào biến toàn cục
        loaded_df = load_df()
    #loaded_context = embedding(loaded_df)
    #loaded_question = embedding_query(question)
    # Calculate cosine similarity between the user query and all documents
    similarities = cosine_similarity(embedding_query(question), embedding(loaded_df))
    df = pd.DataFrame(similarities.T, columns=['score'])
    df = df.join(loaded_df['sentence_contain_keywords'])
    # cắt các dòng có cột nhỏ hơn 0.5
    df = df[df['score'] > 0.5]
    # sắp xếp theo score giảm dần
    df = df.sort_values(by=['score'], ascending=False)
    # reset index sau khi sắp xếp để có giá trị index liên tục
    df = df.reset_index(drop=True)
    return json.dumps(df.to_dict('records'), ensure_ascii=False)

@doc_similarity_blueprint.route('/similarity', methods=['GET'])

def simi():
    question = urllib.parse.unquote(request.args.get('kw'))
    if request.args.get('m') == "bert":
        return bert_simi(question)
    else:
        return "Method not found"