from flask import Blueprint, request
from main.handle_information import main_process

extract_blueprint = Blueprint('extract', __name__)

@extract_blueprint.route("/extract", methods=['GET'])
def extract():
    if 'command_api' in request.args:
        command_api = request.args['command_api']
        type_exp = request.args['type_export']
        type_ext = request.args['type_extract']
        split_sent = request.args['split_sentence']
        keywords_string = None
        if 'keywords_string' in request.args:
            keywords_string = request.args['keywords_string']
        data = main_process(command_api, number_skipping_words=0, type_export=type_exp, type_extract=type_ext,
                            split_sentence=split_sent, keywords_string=keywords_string, predict=None)
        return data
    else:
        return "Error: No command_api field provided. Please specify an command_api."