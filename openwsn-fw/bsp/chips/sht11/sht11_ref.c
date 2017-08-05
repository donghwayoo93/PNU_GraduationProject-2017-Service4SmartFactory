/*
 * sht11.c
 *
 *  Created on: 23.8.2012
 *      Author: ohejda
 *
 *  SHT11 module for MSP430
 *
 *  interface functions:
 *
 *		sht11_init() .. module initialization (setting ports)
 * 		sht_measure_start(mode) .. send start measure command (mode HUMI or TEMP)
 * 		sht_measure_test_done() .. test if measurement is done
 *		sht_measure_read(*p_value, *p_checksum) .. readout measurement and checksum
 *		sht_measure(*p_value, *p_checksum, mode) .. measure using previous functions (and loop waiting)
 *		sht_write_statusreg(*p_value) .. write status register
 * 		sht_read_statusreg(*p_value, *p_checksum) .. read status register
 *		sht_crc(*data, dlen) .. calculate crc
 *		sht_measure_check(*value, mode) .. measure and check crc
 *
 */

/** include section */

// register names
#include <msp430g2553.h>
// self
#include "sht11.h"

/** module local definitions */

// hardware dependent defines
// delay
#define delay_us(x) __delay_cycles(x)
// port (DATA P2.0, SCK P2.1)
#define SHT_PORT_INIT() {P2DIR|=0x03;P2OUT&=~0x03;}
#define SHT_DATA_OUT(x) {if (x!=0) P2DIR|=0x01; else P2DIR&=~0x01;}
#define SHT_DATA_IN (((P2IN&0x01)!=0)?1:0)
#define SHT_SCK(x) {if (x!=0) P2OUT|=0x02; else P2OUT&=~0x02;}

// communication
#define		noACK	0
#define		ACK		1

// crc lookup table
const unsigned char crc_lut[] = {
//   0   1   2   3   4   5   6   7   8   9   A   B   C   D   E   F
    0  , 49, 98, 83,196,245,166,151,185,136,219,234,125, 76, 31, 46,  // 0
    67 ,114, 33, 16,135,182,229,212,250,203,152,169, 62, 15, 92,109,  // 1
    134,183,228,213, 66,115, 32, 17, 63, 14, 93,108,251,202,153,168,  // 2
    197,244,167,150,  1, 48, 99, 82,124, 77, 30, 47,184,137,218,235,  // 3
    61 , 12, 95,110,249,200,155,170,132,181,230,215, 64,113, 34, 19,  // 4
    126, 79, 28, 45,186,139,216,233,199,246,165,148,  3, 50, 97, 80,  // 5
    187,138,217,232,127, 78, 29, 44,  2, 51, 96, 81,198,247,164,149,  // 6
    248,201,154,171, 60, 13, 94,111, 65,112, 35, 18,133,180,231,214,  // 7
    122, 75, 24, 41,190,143,220,237,195,242,161,144,  7, 54,101, 84,  // 8
    57 ,  8, 91,106,253,204,159,174,128,177,226,211, 68,117, 38, 23,  // 9
    252,205,158,175, 56,  9, 90,107, 69,116, 39, 22,129,176,227,210,  // A
    191,142,221,236,123, 74, 25, 40,  6, 55,100, 85,194,243,160,145,  // B
    71 ,118, 37, 20,131,178,225,208,254,207,156,173, 58, 11, 88,105,  // C
    4  , 53,102, 87,192,241,162,147,189,140,223,238,121, 72, 27, 42,  // D
    193,240,163,146,  5, 52,103, 86,120, 73, 26, 43,188,141,222,239,  // E
    130,179,224,209, 70,119, 36, 21, 59, 10, 89,104,255,206,157,172}; // F

/** Sensibus basics section */

