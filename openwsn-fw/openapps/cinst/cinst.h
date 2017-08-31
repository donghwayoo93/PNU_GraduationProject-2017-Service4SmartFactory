#ifndef __CINST_H
#define __CISNT_H

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
} cinst_vars_t;

//=========================== variables =======================================

//=========================== prototypes ======================================

void cinst_init(void);
void cinst_task_cb();
/**
\}
\}
*/

#endif
