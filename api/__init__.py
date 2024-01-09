from .doc_smilarity import doc_similarity_blueprint,top_keywords_blueprint
from .clustered_report import clustered

def register_blueprints(app):
    app.register_blueprint(doc_similarity_blueprint)
    app.register_blueprint(top_keywords_blueprint)
    app.register_blueprint(clustered )
