# -*- encoding: utf-8 -*-
import time

import pandas as pd
import requests
import shutil
from sqlalchemy import create_engine
import sqlalchemy
import os
import math
import sys

# from sqlalchemy.types import NVARCHAR
from sqlalchemy.dialects.mssql import NVARCHAR, INTEGER
import sqlalchemy.dialects.mysql

import nltk
import ssl

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

nltk.download('punkt')

file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)

import util
from util import EXTENSION_DOC, EXTENSION_DOCX, EXTENSION_PDF


def get_list_keywords_in_topic(api_keywords, bear_token, topic_id):
    headers = {"Authorization": f"Bearer {bear_token}"}
    r = requests.get(api_keywords, headers=headers, params={'topic_id': topic_id})
    data = r.json()
    return [kw['keyword'].strip().lower() for kw in data]


def read_rule_by_specific(api_keywords, list_topic_id_1, list_topic_id_2, bear_token):
    dict_general_keywords = {}
    dict_specific_keywords = {}
    if list_topic_id_1:
        for topic_1 in list_topic_id_1:
            dict_specific_keywords[topic_1] = get_list_keywords_in_topic(api_keywords, bear_token, topic_1)
    else:
        dict_specific_keywords = None

    if list_topic_id_2:
        for topic_2 in list_topic_id_2:
            dict_general_keywords[topic_2] = get_list_keywords_in_topic(api_keywords, bear_token, topic_2)
    else:
        dict_general_keywords = None
    return dict_general_keywords, dict_specific_keywords


def check_file_type(file_type, list_extension_keep=None):
    if list_extension_keep is None:
        list_extension_keep = [EXTENSION_DOC, EXTENSION_DOCX, EXTENSION_PDF]
    return True if file_type in list_extension_keep else False


def get_request_by_bear_token(url, bear_token, params=None):
    headers = {"Authorization": f"Bearer {bear_token}"}
    r = requests.get(url, headers=headers)
    result = r.json()
    r.close()
    return result


def get_and_filter_all_reports(session_id, api_all_reports, bear_token, root_temp_folder, list_extension_keep):
    '''
    purpose: get all reports, filter by extension and then save df_info and all reports to temporary folder: 'data'
    :param session_id:
    :param api_all_reports:
    :param bear_token:
    :param root_temp_folder:
    :param list_extension_keep:
    :return:
        # active_folder: /anhdt/173465
        # data_folder: /anhdt/173465/data/
        # df_info: /anhdt/173465/df_info.xlsx
    '''
    # get list report files from api_all_reports + bear token
    result = get_request_by_bear_token(api_all_reports, bear_token)

    # df_info
    df_info = pd.DataFrame(result)

    active_folder = util.make_dir(os.path.join(root_temp_folder, f'{session_id}'))
    data_folder = util.make_dir(os.path.join(active_folder, 'data'))

    df_info['path_file_temp'] = df_info.apply(lambda row_temp: os.path.join(
        data_folder, os.path.basename(row_temp['AttachedFile'])), axis=1)
    df_info['type_file'] = df_info.apply(lambda row_temp: util.get_file_name_extension(
        row_temp['path_file_temp']), axis=1)
    df_info['session_id'] = df_info.apply(lambda row_temp: session_id, axis=1)

    # filter file extension
    df_info['is_satisfied'] = df_info.apply(
        lambda row_temp: check_file_type(row_temp['type_file'], list_extension_keep=list_extension_keep), axis=1)
    df_info = df_info[df_info['is_satisfied'] == True]
    df_info.drop(columns=['is_satisfied'], inplace=True)

    # save df_info
    # df_info.to_excel(os.path.join(active_folder, f'df_info.xlsx'), index=None)

    # save all reports to local folder on server
    for index, row in df_info.iterrows():
        attached_file = row['AttachedFile']
        path_file = row['path_file_temp']
        # print(f"CHECK FILE: {attached_file}")
        rf = requests.get(attached_file, allow_redirects=True)
        with open(path_file, 'wb') as w:
            w.write(rf.content)
            w.close()
    return df_info, active_folder


