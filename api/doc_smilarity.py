from flask import Blueprint, request
from rank_bm25 import BM25Okapi
import urllib.parse

from main_model.model.pipeline import *
from main_model.config.read_config import *
from main_model.util.general_normalize import _clean_text_remove_token, remove_under_score
#from main_model.util.io_util import *
from main.handle_information import *
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd
from langchain.vectorstores.chroma import Chroma
from langchain_community.document_loaders import DataFrameLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.embeddings.sentence_transformer import (SentenceTransformerEmbeddings,)
from langchain_community.retrievers import BM25Retriever


# Biến lưu câu hỏi và ngữ cảnh trước đó
previous_question = None
previous_context = None
loaded_df = None
loaded_df2 = None
file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)
config = read_config_file()
doc_similarity_blueprint = Blueprint('doc_similarity', __name__)
top_keywords_blueprint = Blueprint('top_keywords', __name__)

def find_similar_questions_tfidf(query):
    global loaded_df2
    # Kiểm tra xem đã load dữ liệu chưa
    if loaded_df2 is None:
        # Nếu chưa load, thực hiện load và lưu vào biến toàn cục
        loaded_df2 = load_df()
    question_list = loaded_df2['clean_content'].tolist()
    # Initialize the TF-IDF vectorizer
    vectorizer = TfidfVectorizer()
    tfidf_matrix_query = vectorizer.fit_transform([query])
    tfidf_matrix = vectorizer.transform(question_list)

    # Calculate cosine similarity between the query and each question
    similarity_scores = cosine_similarity(tfidf_matrix_query, tfidf_matrix)[0]

    # Create a DataFrame to store results
    result_df = pd.DataFrame({'sentence_contain_keywords': loaded_df2['sentence_contain_keywords'].tolist(), 'score': similarity_scores})

    # Sort DataFrame by Similarity Score in descending order
    result_df = result_df.sort_values(by='score', ascending=False).reset_index(drop=True)

    return result_df


def find_similar_questions_bm25(query):
    loaded_df,bm25_model_filename = load_df()
    question_list = loaded_df['clean_content'].tolist()

    # Kiểm tra xem có mô hình BM25 đã được tạo và lưu trên ổ cứng chưa
    bm25_model_filename = "models/" + bm25_model_filename
    try:
        # Kiểm tra nếu ngày tháng của file nhỏ hơn 1 ngày thì nhảy sang except
        if (datetime.datetime.now() - datetime.datetime.fromtimestamp(os.path.getmtime(bm25_model_filename))).days < 1:
            # Nếu có, load mô hình BM25
            bm25 = joblib.load(bm25_model_filename)
            # néu khong co thi nhay sang except
        else: raise FileNotFoundError
    except FileNotFoundError:
        # Nếu chưa có mô hình BM25, tạo và lưu chúng
        bm25 = BM25Okapi([question.split() for question in question_list])
        joblib.dump(bm25, bm25_model_filename)

    # Tìm kiếm thông tin với BM25
    scores = bm25.get_scores(query.split())
    # Create a DataFrame to store results
    result_df = pd.DataFrame(
        {'sentence_contain_keywords': loaded_df['sentence_contain_keywords'].tolist(), 'score': scores, 'id': loaded_df['id'].tolist()})

    # Sort DataFrame by Score in descending order
    result_df = result_df.sort_values(by='score', ascending=False).reset_index(drop=True)
    # lấy 20 giá trị đạt điểm cao nhất
    result_df = result_df.head(20)
    return result_df
def extract_top_keywords(query, n=3):
    # Initialize the TF-IDF vectorizer
    vectorizer = TfidfVectorizer()

    # Fit and transform the query
    query_tfidf = vectorizer.fit_transform([query])

    # Get feature names and their corresponding TF-IDF values
    feature_names = vectorizer.get_feature_names_out()
    tfidf_values = query_tfidf.data

    # Sort feature names based on TF-IDF values
    sorted_indices = tfidf_values.argsort()[-n:][::-1]
    top_keywords = [feature_names[i] for i in sorted_indices]
    top_keywords = remove_under_score(top_keywords)
    return top_keywords

def pre_process_table(df, content_col, id_col):
    df['clean_content'] = df.apply(lambda row: _clean_text_remove_token(row[content_col]), axis=1)
    df.rename(columns={content_col: 'sentence_contain_keywords'}, inplace=True)
    df.rename(columns={id_col: 'id'}, inplace=True)
    return df

