from flask import Blueprint, request
from main_model.model.pipeline import *
from main_model.config.read_config import *
from main_model.util.general_normalize import _clean_text_remove_token, remove_under_score
import urllib.parse
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics import pairwise_distances_argmin_min
import matplotlib.pyplot as plt

clustered = Blueprint('cluster', __name__)
config = read_config_file()

def load_df(session_id):
    db = config['test_db']
    #params = (session_id,)
    params = ('20231129_15-04-27')
    sp = """SET NOCOUNT ON; EXEC temp_output_by_session_id '{0}'; """.format(params)
    df = read_data_type_db2(db, sp)
    return pre_process_df2(df)


@clustered.route('/cluster')

def clustering():
    session_id = urllib.parse.unquote(request.args.get('s'))
    df = load_df(session_id)
    # Gán tên cho mỗi nhóm bằng cách so sánh với tên mẫu
    sentences = df['clean_content']
    # Convert text to numerical data using TF-IDF
    vectorizer = TfidfVectorizer(max_features=1000)
    sentence_vectors = vectorizer.fit_transform(sentences)

    num_clusters = int(urllib.parse.unquote(request.args.get('cluster')))
    kmeans = KMeans(n_clusters=num_clusters)
    kmeans.fit(sentence_vectors)
    # Gán nhóm cho mỗi câu
    df['cluster'] = kmeans.labels_

    # Extract feature names and cluster centers
    feature_names = vectorizer.get_feature_names_out()
    cluster_centers = kmeans.cluster_centers_

    # Identify top features (words) in each cluster
    top_n_features = 10  # Number of top features to retrieve for each cluster
    df['representative_sentence'] = df['cluster'].apply(
        lambda cluster: ", ".join(
            [feature_names[i] for i in cluster_centers[cluster].argsort()[-top_n_features:][::-1]])
    )

    '''
    # Find the closest sentence to the centroid of each cluster
    closest, _ = pairwise_distances_argmin_min(kmeans.cluster_centers_, sentence_vectors)
    df['representative_sentence'] = df['cluster'].apply(
        lambda x: df['sentence_contain_keywords'].iloc[closest[x]])
    '''
    # Count sentences in each cluster and sort clusters by this count
    cluster_counts = df['cluster'].value_counts().sort_values(ascending=False)
    sorted_clusters = cluster_counts.index.tolist()
    # Chuẩn bị dữ liệu kết quả theo định dạng JSON
    result = {"clusters": []}
    # Group data by cluster and print the representative sentence and all sentences in each cluster
    for cluster in sorted_clusters:
        cluster_sentences = df[df['cluster'] == cluster]['sentence_contain_keywords'].tolist()
        representative_sentence = df[df['cluster'] == cluster]['representative_sentence'].iloc[0]
        num_sentences = len(cluster_sentences)
        cluster_data = {
            "cluster_id": cluster,
            "representative_sentence": representative_sentence,
            "num_sentences": num_sentences,
            "sentences": cluster_sentences
        }

        result["clusters"].append(cluster_data)

    # Trả kết quả dưới dạng JSON
    return json.dumps(result)

def clustering_df(df):
    # Gán tên cho mỗi nhóm bằng cách so sánh với tên mẫu
    df = pre_process_df2(df, "sentence_contain_keywords")
    sentences = df['clean_content']
    # Convert text to numerical data using TF-IDF
    vectorizer = TfidfVectorizer(max_features=1000)
    sentence_vectors = vectorizer.fit_transform(sentences)

    num_clusters = 6
    kmeans = KMeans(n_clusters=num_clusters)
    kmeans.fit(sentence_vectors)
    # Gán nhóm cho mỗi câu
    df['cluster'] = kmeans.labels_

    # Extract feature names and cluster centers
    feature_names = vectorizer.get_feature_names_out()
    cluster_centers = kmeans.cluster_centers_

    # Identify top features (words) in each cluster
    top_n_features = 10  # Number of top features to retrieve for each cluster
    df['representative_sentence'] = df['cluster'].apply(
        lambda cluster: ", ".join(
            [feature_names[i] for i in cluster_centers[cluster].argsort()[-top_n_features:][::-1]])
    )

    '''
    # Find the closest sentence to the centroid of each cluster
    closest, _ = pairwise_distances_argmin_min(kmeans.cluster_centers_, sentence_vectors)
    df['representative_sentence'] = df['cluster'].apply(
        lambda x: df['sentence_contain_keywords'].iloc[closest[x]])
    '''
    # Count sentences in each cluster and sort clusters by this count
    cluster_counts = df['cluster'].value_counts().sort_values(ascending=False)
    sorted_clusters = cluster_counts.index.tolist()
    # Chuẩn bị dữ liệu kết quả theo định dạng JSON
    result = {"clusters": []}
    # Group data by cluster and print the representative sentence and all sentences in each cluster
    for cluster in sorted_clusters:
        cluster_sentences = df[df['cluster'] == cluster]['sentence_contain_keywords'].tolist()
        representative_sentence = df[df['cluster'] == cluster]['representative_sentence'].iloc[0]
        num_sentences = len(cluster_sentences)
        cluster_data = {
            "cluster_id": cluster,
            "representative_sentence": representative_sentence,
            "num_sentences": num_sentences,
            "sentences": cluster_sentences
        }

        result["clusters"].append(cluster_data)

    # Trả kết quả dưới dạng JSON
    return result

