/*
 * sht11.h
 *
 *  Created on: 23.8.2012
 *      Author: ohejda
 */

#ifndef SHT11_H_
#define SHT11_H_

// measurement mode enumeration
enum {TEMP,HUMI};

// sht commands
							//adr  command  r/w
#define STATUS_REG_W 0x06   //000   0011    0
#define STATUS_REG_R 0x07   //000   0011    1
#define MEASURE_TEMP 0x03   //000   0001    1
#define MEASURE_HUMI 0x05   //000   0010    1
#define RESET        0x1e   //000   1111    0

// function prototypes

/*// sensibus basics .. not interfacing
char sht_write_byte(unsigned char value);
char sht_read_byte(unsigned char ack);
void sht_transstart(void);
void sht_connectionreset(void);
char sht_softreset(void);*/

// initialization
void sht11_init(void);
// start measurement
char sht_measure_start(unsigned char mode);
// test if measurement done (for waiting loops)
char sht_measure_test_done(void);
// read measurement
void sht_measure_read(unsigned char *p_value, unsigned char *p_checksum);
// measure (start measurement and wait result)
char sht_measure(unsigned char *p_value, unsigned char *p_checksum, unsigned char mode);
// read/write status register
char sht_write_statusreg(unsigned char *p_value);
char sht_read_statusreg(unsigned char *p_value, unsigned char *p_checksum);
// calculate checksum
unsigned char sht_crc(unsigned char* data, unsigned char dlen);
// read measurement and check crc
unsigned char sht_measure_check(unsigned int* value, unsigned char mode);

#endif /* SHT11_H_ */