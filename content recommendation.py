import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

# Dữ liệu sách và mô tả (giả định)
data = {
    'title': [
        'Introduction to Machine Learning',
        'Data Science for Beginners',
        'Python Programming Guide',
        'Artificial Intelligence: A Modern Approach'
    ],
    'description': [
        'A comprehensive guide to machine learning techniques.',
        'Learn the basics of data science with practical examples.',
        'Master Python programming with hands-on exercises.',
        'Explore the field of artificial intelligence and its applications.'
    ]
}

books_df = pd.DataFrame(data)

# Người đọc đã đọc các sách
read_books = ['Introduction to Machine Learning', 'Python Programming Guide']

# Tính toán TF-IDF cho mô tả sách
vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(books_df['description'])

# Tính độ tương đồng cosine giữa mô tả sách và sách đã đọc
cosine_similarities = linear_kernel(tfidf_matrix, tfidf_matrix)

# Gợi ý sách dựa trên sách đã đọc
def recommend_books(book_title, cosine_similarities=cosine_similarities, books_df=books_df):
    book_index = books_df.index[books_df['title'] == book_title].tolist()[0]
    similar_books = list(enumerate(cosine_similarities[book_index]))
    similar_books = sorted(similar_books, key=lambda x: x[1], reverse=True)
    similar_books = similar_books[1:4]  # Lấy 3 sách giống nhất
    recommended_books = [books_df.iloc[i[0]]['title'] for i in similar_books]
    return recommended_books

# Gợi ý sách cho người đọc
for book in read_books:
    recommendations = recommend_books(book)
    print(f"For '{book}': Recommended Books: {recommendations}")
