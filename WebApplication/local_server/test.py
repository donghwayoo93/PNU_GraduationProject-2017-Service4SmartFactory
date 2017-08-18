import sys

email = sys.argv[1]
password = sys.argv[2]

# print sys.argv[0]


import socket
import json

HOST, PORT = "localhost", 25800
jsonData = {
    "type": "login",
    "email": email,
    "password": password
}
data = json.dumps(jsonData)

# Create a socket object
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Define the port on which you want to connect
port = 12345

# print "sent:        {}".format(data)

# connect to the server on local computer
sock.sendto(data, (HOST, PORT))

# receive data from the server
received = sock.recv(1024)


# print "received:    {}".format(received)
print "{}".format(received)
