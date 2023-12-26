from .doc_smilarity import doc_similarity_blueprint,top_keywords_blueprint
from .greeting import user

def register_blueprints(app):
    app.register_blueprint(doc_similarity_blueprint)
    app.register_blueprint(top_keywords_blueprint)
