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
import time

THREAD_ROUTE          = 1
THREAD_DODAG_IPC      = 2
THREAD_SENSOR         = 3
THREAD_INST           = 4
THREAD_SYSKILL        = 5

CONNECTION_SYN        = False
CONNECTION_FIN        = False

CONN_SEMAPHORE        = threading.Semaphore(1)
COAP_5685_SEMAPHORE   = threading.Semaphore(1)


class SensorResource(coapResource.coapResource):
    
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


class InstResource(coapResource.coapResource):
    conn  = ''
    inst  = ''
    login = ''
    
    def __init__(self):
        # initialize parent class
        coapResource.coapResource.__init__(
            self,
            path = 'inst',
        )
        self.conn  = ConnectionClass()
        self.inst  = InstructionClass()
        self.login = LoginClass()

    def PUT(self, srcIP, options=[],payload=None):
        # received label = Connection
        if(unichr(payload[0]) == 'C'):
            # trim label 'C'
            payload = payload[1:]
            self.conn._handle(payload)

        elif(unichr(payload[0]) == 'L'):
            # trim label 'L'
            payload = payload[1:]
            login._login(payload)

        elif(unichr(payload[0]) == 'I'):
            ipaddr = srcIP.split(':')
            ip_suffix = ipaddr[5]
            self.inst._sendInstructionData()
            

        elif(unichr(payload[0]) == 'S'):
            print 'error : Instruction coap server received Sensor Packet\n'
            print 'This case SHOULD NOT happen\n'

        respCode = d.COAP_RC_2_05_CONTENT
        respOptions = []
        respPayload = []

        return (respCode, respOptions, respPayload)

class LoginClass():
    DB        = ''
    recv_id   = ''
    recv_pw   = ''
    send_name = ''
    send_auth = ''

    link      = ''

    def __init__(self):
        self.DB   = ''
        self.link = 'coap://[bbbb::2]:5685/inst'

    def _login(self, payload):
        dict = json.loads(payload)

        self.recv_id = dict['id']
        self.recv_pw = dict['pw']

        # make connection with DB
        # get worker's name and auth

        self.send_name = 'KIM'
        self.send_auth = 'H'

        self._sendResult()

    def _sendResult(self):
        resp = {
            'name' : str(self.send_name),
            'auth' : str(self.send_auth)
        }

        payload = json.dumps(resp)

        COAP_5685_SEMAPHORE.acquire()

        c_INST.PUT(
            self.link,
            payload=[ord(b) for b in payload]
        )

        COAP_5685_SEMAPHORE.release()


class InstructionClass():
    FRAG_1    = 0
    FRAG_N    = 0
    FIN       = 0
    link      = ''
    work_flag = ''

    def __init__(self):
        self.FRAG_1    = 24
        self.FRAG_N    = 28
        self.FIN       = 64
        self.link      = 'coap://[bbbb::2]:5685/inst'
        self.work_flag = False


    def _sendInstructionData(self):
        # read data from DB
        data_str         = 'Five drinks in on Friday night We only came to dry your eyes And get you out of your room'
        data_str        += ' Now this bar has closed its doors I found my hand is holding yours Do you wanna go home so soon '
        data_str        += 'Or maybe we shpuld take a ride Through the night and sing along to every song Thats on the radio In the back of a Taxi cab'
        data_str        += 'in Brooklyn no no no The sun should rise Burning all the street lamps out at 3AM So DJ play it again'
        data_str        += 'Until the night turns into morning You ll be in my arms And just keep driving Along the boulevard'
        data_str        += 'And if I kiss you darling Please dont be alone its just start of everything if you want A new Love In New York' 
        data_size        = len(data_str)
        data_offset      = 1
        data_start_index = 0
        payload_str      = 'I'

        tag_sem.acquire()
        data_tag += 1
        tag_sem.release()

        # first Fragmented Packet Format
        # read first 50 bytes from data string
        payload_str += str(chr(self.FRAG_1)) + str(chr(data_size)) + str(chr(data_tag))
        payload_str += data_str[0:50]

        COAP_5685_SEMAPHORE.acquire()

        c_INST.PUT(
            self.link,
            payload=[ord(b) for b in payload_str]
        )

        COAP_5685_SEMAPHORE.release()

        # Second to Nth Fragmented Packet Format
        # read remain bytes, 49 bytes each
        payload_str = 'I'
        data_start_index = 50

        while(data_str != ''):
            payload_str += str(chr(self.FRAG_N)) + str(chr(data_size)) + str(chr(data_tag)) + str(chr(data_offset))
            payload_str += data_str[data_start_index : (data_start_index + 49)]

            COAP_5685_SEMAPHORE.acquire()

            c_INST.PUT(
                self.link,
                payload=[ord(b) for b in payload_str]
            )

            COAP_5685_SEMAPHORE.release()

            data_offset = data_offset + 1

        # check DB whether sensor value changed or not, every 30 seconds
        # if work_flag is set 'True', it returns and send FIN flag
        self._checkDB()
        # 4-handshake --------------------------- 1
        c_INST.PUT(
            self.link,
            payload=[ord(b) for b in 'I'+str(chr(self.FIN))]
        )
        

    def _checkDB(self):
        max_timeout = 300
        # timer start
        print 'check the DataBase with certain period, is condition set which certificates right adjustment'

        # in time, work have done
        self.work_flag = True

        # time out, work haven't done
        # work_flag = False
        if(self.work_flag == True):
            return

        threading.Timer(30, self._checkDB).start()



