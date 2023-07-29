import nltk
import gensim
import numpy as np
from nltk.tokenize import word_tokenize, sent_tokenize
file_docs = []

with open ('demofile.txt', encoding="utf-8") as f:
    tokens = sent_tokenize(f.read())
    for line in tokens:
        file_docs.append(line)

print("Number of documents:",len(file_docs))
gen_docs = [[w.lower() for w in word_tokenize(text)]
            for text in file_docs]
dictionary = gensim.corpora.Dictionary(gen_docs)
print(dictionary.token2id)
corpus = [dictionary.doc2bow(gen_doc) for gen_doc in gen_docs]
tf_idf = gensim.models.TfidfModel(corpus)
for doc in tf_idf[corpus]:
    print([[dictionary[id], np.around(freq, decimals=2)] for id, freq in doc])
 # building the index
sims = gensim.similarities.Similarity('doc/',tf_idf[corpus],
                                        num_features=len(dictionary))
file2_docs = []

with open ('demofile2.txt', encoding="utf-8") as f:
    tokens = sent_tokenize(f.read())
    for line in tokens:
        file2_docs.append(line)

print("Number of documents:",len(file2_docs))
for line in file2_docs:
    query_doc = [w.lower() for w in word_tokenize(line)]
    query_doc_bow = dictionary.doc2bow(query_doc)
    #update an existing dictionary and create bag of words
# perform a similarity query against the corpus
query_doc_tf_idf = tf_idf[query_doc_bow]
# print(document_number, document_similarity)
df = sims[query_doc_tf_idf]
print('Comparing Result:', sims[query_doc_tf_idf])

print()