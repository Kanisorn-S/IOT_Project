import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

url = "https://api.line.me/v2/bot/message/push"
uuid = os.environ.get('LINE_OA_UUID') 
token = os.environ.get('LINE_OA_TOKEN')
headers = {
  'content-type': 'application/json',
  'Authorization': 'Bearer ' + token
}

messages = [{
      "type": "text",
      "text": "Hello, world"
}]

messages = [json.dumps(message) for message in messages]

data = {
  "to": uuid,
  "messages": [
    {
      "type": "text",
      "text": "Hello, world"
    }
  ]
}

res = requests.post(url, headers=headers, data=json.dumps(data))
print(res.text)

