#ifndef __USERAPP_H
#define __USERAPP_H

/**
\addtogroup AppUdp
\{
\addtogroup cexample
\{
*/
#include "opencoap.h"
//=========================== define ==========================================

//=========================== typedef =========================================

typedef struct {
   coap_resource_desc_t desc;
   opentimer_id_t       timerId;
} userapp_vars_t;

//=========================== variables =======================================

//=========================== prototypes ======================================

void userapp_init(void);

/**
\}
\}
*/

#endif
