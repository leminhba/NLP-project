from flask import request, Flask
import sys
import os.path
from main_model.model.pipeline import *
from main_model.config.read_config import *
from main_model.util.io_util import *


from flask import jsonify

file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)

# config = get_config()
json_content = read_config_file()
local_server_name = json_content['local_server_name']
config = read_config_file()
df_extract = read_data(type_data='sql_server', config=config, path_data=None)
df_extract = pre_process_df(df_extract)
y = df_extract['IID']
X = df_extract['clean_content']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=1)
X_train_vec, vectorizer_nd = get_tdidf_vectorizer(X_train, vectorizer_nd=None)
model = Model('svm')
model.train(X_train_vec, y_train)
print(f"TESTING PERIOD...")
X_test_vec, m = get_tdidf_vectorizer(X_test, vectorizer_nd=vectorizer_nd)
y_pred = model.predict_only(X_test_vec)
type_score = 'f1_score'
score = model.score_model(type_score, y_true=y_test, y_pred=y_pred)
print(f"Score {type_score}: {score}")


