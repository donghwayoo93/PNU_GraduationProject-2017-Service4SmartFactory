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
import requests
import pymongo
import datetime
import logging
import logging.handlers


# create logger
logger = logging.getLogger("crumbs")
logger.setLevel(logging.INFO)

# format logger
formatter = logging.Formatter('[%(levelname)s | %(filename)s : %(lineno)s] %(asctime)s > %(message)s')

fileHandler = logging.FileHandler('./log/Server.log')
streamHandler = logging.StreamHandler()

fileHandler.setFormatter(formatter)
streamHandler.setFormatter(formatter)

logger.addHandler(fileHandler)
logger.addHandler(streamHandler)

THREAD_ROUTE          = 1
THREAD_SENSOR         = 2
THREAD_INST           = 3
THREAD_RECV_LABEL     = 4
THREAD_DODAG_IPC      = 5
THREAD_SYSKILL        = 6
THREAD_RENEW_CONN     = 7

CONNECTION_SYN        = False
CONNECTION_FIN        = False

CONN_SEMAPHORE        = threading.Semaphore(1)
COAP_5685_SEMAPHORE   = threading.Semaphore(1)
PAYLOAD_SEMAPHORE     = threading.Semaphore(1)
PARENT_SEMAPHORE      = threading.Semaphore(1)

COAP_RECV_PAYLOAD     = [0]
OPENSERIAL_MTU        = 32
CURRENT_PARENT        = ''


class SensorResource(coapResource.coapResource):
    
    def __init__(self):
        # initialize parent class
        coapResource.coapResource.__init__(
            self,
            path = 'gpio',
        )
    
    def GET(self,options=[]):
        
        print 'GET received'
        
        respCode        = d.COAP_RC_2_05_CONTENT
        respOptions     = []
        respPayload     = [ord(b) for b in 'dummy response']
        
        return (respCode,respOptions,respPayload)

    def PUT(self, srcIp, options=[],payload=None):
        # In case Server Receives Sensor Value Packet
        if(unichr(payload[0]) == 'S'):
            payload = payload[2:]

            my_suffix_1 = format(payload[0], 'x')
            my_suffix_2 = format(payload[1], 'x')


            if(len(my_suffix_1) == 1):
                my_suffix_1 = '0' + my_suffix_1
            if(len(my_suffix_2) == 1):
                my_suffix_2 = '0' + my_suffix_2

            #print payload

            payload = payload[3:]

            solar_1          = payload[0]
            solar_2          = payload[1]

            solar            = (int(solar_1) * 256) + int(solar_2)

            photosynthetic_1 = payload[3]
            photosynthetic_2 = payload[4]

            photosynthetic   = (int(photosynthetic_1) * 256) + int(photosynthetic_2)

            motor            = payload[6]

            DAO_LED          = payload[8]

            ipv6_suffix = str(my_suffix_1) + str(my_suffix_2)

            if(solar != 0):
                solar = (int)(2.5 * (float(solar) / 4096) * 6250)
            if(photosynthetic != 0):
                photosynthetic = (int)(1.5 * (float(photosynthetic) / 4096) * 1000)

            print ipv6_suffix + ' ' + str(solar) + ' ' + str(photosynthetic) + ' ' + str(motor) + ' ' + str(DAO_LED)

            updateSensor(str(ipv6_suffix), str(solar), 'solar')
            updateSensor(str(ipv6_suffix), str(photosynthetic), 'photosynthetic')


        # In case Server Receives Connection Packet
        elif(unichr(payload[0]) == 'C'):
            print 'error : Sensor coap server received Connection Packet\n'
            print 'This case SHOULD NOT happen\n'
        # In case Server Receives Login Packet
        elif(unichr(payload[0]) == 'L'):
            print 'error : Sensor coap server received Login Packet\n'
            print 'This case SHOULD NOT happen\n'
        # In case Server Receives Instruction Packet
        elif(unichr(payload[0]) == 'I'):
            print 'error : Sensor coap server received Instruction Packet\n'
            print 'This case SHOULD NOT happen\n'

        respCode = d.COAP_RC_2_05_CONTENT
        respOptions = []
        respPayload = []
        return (respCode, respOptions, respPayload)
