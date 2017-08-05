/**
 * \file
 *         Device drivers for SHT11 temperature and humidity sensor in Telosb.
 * \author
 *         Pedro Henrique Gomes <pedrohenriquegomes@gmail.com>
 */

#ifndef __SHT11_H__
#define __SHT11_H__

// measurement mode enumeration
enum {TEMP,HUMI};

// sht commands
							//adr  command  r/w
#define STATUS_REG_W 0x06   //000   0011    0
#define STATUS_REG_R 0x07   //000   0011    1
#define MEASURE_TEMP 0x03   //000   0001    1
#define MEASURE_HUMI 0x05   //000   0010    1
#define RESET        0x1e   //000   1111    0

void sht11_init(void);
void sht11_reset(void);
uint8_t sht11_is_present(void);
uint16_t sht11_read_temperature(void);
float sht11_convert_temperature(uint16_t temperature);
uint16_t sht11_read_humidity(void);
float sht11_convert_humidity(uint16_t humidity);


uint8_t sht11_measure_start(uint8_t mode);
uint8_t sht11_measure_test_done(void);
void sht11_measure_read(uint8_t *p_value, uint8_t *p_checksum);
uint8_t sht11_measure(uint8_t *p_value, uint8_t *p_checksum, uint8_t mode);
uint8_t sht11_crc(uint8_t *data, uint8_t dlen);
uint8_t sht11_measure_check(uint16_t *value, uint8_t mode);

#endif /* ifndef __SHT11_H__ */