def read_command_from_client(command_api, bear_token):
    '''
    :param command_api: command input API
    :param bear_token: bear token
    :return:
        + api_all_reports: API for get all reports
        + type_1: List of topic type_1, if topic type_1 is empty, return None. In realistic, topic type_1 cannot be empty
        + type_2: List of topic type_2, if topic type_2 is empty, return None.
    '''
    result = get_request_by_bear_token(command_api, bear_token)[0]
    api_all_reports = result['url']
    type_1 = result['type1']
    type_2 = result['type2']
    api_info = result['api_info']
    if "," in type_1:
        type_1 = type_1.split(',')
        type_1 = [i.strip() for i in type_1]
    elif type_1 != '':
        type_1 = [type_1.strip()]
    else:
        type_1 = None

    if "," in type_2:
        type_2 = type_2.split(', ')
        type_2 = [i.strip() for i in type_2]
    elif type_2 != '':
        type_2 = [type_2.strip()]
    else:
        type_2 = None
    return api_all_reports, type_1, type_2, api_info


def get_all_input_data(session_id, config, command_api, root_temp_folder, list_extension_keep=None):
    '''
    :param config: config variables
    :param command_api: command API get from user, e.g.: "https://giamsatdanhgia.mard.gov.vn/api/link?id=1"
    :param root_temp_folder: folder to save temporary files
    :param list_extension_keep:
    :return:
    '''
    # get bear token
    bear_token = util.get_token(config)

    # get info from command api
    api_get_reports, type_1, type_2, api_info = read_command_from_client(command_api, bear_token)

    # get all reports and save to temporary folder with both df_info (excel) and all report files
    df_info, active_folder = get_and_filter_all_reports(session_id, api_get_reports, bear_token, root_temp_folder,
                                                        list_extension_keep)

    # get keywords in each topics which is got from command API
    api_keywords = config['api_get_keywords']
    dict_general_keywords, dict_specific_keywords = read_rule_by_specific(api_keywords, type_1, type_2, bear_token)
    return df_info, dict_general_keywords, dict_specific_keywords, active_folder, api_info


def check_condition_all(keyword, content):
    # keyword: ["Sạt lở; đê biển", "Sạt lở; đê sông", "Sét; nhiều hơn"]
    all_result = []
    for keyword_str in keyword:
        list_keywords = [x.strip() for x in keyword_str.split(';')]
        length_key_main_not_contains_except_keywords = len([xkey for xkey in list_keywords if not xkey.startswith('-')])
        set_key_result = set()
        for key_tmp in list_keywords:
            if key_tmp.startswith('-'):
                key_except = key_tmp.split(' ')[1] if len(key_tmp.split(' ')) > 1 else None
                if key_except is not None and key_except in content:
                    set_key_result = set()
                    break
            if key_tmp in content:
                set_key_result.add(key_tmp)
            else:
                set_key_result = set()
                break
        # print(f"set_key_result = {set_key_result}")
        # print(f"LEN set_key_result = {len(set_key_result)}")
        # print(f"=======")
        # print(f"length_key_main_not_contains_except_keywords = {length_key_main_not_contains_except_keywords}")
        if len(set_key_result) == length_key_main_not_contains_except_keywords:
            str_ele_single_result = "; ".join(set_key_result)
            all_result.append(str_ele_single_result)
    if len(all_result) > 0:
        # return "_".join(all_result)
        return all_result
    return None


