import paho.mqtt.publish as publish
import paho.mqtt.client as mqtt
import time
import json
import random
import os
from dotenv import load_dotenv
import cv2 as cv
import requests
from img_bb import upload_image_to_imgbb
# from picamzero import Camera
import serial
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
IR = 27

GPIO.setup(IR, GPIO.IN)

load_dotenv()

PORT = 1883
SERVER_IP = "broker.netpie.io"

SUBSCRIBE_TOPIC = "@msg/pic"
PUBLISH_TOPIC = "@msg/sensors"

CLIENT_ID = os.environ.get('MQTT_CLIENT_ID')
TOKEN = os.environ.get('MQTT_TOKEN')
SECRET = os.environ.get('MQTT_SECRET')

MqttUser_Pass = {"username": TOKEN, "password": SECRET}

IMGBB_API_KEY = os.environ.get('IMGBB_API_KEY')



def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe(SUBSCRIBE_TOPIC)

def on_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.payload))
    #cap = cv.VideoCapture(0)
    #ret, frame = cap.read()
    #cv.imshow("Pic", frame)
    # cam = Camera()
    # cam.resolution = (1920, 1080)
    # cam.start_preview()
    # cam.take_photo("./live_images/test_img.jpg")
    # cam.stop_preview()
    os.system("libcamera-still -o ./live_images/test_img.jpg --vflip --hflip")
    #cv.imwrite("./live_images/test_img.jpg", frame)
    #cv.waitKey(1)
    #cap.release()
    #cv.destroyAllWindows()
    image_url = upload_image_to_imgbb("./live_images/test_img.jpg", IMGBB_API_KEY)
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



    
if __name__ == '__main__':
    client = mqtt.Client(protocol=mqtt.MQTTv311, client_id=CLIENT_ID, clean_session=True)
    client.on_connect = on_connect
    client.on_message = on_message

    client.subscribe(SUBSCRIBE_TOPIC)
    client.username_pw_set(TOKEN, SECRET)
    client.connect(SERVER_IP, PORT)
    client.loop_start()

    uart = serial.Serial(
        port='/dev/serial0',
        baudrate=115200,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        timeout=1
        )
    if uart.isOpen():
        print("UART connectoin established. Listening for sensor readings...")
    else:
        print("Failed to open UART connection")
    
    started = False

    while not started:
        if GPIO.input(IR) == 0:
            print("Detect Fruit. Starting the Program")
            started = True
            uart.write("1\n".encode('utf-8'))
            break
        print("No Fruit Detected")
        time.sleep(1)
    
    while started:
        # Get Data from STM32 via USART
        incoming_string = uart.readline()
        print(incoming_string)
        data = {}
        if len(incoming_string):
            data = json.loads(incoming_string)
        # Dummy Data
        # data = {
            # "temp": random.randrange(0, 100),
            # "hum": random.randrange(0, 100),
            # "red": random.randrange(0, 255),
            # "green": random.randrange(0, 255),
            # "blue": random.randrange(0, 255),
            # "alc": random.randrange(0, 100),
            # "status": "Fresh",
        # }
        data_out = json.dumps({"data": data})
        client.publish(PUBLISH_TOPIC, data_out, retain=True)
        print("Publish...")
        time.sleep(2)

