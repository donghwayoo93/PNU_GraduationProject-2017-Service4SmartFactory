from coap import coap

import signal
import os

c = coap.coap()

p = c.GET('coap://[bbbb::1415:9200:1826:1eec]:5683/l')
print chr(p[0])

c.PUT(
    'coap://[bbbb::1415:9200:1826:1eec]:5683/l',
    payload=[ord('2')],
)

p = c.GET('coap://[bbbb::1415:9200:1826:1eec]:5683/l')
print chr(p[0])

#while True:
#        input = raw_input("Done. Press q to close. ")
#        if input=='q':
#            print 'bye bye.'
c.close()
os.kill(os.getpid(), signal.SIGTERM)