##################################################################
#                       UPDATE DB Function Start         

def updateSensor(machineID, sensorData, sensorName):
    connection = pymongo.MongoClient("localhost", 27017)
    DB = connection.mongodbroles
    DB.machines.update({
        "machineID":str(machineID)
    },{
        '$set': {
            "sensorState." + sensorName : str(sensorData)
        }
    }, upsert=True)

    DB.sensorDB.update({
        "machineID":str(machineID)
    },{
        '$push' : {"sensorState":
            {"time":datetime.datetime.now(),
             "sensor":sensorName,
             "data":sensorData}
        }
    }, upsert=True)

def updateNearWorkerID(machineID, workerID):
    connection = pymongo.MongoClient("localhost", 27017)
    DB = connection.mongodbroles
    DB.machines.update({
        "machineID": str(machineID)
    }, {
        '$set': {
            "nearWorkerID": workerID
        }
    }, upsert=True)

##################################################################
#                       UPDATE DB Function End        ^

class InstResource(coapResource.coapResource):

    def __init__(self):
        # initialize parent class
        coapResource.coapResource.__init__(
            self,
            path = 'inst',
        )

    def PUT(self, srcIp, options=[],payload=None):
        global COAP_RECV_PAYLOAD
        print '5685 : ' + str(payload)

        PAYLOAD_SEMAPHORE.acquire()
        COAP_RECV_PAYLOAD = payload
        PAYLOAD_SEMAPHORE.release()

        respCode = d.COAP_RC_2_05_CONTENT
        respOptions = []
        respPayload = []

        return (respCode, respOptions, respPayload)

class LoginClass:
    DB        = ''
    send_name = ''
    send_auth = ''

    link      = ''

    def __init__(self):
        self.DB   = ''
        self.link = 'coap://[bbbb::2]:5685/inst'

    def _login(self, payload):
        payload_str = ''

        for i in range(len(payload)):
            payload_str += chr(payload[i])

        info = payload_str.split(',')
        logger.info('Received LoginData email : ' + str(info[0]))

        json_data = {"type" : "login",
                     "email" : str(info[0]),
                     "password" : str(info[1])
                     }

        headers = {'Content-Type': 'application/json'}
        res = requests.post('http://localhost:8088/api/auth/login',
                            data = json.dumps(json_data),
                            headers = headers)


        print res.text.encode('utf-8')

        dict = json.loads(res.text.encode('utf-8'))

        info = dict['user']
        # make connection with DB
        # get worker's name and auth

        self.send_name = info['email']
        self.send_auth = info['accessLevel']

        self._sendResult()

    def _sendResult(self):
        payload = str(self.send_name) + ',' + str(self.send_auth)

        COAP_5685_SEMAPHORE.acquire()

        c_INST.PUT(
            self.link,
            payload=[ord(b) for b in 'L'+payload]
        )

        COAP_5685_SEMAPHORE.release()
        logger.info('Sends back LoginData email : ' + str(self.send_name) + 'accessLevel : ' + str(self.send_auth))

    def __del__(self):
        logger.info('destruct LoginClass')


