import time 
import board 
import adafruit_dht

sensor = adafruit_dht.DHT22(board.D4)

while True:
    try:
        tempC = sensor.temperature
        hum = sensor.humidity
        print("Temp: ", tempC)
        print("Hum: ", hum)
    except RuntimeError as error:
        print(error.args[0])
        time.sleep(2)
        continue
    except Exception as errror:
        sensor.exit()
        raise error

    time.sleep(3)
