import requests
import cv2 as cv
from time import sleep

cap = cv.VideoCapture(0)
while cap.isOpened():
  ret, frame = cap.read()
  if ret:
    break
cv.imshow("Captured", frame)
cv.imwrite("./images/test_img.jpg", frame)
cv.waitKey(1)
sleep(5)
cap.release()
cv.destroyAllWindows()


url = "https://notify-api.line.me/api/notify"
token = "Vt9BNQWixeFboNwXUInqDOBpHvDbRrWbJtskzA0ZPYm"
headers = {'Authorization':'Bearer '+token}

msg = {
  "message": (None, "We can do Line Notify"),
  "imageFile": open("C:/Users/K0NQ/Desktop/iot/IOT_Project/RaspberryPi/images/test_img.jpg", "r+b")
}

res = requests.post(url, headers=headers, files=msg)
print(res.text)