class machineClass:
    FRAG_1  = 0
    FRAG_N  = 0
    link    = ''

    def __init__(self):
        self.FRAG_1    = 24
        self.FRAG_N    = 28
        self.link      = 'coap://[bbbb::2]:5685/inst'

    def _handle(self, payload):
        payload_str = ''
        for i in range(len(payload)):
            payload_str += chr(payload[i])

        print payload_str

        payload_str = payload_str.split(' ')

        if(payload_str[0] == 'machineInfo'):
            logger.info('Received machineInfo Solicitation Message')
            self._sendMachineInfo(payload_str[1])

        elif(payload_str[0] == 'machineSensor'):
            logger.info('Received machineSensor Solicitation Message')
            self._sendMachineSensor(payload_str[1])
        elif(payload_str[0] == 'machineMotor'):
            logger.info('Received machineMotor Adjustment Message')
            self._adjustMachineMotor(payload_str[1])


    def _adjustMachineMotor(self, workerID, command):
        global c_ROUTE

        link = 'coap://[bbbb::' + str(CURRENT_PARENT) + ']:5683/gpio'

        if(command == 'ON'):
            payload_str = '1x'
        else:
            payload_str = '0x'

        c_ROUTE.PUT(
                link,
                payload=[ord(b) for b in payload_str]
        )

        self._sendMacheinMotor(command)


    def _sendMacheinMotor(self, status):
        global c_INST, COAP_5685_SEMAPHORE, data_tag

        if(status == 'ON'):
            data_str = 'TRUE'
        else:
            data_str = 'FALSE'

        tag_sem.acquire()
        data_tag += 1
        tag_sem.release()

        data_len_upper, data_len_lower = divmod(len(data_str), 256)
        payload_str  = 'M'
        payload_str += str(chr(self.FRAG_1)) + str(chr(data_len_upper)) + str(chr(data_len_lower)) +  str(chr(data_tag))
        payload_str += data_str

        COAP_5685_SEMAPHORE.acquire()
        c_INST.PUT(
            self.link,
            payload=[ord(b) for b in str(payload_str)]
        )
        COAP_5685_SEMAPHORE.release()


    def _sendMachineInfo(self, workerID):
        global c_INST, COAP_5685_SEMAPHORE, data_tag, OPENSERIAL_MTU

        json_data = {
                     "workerID"  : str(workerID)
        }

        res = requests.get('http://localhost:8088/api/machines/info',
                            params=json_data)


        print res.text.encode('utf-8')
        data_str = res.text.encode('utf-8')
        data_str = str(data_str)

        tag_sem.acquire()
        data_tag += 1
        tag_sem.release()

        logger.info('Received ' + str(len(data_str)) + ' bytes of MachineInfoData from DataBase')

        data_start_index = 0
        data_offset = 1
        data_len_upper, data_len_lower = divmod(len(data_str), 256)
        payload_str  = 'M'
        payload_str += str(chr(self.FRAG_1)) + str(chr(data_len_upper)) + str(chr(data_len_lower)) +  str(chr(data_tag))
        payload_str += str(data_str[0:OPENSERIAL_MTU])

        COAP_5685_SEMAPHORE.acquire()
        c_INST.PUT(
            self.link,
            payload=[ord(b) for b in str(payload_str)]
        )
        COAP_5685_SEMAPHORE.release()

        data_start_index = OPENSERIAL_MTU

        while(data_str != ''):
            payload_str  = 'M'
            payload_str += str(chr(self.FRAG_N)) + str(chr(data_len_upper)) + str(chr(data_len_lower)) + str(chr(data_tag)) + str(chr(data_offset))
            payload_str += str(data_str[data_start_index : (data_start_index + OPENSERIAL_MTU)])
            data_str     = data_str[(data_start_index + OPENSERIAL_MTU):]

            COAP_5685_SEMAPHORE.acquire()

            c_INST.PUT(
                self.link,
                payload=[ord(b) for b in str(payload_str)]
            )

            COAP_5685_SEMAPHORE.release()

            data_offset += 1
            data_start_index = 0

        logger.info('Sends back with machineInfo Message')



    def _sendMachineSensor(self, workerID):
        global c_INST, COAP_5685_SEMAPHORE, data_tag, OPENSERIAL_MTU

        json_data = {
                     "workerID"  : str(workerID)
        }

        res = requests.get('http://localhost:8088/api/machines/sensor',
                            params=json_data)

        print res.text.encode('utf-8')
        data_str = res.text.encode('utf-8')
        data_str = str(data_str)

        tag_sem.acquire()
        data_tag += 1
        tag_sem.release()

        logger.info('Received ' + str(len(data_str)) + ' bytes of MachineSensorData from DataBase')

        data_start_index = 0
        data_offset = 1
        data_len_upper, data_len_lower = divmod(len(data_str), 256)
        payload_str  = 'M'
        payload_str += str(chr(self.FRAG_1)) + str(chr(data_len_upper)) + str(chr(data_len_lower)) +  str(chr(data_tag))
        payload_str += str(data_str[0:OPENSERIAL_MTU])


        COAP_5685_SEMAPHORE.acquire()
        c_INST.PUT(
            self.link,
            payload=[ord(b) for b in str(payload_str)]
        )   
        COAP_5685_SEMAPHORE.release()

        data_start_index = OPENSERIAL_MTU

        while(data_str != ''):
            payload_str  = 'M'
            payload_str += str(chr(self.FRAG_N)) + str(chr(data_len_upper)) + str(chr(data_len_lower)) + str(chr(data_tag)) + str(chr(data_offset))
            payload_str += str(data_str[data_start_index : (data_start_index + OPENSERIAL_MTU)])
            data_str     = data_str[(data_start_index + OPENSERIAL_MTU):]
            print str(len(data_str))


            COAP_5685_SEMAPHORE.acquire()

            c_INST.PUT(
                self.link,
                payload=[ord(b) for b in str(payload_str)]
            )

            COAP_5685_SEMAPHORE.release()

            data_offset += 1
            data_start_index = 0

        logger.info('Sends back with machineSensor Message')