class ConnectionClass():
    SYN_dict = {
                'SYN'     : 0,
                'SYN+ACK' : 0,
                'ACK'     : 0
    }

    FIN_dict = {
                'FIN_1' : 1,
                'FIN_2' : 0,
                'ACK_1' : 0,
                'ACK_2' : 0
    }

    link      = 'coap://[bbbb::2]:5685/inst'

    SYN       = 0
    FIN       = 0
    ACK       = 0

    def __init__(self):
        self.SYN      = 128
        self.FIN      = 64
        self.ACK      = 32   

    def _handle(self, payload):
        # Server Received SYN pkt from Client
        # 3-handshake ------------------------------- 1
        if((payload[0] == self.SYN) &
           (self.SYN_dict['SYN'] == 0)):
            self.SYN_dict['SYN']     = 1
            self.SYN_dict['SYN+ACK'] = 1
            # Response with PUT methd
            # reply : SYN + ACK
            # 3-handshake --------------------------- 2
            COAP_5685_SEMAPHORE.acquire()

            c_INST.PUT(
                self.link,
                payload=[ord(b) for b in 'I'+str(chr(self.SYN + self.ACK))]
            )

            COAP_5685_SEMAPHORE.release()

        # Server Received ACK pkt from Client
        # 3-handshake ------------------------------- 3
        # Server sends data to Client
        elif((payload[0] == self.ACK) &
             (self.SYN_dict['SYN'] == 1) &
             (self.SYN_dict['SYN+ACK'] == 1) &
             (self.SYN_dict['ACK'] == 0)):

            self.SYN_dict['ACK'] = 1
            CONN_SEMAPHORE.acquire()
            CONNECTION_SYN = True
            CONN_SEMAPHORE.release()

        # Server Received FIN pkt from Client
        # FIN pkt Arrived 
        # 4-handshake --------------------------- 2
        elif((payload[0] == self.FIN) &
             (self.FIN_dict['FIN_2'] == 0) &
             (self.FIN_dict['FIN_1'] == 1) &
             (CONNECTION_SYN == True)):

            self.FIN_dict['FIN_2'] = 1

        # Server Received ACK pkt from Client
        # ACK pkt Arrived
        # 4-handshake --------------------------- 3
        elif((payload[0] == self.ACK) &
             (self.FIN_dict['ACK_1'] == 0) &
             (self.FIN_dict['FIN_1'] == 1) &
             (self.FIN_dict['FIN_2'] == 1)):

            self.FIN_dict['ACK_1'] = 1

            CONN_SEMAPHORE.acquire()
            CONNECTION_FIN = True
            CONN_SEMAPHORE.release()

            # Reply with Final ACK to Client to close Connection
            # 4-handshake ----------------------- 4

            COAP_5685_SEMAPHORE.acquire()

            c_INST.PUT(
                self.link,
                payload=[ord(b) for b in 'I'+str(chr(self.ACK))]
            )

            COAP_5685_SEMAPHORE.release()


class ThreadClass(threading.Thread):
    def __init__(self, index):
        threading.Thread.__init__(self)
        self.thread_index = index

    def returnIndex(self):
        return self.index

    def run(self):
        if(self.thread_index == THREAD_ROUTE):
            print 'ROUTE  coap server created with PORT : ' + str(5683) + '\n'

        elif(self.thread_index == THREAD_DODAG_IPC):
            
            IPC_HOST = 'localhost'
            IPC_PORT = 25800

            print ' UDP server created with HOST : ' + IPC_HOST + ' PORT : ' + str(IPC_PORT) + '\n'

            server = SocketServer.UDPServer((IPC_HOST, IPC_PORT), UDP_DODAG_IPC)
            server.serve_forever()

        elif(self.thread_index == THREAD_SENSOR):
            c_SENSOR.addResource(SensorResource())
            print 'SENSOR coap server created with PORT : ' + str(5684) + '\n'

        elif(self.thread_index == THREAD_INST):
            c_INST.addResource(InstResource())
            print 'INST   coap server created with PORT : ' + str(5685) + '\n'     

        elif(self.thread_index == THREAD_SYSKILL):
            raw_input('\n\nServer running. Press Enter to close.\n\n')

            if(c_ROUTE != ''):
                c_ROUTE.close()
            if(c_SENSOR != ''):
                c_SENSOR.close()

            os.kill(os.getpid(), signal.SIGTERM)


class UDP_DODAG_IPC(SocketServer.BaseRequestHandler):
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


thread_index = 0
server       = 0
data_tag     = 1
port_sem     = threading.Semaphore(1)
tag_sem      = threading.Semaphore(1)
done_sem     = threading.Semaphore(1)

c_ROUTE  = coap.coap(udpPort=5683) # Working checked
c_SENSOR = coap.coap(udpPort=5684)
c_INST   = coap.coap(udpPort=5685) 

if __name__ == "__main__":

    for i in range(5):
        t = ThreadClass(i+1)
        t.start()