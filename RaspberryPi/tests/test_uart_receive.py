import serial
import json

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

try:
    while True:
        incoming_string = uart.readline()
        print(incoming_string)
        if len(incoming_string):
            data = json.loads(incoming_string)
            print("Tempearature: ", data["temperature"])
            print("Humidity: ", data["humidity"])
            print("Status: ", data["status"])
    



except KeyboardInterrupt:
    print("Program terminated.")

finally:
    uart.close()
    print("UART connection closed.")

