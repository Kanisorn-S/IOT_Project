import paho.mqtt.publish as publish
import paho.mqtt.client as mqtt
import time
import json
import random
import os
from dotenv import load_dotenv

load_dotenv()

PORT = 1883
SERVER_IP = "broker.netpie.io"

SUBSCRIBE_TOPIC = "@msg/llama"
PUBLISH_TOPIC = "@msg/sensors"

CLIENT_ID = os.environ.get('MQTT_CLIENT_ID')
TOKEN = os.environ.get('MQTT_TOKEN')
SECRET = os.environ.get('MQTT_SECRET')

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
        "temp": random.randrange(0, 100),
        "hum": random.randrange(0, 100),
        "red": random.randrange(0, 255),
        "green": random.randrange(0, 255),
        "blue": random.randrange(0, 255),
        "alc": random.randrange(0, 100),
        "status": "Fresh",
    }
    data_out = json.dumps({"data": data})
    client.publish(PUBLISH_TOPIC, data_out, retain=True)
    print("Publish...")
    time.sleep(2)

