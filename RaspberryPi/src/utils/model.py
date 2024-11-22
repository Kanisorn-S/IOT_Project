import cv2 as cv
import numpy as np
import os

os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

import tensorflow as tf


# Load and preprocess your image (example with an arbitrary image path)
def preprocess_image(image_path):
    image = tf.io.read_file(image_path)
    image = tf.image.decode_image(image, channels=3)
    image = tf.image.resize(image, [224, 224])  # Resize to match model's input shape
    image = image / 255.0  # Normalize to [0,1] if needed
    return tf.expand_dims(image, axis=0)  # Add batch dimension

def predict_fruits(model, image_path):
  
  fruits_vegs = [
    "Banana",
    "Apple",
    "Mango",
  ]
  fruits_vegs.sort()

  input_image = preprocess_image(image_path)
  predictions = model.predict(input_image)

  # Get the index of the class with the highest probability
  predicted_class = np.argmax(predictions, axis=-1)[0]
  return fruits_vegs[predicted_class]

if __name__ == "__main__":
   # Load the saved model
  model = tf.keras.models.load_model('./model/MyModel.keras')
  fruits_vegs = [
    "Banana",
    "Apple",
    "Pear",
    "Grapes",
    "Orange",
    "Kiwi",
    "Watermelon",
    "Pomegranate",
    "Pineapple",
    "Mango",
    "Cucumber",
    "Carrot",
    "Capsicum",
    "Onion",
    "Potato",
    "Lemon",
    "Tomato",
    "Radish",
    "Beetroot",
    "Cabbage",
    "Lettuce",
    "Spinach",
    "Soybean",
    "Cauliflower",
    "Bell Pepper",
    "Chili Pepper",
    "Turnip",
    "Corn",
    "Sweetcorn",
    "Sweet Potato",
    "Paprika",
    "Jalepeno",
    "Ginger",
    "Garlic",
    "Peas",
    "Eggplant",
  ]
  fruits_vegs.sort()

  # Example usage
  image_path = './images/test_apple.png'

  input_image = preprocess_image(image_path)
  predictions = model.predict(input_image)

  # Get the index of the class with the highest probability
  predicted_class = np.argmax(predictions, axis=-1)[0]

  print(f"Predicted class: {fruits_vegs[predicted_class]}")
