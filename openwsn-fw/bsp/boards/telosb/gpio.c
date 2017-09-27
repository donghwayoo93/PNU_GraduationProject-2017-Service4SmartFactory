#include "msp430f1611.h"
#include "gpio.h"
#include "stdint.h"

uint8_t status = 0;

void gpio_init(){

   P2DIR     &= ~0x80;                           // input direction
   P2OUT     |=  0x80;                           // put pin high as pushing button brings low
   P2IES     |=  0x80;                           // interrup when transition is high-to-low
   P2IE      |=  0x80;                           // enable interrupts
   
   //__bis_SR_register(GIE+LPM4_bits);             // sleep
}

/******************************** GIO 0 ********************************/

uint8_t gpio_userIntr_get() {
   return status;
}

void gpio_userIntr_set() {
	status = 0;
}


#pragma vector = PORT2_VECTOR
__interrupt void PORT2_ISR (void) {
   P2IFG &= ~0x80;                               // clear the interrupt flag
   status = 1;
}
