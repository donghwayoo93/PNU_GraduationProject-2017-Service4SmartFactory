#include "opendefs.h"
#include "cgpio.h"
#include "opencoap.h"
#include "packetfunctions.h"
#include "gpios.h"
#include "openqueue.h"
#include "openserial.h"
#include "opentimers.h"
#include "scheduler.h"
#include "IEEE802154E.h"

#include "idmanager.h"
#include "adc_sensor.h"
#include "sensors.h"

//=========================== defines =========================================

#define ON  '1'
#define OFF '0'
#define TOG '2'

#define CGPIOPERIOD  10000
#define PAYLOADLEN      14

const uint8_t cgpio_path0[] = "gpio";

//=========================== variables =======================================

cgpio_vars_t cgpio_vars;

//=========================== prototypes ======================================

owerror_t cgpio_receive(
   OpenQueueEntry_t* msg,
   coap_header_iht*  coap_header,
   coap_option_iht*  coap_options
);

void    cgpio_timer_cb(opentimer_id_t id);
void    cgpio_task_cb(void);

void     cgpio_sendDone(
   OpenQueueEntry_t* msg,
   owerror_t error
);

//=========================== public ==========================================

void cgpio_init() {
   
   // prepare the resource descriptor for the /gpio path
   cgpio_vars.desc.path0len            = sizeof(cgpio_path0)-1;
   cgpio_vars.desc.path0val            = (uint8_t*)(&cgpio_path0);
   cgpio_vars.desc.path1len            = 0;
   cgpio_vars.desc.path1val            = NULL;
   cgpio_vars.desc.componentID         = COMPONENT_CGPIO;
   cgpio_vars.desc.discoverable        = TRUE;
   cgpio_vars.desc.callbackRx          = &cgpio_receive;
   cgpio_vars.desc.callbackSendDone    = &cgpio_sendDone;
   
   sensors_init();
   // register with the CoAP module
   opencoap_register(&cgpio_vars.desc);
   cgpio_vars.timerId = opentimers_start(CGPIOPERIOD,
                                          TIMER_PERIODIC,TIME_MS,
                                          cgpio_timer_cb);
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
         packetfunctions_reserveHeaderSize(msg,4);
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
         } else if (msg->payload[0]==OFF){
            gpios_GIO0_off();
         }

         if (msg->payload[1]==ON) {
            gpios_GIO1_on();
         } else if (msg->payload[1]==TOG) {
            gpios_GIO1_toggle();
         } else if (msg->payload[1]==OFF){
            gpios_GIO1_off();
         }
         
         // reset packet payload
         msg->payload                     = &(msg->packet[127]);
         msg->length                      = 0;

         packetfunctions_reserveHeaderSize(msg, 3);
         msg->payload[0] = COAP_PAYLOAD_MARKER;

         if (gpios_GIO0_isOn()==1) {
            msg->payload[1]               = ON;
         } else {
            msg->payload[1]               = OFF;
         }

         if (gpios_GIO1_isOn()==1) {
            msg->payload[2]               = ON;
         } else {
            msg->payload[2]               = OFF;
         }
         
         // set the CoAP header
         coap_header->Code                = COAP_CODE_RESP_CONTENT;
         
         outcome                          = E_SUCCESS;
         break;
         
      default:
         outcome                          = E_FAIL;
         break;
   }
   
   return outcome;
}

//timer fired, but we don't want to execute task in ISR mode
//instead, push task to scheduler with COAP priority, and let scheduler take care of it
void cgpio_timer_cb(opentimer_id_t id){
   scheduler_push_task(cgpio_task_cb,TASKPRIO_COAP);
}

