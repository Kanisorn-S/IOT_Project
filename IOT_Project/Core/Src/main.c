/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file           : main.c
  * @brief          : Main program body
  ******************************************************************************
  * @attention
  *
  * Copyright (c) 2024 STMicroelectronics.
  * All rights reserved.
  *
  * This software is licensed under terms that can be found in the LICENSE file
  * in the root directory of this software component.
  * If no LICENSE file comes with this software, it is provided AS-IS.
  *
  ******************************************************************************
  */
/* USER CODE END Header */
/* Includes ------------------------------------------------------------------*/
#include "main.h"

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */
#include <stdio.h>
#include <stdbool.h>
#include <string.h>
#include <stdlib.h>
#include <math.h>
#include "dht22.h"
#include "active_buzzer.h"
#include "tcs3200.h"
/* USER CODE END Includes */

/* Private typedef -----------------------------------------------------------*/
/* USER CODE BEGIN PTD */

/* USER CODE END PTD */

/* Private define ------------------------------------------------------------*/
/* USER CODE BEGIN PD */
// Threshold for each fruit
// Apple
#define HUM_APPLE_MIN 90
#define HUM_APPLE_MAX 95
#define ALC_APPLE 102.604
#define L_APPLE 0.84
#define CC_APPLE 16.5
#define BI_APPLE 1.7


// Banana
#define HUM_BANANA_MIN 50
#define HUM_BANANA_MAX 95
#define ALC_BANANA 90
#define L_BANANA 0.7
#define CC_BANANA 5
#define BI_BANANA 2.5


// Mango
#define HUM_MANGO_MIN 90
#define HUM_MANGO_MAX 95
#define ALC_MANGO 67.29
#define L_MANGO 0.95
#define CC_MANGO 13.5
#define BI_MANGO 1.6


// Basic Threshold
#define TEMP_THRESHOLD 28

// DHT22
#define DHT22_PORT GPIOB
#define DHT22_PIN GPIO_PIN_14

// Active Buzzer
#define BUZZER_PORT GPIOC
#define BUZZER_PIN GPIO_PIN_3

// General Settings
#define CALIBRATION_TIME 5
#define STATUS_DEBOUNCE_TIME 5
#define FLASH_ADDRESS 0x08040000
#define FRUIT_ADDRESS 0x08060000

// Current Fruit
#define FRUIT "banana"
/* USER CODE END PD */

/* Private macro -------------------------------------------------------------*/
/* USER CODE BEGIN PM */

/* USER CODE END PM */

/* Private variables ---------------------------------------------------------*/
ADC_HandleTypeDef hadc1;

TIM_HandleTypeDef htim1;
TIM_HandleTypeDef htim3;

UART_HandleTypeDef huart1;
UART_HandleTypeDef huart2;

/* USER CODE BEGIN PV */
// DHT22
DHT22_t DHT_22;
char dht22_readings[50];
uint32_t pMillis, cMillis;
uint32_t *pPMillis = &pMillis;
uint32_t *pCMillis = &cMillis;

// MQ3
volatile uint16_t alcohol_level;
uint32_t alc_0;
char mq3_readings[50];

// TCS3200
char tcs3200_readings[50];
float hum_0;
char l_l0[100];

// Color Variables
float l_0 = 1;
float a_0 = 1;
float b_0 = 1;
float l, a, b;
float normalized_l;
float normalized_hue;
float color_change;
float normalized_browning_index;

// Diff variables
float hum_diff;
float alc_diff;
/* USER CODE END PV */

/* Private function prototypes -----------------------------------------------*/
void SystemClock_Config(void);
static void MX_GPIO_Init(void);
static void MX_USART2_UART_Init(void);
static void MX_TIM1_Init(void);
static void MX_ADC1_Init(void);
static void MX_TIM3_Init(void);
static void MX_USART1_UART_Init(void);
/* USER CODE BEGIN PFP */
void convert_colors(float R, float G, float B, float* l, float* a, float* b);
int check_fruit_condition(float temperature, float alc_level, float alc_threshold, float humidity, float hum_min, float hum_max, float l_value, float l_threshold, float bi_value, float bi_threshold, float cc_value, float cc_threshold);
void get_variables(float l_0, float a_0, float b_0, float l, float a, float b, float* normalized_l, float* normalized_hue, float* color_change, float* normalized_browning_index);
float convert_to_percentage_diff(float current_value, float initial_value);
void write_to_flash(uint32_t flash_address, uint32_t alc, float l, float cc,  float bi);
void read_from_flash(uint32_t flash_address, uint32_t* alc_0, float* l_0, float* cc_0, float* bi_0);
void write_fruit_to_flash(uint32_t flash_address, char fruit);
void read_fruit_from_flash(uint32_t flash_address, char* fruit);
/* USER CODE END PFP */

