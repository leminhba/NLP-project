from flask import Blueprint, request
from main_model.config.read_config import *
from main_model.util.io_util import *
from main_model.model.pipeline import *

predict_blueprint = Blueprint('predict', __name__)
@predict_blueprint.route('/predict_model')

def predict_classification():
    '''
       * 'query_report', not required, default = not specify - get all data in db
       * 'type_input_data', not required:
           + default: type_input_data = 'excel' for testing
               - please provide 'path_input_data' to read
               - demo: path_input_data = '/home/anhdt157/data/DMP/Agr/ai_ml_tool/data_test/demo_data.xls'
           + type_input_data = 'sql_server': Get data from sql_server, server info is got from config_run.json
       * 'path_input_data': only provide if using type_input_data = 'excel'
       * 'model_name', not required, default = use first saved model in list
       * 'type_save_data', not required:
           + default = 'excel' --> save data in excel file, with additional column: 'time'
           + 'sql_server': The result will be saved in sql server, in table: 'output_predict', with additional column: 'time'
       * 'path_save_data':
           + not required, only use if type_save_data is 'excel', default the result will be saved in main_model/result_classfication
       '''
    # config
    config = read_config_file()

    # Data input
    # ================================PARAM 1: year_report=========================================
    query_report = None
    if 'query_report' in request.args:
        query_report = request.args['query_report']
    else:
        print(f"No 'query_report' field provided. Take all the data in db")

    # ================================PARAM 2: type_input_data=========================================
    # [TYPE_DATA_EXCEL, TYPE_DATA_SQL_SERVER]
    type_input_data = TYPE_DATA_EXCEL
    if 'type_input_data' in request.args:
        type_input_data = request.args['type_input_data']

    # ================================PARAM 3: path_input_data=========================================
    path_input_data = None
    if 'path_input_data' in request.args:
        path_input_data = request.args['path_input_data']

    # ================================PARAM 4: model_name=========================================
    all_models = get_list_all_model_vectorizer()
    result = list(all_models.keys())
    print(f"type_result = {type(result)}, result = {result}")
    model_name = result[0]
    if 'model_name' in request.args:
        name_args = request.args['model_name']
        if name_args in result:
            model_name = name_args
        else:
            print(f"WARNING: model_name: {name_args} not found, use first available model instead")
    else:
        print(f"Field 'model_name' not found, use first available model instead")

    # ================================PARAM 5: type_save_data=========================================
    type_save_data = TYPE_DATA_EXCEL
    if 'type_save_data' in request.args:
        type_save_data = request.args['type_save_data']

    # ================================PARAM 6: path_save_data=========================================
    time_save_run = get_session_id(config)
    path_save_data = get_path_result_predict(model_name, time_save_run)
    print(f"path_save_data ====== {path_save_data}")
    if 'path_save_data' in request.args:
        path_save_data = request.args['path_save_data']

    # >>>> ===================STEP I: read input data============================
    df_report = read_data_predict(type_data=type_input_data, config_in=config, path_data=path_input_data,
                                  query_report=query_report)

    # >>>> =================== STEP II: Loading model ===================
    model_dict = all_models[model_name]
    model = load_model(model_dict['model_path'])
    vectorizer = load_model(model_dict['vectorizer_path'])

    # >>>> =================== STEP III: Predict ===================
    print(f"Start predicting with model_name: {model_name}")
    # time_save = str(round(time.time()))
    main_predict(model, vectorizer, df_report, model_name, type_save_data, time_save_run, config, path_save_data)
    return f"Predict successfully, data is saved at path: {path_save_data}"