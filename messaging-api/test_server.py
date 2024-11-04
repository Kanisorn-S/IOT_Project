import os
import uvicorn
import json

from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Request, HTTPException, Header
from fastapi_mqtt.config import MQTTConfig
from fastapi_mqtt.fastmqtt import FastMQTT
from gmqtt.mqtt.constants import MQTTv311

from response_message import response_message

# NETPIE
CLIENT_ID = "acff940e-e89c-4939-b55f-26e079cf05ce"
TOKEN = "WPqKsCuDf4syDQHR7LP4EgaxQ46X27ZG"
SECRET = "3hMYNLXHTH2gXPQJ43vqGuhmGJGgvV6J"

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
  data = json.loads(mqtt_msg)
  print(data["data"]["Temp"])
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


if __name__ == "__main__":

    uvicorn.run(app, host="0.0.0.0")