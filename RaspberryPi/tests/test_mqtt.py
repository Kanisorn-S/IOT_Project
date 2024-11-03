import paho.mqtt.publish as publish
import paho.mqtt.client as mqtt
import time
import json
import random
import os
from dotenv import load_dotenv
import cv2 as cv
import requests

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

def upload_image_to_imgbb(image_path, api_key):
    # Open the image file in binary mode
    with open(image_path, "rb") as image_file:
        # Prepare the image data to upload
        files = {
            'image': image_file.read()
        }
        
        # API endpoint to upload the image
        url = "https://api.imgbb.com/1/upload"
        
        # Payload with API key and expiration time (optional)
        payload = {
            'key': api_key,
            'expiration': 600  # Expiration time in seconds (optional)
        }
        
        # Send POST request to upload the image
        response = requests.post(url, files=files, data=payload)
        
        # Check if the upload was successful
        if response.status_code == 200:
            # Extract the image URL from the response
            image_url = response.json()['data']['url']
            print("Image URL:", image_url)
            return image_url
        else:
            print("Error:", response.status_code, response.text)
            return None
        

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

