from .doc_smilarity import doc_similarity_blueprint,top_keywords_blueprint
from .RAG import RAG_blueprint
from .clustered_report import clustered
from .predict import predict_blueprint
from .extract import extract_blueprint
from .create_vectordb import create_vectordb_blueprint

def register_blueprints(app):
    app.register_blueprint(doc_similarity_blueprint)
    app.register_blueprint(top_keywords_blueprint)
    app.register_blueprint(clustered )
    app.register_blueprint(predict_blueprint)
    app.register_blueprint(extract_blueprint)
    app.register_blueprint(RAG_blueprint)
    app.register_blueprint(create_vectordb_blueprint)
