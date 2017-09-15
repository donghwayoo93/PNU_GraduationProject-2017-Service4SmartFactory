#ifndef __CGPIO_H
#define __CGPIO_H

#include "opencoap.h"
//=========================== define ==========================================

//=========================== typedef =========================================

typedef struct {
   coap_resource_desc_t    desc;
   opentimer_id_t       timerId;
} cgpio_vars_t;

//=========================== variables =======================================

//=========================== prototypes ======================================

void cgpio_init(void);
/**
\}
\}
*/

#endif