def load_df():

    if request.args.get('t') == "chi_so":  # lay danh sach chi so
        db = config['test_db2']
        sp = """EXEC list_indicator """
        df = read_data_type_db2(db, sp)
        model_filename = "bm25_ind.joblib"
        return pre_process_table(df, 'ind_name_vn', 'ind_id'), model_filename
    elif request.args.get('t') == "hoi_dap":  # hoi dap
        db = config['test_db2']
        sp = """EXEC list_qa """
        df = read_data_type_db2(db, sp)
        model_filename = "bm25_qa.joblib"
        return pre_process_table(df, 'question', 'qa_id'), model_filename
    elif request.args.get('t') == "quy_hoach":  # hoi dap
        db = config['test_db2']
        #sp = "DocUpload_by_cat"
        params = ('2')
        sp = """SET NOCOUNT ON; EXEC DocUpload_by_cat '{0}'; """.format(params)
        df = read_data_type_db2(db, sp)
        #df = exec_sp_select(db, sp, params)
        model_filename = "bm25_qh.joblib"
        return pre_process_table(df, 'Files', 'id', 'Title'), model_filename
    else:  # lay theo session
        db = config['test_db']
        params = ('20230502_22-17-06')
        sp = """SET NOCOUNT ON; EXEC temp_output_by_session_id '{0}'; """.format(params)
        df = read_data_type_db2(db, sp)
        model_filename = "bm25_session.joblib"
        return pre_process_df2(df), model_filename


def bert_simi(question):
    #model_name = "BAAI/bge-small-en-v1.5"
    #model_name = "keepitreal/vietnamese-sbert"
    model_name = "intfloat/multilingual-e5-small"
    encode_kwargs = {'normalize_embeddings': True}  # set True to compute cosine similarity
    bge_embeddings = HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs={'device': 'cuda'},
        encode_kwargs=encode_kwargs
    )


    # create the open-source embedding function
    embedding_function = SentenceTransformerEmbeddings(model_name=model_name)
    collection_name = urllib.parse.unquote(request.args.get('t'))
    # load it into Chroma
    persist_directory = "./chroma_db/" + collection_name
    vectorstore = Chroma(persist_directory=persist_directory,
                             embedding_function=embedding_function)


    docs = vectorstore.similarity_search_with_score(question, k=10)

    # Trả về danh sách các dictionary
    documents_and_scores = [{'sentence_contain_keywords': document.page_content, 'score': score, 'id': document.metadata['id']} for document, score in docs]

    return json.dumps(documents_and_scores, ensure_ascii=False)
@doc_similarity_blueprint.route('/similarity', methods=['GET'])

def simi():
    question = urllib.parse.unquote(request.args.get('kw'))
    question = _clean_text_remove_token(question)
    if request.args.get('m') == "bert":
        return bert_simi(question)
    elif request.args.get('m') == "bm25":
        return json.dumps(find_similar_questions_bm25(question).to_dict('records'), ensure_ascii=False)
    else:
        return json.dumps(find_similar_questions_tfidf(question).to_dict('records'), ensure_ascii=False)

@top_keywords_blueprint.route('/top_keywords', methods=['GET'])

def top_keywords():
    question = urllib.parse.unquote(request.args.get('kw'))
    question = _clean_text_remove_token(question)
    return json.dumps(extract_top_keywords(question, n=5), ensure_ascii=False)



def create_vectordb():
    collection_name = urllib.parse.unquote(request.args.get('t'))
    model_name = "keepitreal/vietnamese-sbert"
    encode_kwargs = {'normalize_embeddings': True}  # set True to compute cosine similarity
    bge_embeddings = HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs={'device': 'cuda'},
        encode_kwargs=encode_kwargs
    )

    loaded_df, file = load_df()
    df = loaded_df[['id', 'sentence_contain_keywords', 'clean_content', 'title']]
    loader = DataFrameLoader(df, page_content_column="sentence_contain_keywords")
    documents = loader.load()

    # create the open-source embedding function
    embedding_function = SentenceTransformerEmbeddings(model_name=model_name)
    # load it into Chroma
    persist_directory = "./chroma_db/" + collection_name
    # Kiểm tra xem thư mục tồn tại hay không
    if os.path.exists(persist_directory):
        # Nếu tồn tại, xóa nó đi
        shutil.rmtree(persist_directory)
    vectorstore = Chroma.from_documents(documents, persist_directory=persist_directory,
                             embedding=embedding_function)

    return "Đã xử lý thành công"