class InstructionClass:
    FRAG_1    = 0
    FRAG_N    = 0
    FIN       = 0
    link      = ''

    def __init__(self):
        self.FRAG_1    = 24
        self.FRAG_N    = 28
        self.FIN       = 127
        self.link      = 'coap://[bbbb::2]:5685/inst'

    def _handle(self, payload):
        payload_str = ''
        for i in range(len(payload)):
            payload_str += chr(payload[i])

        print payload_str

        payload_str = payload_str.split(' ')

        if(payload_str[0] == 'InstructionSolicitation'):
            logger.info('Received Instruction Solicitation Message')
            self._sendInstructionData(payload_str[1])

    def _sendInstructionData(self, workerID):
        global data_tag
        global c_INST
        global COAP_5685_SEMAPHORE

        json_data = {"type" : "machineManual",
                     "workerID"  : str(workerID),
                     "manualNum" : "1"
        }

        res = requests.get('http://localhost:8088/api/machines/manual',
                            params=json_data)

        data_str = res.text.encode('utf-8')
        data_str = str(data_str)

        # read data from DB
        #data_str         = 'Five drinks in on Friday night We only came to dry your eyes And get you out of your room'
        #data_str        += ' Now this bar has closed its doors I found my hand is holding yours Do you wanna go home so soon '
        #data_str        += 'Or maybe we shpuld take a ride Through the night and sing along to every song Thats on the radio In the back of a Taxi cab'
        #data_str        += 'in Brooklyn no no no The sun should rise Burning all the street lamps out at 3AM So DJ play it again'
        #data_str        += 'Until the night turns into morning You ll be in my arms And just keep driving Along the boulevard'
        #data_str        += 'And if I kiss you darling Please dont be alone its just start of everything if you want A new Love In New York' 
        data_size        = len(data_str)
        data_size_upper  = 0
        data_size_lower  = 0
        data_offset      = 1
        data_start_index = 0
        payload_str      = 'I'

        logger.info('Received ' + str(data_size) + ' bytes of Instruction from DataBase')

        tag_sem.acquire()
        data_tag += 1
        tag_sem.release()

        data_size_upper, data_size_lower = divmod(data_size, 256)

        # first Fragmented Packet Format
        # read first 32 bytes from data string
        payload_str += str(chr(self.FRAG_1)) + str(chr(data_size_upper)) + str(chr(data_size_lower)) + str(chr(data_tag))
        payload_str += str(data_str[0:OPENSERIAL_MTU])

        #print 'data_size            : ' + str(data_size)
        #print 'data_size_upper      : ' + str(data_size_upper)
        #print 'data_size_lower      : ' + str(data_size_lower)

        COAP_5685_SEMAPHORE.acquire()

        c_INST.PUT(
            self.link,
            payload=[ord(b) for b in str(payload_str)]
        )

        COAP_5685_SEMAPHORE.release()

        # Second to Nth Fragmented Packet Format
        # read remain bytes, 32 bytes each
        
        data_start_index = OPENSERIAL_MTU

        while(data_str != ''):
            payload_str  = 'I'
            payload_str += str(chr(self.FRAG_N)) + str(chr(data_size_upper)) + str(chr(data_size_lower)) + str(chr(data_tag)) + str(chr(data_offset))
            payload_str += str(data_str[data_start_index : (data_start_index + OPENSERIAL_MTU)])
            data_str     = data_str[(data_start_index + OPENSERIAL_MTU):]

            print payload_str

            COAP_5685_SEMAPHORE.acquire()

            c_INST.PUT(
                self.link,
                payload=[ord(b) for b in str(payload_str)]
            )

            COAP_5685_SEMAPHORE.release()

            data_offset = data_offset + 1
            data_start_index = 0

        logger.info('Sends back with Instruction Data')   


