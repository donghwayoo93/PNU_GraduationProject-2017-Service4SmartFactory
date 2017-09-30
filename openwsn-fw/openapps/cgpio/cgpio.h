#ifndef __CGPIO_H
#define __CGPIO_H

/**
\addtogroup AppUdp
\{
\addtogroup cexample
\{
*/
#include "opencoap.h"

//=========================== define ==========================================

//=========================== typedef =========================================


//=========================== variables ======================================
typedef struct {
   coap_resource_desc_t desc;
} cgpio_vars_t;

//=========================== prototypes ======================================

void cgpio_init(void);



/**
\}
\}
*/

#endif