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
        ch = sys.stdin.read(1)
        if ch == 'k':
            return 'k'
        elif ch == 'x':
            return 'x'
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return False

def capture_image():
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    image_path = f"./data/image_{timestamp}.jpg"
    os.system(f"libcamera-still -o {image_path} --vflip --hflip -t 1 --nopreview")
    print(f"Image saved to {image_path}")

def start_preview():
    os.system("libcamera-hello --timeout 0 &")

def stop_preview():
    os.system("pkill libcamera-hello")

if __name__ == "__main__":
    start_preview()
    print("Press 'k' to capture an image.")
    print("Press 'x' to exit the program.")
    try:
        while True:
            key = is_key_pressed()
            if key == 'k':
                capture_image()
            elif key == 'x':
                print("Exiting program.")
                break
    finally:
        stop_preview()
