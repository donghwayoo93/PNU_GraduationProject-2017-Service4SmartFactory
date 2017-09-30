#include "opendefs.h"
#include "cgpio.h"
#include "opentimers.h"
#include "gpio.h"
#include "leds.h"
#include "scheduler.h"
#include "icmpv6rpl.h"
#include "opencoap.h"
#include "packetfunctions.h"
#include "openqueue.h"

//=========================== defines =========================================

/// inter-packet period (in ms)
#define CGPIOPERIOD  1000

const uint8_t cgpio_path0[] = "gpio";

//=========================== variables =======================================

cgpio_vars_t cgpio_vars;


//=========================== prototypes ======================================

owerror_t cgpio_receive(OpenQueueEntry_t* msg,
                    coap_header_iht*  coap_header,
                    coap_option_iht*  coap_options);

void    cgpio_timer_cb(opentimer_id_t id);
void    cgpio_task_cb(void);
void    cgpio_sendDone(OpenQueueEntry_t* msg,
                        owerror_t error);


opentimer_id_t GpioTimerId = 0;

//=========================== public ==========================================

void cgpio_init() {

   if (idmanager_getIsDAGroot() == TRUE) return;

   // prepare the resource descriptor for the /i path
   cgpio_vars.desc.path0len = sizeof(cgpio_path0) - 1;
   cgpio_vars.desc.path0val = (uint8_t*)(&cgpio_path0);
   cgpio_vars.desc.path1len = 0;
   cgpio_vars.desc.path1val = NULL;
   cgpio_vars.desc.componentID = COMPONENT_CGPIO;
   cgpio_vars.desc.discoverable = TRUE;
   cgpio_vars.desc.callbackRx = &cgpio_receive;
   cgpio_vars.desc.callbackSendDone = &cgpio_sendDone;
   
   GpioTimerId  = opentimers_start(CGPIOPERIOD,
                                       TIMER_PERIODIC,TIME_MS,
                                       cgpio_timer_cb);

   opencoap_register(&cgpio_vars.desc);
}

//=========================== private =========================================

//timer fired, but we don't want to execute task in ISR mode
//instead, push task to scheduler with COAP priority, and let scheduler take care of it
void cgpio_timer_cb(opentimer_id_t id){
   scheduler_push_task(cgpio_task_cb,TASKPRIO_BUTTON);
}

void cgpio_task_cb() {
   if(gpio_userIntr_get() == 0) {
      //leds_error_on();
   }
   else{
   	  //leds_error_off();
   	  //icmpv6rpl_killPreferredParent();
   	  //gpio_userIntr_set();
   }
}


owerror_t cgpio_receive(OpenQueueEntry_t* msg,
                      coap_header_iht* coap_header,
                      coap_option_iht* coap_options) {

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

         for(i = 0; i < 55; i++){
            msg->payload[i+1] = i+65; 
         }
         
         coap_header->Code = COAP_CODE_RESP_CONTENT;

         outcome = E_SUCCESS;
         break;
      //------------------------------------------case GET
      case COAP_CODE_REQ_PUT:
         if(msg->l4_destination_port == WKP_UDP_COAP_ROUTE){    // Destination UDP Port #5683

         }
         else if(msg->l4_destination_port == WKP_UDP_COAP_INST){   // Destination UDP Port #5685
            openserial_printInst((uint8_t*)(msg->payload),msg->length);
            recv_len = msg->length;
            leds_error_toggle();

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

void cgpio_sendDone(OpenQueueEntry_t* msg, owerror_t error) {
   openqueue_freePacketBuffer(msg);
}