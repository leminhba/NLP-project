import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

nlp = spacy.load("en_core_web_sm")
documents = [
    "Solar panels are a renewable energy source and are good for the environment.",
    "Wind turbines harness wind energy and generate electricity.",
    "Geothermal heating uses heat from the Earth to warm buildings.",
    "Hydropower is a sustainable energy source, relying on water flow for electricity generation.",
    # Add more documents as needed
]
# Tokenize and vectorize the documents
tfidf_vectorizer = TfidfVectorizer()
tfidf_matrix = tfidf_vectorizer.fit_transform(documents)
user_query = "What are the benefits of wind energy for the environment?"
query_vector = tfidf_vectorizer.transform([user_query])


# Calculate cosine similarity between the user query and all documents
cosine_similarities = cosine_similarity(query_vector, tfidf_matrix)

# Get the index of the most similar document
most_similar_document_index = cosine_similarities.argmax()
most_similar_document = documents[most_similar_document_index]
print("Most similar document:", most_similar_document)