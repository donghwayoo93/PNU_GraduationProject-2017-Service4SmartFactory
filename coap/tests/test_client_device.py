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

coapInstServer = ''
coapBindServer = 'coap://[bbbb::1]:5685/bind'
binded_port    = 0

c_Inst   = ''
c_Bind   = coap.coap(udpPort=5689)

Instruction_List = ['']
Instruction_FLAG = False
Instruction_Data = ''

thread_index = 0
Sync_sem     = threading.Semaphore(1)


def getBindedPortNumber():
	print 'bind port number start \n'
	temp_port_num = 0
	allocated_port_str = c_Bind.GET(
			coapBindServer
	)
	temp_port_num = int(allocated_port_str)
	if((temp_port_num == 5686) | (temp_port_num == 5687) | (temp_port_num == 5688)):
		binded_port = temp_port_num
		print 'binded port : ' + str(binded_port)
	else:
		print 'error : '
		print 'Wrong Port Number received\n'


def openInstCoapClient(self, binded_port):
	print 'open Instruction coap client start \n'
	c_Inst = coap.coap(udpPort=binded_port)
	c_Inst.addResource(InstResource())
	coapInstServer = 'coap://[bbbb::1]:'+str(binded_port) + '/inst'


class InstResource(coapResource.coapResource):
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

    link         = 'coap://[bbbb::1]/client'

    SYN          = 0
    FIN          = 0
    ACK          = 0
    FRAG_1       = 0
    FRAG_N       = 0

    data_tag     = 0
    data_size    = 0
    total_offset = 0

    def __init__(self):
    	coapResource.coapResource.__init__(
    			self,
    			path='client'
    	)
        self.SYN      = 128
        self.FIN      = 64
        self.ACK      = 32
        self.FRAG_1   = 24
        self.FRAG_N   = 28

        # after initialize, conduct SYN phase
        self.SYN()

    def SYN(self):
        # send SYN to Server
        response = c_Inst.PUT(
        	coapInstServer,
        	payload=[ord(b) for b in 'I'+str(chr(self.SYN))]
        )
        self.SYN_dict['SYN'] = 1

        # Expecting response with SYN+ACK
        if(unichr(response[0]) == 'I'):
        	response = response[1:]
        	if((response[0] == (self.SYN + self.ACK)) &
        		(self.SYN_dict['SYN+ACK'] == 0)):

        		self.SYN_dict['SYN+ACK'] = 1

        		# send ACK to Server
        		c_Inst.PUT(
        			coapInstServer,
        			payload=[ord(b) for b in 'I'+str(chr(self.ACK))]
        		)
        		self.SYN_dict['ACK'] = 1


    def checkBuffer(self):
    	for i in range(self.total_offset):
    		if(Instruction_List[i] == ''):
    			return False
		return True


    def PUT(self, srcIP, options=[], payload=None):
    	if(unichr(payload[0]) =='I'):
    		payload = payload[1:]
    		# first fragmented packet
    		if(payload[0] == self.FRAG_1):
    			self.data_size = payload[1]
    			self.data_tag  = payload[2]
    			if(self.data_size > 50):
	    			# calculate total offset size
	    			self.total_offset = int(((self.data_size - 50) / 49) + 1)
	    			# allocate buffer with offset quantity
	    			Instruction_List = Instruction_List * self.total_offset

	    		# save first fragmented Instruction
	    		Instruction_List[0] = payload[3:]
	    	# second fragmented packet
	    	elif(payload[0] == self.FRAG_N):
	    		if((self.data_size == payload[1]) &
	    		   (self.data_tag == payload[2])):
	    			# payload[3] == data_offset, actual data starts from payload[4:]
	    			Instruction_List[payload[3]] = payload[4:]
	    			# last fragmented packet received
    				if(self.checkBuffer() == True):
    					Sync_sem.acquire()
    					Instruction_FLAG = True
    					Sync_sem.release()

    		elif((payload[0] == self.FIN) &
    			(self.FIN_dict['FIN_1'] == 0)):
    			self.FIN_dict['FIN_1'] = 1
    			# response with FIN_2
    			c_Inst.PUT(
    				coapInstServer,
    				payload=[ord(b) for b in 'I'+str(chr(self.FIN))]
    			)
    			self.FIN_dict['FIN_2'] = 1
    			# response with FIN_2
    			c_Inst.PUT(
    				coapInstServer,
    				payload=[ord(b) for b in 'I'+str(chr(self.ACK))]
    			)
    			self.FIN_dict['ACK_1'] = 1

    		elif((payload[0] == self.ACK) &
    			(self.FIN_dict['FIN_1'] == 1) &
    			(self.FIN_dict['FIN_2'] == 1) &
    			(self.FIN_dict['ACK_1'] == 1)):
    			# client received final ack termincate the connection with server
    			os.kill(os.getpid(), signal.SIGTERM)
    			self.FIN_dict['ACK_2'] = 1
				

	        respCode = d.COAP_RC_2_05_CONTENT
	        respOptions = []
	        respPayload = []

	        return (respCode, respOptions, respPayload)

    	else:
    		print 'error : '
    		print 'Wrong prefix in packet'
    		print str(payload[0]) + '\n'

class ThreadClass(threading.Thread):
	def __init__(self, index):
		threading.Thread.__init__(self)
		self.thread_index = index

	def run(self):
		if(self.thread_index == 1):
			print 'thread index == 1\n'
			Instruction_FLAG = False
			while(True):
				if(Instruction_FLAG == True):
					buf2string()
					Sync_sem.acquire()
					Instruction_FLAG = False
					Sync_sem.release()
					break

			signalClient()
		elif(self.thread_index == 2):
			raw_input('\n\nClient running. Press Enter to close.\n\n')
			os.kill(os.getpid(), signal.SIGTERM)

def buf2string(self):
	for i in range(len(Instruction_List)):
		Instruction_Data += Instruction_List[i]

def signalClient(self):
	# send to client side program
	# Instructio data
	print 'send instruction string data'


if __name__ == '__main__':
	for i in range(2):
		t = ThreadClass(i+1)
		t.start()

	getBindedPortNumber()
	openInstCoapClient(binded_port)
