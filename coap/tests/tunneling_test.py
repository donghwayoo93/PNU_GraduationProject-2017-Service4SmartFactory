from coap import coap

import os
import signal
import sys
here = sys.path[0]
sys.path.insert(0, os.path.join(here,'..'))

import threading
import time

uri = 'coap://[bbbb::2]:5685'
thread_index = 0

c = coap.coap(udpPort=5685)
input = ''


class ThreadClass(threading.Thread):
    def __init__(self, index):
        threading.Thread.__init__(self)
        self.thread_index = index

    def run(self):
    	if(self.thread_index == 1):
    		recv = ''
    		while True:
				recv = c.PUT(
					uri+'/inst',
					payload=[ord(b) for b in 'test_string']
				)
				print recv
				time.sleep(15)


    	elif(self.thread_index == 2):
    		raw_input('\n\nServer running. Press Enter to close.\n\n')
    		os.kill(os.getpid(), signal.SIGTERM)	


if __name__ == '__main__':
	for i in range(2):
		t = ThreadClass(i+1)
		t.start()

	

