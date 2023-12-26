from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from IPython.display import HTML
import pandas as pd

def highlight_keywords(query, text, keywords):
    highlighted_text = text
    for keyword in keywords:
        highlighted_text = highlighted_text.replace(keyword, f"<span style='color:red'>{keyword}</span>")
    return highlighted_text

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

    return top_keywords

def find_similar_questions_tfidf(query, question_list):
    # Initialize the TF-IDF vectorizer
    vectorizer = TfidfVectorizer()

    # Fit and transform the corpus (including the query)
    corpus = [query] + question_list
    tfidf_matrix = vectorizer.fit_transform(corpus)

    # Calculate cosine similarity between the query and each question
    similarity_scores = cosine_similarity(tfidf_matrix[0], tfidf_matrix[1:])[0]

    # Create a DataFrame to store results
    result_df = pd.DataFrame({'Question': question_list, 'Similarity Score': similarity_scores})

    # Sort DataFrame by Similarity Score in descending order
    result_df = result_df.sort_values(by='Similarity Score', ascending=False).reset_index(drop=True)

    # Extract and display the top 3 keywords in the query
    top_keywords = extract_top_keywords(query, n=3)
    print(f"Top 3 Keywords in Query: {', '.join(top_keywords)}")

    # Highlight keywords in the top matching question
    top_question = result_df.iloc[0]['Question']
    highlighted_text = highlight_keywords(query, top_question, top_keywords)

    # Display the highlighted text
    display(HTML(f"<strong>Query:</strong> {query}<br><strong>Top Matching Question:</strong> {highlighted_text}"))

    return result_df

# Example usage
query = "How to use machine learning for image recognition?"
question_list = [
    "What are some applications of machine learning?",
    "Can you explain the process of image recognition using machine learning?",
    "How does deep learning contribute to image recognition?",
    "What are the best practices for training a machine learning model for image recognition?"
]

result_df = find_similar_questions_tfidf(query, question_list)
print("Similarity Results:")
print(result_df)
