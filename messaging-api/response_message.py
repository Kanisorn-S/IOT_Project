from linebot.v3.messaging import TextMessage
import paho.mqtt.publish as publish
import paho.mqtt.client as mqtt
import json
import time

def response_message(event, msg):

    request_message = event.message.text
    sensors_data = json.loads(msg)
    response = "No data found"
    if sensors_data["data"][str(request_message)]:
      response = "The current " + str(request_message) + " is " + str(sensors_data["data"][str(request_message)])



    return TextMessage(text=response)