import sys
jsonData = {}
if(sys.argv[1] == 'login'):
    email = sys.argv[2]
    password = sys.argv[3]
    jsonData = {
        "type": "login",
        "email": email,
        "password": password
    }
elif(sys.argv[1] == 'machineInfo'):
    jsonData = {
        "type": sys.argv[1]
    }
elif(sys.argv[1] == 'machineSensor'):
    jsonData = {
        "type": sys.argv[1]
    }
elif(sys.argv[1] == 'machineManual'):
    jsonData = {
        "type": sys.argv[1]
    }
import socket
import json

HOST, PORT = "localhost", 25805
CLIENTPORT = 30000

data = json.dumps(jsonData)

# Create a socket object
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Define the port on which you want to connect
port = 12345
sock.bind((HOST, CLIENTPORT))

# connect to the server on local computer
sock.sendto(data, (HOST, PORT))

# receive data from the server
received = sock.recv(1024)

sock.close()

print received