def classify_handle(id_file, filename, report_unit, area_id, year, content, dict_general_keywords,
                    dict_specific_keywords, session_id, command_api, api_info):
    list_result = []
    content = content.lower()
    list_paragraphs = content.split('\n')
    list_paras_sents = []
    for para_i in list_paragraphs:
        list_sents = nltk.tokenize.sent_tokenize(para_i)
        for sent in list_sents:
            list_paras_sents.append({'sent': sent, 'para': para_i})

    if dict_general_keywords is not None and dict_specific_keywords is not None:
        for element_sent in list_paras_sents:
            sent_i = element_sent['sent']
            para_i = element_sent['para']
            for topic, keyword in dict_general_keywords.items():
                result = check_condition_all(keyword, sent_i)
                if result is not None:
                    for topic_spe, keyword_spe in dict_specific_keywords.items():
                        result_spe = check_condition_all(keyword_spe, sent_i)
                        if result_spe is not None:
                            for ele_result in result:
                                for ele_result_spe in result_spe:
                                    list_result.append({'id_file': id_file,
                                                        'filename': filename,
                                                        'report_unit': report_unit,
                                                        'area_id': area_id,
                                                        'year': year,
                                                        'topic_1': topic_spe,
                                                        'keywords_topic_1': ele_result_spe,
                                                        'topic_2': topic,
                                                        'keywords_topic_2': ele_result,
                                                        'sentence_contain_keywords': sent_i,
                                                        'paragraph_contain_keywords': para_i,
                                                        'session_id': session_id,
                                                        'command_api': command_api,
                                                        'api_info': api_info
                                                        })
    elif dict_specific_keywords is not None:
        for element_sent in list_paras_sents:
            sent_i = element_sent['sent']
            para_i = element_sent['para']
            # dict_specific_keywords: {'KH': ["Giảm; khả năng; chống chịu", "Giảm; khả năng; sinh sản"]}
            # topic: "KH"
            # keyword: ["Giảm; khả năng; chống chịu", "Giảm; khả năng; sinh sản"]
            # print(f"NOT NONE")
            for topic, keyword in dict_specific_keywords.items():
                result = check_condition_all(keyword, sent_i)
                if result is not None:
                    for ele_result in result:
                        list_result.append({'id_file': id_file,
                                            'filename': filename,
                                            'report_unit': report_unit,
                                            'area_id': area_id,
                                            'year': year,
                                            'topic_1': topic,
                                            'keywords_topic_1': ele_result,
                                            'topic_2': "",
                                            'keywords_topic_2': "",
                                            'sentence_contain_keywords': sent_i,
                                            'paragraph_contain_keywords': para_i,
                                            'session_id': session_id,
                                            'command_api': command_api,
                                            'api_info': api_info
                                            })
    return list_result


def print_and_log_file(f_cursur, content):
    print(content)
    f_cursur.write(f"{content}\n")


def process_all_report(df_info, dict_general_keywords, dict_specific_keywords, number_words_skipping, session_id,
                       command_api, api_info, active_folder):
    '''
    :param df_info:
    :param dict_general_keywords:
    :param dict_specific_keywords:
    :param number_words_skipping:
    :param session_id:
    :param command_api:
    :param api_info:
    :param active_folder: folder contains all temp files in local (server)
    # folder contains data: {active_folder}/data
    # folder contains log: {active_folder}/log
    :return:
    '''
    log_folder = os.path.join(active_folder, 'log')
    util.make_dir(log_folder)

    log_file = os.path.join(log_folder, 'log.txt')
    performance_file = os.path.join(log_folder, 'performance.csv')

    err = 0
    result_list = []
    f_log = open(log_file, 'a', encoding='utf-8')
    f_performance = open(performance_file, 'a', encoding='utf-8')
    # init performance file
    f_performance.write(f"url_file|time_process|time_total|status\n")

    start_time_all = time.time()
    count_x = 0
    length_df_info = len(df_info)
    for index, row in df_info.iterrows():
        count_x += 1
        start_time_element = time.time()
        path_file_temp = row["path_file_temp"]
        print_and_log_file(f_log, f'Processing {count_x}/{length_df_info} file: {os.path.basename(path_file_temp)}')
        # read content from file (with corresponding TYPE)
        content, message = util.extract_text_from_file(path_file_temp)
        if content is None:
            print_and_log_file(f_log, f'File at path: {path_file_temp} got an error: {message}')
            err += 1
            # log performance
            print_and_log_file(f_performance,
                               f"{row['AttachedFile']}|{round(time.time() - start_time_element, 2)}|"
                               f"{round(time.time() - start_time_all, 2)}|"
                               f"error")
            continue

        if number_words_skipping != 0:
            # content = content[number_words_skipping:]
            content = util.remove_number_words(content, number_words_skipping)
        id_file = row['Id']
        filename = row['AttachedFile']
        report_unit = row['DonViBaoCao']
        area_id = row['AreaId']
        year = row['Date']
        list_of_all_dict_mining = classify_handle(id_file, filename, report_unit, area_id, year,
                                                  content,
                                                  dict_general_keywords, dict_specific_keywords,
                                                  session_id, command_api, api_info)

        if list_of_all_dict_mining is not None and len(list_of_all_dict_mining) > 0:
            result_list.extend(list_of_all_dict_mining)
        print_and_log_file(f_performance,
                           f"{filename}|{round(time.time() - start_time_element, 2)}|"
                           f"{round(time.time() - start_time_all, 2)}|"
                           f"success")
    f_log.close()
    f_performance.close()
    return result_list, log_file, err


