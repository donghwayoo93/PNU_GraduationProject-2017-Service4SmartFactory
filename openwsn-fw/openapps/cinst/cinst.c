/**
\brief An example CoAP application.
*/

#include "opendefs.h"
#include "cinst.h"
#include "opencoap.h"
#include "opentimers.h"
#include "openqueue.h"
#include "packetfunctions.h"
#include "openserial.h"
#include "openrandom.h"
#include "scheduler.h"
#include "openserial.h"

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


const uint8_t cinst_path0[] = "inst";

//=========================== variables =======================================

cinst_vars_t cinst_vars;

//=========================== prototypes ======================================

owerror_t cinst_receive(OpenQueueEntry_t* msg,
                    coap_header_iht*  coap_header,
                    coap_option_iht*  coap_options);
void    cinst_timer_cb(opentimer_id_t id);
void    cinst_task_cb(void);
void    cinst_sendDone(OpenQueueEntry_t* msg,
                       owerror_t error);

//=========================== public ==========================================

void cinst_init() {
   
   // prepare the resource descriptor for the /inst path
   cinst_vars.desc.path0len             = sizeof(cinst_path0)-1;
   cinst_vars.desc.path0val             = (uint8_t*)(&cinst_path0);
   cinst_vars.desc.path1len             = 0;
   cinst_vars.desc.path1val             = NULL;
   cinst_vars.desc.componentID          = COMPONENT_CINST;
   cinst_vars.desc.discoverable         = TRUE;
   cinst_vars.desc.callbackRx           = &cinst_receive;
   cinst_vars.desc.callbackSendDone     = &cinst_sendDone;

   /*
		init sensors
   */
   //sensors_init();
   
   
   opencoap_register(&cinst_vars.desc);
}

//=========================== private =========================================

