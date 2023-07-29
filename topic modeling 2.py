import itertools
import logging

import numpy as np
import matplotlib.pyplot as plt
import gensim
from gensim.utils import simple_preprocess
import joblib
import sys
from main_model.model.pipeline import *
from main_model.config.read_config import *
from main_model.util.general_normalize import _clean_text
from main_model.util.io_util import *
from distances import get_most_similar_documents

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


def main():
    # TODO
    file_dir = os.path.dirname(__file__)
    sys.path.append(file_dir)
    # config = get_config()
    json_content = read_config_file()

    config = read_config_file()
    df_extract = read_data(type_data='sql_server', config=config, path_data=None)
    df_extract = pre_process_df(df_extract)
    doc_tokenized = [simple_preprocess(doc) for doc in df_extract['clean_content']]

    id2word = gensim.corpora.Dictionary(doc_tokenized)
 #   id2word.filter_extremes(no_below=20, no_above=0.1)
 #   id2word.compactify()

    # save dictionary
    #id2word.save(PATH_DICTIONARY)

    #ictionary = gensim.corpora.Dictionary()
    corpus = [id2word.doc2bow(doc, allow_update=True) for doc in doc_tokenized]

    #corpus = StreamCorpus(doc_tokenized, id2word)
    # Term Document Frequency
    #corpus = [id2word.doc2bow(text) for text in sentences]
    # save corpus
   # gensim.corpora.MmCorpus.serialize(PATH_CORPUS, corpus)
    # load corpus
    # mm_corpus = gensim.corpora.MmCorpus('path_to_save_file.mm')
    lda_model = gensim.models.ldamodel.LdaModel(
        corpus, num_topics=64, id2word=id2word, passes=10, chunksize=100
    )
    # save model
    #lda_model.save(PATH_LDA_MODEL)
    #lda_model.print_topics(-1)
    lda_model.show_topics(num_topics=10, num_words=20)
    for idx, topic in lda_model.show_topics():
        print('Topic: {} \nWords: {}'.format(idx, ''.join([w[0] for w in topic])))

    # Compute Perplexity
    #print('\nPerplexity: ', lda_model.log_perplexity(corpus))  # a measure of how good the model is. lower the better.
    # Compute Coherence Score
    #coherence_model_lda = gensim.models.CoherenceModel(model=lda_model, texts=doc_tokenized, dictionary=id2word, coherence='c_v')
    #coherence_lda = coherence_model_lda.get_coherence()
    #print('\nCoherence Score: ', coherence_lda)

    def format_topics_sentences(ldamodel=lda_model, corpus=corpus, texts=doc_tokenized):
        # Init output
        sent_topics_df = pd.DataFrame()

        # Get main topic in each document
        for i, row in enumerate(ldamodel[corpus]):
            row = sorted(row, key=lambda x: (x[1]), reverse=True)
            # Get the Dominant topic, Perc Contribution and Keywords for each document
            for j, (topic_num, prop_topic) in enumerate(row):
                if j == 0:  # => dominant topic
                    wp = ldamodel.show_topic(topic_num)
                    topic_keywords = ", ".join([word for word, prop in wp])
                    sent_topics_df = sent_topics_df.append(
                        pd.Series([int(topic_num), round(prop_topic, 4), topic_keywords]), ignore_index=True)
                else:
                    break
        sent_topics_df.columns = ['Dominant_Topic', 'Perc_Contribution', 'Topic_Keywords']

        # Add original text to the end of the output
        contents = pd.Series(texts)
        sent_topics_df = pd.concat([sent_topics_df, contents], axis=1)
        return sent_topics_df

    df_topic_sents_keywords = format_topics_sentences(ldamodel=lda_model, corpus=corpus, texts=doc_tokenized)

    # Format
    df_dominant_topic = df_topic_sents_keywords.reset_index()
    df_dominant_topic.columns = ['Document_No', 'Dominant_Topic', 'Topic_Perc_Contrib', 'Keywords', 'Text']

    # Show
    df_dominant_topic.head(10)

    test_doc = ["dù dịch bệnh trên gia súc, gia cầm được kiểm soát tốt nhưng chăn nuôi lợn gặp khó khăn do giá bán thịt hơi vẫn ở mức thấp trong khi giá nguyên liệu chế biến thức ăn chăn nuôi tăng cao"]
    test_doc = [doc.split() for doc in test_doc]
    # Convert document(a list    of    words) into    the    bag - of - words    format
    test_corpus = [id2word.doc2bow(doc) for doc in test_doc]
    id_words = [[(id2word[id], count) for id, count in line] for line in test_corpus]
    vec_lda_topics_03 = lda_model[test_corpus]
    print('document 03 topics: ', vec_lda_topics_03)
    from gensim.matutils import cossim
    #doc1 = lda_model.get_document_topics(test_corpus[0], minimum_probability=0)
    #doc2 = lda_model.get_document_topics(test_corpus[1], minimum_probability=0)
    #print(cossim(doc1, doc2))

    #new_doc_distribution = np.array([tup[1] for tup in lda_model.get_document_topics(test_corpus)])
    new_doc_distribution = np.array([[tup[0] for tup in lst] for lst in lda_model[test_corpus]])
    # we need to use nested list comprehension here
    # this may take 1-2 minutes...
    doc_topic_dist = np.array([[tup[1] for tup in lst] for lst in lda_model[corpus]])
    doc_topic_dist.shape
    # this is surprisingly fast

    most_sim_ids = get_most_similar_documents(new_doc_distribution, doc_topic_dist)
    most_similar_df = df_extract[df_extract.index.isin(most_sim_ids)]

   # text = _clean_text(text)
    #texts_corpus2 = make_texts_corpus(text)

   # bow = gensim.corpora.Dictionary.doc2bow(texts_corpus2)
   # for index, score in sorted(lda_model[bow], key=lambda tup: -1 * tup[1]):
    #    print("Score: {}\t Topic: {}".format(score, lda_model.print_topic(index, 5)))

if __name__ == '__main__':
    main()