def process_tables_all_report(df_info, active_folder):
    '''
    :param df_info:
    :param dict_general_keywords:
    :param dict_specific_keywords:
    :param number_words_skipping:
    :param session_id:
    :param command_api:
    :param api_info:
    :param active_folder: folder contains all temp files in local (server)
    # folder contains data: {active_folder}/data
    # folder contains log: {active_folder}/log
    :return:
    '''
    log_folder = os.path.join(active_folder, 'log')
    util.make_dir(log_folder)

    log_file = os.path.join(log_folder, 'log.txt')
    performance_file = os.path.join(log_folder, 'performance.csv')

    err = 0
    result_list = []
    f_log = open(log_file, 'a', encoding='utf-8')
    f_performance = open(performance_file, 'a', encoding='utf-8')
    # init performance file
    f_performance.write(f"url_file|time_process|time_total|status\n")

    start_time_all = time.time()
    count_x = 0
    length_df_info = len(df_info)
    for index, row in df_info.iterrows():
        count_x += 1
        start_time_element = time.time()
        path_file_temp = row["path_file_temp"]
        print_and_log_file(f_log, f'Processing {count_x}/{length_df_info} file: {os.path.basename(path_file_temp)}')
        # read content from file (with corresponding TYPE)
        tables, message = util.extract_table_from_file(path_file_temp)


    f_log.close()
    f_performance.close()
    return tables, log_file, err

def process_content_all_report(df_info, active_folder):
    '''
    :param df_info:
    :param dict_general_keywords:
    :param dict_specific_keywords:
    :param number_words_skipping:
    :param session_id:
    :param command_api:
    :param api_info:
    :param active_folder: folder contains all temp files in local (server)
    # folder contains data: {active_folder}/data
    # folder contains log: {active_folder}/log
    :return:
    '''
    log_folder = os.path.join(active_folder, 'log')
    util.make_dir(log_folder)

    log_file = os.path.join(log_folder, 'log.txt')
    performance_file = os.path.join(log_folder, 'performance.csv')

    err = 0
    result_list = []
    f_log = open(log_file, 'a', encoding='utf-8')
    f_performance = open(performance_file, 'a', encoding='utf-8')
    # init performance file
    f_performance.write(f"url_file|time_process|time_total|status\n")

    start_time_all = time.time()
    count_x = 0
    length_df_info = len(df_info)
    for index, row in df_info.iterrows():
        count_x += 1
        start_time_element = time.time()
        path_file_temp = row["path_file_temp"]
        print_and_log_file(f_log, f'Processing {count_x}/{length_df_info} file: {os.path.basename(path_file_temp)}')
        # read content from file (with corresponding TYPE)
        content, message = util.extract_text_from_file(path_file_temp)


    f_log.close()
    f_performance.close()
    return content, log_file, err


def process_all_report(df_info, dict_general_keywords, dict_specific_keywords, number_words_skipping, session_id,
                       command_api, api_info, active_folder):
    '''
    :param df_info:
    :param dict_general_keywords:
    :param dict_specific_keywords:
    :param number_words_skipping:
    :param session_id:
    :param command_api:
    :param api_info:
    :param active_folder: folder contains all temp files in local (server)
    # folder contains data: {active_folder}/data
    # folder contains log: {active_folder}/log
    :return:
    '''
    log_folder = os.path.join(active_folder, 'log')
    util.make_dir(log_folder)

    log_file = os.path.join(log_folder, 'log.txt')
    performance_file = os.path.join(log_folder, 'performance.csv')

    err = 0
    result_list = []
    f_log = open(log_file, 'a', encoding='utf-8')
    f_performance = open(performance_file, 'a', encoding='utf-8')
    # init performance file
    f_performance.write(f"url_file|time_process|time_total|status\n")

    start_time_all = time.time()
    count_x = 0
    length_df_info = len(df_info)
    for index, row in df_info.iterrows():
        count_x += 1
        start_time_element = time.time()
        path_file_temp = row["path_file_temp"]
        print_and_log_file(f_log, f'Processing {count_x}/{length_df_info} file: {os.path.basename(path_file_temp)}')
        # read content from file (with corresponding TYPE)
        content, message = util.extract_text_from_file(path_file_temp)
        if content is None:
            print_and_log_file(f_log, f'File at path: {path_file_temp} got an error: {message}')
            err += 1
            # log performance
            print_and_log_file(f_performance,
                               f"{row['AttachedFile']}|{round(time.time() - start_time_element, 2)}|"
                               f"{round(time.time() - start_time_all, 2)}|"
                               f"error")
            continue

        if number_words_skipping != 0:
            # content = content[number_words_skipping:]
            content = util.remove_number_words(content, number_words_skipping)
        id_file = row['Id']
        filename = row['AttachedFile']
        report_unit = row['DonViBaoCao']
        area_id = row['AreaId']
        year = row['Date']
        list_of_all_dict_mining = classify_handle(id_file, filename, report_unit, area_id, year,
                                                  content,
                                                  dict_general_keywords, dict_specific_keywords,
                                                  session_id, command_api, api_info)

        if list_of_all_dict_mining is not None and len(list_of_all_dict_mining) > 0:
            result_list.extend(list_of_all_dict_mining)
        print_and_log_file(f_performance,
                           f"{filename}|{round(time.time() - start_time_element, 2)}|"
                           f"{round(time.time() - start_time_all, 2)}|"
                           f"success")
    f_log.close()
    f_performance.close()
    return result_list, log_file, err

