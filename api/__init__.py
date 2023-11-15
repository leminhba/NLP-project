from .doc_smilarity import doc_similarity_blueprint

def register_blueprints(app):
    app.register_blueprint(doc_similarity_blueprint, url_prefix='/api')