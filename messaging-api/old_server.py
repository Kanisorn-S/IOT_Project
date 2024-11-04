import os
import uvicorn

from fastapi import FastAPI, Request, HTTPException, Header

from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.webhooks import MessageEvent, TextMessageContent

from linebot.v3.messaging import (
    ApiClient, 
    MessagingApi, 
    Configuration, 
    ReplyMessageRequest, 
    TextMessage, 
    # FlexMessage, 
    # Emoji,
)

from response_message import response_message

import paho.mqtt.publish as publish
import paho.mqtt.client as mqtt
import time
import json
import random
import ssl

app = FastAPI()

# LINE Access Key
get_access_token = os.environ.get('ACCESS_TOKEN')
configuration = Configuration(access_token=get_access_token)
# LINE Secret Key
get_channel_secret = os.environ.get('CHANNEL_SECRET')
handler = WebhookHandler(channel_secret=get_channel_secret)

@app.post("/callback")
async def callback(request: Request, x_line_signature: str = Header(None)):
    body = await request.body()
    body_str = body.decode('utf-8')
    try:
        handler.handle(body_str, x_line_signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        raise HTTPException(status_code=400, detail="Invalid signature.")

    return 'OK'

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event: MessageEvent):
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)

        reply_message = "Hello from Dev Environment"

        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=reply_message)]
            )
        )

if __name__ == "__main__":

    uvicorn.run(app, host="0.0.0.0")

    PORT = 1883
    SERVER_IP = "broker.netpie.io"

    SUBSCRIBE_TOPIC = "@msg/sensors"
    PUBLISH_TOPIC = "@msg/dht"

    CLIENT_ID = "acff940e-e89c-4939-b55f-26e079cf05ce"
    TOKEN = "WPqKsCuDf4syDQHR7LP4EgaxQ46X27ZG"
    SECRET = "3hMYNLXHTH2gXPQJ43vqGuhmGJGgvV6J"

    MqttUser_Pass = {"username": TOKEN, "password": SECRET}

    def on_connect(client, userdata, flags, rc):
        print("Connected with result code " + str(rc))
        client.subscribe(SUBSCRIBE_TOPIC)

    def on_message(client, userdata, msg):
        print(msg.topic + " " + str(msg.payload))
    
    client = mqtt.Client(protocol=mqtt.MQTTv311, client_id=CLIENT_ID, clean_session=True)
    client.on_connect = on_connect
    client.on_message = on_message

    client.subscribe(SUBSCRIBE_TOPIC)
    client.username_pw_set(TOKEN, SECRET)
    client.connect(SERVER_IP, PORT)
    client.loop_start()

    while True:
    # Get Data from STM32 via USART
    # Dummy Data
        data = {
            "Temp": random.randrange(0, 100),
            "Humi": random.randrange(0, 100),
            "R": random.randrange(0, 255),
            "G": random.randrange(0, 255),
            "B": random.randrange(0, 255),
            "Gas Value": random.randrange(0, 100),
        }
        data_out = json.dumps({"data": data})
        client.publish(PUBLISH_TOPIC, data_out, retain=True)
        print("Publish...")
        time.sleep(2)

