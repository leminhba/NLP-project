import requests
import json
from main.handle_information import *

api_url = "http://localhost:8080/api/projects/2/import"
todo = {"text": "President Recep Tayyip Erdogan has said Turkey was ready to help seek a “peaceful resolution” to an armed rebellion in Russia, in a phone call with his Russian counterpart Vladimir Putin, his office said", "question": "Some text 4"}
headers =  {"Content-Type":"application/json",  "Authorization": "Token 736f5d228135dc5bd11f74d4fd890369e719417d"}
#response = requests.post(api_url, data=json.dumps(todo), headers=headers)
#response.json()
#response.status_code

df = main_process_info("https://giamsatdanhgia.mard.gov.vn/api/link?id=63")
for doc in df['sentence_contain_keywords'].head(5):
    todo = {
        "text": doc,
        "question": ""}
    response = requests.post(api_url, data=json.dumps(todo), headers=headers)
    response.json()
    response.status_code

