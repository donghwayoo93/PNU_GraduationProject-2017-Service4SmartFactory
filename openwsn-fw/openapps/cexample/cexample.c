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
#include "adc_sensor.h"
#include "sensors.h"
//#include "sht11.h"


//=========================== defines =========================================

/// inter-packet period (in ms)
#define CEXAMPLEPERIOD  10000
#define PAYLOADLEN      10

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
   sensors_init();
   
   opencoap_register(&cexample_vars.desc);
   cexample_vars.timerId    = opentimers_start(CEXAMPLEPERIOD,
                                                TIMER_PERIODIC,TIME_MS,
                                                cexample_timer_cb);
}

//=========================== private =========================================

owerror_t cexample_receive(OpenQueueEntry_t* msg,
                      coap_header_iht* coap_header,
                      coap_option_iht* coap_options) {

	owerror_t outcome;
	uint8_t PUT_flag = E_FAIL;
   uint8_t i = 0, new_Period_upper = 0, new_Period_lower = 0;
   uint8_t changed_type = 'N';

	switch (coap_header->Code) {
		case COAP_CODE_REQ_GET:
			msg->payload = &(msg->packet[127]);
			msg->length = 0;

			packetfunctions_reserveHeaderSize(msg, 55);
			msg->payload[0] = COAP_PAYLOAD_MARKER;

         for(i = 0; i < 55; i++){
            msg->payload[i+1] = i+65; 
         }
			
			coap_header->Code = COAP_CODE_RESP_CONTENT;

			outcome = E_SUCCESS;
			break;
      //------------------------------------------case GET
		case COAP_CODE_REQ_PUT:
         if(msg->l4_destination_port == WKP_UDP_COAP_ROUTE){    // Destination UDP Port #5683
            /* DIO & DAO PERIOD ADJUSTMENT PKT FORMAT */
            /////////////////////////////////////////////////////////////////////////
            //      0      /      1      /      2      /      3      /      4      //
            //=====================================================================//
            // PERIOD TYPE /  SEPERATOR  /PERIOD_UPPER /PERIOD_LOWER /  MARKER_END //
            /////////////////////////////////////////////////////////////////////////
            if((msg->payload[0] == DIO_PERIOD) &&
               (msg->payload[1] == CEXAMPLE_SEPERATOR) &&
               (msg->payload[4] == MARKER_END)) {                       // SET DIO Period
               new_Period_upper = (msg->payload[2] - 48);
               new_Period_lower = (msg->payload[3] - 48);
               icmpv6rpl_setDIOPeriod(((new_Period_upper * 10) + new_Period_lower) * 1000);                 // void (uint32_t dioPeriod)
               changed_type = 'I';
               PUT_flag = E_SUCCESS;
            }
            else if((msg->payload[0] == DAO_PERIOD) &&
               (msg->payload[1] == CEXAMPLE_SEPERATOR) &&
               (msg->payload[4] == MARKER_END)) {                       // SET DAO Period
               new_Period_upper = (msg->payload[2] - 48);
               new_Period_lower = (msg->payload[3] - 48);
               icmpv6rpl_setDAOPeriod(((new_Period_upper * 10) + new_Period_lower) * 1000);                 // void (uint32_t daoPeriod)
               changed_type = 'A';
               PUT_flag = E_SUCCESS;
            }
            else{                                                       // Received Undefined VALUE
               PUT_flag = E_FAIL;
            }

            msg->payload = &(msg->packet[127]);
            msg->length = 0;

   			if (PUT_flag == E_SUCCESS) {                                // Response with changed Value
   				packetfunctions_reserveHeaderSize(msg, 11);
   				msg->payload[0] = COAP_PAYLOAD_MARKER;

               msg->payload[1]  = 'D';
               msg->payload[2]  = changed_type;
               msg->payload[3]  = 'O';
               msg->payload[4]  = ' ';
   				msg->payload[5]  = new_Period_upper + 48;
               msg->payload[6]  = new_Period_lower + 48;
   				msg->payload[7]  = ' ';
   				msg->payload[8]  = 'P';
   				msg->payload[9]  = 'U';
   				msg->payload[10] = 'T';
   			}
            else if(PUT_flag == E_FAIL){                                // Response with error
               packetfunctions_reserveHeaderSize(msg, 8);
               msg->payload[0] = COAP_PAYLOAD_MARKER;

               msg->payload[1]  = 'D';
               msg->payload[2]  = changed_type;
               msg->payload[3]  = 'O';
               msg->payload[4]  = ' ';
               msg->payload[5]  = 'E';
               msg->payload[6]  = 'R';
               msg->payload[7]  = 'R';
            }
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
   
   uint16_t             sensor_read_solar          = 0; // visible range                    (560 nm)
   uint16_t             sensor_read_photosynthetic = 0; // visible range and infrared range (960 nm)
   //uint16_t             sensor_read_temperature	   = 0;
   //uint16_t             sensor_read_humidity	      = 0;
   
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
   sensor_read_solar		      = adc_sens_read_total_solar();
   sensor_read_photosynthetic = adc_sens_read_photosynthetic();
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

   pkt->payload[0]                = 'S';

   pkt->payload[1]                = 0x20;

   pkt->payload[2]                = (my_suffix_1)&0xff;
   pkt->payload[3]                = (my_suffix_2)&0xff;

   pkt->payload[4]                = 0x20;
   
   pkt->payload[5]                = (sensor_read_solar>>8)&0xff;
   pkt->payload[6]                = (sensor_read_solar>>0)&0xff;

   pkt->payload[7]				    = 0x20;

   pkt->payload[8]                = (sensor_read_photosynthetic >> 8) & 0xff;
   pkt->payload[9]                = (sensor_read_photosynthetic >> 0) & 0xff;

   //pkt->payload[10]                = 0x20;

   //pkt->payload[11]                = (sensor_read_temperature >> 8) & 0xff;
   //pkt->payload[12]                = (sensor_read_temperature >> 0) & 0xff;

   //pkt->payload[13]               = 0x20;

   //pkt->payload[14]               = (sensor_read_humidity >> 8) & 0xff;
   //pkt->payload[15]               = (sensor_read_humidity >> 0) & 0xff;



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
