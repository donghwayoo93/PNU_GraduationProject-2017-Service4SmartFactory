/**
\brief An example CoAP application.
*/

#include "opendefs.h"
#include "userapp.h"
#include "opencoap.h"
#include "opentimers.h"
#include "openqueue.h"
#include "packetfunctions.h"
#include "openserial.h"
#include "openrandom.h"
#include "scheduler.h"

#include "idmanager.h"
#include "IEEE802154E.h"

/*
	added for solar sensor
*/
#include "adc_sensor.h"
#include "sensors.h"
#include "sht11.h"


//=========================== defines =========================================

/// inter-packet period (in ms)
#define USERAPPPERIOD  10000
#define PAYLOADLEN     14

const uint8_t userapp_path0[] = "app";

//=========================== variables =======================================

userapp_vars_t userapp_vars;

//=========================== prototypes ======================================

owerror_t userapp_receive(OpenQueueEntry_t* msg,
                    coap_header_iht*  coap_header,
                    coap_option_iht*  coap_options);
void    userapp_timer_cb(opentimer_id_t id);
void    userapp_task_cb(void);
void    userapp_sendDone(OpenQueueEntry_t* msg,
                       owerror_t error);

//=========================== public ==========================================

void userapp_init() {
   
   // prepare the resource descriptor for the /ex path
   userapp_vars.desc.path0len             = sizeof(userapp_path0)-1;
   userapp_vars.desc.path0val             = (uint8_t*)(&userapp_path0);
   userapp_vars.desc.path1len             = 0;
   userapp_vars.desc.path1val             = NULL;
   userapp_vars.desc.componentID          = COMPONENT_USERAPP;// originally COMPONENT_CEXAMPLE
   userapp_vars.desc.discoverable         = TRUE;
   userapp_vars.desc.callbackRx           = &userapp_receive;
   userapp_vars.desc.callbackSendDone     = &userapp_sendDone;

   /*
		init sensors
   */
   sensors_init();
   
   
   opencoap_register(&userapp_vars.desc);
   userapp_vars.timerId    = opentimers_start(USERAPPPERIOD,
                                                TIMER_PERIODIC,TIME_MS,
                                                userapp_timer_cb);
}

//=========================== private =========================================

owerror_t userapp_receive(OpenQueueEntry_t* msg,
                      coap_header_iht* coap_header,
                      coap_option_iht* coap_options) {
	/*
		created by Yoo DongHwa
		2017-07-10
		interacting with coap
		coap/tests/test_client_coap.py
	*/

   /*
	owerror_t outcome;
	uint8_t PUT_flag = E_FAIL;

	switch (coap_header->Code) {
		case COAP_CODE_REQ_GET:
			msg->payload = &(msg->packet[127]);
			msg->length = 0;

			packetfunctions_reserveHeaderSize(msg, 8);
			msg->payload[0] = COAP_PAYLOAD_MARKER;

			msg->payload[1] = 'a';
			msg->payload[2] = 'p';
			msg->payload[3] = 'p';
			msg->payload[4] = ' ';
			msg->payload[5] = 'g';
			msg->payload[6] = 'e';
			msg->payload[7] = 't';
			
			coap_header->Code = COAP_CODE_RESP_CONTENT;

			outcome = E_SUCCESS;
			break;

		case COAP_CODE_REQ_PUT:
			if (msg->payload[0] == '7') {
				PUT_flag = E_SUCCESS;
			}

			if (PUT_flag == E_SUCCESS) {
				msg->payload = &(msg->packet[127]);
				msg->length = 0;

				packetfunctions_reserveHeaderSize(msg, 8);
				msg->payload[0] = COAP_PAYLOAD_MARKER;

				msg->payload[1] = 'a';
				msg->payload[2] = 'p';
				msg->payload[3] = 'p';
				msg->payload[4] = ' ';
				msg->payload[5] = 'p';
				msg->payload[6] = 'u';
            msg->payload[7] = 't';

				coap_header->Code = COAP_CODE_RESP_CONTENT;

				outcome = E_SUCCESS;
				break;
			}

		default:
			outcome = E_FAIL;
			break;
	}

   return outcome;

   */
}

//timer fired, but we don't want to execute task in ISR mode
//instead, push task to scheduler with COAP priority, and let scheduler take care of it
void userapp_timer_cb(opentimer_id_t id){
   scheduler_push_task(userapp_task_cb,TASKPRIO_COAP);
}

