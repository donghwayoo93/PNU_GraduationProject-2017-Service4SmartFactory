#include "opendefs.h"
#include "cgpio.h"
#include "opentimers.h"
#include "gpio.h"
#include "leds.h"
#include "scheduler.h"
#include "icmpv6rpl.h"

//=========================== defines =========================================

/// inter-packet period (in ms)
#define CGPIOPERIOD  1000

//=========================== variables =======================================


//=========================== prototypes ======================================

void    cgpio_timer_cb(opentimer_id_t id);
void    cgpio_task_cb(void);


opentimer_id_t GpioTimerId = 0;

//=========================== public ==========================================

void cgpio_init() {
   
   GpioTimerId  = opentimers_start(CGPIOPERIOD,
                                       TIMER_PERIODIC,TIME_MS,
                                       cgpio_timer_cb);
}

//=========================== private =========================================

//timer fired, but we don't want to execute task in ISR mode
//instead, push task to scheduler with COAP priority, and let scheduler take care of it
void cgpio_timer_cb(opentimer_id_t id){
   scheduler_push_task(cgpio_task_cb,TASKPRIO_BUTTON);
}

void cgpio_task_cb() {
   if(gpio_userIntr_get() == 0) {
      leds_error_on();
   }
   else{
   	  leds_error_off();
   	  icmpv6rpl_killPreferredParent();
   	  gpio_userIntr_set();
   }
}