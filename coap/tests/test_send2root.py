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

UDP_IP = "bbbb::1" # localhost
UDP_PORT = 25801

sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)



class ThreadClass(threading.Thread):
    def __init__(self, index):
        threading.Thread.__init__(self)
        self.thread_index = index

    def run(self):
        if(self.thread_index == 1):
           while True:
               sock.sendto('string to rasp', (UDP_IP, UDP_PORT))
               time.sleep(15)

        elif(self.thread_index == 2):
            raw_input('\n\nServer running. Press Enter to close.\n\n')
            os.kill(os.getpid(), signal.SIGTERM)





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

if __name__ == "__main__":

    for i in range(2):
        t = ThreadClass(i+1)
        t.start()