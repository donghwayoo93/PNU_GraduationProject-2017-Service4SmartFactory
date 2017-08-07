/**
 * \file
 *         Device drivers for SHT11 temperature and humidity sensor in Telosb.
 * \author
 *         Pedro Henrique Gomes <pedrohenriquegomes@gmail.com>
 */

#include "i2c.h"
#include "sht11.h"

//#include "msp430f1611.h"

//=========================== define ===========================================

// port Data(P2.0), SCK(P2.1)
#define SHT11_DATA_OUT(x) {if (x != 0) P2DIR |= 0x01; else P2DIR &= ~0x01;}
#define SHT11_DATA_IN (((P2IN & 0x01) != 0) ? 1 : 0)
#define SHT11_SCK(x) {if(x != 0) P2OUT |= 0x02; else P2OUT &= ~0x02;}

#define NOACK 0
#define ACK   1

#define delay_us(x) __delay_cycles(x)

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

//=========================== variables ========================================

//=========================== prototypes =======================================

uint8_t sht11_write_byte(uint8_t value);
uint8_t sht11_read_byte(uint8_t ack);
void sht11_trans_start(void);
void sht11_connection_reset(void);
uint8_t sht11_softreset(void);

uint8_t sht11_measure_start(uint8_t mode);
uint8_t sht11_measure_test_done(void);
void sht11_measure_read(uint8_t *p_value, uint8_t *p_checksum);
uint8_t sht11_measure(uint8_t *p_value, uint8_t *p_checksum, uint8_t mode);
uint8_t sht11_crc(uint8_t *data, uint8_t dlen);
uint8_t sht11_measure_check(uint16_t *value, uint8_t mode);

//=========================== public ===========================================

void sht11_init(void) {
	P2DIR |=  0x03;
	P2OUT &= ~0x03;
}

void sht11_reset(void) {
	sht11_connection_reset();
}

uint8_t sht11_is_present(void) {
    return 0;
}

uint16_t sht11_read_temperature(void) {
	uint16_t temp_value = 0;

	if(sht11_measure_check(&temp_value, TEMP) == 0)
		return temp_value;
	else
		return 0xFFFF; // MAX VALUE means error
}

float sht11_convert_temperature(uint16_t temperature) {
    return 0;
}

uint16_t sht11_read_humidity(void) {
	uint16_t humi_value = 0;

	if(sht11_measure_check(&humi_value, HUMI) == 0)
		return humi_value;
	else
		return 0xFFFF; // MAX VALUE means error
}

float sht11_convert_humidity(uint16_t humidity) {
    return 0;
}

//=========================== private ==========================================

/* writes a byte on the bus and checks the ACK */
uint8_t sht11_write_byte(uint8_t value){
	uint8_t i, error = 0;

	for (i=0x80;i>0;i>>=1){             	//shift bit for masking
		if (i & value){
			SHT11_DATA_OUT(0);		//masking value with i , write to SENSI-BUS
		 }
    	else{
    		SHT11_DATA_OUT(1);
    	}
		SHT11_SCK(1);                          //clk for SENSI-BUS
		delay_us(5);						//pulswith approx. 5 us
		SHT11_SCK(0);
  	}
	SHT11_DATA_OUT(0);                       //release DATA-line
	SHT11_SCK(1);                            //clk #9 for ack
	error=SHT11_DATA_IN;                    //check ack (DATA will be pulled down by SHT11)
	SHT11_SCK(0);
	return error;                     	//error=1 in case of no acknowledge
}

/* reads a byte from bus and gives the ACK if "ack=1" */
uint8_t sht11_read_byte(uint8_t ack){
	uint8_t i,val=0;
	SHT11_DATA_OUT(0);             			//release DATA-line
	for (i=0x80;i>0;i>>=1){             	//shift bit for masking
		SHT11_SCK(1);          				//clk for SENSI-BUS
		if (SHT11_DATA_IN){
			val=(val | i);   	            //read bit
		}
		SHT11_SCK(0);
  	}
	SHT11_DATA_OUT(ack);               		//in case of "ack==1" pull down DATA-Line
	SHT11_SCK(1);                            //clk #9 for ack
	delay_us(5);         					//pulswith approx. 5 us
	SHT11_SCK(0);
	SHT11_DATA_OUT(0);                 		//release DATA-line
	return val;
}

