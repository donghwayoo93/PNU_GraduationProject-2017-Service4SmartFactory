from coap import coap

import signal
import os

# created by Yoo DongHwa
# 2017-07-10
# send coap packet to mote's specific uri path
# openwsn-fw/openapps/cinfo/cinfo.c
# openwsn-fw/openapps/cleds/cleds.c
# openwsn-fw/openapps/cexample/cexample.c

# uri = 'coap://[bbbb::1415:9200:13e1:b83c]/'
# uri = 'coap://[bbbb::1415:9200:1826:0e94]/'
uri = 'coap://[bbbb::1415:92cc:0000:0003]/'

moteip = ''
input_uri = ''
uri_path_available = 0
count = 0

# input_uri = input('type mote ipv6 addr  ex)bbbb::1415:9200:13e1:b83c')
# uri = 'coap://[' + input_uri + ']/'

while True:

    print 'coap test client file'
    input_uri = raw_input('type uri\n')

    if(input_uri == 'i'):
        uri_path_available = 1
    elif(input_uri == 'l'):
        uri_path_available = 1
    elif(input_uri == 'ex'):
        uri_path_available = 1
    else:
        print 'unavailable uri path'
        while True:
            input = raw_input("Press q to close. ")
            if input=='q':
                print 'bye bye.'
                os.kill(os.getpid(), signal.SIGTERM)

    if(uri_path_available == 1):
        if(count == 0):
            c = coap.coap()
            print 'coap object created'

        print 'uri is ' + uri + input_uri

    if(input_uri == 'i'):
        # only GET
        recv = c.GET(uri+input_uri)
        print_str = ''
        for s in recv:
            print_str += chr(s)

        print print_str

    elif(input_uri == 'l'):
        # GET and PUT
        input_code = raw_input("GET or PUT (case sensitive)\n")

        if(input_code == "GET"):
            recv = c.GET(uri+input_uri)
            print_str = ''

            for s in recv:
                print_str += chr(s)

            print print_str

        elif(input_code == "PUT"):
            to_send = raw_input('input a byte to send (0 = off, 1 = on, 2 = toggle)\n')
            recponse = c.PUT(
                uri+input_uri,
                payload=[ord(to_send)]
            )

            print_str = 'response : '
            for s in recponse:
                print_str += chr(s)

            print print_str
            print 'PUT send Done'

    elif(input_uri == 'ex'):
        # GET and PUT
        input_code = raw_input("GET or PUT (case sensitive)\n")

        if(input_code == "GET"):
            recv = c.GET(uri+input_uri)
            print_str = ''

            for s in recv:
                print_str += chr(s)

            print print_str

        elif(input_code == "PUT"):
            to_send = raw_input('input a byte to send (7 = working)\n')
            response = c.PUT(
                uri+input_uri,
                payload=[to_send]
            )

            print_str = 'response : '

            for s in response:
                print_str += chr(s)

            print 'PUT send Done'
            print print_str

    input = raw_input("Done. Press q to close. or enter other")
    if input=='q':
        print 'bye bye.'
        #c.close()
        os.kill(os.getpid(), signal.SIGTERM)
    else:
        uri_path_available = 0
        count = 1
        continue