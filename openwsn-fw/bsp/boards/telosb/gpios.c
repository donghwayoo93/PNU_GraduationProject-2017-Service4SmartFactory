#include "msp430f1611.h"
#include "gpios.h"


void gpios_init(){
	P2DIR |= 0x4B;
	P2OUT |= 0x4B;
}

/******************************** GIO 0 ********************************/

void gpios_GIO0_on(){
	P2OUT &= ~0x01;
}

void gpios_GIO0_off(){
	P2OUT |= 0x01;
}

void gpios_GIO0_toggle(){
	P2OUT ^= 0x01;
}
uint8_t gpios_GIO0_isOn() {
   return (uint8_t)(~P2OUT & 0x01);
}

/******************************** GIO 1 ********************************/

void gpios_GIO1_on(){
	P2OUT &= ~0x02;
}

void gpios_GIO1_off(){
	P2OUT |= 0x02;
}

void gpios_GIO1_toggle(){
	P2OUT ^= 0x02;
}
uint8_t gpios_GIO1_isOn() {
   return (uint8_t)(~P2OUT & 0x02)>>1;
}

/******************************** GIO 2 ********************************/
/*
void gpios_GIO2_on(){
	P2OUT &= ~0x08;
}

void gpios_GIO2_off(){
	P2OUT |= 0x08;
}

void gpios_GIO2_toggle(){
	P2OUT ^= 0x08;
}
uint8_t gpios_GIO2_isOn() {
   return (uint8_t)(~P2OUT & 0x08)>>3;
}
*/

/******************************** GIO 3 ********************************/
/*
void gpios_GIO3_on(){
	P2OUT &= ~0x40;
}

void gpios_GIO3_off(){
	P2OUT |= 0x40;
}

void gpios_GIO3_toggle(){
	P2OUT ^= 0x40;
}
uint8_t gpios_GIO3_isOn() {
   return (uint8_t)(~P2OUT & 0x40)>>6;
}
*/
