import itertools
import logging
import urllib.parse
import numpy as np
import matplotlib.pyplot as plt
import gensim
from gensim import similarities
from gensim.utils import simple_preprocess
from gensim import models
from flask import Flask, redirect, url_for, request,jsonify
import sys
from main_model.model.pipeline import *
from main_model.config.read_config import *
from main_model.util.general_normalize import _clean_text
from main_model.util.io_util import *
from distances import get_most_similar_documents
import json
logging.basicConfig(format='%(levelname)s : %(message)s', level=logging.INFO)
logging.root.level = logging.INFO


PATH_DICTIONARY = "models/id2word.dictionary"
PATH_CORPUS = "models/corpus.mm"
PATH_LDA_MODEL = "models/LDA.model"
PATH_DOC_TOPIC_DIST = "models/doc_topic_dist.dat"


def head(stream, n=10):
    """
    Return the first `n` elements of the stream, as plain list.
    """
    return list(itertools.islice(stream, n))


def make_texts_corpus(sentences):
    for sentence in sentences:
        yield simple_preprocess(sentence, deacc=True)


class StreamCorpus(object):
    def __init__(self, sentences, dictionary, clip_docs=None):
        """
        Parse the first `clip_docs` documents
        Yield each document in turn, as a list of tokens.
        """
        self.sentences = sentences
        self.dictionary = dictionary
        self.clip_docs = clip_docs

    def __iter__(self):
        for tokens in itertools.islice(make_texts_corpus(self.sentences),
                                       self.clip_docs):
            yield self.dictionary.doc2bow(tokens)

    def __len__(self):
        return self.clip_docs


class LDAModel:

    def __init__(self, num_topics, passes, chunksize,
                 random_state=100, update_every=1, alpha='auto',
                 per_word_topics=False):
        """
        :param sentences: list or iterable (recommend)
        """

        # data
        self.sentences = None

        # params
        self.lda_model = None
        self.dictionary = None
        self.corpus = None

        # hyperparams
        self.num_topics = num_topics
        self.passes = passes
        self.chunksize = chunksize
        self.random_state = random_state
        self.update_every = update_every
        self.alpha = alpha
        self.per_word_topics = per_word_topics

        # init model
        # self._make_dictionary()
        # self._make_corpus_bow()

    def _make_corpus_bow(self, sentences):
        self.corpus = StreamCorpus(sentences, self.id2word)
        # save corpus
        gensim.corpora.MmCorpus.serialize(PATH_CORPUS, self.corpus)

    def _make_corpus_tfidf(self):
        pass

    def _make_dictionary(self, sentences):
        self.texts_corpus = make_texts_corpus(sentences)
        self.id2word = gensim.corpora.Dictionary(self.texts_corpus)
        self.id2word.filter_extremes(no_below=10, no_above=0.25)
        self.id2word.compactify()
        self.id2word.save(PATH_DICTIONARY)

    def documents_topic_distribution(self):
        doc_topic_dist = np.array(
            [[tup[1] for tup in lst] for lst in self.lda_model[self.corpus]]
        )
        # save documents-topics matrix
        joblib.dump(doc_topic_dist, PATH_DOC_TOPIC_DIST)
        return doc_topic_dist

    def fit(self, sentences):
        from itertools import tee
        sentences_1, sentences_2 = tee(sentences)
        self._make_dictionary(sentences_1)
        self._make_corpus_bow(sentences_2)
        self.lda_model = gensim.models.ldamodel.LdaModel(
            self.corpus, id2word=self.id2word, num_topics=64, passes=5,
            chunksize=100, random_state=42, alpha=1e-2, eta=0.5e-2,
            minimum_probability=0.0, per_word_topics=False
        )
        self.lda_model.save(PATH_LDA_MODEL)

    def transform(self, sentence):
        """
        :param document: preprocessed document
        """
        document_corpus = next(make_texts_corpus([sentence]))
        corpus = self.id2word.doc2bow(document_corpus)
        document_dist = np.array(
            [tup[1] for tup in self.lda_model.get_document_topics(bow=corpus)]
        )
        return corpus, document_dist

    def predict(self, document_dist):
        doc_topic_dist = self.documents_topic_distribution()
        return get_most_similar_documents(document_dist, doc_topic_dist)

    def update(self, new_corpus):  # TODO
        """
        Online Learning LDA
        https://radimrehurek.com/gensim/models/ldamodel.html#usage-examples
        https://radimrehurek.com/gensim/wiki.html#latent-dirichlet-allocation
        """
        self.lda_model.update(new_corpus)
        # get topic probability distribution for documents
        for corpus in new_corpus:
            yield self.lda_model[corpus]

    def model_perplexity(self):
        logging.INFO(self.lda_model.log_perplexity(self.corpus))

    def coherence_score(self):
        self.coherence_model_lda = gensim.models.coherencemodel.CoherenceModel(
            model=self.lda_model, texts=self.corpus,
            dictionary=self.id2word, coherence='c_v'
        )
        logging.INFO(self.coherence_model_lda.get_coherence())

    def compute_coherence_values(self, mallet_path, dictionary, corpus,
                                 texts, end=40, start=2, step=3):
        """
        Compute c_v coherence for various number of topics

        Parameters:
        ----------
        dictionary : Gensim dictionary
        corpus : Gensim corpus
        texts : List of input texts
        end : Max num of topics

        Returns:
        -------
        model_list : List of LDA topic models
        coherence_values : Coherence values corresponding to the LDA model
                           with respective number of topics
        """
        coherence_values = []
        model_list = []
        for num_topics in range(start, end, step):
            model = gensim.models.wrappers.LdaMallet(
                mallet_path, corpus=self.corpus,
                num_topics=self.num_topics, id2word=self.id2word)
            model_list.append(model)
            coherencemodel = gensim.models.coherencemodel.CoherenceModel(
                model=model, texts=self.texts_corpus,
                dictionary=self.dictionary, coherence='c_v'
            )
            coherence_values.append(coherencemodel.get_coherence())

        return model_list, coherence_values

    def plot(self, coherence_values, end=40, start=2, step=3):
        x = range(start, end, step)
        plt.plot(x, coherence_values)
        plt.xlabel("Num Topics")
        plt.ylabel("Coherence score")
        plt.legend(("coherence_values"), loc='best')
        plt.show()

    def print_topics(self):
        pass