void cgpio_task_cb() {
   OpenQueueEntry_t*    pkt;
   owerror_t            outcome;
   uint8_t              my_suffix_1, my_suffix_2;
   uint8_t              i;
   
   uint16_t             sensor_read_solar          = 0; // visible range                    (560 nm)
   uint16_t             sensor_read_photosynthetic = 0; // visible range and infrared range (960 nm)
   uint8_t              gpio_read_motor            = 0;
   uint8_t              gpio_read_syn_led          = 0;
   
   // don't run if not synch
   if (ieee154e_isSynch() == FALSE) return;
   
   // don't run on dagroot
   if (idmanager_getIsDAGroot()) {
      opentimers_stop(cgpio_vars.timerId);
      return;
   }

   sensor_read_solar          = adc_sens_read_total_solar();
   sensor_read_photosynthetic = adc_sens_read_photosynthetic();
   if(gpios_GIO0_isOn() == 1)
      gpio_read_motor         = 1;
   else
      gpio_read_motor         = 0;

   if(gpios_GIO1_isOn() == 1)
      gpio_read_syn_led       = 1;
   else
      gpio_read_syn_led       = 0;     

   my_suffix_1 = idmanager_getMyID(ADDR_64B)->addr_64b[6];
   my_suffix_2 = idmanager_getMyID(ADDR_64B)->addr_64b[7];

   // create a CoAP RD packet
   pkt = openqueue_getFreePacketBuffer(COMPONENT_CGPIO);
   if (pkt==NULL) {
      openserial_printError(
         COMPONENT_CGPIO,
         ERR_NO_FREE_PACKET_BUFFER,
         (errorparameter_t)0,
         (errorparameter_t)0
      );
      openqueue_freePacketBuffer(pkt);
      return;
   }
   // take ownership over that packet
   pkt->creator                   = COMPONENT_CGPIO;
   pkt->owner                     = COMPONENT_CGPIO;
   // CoAP payload
   packetfunctions_reserveHeaderSize(pkt,PAYLOADLEN);
   for (i=0;i<PAYLOADLEN;i++) {
      pkt->payload[i]             = i;
   }

   pkt->payload[0]                = 'S';
   pkt->payload[1]                = 0x20;
   pkt->payload[2]                = (my_suffix_1)&0xff;
   pkt->payload[3]                = (my_suffix_2)&0xff;
   pkt->payload[4]                = 0x20;
   pkt->payload[5]                = (sensor_read_solar>>8)&0xff;
   pkt->payload[6]                = (sensor_read_solar>>0)&0xff;
   pkt->payload[7]                = 0x20;
   pkt->payload[8]                = (sensor_read_photosynthetic >> 8) & 0xff;
   pkt->payload[9]                = (sensor_read_photosynthetic >> 0) & 0xff;
   pkt->payload[10]               = 0x20;
   pkt->payload[11]               = gpio_read_motor;
   pkt->payload[12]               = 0x20;
   pkt->payload[13]               = gpio_read_syn_led;


   packetfunctions_reserveHeaderSize(pkt,1);
   pkt->payload[0] = COAP_PAYLOAD_MARKER;
   
   // content-type option
   packetfunctions_reserveHeaderSize(pkt,2);
   pkt->payload[0]                = (COAP_OPTION_NUM_CONTENTFORMAT - COAP_OPTION_NUM_URIPATH) << 4
                                    | 1;
   pkt->payload[1]                = COAP_MEDTYPE_APPOCTETSTREAM;
   // location-path option
   packetfunctions_reserveHeaderSize(pkt,sizeof(cgpio_path0)-1);
   memcpy(&pkt->payload[0],cgpio_path0,sizeof(cgpio_path0)-1);
   packetfunctions_reserveHeaderSize(pkt,1);
   pkt->payload[0]                = ((COAP_OPTION_NUM_URIPATH) << 4) | (sizeof(cgpio_path0)-1);
   
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
      &cgpio_vars.desc
   );
   
   // avoid overflowing the queue if fails
   if (outcome==E_FAIL) {
      openqueue_freePacketBuffer(pkt);
   }
   
   return;
}


void cgpio_sendDone(OpenQueueEntry_t* msg, owerror_t error) {
   openqueue_freePacketBuffer(msg);
}
