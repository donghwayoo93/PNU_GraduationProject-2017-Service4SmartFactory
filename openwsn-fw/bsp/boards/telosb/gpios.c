#include "msp430f1611.h"
#include "gpios.h"


void gpios_init(){
	P6DIR |= 0x0C;
	P6OUT &= ~0x0C;
}

/******************************** GIO 0 ********************************/

// P6.3 ADC3 0b00001000
void gpios_GIO0_on(){
	P6OUT |= 0x08;
}

void gpios_GIO0_off(){
	P6OUT &= ~0x08;
}

void gpios_GIO0_toggle(){
	P6OUT ^= 0x08;
}
uint8_t gpios_GIO0_isOn() {
   return (uint8_t)(P6OUT & 0x08)>>3;
}

/******************************** GIO 1 ********************************/
// P6.2 ADC2 0b00000100
void gpios_GIO1_on(){
	P6OUT |= 0x04;
}

void gpios_GIO1_off(){
	P6OUT &= ~0x04;
}

void gpios_GIO1_toggle(){
	P6OUT ^= 0x04;
}
uint8_t gpios_GIO1_isOn() {
   return (uint8_t)(P6OUT & 0x04)>>2;
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
