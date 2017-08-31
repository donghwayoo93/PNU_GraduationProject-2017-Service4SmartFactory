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

UDP_IP               = 'bbbb::2'
UDP_PORT             = 25801

TUN_DST_IP           = 'bbbb::1'
TUN_DST_PORT         = 25800

UDP_IPC_IP           = 'localhost'
UDP_IPC_PORT         = 25805

SEND_OUT_SEMAPHORE   = threading.Semaphore(1)
SEND_IN_SEMAPHORE    = threading.Semaphore(1)
CONN_SEMAPHORE       = threading.Semaphore(1)
INST_SEMAPHORE       = threading.Semaphore(1)

sock                 = ''
sock_internal        = ''
Instruction_String   = ''

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

        self.SYN      = 128
        self.FIN      = 64
        self.ACK      = 32
        self.FRAG_1   = 24
        self.FRAG_N   = 28

    def _sendSYN(self):
        # 3-handshake ---------------------------------------- 1
        self.SYN_dict['SYN'] = 1
        self.msg             = 'C'+str(chr(self.SYN))
        SEND_OUT_SEMAPHORE.acquire()
        sock.sendto(self.msg, (TUN_DST_IP, TUN_DST_PORT))
        SEND_OUT_SEMAPHORE.release()

    def _handle(self, data):
        # client receives SYN+ACK pkt
        # response with ACK pkt and ready for other data
        if((self.SYN_dict['SYN'] == 1) &
           (self.SYN_dict['SYN+ACK'] == 0) &
           (data[0] == self.SYN + self.ACK)):
            print 'client received SYN+ACK'
            # 3-handshake ------------------------------------ 2
            self.SYN_dict['SYN+ACK'] = 1
            self.SYN_dict['ACK']     = 1
            self.msg                 = 'C'+str(chr(self.ACK))
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
            self.msg               = 'C'+str(chr(self.FIN))
            sock.sendto(self.msg, (TUN_DST_IP, TUN_DST_PORT))
            # 4-handshake ------------------------------------ 3
            print 'client send ACK_1'
            self.msg               = 'C'+str(chr(self.ACK))
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

    def _recvInstructionData(self, payload):

        if(payload[0] == self.FRAG_1):
            print 'client received FRAG_1'
            self.Instruction_size      = payload[1]
            self.Instruction_tag       = payload[2]
            self.Instruction_List_size = int((self.Instruction_size - 50) / 49 + 1)
            self.Instruction_List      = self.Instruction_List * self.Instruction_List_size
            self.Instruction_List[0]   = payload[3:]

        elif(payload[0] == self.FRAG_N):
            print 'client received FRAG_N : ' + str(payload[3]) + 'th'
            if(self.Instruction_tag == payload[2]):
                self.Instruction_List[payload[3]] = payload[4:]

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
        # make fragmented string to one
        INST_SEMAPHORE.acquire()
        for i in range(self.Instruction_List_size):
            Instruction_String += self.Instruction_List[i]
        INST_SEMAPHORE.release()

        print 'client makeString'

        # send instruction string internal
        SEND_IN_SEMAPHORE.acquire()
        sock_internal.sendto(Instruction_List, (UDP_IPC_IP, UDP_IPC_PORT))
        SEND_IN_SEMAPHORE.release()


class LoginClass:
    msg = ''
    def __init__(self):
        self.msg = 'L'

    def _login(self, payload):
        self.msg += str(payload)
        # toss login data to outer
        SEND_OUT_SEMAPHORE.acquire()
        sock.sendto(self.msg, (TUN_DST_IP, TUN_DST_PORT))
        SEND_OUT_SEMAPHORE.release()

    def _recvResult(self, payload):
        self.msg = 'L'+str(payload)
        # toss login result to internal
        SEND_IN_SEMAPHORE.acquire()
        sock_internal.sendto(self.msg, (UDP_IPC_IP, UDP_IPC_PORT))
        SEND_IN_SEMAPHORE.release()


class ThreadClass(threading.Thread):
	def __init__(self, index):
		threading.Thread.__init__(self)
		self.thread_index = index

	def run(self):
	    if(self.thread_index == THREAD_IPV6_UDP_SOCK):
                print 'client send syn'
                conn._sendSYN()
                while True:
                    data, addr = sock.recvfrom(127)
                    
                    if(data[0] == 'I'):
                        inst._recvInstructionData(data[1:])

                    elif(data[0] == 'C'):
                        conn._handle(data[1:])

                    # login result from outer server
                    elif(data[0] == 'L'):
                        # send this result to internal
                        login._recvResult(data[1:])

            elif(self.thread_index == THREAD_UDP_IPC_SOCK):
                while True:
                    data, addr = sock_internal.recvfrom(1024)

                    # login request from internal
                    if(data[0] == 'L'):
                        # send this request to outer server
                        login._login(data[1:])

	    elif(self.thread_index == THREAD_SYSKILL):
			raw_input('\n\nClient running. Press Enter to close.\n\n')
			os.kill(os.getpid(), signal.SIGTERM)

if __name__ == '__main__':
    
    conn                 = ConnectionClass()
    inst                 = InstructionClass()
    login                = LoginClass()
    
    
    
    sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))

    sock_internal = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock_internal.bind((UDP_IPC_IP, UDP_IPC_PORT))

    for i in range(3):
            t = ThreadClass(i+1)
            t.start()

