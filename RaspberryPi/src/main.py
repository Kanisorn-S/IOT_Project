import cv2 as cv
import paho.mqtt.publish as publish
import paho.mqtt.client as mqtt
from time import sleep
import serial
import requests
import os
import requests
import json
import time
import RPi.GPIO as GPIO
# from picamzero import Camera
# from picamera2 import Picamera2, Preview
from dotenv import load_dotenv
from utils.img_bb import upload_image_to_imgbb
from utils.classify import predict_from_cap, predict_from_path
import board
import adafruit_dht

# Tensorflow 
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

import tensorflow as tf
from utils.model import predict_fruits

model = tf.keras.models.load_model('./model/new.h5')

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
    # cam = Camera()
    # cam.resolution = (1920, 1080)
    # cam.take_photo("./live_images/test_img.jpg")
    # cam.stop_preview()
    os.system("libcamera-still -o ./images/test_img.jpg --vflip --hflip")
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

# GPIO setup
GPIO.setmode(GPIO.BCM)
IR = 27
GPIO.setup(IR, GPIO.IN)

# IMGBB Setup
IMGBB_API_KEY = os.environ.get("IMGBB_API_KEY")

started = False
# fruit_id = "69"
fruit_conversion = {
        "Apple": "0",
        "Banana": "1",
        "Mango": "2",
}

first_request = True

TEMP_THRESHOLD = 28
HUM_APPLE_MIN = 90
HUM_APPLE_MAX = 95
HUM_BANANA_MIN = 50
HUM_BANANA_MAX = 95
HUM_MANGO_MIN = 90
HUM_MANGO_MAX = 95

# Initialize DHT22
sensor = adafruit_dht.DHT22(board.D4)

def temp_status(temp, temp_max, hum, hum_min, hum_max):
    if temp > temp_max:
        return 1
    elif hum > hum_max or hum < hum_min:
        return 1
    else:
        return 0



try: 

    while not started:
        if GPIO.input(IR) == 0:
            print("Detect Fruit. Starting the Program")
            # Classify fruit
            img_path = './images/current_fruit.jpg'
            os.system("libcamera-still -o ./images/current_fruit.jpg --vflip --hflip")
            fruit = predict_from_path(model, img_path)
            print("Predicted fruit: ", fruit)
            if fruit in fruit_conversion:
                global fruit_id
                fruit_id = str(fruit_conversion[fruit])
            else:
                print(f"Fruit '{fruit}' not recognized. Defaulting to 'Unknown'.")
                fruit_id = "69"
            uart.write("1\n".encode('utf-8'))
            time.sleep(1)
            uart.write(f'f{fruit_id}\n'.encode('utf-8'))
            started = True
            break
        print("No Fruit Detected")
        time.sleep(1)

    while started:

        # Get Data from DHT22
        try:
            temp = sensor.temperature
            hum = sensor.humidity
            print("Temp: ", temp)
            print("Hum: ", hum)
        except RuntimeError as error:
            # print(error.args[0])
            sleep(2)
            continue
        except Exception as error:
            sensor.exit()
            raise error
        # Get Data from STM32 via USART
        incoming_string = uart.readline()
        # print(incoming_string)
        if first_request:
            data = {}
            first_request = False
        if len(incoming_string):
            try:
                data = json.loads(incoming_string)
                data["temp"] = temp
                data["hum"] = hum
                if data["status"] == 0:
                    print("STM32 returned status 0.") 
                    print("Current fruit_id: ", fruit_id)
                    if fruit_id == '0':
                        print("Checking apple status...")
                        data["status"] = temp_status(temp, TEMP_THRESHOLD, hum, HUM_APPLE_MIN, HUM_APPLE_MAX)
                        print(data["status"])
                    elif fruit_id == '1':
                        print("Checking banana status...")
                        data["status"] = temp_status(temp, TEMP_THRESHOLD, hum, HUM_BANANA_MIN, HUM_BANANA_MAX)
                        print(data["status"])
                    elif fruit_id == '2':
                        print("Checking mango status...")
                        data["status"] = temp_status(temp, TEMP_THRESHOLD, hum, HUM_MANGO_MIN, HUM_MANGO_MAX)
                        print(data["status"])

                current_status = str(data["status"])
                uart.write(current_status.encode('utf-8'))


            except Exception as e:
                print(f"Error processing incoming data: {e}")
                continue

        data_out = json.dumps({"data": data})


        # Publish to NETPIE
        client.publish(PUBLISH_TOPIC, data_out, retain=True)
        client.publish(PUBLISH_TOPIC_2, data_out, retain=True)
        print("Publish...")
        sleep(2)

except KeyboardInterrupt:
    print("Program Terminated")

finally:
    uart.close()
    print("Clean up...")
