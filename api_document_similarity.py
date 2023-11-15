import itertools
import logging
import urllib.parse
import numpy as np
import matplotlib.pyplot as plt
import gensim
from gensim import similarities
from gensim.utils import simple_preprocess
from gensim import models
from flask import Flask, redirect, url_for, request,jsonify

from main_model.model.pipeline import *
from main_model.config.read_config import *
from main_model.util.general_normalize import _clean_text, __remove_token
from main_model.util.io_util import *
from main.handle_information import *
from distances import get_most_similar_documents
import json
import requests
logging.basicConfig(format='%(levelname)s : %(message)s', level=logging.INFO)
logging.root.level = logging.INFO


PATH_DICTIONARY = "models/id2word.dictionary"
PATH_CORPUS = "models/corpus.mm"
PATH_LDA_MODEL = "models/LDA.model"
PATH_DOC_TOPIC_DIST = "models/doc_topic_dist.dat"


def pre_process_table(df):
    content_col = 'ind_name_vn'
    df['clean_content'] = df.apply(lambda row: _clean_text(row[content_col]), axis=1)
    df.rename(columns={'ind_name_vn':'sentence_contain_keywords'}, inplace=True)
    return df


app = Flask(__name__)
@app.route("/main", methods=['GET'])
def main():
    # TODO
    import torch
    from transformers import AutoModel, AutoTokenizer
    model = AutoModel.from_pretrained("vinai/phobert-base-v2")
    tokenizer = AutoTokenizer.from_pretrained("vinai/phobert-base-v2")
    file_dir = os.path.dirname(__file__)
    sys.path.append(file_dir)
    config = read_config_file()
    if request.args.get('t') == "1": #lay danh sach chi so
        sp = """EXEC list_indicator """
        db = config['test_db2']
        df_extract = read_data_type_db2(db, sp)
        df_extract = pre_process_table(df_extract)
    else:  #lay theo session
        db = config['test_db']
        params = ('20230502_22-17-06')
        sp = """SET NOCOUNT ON; EXEC temp_output_by_session_id '{0}'; """.format(params)
        df_extract = read_data_type_db2(db, sp)
        #df_extract = read_data('excel', path_data='qa.xls')
        df_extract = pre_process_df(df_extract)

    user_query = _clean_text(urllib.parse.unquote(request.args.get('kw')))
    user_query = __remove_token(user_query)

    if request.args.get('m') == "bert":

        # Tokenize and encode the documents
        document_embeddings = []
        for document in df_extract['clean_content']:
            inputs = tokenizer(document, return_tensors="pt", padding=True, truncation=True)
            with torch.no_grad():
                outputs = model(**inputs)
            document_embedding = outputs.last_hidden_state.mean(dim=1)  # Average over tokens
            document_embeddings.append(document_embedding)
        document_embeddings = torch.cat(document_embeddings)

        user_query_inputs = tokenizer(user_query, return_tensors="pt", padding=True, truncation=True)
        with torch.no_grad():
            user_query_outputs = model(**user_query_inputs)
        user_query_embedding = user_query_outputs.last_hidden_state.mean(dim=1)

        from sklearn.metrics.pairwise import cosine_similarity

        # Calculate cosine similarity between the user query and all documents
        similarities = cosine_similarity(user_query_embedding, document_embeddings)
        df = pd.DataFrame(similarities.T, columns=['score'])
        df = df.join(df_extract['sentence_contain_keywords'])
        #cắt các dòng có cột nhỏ hơn 0.5
        df = df[df['score'] > 0.5]
        #sắp xếp theo score giảm dần
        df = df.sort_values(by=['score'], ascending=False)
        # reset index sau khi sắp xếp để có giá trị index liên tục
        df = df.reset_index(drop=True)

        #newdf = df.sort_values(by=['score'], ascending=False)
        return json.dumps(df.to_dict('records'), ensure_ascii=False)
    else:

        doc_tokenized = [simple_preprocess(doc) for doc in df_extract['clean_content']]
        id2word = gensim.corpora.Dictionary(doc_tokenized)
        id2word.filter_extremes(no_below=5, no_above=0.5)
        id2word.compactify()

    # save dictionary
    #id2word.save(PATH_DICTIONARY)

    #ictionary = gensim.corpora.Dictionary()
        corpus = [id2word.doc2bow(doc, allow_update=True) for doc in doc_tokenized]

    #corpus = StreamCorpus(doc_tokenized, id2word)
    # Term Document Frequency
    #corpus = [id2word.doc2bow(text) for text in sentences]
    # save corpus
    #gensim.corpora.MmCorpus.serialize(PATH_CORPUS, corpus)
    # load corpus
    # mm_corpus = gensim.corpora.MmCorpus('path_to_save_file.mm')

        if request.args.get('m') == "lsa":
            model = models.LsiModel(corpus, num_topics=4, id2word=id2word)
        else:
            model = models.LdaModel(corpus, num_topics=15, id2word=id2word)
        # Chuyển câu thành dạng vector BoW

        query_bow = id2word.doc2bow(user_query.split())
        # Chuyển câu cần so sánh thành dạng vector topic
        query_lda = model[query_bow]

        # Tạo một ma trận tương đồng sử dụng mô hình LDA/LSA
        index = gensim.similarities.MatrixSimilarity(model[corpus])

        # Tính tương tự giữa câu cần so sánh và các câu trong tập dữ liệu
        simil = index[query_lda]
        simil = sorted(list(enumerate(simil)), key=lambda item: -item[1])

        #print("Similarity scores for each document\n", simil)
        #print("Similarity scores with document")
        data = []
        for doc_position, doc_score in simil:
            data.append({"sentence_contain_keywords": df_extract['sentence_contain_keywords'][doc_position], "score": str(doc_score)})
            #print(doc_score, df_extract['sentence_contain_keywords'][doc_position])
        return json.dumps(data, ensure_ascii=False)

