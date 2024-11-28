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
            return True
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return False

def capture_image():
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    image_path = f"./data/image_{timestamp}.jpg"
    os.system(f"libcamera-still -o {image_path} --vflip --hflip")
    print(f"Image saved to {image_path}")

if __name__ == "__main__":
    print("Press 'k' to capture an image.")
    while True:
        if is_key_pressed():
            capture_image()