# def convert_dtype_sql(df_param):
#     dtypes_dict = {}
#     for i, j in zip(df_param.columns, df_param.dtypes):
#         if "object" in str(j):
#             dtypes_dict.update({i: sqlalchemy.types.NVARCHAR(length=255)})
#
#         if "datetime" in str(j):
#             dtypes_dict.update({i: sqlalchemy.types.DateTime()})
#
#         if "float" in str(j):
#             dtypes_dict.update({i: sqlalchemy.types.Float(precision=3, asdecimal=True)})
#
#         if "int" in str(j):
#             dtypes_dict.update({i: sqlalchemy.types.INT()})
#
#     return dtypes_dict


def insert_db(df_result, config, output_session=False):
    # "uri_database": "mysql://root:root@localhost:3306/bnn",
    custom_uri = config['uri_database']
    print("connection {}".format(custom_uri))
    engine = create_engine(custom_uri, encoding='utf-8')

    # process dtype --> type of sql
    # output_dict = convert_dtype_sql(df_result)

    dict_type = {}
    list_int = ["id_file", "area_id", "year"]
    for col_temp in df_result:
        if col_temp in list_int:
            dict_type[col_temp] = INTEGER
        else:
            if 'mysql' in config['uri_database']:
                dict_type[col_temp] = sqlalchemy.dialects.mysql.LONGTEXT
            else:
                dict_type[col_temp] = NVARCHAR
    if output_session:
        # save to output_session table
        df_result.to_sql('output_session',
                         engine, method='multi', if_exists='append', index=False,
                         dtype=dict_type)
    else:
        # normally save result data to db
        df_result.to_sql(config['output_table_name_temp'],
                         engine, method='multi', if_exists='append', index=False,
                         dtype=dict_type)


def split_df(df_in, chunk_s):
    # 9
    # 4
    chunks = list()
    chunk_size = int(chunk_s)
    num_chunks = math.ceil(len(df_in) / chunk_size)
    for i in range(num_chunks):
        chunks.append(df_in[i * chunk_size:(i + 1) * chunk_size])
    return chunks


def group_result_df(df_in, column_concat):
    # # firstly, rename column_concat
    tmp_column_concat = f'tmp_{column_concat}'

    # list columns to group
    list_group_columns = list(df_in.columns)
    list_group_columns.remove(column_concat)

    df_result = df_in.groupby(list_group_columns)[column_concat].apply(set).reset_index(name=tmp_column_concat)
    df_result[column_concat] = df_result.apply(lambda row: '; '.join([str(i) for i in list(row[tmp_column_concat])]),
                                               axis=1)
    df_result = df_result.drop(columns=[tmp_column_concat])
    return df_result