/* generates the transmission start */
void sht11_trans_start(void){
	SHT11_DATA_OUT(0);
	SHT11_SCK(0);                   //Initial state
	delay_us(1);
	SHT11_SCK(1);
	delay_us(1);
	SHT11_DATA_OUT(1);
	delay_us(1);
	SHT11_SCK(0);
	delay_us(5);
	SHT11_SCK(1);
	delay_us(1);
	SHT11_DATA_OUT(0);
	delay_us(1);
	SHT11_SCK(0);
}

/* communication reset */
void sht11_connection_reset(void){
	uint8_t i;
	SHT11_DATA_OUT(0); 
	SHT11_SCK(0);     	//Initial state
	//for(i=0;i<9;i++)                  //9 SCK cycles
	for(i=9;i!=0;i--){                  //9 SCK cycles (detecting 0 is easier - says TI)
		SHT11_SCK(1);
		delay_us(1);
		SHT11_SCK(0);
	}
	sht11_trans_start();                   //transmission start
}

/* reset the sensor by soft reset */
uint8_t sht11_softreset(void){
	uint8_t error = 0;
	sht11_connection_reset();
	error+=sht11_write_byte(RESET);
	return error;
}

/* measurement start (temperature / humidity) */
uint8_t sht11_measure_start(uint8_t mode){
	sht11_trans_start();
	switch(mode){
		case TEMP:
			return (sht11_write_byte(MEASURE_TEMP));
			break;
		case HUMI:
			return (sht11_write_byte(MEASURE_HUMI));
			break;
		default:
			break;
	}
	return 1; // this case should not happen : error
}

/* test measurement done */
uint8_t sht11_measure_test_done(void){
	if(SHT11_DATA_IN == 0){
		return 1;
	}
	return 0;
}

/* read measurement */
void sht11_measure_read(uint8_t *p_value, uint8_t *p_checksum){
	*(p_value + 1) = sht11_read_byte(ACK);   // read the first byte  (MSB)
	*(p_value)     = sht11_read_byte(ACK);   // read the second byte (LSB)
	*p_checksum    = sht11_read_byte(NOACK); //read the checksum
}

/* makes a measurement with checksum */
uint8_t sht11_measure(uint8_t *p_value, uint8_t *p_checksum, uint8_t mode){
	uint8_t  error = 0;
	uint16_t     i = 0;

	error += sht11_measure_start(mode); // start measurement

	while(i < 20000){
		if(sht11_measure_test_done() == 1){
			delay_us(100);
			i++;
		}// end if
	}// end while

	if(i == 20000)
		error++; // time out error

	sht11_measure_read(p_value, p_checksum);

	return error; // error == 0 => no error 
	              // error == 1 => error
}

/* calculate crc */
uint8_t sht11_crc(uint8_t *data, uint8_t dlen){
	uint8_t crc = 0, ret = 0;
	uint8_t i;

	// get crc
	for(i=dlen; i!=0; i--){
		crc ^= *data++;
		crc  = crc_lut[crc];
	}

	// reverse result
	ret |= crc&0x01;
	for (i=7; i!=0; i--){
		ret<<=1;
		crc>>=1;
		ret |= crc&0x01;
	}
	return ret;
}

/* measure and check with crc */
uint8_t sht11_measure_check(uint16_t *value, uint8_t mode){
	uint8_t checksum;
	uint16_t val;
	uint8_t data[3];

	if(sht11_measure((uint8_t *)&val, &checksum, mode)!=0)
		return 1;

	switch(mode){
		case TEMP:
			data[0] = MEASURE_TEMP;
			break;
		case HUMI:
			data[0] = MEASURE_HUMI;
			break;
		default: // this should not happen
			return 1;
	} // end switch

	data[1] = (uint16_t)val>>8;
	data[2] = val;

	if(checksum != sht11_crc(data, 3)) // checksum incorrect!
		return 1;
	else // assign correct value to pointer
		*value = val;

	return 0;
}