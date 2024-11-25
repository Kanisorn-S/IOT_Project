import RPi.GPIO as GPIO
import time

DHT_PIN = 4  # GPIO pin where the DHT22 is connected

def read_dht22():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(DHT_PIN, GPIO.OUT)
    GPIO.output(DHT_PIN, GPIO.LOW)
    time.sleep(0.02)
    GPIO.output(DHT_PIN, GPIO.HIGH)
    GPIO.setup(DHT_PIN, GPIO.IN)

    data = []
    for i in range(500):
        data.append(GPIO.input(DHT_PIN))

    bit_count = 0
    tmp = 0
    count = 0
    humidity_bit = ""
    temperature_bit = ""
    crc = ""

    try:
        while data[count] == 1:
            count += 1

        for i in range(32):
            while data[count] == 0:
                count += 1
            while data[count] == 1:
                tmp += 1
                count += 1
            if tmp > 3:
                if bit_count < 16:
                    humidity_bit += "1"
                if bit_count >= 16 and bit_count < 32:
                    temperature_bit += "1"
            else:
                if bit_count < 16:
                    humidity_bit += "0"
                if bit_count >= 16 and bit_count < 32:
                    temperature_bit += "0"
            bit_count += 1
            tmp = 0

        for i in range(8):
            while data[count] == 0:
                count += 1
            while data[count] == 1:
                tmp += 1
                count += 1
            if tmp > 3:
                crc += "1"
            else:
                crc += "0"
            tmp = 0

        humidity = int(humidity_bit, 2) / 10.0
        temperature = int(temperature_bit, 2) / 10.0

        return {'temperature': temperature, 'humidity': humidity}
    except:
        return {'error': 'Failed to retrieve data from humidity sensor'}
    finally:
        GPIO.cleanup()