void userapp_task_cb() {
   OpenQueueEntry_t*    pkt;
   owerror_t            outcome;
   uint8_t              i;
   
   uint16_t             sensor_read_solar          = 0;
   uint16_t             sensor_read_photosynthetic = 0;
   uint16_t             sensor_read_temperature	   = 0;
   uint16_t             sensor_read_humidity	      = 0;
   
   // don't run if not synch
   if (ieee154e_isSynch() == FALSE) return;
   
   // don't run on dagroot
   if (idmanager_getIsDAGroot()) {
      opentimers_stop(userapp_vars.timerId);
      return;
   }

   /*   2017.07.06
        modified by Yoo DongHwa
		get raw adc value from light sensors
   */
   sensor_read_solar		      = adc_sens_read_total_solar();
   sensor_read_photosynthetic = adc_sens_read_photosynthetic();
   sensor_read_temperature    = sht11_read_temperature();
   sensor_read_humidity       = sht11_read_humidity();

  // solar_lx			 = (uint16_t)(2.5 * (sensor_read_solar / 4096) * 6250);
  // photosynthetic_lx   = (uint16_t)(1.5 * (sensor_read_photosynthetic / 4096) * 1000);

   // create a CoAP RD packet
   pkt = openqueue_getFreePacketBuffer(COMPONENT_USERAPP);
   if (pkt==NULL) {
      openserial_printError(
         COMPONENT_USERAPP,
         ERR_NO_FREE_PACKET_BUFFER,
         (errorparameter_t)0,
         (errorparameter_t)0
      );
      openqueue_freePacketBuffer(pkt);
      return;
   }
   // take ownership over that packet
   pkt->creator                   = COMPONENT_USERAPP;
   pkt->owner                     = COMPONENT_USERAPP;
   // CoAP payload
   packetfunctions_reserveHeaderSize(pkt,PAYLOADLEN);
   for (i=0;i<PAYLOADLEN;i++) {
      pkt->payload[i]             = i;
   }
   /*
                           packet format(sequence in payload)
    ///////////////////////////////////////////////////////////////////////////////////////////
	/  sensor_read_solar  sensor_read_photosynthetic  sensor_read_temp  sensor_read_humidity  /
	/   raw adc value            raw adc value          raw adc value      raw adc value      /
	/     adc12mem5                adc12mem4                                                  /
	///////////////////////////////////////////////////////////////////////////////////////////
   */
   
   pkt->payload[0]                = (sensor_read_solar>>8)&0xff;
   pkt->payload[1]                = (sensor_read_solar>>0)&0xff;

   pkt->payload[2]				    = 0x20;
   pkt->payload[3]                = 0x20;

   pkt->payload[4]                = (sensor_read_photosynthetic >> 8) & 0xff;
   pkt->payload[5]                = (sensor_read_photosynthetic >> 0) & 0xff;

   pkt->payload[6]                = 0x20;
   pkt->payload[7]                = 0x20;

   pkt->payload[8]                = (sensor_read_temperature >> 8) & 0xff;
   pkt->payload[9]                = (sensor_read_temperature >> 0) & 0xff;

   pkt->payload[10]               = 0x20;
   pkt->payload[11]               = 0x20;

   pkt->payload[12]               = (sensor_read_humidity >> 8) & 0xff;
   pkt->payload[13]               = (sensor_read_humidity >> 0) & 0xff;

   packetfunctions_reserveHeaderSize(pkt,1);
   pkt->payload[0] = COAP_PAYLOAD_MARKER;
   
   // content-type option
   packetfunctions_reserveHeaderSize(pkt,2);
   pkt->payload[0]                = (COAP_OPTION_NUM_CONTENTFORMAT - COAP_OPTION_NUM_URIPATH) << 4
                                    | 1;
   pkt->payload[1]                = COAP_MEDTYPE_APPOCTETSTREAM;
   // location-path option
   packetfunctions_reserveHeaderSize(pkt,sizeof(userapp_path0)-1);
   memcpy(&pkt->payload[0],userapp_path0,sizeof(userapp_path0)-1);
   packetfunctions_reserveHeaderSize(pkt,1);
   pkt->payload[0]                = ((COAP_OPTION_NUM_URIPATH) << 4) | (sizeof(userapp_path0)-1);
   
   // metadata
   pkt->l4_destination_port       = WKP_UDP_COAP;
   pkt->l3_destinationAdd.type    = ADDR_128B;

   pkt->l3_destinationAdd.addr_128b[0]  = 0xbb;
   pkt->l3_destinationAdd.addr_128b[1]  = 0xbb;
   pkt->l3_destinationAdd.addr_128b[2]  = 0x00;
   pkt->l3_destinationAdd.addr_128b[3]  = 0x00;
   pkt->l3_destinationAdd.addr_128b[4]  = 0x00;
   pkt->l3_destinationAdd.addr_128b[5]  = 0x00;
   pkt->l3_destinationAdd.addr_128b[6]  = 0x00;
   pkt->l3_destinationAdd.addr_128b[7]  = 0x00;
   pkt->l3_destinationAdd.addr_128b[8]  = 0x00;
   pkt->l3_destinationAdd.addr_128b[9]  = 0x00;
   pkt->l3_destinationAdd.addr_128b[10] = 0x00;
   pkt->l3_destinationAdd.addr_128b[11] = 0x00;
   pkt->l3_destinationAdd.addr_128b[12] = 0x00;
   pkt->l3_destinationAdd.addr_128b[13] = 0x00;
   pkt->l3_destinationAdd.addr_128b[14] = 0x00;
   pkt->l3_destinationAdd.addr_128b[15] = 0x01;

   //memcpy(&pkt->l3_destinationAdd.addr_128b[0],&ipAddr_ringmaster,16);
   
   // send
   outcome = opencoap_send(
      pkt,
      COAP_TYPE_NON,
      COAP_CODE_REQ_PUT,
      1,
      &userapp_vars.desc
   );
   
   // avoid overflowing the queue if fails
   if (outcome==E_FAIL) {
      openqueue_freePacketBuffer(pkt);
   }
   
   return;
}

void userapp_sendDone(OpenQueueEntry_t* msg, owerror_t error) {
   openqueue_freePacketBuffer(msg);
}
