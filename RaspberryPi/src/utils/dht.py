import Adafruit_DHT

DHT_SENSOR = Adafruit_DHT.DHT22
DHT_PIN = 4  # GPIO pin where the DHT22 is connected

def read_dht22():
    humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
    if humidity is not None and temperature is not None:
        return {'temperature': temperature, 'humidity': humidity}
    else:
        return {'error': 'Failed to retrieve data from humidity sensor'}
