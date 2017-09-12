#ifndef __GPIOS_H
#define __GPIOS_H

#include "stdint.h"
 
//=========================== define ==========================================

#ifndef TRUE
#define TRUE 1
#endif

#ifndef FALSE
#define FALSE 0
#endif

void gpios_init(void);

/******************************** GIO 0 ********************************/
void gpios_GIO0_on(void);
void gpios_GIO0_off(void);
void gpios_GIO0_toggle(void);
uint8_t gpios_GIO0_isOn(void);
/******************************** GIO 1 ********************************/
void gpios_GIO1_on(void);
void gpios_GIO1_off(void);
void gpios_GIO1_toggle(void);
uint8_t gpios_GIO1_isOn(void);
/******************************** GIO 2 ********************************/
void gpios_GIO2_on(void);
void gpios_GIO2_off(void);
void gpios_GIO2_toggle(void);
uint8_t gpios_GIO2_isOn(void);
/******************************** GIO 3 ********************************/
void gpios_GIO3_on(void);
void gpios_GIO3_off(void);
void gpios_GIO3_toggle(void);
uint8_t gpios_GIO3_isOn(void);

#endif