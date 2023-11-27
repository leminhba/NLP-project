from flask import Blueprint, request
from transformers import AutoModel, AutoTokenizer
from main_model.model.pipeline import *
from main_model.config.read_config import *
from main_model.util.general_normalize import _clean_text_remove_token, clean_prefix_and_whitespace
from main_model.util.io_util import *
from main.handle_information import *

file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)
config = read_config_file()
split_sent_blueprint = Blueprint('split_sent', __name__)

db = config['test_db']
params = ('20230503_21-39-30')
sp = """SET NOCOUNT ON; EXEC temp_output_by_session_id '{0}'; """.format(params)
df = read_data_type_db2(db, sp)
list_result = []
for index, row in df.iterrows():
    id_file = row['id_file']
    report_unit = row['report_unit']
    filename = row['filename']
    area_id = row['area_id']
    year = row['year']
    source_id = row['id']
    paragraph = row['paragraph_contain_keywords']
    session_id = util.get_session_id(config)
    created_date = util.get_current_date()
    # Phân tách đoạn văn thành các câu bằng dấu chấm và dấu ; và dấu xuống dòng, nếu độ dài nhỏ hơn 40 thì bỏ
    sentences = [sentence.strip() for sentence in re.split(r'[.。;；\n]', paragraph) if len(sentence) > 40]
    # Copy câu vào dataframe mới
    for sentence in sentences:
        list_result.append({'id_file': id_file,
                            'report_unit': report_unit,
                            'filename': filename,
                            'area_id': area_id,
                            'year': year,
                            'paragraph_contain_keywords': paragraph,
                            'sentence_contain_keywords': clean_prefix_and_whitespace(sentence),
                            'session_id': session_id,
                            'source_id': source_id
                            })


df_session = pd.DataFrame([{"session_id": session_id,
                                    "created_date": created_date,
                                    "api_info": "Tách câu " + session_id,
                                    "type_extract": "split_sent"}])
insert_db(df_session, config, output_session=True)
new_df = pd.DataFrame(list_result)
list_df_write = split_df(new_df, config['batch_size'])
for i in range(len(list_df_write)):
    insert_db(list_df_write[i], config)
