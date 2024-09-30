/*
 * tcs3200.h
 *
 *  Created on: Sep 10, 2024
 *      Author: K0NQ
 */

#ifndef INC_TCS3200_H_
#define INC_TCS3200_H_

#include <stdio.h>
#include "main.h"

// Define Color Filter
#define TCS3200_COLOR_RED 0x00
#define TCS3200_COLOR_GREEN 0x01
#define TCS3200_COLOR_BLUE 0x02
#define TCS3200_COLOR_CLEAR 0x03

// Define Frequency Scaling
#define TCS3200_PWR_DOWN 0x00
#define TCS3200_OFREQ_2P 0x01
#define TCS3200_OFREQ_20P 0x02
#define TCS3200_OFREQ_100P 0x03

// Define MIN/MAX Frequency Each Color
#define MIN_RED 616
#define MAX_RED 2941
#define MIN_GREEN 666
#define MAX_GREEN 3095
#define MIN_BLUE 800
#define MAX_BLUE 3533

void HAL_TIM_IC_CaptureCallback(TIM_HandleTypeDef *htim);
void TCS3200_Freq_Scaling(uint8_t scaling);
void TCS3200_Select_Filter(uint8_t filter);
uint32_t TCS3200_ReadFrequency(uint8_t filter);
uint8_t MapFrequencyToHex(uint32_t freq, uint32_t min_freq, uint32_t max_freq);

extern volatile uint32_t capture_val1, capture_val2;
extern volatile uint32_t frequency;
extern volatile uint8_t capture_flag;


#endif /* INC_TCS3200_H_ */