/* Private user code ---------------------------------------------------------*/
/* USER CODE BEGIN 0 */
bool stm_started = false;
bool started = false;
bool use_mem = false;
//
void HAL_GPIO_EXTI_Callback(uint16_t GPIO_Pin)
{
	int i = 0;
	for (i = 0; i < 10000000; i++);
	if (HAL_GPIO_ReadPin(GPIOC, GPIO_PIN_13) == 0) {
		char message[] = "Starting STM32 in memory mode...\r\n";
		HAL_UART_Transmit(&huart2, message, strlen(message), 1000);
		stm_started = true;
		use_mem = true;
	} else {
		char message[] = "Starting STM32 in normal mode...\r\n";
		HAL_UART_Transmit(&huart2, message, strlen(message), 1000);
		stm_started = true;
		use_mem = false;
	}
}
/* USER CODE END 0 */

/**
  * @brief  The application entry point.
  * @retval int
  */
int main(void)
{

  /* USER CODE BEGIN 1 */

  /* USER CODE END 1 */

  /* MCU Configuration--------------------------------------------------------*/

  /* Reset of all peripherals, Initializes the Flash interface and the Systick. */
  HAL_Init();

  /* USER CODE BEGIN Init */

  /* USER CODE END Init */

  /* Configure the system clock */
  SystemClock_Config();

  /* USER CODE BEGIN SysInit */

  /* USER CODE END SysInit */

  /* Initialize all configured peripherals */
  MX_GPIO_Init();
  MX_USART2_UART_Init();
  MX_TIM1_Init();
  MX_ADC1_Init();
  MX_TIM3_Init();
  MX_USART1_UART_Init();
  /* USER CODE BEGIN 2 */
  HAL_TIM_Base_Start(&htim1);
  TCS3200_Freq_Scaling(TCS3200_OFREQ_20P);
  Active_Buzzer buzzer = Active_Buzzer_Init(BUZZER_PORT, BUZZER_PIN);
  bool isBuzzerOn = false;
  bool is_first_loop = true;
  char buff[200];
  char json_msg[200];

  float min_hum, max_hum, max_alc, min_l, max_cc, max_bi;

  int i = 0;
  int j = 0;
  int status_debounce = 0;
  int prev_status = 0;
  char fruit;
  int index = 0;
  /* USER CODE END 2 */

  /* Infinite loop */
  /* USER CODE BEGIN WHILE */
  while (1)
  {
    // STM started
	  if(stm_started) {
      // Raspberry Pi started
      if (started) {
        // Main Program
        // Read Color from TCS3200
		  	uint32_t red_frequency = TCS3200_ReadFrequency(TCS3200_COLOR_RED);
		  	uint32_t green_frequency = TCS3200_ReadFrequency(TCS3200_COLOR_GREEN);
		  	uint32_t blue_frequency = TCS3200_ReadFrequency(TCS3200_COLOR_BLUE);

		  	uint8_t red_hex = MapFrequencyToHex(red_frequency, MIN_RED, MAX_RED);
		  	uint8_t green_hex = MapFrequencyToHex(green_frequency, MIN_GREEN, MAX_GREEN);
		  	uint8_t blue_hex = MapFrequencyToHex(blue_frequency, MIN_BLUE, MAX_BLUE);

		  	sprintf(tcs3200_readings, "Red: %d Green: %d Blue: %d\r\n", red_hex, green_hex, blue_hex);

        // Read Alcohol Level from MQ3
		  	HAL_ADC_Start(&hadc1);
		  	HAL_ADC_PollForConversion(&hadc1, 20);
		  	alcohol_level = HAL_ADC_GetValue(&hadc1);

        // Check for use memory mode
        // First time initialization
		    if (is_first_loop && !use_mem) {
		      convert_colors(red_hex, green_hex, blue_hex, &l_0, &a_0, &b_0);
		      sprintf(l_l0, "Calibrating...\r\n");
		      HAL_UART_Transmit(&huart2, l_l0, strlen(l_l0), 1000);
		      i = i + 1;
		      if (i > CALIBRATION_TIME){
			      is_first_loop = false;
			      alc_0 = alcohol_level;
			      write_to_flash(FLASH_ADDRESS, alc_0, l_0, a_0, b_0);
		      }
		    } else if (use_mem) { // Use memory mode
			    sprintf(l_l0, "Loading Variables from Memory...\r\n");
			    HAL_UART_Transmit(&huart2, l_l0, strlen(l_l0), 1000);
			    read_from_flash(FLASH_ADDRESS, &alc_0, &l_0, &a_0, &b_0);
			    j = j + 1;
			    if (j > CALIBRATION_TIME){
			      is_first_loop = false;
			      use_mem = false;
			    }
		    } else { // Done Initialization
		      float alc_diff = convert_to_percentage_diff(alcohol_level, alc_0);
		      convert_colors(red_hex, green_hex, blue_hex, &l, &a, &b);
		      get_variables(l_0, a_0, b_0, l, a, b, &normalized_l, &normalized_hue, &color_change, &normalized_browning_index);
		      sprintf(l_l0, "Normalized L*: %.2f\r\nNormalized Hue: %.2f\r\nColor Change: %.2f\r\nNormalized Browning Index: %.2f\r\n", normalized_l, normalized_hue, color_change, normalized_browning_index);
	  	  	sprintf(dht22_readings, "Temp(C): %.2f C Hum: %.2f \%\r\n", DHT_22.temp_C, DHT_22.humidity);
			  	sprintf(mq3_readings, "Alc: %.2f \%\r\n", alc_diff);
			  	sprintf(buff, "DHT22 Reading: %s\r\nMQ3 Reading: %s\r\nColor Variables: %s\r\n", dht22_readings, mq3_readings, l_l0);
			  	HAL_UART_Transmit(&huart2, buff, strlen(buff), 1000);

			  	int temp_status = check_fruit_condition(DHT_22.temp_C, alc_diff, max_alc, DHT_22.humidity, min_hum, max_hum, normalized_l, min_l, normalized_browning_index, max_bi, color_change, max_cc);
			  	char s[8];
			  	int status;
			  	if (HAL_UART_Receive(&huart1, s, 1, 1000) == HAL_OK) {
			  	  status = s[0] - '0';
			  	  char rasp_status[20];
			  	  sprintf(rasp_status, "status from rasp: %d", status);
			  	  HAL_UART_Transmit(&huart2, rasp_status, strlen(rasp_status), 1000);

			  	}

			  	if (status != prev_status) {
			  	  status_debounce = status_debounce + 1;
			  	} else {
			  	  status_debounce = 0;
			  	}
			  	if (status != prev_status && status_debounce > STATUS_DEBOUNCE_TIME) {
			  	  prev_status = status;
			  	  status_debounce = 0;
			  	}
			  	char status_msg[100];
			  	  if (prev_status == 1) {
			  	  	sprintf(status_msg, "\r\n-------------Potential Spoilage-----------\r\n");
			  	  	HAL_UART_Transmit(&huart2, status_msg, strlen(status_msg), 1000);
			  	  	HAL_GPIO_TogglePin(GPIOC, GPIO_PIN_3);
			  	  } else if (prev_status == 2) {
			  	  	sprintf(status_msg, "\r\n-------------Spoilage-----------\r\n");
			  	  	HAL_UART_Transmit(&huart2, status_msg, strlen(status_msg), 1000);
			  	  	HAL_GPIO_WritePin(GPIOC, GPIO_PIN_3, GPIO_PIN_RESET);
			  	  } else {
			  	  	HAL_GPIO_WritePin(GPIOC, GPIO_PIN_3, GPIO_PIN_SET);
			  	  }

			  	  sprintf(json_msg, "{\"red\": %d, \"green\": %d, \"blue\": %d, \"temp\": %.2f, \"hum\": %.2f, \"alc\": %.2f, \"status\": %d}\n", red_hex, green_hex, blue_hex, DHT_22.temp_C, DHT_22.humidity, alc_diff, prev_status);
			  	  HAL_UART_Transmit(&huart1, json_msg, strlen(buff), 1000);
        }
      } else {
    	  char message[] = "Waiting for Raspberry Pi to start...\r\n";
        HAL_UART_Transmit(&huart2, message, strlen(message), 1000);
        // Check for Raspberry Pi Start
        char t[8];
        if (HAL_UART_Receive(&huart1, t, 1, 1000) == HAL_OK) {
          // Fruit Detected 
          if (!started && t[0] == '1') {
            bool know_fruit = false;
            if (use_mem) {
              know_fruit = true;
            }
            // Wait for Raspberry Pi to send fruit
            while (!know_fruit) {
              if (HAL_UART_Receive(&huart1, t, 2, 1000) == HAL_OK) {
                if (t[0] == 'f') {
                  fruit = t[1];
                  char fruity[10];
                  sprintf(fruity, "fruit: %c", fruit);
                  HAL_UART_Transmit(&huart2, fruity, strlen(fruity), 1000);
                  know_fruit = true;
                  write_fruit_to_flash(FRUIT_ADDRESS, fruit);
                }
              }
            }
            read_fruit_from_flash(FRUIT_ADDRESS, &fruit);
            started = true;

            // Set thresholds based on the fruit
            if (fruit == '0') {
              char message[] = "Fruit is Apple!\r\n";
              HAL_UART_Transmit(&huart2, message, strlen(message), 1000);
              min_hum = HUM_APPLE_MIN;
              max_hum = HUM_APPLE_MAX;
              max_alc = ALC_APPLE;
              min_l = L_APPLE;
              max_cc = CC_APPLE;
              max_bi = BI_APPLE;
            } else if (fruit == '1') {
              char message[] = "Fruit is Banana!\r\n";
              HAL_UART_Transmit(&huart2, message, strlen(message), 1000);
              min_hum = HUM_BANANA_MIN;
              max_hum = HUM_BANANA_MAX;
              max_alc = ALC_BANANA;
              min_l = L_BANANA;
              max_cc = CC_BANANA;
              max_bi = BI_BANANA;
            } else if (fruit == '2') {
              char message[] = "Fruit is Mango!\r\n";
              HAL_UART_Transmit(&huart2, message, strlen(message), 1000);
              min_hum = HUM_MANGO_MIN;
              max_hum = HUM_MANGO_MAX;
              max_alc = ALC_MANGO;
              min_l = L_MANGO;
              max_cc = CC_MANGO;
              max_bi = BI_MANGO;
            }
          }
        }
      }


	  } else {
		  char message[] = "Waiting for STM32 to start...\r\n";
		  HAL_UART_Transmit(&huart2, message, strlen(message), 1000);
	  }

	  HAL_Delay(1000);
    /* USER CODE END WHILE */

    /* USER CODE BEGIN 3 */
  }
  /* USER CODE END 3 */
}

