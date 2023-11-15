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



def main():
    # TODO
    file_dir = os.path.dirname(__file__)
    sys.path.append(file_dir)
    # config = get_config()
    json_content = read_config_file()

    config = read_config_file()
    df_extract = read_data(type_data='sql_server', config=config, path_data=None, where_stm='WHERE session_id = \'20230502_22-17-06\'')
    df_extract = pre_process_df2(df_extract)
    doc_tokenized = [simple_preprocess(doc) for doc in df_extract['clean_content']]
    # assume the word 'b' is to be deleted, put its id in a variable


    id2word = gensim.corpora.Dictionary(doc_tokenized)
    #my_list = ['numbertoken', 'điều', 'và', 'của', 'về', 'có', 'công', 'trình', 'chủ', 'để', 'ra']
    #del_ids = [k for k, v in id2word.items() if v in my_list]
    # remove unwanted word ids from the dictionary in place
    #id2word.filter_tokens(bad_ids=del_ids)
    id2word.filter_extremes(no_below=3, no_above=0.5)
    id2word.compactify()

    # save dictionary
    #id2word.save(PATH_DICTIONARY)
    corpus = [id2word.doc2bow(doc) for doc in doc_tokenized]


    # save corpus
    #gensim.corpora.MmCorpus.serialize(PATH_CORPUS, corpus)
    # load corpus
    # mm_corpus = gensim.corpora.MmCorpus('path_to_save_file.mm')
    #lda_model = gensim.models.LsiModel(corpus, num_topics=16, id2word=id2word)
    lda_model = gensim.models.ldamodel.LdaModel(corpus, num_topics=15, id2word=id2word)
    # save model
    #lda_model.save(PATH_LDA_MODEL)
    #lda_model = gensim.models.ldamodel.LdaModel.load(PATH_LDA_MODEL)
    #lda_model.print_topics(-1)
    #lda_model.show_topics(num_topics=15, num_words=20)
    #for idx, topic in lda_model.show_topics():
        #print('Topic: {} \nWords: {}'.format(idx, ''.join([w[0] for w in topic])))

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




    df_dominant_topic = df_topic_sents_keywords.reset_index()
    df_dominant_topic.columns = ['Document_No', 'Dominant_Topic', 'Topic_Perc_Contrib', 'Keywords', 'Text']

    # Show
    df_dominant_topic.head(10)


    from gensim.matutils import cossim
    #doc1 = lda_model.get_document_topics(test_corpus[0], minimum_probability=0)
    #doc2 = lda_model.get_document_topics(test_corpus[1], minimum_probability=0)
    #print(cossim(doc1, doc2))

    #new_doc_distribution = np.array([tup[1] for tup in lda_model.get_document_topics(test_corpus)])

    # this is surprisingly fast



   # text = _clean_text(text)
    #texts_corpus2 = make_texts_corpus(text)

   # bow = gensim.corpora.Dictionary.doc2bow(texts_corpus2)
   # for index, score in sorted(lda_model[bow], key=lambda tup: -1 * tup[1]):
    #    print("Score: {}\t Topic: {}".format(score, lda_model.print_topic(index, 5)))

if __name__ == '__main__':
    main()
