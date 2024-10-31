import requests
import json

url = "https://api.line.me/v2/bot/message/push"
uuid = "U7f3349a1885dc7ae6f38c1a2b5808137"
token = "dVoaynpH9HCvrLOMNr3r5n1gLERXEkEqy4T/rZaVCA6phXSo5jgoEsYCGJZ/ZoYdU/HW0BhJG8i05pZwHJUmGHMIlMCZEux7vCra8wU5/1puLJSDSte6ilAF3XYTU9QqeOg3zU79sAkBSiZIQLIIRgdB04t89/1O/w1cDnyilFU="
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

