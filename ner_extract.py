from docx import Document
import pandas as pd
from main.handle_information import *
from main.util import get_config
import json
from flask import Flask, redirect, url_for, request,jsonify
import spacy
nlp = spacy.load("xx_sent_ud_sm")

app = Flask(__name__)

@app.route("/extract_info", methods=['GET'])
def extract_info():
    if 'command_api' in request.args:
        command_api = request.args['command_api']

        # try:
        data = main_process_info(command_api)

        return data
    else:
        return "Error: No command_api field provided. Please specify an command_api."



if __name__ == '__main__':
    app.run(debug=True)

