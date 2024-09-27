/*
 * dht22.c
 *
 *  Created on: Sep 7, 2024
 *      Author: K0NQ
 */

#include <stdio.h>
#include <stdlib.h>
#include "dht22.h"


void microDelay (TIM_HandleTypeDef *htim, uint16_t delay)
{
  __HAL_TIM_SET_COUNTER(htim, 0);
  while (__HAL_TIM_GET_COUNTER(htim) < delay);
}

uint8_t DHT22_Start (GPIO_TypeDef* DHT22_PORT, uint16_t DHT22_PIN, TIM_HandleTypeDef *htim, uint32_t *pMillis, uint32_t *cMillis)
{
  uint8_t Response = 0;
  uint32_t pM, cM;
  GPIO_InitTypeDef GPIO_InitStructPrivate = {0};
  GPIO_InitStructPrivate.Pin = GPIO_PIN_14;
  GPIO_InitStructPrivate.Mode = GPIO_MODE_OUTPUT_PP;
  GPIO_InitStructPrivate.Speed = GPIO_SPEED_FREQ_LOW;
  GPIO_InitStructPrivate.Pull = GPIO_NOPULL;
  HAL_GPIO_Init(DHT22_PORT, &GPIO_InitStructPrivate);
  HAL_GPIO_WritePin (DHT22_PORT, DHT22_PIN, 0);
  microDelay (htim, 1300);
  HAL_GPIO_WritePin (GPIOB, GPIO_PIN_14, 1);
  microDelay (htim, 30);
  GPIO_InitStructPrivate.Mode = GPIO_MODE_INPUT;
  GPIO_InitStructPrivate.Pull = GPIO_PULLUP;
  HAL_GPIO_Init(DHT22_PORT, &GPIO_InitStructPrivate);
  microDelay (htim, 40);
  if (!(HAL_GPIO_ReadPin (DHT22_PORT, DHT22_PIN)))
  {
    microDelay (htim, 80);
    if ((HAL_GPIO_ReadPin (DHT22_PORT, DHT22_PIN))) Response = 1;
  }
  pM = HAL_GetTick();
  cM = HAL_GetTick();
  while ((HAL_GPIO_ReadPin (DHT22_PORT, DHT22_PIN)) && pM + 2 > cM)
  {
    cM = HAL_GetTick();
  }
  return Response;
}

uint8_t DHT22_Read (GPIO_TypeDef* DHT22_PORT, uint16_t DHT22_PIN, TIM_HandleTypeDef *htim, uint32_t *pMillis, uint32_t *cMillis)
{
  uint8_t x,y;
  uint32_t pM, cM;
  for (x=0;x<8;x++)
  {
    pM = HAL_GetTick();
    cM = HAL_GetTick();
    while (!(HAL_GPIO_ReadPin (DHT22_PORT, DHT22_PIN)) && pM + 2 > cM)
    {
      cM = HAL_GetTick();
    }
    microDelay (htim, 40);
    if (!(HAL_GPIO_ReadPin (DHT22_PORT, DHT22_PIN)))   // if the pin is low
      y&= ~(1<<(7-x));
    else
      y|= (1<<(7-x));
    pM = HAL_GetTick();
    cM = HAL_GetTick();
    while ((HAL_GPIO_ReadPin (DHT22_PORT, DHT22_PIN)) && pM + 2 > cM)
    {  // wait for the pin to go low
      cM = HAL_GetTick();
    }
  }
  return y;
}

void DHT22_Read_All(DHT22_t *DataStruct, UART_HandleTypeDef *huart, GPIO_TypeDef* DHT22_PORT, uint16_t DHT22_PIN, TIM_HandleTypeDef *htim, uint32_t *pMillis, uint32_t *cMillis)
{
  uint8_t hum1, hum2, tempC1, tempC2, SUM, CHECK;
  float temp_Celsius =0;
  float temp_Fahrenheit = 0;
  float Humidity = 0;
  uint8_t hum_integral, hum_decimal, tempC_integral, tempC_decimal, tempF_integral, tempF_decimal;
  char string[15];
  hum1 = DHT22_Read(DHT22_PORT, DHT22_PIN, htim, *pMillis, *cMillis);
  hum2 = DHT22_Read(DHT22_PORT, DHT22_PIN, htim, *pMillis, *cMillis);
  tempC1 = DHT22_Read(DHT22_PORT, DHT22_PIN, htim, *pMillis, *cMillis);
  tempC2 = DHT22_Read(DHT22_PORT, DHT22_PIN, htim, *pMillis, *cMillis);
  SUM = DHT22_Read(DHT22_PORT, DHT22_PIN, htim, *pMillis, *cMillis);
  CHECK = hum1 + hum2 + tempC1 + tempC2;
  if (CHECK == SUM)
  {
    if (tempC1>127)
    {
      temp_Celsius = (float)tempC2/10*(-1);
    }
    else
    {
      temp_Celsius = (float)((tempC1<<8)|tempC2)/10;
    }

    temp_Fahrenheit = temp_Celsius * 9/5 + 32;

    Humidity = (float) ((hum1<<8)|hum2)/10;

    hum_integral = Humidity;
    hum_decimal = Humidity*10-hum_integral*10;
    sprintf(string,"%d.%d", hum_integral, hum_decimal);
    DataStruct->humidity = strtof(string, NULL);

    if (temp_Celsius < 0)
    {
      tempC_integral = temp_Celsius *(-1);
      tempC_decimal = temp_Celsius*(-10)-tempC_integral*10;
      sprintf(string,"-%d.%d", tempC_integral, tempC_decimal);
      DataStruct->temp_C = strtof(string, NULL);
    }
    else
    {
      tempC_integral = temp_Celsius;
      tempC_decimal = temp_Celsius*10-tempC_integral*10;
      sprintf(string,"%d.%d", tempC_integral, tempC_decimal);
      DataStruct->temp_C = strtof(string, NULL);
    }
    // HAL_UART_Transmit(huart, string, 15, 1000);

    if(temp_Fahrenheit < 0)
    {
      tempF_integral = temp_Fahrenheit*(-1);
      tempF_decimal = temp_Fahrenheit*(-10)-tempF_integral*10;
      sprintf(string,"-%d.%d", tempF_integral, tempF_decimal);
      DataStruct->temp_F = strtof(string, NULL);
    }
    else
    {
      tempF_integral = temp_Fahrenheit;
      tempF_decimal = temp_Fahrenheit*10-tempF_integral*10;
      sprintf(string,"%d.%d", tempF_integral, tempF_decimal);
      DataStruct->temp_F = strtof(string, NULL);
    }
    // HAL_UART_Transmit(huart, string, 15, 1000);
  }
}