class ConnectionClass:
    SYN_dict = {
                'SYN'     : 0,
                'SYN+ACK' : 0,
                'ACK'     : 0
    }

    FIN_dict = {
                'FIN_1' : 0,
                'FIN_2' : 0,
                'ACK'   : 0,
    }

    link      = 'coap://[bbbb::2]:5685/inst'

    SYN       = 0
    FIN       = 0
    ACK       = 0

    def __init__(self):
        self.FIN      = 127
        self.SYN      = 64
        self.ACK      = 32   

    def _handle(self, payload):
        global CONNECTION_SYN
        global CONNECTION_FIN
        global c_INST
        global COAP_5685_SEMAPHORE
        global rpl

        print str(payload)
        print 'FIN_1 : ' + str(self.FIN_dict['FIN_1'])
        print 'FIN_2 : ' + str(self.FIN_dict['FIN_2'])

        # Server Received SYN pkt from Client
        # 3-handshake ------------------------------- 1
        if((payload[0] == self.SYN) &
           (self.SYN_dict['SYN'] == 0)):
            self.SYN_dict['SYN']     = 1
            self.SYN_dict['SYN+ACK'] = 1
            logger.info('Received SYN from Client')
            # Response with PUT methd
            # reply : SYN + ACK
            # 3-handshake --------------------------- 2
            COAP_5685_SEMAPHORE.acquire()
            c_INST.PUT(
                self.link,
                payload=[ord(b) for b in 'C'+str(chr(self.SYN + self.ACK))]
            )
            logger.info('Sends back with SYN+ACK')
            COAP_5685_SEMAPHORE.release()

        # Server Received ACK pkt from Client
        # 3-handshake ------------------------------- 3
        # Server sends data to Client
        elif((payload[0] == self.ACK) &
             (self.SYN_dict['SYN'] == 1) &
             (self.SYN_dict['SYN+ACK'] == 1) &
             (self.SYN_dict['ACK'] == 0)):
            logger.info('Received ACK from Client')
            self.SYN_dict['ACK'] = 1
            CONN_SEMAPHORE.acquire()
            CONNECTION_SYN = True
            CONN_SEMAPHORE.release()
            logger.info('Connection SYN flag status => True')

        # Server Received FIN pkt from Client
        # FIN pkt Arrived 
        # 4-handshake --------------------------- 2
        elif((payload[0] == self.FIN) &
             (self.FIN_dict['FIN_2'] == 0) &
             (self.FIN_dict['FIN_1'] == 0) &
             (CONNECTION_SYN == True)):
            logger.info('Received FIN_1 from Client')
            self.FIN_dict['FIN_1'] = 1
            self.FIN_dict['FIN_2'] = 1

            rpl.DAO_Adjust('0:0:0:2', 'ex', 30)

            rpl.DIO_Adjust(CURRENT_PARENT, 'ex', 10)

            COAP_5685_SEMAPHORE.acquire()

            c_INST.PUT(
                self.link,
                payload=[ord(b) for b in 'C'+str(chr(self.FIN))]
            )
            logger.info('Sends back with FIN_2')
            COAP_5685_SEMAPHORE.release()


        elif((payload[0] == self.ACK) &
             (self.FIN_dict['FIN_1'] == 1) &
             (self.FIN_dict['FIN_2'] == 1) &
             (CONNECTION_SYN == True)):
            logger.info('Received FINAL ACK from Client')
            self.FIN_dict['ACK'] = 1

            CONN_SEMAPHORE.acquire()
            CONNECTION_FIN = True
            CONN_SEMAPHORE.release()

            logger.info('Connection FIN flag status => True')

    def __del__(self):
        logger.info('Destruct Connection Class')

    def _renewClass(self):
        self.SYN_dict['SYN']     = 0
        self.SYN_dict['SYN+ACK'] = 0
        self.SYN_dict['ACK']     = 0

        self.FIN_dict['FIN_1']   = 0
        self.FIN_dict['FIN_2']   = 0
        self.FIN_dict['ACK']     = 0


