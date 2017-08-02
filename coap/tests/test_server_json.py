import os
import signal
import sys
here = sys.path[0]
sys.path.insert(0, os.path.join(here,'..'))

import threading
from   coap   import    coap,                    \
                        coapResource,            \
                        coapDefines as d
#import logging_setup
import json

class testResource(coapResource.coapResource):
    
    def __init__(self):
        # initialize parent class
        coapResource.coapResource.__init__(
            self,
            path = 'ex',
        )
    
    def GET(self,options=[]):
        
        print 'GET received'
        
        respCode        = d.COAP_RC_2_05_CONTENT
        respOptions     = []
        respPayload     = [ord(b) for b in 'dummy response']
        
        return (respCode,respOptions,respPayload)

    def PUT(self,srcip, options=[],payload=None):

        payload_str  = ''
        json_str     = ''
        sensor_value = ''

        for i in payload:
            str_i = str(i)
            if(str_i == '32'):
                payload_str += ' '
            elif(str_i == '0'):
                payload_str += ''
            else:
                payload_str += str_i

        sensor_arr = payload_str.split('  ')

        sensor_value = {
                        'ipaddr' : str(srcip),
                        'solar' : str(sensor_arr[0]),
                        'photosynthetic' : str(sensor_arr[1]),
                        'temperature' : str(sensor_arr[2]), 
                        'humidity' : str(sensor_arr[3])
                        }

        json_str = json.dumps(sensor_value)

        print json_str

        #print 'PUT RECEIVED, payload :' + asciipayload

        respCode = d.COAP_RC_2_05_CONTENT
        respOptions = []
        respPayload = [ord(b) for b in self.listmotes()]


        return (respCode, respOptions, respPayload)

# open
c = coap.coap()

# install resource
c.addResource(testResource())

for t in threading.enumerate():
    print t.name

# let the server run
raw_input('\n\nServer running. Press Enter to close.\n\n')

# close
c.close()
os.kill(os.getpid(), signal.SIGTERM)