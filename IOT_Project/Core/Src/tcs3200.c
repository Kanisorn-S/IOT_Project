/*
 * tcs3200.c
 *
 *  Created on: Sep 10, 2024
 *      Author: K0NQ
 */

#include <stdio.h>
#include <stdlib.h>
#include "tcs3200.h"


volatile uint32_t capture_val1 = 0, capture_val2 = 0;
volatile uint32_t frequency = 0;
volatile uint8_t capture_flag = 0;

void HAL_TIM_IC_CaptureCallback(TIM_HandleTypeDef *htim) {
  if (htim->Instance == TIM3 && htim->Channel == HAL_TIM_ACTIVE_CHANNEL_3) {
    if (capture_flag == 0) {
      // First capture
      capture_val1 = HAL_TIM_ReadCapturedValue(htim, TIM_CHANNEL_3);
      capture_flag = 1;
    } else if (capture_flag == 1) {
      // Second capture
      capture_val2 = HAL_TIM_ReadCapturedValue(htim, TIM_CHANNEL_3);

      // Calculate time difference
      if (capture_val2 > capture_val1) {
        frequency = 1000000 / (capture_val2 - capture_val1);
      } else {
        frequency = 1000000 / ((65535 - capture_val1) + capture_val2 + 1);
      }

      // Reset the flag
      capture_flag = 0;
    }
  }
}

void TCS3200_Freq_Scaling(uint8_t scaling) {
  switch (scaling) {
    case TCS3200_PWR_DOWN:
      HAL_GPIO_WritePin(GPIOB, GPIO_PIN_1, GPIO_PIN_RESET);
      HAL_GPIO_WritePin(GPIOB, GPIO_PIN_2, GPIO_PIN_RESET);
      break;
    case TCS3200_OFREQ_2P:
      HAL_GPIO_WritePin(GPIOB, GPIO_PIN_1, GPIO_PIN_RESET);
      HAL_GPIO_WritePin(GPIOB, GPIO_PIN_2, GPIO_PIN_SET);
      break;
    case TCS3200_OFREQ_20P:
      HAL_GPIO_WritePin(GPIOB, GPIO_PIN_1, GPIO_PIN_SET);
      HAL_GPIO_WritePin(GPIOB, GPIO_PIN_2, GPIO_PIN_RESET);
      break;
    case TCS3200_OFREQ_100P:
      HAL_GPIO_WritePin(GPIOB, GPIO_PIN_1, GPIO_PIN_SET);
      HAL_GPIO_WritePin(GPIOB, GPIO_PIN_2, GPIO_PIN_SET);
      break;
  }
}

void TCS3200_Select_Filter(uint8_t filter) {
  switch (filter) {
    case TCS3200_COLOR_RED:
      HAL_GPIO_WritePin(GPIOB, GPIO_PIN_4, GPIO_PIN_RESET);
      HAL_GPIO_WritePin(GPIOB, GPIO_PIN_5, GPIO_PIN_RESET);
      break;
    case TCS3200_COLOR_GREEN:
      HAL_GPIO_WritePin(GPIOB, GPIO_PIN_4, GPIO_PIN_SET);
      HAL_GPIO_WritePin(GPIOB, GPIO_PIN_5, GPIO_PIN_SET);
      break;
    case TCS3200_COLOR_BLUE:
      HAL_GPIO_WritePin(GPIOB, GPIO_PIN_4, GPIO_PIN_RESET);
      HAL_GPIO_WritePin(GPIOB, GPIO_PIN_5, GPIO_PIN_SET);
      break;
    case TCS3200_COLOR_CLEAR:
      HAL_GPIO_WritePin(GPIOB, GPIO_PIN_4, GPIO_PIN_SET);
      HAL_GPIO_WritePin(GPIOB, GPIO_PIN_5, GPIO_PIN_RESET);
      break;
  }
}

uint32_t TCS3200_ReadFrequency(uint8_t filter) {
  TCS3200_Select_Filter(filter);
  HAL_Delay(100);
  return frequency;
}

uint8_t MapFrequencyToHex(uint32_t freq, uint32_t min_freq, uint32_t max_freq) {
  if (freq < min_freq) {
    freq = min_freq;
  }
  if (freq > max_freq) {
    freq = max_freq;
  }

  return (uint8_t)(((freq - min_freq) * 255) / (max_freq - min_freq));
}
