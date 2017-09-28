#!/usr/bin/env python

import zmq

context = zmq.Context()
socket = context.socket(zmq.REQ)

socket.connect("tcp:://localhost:50001")

socket.send_json({"sub": ["bonjour"]})

message = socket.recv_unicode()

print message