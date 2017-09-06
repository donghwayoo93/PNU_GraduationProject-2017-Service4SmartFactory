import os
import signal
import sys
here = sys.path[0]
sys.path.insert(0, os.path.join(here,'..'))

import threading
#import logging_setup
import json
import socket
import time

THREAD_IPV6_UDP_SOCK = 1
THREAD_UDP_IPC_SOCK  = 2
THREAD_SYSKILL       = 3

CONNECTION_SYN       = False
CONNECTION_FIN       = False

UDP_OV_IP            = 'bbbb::2'
UDP_OV_PORT          = 25801

TUN_DST_IP           = 'bbbb::1'
TUN_DST_PORT         = 25800

UDP_IPC_IP           = 'localhost'
UDP_IPC_PORT         = 25805

UDP_WEB_APP_IP       = 'localhost'
UDP_WEB_APP_PORT     = 30000


SEND_OUT_SEMAPHORE   = threading.Semaphore(1)
SEND_IN_SEMAPHORE    = threading.Semaphore(1)
CONN_SEMAPHORE       = threading.Semaphore(1)
INST_SEMAPHORE       = threading.Semaphore(1)

sock                 = ''
sock_internal        = ''
Instruction_String   = ''
workerID             = '0EB2'

class ConnectionClass:
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

    SYN          = 0
    FIN          = 0
    ACK          = 0
    FRAG_1       = 0
    FRAG_N       = 0

    data_tag     = 0
    data_size    = 0
    total_offset = 0

    Response_addr = ''
    msg           = ''

    def __init__(self):

        self.FIN      = 127
        self.SYN      = 64
        self.ACK      = 32
        self.FRAG_1   = 24
        self.FRAG_N   = 28

    def _sendSYN(self):
        # 3-handshake ---------------------------------------- 1
        self.SYN_dict['SYN'] = 1
        self.msg             = 'C' + str(chr(self.SYN))
        SEND_OUT_SEMAPHORE.acquire()
        sock.sendto(self.msg, (TUN_DST_IP, TUN_DST_PORT))
        SEND_OUT_SEMAPHORE.release()
        print 'client sends SYN'

    def _handle(self, data):
        global CONNECTION_SYN, CONNECTION_FIN, CONN_SEMAPHORE
        print str(data[0])
        data[0] = int(data[0])
        
        # client receives SYN+ACK pkt
        # response with ACK pkt and ready for other data
        if((self.SYN_dict['SYN'] == 1) &
           (self.SYN_dict['SYN+ACK'] == 0) &
           (data[0] == self.SYN + self.ACK)):
            print 'client received SYN+ACK'
            # 3-handshake ------------------------------------ 2
            self.SYN_dict['SYN+ACK'] = 1
            self.SYN_dict['ACK']     = 1
            self.msg                 = 'C' + str(chr(self.ACK))
            # 3-handshake ------------------------------------ 3
            print 'client send ACK'
            SEND_OUT_SEMAPHORE.acquire()
            sock.sendto(self.msg, (TUN_DST_IP, TUN_DST_PORT))
            SEND_OUT_SEMAPHORE.release()

            # change connection flag
            CONN_SEMAPHORE.acquire()
            CONNECTION_SYN = True
            CONN_SEMAPHORE.release()

        # client receives FIN pkt
        # response with FIN_2, ACK_1 and ready for final ACK_2 pkt
        elif((CONNECTION_SYN == True) &
             (self.FIN_dict['FIN_1'] == 0) &
             (self.FIN_dict['FIN_2'] == 0) &
             (data[0] == self.FIN)):
            print 'client received FIN_1'
            # 4-handshake ------------------------------------ 1
            self.FIN_dict['FIN_1'] = 1
            self.FIN_dict['FIN_2'] = 1
            self.FIN_dict['ACK_1'] = 1
            # 4-handshake ------------------------------------ 2
            SEND_OUT_SEMAPHORE.acquire()
            print 'client send FIN_2'
            self.msg               = 'C' + str(chr(self.FIN))
            sock.sendto(self.msg, (TUN_DST_IP, TUN_DST_PORT))
            # 4-handshake ------------------------------------ 3
            print 'client send ACK_1'
            self.msg               = 'C' + str(chr(self.ACK))
            sock.sendto(self.msg, (TUN_DST_IP, TUN_DST_PORT))
            SEND_OUT_SEMAPHORE.release()

        # client receives final ACK_2 pkt
        # response nothing and ready to kill itself
        elif ((CONNECTION_SYN == True) &
              (self.FIN_dict['FIN_1'] == 1) &
              (self.FIN_dict['FIN_2'] == 1) &
              (self.FIN_dict['ACK_1'] == 1) &
              (data[0] == self.ACK)):
            print 'client received ACK_2'
            # 4-handshake ------------------------------------ 4
            # change connection flag
            self.FIN_dict['ACK_2'] = 1
            CONN_SEMAPHORE.acquire()
            CONNECTION_FIN = True
            CONN_SEMAPHORE.release()
            os.kill(os.getpid(), signal.SIGTERM)