def read_db_table(config, table_name):
    return read_data_type_db(config, table_name, where_stm='WHERE status = 1')


def pre_process_table(df):
    content_col = 'ind_name_vn'
    df['clean_content'] = df.apply(lambda row: _clean_text(row[content_col]), axis=1)
    df.rename(columns={'ind_name_vn':'sentence_contain_keywords'}, inplace=True)
    return df


app = Flask(__name__)
@app.route("/main", methods=['GET'])
def main():
    # TODO
    file_dir = os.path.dirname(__file__)
    sys.path.append(file_dir)
    config = read_config_file()
    if request.args.get('t') == "1":
        table_name = "Indicator"
        where_stm = ''
        df_extract = read_data_type_db2(config, table_name, where_stm)
        df_extract = pre_process_table(df_extract)
    else:
        table_name = config['input_table_name']
        df_extract = read_data(type_data='sql_server', config=config, path_data=None)
        df_extract = pre_process_df(df_extract)



    doc_tokenized = [simple_preprocess(doc) for doc in df_extract['clean_content']]

    id2word = gensim.corpora.Dictionary(doc_tokenized)
    id2word.filter_extremes(no_below=20, no_above=0.1)
    id2word.compactify()


    # save dictionary
    #id2word.save(PATH_DICTIONARY)

    #ictionary = gensim.corpora.Dictionary()
    corpus = [id2word.doc2bow(doc, allow_update=True) for doc in doc_tokenized]

    #corpus = StreamCorpus(doc_tokenized, id2word)
    # Term Document Frequency
    #corpus = [id2word.doc2bow(text) for text in sentences]
    # save corpus
    #gensim.corpora.MmCorpus.serialize(PATH_CORPUS, corpus)
    # load corpus
    # mm_corpus = gensim.corpora.MmCorpus('path_to_save_file.mm')


    test_doc = _clean_text(urllib.parse.unquote(request.args.get('kw')))

    if request.args.get('m') == "lsa":
        model = models.LsiModel(corpus, num_topics=4, id2word=id2word)
    else:
        model = models.LdaModel(corpus, num_topics=10, id2word=id2word)


    test_corpus = id2word.doc2bow(test_doc.lower().split())
    vec_lda = model[test_corpus]
    # transforming corpus to LSI space and index it

    index = similarities.MatrixSimilarity(model[corpus])
    # performing a similarity query against the corpus

    simil = index[vec_lda]

    simil = sorted(list(enumerate(simil)), key=lambda item: -item[1])
    # printing (document_number, document_similarity)

    print("Similarity scores for each document\n", simil)
    print("Similarity scores with document")
    data = []
    for doc_position, doc_score in simil:
        data.append({"sentence_contain_keywords": df_extract['sentence_contain_keywords'][doc_position], "score": str(doc_score)})
        #print(doc_score, df_extract['sentence_contain_keywords'][doc_position])
    return json.dumps(data,ensure_ascii=False)

if __name__ == '__main__':
    app.run(debug=True)
