import torch
from transformers import AutoModel, AutoTokenizer
from sklearn.decomposition import LatentDirichletAllocation

model = AutoModel.from_pretrained("vinai/phobert-base-v2")
tokenizer = AutoTokenizer.from_pretrained("vinai/phobert-base-v2")

from main_model.model.pipeline import *
from main_model.config.read_config import *
from main_model.util.general_normalize import _clean_text,__remove_token
from main_model.util.io_util import *


# Define a function to extract features from your text data using Bert
def bert_features(data):
    input_ids = []
    attention_masks = []

    # Tokenize the text and create input_ids and attention_masks
    for text in data:
        inputs = tokenizer.encode_plus(text, padding='max_length', truncation=True, max_length=64)
        input_ids.append(inputs['input_ids'])
        attention_masks.append(inputs['attention_mask'])

    # Convert input_ids and attention_masks to tensors
    input_ids = torch.tensor(input_ids)
    attention_masks = torch.tensor(attention_masks)

    # Use Bert to extract features from the input text
    with torch.no_grad():
        outputs = model(input_ids, attention_masks)
        features = outputs[0]

    return features

config = read_config_file()
df_extract = read_data(type_data='sql_server', config=config, path_data=None,
                       where_stm='WHERE session_id = \'20230502_22-17-06\'')
df_extract = pre_process_df(df_extract)
import numpy as np
embedding_bert = np.array(model.encode(df_extract['clean_content']))
#Bert embeddings are shape of 768
print("Bert Embedding shape", embedding_bert.shape)
print("Bert Embedding sample", embedding_bert[0][0:50])

features = bert_features(df_extract['clean_content'])

# Use LDA to identify the topics in the text
lda = LatentDirichletAllocation(n_components=10)

lda.fit(features)

# Print the topics identified by LDA
print(lda.components_)
