import paho.mqtt.publish as publish
import paho.mqtt.client as mqtt
import time
import json
import random
import ssl

PORT = 1883
SERVER_IP = "broker.netpie.io"

SUBSCRIBE_TOPIC = "@msg/llama"
PUBLISH_TOPIC = "@shadow/data/update"

CLIENT_ID = "fcbcbc65-61b8-41bd-a18b-efae842c5841"
TOKEN = "SM7Wwmuxh8DkS39bjn9kYWaJYL7qEMoy"
SECRET = "yesZhxw3b9uXsSnRN9pW8FXJZ7K1e8aS"

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

