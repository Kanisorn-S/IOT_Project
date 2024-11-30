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
   status_convert = {
      "2": "High risk of Spoilage",
      "1": "Risk of Rotten. Improper Storing Condition",
      "0": "Fresh",
   }
   requested_attr = convert_word[requested]
   if requested_attr == "color":
      response = "The current color is R: " + str(sensors_data["data"]["red"]) + " G: " + str(sensors_data["data"]["green"]) + " B: " + str(sensors_data["data"]["blue"])
   elif requested_attr == 'pic':
      return 1
   elif requested_attr == 'status':
      response = "The current status is " + str(status_convert[str(sensors_data["data"]["status"])])
   elif sensors_data["data"][str(requested_attr)] is not None:
      response = "The current " + str(requested) + " is " + str(sensors_data["data"][str(requested_attr)])
      if requested_attr == "temp":
         response += "°C"
      elif requested_attr == "hum":
         response += "%"
      elif requested_attr == "alc":
         response += "% Change"
      

   return TextMessage(text=response)