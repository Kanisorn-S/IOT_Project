import cv2 as cv
import paho.mqtt.publish as publish
import paho.mqtt.client as mqtt
from time import sleep
import serial
import requests
import os
import requests
import json
from dotenv import load_dotenv
from utils.img_bb import upload_image_to_imgbb
from utils.classify import predict_from_cap

# Tensorflow 
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

import tensorflow as tf
from utils.model import predict_fruits

model = tf.keras.models.load_model('./model/MyModel.keras')

load_dotenv()

# UART setup
uart = serial.Serial(
        port='/dev/serial0',
        baudrate=115200,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        timeout=1
)

if uart.isOpen():
    print("UART connection established. Listening for sensor readings...")
else:
    print("Failed to open UART connection.")

# MQTT setup
PORT = 1883
SERVER_IP = "broker.netpie.io"

SUBSCRIBE_TOPIC = "@msg/pic"
PUBLISH_TOPIC = "@shadow/data/update"
PUBLISH_TOPIC_2 = "@msg/sensors"

CLIENT_ID = os.environ.get('MQTT_CLIENT_ID')
TOKEN = os.environ.get('MQTT_TOKEN')
SECRET = os.environ.get('MQTT_SECRET')

MqttUser_Pass = {"username": TOKEN, "password": SECRET}

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe(SUBSCRIBE_TOPIC)

def on_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.payload))
    cap = cv.VideoCapture(0)
    ret, frame = cap.read()
    cv.imshow("Pic", frame)
    cv.imwrite("./images/test_img.jpg", frame)
    cv.waitKey(1)
    cap.release()
    cv.destroyAllWindows()
    image_url = upload_image_to_imgbb("./images/test_img.jpg", IMGBB_API_KEY)
    url = "https://api.line.me/v2/bot/message/push"
    uuid = os.environ.get('LINE_OA_UUID') 
    token = os.environ.get('LINE_OA_TOKEN')
    headers = {
        'content-type': 'application/json',
        'Authorization': 'Bearer ' + token
    }

    current_img = {
        "type": "image",
        "originalContentUrl": image_url,
        "previewImageUrl": image_url,
    }

    msg = {
        "type": "text",
        "text": "Here's the current picture!"
    }

    data = {
        "to": uuid,
        "messages": [
            msg,
            current_img
        ]
    }

    res = requests.post(url, headers=headers, data=json.dumps(data))
    print(res.text)
    
client = mqtt.Client(protocol=mqtt.MQTTv311, client_id=CLIENT_ID, clean_session=True)
client.on_connect = on_connect
client.on_message = on_message

client.subscribe(SUBSCRIBE_TOPIC)
client.username_pw_set(TOKEN, SECRET)
client.connect(SERVER_IP, PORT)
client.loop_start()

# IMGBB Setup
IMGBB_API_KEY = os.environ.get("IMGBB_API_KEY")

started = False

try: 
  while True:

    if started:
        # Get Data from STM32 via USART
        data_out = uart.readline()

        # Publish to NETPIE
        client.publish(PUBLISH_TOPIC, data_out, retain=True)
        client.publish(PUBLISH_TOPIC_2, data_out, retain=True)
        print("Publish...")
        sleep(2)

    # Wait for IR sensor to detect fruit
    elif not started and True:
        # Classify fruit, then send fruit name to STM32 via UART
        cap = cv.VideoCapture(0)
        # Image classification
        img_path = './images/fruit.png'
        fruit = predict_from_cap(model, cap, img_path)
        uart.write(fruit.encode('utf-8'))
        cap.release()
        cv.destroyAllWindows()
        started = True

    else:
       pass

except KeyboardInterrupt:
  print("Program Terminated")

finally:
  uart.close()
  cv.destroyAllWindows()
  print("Clean up...")