//----------------------------------------------------------------------------------
// writes a byte on the Sensibus and checks the acknowledge
//----------------------------------------------------------------------------------
char sht_write_byte(unsigned char value)
{
	unsigned char i,error=0;
	for (i=0x80;i>0;i>>=1)             	//shift bit for masking
  	{
		if (i & value) 	SHT_DATA_OUT(0)		//masking value with i , write to SENSI-BUS
    		else SHT_DATA_OUT(1);
		SHT_SCK(1);                          //clk for SENSI-BUS
		delay_us(5);						//pulswith approx. 5 us
		SHT_SCK(0);
  	}
	SHT_DATA_OUT(0);                       //release DATA-line
	SHT_SCK(1);                            //clk #9 for ack
	error=SHT_DATA_IN;                    //check ack (DATA will be pulled down by SHT11)
	SHT_SCK(0);
	return error;                     	//error=1 in case of no acknowledge
}

//----------------------------------------------------------------------------------
// reads a byte form the Sensibus and gives an acknowledge in case of "ack=1"
//----------------------------------------------------------------------------------
char sht_read_byte(unsigned char ack)
{
	unsigned char i,val=0;
	SHT_DATA_OUT(0);             			//release DATA-line
	for (i=0x80;i>0;i>>=1)             	//shift bit for masking
	{
		SHT_SCK(1);          				//clk for SENSI-BUS
		if (SHT_DATA_IN) val=(val | i);   	//read bit
		SHT_SCK(0);
  	}
	SHT_DATA_OUT(ack);               		//in case of "ack==1" pull down DATA-Line
	SHT_SCK(1);                            //clk #9 for ack
	delay_us(5);         					//pulswith approx. 5 us
	SHT_SCK(0);
	SHT_DATA_OUT(0);                 		//release DATA-line
	return val;
}

//----------------------------------------------------------------------------------
// generates a transmission start
//       _____         ________
// DATA:      |_______|
//           ___     ___
// SCK : ___|   |___|   |______
//----------------------------------------------------------------------------------
void sht_transstart(void)
{
	SHT_DATA_OUT(0);
	SHT_SCK(0);                   //Initial state
	delay_us(1);
	SHT_SCK(1);
	delay_us(1);
	SHT_DATA_OUT(1);
	delay_us(1);
	SHT_SCK(0);
	delay_us(5);
	SHT_SCK(1);
	delay_us(1);
	SHT_DATA_OUT(0);
	delay_us(1);
	SHT_SCK(0);
}

//----------------------------------------------------------------------------------
// communication reset: DATA-line=1 and at least 9 SCK cycles followed by transstart
//       _____________________________________________________         ________
// DATA:                                                      |_______|
//          _    _    _    _    _    _    _    _    _        ___     ___
// SCK : __| |__| |__| |__| |__| |__| |__| |__| |__| |______|   |___|   |______
//----------------------------------------------------------------------------------

void sht_connectionreset(void)
{
	unsigned char i;
	SHT_DATA_OUT(0); SHT_SCK(0);     	//Initial state
	//for(i=0;i<9;i++)                  //9 SCK cycles
	for(i=9;i!=0;i--)                  //9 SCK cycles (detecting 0 is easier - says TI)
	{
		SHT_SCK(1);
		delay_us(1);
		SHT_SCK(0);
	}
	sht_transstart();                   //transmission start
}

//----------------------------------------------------------------------------------
// resets the sensor by a softreset
//----------------------------------------------------------------------------------
char sht_softreset(void)
{
	unsigned char error=0;
	sht_connectionreset();              //reset communication
	error+=sht_write_byte(RESET);      //send RESET-command to sensor
	return error;                     //error=1 in case of no response form the sensor
}

/** interface functions section */

//----------------------------------------------------------------------------------
// sht initialization (only port settings)
//----------------------------------------------------------------------------------
void sht11_init(void)
{
	SHT_PORT_INIT();
}

//----------------------------------------------------------------------------------
// start measurement (humidity/temperature)
//----------------------------------------------------------------------------------
char sht_measure_start(unsigned char mode)
{
	sht_transstart(); // transmission start
	switch(mode) {  // send command to sensor
		case TEMP: return(sht_write_byte(MEASURE_TEMP)); //break;
		case HUMI: return(sht_write_byte(MEASURE_HUMI)); //break;
		default:	break;
	}
	return 1; // error
}

