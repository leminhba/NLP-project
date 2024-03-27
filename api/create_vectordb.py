from flask import Blueprint, request

import urllib.parse

from main_model.model.pipeline import *
from main_model.config.read_config import *
from main_model.util.general_normalize import _clean_text_remove_token, remove_under_score
from main_model.util.io_util import *
from main.handle_information import *
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders import DataFrameLoader
from langchain_community.embeddings.sentence_transformer import (SentenceTransformerEmbeddings,)
from langchain.storage._lc_store import create_kv_docstore
from langchain.vectorstores.chroma import Chroma
from langchain.storage import LocalFileStore, InMemoryStore
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.retrievers import ParentDocumentRetriever
import pandas as pd
config = read_config_file()
create_vectordb_blueprint = Blueprint('create_vectordb', __name__)

def load_df():

    if request.args.get('t') == "chi_so":  # lay danh sach chi so
        db = config['test_db2']
        sp = """EXEC list_indicator """
        df = read_data_type_db2(db, sp)
        new_df = df[['ind_id', 'ind_name_vn']]
        new_df.rename(columns={'ind_id': 'id'}, inplace=True)
        return new_df, 'ind_name_vn'
    elif request.args.get('t') == "hoi_dap":  # hoi dap
        db = config['test_db2']
        sp = """EXEC list_qa """
        df = read_data_type_db2(db, sp)
        return df, 'question'
    elif request.args.get('t') == "quy_hoach":  # hoi dap
        db = config['test_db2']
        #sp = "DocUpload_by_cat"
        params = ('2')
        sp = """SET NOCOUNT ON; EXEC DocUpload_by_cat '{0}'; """.format(params)
        df = read_data_type_db2(db, sp)
        new_df = df[['id', 'Title', 'Files']]
        new_df['content'] = new_df['Files'].apply(lambda x: read_txt_file(x))
        #thay files bang content
        return new_df, 'content'


def replace_last_four_chars(string):
    if len(string) >= 4:
        return string[:-4] + 'txt'
    else:
        return 'txt'

def pre_process_table(df, content_col, id_col):
    df['clean_content'] = df.apply(lambda row: _clean_text_remove_token(row[content_col]), axis=1)
    df.rename(columns={content_col: 'sentence_contain_keywords'}, inplace=True)
    df.rename(columns={id_col: 'id'}, inplace=True)
    return df
@create_vectordb_blueprint.route('/create_vectordb', methods=['GET'])

def create_vectordb():
    collection_name = urllib.parse.unquote(request.args.get('t'))
    #model_name = "keepitreal/vietnamese-sbert"
    #model_name = "BAAI/bge-small-en-v1.5"
    model_name = "intfloat/multilingual-e5-small"
    encode_kwargs = {'normalize_embeddings': True}  # set True to compute cosine similarity
    bge_embeddings = HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs={'device': 'cuda'},
        encode_kwargs=encode_kwargs
    )

    df, content = load_df()

    loader = DataFrameLoader(df, page_content_column=content)
    documents = loader.load()
    # load it into Chroma
    persist_directory = "./chroma_db/" + collection_name
    # Kiểm tra xem thư mục tồn tại hay không
    if os.path.exists(persist_directory):
        # Nếu tồn tại, xóa nó đi
        shutil.rmtree(persist_directory)
        # create the open-source embedding function
    embedding_function = SentenceTransformerEmbeddings(model_name=model_name)

    if collection_name == "quy_hoach":
        #fs = LocalFileStore("./store_location")
        store = InMemoryStore()
        parent_splitter = RecursiveCharacterTextSplitter(chunk_size=5000)
        child_splitter = RecursiveCharacterTextSplitter(chunk_size=1500)
        vectorstore = Chroma(embedding_function=embedding_function, persist_directory=persist_directory)
        retriever = ParentDocumentRetriever(
            vectorstore=vectorstore,
            docstore=store,
            child_splitter=child_splitter,
            parent_splitter=parent_splitter,
        )
        retriever.add_documents(documents, ids=None)
    else:
        vectorstore = Chroma.from_documents(documents, persist_directory=persist_directory,
                             embedding=embedding_function)

    return "Đã xử lý thành công"