class InstructionClass:
    Instruction_List      = 0
    Instruction_List_size = 0
    Instruction_size      = 0
    Instruction_tag       = 0

    FRAG_1                = 0
    FRAG_N                = 0

    def __init__(self):
        self.Instruction_List = []
        self.FRAG_1           = 24
        self.FRAG_N           = 28

    def _instructionSolicitation(self):
        global workerID
        msg = 'I' + 'InstructionSolicitation' + ' ' + str(workerID)

        SEND_OUT_SEMAPHORE.acquire()
        sock.sendto(msg, (TUN_DST_IP, TUN_DST_PORT))
        SEND_OUT_SEMAPHORE.release()
        
        print 'Instruction Solicitation msg sent'
        

    def _recvInstructionData(self, payload):

        payload = [int(i) for i in payload]

        if(payload[0] == self.FRAG_1):
            print 'client received FRAG_1'
            data_size_upper = payload[1]
            data_size_lower = payload[2]
            self.Instruction_size      = (data_size_upper * 256) + data_size_lower
            self.Instruction_tag       = payload[3]
            self.Instruction_List_size = int(self.Instruction_size/32 + 1)
            for i in range(self.Instruction_List_size):
                self.Instruction_List.append('')
            self.Instruction_List[0]   = payload[4:]
            
            print 'data size : ' + str(self.Instruction_size)

        elif(payload[0] == self.FRAG_N):
            print 'client received FRAG_N : ' + str(payload[4]) + 'th'
            if(self.Instruction_tag == payload[3]):
                self.Instruction_List[payload[4]] = payload[5:]

            if(self._checkList() == True):
                self._makeString()              
            

    def _checkList(self):
        total_length = 0
        for i in range(self.Instruction_List_size):
            total_length += len(self.Instruction_List[i])

        # All Instruction data received
        if(total_length == self.Instruction_size):
            print 'client checkList => True'
            return True
        # Not yet....
        else:
            print 'client checkList => False'
            return False

    def _makeString(self):
        global Instruction_String
        # make fragmented string to one
        INST_SEMAPHORE.acquire()
        for i in range(self.Instruction_List_size):
            Instruction_String += ''.join(str(chr(c)) for c in self.Instruction_List[i])
        INST_SEMAPHORE.release()

        print 'client makeString'
        print Instruction_String

        # send instruction string internal
        SEND_IN_SEMAPHORE.acquire()
        sock_internal.sendto(str(Instruction_String), (UDP_WEB_APP_IP, UDP_WEB_APP_PORT))
        SEND_IN_SEMAPHORE.release()
        
        Instruction_String = ''
        self.Instruction_List = []

class MachineClass:
    machine_List      = 0
    machine_List_size = 0
    machine_size      = 0
    machine_tag       = 0

    FRAG_1            = 0
    FRAG_N            = 0

    Machine_String    = ''

    def __init__(self):
        self.machine_List     = []
        self.FRAG_1           = 24
        self.FRAG_N           = 28

    def _machineInfoSolicitation(self):
        global workerID
        msg = 'M' + 'machineInfo' + ' ' +str(workerID)

        SEND_OUT_SEMAPHORE.acquire()
        sock.sendto(msg, (TUN_DST_IP, TUN_DST_PORT))
        SEND_OUT_SEMAPHORE.release()
        
        print 'machineInfo Solicitation msg sent'
        
    def _machineSensorSolicitation(self):
        global workerID
        msg = 'M' + 'machineSensor' + ' ' +str(workerID)

        SEND_OUT_SEMAPHORE.acquire()
        sock.sendto(msg, (TUN_DST_IP, TUN_DST_PORT))
        SEND_OUT_SEMAPHORE.release()
        
        print 'machineSensor Solicitation msg sent'

    def _recvMachineData(self, payload):

        payload = [int(i) for i in payload]
        
        print 'machine : ' + str(payload)

        if(payload[0] == self.FRAG_1):
            print 'client received machine FRAG_1'
            data_size_upper = payload[1]
            data_size_lower = payload[2]
            self.machine_size      = (data_size_upper * 256) + data_size_lower
            self.machine_tag       = payload[3]
            self.machine_List_size = int(self.machine_size/32 + 1)
            for i in range(self.machine_List_size):
                self.machine_List.append('')
            self.machine_List[0]   = payload[4:]
            
            print 'machine data size : ' + str(self.machine_size)

        elif(payload[0] == self.FRAG_N):
            print 'client received machine FRAG_N : ' + str(payload[4]) + 'th'
            if(self.machine_tag == payload[3]):
                self.machine_List[payload[4]] = payload[5:]

            if(self._checkList() == True):
                self._makeString()
                self.machine_List = []

    def _checkList(self):
        total_length = 0
        for i in range(self.machine_List_size):
            total_length += len(self.machine_List[i])

        # All Instruction data received
        if(total_length == self.machine_size):
            print 'client machine checkList => True'
            return True
        # Not yet....
        else:
            print 'client machine checkList => False'
            return False

    def _makeString(self):
        # make fragmented string to one
        for i in range(self.machine_List_size):
            self.Machine_String += ''.join(str(chr(c)) for c in self.machine_List[i])

        print 'client makeString'
        print self.Machine_String

        # send instruction string internal
        SEND_IN_SEMAPHORE.acquire()
        sock_internal.sendto(str(self.Machine_String), (UDP_WEB_APP_IP, UDP_WEB_APP_PORT))
        SEND_IN_SEMAPHORE.release()
        
        self.Machine_String = ''



