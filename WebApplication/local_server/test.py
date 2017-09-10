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
elif(sys.argv[1] == 'connect'):
    jsonData = {
        "type": sys.argv[1]
    }
elif(sys.argv[1] == 'disconnect'):
    jsonData = {
        "type": sys.argv[1]
    }
elif(sys.argv[1] == 'rssi'):
    jsonData = {
        "type": sys.argv[1]
    }
import socket
import json

HOST, SERVERPORT = "localhost", 25805
CLIENTPORT = 30000

data = json.dumps(jsonData)

# Create a socket object
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(30)
# Define the port on which you want to connect
sock.bind((HOST, CLIENTPORT))

# connect to the server on local computer
sock.sendto(data, (HOST, SERVERPORT))

try:
    # receive data from the server
    received = sock.recv(1024)
except socket.error:
    received = "Unauthorized"
finally:
    sock.close()
    print received
