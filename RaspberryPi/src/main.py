import cv2 as cv
import paho.mqtt.publish as publish
import paho.mqtt.client as mqtt
from time import sleep
import serial
import requests

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

SUBSCRIBE_TOPIC = "@msg/llama"
PUBLISH_TOPIC = "@shadow/data/update"
PUBLISH_TOPIC_2 = "@msg/sensors"

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

# Line Notify setup
url = "https://notify-api.line.me/api/notify"
token = "Vt9BNQWixeFboNwXUInqDOBpHvDbRrWbJtskzA0ZPYm"
headers = {'Authorization':'Bearer ' + token}

def send_line_notify(message: str, img: str = None):
    if img:
        msg = {
            "message": (None, message),
            "imageFile": open(img)
        }
        res = requests.post(url, headers=headers, files=msg)
        print(res.text)
    else:
        msg = {
            "message": message
        }
        res = requests.posst(url, headers, data=msg)
        print(res.text)
        
cap = cv.VideoCapture(0)
try: 
  while True:
      # Get Data from STM32 via USART
      data_out = uart.readline()

      # Image Recognition
      ret, frame = cap.read()
      cv.imshow("Webcam", frame)    
      # Publish to NETPIE
      client.publish(PUBLISH_TOPIC, data_out, retain=True)
      client.publish(PUBLISH_TOPIC_2, data_out, retain=True)
      print("Publish...")
      sleep(2)

except KeyboardInterrupt:
  print("Program Terminated")

finally:
  uart.close()
  cap.release()
  cv.destroyAllWindows()
  print("Clean up...")
