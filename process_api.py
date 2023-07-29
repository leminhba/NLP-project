from flask import request, Flask
from main.handle_information import main_process
from main.util import get_config
config = get_config()

app = Flask(__name__)
app.config["DEBUG"] = False
app.config['SERVER_NAME'] = config['local_server_name']


@app.route('/api_process_reports', methods=['GET'])
def api_process():
    if 'command_api' in request.args:
        command_api = request.args['command_api']
        number_skipping_words = 0
        if 'number_words' in request.args:
            number_skipping_words = int(request.args['number_words'])
        # try:
        session_id = main_process(command_api, number_skipping_words=number_skipping_words)
        return f"Process successfully with session_id: {session_id}"
        # except:
        #     return "Error when processing..."
    else:
        return "Error: No command_api field provided. Please specify an command_api."


if __name__ == '__main__':
    app.run()
