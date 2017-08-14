/**
\brief An example CoAP application.
*/

#include "opendefs.h"
#include "cexample.h"
#include "opencoap.h"
#include "opentimers.h"
#include "openqueue.h"
#include "packetfunctions.h"
#include "openserial.h"
#include "openrandom.h"
#include "scheduler.h"

#include "idmanager.h"
#include "IEEE802154E.h"

#include "icmpv6rpl.h"

/*
	added for solar sensor
*/
//#include "adc_sensor.h"
//#include "sensors.h"
//#include "sht11.h"


//=========================== defines =========================================

/// inter-packet period (in ms)
#define CEXAMPLEPERIOD  30000
#define PAYLOADLEN      14

const uint8_t cexample_path0[] = "ex";

//=========================== variables =======================================

cexample_vars_t cexample_vars;

//=========================== prototypes ======================================

owerror_t cexample_receive(OpenQueueEntry_t* msg,
                    coap_header_iht*  coap_header,
                    coap_option_iht*  coap_options);
void    cexample_timer_cb(opentimer_id_t id);
void    cexample_task_cb(void);
void    cexample_sendDone(OpenQueueEntry_t* msg,
                       owerror_t error);

//=========================== public ==========================================

void cexample_init() {
   
   // prepare the resource descriptor for the /ex path
   cexample_vars.desc.path0len             = sizeof(cexample_path0)-1;
   cexample_vars.desc.path0val             = (uint8_t*)(&cexample_path0);
   cexample_vars.desc.path1len             = 0;
   cexample_vars.desc.path1val             = NULL;
   cexample_vars.desc.componentID          = COMPONENT_CEXAMPLE;
   cexample_vars.desc.discoverable         = TRUE;
   cexample_vars.desc.callbackRx           = &cexample_receive;
   cexample_vars.desc.callbackSendDone     = &cexample_sendDone;

   /*
		init sensors
   */
   //sensors_init();
   
   
   opencoap_register(&cexample_vars.desc);
   cexample_vars.timerId    = opentimers_start(CEXAMPLEPERIOD,
                                                TIMER_PERIODIC,TIME_MS,
                                                cexample_timer_cb);
}

//=========================== private =========================================

owerror_t cexample_receive(OpenQueueEntry_t* msg,
                      coap_header_iht* coap_header,
                      coap_option_iht* coap_options) {
	/*
		created by Yoo DongHwa
		2017-07-10
		interacting with coap
		coap/tests/test_client_coap.py
      2017-08-12
      modified
      adjust DIO, DAO Period with CoAP Packet based RPL.py
	*/
	owerror_t outcome;
	uint8_t PUT_flag = E_FAIL;
   uint8_t i = 0;
   uint16_t new_dioPeriod = 0, new_daoPeriod = 0;

	switch (coap_header->Code) {
		case COAP_CODE_REQ_GET:
			msg->payload = &(msg->packet[127]);
			msg->length = 0;

			packetfunctions_reserveHeaderSize(msg, 9);
			msg->payload[0] = COAP_PAYLOAD_MARKER;

			msg->payload[1] = 'e';
			msg->payload[2] = 'x';
			msg->payload[3] = ' ';
			msg->payload[4] = 'g';
			msg->payload[5] = 'e';
			msg->payload[6] = 't';
			msg->payload[7] = ' ';

			if (1 == 1) {
				msg->payload[8] = 'o';
			}
			else {
				msg->payload[8] = 'x';
			}
			
			coap_header->Code = COAP_CODE_RESP_CONTENT;

			outcome = E_SUCCESS;
			break;
      //------------------------------------------case GET
		case COAP_CODE_REQ_PUT:
         
         if((msg->payload[0] == DIO_PERIOD) &&
            (msg->payload[1] == CEXAMPLE_SEPERATOR)) {               // SET DIO Period
            new_dioPeriod = (msg->payload[2] - 48);
            if(msg->payload[3] == MARKER_END){
               new_dioPeriod = new_dioPeriod * 10000;
               icmpv6rpl_setDIOPeriod(new_dioPeriod);                 // void (uint16_t dioPeriod)
               PUT_flag = E_SUCCESS;
            }
         }
         else if((msg->payload[0] == DAO_PERIOD) &&
            (msg->payload[1] == CEXAMPLE_SEPERATOR)) {               // SET DAO Period
            new_daoPeriod = (msg->payload[2] - 48);
            if(msg->payload[3] == MARKER_END){
               new_daoPeriod = new_daoPeriod * 10000;
               icmpv6rpl_setDAOPeriod(new_daoPeriod);                 // void (uint16_t daoPeriod)
               PUT_flag = E_SUCCESS;
            }
         }
         else{                                                       // Received Undefined VALUE
            PUT_flag = E_FAIL;
         }

         msg->payload = &(msg->packet[127]);
         msg->length = 0;

			if (PUT_flag == E_SUCCESS) {                                // Response with changed Value
				packetfunctions_reserveHeaderSize(msg, 7);
				msg->payload[0] = COAP_PAYLOAD_MARKER;

				msg->payload[1] = new_dioPeriod + 48;
				msg->payload[2] = new_daoPeriod + 48;
				msg->payload[3] = ' ';
				msg->payload[4] = 'p';
				msg->payload[5] = 'u';
				msg->payload[6] = 't';
			}
         else if(PUT_flag == E_FAIL){                                // Response with error
            packetfunctions_reserveHeaderSize(msg, 7);
            msg->payload[0] = COAP_PAYLOAD_MARKER;

            msg->payload[1] = 'e';
            msg->payload[2] = 'x';
            msg->payload[3] = ' ';
            msg->payload[4] = 'e';
            msg->payload[5] = 'r';
            msg->payload[6] = 'r';
         }

         coap_header->Code = COAP_CODE_RESP_CONTENT;
         outcome = E_SUCCESS;

         break;
         //------------------------------------------case PUT
		default:
			outcome = E_FAIL;
			break;
	}  // end switch-case

   return outcome;
}