/**
  * @brief System Clock Configuration
  * @retval None
  */
void SystemClock_Config(void)
{
  RCC_OscInitTypeDef RCC_OscInitStruct = {0};
  RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};

  /** Configure the main internal regulator output voltage
  */
  __HAL_RCC_PWR_CLK_ENABLE();
  __HAL_PWR_VOLTAGESCALING_CONFIG(PWR_REGULATOR_VOLTAGE_SCALE1);

  /** Initializes the RCC Oscillators according to the specified parameters
  * in the RCC_OscInitTypeDef structure.
  */
  RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSI;
  RCC_OscInitStruct.HSIState = RCC_HSI_ON;
  RCC_OscInitStruct.HSICalibrationValue = RCC_HSICALIBRATION_DEFAULT;
  RCC_OscInitStruct.PLL.PLLState = RCC_PLL_ON;
  RCC_OscInitStruct.PLL.PLLSource = RCC_PLLSOURCE_HSI;
  RCC_OscInitStruct.PLL.PLLM = 16;
  RCC_OscInitStruct.PLL.PLLN = 336;
  RCC_OscInitStruct.PLL.PLLP = RCC_PLLP_DIV4;
  RCC_OscInitStruct.PLL.PLLQ = 4;
  if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK)
  {
    Error_Handler();
  }

  /** Initializes the CPU, AHB and APB buses clocks
  */
  RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK|RCC_CLOCKTYPE_SYSCLK
                              |RCC_CLOCKTYPE_PCLK1|RCC_CLOCKTYPE_PCLK2;
  RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
  RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
  RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV2;
  RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV1;

  if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_2) != HAL_OK)
  {
    Error_Handler();
  }
}