def main_process(command_api, number_skipping_words=0):
    current_folder = os.getcwd()
    list_extension_keep = ['docx', 'pdf', 'doc']
    # keep_df_info = True  # If True, save df_info, only keep this file for preview
    delete_temp_folder = True  # If True, delete folder contains all downloaded files
    config = util.get_config()
    session_id = util.get_session_id(config)
    # more
    created_date = util.get_current_date()

    # 1. GET ALL INPUT DATA
    df_info, dict_general_keywords, dict_specific_keywords, active_folder, api_info = get_all_input_data(
        session_id, config, command_api, current_folder, list_extension_keep)

    # 2. PROCESS
    result_list, log_file, err = process_all_report(df_info, dict_general_keywords, dict_specific_keywords,
                                                    number_skipping_words,
                                                    session_id, command_api, api_info, active_folder)

    # 3. SAVE RESULT
    df = pd.DataFrame(result_list)
    # group duplicate sent, keyword_topic
    print(f"Start Processing duplicate results...")
    df = group_result_df(df, column_concat='keywords_topic_1')
    print(f"Finish processing duplicate results...")

    # df that has output session information
    df_session = pd.DataFrame([{"created_by": api_info,
                                "session_id": session_id,
                                "created_date": created_date,
                                "api_info": api_info}])
    insert_db(df_session, config, output_session=True)

    list_df_write = split_df(df, config['batch_size'])
    f_log = open(log_file, 'a', encoding='utf-8')
    print_and_log_file(f_log, f"Start inserting to database...")
    for i in range(len(list_df_write)):
        print_and_log_file(f_log, f"Writing data at batch: {i} to database")
        try:
            insert_db(list_df_write[i], config)

            # ins
        except Exception as e:
            print_and_log_file(f_log, f"Error writing data at batch: {i} to db, error: {str(e)}")
    print_and_log_file(f_log, f"Number of processed files: {len(df_info)}, success = {len(df_info) - err} files, "
                              f"error = {err} files")
    f_log.close()

    # 4. REMOVE ALL TEMPORARY FILES
    # shutil.rmtree(active_folder, ignore_errors=True)
    if delete_temp_folder:
        # print(f"Active folder = {active_folder}")
        data_folder = util.make_dir(os.path.join(active_folder, 'data'))
        shutil.rmtree(data_folder)
    return session_id


def main_process_tables(command_api, number_skipping_words=0):
    current_folder = os.getcwd()
    list_extension_keep = ['docx', 'pdf', 'doc']
    # keep_df_info = True  # If True, save df_info, only keep this file for preview
    delete_temp_folder = True  # If True, delete folder contains all downloaded files
    config = util.get_config()
    session_id = util.get_session_id(config)
    # more
    created_date = util.get_current_date()

    # 1. GET ALL INPUT DATA
    df_info, dict_general_keywords, dict_specific_keywords, active_folder, api_info = get_all_input_data(
        session_id, config, command_api, current_folder, list_extension_keep)

    # 2. PROCESS

    tables = process_tables_all_report(df_info, active_folder)

    # 4. REMOVE ALL TEMPORARY FILES
    # shutil.rmtree(active_folder, ignore_errors=True)
    if delete_temp_folder:
        # print(f"Active folder = {active_folder}")
        data_folder = util.make_dir(os.path.join(active_folder, 'data'))
        shutil.rmtree(data_folder)
    return tables


def main_process_info(command_api, number_skipping_words=0):
    current_folder = os.getcwd()
    list_extension_keep = ['docx', 'pdf', 'doc']
    # keep_df_info = True  # If True, save df_info, only keep this file for preview
    delete_temp_folder = True  # If True, delete folder contains all downloaded files
    config = util.get_config()
    session_id = util.get_session_id(config)
    # more
    created_date = util.get_current_date()

    # 1. GET ALL INPUT DATA
    df_info, dict_general_keywords, dict_specific_keywords, active_folder, api_info = get_all_input_data(
        session_id, config, command_api, current_folder, list_extension_keep)

    # 2. PROCESS
    #result_list, log_file, err = process_content_all_report(df_info, active_folder)
    result_list, log_file, err = process_all_report(df_info, dict_general_keywords, dict_specific_keywords,
                                                    number_skipping_words,
                                                    session_id, command_api, api_info, active_folder)
    df = pd.DataFrame(result_list)
    # group duplicate sent, keyword_topic
    print(f"Start Processing duplicate results...")
    df = group_result_df(df, column_concat='keywords_topic_1')

    # 4. REMOVE ALL TEMPORARY FILES
    # shutil.rmtree(active_folder, ignore_errors=True)
    if delete_temp_folder:
        # print(f"Active folder = {active_folder}")
        data_folder = util.make_dir(os.path.join(active_folder, 'data'))
        shutil.rmtree(data_folder)
    return df