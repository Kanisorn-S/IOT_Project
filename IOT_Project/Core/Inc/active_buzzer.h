/*
 * active_buzzer.h
 *
 *  Created on: Sep 12, 2024
 *      Author: K0NQ
 */

#ifndef INC_ACTIVE_BUZZER_H_
#define INC_ACTIVE_BUZZER_H_

#include "main.h"
#include <stdint.h>

typedef struct
{
  GPIO_TypeDef* GPIOx;
  uint16_t GPIO_Pin;
} Active_Buzzer;


Active_Buzzer Active_Buzzer_Init(GPIO_TypeDef* GPIOx, uint16_t GPIO_Pin);
void Active_Buzzer_On(Active_Buzzer buzzer);
void Active_Buzzer_Off(Active_Buzzer buzzer);
void Active_Buzzer_Toggle(Active_Buzzer buzzer);
void Active_Buzzer_Timed(Active_Buzzer buzzer, uint32_t duration);

#endif /* INC_ACTIVE_BUZZER_H_ */