owerror_t cinst_receive(OpenQueueEntry_t* msg,
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
    uint8_t i = 0, recv_len = 0;
    uint32_t new_Period = 0;

	switch (coap_header->Code) {
		case COAP_CODE_REQ_GET:
			msg->payload = &(msg->packet[127]);
			msg->length = 0;

			packetfunctions_reserveHeaderSize(msg, 55);
			msg->payload[0] = COAP_PAYLOAD_MARKER;
/*
			msg->payload[1] = 'e';
			msg->payload[2] = 'x';
			msg->payload[3] = ' ';
			msg->payload[4] = 'g';
			msg->payload[5] = 'e';
			msg->payload[6] = 't';
			msg->payload[7] = ' ';
*/
         for(i = 0; i < 55; i++){
            msg->payload[i+1] = i+65; 
         }
			
			coap_header->Code = COAP_CODE_RESP_CONTENT;

			outcome = E_SUCCESS;
			break;
      //------------------------------------------case GET
		case COAP_CODE_REQ_PUT:
         if(msg->l4_destination_port == WKP_UDP_COAP_ROUTE){    // Destination UDP Port #5683
            if((msg->payload[0] == DIO_PERIOD) &&
               (msg->payload[1] == CEXAMPLE_SEPERATOR) &&
               (msg->payload[3] == MARKER_END)) {               // SET DIO Period
               new_Period = (msg->payload[2] - 48);
               icmpv6rpl_setDIOPeriod(new_Period*10000);                 // void (uint32_t dioPeriod)
               PUT_flag = E_SUCCESS;
           		 }
            else if((msg->payload[0] == DAO_PERIOD) &&
               (msg->payload[1] == CEXAMPLE_SEPERATOR) &&
               (msg->payload[3] == MARKER_END)) {               // SET DAO Period
               new_Period = (msg->payload[2] - 48);
               icmpv6rpl_setDAOPeriod(new_Period*10000);                 // void (uint32_t daoPeriod)
               PUT_flag = E_SUCCESS;
            		}
            else{                                                       // Received Undefined VALUE
               PUT_flag = E_FAIL;
            		}

            msg->payload = &(msg->packet[127]);
            msg->length = 0;

   			if (PUT_flag == E_SUCCESS) {                                // Response with changed Value
   				packetfunctions_reserveHeaderSize(msg, 6);
   				msg->payload[0] = COAP_PAYLOAD_MARKER;

   				msg->payload[1] = new_Period + 48;
   				msg->payload[2] = ' ';
   				msg->payload[3] = 'p';
   				msg->payload[4] = 'u';
   				msg->payload[5] = 't';
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
        	 }
		else if(msg->l4_destination_port == WKP_UDP_COAP_INST){   // Destination UDP Port #5685
			openserial_printInst((uint8_t*)(msg->payload),msg->length);
			recv_len = msg->length;

            msg->payload = &(msg->packet[127]);
            msg->length = 0;
            packetfunctions_reserveHeaderSize(msg, 2);
	        msg->payload[0] = COAP_PAYLOAD_MARKER;
            msg->payload[1] = recv_len;
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

void cinst_sendDone(OpenQueueEntry_t* msg, owerror_t error) {
   openqueue_freePacketBuffer(msg);
}

void cinst_task_cb() {
   OpenQueueEntry_t*    pkt;
   owerror_t            outcome;
   uint8_t              my_suffix_1, my_suffix_2;
   uint8_t              i;
   uint8_t              input_buffer[54];
   uint8_t              numDataBytes;

   // don't run if not synch
   if (ieee154e_isSynch() == FALSE) return;
   
   // don't run on dagroot
   if (idmanager_getIsDAGroot()) {
      return;
   }

	numDataBytes = openserial_getInputBufferFilllevel();

	if(numDataBytes > 54 || numDataBytes == 0){
		openserial_printError(COMPONENT_CINST,
							  ERR_INPUTBUFFER_LENGTH,
							  (errorparameter_t)numDataBytes,
 							  (errorparameter_t)0);
		return;
	}

	openserial_getInputBuffer(&(input_buffer[0]), numDataBytes);


   // create a CoAP RD packet
   pkt = openqueue_getFreePacketBuffer(COMPONENT_CINST);
   if (pkt==NULL) {
      openserial_printError(
         COMPONENT_CINST,
         ERR_NO_FREE_PACKET_BUFFER,
         (errorparameter_t)0,
         (errorparameter_t)0
      );
      openqueue_freePacketBuffer(pkt);
      return;
   }

   // take ownership over that packet
   pkt->creator                   = COMPONENT_CINST;
   pkt->owner                     = COMPONENT_CINST;
   // CoAP payload
   packetfunctions_reserveHeaderSize(pkt,numDataBytes);
   for (i=0;i<numDataBytes;i++) {
      pkt->payload[i]             = i;
   	}
	
	memcpy(pkt->payload, &(input_buffer[0]), numDataBytes);

   packetfunctions_reserveHeaderSize(pkt,1);
   pkt->payload[0] = COAP_PAYLOAD_MARKER;
   
   // content-type option
   packetfunctions_reserveHeaderSize(pkt,2);
   pkt->payload[0]                = (COAP_OPTION_NUM_CONTENTFORMAT - COAP_OPTION_NUM_URIPATH) << 4
                                    | 1;
   pkt->payload[1]                = COAP_MEDTYPE_APPOCTETSTREAM;
   // location-path option
   packetfunctions_reserveHeaderSize(pkt,sizeof(cinst_path0)-1);
   memcpy(&pkt->payload[0],cinst_path0,sizeof(cinst_path0)-1);
   packetfunctions_reserveHeaderSize(pkt,1);
   pkt->payload[0]                = ((COAP_OPTION_NUM_URIPATH) << 4) | (sizeof(cinst_path0)-1);
   
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
   
   // send
   outcome = opencoap_send(
      pkt,
      COAP_TYPE_NON,
      COAP_CODE_REQ_PUT,
      1,
      &cinst_vars.desc
   );
   
   // avoid overflowing the queue if fails
   if (outcome==E_FAIL) {
      openqueue_freePacketBuffer(pkt);
   }
   
   return;
}


