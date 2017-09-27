#ifndef __GPIO_H
#define __GPIO_H

#include "stdint.h"
 
//=========================== define ==========================================

#ifndef TRUE
#define TRUE 1
#endif

#ifndef FALSE
#define FALSE 0
#endif

void gpio_init(void);
uint8_t gpio_userIntr_get();
void gpio_userIntr_set();


#endif