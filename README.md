# IOT Project using STM32 NUCLEO-F411RE and Raspberry Pi

## Sensors and Actuators Used
- DHT22 Temperature and Humidity Sensor
- MQ3 Gas Sensor
- TCS3200 Color Sensor
- Active Buzzer

## Connection and Circuit Diagram
![image](https://github.com/user-attachments/assets/bfc55b73-6416-45ff-8c6e-e9e7af903a88)

## Interfacing with Sensors and Buzzer
### DHT22
The DHT22 communicates with a microcontroller through a custom protocol that uses a single wire/bus for communication (through the data line connection).
Communication Protocol:
1. MCU Pulls LOW to Initiate the communication
2. MCU Pulls HIGH and waits for the response
(Steps 1-2 is the MCU Initiating Read (Start Condition))
3. DHT responds by pulling LOW
4. DHT pulls HIGH to indicate 'get ready'
(Steps 3-4 is the DHT Responds (Acknowledge))
5. DHT sends 40 data bits


![image](https://github.com/user-attachments/assets/eef0379d-b3f6-45e3-8940-54fa34835d88)

The DHT22 sensor provides both temperature in Deg.C (T) and relative humidity(RH) readings. It sends this information in the following order: RH_Integral, RH_Decimal, T_Integral, T_Decimal. This is then followed by a checksum. (All data are MSB)


![image](https://github.com/user-attachments/assets/e9fb75c8-2cee-4072-9824-9c2671902ee4)


The source code used for interfacing with DHT22 in this project is from https://microcontrollerslab.com/dht22-stm32-blue-pill-stm32cubeide/ which provides 2 main functions: 
- ``DHT22_Start``: Initiate the communication protocol
- ``DHT22_Read``: Read the data sent by the DHT22

We then turn the implementation in main into another function called ``DHT22_Read_All``, which reads both humidity and temperature, storing them into a variable, and performs the checksum procedure.

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
