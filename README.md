# IOT Project using STM32 NUCLEO-F411RE and Raspberry Pi

## Sensors and Actuators Used
- DHT22 Temperature and Humidity Sensor
- MQ3 Gas Sensor
- TCS3200 Color Sensor
- Active Buzzer

## Connection and Circuit Diagram
![image](https://github.com/user-attachments/assets/3aa6c1a3-b580-4211-87a9-c2094b5469eb)

## Variables and Methods for Used
- TCS3200 Color Sensor:
  - (uint8_t) `red_hex` [Red Hex value from 0-255]
  - (uint8_t) `green_hex` [Green Hex value from 0-255]
  - (uint8_t) `blue_hex` [Blue Hex value from 0-255]

- DHT22 Temperature and Humidity Sensor:
  - (float) `DHT_22.temp_C` [Temperature in Celcius]
  - (float) `DHT_22.temp_F` [Temperature in Farenheit]
  - (float) `DHT_22.humidity` [Relative Humidity in Percentage]

- MQ3 Alcohol Sensor
  - (uint16_t) `alcohol_level` [Alcohol reading from 0-4095]

- Active Buzzer
  - Turn On: ```HAL_GPIO_WritePin(GPIOC, GPIO_PIN_3, GPIO_PIN_RESET);```
  - Turn Off: ```HAL_GPIO_WritePin(GPIOC, GPIO_PIN_3, GPIO_PIN_SET);```
