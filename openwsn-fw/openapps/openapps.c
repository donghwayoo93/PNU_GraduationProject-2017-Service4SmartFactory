/**
\brief Applications running on top of the OpenWSN stack.

\author Thomas Watteyne <watteyne@eecs.berkeley.edu>, September 2014.
*/

#include "opendefs.h"

// CoAP
#include "c6t.h"
//#include "cinfo.h"
//#include "cleds.h"
//#include "cexample.h"
#include "cstorm.h"
#include "cwellknown.h"
#include "rrt.h"
#include "cgpio.h"
#include "croute.h"
// UDP
#include "uecho.h"
#include "uinject.h"

//=========================== variables =======================================

//=========================== prototypes ======================================

//=========================== public ==========================================

//=========================== private =========================================

void openapps_init(void) {
   // CoAP
   c6t_init();
   //cinfo_init();
   //cexample_init(); // add initial funtcion cexample
   croute_init()
   //cleds__init();
   cstorm_init();
   cwellknown_init();
   rrt_init();
   cgpio_init();
   // UDP
//   uecho_init();
}