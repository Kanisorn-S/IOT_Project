import cv2 as cv
import os
from utils.model import predict_fruits

os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

import tensorflow as tf

model = tf.keras.models.load_model('./model/MyModel.keras')

def predict_from_cap(model, cap, path):
  ret, frame = cap.read()
  cv.imwrite(path, frame)
  fruit = predict_fruits(model, path) 
  return fruit

def predict_from_path(model, path):
  fruit = predict_fruits(model, path)
  return fruit


if __name__ == "__main__":
  
  cap = cv.VideoCapture(0)

  ret, frame = cap.read()

  cv.imwrite("./images/fruit.png", frame)

  cv.imshow("Cap", frame)
  cv.waitKey(1)

  fruits = predict_fruits(model, './images/fruit.png')
  print(fruits)