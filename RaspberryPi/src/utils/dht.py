import pigpio
import DHT22

DHT_PIN = 4  # GPIO pin where the DHT22 is connected

pi = pigpio.pi()
sensor = DHT22.sensor(pi, DHT_PIN)

def read_dht22():
    sensor.trigger()
    humidity = sensor.humidity()
    temperature = sensor.temperature()
    if humidity is not None and temperature is not None:
        return {'temperature': temperature, 'humidity': humidity}
    else:
        return {'error': 'Failed to retrieve data from humidity sensor'}
