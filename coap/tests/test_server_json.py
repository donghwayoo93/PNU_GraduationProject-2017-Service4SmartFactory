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
import SocketServer

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

    def PUT(self,options=[],payload=None):

        payload_str   = ''
        json_str      = ''
        sensor_value  = ''

        my_suffix_1 = format(payload[0], 'x')
        my_suffix_2 = format(payload[1], 'x')

        if(len(my_suffix_1) == 1):
            my_suffix_1 = '0' + my_suffix_1
        if(len(my_suffix_2) == 1):
            my_suffix_2 = '0' + my_suffix_2

        for i in payload:
            str_i = str(i)
            if(str_i == '32'):
                payload_str += ' '
            elif(str_i == '0'):
                payload_str += ''
            else:
                payload_str += str_i

        sensor_arr = payload_str.split(' ')
        sensor_arr[0] = str(my_suffix_1) + str(my_suffix_2)

        sensor_value = {
                        'ipaddr' : str(sensor_arr[0]),
                        'solar' : str(sensor_arr[1]),
                        'photosynthetic' : str(sensor_arr[2]),
                        'temperature' : str(sensor_arr[3]), 
                        'humidity' : str(sensor_arr[4])
                        }

        json_str = json.dumps(sensor_value)

        print json_str

        #print 'PUT RECEIVED, payload :' + asciipayload

        respCode = d.COAP_RC_NONE
        respOptions = []
        respPayload = []
        # respPayload = [ord(b) for b in self.listmotes()]

        return (respCode, respOptions, respPayload)


class ThreadClass(threading.Thread):
    def __init__(self, index):
        threading.Thread.__init__(self)
        self.thread_index = index

    def run(self):
        if(self.thread_index == 1):

            # c = coap.coap()
            c.addResource(testResource())

            print 'coap server created with PORT : ' + str(d.DEFAULT_UDP_PORT)

        elif(self.thread_index == 2):
            
            IPC_HOST = 'localhost'
            IPC_PORT = 25800

            print 'UDP server created with HOST : ' + IPC_HOST + ' PORT : ' + str(IPC_PORT)

            server = SocketServer.UDPServer((IPC_HOST, IPC_PORT), UDP_IPC)
            server.serve_forever()

        elif(self.thread_index == 3):
            raw_input('\n\nServer running. Press Enter to close.\n\n')
            c.close()
            os.kill(os.getpid(), signal.SIGTERM)


class UDP_IPC(SocketServer.BaseRequestHandler):
    def handle(self):
        data = self.request[0]
        socket = self.request[1]

        print data

        dict = json.loads(data)

        pkt_type = dict['type']
        src_addr = dict['src_addr']
        dst_addr = dict['dst_addr']
        uri      = dict['uri']
        period   = dict['period']

        if(pkt_type == 'DIO'):
            self.DIO_Adjust(dst_addr, uri, period)
        elif(pkt_type == 'DAO'):
            self.DAO_Adjust(dst_addr, uri, period)
        else:
            print 'error : no match type for the handler'
            print 'pkt_type : ' + pkt_type

        socket.sendto(data.upper(), self.client_address)

    def DIO_Adjust(self, Dest, uri, period):

        link        = 'coap://[bbbb::' + str(Dest) + ']/' + str(uri)
        payload_str = '1=' + str(period) + '!'

        response = c.PUT(
                link,
                payload=[ord(b) for b in payload_str]
        )

        print_str = ''
        for r in response:
            print_str += chr(r)
        
        print 'response : ' + print_str

    def DAO_Adjust(self, Dest, uri, period):

        link        = 'coap://[bbbb::' + str(Dest) + ']/' + str(uri)
        payload_str = '2=' + str(period) + '!'

        response = c.PUT(
                link,
                payload=[ord(b) for b in payload_str]
        )

        print_str = ''
        for r in response:
            print_str += chr(r)
        
        print 'response : ' + print_str

# open


# c = coap.coap()

# install resource
# c.addResource(testResource())

# for t in threading.enumerate():
#     print t.name

# let the server run
# raw_input('\n\nServer running. Press Enter to close.\n\n')


# close
# c.close()
# os.kill(os.getpid(), signal.SIGTERM)
thread_index = 0
c            = coap.coap()
server       = 0

if __name__ == "__main__":

    for i in range(3):
        t = ThreadClass(i+1)
        t.start()