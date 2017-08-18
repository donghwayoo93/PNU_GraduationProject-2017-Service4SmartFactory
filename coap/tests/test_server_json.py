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

class SENSORResource(coapResource.coapResource):
    
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

    def PUT(self, srcIP, options=[],payload=None):
        # In case Server Receives Sensor Value Packet
        if(unichr(payload[0]) == 'S'):
            payload = payload[2:]
            payload_str   = ''
            json_str      = ''
            sensor_value  = ''

            ipaddr = srcIP.split(':')
            ip_suffix = ipaddr[5]

            print str(ip_suffix)

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

        # In case Server Receives Instruction Packet
        elif(unichr(payload[0]) == 'I'):
            print 'error : Sensor coap server received Instruction Packet\n'
            print 'This case SHOULD NOT happen\n'

        respCode = d.COAP_RC_NONE
        respOptions = []
        respPayload = []
        return (respCode, respOptions, respPayload)

class INSTResource(coapResource.coapResource):
    SYN_dict = {
                'SYN'     : 0,
                'SYN+ACK' : 0,
                'ACK'     : 0
    }

    FIN_dict = {
                'FIN_1' : 0,
                'FIN_2' : 0,
                'ACK_1' : 0,
                'ACK_2' : 0
    }

    SYN      = 0
    FIN      = 0
    ACK      = 0
    FRAG_1   = 0
    FRAG_N   = 0

    index    = 0
    c        = ''
    
    def __init__(self, index):
        # initialize parent class
        coapResource.coapResource.__init__(
            self,
            path = 'ex',
        )
        self.SYN      = 128
        self.FIN      = 64
        self.ACK      = 32
        self.FRAG_1   = 24
        self.FRAG_N   = 28
        self.index    = index

    def sendInstructionData(self):
        # read data from DB
        data_str       = ''
        data_size      = len(data_str)
        data_offset    = 1
        link           = 'coap://[bbbb::2]/data'
        payload_str    = 'I'

        tag_sem.acquire()
        data_tag += 1
        tag_sem.release()

        if(self.index == 5686):
            self.c = c_5686
        elif(self.index == 5687):
            self.c = c_5687
        elif(self.index == 5688):
            self.c = c_5688

        payload_str += str(chr(self.FRAG_1)) + str(chr(data_size)) + str(chr(data_tag))
        payload_str += # 읽어온 데이터

        self.c.PUT(
            link,
            payload=[ord(b) for b in payload_str]
        )

        payload_str = 'I'

        while(data_str != ''):

            payload_str += str(chr(self.FRAG_N)) + str(chr(data_size)) + str(chr(data_tag)) + str(chr(data_offset))
            payload_str += # 읽어온 데이터

            self.c.PUT(
                link,
                payload=[ord(b) for b in payload_str]
            )
            data_offset += 1


    def PUT(self, srcIP, options=[],payload=None):
        if(unichr(payload[0]) == 'I'):
            ipaddr = srcIP.split(':')
            ip_suffix = ipaddr[5]

            payload = payload[1:]

            # Server Received SYN pkt from Client
            # Response with SYN+ACK pkt
            if((payload[0] == self.SYN) &
               (self.SYN_dict['SYN'] == 0)):
                self.SYN_dict['SYN']     = 1
                self.SYN_dict['SYN+ACK'] = 1

                respCode = d.COAP_RC_2_05_CONTENT
                respOptions = []
                respPayload = [ord(b) for b in 'I'+str(chr(self.SYN + self.ACK))]

                return (respCode, respOptions, respPayload)

            # Server Received ACK pkt from Client
            # Server sends data to Client
            elif((payload[0] == self.ACK) &
                 (self.SYN_dict['ACK'] == 0)):
                self.SYN_dict['ACK'] = 1
                self.sendInstructionData()


                


        elif(unichr(payload[0]) == 'S'):
            print 'error : Instruction coap server received Sensor Packet\n'
            print 'This case SHOULD NOT happen\n'

        respCode = d.COAP_RC_2_05_CONTENT
        respOptions = []
        respPayload = []

        return (respCode, respOptions, respPayload)

class BindResource(coapResource.coapResource):
    alloc_index    = ''
    appendix       = 5686
    alloc_FLAG     = False

    def __init__(self):
        coapResource.coapResource.__init__(
            self,
            path = 'bind',
        )

    def GET(self,options=[]):
        print '[BIND] GET received\n'

        port_sem.acquire()

        for i in range(len(ports)):
            if(ports[i] == 0):
                self.alloc_index = i
                self.alloc_FLAG = True
                break;
            elif((ports[i] == 1) & (i == 2)):
                print 'error : ALL ports are allocated\n'
                self.alloc_FLAG = False
                break;

        ports[self.alloc_index] = 1

        port_sem.release()
        
        respCode        = d.COAP_RC_2_05_CONTENT
        respOptions     = []

        if(self.alloc_FLAG == True):
            respPayload     = [ord(b) for b in str(alloc_index + appendix)]
            self.alloc_FLAG = False
            t = ThreadClass(alloc_index + appendix)
            t.start()
        else:
            respPayload     = [ord(b) for b in 'error']    
        
        return (respCode,respOptions,respPayload)


class ThreadClass(threading.Thread):
    def __init__(self, index):
        threading.Thread.__init__(self)
        self.thread_index = index

    def run(self):
        if(self.thread_index == 1):
            # c = coap.coap()
            # c.addResource(testResource())
            # c_ROUTE.addResource(testResource())
            print 'ROUTE  coap server created with PORT : ' + str(5683) + '\n'

        elif(self.thread_index == 2):
            
            IPC_HOST = 'localhost'
            IPC_PORT = 25800

            print ' UDP server created with HOST : ' + IPC_HOST + ' PORT : ' + str(IPC_PORT) + '\n'

            server = SocketServer.UDPServer((IPC_HOST, IPC_PORT), UDP_IPC)
            server.serve_forever()

        elif(self.thread_index == 3):
            c_SENSOR.addResource(SENSORResource())

            print 'SENSOR coap server created with PORT : ' + str(5684) + '\n'

        elif(self.thread_index == 4):
            c_Bind.addResource(BindResource())

            print 'BIND   coap server created with PORT : ' + str(5685) + '\n'     

        elif(self.thread_index == 5):
            raw_input('\n\nServer running. Press Enter to close.\n\n')

            c_ROUTE.close()
            c_SENSOR.close()
            c_INST.close()

            os.kill(os.getpid(), signal.SIGTERM)

        elif(self.thread_index == 5686):
            c_5686 = coap.coap(udpPort=self.thread_index)
            c_5686.addResource(INSTResource(5686))

        elif(self.thread_index == 5687):
            c_5687 = coap.coap(udpPort=self.thread_index)
            c_5687.addResource(INSTResource(5687))

        elif(self.thread_index == 5688):
            c_5688 = coap.coap(udpPort=self.thread_index)
            c_5688.addResource(INSTResource(5688))



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

        response = c_ROUTE.PUT(
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

        response = c_ROUTE.PUT(
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
server       = 0
port_sem     = threading.Semaphore(1)
tag_sem      = threading.Semaphore(1)
ports        = [0, 0, 0]

c_ROUTE  = coap.coap(udpPort=5683) # Working checked
c_SENSOR = coap.coap(udpPort=5684)
c_Bind   = coap.coap(udpPort=5685) 

c_5686   = ''
c_5687   = ''
c_5688   = ''

data_tag = 0

if __name__ == "__main__":

    for i in range(5):
        t = ThreadClass(i+1)
        t.start()