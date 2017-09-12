#include "opendefs.h"
#include "cgpio.h"
#include "opencoap.h"
#include "packetfunctions.h"
#include "gpios.h"
#include "openqueue.h"


#define ON  '1'
#define OFF '0'
#define TOG '2'

//=========================== variables =======================================

cgpio_vars_t cgpio_vars;

const uint8_t cgpio_path0[] = "gpio";

//=========================== prototypes ======================================

owerror_t cgpio_receive(
   OpenQueueEntry_t* msg,
   coap_header_iht*  coap_header,
   coap_option_iht*  coap_options
);
void     cgpio_sendDone(
   OpenQueueEntry_t* msg,
   owerror_t error
);

//=========================== public ==========================================

void cgpio_init() {
   
   // prepare the resource descriptor for the /l path
   cgpio_vars.desc.path0len            = sizeof(cgpio_path0)-1;
   cgpio_vars.desc.path0val            = (uint8_t*)(&cgpio_path0);
   cgpio_vars.desc.path1len            = 0;
   cgpio_vars.desc.path1val            = NULL;
   cgpio_vars.desc.componentID         = COMPONENT_CGPIO;
   cgpio_vars.desc.discoverable        = TRUE;
   cgpio_vars.desc.callbackRx          = &cgpio_receive;
   cgpio_vars.desc.callbackSendDone    = &cgpio_sendDone;
   
   // register with the CoAP module
   opencoap_register(&cgpio_vars.desc);
}

//=========================== private =========================================

owerror_t cgpio_receive(
      OpenQueueEntry_t* msg,
      coap_header_iht*  coap_header,
      coap_option_iht*  coap_options
   ) {
   owerror_t outcome;
   
   switch (coap_header->Code) {
      case COAP_CODE_REQ_GET:
         // reset packet payload
         msg->payload                     = &(msg->packet[127]);
         msg->length                      = 0;
         
         // add CoAP payload
         packetfunctions_reserveHeaderSize(msg,7);
         msg->payload[0]                  = COAP_PAYLOAD_MARKER;

         if (gpios_GIO0_isOn()==1) {
            msg->payload[1]               = ON;
         } else {
            msg->payload[1]               = OFF;
         }

         msg->payload[2]                  = ' ';

         if (gpios_GIO1_isOn()==1) {
            msg->payload[3]               = ON;
         } else {
            msg->payload[3]               = OFF;
         }

         msg->payload[4]                  = ' ';

         if (/*gpios_GIO2_isOn()*/1==1) {
            msg->payload[5]               = ON;
         } else {
            msg->payload[5]               = OFF;
         }

         msg->payload[5]                  = ' ';

         if (/*gpios_GIO3_isOn()*/1==1) {
            msg->payload[6]               = ON;
         } else {
            msg->payload[6]               = OFF;
         }
            
         // set the CoAP header
         coap_header->Code                = COAP_CODE_RESP_CONTENT;   
         outcome                          = E_SUCCESS;
         break;
      
      case COAP_CODE_REQ_PUT:
      
         // change the GPIO's state
         if (msg->payload[0]==ON) {
            gpios_GIO0_on();
         } else if (msg->payload[0]==TOG) {
            gpios_GIO0_toggle();
         } else {
            gpios_GIO0_off();
         }

         if (msg->payload[1]==ON) {
            gpios_GIO1_on();
         } else if (msg->payload[1]==TOG) {
            gpios_GIO1_toggle();
         } else {
            gpios_GIO1_off();
         }
/*
         if (msg->payload[2]==ON) {
            gpios_GIO2_on();
         } else if (msg->payload[2]==TOG) {
            gpios_GIO2_toggle();
         } else {
            gpios_GIO2_off();
         }

         if (msg->payload[3]==ON) {
            gpios_GIO3_on();
         } else if (msg->payload[3]==TOG) {
            gpios_GIO3_toggle();
         } else {
            gpios_GIO3_off();
         }
         */
         
         // reset packet payload
         msg->payload                     = &(msg->packet[127]);
         msg->length                      = 0;
         
         // set the CoAP header
         coap_header->Code                = COAP_CODE_RESP_CHANGED;
         
         outcome                          = E_SUCCESS;
         break;
         
      default:
         outcome                          = E_FAIL;
         break;
   }
   
   return outcome;
}

void cgpio_sendDone(OpenQueueEntry_t* msg, owerror_t error) {
   openqueue_freePacketBuffer(msg);
}
