import os
import sys
import termios
import tty
import time

def is_key_pressed():
    if not sys.stdin.isatty():
        return False
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1).lower()
        if ch == 'a':
            return 'apple'
        elif ch == 'b':
            return 'banana'
        elif ch == 'm':
            return 'mango'
        elif ch == 'x':
            return 'x'
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return False

def capture_image(fruit):
    stop_preview()
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    image_path = f"./data/{fruit}/image_{timestamp}.jpg"
    os.system(f"libcamera-still -o {image_path} --vflip --hflip -t 1 --nopreview")
    print(f"Image saved to {image_path}")
    start_preview()

def start_preview():
    os.system("libcamera-hello --timeout 0 &")

def stop_preview():
    os.system("pkill libcamera-hello")

if __name__ == "__main__":
    start_preview()
    try:
        print("Press 'a' to capture an apple.")
        print("Press 'b' to capture an banana.")
        print("Press 'm' to capture an mango.")
        print("Press 'x' to exit the program.")
        while True:
            key = is_key_pressed()
            if key == 'x':
                print("Exiting program.")
                break
            else:
                capture_image(key)
    finally:
        stop_preview()
