from linebot.v3.messaging import TextMessage
import paho.mqtt.publish as publish
import paho.mqtt.client as mqtt
import json
import time
import string

def response_message(event, msg):

   request_message = event.message.text
   request_message = request_message.strip().lower().translate(str.maketrans('', '', string.punctuation)).split()
   requested = request_message[-1]
   sensors_data = json.loads(msg)
   response = "No data found"
   convert_word = {
      "color": "color",
      "temperature": "temp",
      "humidity": "hum",
      "alcohol": "alc",
      "status": "status",
      "picture": "pic",
   }
   requested_attr = convert_word[requested]
   if requested_attr == "color":
      response = "The current color is R: " + str(sensors_data["data"]["red"]) + " G: " + str(sensors_data["data"]["green"]) + " B: " + str(sensors_data["data"]["blue"])
   elif requested_attr == 'pic':
      return 1
   elif sensors_data["data"][str(requested_attr)]:
      response = "The current " + str(requested) + " is " + str(sensors_data["data"][str(requested_attr)])

   return TextMessage(text=response)