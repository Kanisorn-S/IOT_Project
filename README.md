# IOT Project using STM32 NUCLEO-F411RE and Raspberry Pi

## Sensors and Actuators Used
- DHT22 Temperature and Humidity Sensor
- MQ3 Gas Sensor
- TCS3200 Color Sensor
- CSI Camera
- IR Sensor
- Active Buzzer (Neither sensor nor actuator)

## Connection and Circuit Diagram
![image](https://github.com/user-attachments/assets/5d47f8a6-cf87-4219-b44f-9f1b35323d4d)


## Interfacing with Sensors and Buzzer

### DHT22

The DHT22 communicates with a microcontroller through a custom protocol that uses a single wire/bus for communication (through the data line connection).
Communication Protocol:
1. MCU Pulls LOW to Initiate the communication
2. MCU Pulls HIGH and waits for the response
(Steps 1-2 is the MCU Initiating Read (Start Condition))
3. DHT responds by pulling LOW
4. DHT pulls HIGH to indicate 'get ready'
(Steps 3-4 are the DHT Responds (Acknowledge))
5. DHT sends 40 data bits


![image](https://github.com/user-attachments/assets/eef0379d-b3f6-45e3-8940-54fa34835d88)

The DHT22 sensor provides both temperature in Deg.C (T) and relative humidity(RH) readings. It sends this information in the following order: RH_Integral, RH_Decimal, T_Integral, T_Decimal. A checksum then follows this. (All data are MSB)


![image](https://github.com/user-attachments/assets/e9fb75c8-2cee-4072-9824-9c2671902ee4)


We uses the ``Adafruit-CircuitPython-DHT`` library on the Raspberry Pi 4 in order to read the temperature and humidity from the DHT22.

The Library can be installed using ``pip install adafruit-circuitpython-dht``.

We can get the temperature and humidity by first creating a DHT22 object. Then, in a while loop, we can access the temperature and humidity through the DHT22 attributes with the corresponding name.

```python
import adafruit_dht
import board
from time import sleep

sensor = adafruit_dht.DHT22(board.D4)
while True:
  try:
    temp = sensor.temperature
    hum = sensor.humidity
  except RuntimeError as error:
    print(error.args[0])
    sleep(2)
    continue
  except Exception as error:
    sensor.exit()
    raise error
```

---

### TCS3200

The TCS3200 communicates with a microcontroller by sending a square wave signal with varying frequency based on the light intensity reflected off a surface onto the photodiodes. The TCS3200 has 4 filter options: Red, Blue, Green, and Clear. It also has 4 frequency intensity options: sleep, 2%, 20%, and 100%.

#### Frequency Scaling and Filtering
In the source file, tcs3200.c, we implemented two functions to handle frequency scaling and filtering: ``TCS3200_Freq_Scaling`` and ``TCS3200_Select_Filter``
These functions are implemented simply by writing HIGH or LOW to a specific digital pin connection in order to enable the desired setting. The HIGH and LOW combinations of the digital pins can be found in the datasheet of the TCS3200

![image](https://github.com/user-attachments/assets/e3135fc4-0c67-4373-85fe-8dfd756db2b4)

#### Reading the Frequency
After selecting the frequency and filter, we read the input through the connection with the OUT pin of the TCS3200 using timer interrupt input capture mode. We connect the OUT pin of the TCS3200 to PB0, which we set as TIM3_CH3. We then configured TIM3 Channel3 to be Input Capture direct mode with the following parameter:
- Prescaler: 84-1 (The APB clocks are set to 84 MHz, thus, this prescaler will give us a 1MHz counter)
- Counter Mode: Up
- Counter Period: 65536-1
- Auto Reload Preload: Enable

In tcs3200.c, we override the function ``HAL_TIM_IC_CaptureCallback`` to read the frequency of the square wave signal received then storing the frequency into a variable that can be used in the main program.

---

### MQ3

The MQ3 communicates with a microcontroller by sending an analog signal which varies based on the alcohol concentration in the surrounding air. We connect the Analog OUT pin of the MQ3 to PA0 to utilize the ADC1 IN1 to read and convert the analog value.

#### Connection and Interfacing
The MQ3 operates at a 5V logic level while the STM32 gpio pins operate at 3.3V logic level; therefore, we use a voltage divider comprising of a 1Kohm and a 2Kohm (2 1Kohm in series) to drop the voltage range from 0-5V down to 0-3.3V, making the MQ3 compatible with the STM32.

#### Reading the Analog Value
We used ADC1 IN0 on the STM32 in order to read the analog value sent from the MQ3. We used ``HAL_ADC_PollForConversion`` and ``HAL_ADC_GetValue`` within the main program to retrieve the value from the MQ3

---

### Buzzer

We use an active buzzer as our alert system. We connect the control pin (I/O) of the active buzzer to the PC3 pin on the STM32

#### Connection and Interfacing
We connect the buzzer to a 5V power source to get a loud and clear sound; however, a normal gpio output (in push-pull mode) of the STM32 operating on 3.3V logic is insufficient to drive the buzzer. Therefore, we must set the PC3 pin GPIO mode to Output Open Drain.

#### Controlling the Buzzer
The active buzzer we use is an active low buzzer; therefore, to turn the buzzer on we must write LOW to the control pin, and to turn it off we must write HIGH to the control pin. We achieved this simply by using ``HAL_GPIO_WritePin`` along with ``HAL_GPIO_TogglePin`` to implement 2 different alert.

#### Active vs Passive Buzzer
An active buzzer has a built-in oscillator while a passive buzzer doesn't. An active buzzer can produce sound with only a DC power supply, making it easier and simpler to implement. A passive buzzer, on the other hand, needs an AC signal in order to produce a sound, making it harder and more complex; however, it does have the capability of varying the pitch and tone of the sound being produced.

---

### IR Sensor

We use the IR Sensor to detect when the user places a fruit in the box. When the IR sensor detects the fruit within the box, the main program can begin.

We connected the IR sensor to the Raspberry Pi and implemented its functionality using the RPi.GPIO library, which can be installed using ``pip install RPi.GPIO``.

For the implementation, we first setup the GPIO pin to the correct mode. Then, within a while loop, we check the value of the GPIO pin that is connected to the OUT pin of the IR sensor. Since the IR sensor is active low, when the value of the GPIO pin is 0, we begin the main program.

```python
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
IR_PIN = 27
GPIO.setup(IR_PIN, GPIO.IN)

while True:
  if GPIO.input(IR_PIN) == 0:
    # Begin the main program
    ...
```
---
## Flash Memory

In order to improve the practicality and usability of the project, we utilize the flash memory of the STM32 board. Our project measures and detects fruit spoilage by comparing the current readings of alcohol level and several variables of colors to the initial value when the program first began. We can obviously keep the board plugged in all the time and have the program constantly running; however, this could be quite inefficient and hard to perform tests on. In order to combat this, we would store the initial readings of the values used in flash memory, then allow the user to begin the program in memory mode to retrieve those initial values from memory instead of re-recording the initial values.

### Flash Memory Architecture
Our STM32 Board comes with 512KB of memory, divided into 7 sectors. Our main program instructions would be stored in the early sectors; therefore, in order to ensure that we don't override our program when using flash memory, we would need to use one of the later sectors to store our values, in this case, we decided to use sector6, which begins at 0x08040000. The 4 values we are storing would be stored at 0x08040000, 0x08040010, 0x08040020, and 0x08040030 since it would be the most convenient when debugging through the memory browser.

![image](https://github.com/user-attachments/assets/9a43f592-a0f9-41cf-9b2c-7f8c970cf908)

### Reading and Writing Procedure
In order to enable reading and writing operations, we implemented 2 functions:
- ``write_to_flash``: This function would be called when the user starts the program in normal mode. The function will erase the memory in sector 6 and store new initial values in the sector.
- ``read_from_flash``: This function would be called when the user starts the program in memory mode. The function will retrieve the initial values stored at the memory addresses in sector 6.

### Functions Used to Interact with Flash Memory
- ``HAL_FLASH_Unlock``: Unlock flash memory
- ``HAL_FLASH_Program``: Store a value at a certain flash memory address
- ``HAL_FLASH_Lock``: Lock flash memory after finishing modification/read operations 

## User Button and External Interrupt

We used the built-in button on the STM32 board to allow the user to select between normal mode and memory mode. The on-board button is connected to the PC13 pin, which we set to GPIO_EXTI13. We then override the ``HAL_GPIO_EXTI_Callback`` in the main program to handle the user pressing the button.

The callback function is called when the user first press the button. As the first press is registered, we begin a delay using a for-loop 
``int i =0;
for (i=0; i<10000000; i++);``
We then recheck the status of the button to see if it is being held down or not. If the button is held, we begin the program in memory mode, else we begin the program in normal mode.


## Variables and Methods for Used
- TCS3200 Color Sensor:
  - (uint8_t) `red_hex` [Red Hex value from 0-255]
  - (uint8_t) `green_hex` [Green Hex value from 0-255]
  - (uint8_t) `blue_hex` [Blue Hex value from 0-255]

- DHT22 Temperature and Humidity Sensor:
  - (float) `sensor.temperature` [Temperature in Celcius]
  - (float) `sensor.humidity` [Relative Humidity in Percentage]

- MQ3 Alcohol Sensor
  - (uint16_t) `alcohol_level` [Alcohol reading from 0-4095]

- Active Buzzer
  - Turn On: ```HAL_GPIO_WritePin(GPIOC, GPIO_PIN_3, GPIO_PIN_RESET);```
  - Turn Off: ```HAL_GPIO_WritePin(GPIOC, GPIO_PIN_3, GPIO_PIN_SET);```
 

# Fruit Classification with Webcam using Tensorflow and Keras
This ML part implements a fruit classification system for three classes: Apple, Banana, and Mango, using TensorFlow Keras. It leverages image preprocessing, a Convolutional Neural Network (CNN), and visual evaluation tools for performance analysis.

## Step by Step Process
1. **Dataset Preprocessing**:
   - Images resized to `224x224x3`.
   - Normalized pixel values (0-1 range).
   - Augmented using `ImageDataGenerator` for better generalization.

2. **Model Architecture**:
   - Three convolutional layers with increasing filters (8, 16, 32).
   - Dropout regularization (35%) to reduce overfitting.
   - Fully connected layers with 256 and 128 neurons.
   - Output layer with 3 neurons using softmax activation.

3. **Training Pipeline**:
   - Data split: 75% training, 25% validation.
   - Augmentation: Rotation, zoom, and shifts applied dynamically.
   - Trained for 100 epochs using Adam optimizer and categorical crossentropy loss.
  
   
![image](https://github.com/user-attachments/assets/afd1cf0b-4847-449f-8e1b-9fb4bdb56eed)

---
## Visualization Method

### 1. Accuracy Graph

Tracks validation accuracy over epochs:
```python
plt.plot(history.history["val_accuracy"], color="r", label="Validation Accuracy")
plt.title("Accuracy Graph")
plt.xlabel("Number of Epochs")
plt.ylabel("Accuracy")
plt.legend()
plt.grid()
plt.show()
```
![acc_graph](https://github.com/user-attachments/assets/4294d723-4ec8-4429-88f3-bc381c8d558b)


### 2. Confusion Matrix
Shows classification performance for each class:
```python
from sklearn.metrics import confusion_matrix
sns.heatmap(confusion_matrix(y_true, y_pred_classes), annot=True, fmt=".0f", cmap="Blues")
```
![image](https://github.com/user-attachments/assets/58e3510c-f972-4125-ae6a-efddedd831b6)


---

## Results

- **Validation Accuracy**: Achieved high accuracy on validation data (specific value depends on the trained model in this case accuracy = 0.875).
- **Confusion Matrix**: Highlights correct and misclassified predictions across Apple, Banana, and Mango classes.

---

## Dependencies

- Python 3.7+
- TensorFlow/Keras
- NumPy
- OpenCV
- Matplotlib
- Seaborn
- Scikit-learn
  
---

## Instructions to Run

1. **Dataset Preparation**:
   - Ensure the dataset is structured with separate folders for training and testing data.
   - Classes: `Apple`, `Banana`, `Mango`.

2. **Train the Model**:
   - Run the training script provided to preprocess images, build the CNN model, and train it.

3. **Evaluate the Model**:
   - Generate accuracy graphs and confusion matrix plots to assess performance.

4. **Export for live-cam fruit detection**:
   - Use the `.h5` file from this model to implement **live-cam fruit detection** for real-time classification.

---

## References

- Dataset and code available on [Kaggle](https://www.kaggle.com/code/methasitboonpun/fruit-classification-that-worked-but-bad-data).
```
