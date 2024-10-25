import serial
from time import sleep
import keyboard

uart = serial.Serial(
        port='/dev/serial0',
        baudrate=115200,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        timeout=1
)

if uart.isOpen():
    print("UART connection established at 115200 baud.")
else:
    print("Failed to open UART connection.")
    exit(1)

try:
    print("Start typing. Press ESC to exit.")
    while True:

        if keyboard.is_pressed('esc'):
            print("Exiting...")
            break

        event = keyboard.read_event()
        if event.event_type == keyboard.KEY_DOWN:
            char = event.name
            if len(char) == 1:
                uart.write(char.encode('utf-8'))
                print(f'Sent: {char}')

except KeyboardInterrupt:
    print("Program terminated.")

finally:

    uart.close()
    print("UART connection closed.")

