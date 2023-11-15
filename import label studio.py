import requests
import json
from main.handle_information import *

api_url = "http://localhost:8080/api/projects/2/import"
headers =  {"Content-Type":"application/json",  "Authorization": "Token 736f5d228135dc5bd11f74d4fd890369e719417d"}


df = main_process_info("https://giamsatdanhgia.mard.gov.vn/api/link?id=63")
data =[]
for doc in df['sentence_contain_keywords'].head(5):
    data.append(
        {"text": doc, "question": ""})
response = requests.post(api_url, data=json.dumps(data), headers=headers)
response.json()
response.status_code