@app.route("/extract_info", methods=['GET'])
def extract_info():
    if 'command_api' in request.args:
        command_api = request.args['command_api']
        # try:
        data = main_process_info(command_api)
        return data
    else:
        return "Error: No command_api field provided. Please specify an command_api."


@app.route("/extract", methods=['GET'])
def extract():
    if 'command_api' in request.args:
        command_api = request.args['command_api']
        type_exp = request.args['type_export']
        type_ext = request.args['type_extract']
        split_sent = request.args['split_sentence']
        # try:
        data = main_process(command_api, number_skipping_words=0, type_export=type_exp, type_extract=type_ext, split_sentence=split_sent)
        return data
    else:
        return "Error: No command_api field provided. Please specify an command_api."


@app.route("/import_label_studio", methods=['GET'])
def import_label_studio():
    headers = {"Content-Type": "application/json", "Authorization": "Token 736f5d228135dc5bd11f74d4fd890369e719417d"}
    config = read_config_file()
    table_name = config['input_table_name']
    where_stm = 'WHERE session_id = \'' + request.args.get('session_id') + '\''
    # df_extract = read_data(type_data='sql_server', config=config, path_data=None)
    df_extract = read_data_type_db(config, table_name, where_stm)
    api_url = "http://localhost:8080/api/projects/" + request.args.get('p') + "/import"
    data = []
    for doc in df_extract['sentence_contain_keywords']:
        data.append(
            {"text": doc, "question": ""})
    response = requests.post(api_url, data=json.dumps(data), headers=headers)
    return 'Đã import thành công'

@app.route("/project_label_studio", methods=['GET'])
def project_label_studio():
    #cho vao file config
    headers = {"Content-Type": "application/json", "Authorization": "Token 736f5d228135dc5bd11f74d4fd890369e719417d"}
    api_url = "http://localhost:8080/api/projects/"
    response = requests.post(api_url, headers=headers)
    response.json()
    return 'Đã import thành công'

if __name__ == '__main__':
    app.run(debug=True)
