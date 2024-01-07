import pandas as pd
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

# Function for basic text cleaning
def clean_text(text):
    # Removing special characters and digits
    text = re.sub(r'[^a-zA-ZÀ-ỹ\s]', '', text, re.I|re.A)
    # Converting to lower case
    text = text.lower()
    return text

# Load the Excel file
file_path = 'D:/cau_kho_khan.xls'  # Replace with your file path
data = pd.read_excel(file_path)

# Clean the sentences
data['cleaned_sentence'] = data['sentence_contain_keywords'].apply(clean_text)

# Convert text to numerical data using TF-IDF
vectorizer = TfidfVectorizer(max_features=1000)
X = vectorizer.fit_transform(data['cleaned_sentence'])

# Apply K-Means clustering
# Assuming an arbitrary number of clusters, for example, 5
n_clusters = 5
kmeans = KMeans(n_clusters=n_clusters, random_state=0).fit(X)

# Add the cluster labels to the dataframe
data['cluster'] = kmeans.labels_

# Optionally, save the dataframe with cluster labels to an Excel file
output_file_path = 'D:/cau_kho_khan_ket_qua.xlsx'  # Replace with your desired output file path
data.to_excel(output_file_path, index=False)

print("Clustering completed. Results saved to:", output_file_path)
