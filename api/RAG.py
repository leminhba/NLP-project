from flask import Blueprint, request, jsonify
import urllib.parse

from langchain_community.vectorstores import Chroma
from langchain.retrievers import ParentDocumentRetriever
from langchain_community.llms import KoboldApiLLM

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.storage import InMemoryStore
from langchain_community.document_loaders import TextLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
from main_model.model.pipeline import *
from main_model.config.read_config import *
from main_model.util.general_normalize import _clean_text_remove_token
from main_model.util.io_util import *
from main.handle_information import *



file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)
config = read_config_file()
RAG_blueprint = Blueprint('RAG', __name__)


@RAG_blueprint.route('/RAG', methods=['GET'])

def doc_retriever():
    # Kiểm tra xem tham số 'id' có được truyền vào không
    if 'id' not in request.args:
        return jsonify({'error': 'Thiếu tham số id'}), 400  # Trả về mã lỗi 400 Bad Request

    # Lấy giá trị của tham số 'id' từ request
    doc_id = request.args.get('id')

    # Kiểm tra xem giá trị của 'id' có hợp lệ không
    if not doc_id.isdigit():  # chỉ chấp nhận số
        return jsonify({'error': 'Tham số id không hợp lệ'}), 400  # Trả về mã lỗi 400 Bad Request

    db = config['test_db2']
    sp = """SET NOCOUNT ON; EXEC DocUpload_by_id {0}; """.format(doc_id)
    df = read_data_type_db2(db, sp)
    # Sử dụng phương thức apply để chia chuỗi trong mỗi hàng và thêm đường dẫn "
    file_paths = df['Files'].apply(lambda x: [item for item in x.split(';')])
    model_name = "BAAI/bge-small-en-v1.5"
    encode_kwargs = {'normalize_embeddings': True}  # set True to compute cosine similarity
    bge_embeddings = HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs={'device': 'cuda'},
        encode_kwargs=encode_kwargs
    )
    docs = []
    for file_path in file_paths:
        for path in file_path:
            if path:
                path = 'D:/Laptrinh/GSDG/GSDGNganh/MIC/Upload/' + path
                loader = TextLoader(path, encoding='utf-8')
                docs.extend(loader.load())

    # This text splitter is used to create the parent documents - The big chunks
    parent_splitter = RecursiveCharacterTextSplitter(chunk_size=2000)

    # This text splitter is used to create the child documents - The small chunks
    # It should create documents smaller than the parent
    child_splitter = RecursiveCharacterTextSplitter(chunk_size=400)

    # The vectorstore to use to index the child chunks
    vectorstore = Chroma(collection_name="split_parents", embedding_function=bge_embeddings)

    # The storage layer for the parent documents
    store = InMemoryStore()
    big_chunks_retriever = ParentDocumentRetriever(
        vectorstore=vectorstore,
        docstore=store,
        child_splitter=child_splitter,
        parent_splitter=parent_splitter,
    )
    big_chunks_retriever.add_documents(docs)
    if 'kw' not in request.args:
        return jsonify({'error': 'Thiếu tham số kw'}), 400  # Trả về mã lỗi 400 Bad Request
    question = urllib.parse.unquote(request.args.get('kw'))


    # retrieved_docs = doc_retriever.get_relevant_documents(question)
    type = urllib.parse.unquote(request.args.get('type'))
    if type == "0":
        sub_docs = vectorstore.similarity_search(question, k=10)
        # Trả về danh sách các dictionary
        result = [
            {'context': document.page_content, 'answer': '', 'document': document.metadata['source']} for
            document in sub_docs]

        #result = {'context': sub_docs[0].page_content, 'answer': '', 'document': sub_docs[0].metadata['source']}
    else:
        sub_docs = vectorstore.similarity_search(question)
        llm = KoboldApiLLM(endpoint="http://localhost:5001/", max_length=280)
        response = llm(
            f"### Instruction:\nSử dụng ngữ cảnh sau đây để trả lời câu hỏi. Nếu bạn không biết câu trả lời, chỉ cần nói rằng bạn không biết, đừng cố bịa ra câu trả lời.\n Câu hỏi như sau:{question}?\nNgữ cảnh:{sub_docs[0].page_content} ### Response:")
        result = {'context': sub_docs[0].page_content, 'answer': response, 'document': sub_docs[0].metadata['source']}
    return json.dumps(result, ensure_ascii=False)