//----------------------------------------------------------------------------------
// test measurement done (1 done, 0 not)
//----------------------------------------------------------------------------------
char sht_measure_test_done(void)
{
	if (SHT_DATA_IN==0) return 1;
	return 0;
}

//----------------------------------------------------------------------------------
// read measurement
//----------------------------------------------------------------------------------
void sht_measure_read(unsigned char *p_value, unsigned char *p_checksum)
{
	*(p_value+1) = sht_read_byte(ACK); 	// read the first byte (MSB)
	*(p_value) 	 = sht_read_byte(ACK); 	// read the second byte (LSB)
	*p_checksum  = sht_read_byte(noACK); // read checksum
}

//----------------------------------------------------------------------------------
// makes a measurement (humidity/temperature) with checksum (with waiting)
//----------------------------------------------------------------------------------
char sht_measure(unsigned char *p_value, unsigned char *p_checksum, unsigned char mode)
{
  unsigned error=0;
  unsigned int i=0;

  error += sht_measure_start(mode); //start measurement

  while (i<20000) // test measurement done (aprox. 2s)
  {
	  if (sht_measure_test_done()==1) break;
	  delay_us(100);
	  i++;
  }
  if (i==20000) error++;

  // read and check measurement
  sht_measure_read(p_value,p_checksum);

  // return error count (0 if value ok)
  return error;
}

//----------------------------------------------------------------------------------
// reads the status register with checksum (8-bit)
//----------------------------------------------------------------------------------
char sht_read_statusreg(unsigned char *p_value, unsigned char *p_checksum)
{
  unsigned char error=0;
  sht_transstart();                   //transmission start
  error=sht_write_byte(STATUS_REG_R); //send command to sensor
  *p_value=sht_read_byte(ACK);        //read status register (8-bit)
  *p_checksum=sht_read_byte(noACK);   //read checksum (8-bit)
  return error;                     //error=1 in case of no response form the sensor
}

//----------------------------------------------------------------------------------
// writes the status register with checksum (8-bit)
//----------------------------------------------------------------------------------
char sht_write_statusreg(unsigned char *p_value)
{
  unsigned char error=0;
  sht_transstart();                   //transmission start
  error+=sht_write_byte(STATUS_REG_W);//send command to sensor
  error+=sht_write_byte(*p_value);    //send value of status register
  return error;                     //error>=1 in case of no response form the sensor
}

//----------------------------------------------------------------------------------
// calculate crc
//----------------------------------------------------------------------------------
unsigned char sht_crc(unsigned char* data, unsigned char dlen)
{
    unsigned char crc = 0,ret = 0;
    unsigned char i;

    // get crc (xor -> lookup table)
    for (i=dlen;i!=0;i--)
    {
        crc ^= *data++;
        crc = crc_lut[crc];
    }

    // reverse result
    ret |= crc&0x01;
    for (i=7;i!=0;i--)
    {
        ret<<=1;
        crc>>=1;
        ret |= crc&0x01;
    }

    return ret;
}

//----------------------------------------------------------------------------------
// measure and check crc (with waiting)
//----------------------------------------------------------------------------------
unsigned char sht_measure_check(unsigned int *value, unsigned char mode)
{
	unsigned char checksum;
	unsigned int val;
	unsigned char data[3];
	if (sht_measure((unsigned char*)&val,&checksum,mode)!=0) return 1;
	switch (mode)
	{
		case TEMP: data[0]=MEASURE_TEMP; break;
		case HUMI: data[0]=MEASURE_HUMI; break;
		default: return 1;
	}
	data[1]=(unsigned int)val>>8;
	data[2]=val;
	if (checksum!=sht_crc(data,3)) return 1;
	*value=val;
	return 0;
}