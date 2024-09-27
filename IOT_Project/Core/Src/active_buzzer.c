/*
 * active_buzzer.c
 *
 *  Created on: Sep 12, 2024
 *      Author: K0NQ
 */


#include "active_buzzer.h"
#include "main.h"
#include <stdio.h>


Active_Buzzer Active_Buzzer_Init(GPIO_TypeDef* GPIOx, uint16_t GPIO_Pin)
{
  // Create New Active_Buzzer struct
  Active_Buzzer buzzer;
  buzzer.GPIOx = GPIOx;
  buzzer.GPIO_Pin = GPIO_Pin;

  // Set Default to HIGH
  HAL_GPIO_WritePin(GPIOx, GPIO_Pin, GPIO_PIN_SET);

  // Initialize GPIO port
  GPIO_InitTypeDef GPIO_InitStruct = {0};
  GPIO_InitStruct.Pin = GPIO_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_OD;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
  HAL_GPIO_Init(GPIOx, &GPIO_InitStruct);

  return buzzer;
}

void Active_Buzzer_On(Active_Buzzer buzzer)
{
  HAL_GPIO_WritePin(buzzer.GPIOx, buzzer.GPIO_Pin, GPIO_PIN_RESET);
}

void Active_Buzzer_Off(Active_Buzzer buzzer)
{
  HAL_GPIO_WritePin(buzzer.GPIOx, buzzer.GPIO_Pin, GPIO_PIN_SET);
}

void Active_Buzzer_Toggle(Active_Buzzer buzzer)
{
  HAL_GPIO_TogglePin(buzzer.GPIOx, buzzer.GPIO_Pin);
}

void Active_Buzzer_Timed(Active_Buzzer buzzer, uint32_t duration)
{
  Active_Buzzer_On(buzzer);
  HAL_Delay(duration);
  Active_Buzzer_Off(buzzer);
}
