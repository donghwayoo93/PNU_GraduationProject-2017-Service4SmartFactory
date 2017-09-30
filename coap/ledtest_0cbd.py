'''
from coap import coap

import signal
import os

uri = 'coap://[bbbb::1415:9200:1862:0cbd]/l'

c = coap.coap()

p = c.GET(uri)
print chr(p[0])

c.PUT(
    uri,
    payload=[ord('2')],
)

p = c.GET(uri)
print chr(p[0])

while True:
        input = raw_input("Done. Press q to close. ")
        if input=='q':
            print 'bye bye.'
            #c.close()
            os.kill(os.getpid(), signal.SIGTERM)
            '''
this = ' 123456'

print this
print this[1:]