class LoginClass:
    msg = ''
    def __init__(self):
        self.msg = 'L'

    def _login(self, id, pw):
        self.msg += str(id) + ',' + str(pw)
        # toss login data to outer Server
        SEND_OUT_SEMAPHORE.acquire()
        sock.sendto(self.msg, (TUN_DST_IP, TUN_DST_PORT))
        SEND_OUT_SEMAPHORE.release()

    def _recvResult(self, payload):
        payload = [int(i) for i in payload]
        payload_str = ''

        for i in range(len(payload)):
            payload_str += chr(payload[i])

        print 'check on _recvResult        : ' + payload_str

        info = payload_str.split(',')

        json_data = {"user":{
            "email" : str(info[0]),
            "accessLevel" : str(info[1])
        }}

        self.msg = json.dumps(json_data)
        # toss login result to internal
        SEND_IN_SEMAPHORE.acquire()
        sock_internal.sendto(self.msg, (UDP_WEB_APP_IP, UDP_WEB_APP_PORT))
        SEND_IN_SEMAPHORE.release()


class ThreadClass(threading.Thread):
    def __init__(self, index):
        threading.Thread.__init__(self)
        self.thread_index = index

    def run(self):
        if(self.thread_index == THREAD_IPV6_UDP_SOCK):
            conn._sendSYN()
            while True:
                data, addr = sock.recvfrom(1024)
                data = data[1:len(data)-1]
                data = data.split(',')
                # Instruction Data from Outer Server
                if(int(data[0]) == ord('I')):
                    # trim Packet label 'I' and Toss to InstructionClass to handle
                    print 'handling Instruction Data'
                    inst._recvInstructionData(data[1:])
                    
                # Connection Packet from Outer Server
                elif(int(data[0]) == ord('C')):
                    # trim Packet label 'C' and Toss to ConnectionClass to handle
                    print 'handling Connection Data'
                    conn._handle(data[1:])
                    
                # login result from outer server
                elif(int(data[0]) == ord('L')):
                    # send this result to internal
                    # trim Packet label 'L' and Toss to LoginClass to handle
                    print 'handling Login Data'
                    login._recvResult(data[1:])

                # Machine Info or Sensor result from outer server
                elif(int(data[0]) == ord('M')):
                    # send this result to internal
                    # trim Packet label 'L' and Toss to LoginClass to handle
                    print 'handling Machine Data'
                    machine._recvMachineData(data[1:])

                    

        elif(self.thread_index == THREAD_UDP_IPC_SOCK):
            while True:
                data, addr = sock_internal.recvfrom(1024)

                dict = json.loads(data)

                # handling login
                if(dict['type'] == 'login'):
                    login._login(dict['email'], dict['password'])
                # handling Instruction Soliciation
                elif(dict['type'] == 'machineManual'):
                    inst._instructionSolicitation()
                elif(dict['type'] == 'machineInfo'):
                    machine._machineInfoSolicitation()
                elif(dict['type'] == 'machineSensor'):
                    machine._machineSensorSolicitation()                    
                    

        elif(self.thread_index == THREAD_SYSKILL):
            raw_input('\n\nClient running. Press Enter to close.\n\n')
            os.kill(os.getpid(), signal.SIGTERM)


if __name__ == '__main__':
    
    conn                 = ConnectionClass()
    inst                 = InstructionClass()
    login                = LoginClass()
    machine              = MachineClass()  
    
    # receive Server Data from Openvisualizer & TUN Interface
    sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
    sock.bind((UDP_OV_IP, UDP_OV_PORT))

    # send Data from Server to Web APP
    sock_internal = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock_internal.bind((UDP_IPC_IP, UDP_IPC_PORT))

    for i in range(3):
        t = ThreadClass(i+1)
        t.start()

