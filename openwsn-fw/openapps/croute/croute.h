#ifndef __CROUTE_H
#define __CROUTE_H

/**
\addtogroup AppUdp
\{
\addtogroup croute
\{
*/
#include "opencoap.h"
//=========================== define ==========================================

//=========================== typedef =========================================

typedef struct {
   coap_resource_desc_t desc;
} croute_vars_t;

//=========================== variables =======================================

//=========================== prototypes ======================================

void croute_init(void);

/**
\}
\}
*/

#endif