/**
  * @brief ADC1 Initialization Function
  * @param None
  * @retval None
  */
static void MX_ADC1_Init(void)
{

  /* USER CODE BEGIN ADC1_Init 0 */

  /* USER CODE END ADC1_Init 0 */

  ADC_ChannelConfTypeDef sConfig = {0};

  /* USER CODE BEGIN ADC1_Init 1 */

  /* USER CODE END ADC1_Init 1 */

  /** Configure the global features of the ADC (Clock, Resolution, Data Alignment and number of conversion)
  */
  hadc1.Instance = ADC1;
  hadc1.Init.ClockPrescaler = ADC_CLOCK_SYNC_PCLK_DIV4;
  hadc1.Init.Resolution = ADC_RESOLUTION_12B;
  hadc1.Init.ScanConvMode = DISABLE;
  hadc1.Init.ContinuousConvMode = DISABLE;
  hadc1.Init.DiscontinuousConvMode = DISABLE;
  hadc1.Init.ExternalTrigConvEdge = ADC_EXTERNALTRIGCONVEDGE_NONE;
  hadc1.Init.ExternalTrigConv = ADC_SOFTWARE_START;
  hadc1.Init.DataAlign = ADC_DATAALIGN_RIGHT;
  hadc1.Init.NbrOfConversion = 1;
  hadc1.Init.DMAContinuousRequests = DISABLE;
  hadc1.Init.EOCSelection = ADC_EOC_SINGLE_CONV;
  if (HAL_ADC_Init(&hadc1) != HAL_OK)
  {
    Error_Handler();
  }

  /** Configure for the selected ADC regular channel its corresponding rank in the sequencer and its sample time.
  */
  sConfig.Channel = ADC_CHANNEL_0;
  sConfig.Rank = 1;
  sConfig.SamplingTime = ADC_SAMPLETIME_3CYCLES;
  if (HAL_ADC_ConfigChannel(&hadc1, &sConfig) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN ADC1_Init 2 */

  /* USER CODE END ADC1_Init 2 */

}

/**
  * @brief TIM1 Initialization Function
  * @param None
  * @retval None
  */
static void MX_TIM1_Init(void)
{

  /* USER CODE BEGIN TIM1_Init 0 */

  /* USER CODE END TIM1_Init 0 */

  TIM_ClockConfigTypeDef sClockSourceConfig = {0};
  TIM_MasterConfigTypeDef sMasterConfig = {0};

  /* USER CODE BEGIN TIM1_Init 1 */

  /* USER CODE END TIM1_Init 1 */
  htim1.Instance = TIM1;
  htim1.Init.Prescaler = 84-1;
  htim1.Init.CounterMode = TIM_COUNTERMODE_UP;
  htim1.Init.Period = 65535;
  htim1.Init.ClockDivision = TIM_CLOCKDIVISION_DIV1;
  htim1.Init.RepetitionCounter = 0;
  htim1.Init.AutoReloadPreload = TIM_AUTORELOAD_PRELOAD_DISABLE;
  if (HAL_TIM_Base_Init(&htim1) != HAL_OK)
  {
    Error_Handler();
  }
  sClockSourceConfig.ClockSource = TIM_CLOCKSOURCE_INTERNAL;
  if (HAL_TIM_ConfigClockSource(&htim1, &sClockSourceConfig) != HAL_OK)
  {
    Error_Handler();
  }
  sMasterConfig.MasterOutputTrigger = TIM_TRGO_RESET;
  sMasterConfig.MasterSlaveMode = TIM_MASTERSLAVEMODE_DISABLE;
  if (HAL_TIMEx_MasterConfigSynchronization(&htim1, &sMasterConfig) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN TIM1_Init 2 */

  /* USER CODE END TIM1_Init 2 */

}

/**
  * @brief TIM3 Initialization Function
  * @param None
  * @retval None
  */
static void MX_TIM3_Init(void)
{

  /* USER CODE BEGIN TIM3_Init 0 */

  /* USER CODE END TIM3_Init 0 */

  TIM_ClockConfigTypeDef sClockSourceConfig = {0};
  TIM_MasterConfigTypeDef sMasterConfig = {0};
  TIM_IC_InitTypeDef sConfigIC = {0};

  /* USER CODE BEGIN TIM3_Init 1 */

  /* USER CODE END TIM3_Init 1 */
  htim3.Instance = TIM3;
  htim3.Init.Prescaler = 84-1;
  htim3.Init.CounterMode = TIM_COUNTERMODE_UP;
  htim3.Init.Period = 65536-1;
  htim3.Init.ClockDivision = TIM_CLOCKDIVISION_DIV1;
  htim3.Init.AutoReloadPreload = TIM_AUTORELOAD_PRELOAD_ENABLE;
  if (HAL_TIM_Base_Init(&htim3) != HAL_OK)
  {
    Error_Handler();
  }
  sClockSourceConfig.ClockSource = TIM_CLOCKSOURCE_INTERNAL;
  if (HAL_TIM_ConfigClockSource(&htim3, &sClockSourceConfig) != HAL_OK)
  {
    Error_Handler();
  }
  if (HAL_TIM_IC_Init(&htim3) != HAL_OK)
  {
    Error_Handler();
  }
  sMasterConfig.MasterOutputTrigger = TIM_TRGO_RESET;
  sMasterConfig.MasterSlaveMode = TIM_MASTERSLAVEMODE_DISABLE;
  if (HAL_TIMEx_MasterConfigSynchronization(&htim3, &sMasterConfig) != HAL_OK)
  {
    Error_Handler();
  }
  sConfigIC.ICPolarity = TIM_INPUTCHANNELPOLARITY_RISING;
  sConfigIC.ICSelection = TIM_ICSELECTION_DIRECTTI;
  sConfigIC.ICPrescaler = TIM_ICPSC_DIV1;
  sConfigIC.ICFilter = 0;
  if (HAL_TIM_IC_ConfigChannel(&htim3, &sConfigIC, TIM_CHANNEL_3) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN TIM3_Init 2 */
  HAL_NVIC_SetPriority(TIM3_IRQn, 0, 0);
  HAL_NVIC_EnableIRQ(TIM3_IRQn);

  HAL_TIM_IC_Start_IT(&htim3, TIM_CHANNEL_3);
  /* USER CODE END TIM3_Init 2 */

}

/**
  * @brief USART1 Initialization Function
  * @param None
  * @retval None
  */
static void MX_USART1_UART_Init(void)
{

  /* USER CODE BEGIN USART1_Init 0 */

  /* USER CODE END USART1_Init 0 */

  /* USER CODE BEGIN USART1_Init 1 */

  /* USER CODE END USART1_Init 1 */
  huart1.Instance = USART1;
  huart1.Init.BaudRate = 115200;
  huart1.Init.WordLength = UART_WORDLENGTH_8B;
  huart1.Init.StopBits = UART_STOPBITS_1;
  huart1.Init.Parity = UART_PARITY_NONE;
  huart1.Init.Mode = UART_MODE_TX_RX;
  huart1.Init.HwFlowCtl = UART_HWCONTROL_NONE;
  huart1.Init.OverSampling = UART_OVERSAMPLING_16;
  if (HAL_UART_Init(&huart1) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN USART1_Init 2 */

  /* USER CODE END USART1_Init 2 */

}

/**
  * @brief USART2 Initialization Function
  * @param None
  * @retval None
  */
static void MX_USART2_UART_Init(void)
{

  /* USER CODE BEGIN USART2_Init 0 */

  /* USER CODE END USART2_Init 0 */

  /* USER CODE BEGIN USART2_Init 1 */

  /* USER CODE END USART2_Init 1 */
  huart2.Instance = USART2;
  huart2.Init.BaudRate = 115200;
  huart2.Init.WordLength = UART_WORDLENGTH_8B;
  huart2.Init.StopBits = UART_STOPBITS_1;
  huart2.Init.Parity = UART_PARITY_NONE;
  huart2.Init.Mode = UART_MODE_TX_RX;
  huart2.Init.HwFlowCtl = UART_HWCONTROL_NONE;
  huart2.Init.OverSampling = UART_OVERSAMPLING_16;
  if (HAL_UART_Init(&huart2) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN USART2_Init 2 */

  /* USER CODE END USART2_Init 2 */

}

/**
  * @brief GPIO Initialization Function
  * @param None
  * @retval None
  */
static void MX_GPIO_Init(void)
{
  GPIO_InitTypeDef GPIO_InitStruct = {0};
/* USER CODE BEGIN MX_GPIO_Init_1 */
/* USER CODE END MX_GPIO_Init_1 */

  /* GPIO Ports Clock Enable */
  __HAL_RCC_GPIOC_CLK_ENABLE();
  __HAL_RCC_GPIOH_CLK_ENABLE();
  __HAL_RCC_GPIOA_CLK_ENABLE();
  __HAL_RCC_GPIOB_CLK_ENABLE();

  /*Configure GPIO pin Output Level */
  HAL_GPIO_WritePin(GPIOC, GPIO_PIN_3, GPIO_PIN_RESET);

  /*Configure GPIO pin Output Level */
  HAL_GPIO_WritePin(LD2_GPIO_Port, LD2_Pin, GPIO_PIN_RESET);

  /*Configure GPIO pin Output Level */
  HAL_GPIO_WritePin(GPIOB, GPIO_PIN_1|GPIO_PIN_2|GPIO_PIN_14|GPIO_PIN_4
                          |GPIO_PIN_5, GPIO_PIN_RESET);

  /*Configure GPIO pin : PC13 */
  GPIO_InitStruct.Pin = GPIO_PIN_13;
  GPIO_InitStruct.Mode = GPIO_MODE_IT_FALLING;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  HAL_GPIO_Init(GPIOC, &GPIO_InitStruct);

  /*Configure GPIO pin : PC3 */
  GPIO_InitStruct.Pin = GPIO_PIN_3;
  GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_OD;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
  HAL_GPIO_Init(GPIOC, &GPIO_InitStruct);

  /*Configure GPIO pin : LD2_Pin */
  GPIO_InitStruct.Pin = LD2_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
  HAL_GPIO_Init(LD2_GPIO_Port, &GPIO_InitStruct);

  /*Configure GPIO pins : PB1 PB2 PB14 PB4
                           PB5 */
  GPIO_InitStruct.Pin = GPIO_PIN_1|GPIO_PIN_2|GPIO_PIN_14|GPIO_PIN_4
                          |GPIO_PIN_5;
  GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
  HAL_GPIO_Init(GPIOB, &GPIO_InitStruct);

  /* EXTI interrupt init*/
  HAL_NVIC_SetPriority(EXTI15_10_IRQn, 0, 0);
  HAL_NVIC_EnableIRQ(EXTI15_10_IRQn);

/* USER CODE BEGIN MX_GPIO_Init_2 */
/* USER CODE END MX_GPIO_Init_2 */
}

/* USER CODE BEGIN 4 */
// using https://web.archive.org/web/20111111080001/http://www.easyrgb.com/index.php?X=MATH&H=01#tex1
void convert_colors(float R, float G, float B, float* l, float* a, float* b)
{
    float var_R = R/255.0;
    float var_G = G/255.0;
    float var_B = B/255.0;


    if ( var_R > 0.04045 ) var_R = pow( (( var_R + 0.055 ) / 1.055 ), 2.4 );
    else                   var_R = var_R / 12.92;
    if ( var_G > 0.04045 ) var_G = pow( ( ( var_G + 0.055 ) / 1.055 ), 2.4);
    else                   var_G = var_G / 12.92;
    if ( var_B > 0.04045 ) var_B = pow( ( ( var_B + 0.055 ) / 1.055 ), 2.4);
    else                   var_B = var_B / 12.92;

    var_R = var_R * 100.;
    var_G = var_G * 100.;
    var_B = var_B * 100.;

    //Observer. = 2°, Illuminant = D65
    float X = var_R * 0.4124 + var_G * 0.3576 + var_B * 0.1805;
    float Y = var_R * 0.2126 + var_G * 0.7152 + var_B * 0.0722;
    float Z = var_R * 0.0193 + var_G * 0.1192 + var_B * 0.9505;


    float var_X = X / 95.047 ;         //ref_X =  95.047   Observer= 2°, Illuminant= D65
    float var_Y = Y / 100.000;          //ref_Y = 100.000
    float var_Z = Z / 108.883;          //ref_Z = 108.883

    if ( var_X > 0.008856 ) var_X = pow(var_X , ( 1./3. ) );
    else                    var_X = ( 7.787 * var_X ) + ( 16. / 116. );
    if ( var_Y > 0.008856 ) var_Y = pow(var_Y , ( 1./3. ));
    else                    var_Y = ( 7.787 * var_Y ) + ( 16. / 116. );
    if ( var_Z > 0.008856 ) var_Z = pow(var_Z , ( 1./3. ));
    else                    var_Z = ( 7.787 * var_Z ) + ( 16. / 116. );

    float l_s = ( 116. * var_Y ) - 16.;
    float a_s = 500. * ( var_X - var_Y );
    float b_s = 200. * ( var_Y - var_Z );

    *l = l_s;
    *a = a_s;
    *b = b_s;
}

void get_variables(float l_0, float a_0, float b_0, float l, float a, float b, float* normalized_l, float* normalized_hue, float* color_change, float* normalized_browning_index)
{
	float h_0 = sqrt(pow(a_0, 2) + pow(b_0, 2));
	float h = sqrt(pow(a, 2) + pow(b, 2));
	float x_0 = (a_0 + 1.75 * l_0) / (5.645 * l_0 + a_0 - 3.012 * b_0);
	float x = (a + 1.75 * l) / (5.645 * l + a - 3.012 * b);
	float bi_0 = (100 * (x_0 - 0.31)) / 0.17;
	float bi = (100 * (x - 0.31)) / 0.17;
	float delta_e = sqrt(pow((l - l_0), 2) + pow((a - a_0), 2) + pow((b - b_0), 2));

	*normalized_l = l / l_0;
	*normalized_hue = h / h_0;
	*color_change = delta_e;
	*normalized_browning_index = bi / bi_0;

}

int check_fruit_condition(float temperature, float alc_level, float alc_threshold, float humidity, float min_hum, float max_hum, float l_value, float l_threshold, float bi_value, float bi_threshold, float cc_value, float cc_threshold)
{
	if ((l_value < l_threshold) || (bi_value > bi_threshold) || (cc_value > cc_threshold)) {
				return 2;
	}
//	if (temperature > TEMP_THRESHOLD) {
//		return 1;
//	}
//
//	if ((humidity < min_hum || humidity > max_hum)) {
//			return 1;
//	}


	return 0;
}
float convert_to_percentage_diff(float current_value, float initial_value)
{
	return (100 * (current_value - initial_value)) / initial_value;
}

void write_fruit_to_flash(uint32_t flash_address, char fruit)
{
  HAL_FLASH_Unlock();
  FLASH_Erase_Sector(7, FLASH_VOLTAGE_RANGE_3);
  HAL_FLASH_Lock();
  HAL_FLASH_Unlock();
  HAL_FLASH_Program(FLASH_TYPEPROGRAM_WORD, flash_address, fruit);
  HAL_FLASH_Lock();
}

void read_fruit_from_flash(uint32_t flash_address, char* fruit)
{
  HAL_FLASH_Unlock();
  *fruit = *(__IO uint32_t*)flash_address;
  HAL_FLASH_Lock();
}

void write_to_flash(uint32_t flash_address, uint32_t alc, float l, float a, float b)
{
	HAL_FLASH_Unlock();
	FLASH_Erase_Sector(6, FLASH_VOLTAGE_RANGE_3);
	HAL_FLASH_Lock();
	HAL_FLASH_Unlock();
	float data[4] = {alc, l, a, b};
	for (int i = 0; i<=3; i++) {
		if (i == 0) {
			HAL_FLASH_Program(FLASH_TYPEPROGRAM_WORD, flash_address, data[i]);
		} else {
			HAL_FLASH_Program(FLASH_TYPEPROGRAM_WORD, flash_address, *(uint32_t *)&(data[i]));
		}

		flash_address+=16;
	}
	HAL_FLASH_Lock();
}

void read_from_flash(uint32_t flash_address, uint32_t* alc_0, float* l_0, float* a_0, float* b_0)
{
	HAL_FLASH_Unlock();
	float read_data[4];
	for (int i = 0; i <=3; i++) {
		if (i == 0) {
			read_data[i] = *(__IO uint32_t*)flash_address;
		} else {
			read_data[i] = *(float *)flash_address;
		}
		flash_address+=16;
	}
	*alc_0 = read_data[0];
	*l_0 = read_data[1];
	*a_0 = read_data[2];
	*b_0 = read_data[3];
	HAL_FLASH_Lock();
}
/* USER CODE END 4 */

/**
  * @brief  Period elapsed callback in non blocking mode
  * @note   This function is called  when TIM2 interrupt took place, inside
  * HAL_TIM_IRQHandler(). It makes a direct call to HAL_IncTick() to increment
  * a global variable "uwTick" used as application time base.
  * @param  htim : TIM handle
  * @retval None
  */
void HAL_TIM_PeriodElapsedCallback(TIM_HandleTypeDef *htim)
{
  /* USER CODE BEGIN Callback 0 */

  /* USER CODE END Callback 0 */
  if (htim->Instance == TIM2) {
    HAL_IncTick();
  }
  /* USER CODE BEGIN Callback 1 */

  /* USER CODE END Callback 1 */
}

/**
  * @brief  This function is executed in case of error occurrence.
  * @retval None
  */
void Error_Handler(void)
{
  /* USER CODE BEGIN Error_Handler_Debug */
  /* User can add his own implementation to report the HAL error return state */
  __disable_irq();
  while (1)
  {
  }
  /* USER CODE END Error_Handler_Debug */
}

#ifdef  USE_FULL_ASSERT
/**
  * @brief  Reports the name of the source file and the source line number
  *         where the assert_param error has occurred.
  * @param  file: pointer to the source file name
  * @param  line: assert_param error line source number
  * @retval None
  */
void assert_failed(uint8_t *file, uint32_t line)
{
  /* USER CODE BEGIN 6 */
  /* User can add his own implementation to report the file name and line number,
     ex: printf("Wrong parameters value: file %s on line %d\r\n", file, line) */
  /* USER CODE END 6 */
}
#endif /* USE_FULL_ASSERT */
