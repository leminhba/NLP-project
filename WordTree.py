from flask import request, Flask
import sys
import os.path
from main_model.model.pipeline import *
from main_model.config.read_config import *
from main_model.util.io_util import *
import wordtree
from wordcloud import WordCloud
import matplotlib.pyplot as plt

file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)

# config = get_config()
json_content = read_config_file()
local_server_name = json_content['local_server_name']
config = read_config_file()
df_extract = read_data(type_data='sql_server', config=config, path_data=None)
df_extract = pre_process_df(df_extract)

X = df_extract['clean_content']

#text = " ".join(cat.split()[1] for cat in df_extract['clean_content'])
#word_cloud = WordCloud(collocations = False, background_color = 'white').generate(text)
#plt.imshow(word_cloud, interpolation='bilinear')
#plt.axis("off")
#plt.show()

g = wordtree.search_and_draw(corpus = X, keyword = "còn")
g.render(filename = "test") # creates a file world.dv.png

