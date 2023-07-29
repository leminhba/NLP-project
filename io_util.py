# import csv
# import time
import joblib
import pandas as pd
import pyodbc
from sqlalchemy import create_engine


def save_model(model, path_model):
    print(f"Saving model to: {path_model}...")
    joblib.dump(model, path_model, compress=True)


def load_model(path_model):
    print(f"Loading model from: {path_model}...")
    return joblib.load(path_model)


# def load_data(path_data):
#     df = pd.read_excel(path_data)
#     return df

TYPE_DATA_EXCEL = 'excel'
TYPE_DATA_SQL_SERVER = 'sql_server'


# TABLE_NAME_PREDICT_OUTPUT = 'output_predict'


def read_data(type_data, config=None, **kwargs):
    if type_data == TYPE_DATA_EXCEL:
        if 'path_data' in kwargs:
            path_data = kwargs['path_data']
            if path_data is not None:
                df = pd.read_excel(path_data)
                df_extract = df[df['status'] == 1]
                return df_extract
            else:
                print(f"path_data is not found!")
                return None
        else:
            print(f"Please provide 'path_data' parameter")
            return None
    elif type_data == TYPE_DATA_SQL_SERVER:
        return read_data_type_db(config,  config['input_table_name'], where_stm='WHERE status = 1')
    print(f"Error, not found any data type match with list of type: excel, sql_server")
    return None


def read_data_type_db(config, table_read, where_stm=None):
    # "uri_database": "mysql://root:root@localhost:3306/bnn",
    #where_stm: 'WHERE status = 1'
    if config is None:
        print(f"Config not found!")
        return None
    if 'uri_database' in config:
        # custom_uri = config['uri_database']
        # print("connection {}".format(custom_uri))


        # engine = create_engine(custom_uri, encoding='utf-8')
        # conn = engine.connect().execution_options(autocommit=True)
        custom_uri = config['test_db']
        print(f"New URI: {custom_uri}")

        cnxn = pyodbc.connect(custom_uri)


        # output_table_name = config['output_table_name']

        sql_query_stm = f"SELECT * FROM {table_read}"
        if where_stm is not None:
            sql_query_stm = f"{sql_query_stm} {where_stm}"
        df = pd.read_sql(sql_query_stm, cnxn)
        cnxn.close()
        return df
    else:
        print(f"'uri_database' not found in config file")
        return None


def read_data_predict(type_data, **kwargs):
    # READ DATA FOR PREDICT PERIOD
    print(f"kwargs >>>> {kwargs}")
    query_report = None
    if 'query_report' in kwargs:
        query_report = kwargs['query_report']
    if type_data == TYPE_DATA_EXCEL:
        if 'path_data' in kwargs:
            path_data = kwargs['path_data']
            df = pd.read_excel(path_data)
            if query_report is not None:
                for stm in query_report.split('AND'):
                    list_equation = stm.split('=')
                    if len(list_equation) == 2:
                        left = list_equation[0]
                        right = list_equation[1]
                        df = df[df[left] == right]
            return df
        else:
            print(f"Please provide 'path_data' parameter")
            return None
    elif type_data == TYPE_DATA_SQL_SERVER:
        config_in = None
        if 'config_in' in kwargs:
            config_in = kwargs['config_in']
            print(f"config_in in kwargs, config = {config_in}")
        else:
            print(f"config_in NOT FOUND in kwargs")
        if config_in is not None:
            print(f"config_new = {config_in}")
        else:
            print(f"ERROR: config not found!")
        if query_report is not None:
            return read_data_type_db(config_in,  config_in['input_table_name'], where_stm=f'WHERE {query_report}')
        else:
            return read_data_type_db(config_in,  config_in['input_table_name'])
    print(f"Error, not found any data type match with list of type: excel, sql_server")
    return None


# def read_data_predict_demo(path_data, year_report):
#     df = pd.read_excel(path_data)
#     if year_report is not None:
#         df = df[df['year'] == year_report]
#     return df


def save_data_result_excel(df, path_data):
    df.to_excel(path_data, index=False)
    print(f"Save result data successfully...")

# if __name__ == '__main__':
#     df = load_data('/home/anhdt157/data/DMP/Agr/ai_ml_tool/data_test/demo_data.xls')
#     df_x = df[df['status'] == 1]
#     print(df_x.head())
