from docx import Document
import pandas as pd
from main.handle_information import *
from main.util import get_config
import json
from flask import Flask, redirect, url_for, request,jsonify
app = Flask(__name__)


@app.route("/extract_table", methods=['GET'])
def extract_table():
    document = Document('D:\\3.docx')
    tables = []
    keyword = request.args.get('kw')
    for table in document.tables:
        found = False
        df = [['' for i in range(len(table.columns))] for j in range(len(table.rows))]
        for i, row in enumerate(table.rows):
            for j, cell in enumerate(row.cells):
                if cell.text:
                    df[i][j] = cell.text
                    if keyword in cell.text:
                        found = True
        if found:
            tables.append(pd.DataFrame(df))

    n = request.args.get('n', type=int)

    for nr, i in enumerate(tables):
        #i.to_csv("table_" + str(nr) + ".csv", header=False, index=False, encoding='utf-16')
        if nr == n:
            data = i.to_json(orient='records', force_ascii=False)
            return data
    return ""

@app.route("/extract_table2", methods=['GET'])
def extract_table2():
    if 'command_api' in request.args:
        command_api = request.args['command_api']

        # try:
        tables = main_process_tables(command_api)
        keyword = "a" #request.args.get('kw')
        for table in tables:
            found = False
            df = [['' for i in range(len(table.columns))] for j in range(len(table.rows))]
            for i, row in enumerate(table.rows):
                for j, cell in enumerate(row.cells):
                    if cell.text:
                        df[i][j] = cell.text
                        if keyword in cell.text:
                            found = True
            if found:
                tables.append(pd.DataFrame(df))

        n = 1 #request.args.get('n', type=int)

        for nr, i in enumerate(tables):
            # i.to_csv("table_" + str(nr) + ".csv", header=False, index=False, encoding='utf-16')
            if nr == n:
                data = i.to_json(orient='records', force_ascii=False)
                return data
        return "no data found"
    else:
        return "Error: No command_api field provided. Please specify an command_api."



    n = request.args.get('n', type=int)

    for nr, i in enumerate(tables):
        #i.to_csv("table_" + str(nr) + ".csv", header=False, index=False, encoding='utf-16')
        if nr == n:
            data = i.to_json(orient='records', force_ascii=False)
            return data
    return ""


@app.route('/api_process_reports', methods=['GET'])
def api_process():
    if 'command_api' in request.args:
        command_api = request.args['command_api']

        # try:
        tables = main_process(command_api)
        return f"Process successfully with counted tables : {tables.count()}"
        # except:
        #     return "Error when processing..."
    else:
        return "Error: No command_api field provided. Please specify an command_api."


if __name__ == '__main__':
    app.run(debug=True)

