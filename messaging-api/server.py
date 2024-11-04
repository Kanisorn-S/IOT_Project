import os
import uvicorn
import json

from contextlib import asynccontextmanager
from typing import Any

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

from fastapi import FastAPI, Request, HTTPException, Header
from fastapi_mqtt.config import MQTTConfig
from fastapi_mqtt.fastmqtt import FastMQTT
from gmqtt.mqtt.constants import MQTTv311

from response_message import response_message

# LINE Access Key
get_access_token = os.environ.get('ACCESS_TOKEN')
configuration = Configuration(access_token=get_access_token)
# LINE Secret Key
get_channel_secret = os.environ.get('CHANNEL_SECRET')
handler = WebhookHandler(channel_secret=get_channel_secret)

# NETPIE
CLIENT_ID = os.environ.get('CLIENT_ID')
TOKEN = os.environ.get('TOKEN')
SECRET = os.environ.get('SECRET')

mqtt_config = MQTTConfig(
  host="broker.netpie.io",
  port=1883,
  username=TOKEN,
  password=SECRET,
  version=MQTTv311,
)

fast_mqtt = FastMQTT(
   config=mqtt_config,
   client_id=CLIENT_ID
)

@asynccontextmanager
async def _lifespan(_app: FastAPI):
   await fast_mqtt.mqtt_startup()
   yield
   await fast_mqtt.mqtt_shutdown()

app = FastAPI(lifespan=_lifespan)

mqtt_msg = ""

@fast_mqtt.on_connect()
def connect(client, flags, rc, properties):
  fast_mqtt.client.subscribe("@msg/sensors")
  print("Connected: ", client, flags, rc, properties)

@fast_mqtt.on_message()
async def message(client, topic, payload, qos, properties):
  print("Received message: ", topic, payload.decode(), qos, properties)
  global mqtt_msg
  mqtt_msg = payload.decode()
  print(json.loads(mqtt_msg))
  return 0

@fast_mqtt.subscribe("@msg/sensors")
async def message_to_topic(client, topic, payload, qos, properties):
    print("Received message to specific topic: ", topic, payload.decode(), qos, properties)

@fast_mqtt.on_disconnect()
def disconnect(client, packet, exc=None):
    print("Disconnected")

@fast_mqtt.on_subscribe()
def subscribe(client, mid, qos, properties):
    print("subscribed", client, mid, qos, properties)


@app.get("/")
async def func():
    global fast_mqtt
    fast_mqtt.publish("@msg/dht22", "Hello from Fastapi") 

    global mqtt_msg
    return {"result": True,"message":mqtt_msg }

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

        global mqtt_msg
        reply_message = response_message(event, mqtt_msg)
        if reply_message == 1:
            global fast_mqtt
            fast_mqtt.publish('@msg/pic', '1')
        else: 
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[reply_message]
                )
            )


if __name__ == "__main__":

    uvicorn.run(app, host="0.0.0.0")