class ThreadClass(threading.Thread):

    def __init__(self, index):
        threading.Thread.__init__(self)
        self.thread_index = index

    def returnIndex(self):
        return self.index

    def run(self):
        if(self.thread_index == THREAD_ROUTE):
            logger.info('Route CoAP Server : 5683')

        elif(self.thread_index == THREAD_SENSOR):
            c_SENSOR.addResource(SensorResource())
            logger.info('Sensor CoAP Server : 5684')

        elif(self.thread_index == THREAD_INST):
            c_INST.addResource(InstResource())
            logger.info('Instruction CoAP Server : 5685')

        elif(self.thread_index == THREAD_RECV_LABEL):
            global COAP_RECV_PAYLOAD, PAYLOAD_SEMAPHORE
            global conn, inst, login, machine

            while True:
                payload = COAP_RECV_PAYLOAD

                # received label = Connection
                if(unichr(payload[0]) == 'C'):
                    # trim label 'C'
                    conn._handle(payload[1:])
                # received label = Login
                elif(unichr(payload[0]) == 'L'):
                    # trim label 'L'
                    login._login(payload[1:])
                # received label = Instruction
                elif(unichr(payload[0]) == 'I'):
                    inst._handle(payload[1:])
                # received lavel = Machine
                elif(unichr(payload[0]) == 'M'):
                    machine._handle(payload[1:])

                PAYLOAD_SEMAPHORE.acquire()
                COAP_RECV_PAYLOAD = [0]
                PAYLOAD_SEMAPHORE.release()

                time.sleep(1)

        elif(self.thread_index == THREAD_DODAG_IPC):
            
            IPC_HOST = 'localhost'
            IPC_PORT = 25800

            print ' UDP server created with HOST : ' + IPC_HOST + ' PORT : ' + str(IPC_PORT)

            server = SocketServer.UDPServer((IPC_HOST, IPC_PORT), UDP_DODAG_IPC)
            server.serve_forever()

        elif(self.thread_index == THREAD_SYSKILL):
            raw_input('\n\nServer running. Press Enter to close.\n\n')

            if(c_ROUTE != ''):
                c_ROUTE.close()
            if(c_SENSOR != ''):
                c_SENSOR.close()
            if(c_INST != ''):
                c_INST.close()

            os.kill(os.getpid(), signal.SIGTERM)

        elif(self.thread_index == THREAD_RENEW_CONN):
            global CONNECTION_FIN, CONNECTION_SYN, CONN_SEMAPHORE
            global CURRENT_PARENT, PARENT_SEMAPHORE
            global conn, data_tag, tag_sem

            time.sleep(1)
            
            while True:
                if((CONNECTION_SYN == True) & (CONNECTION_FIN == True)):
                    logger.info('Server Renews the Flags and classes')
                    # initialize SYN, FIN Flag
                    CONN_SEMAPHORE.acquire()
                    CONNECTION_SYN = False
                    CONNECTION_FIN = False
                    CONN_SEMAPHORE.release()
                    # initialize Current Parent
                    PARENT_SEMAPHORE.acquire()
                    CURRENT_PARENT = ''
                    PARENT_SEMAPHORE.release()

                    conn._renewClass()


                if (data_tag == 255):
                    logger.info('Server Renews the data_tag value to 1')
                    tag_sem.acquire()
                    data_tag = 1
                    tag_sem.release()

