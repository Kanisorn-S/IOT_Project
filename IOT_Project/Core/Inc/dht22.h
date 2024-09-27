/*
 * dht22.h
 *
 *  Created on: Sep 7, 2024
 *      Author: K0NQ
 */

#ifndef INC_DHT22_H_
#define INC_DHT22_H_

#include <stdio.h>
#include "main.h"

// DHT22 structure
typedef struct
{
	float humidity;
	float temp_C;
	float temp_F;
} DHT22_t;

uint8_t DHT22_Start(GPIO_TypeDef* DHT22_PORT, uint16_t DHT22_PIN, TIM_HandleTypeDef *htim, uint32_t *pMillis, uint32_t *cMillis);
uint8_t DHT22_Read(GPIO_TypeDef* DHT22_PORT, uint16_t DHT22_PIN, TIM_HandleTypeDef *htim, uint32_t *pMillis, uint32_t *cMillis);
void DHT22_Read_All(DHT22_t *DataStruct, UART_HandleTypeDef *huart, GPIO_TypeDef* DHT22_PORT, uint16_t DHT22_PIN, TIM_HandleTypeDef *htim, uint32_t *pMillis, uint32_t *cMillis);


#endif /* INC_DHT22_H_ */