//timer fired, but we don't want to execute task in ISR mode
//instead, push task to scheduler with COAP priority, and let scheduler take care of it
void cexample_timer_cb(opentimer_id_t id){
   scheduler_push_task(cexample_task_cb,TASKPRIO_COAP);
}

void cexample_task_cb() {
   OpenQueueEntry_t*    pkt;
   owerror_t            outcome;
   uint8_t              my_suffix_1, my_suffix_2;
   uint8_t              i;
   
   uint16_t             sensor_read_solar          = 0;
   uint16_t             sensor_read_photosynthetic = 0;
   uint16_t             sensor_read_temperature	   = 0;
   uint16_t             sensor_read_humidity	      = 0;
   
   // don't run if not synch
   if (ieee154e_isSynch() == FALSE) return;
   
   // don't run on dagroot
   if (idmanager_getIsDAGroot()) {
      opentimers_stop(cexample_vars.timerId);
      return;
   }

   /*   2017.07.06
        modified by Yoo DongHwa
		get raw adc value from light sensors
   */
   //sensor_read_solar		  = adc_sens_read_total_solar();
   //sensor_read_photosynthetic = adc_sens_read_photosynthetic();
   //sensor_read_temperature    = sensors_getCallbackRead(SENSOR_TEMPERATURE);
   //sensor_read_humidity       = sensors_getCallbackRead(SENSOR_HUMIDITY);

  // solar_lx			 = (uint16_t)(2.5 * (sensor_read_solar / 4096) * 6250);
  // photosynthetic_lx   = (uint16_t)(1.5 * (sensor_read_photosynthetic / 4096) * 1000);

   my_suffix_1 = idmanager_getMyID(ADDR_64B)->addr_64b[6];
   my_suffix_2 = idmanager_getMyID(ADDR_64B)->addr_64b[7];

   // create a CoAP RD packet
   pkt = openqueue_getFreePacketBuffer(COMPONENT_CEXAMPLE);
   if (pkt==NULL) {
      openserial_printError(
         COMPONENT_CEXAMPLE,
         ERR_NO_FREE_PACKET_BUFFER,
         (errorparameter_t)0,
         (errorparameter_t)0
      );
      openqueue_freePacketBuffer(pkt);
      return;
   }
   // take ownership over that packet
   pkt->creator                   = COMPONENT_CEXAMPLE;
   pkt->owner                     = COMPONENT_CEXAMPLE;
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

   pkt->payload[0]                = (my_suffix_1)&0xff;
   pkt->payload[1]                = (my_suffix_2)&0xff;

   pkt->payload[2]                = 0x20;
   
   pkt->payload[3]                = (sensor_read_solar>>8)&0xff;
   pkt->payload[4]                = (sensor_read_solar>>0)&0xff;

   pkt->payload[5]				    = 0x20;

   pkt->payload[6]                = (sensor_read_photosynthetic >> 8) & 0xff;
   pkt->payload[7]                = (sensor_read_photosynthetic >> 0) & 0xff;

   pkt->payload[8]                = 0x20;

   pkt->payload[9]                = (sensor_read_temperature >> 8) & 0xff;
   pkt->payload[10]                = (sensor_read_temperature >> 0) & 0xff;

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
   packetfunctions_reserveHeaderSize(pkt,sizeof(cexample_path0)-1);
   memcpy(&pkt->payload[0],cexample_path0,sizeof(cexample_path0)-1);
   packetfunctions_reserveHeaderSize(pkt,1);
   pkt->payload[0]                = ((COAP_OPTION_NUM_URIPATH) << 4) | (sizeof(cexample_path0)-1);
   
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
      &cexample_vars.desc
   );
   
   // avoid overflowing the queue if fails
   if (outcome==E_FAIL) {
      openqueue_freePacketBuffer(pkt);
   }
   
   return;
}

void cexample_sendDone(OpenQueueEntry_t* msg, owerror_t error) {
   openqueue_freePacketBuffer(msg);
}