class UDP_DODAG_IPC(SocketServer.BaseRequestHandler):
    def handle(self):
        global rpl
        data   = self.request[0]
        socket = self.request[1]

        dict = json.loads(data)

        pkt_type = dict['type']
        src_addr = dict['src_addr']
        dst_addr = dict['dst_addr']
        uri      = dict['uri']
        period   = dict['period']

        if(pkt_type == 'DIO'):
            rpl.DIO_Adjust(dst_addr, uri, period)
        elif(pkt_type == 'DAO'):
            rpl.DAO_Adjust(dst_addr, uri, period)
        else:
            print 'error : no match type for the handler'
            print 'pkt_type : ' + pkt_type

        socket.sendto(data.upper(), self.client_address)


class RPLClass:

    def DIO_Adjust(self, Dest, uri, period):
        global CURRENT_PARENT
        global PARENT_SEMAPHORE
        global c_ROUTE

        # save Current parent's ipv6 address
        PARENT_SEMAPHORE.acquire()
        CURRENT_PARENT = str(Dest)
        PARENT_SEMAPHORE.release()

        print 'Parent addr       : ' + Dest
        print 'CURRENT_PARENT    : ' + CURRENT_PARENT

        link        = 'coap://[bbbb::' + str(Dest) + ']:5683/' + str(uri)
        payload_str = '1=' + str(period) + '!'

        if(str(Dest) != ''):
            logger.info('Server sends DIO adjust message Destination : ' + str(Dest))
            print str(link)
            print str(payload_str)

            response = c_ROUTE.PUT(
                    link,
                    payload=[ord(b) for b in payload_str]
            )
            
            print_str = ''
            for r in response:
                print_str += chr(r)
            print 'response : ' + print_str

            link        = 'coap://[bbbb::' + str(Dest) + ']:5683/gpio'
            if(int(period) > 10):
                payload_str = 'x1'        # turn on LED
            else:
                payload_str = 'x0'        # turn off  LED

            c_ROUTE.PUT(
                    link,
                    payload=[ord(b) for b in payload_str]
            )
            logger.info('Server sent LED adjust message Destination : ' + str(Dest))

        else:
            logger.info('No parrent node to send DIO')

    def DAO_Adjust(self, Dest, uri, period):
        global c_ROUTE

        if(Dest == '0:0:0:2'):
            Dest = '2'

        link        = 'coap://[bbbb::' + str(Dest) + ']:5683/' + str(uri)
        payload_str = '2=' + str(period) + '!'

        logger.info('Server sends DAO adjust message Destination : ' + str(Dest))  
        print str(link)
        print str(payload_str)

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

c_ROUTE      = coap.coap(udpPort=5683) # Working checked
c_SENSOR     = coap.coap(udpPort=5684)
c_INST       = coap.coap(udpPort=5685) 

conn         = ConnectionClass()
inst         = InstructionClass()
login        = LoginClass()
machine      = machineClass()
rpl          = RPLClass()

if __name__ == "__main__":

    for i in range(7):
        t = ThreadClass(i+1)
        t.start()