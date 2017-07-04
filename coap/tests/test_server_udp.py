import SocketServer
import json

class UDPHandler(SocketServer.BaseRequestHandler):

    def handle(self):
        data = self.request[0]
        socket = self.request[1]

        # json decode
        dict = json.loads(data)

        # save decoded json string by each identifier
        recv_addr = dict['moteipv6Addr']
        recv_data  = dict['moteDataStr']

        # remove [, ] located first of string and end of string
        recv_addr = recv_addr[1:len(recv_addr) - 1].split(',')
        recv_data = recv_data[1:len(recv_data) - 1].split(',')

        # moteipv6Addr & moteDataStr
        moteipv6Addr_temp = []
        moteipv6Addr      = ""
        moteDataStr       = ""
        MarkerFlag        = False

        for a in recv_addr:
            # remove preceding zeros
            # change str to int to hex
            moteipv6Addr_temp.append(format(int(a), 'x'))

        for i in range(0, 16):
            if(i % 2 == 0):
                if(i == 0):
                    # this is prefix
                    moteipv6Addr += moteipv6Addr_temp[i].zfill(2) + moteipv6Addr_temp[i + 1].zfill(2) + ":"
                elif(moteipv6Addr_temp[i] != '0'):
                    moteipv6Addr += moteipv6Addr_temp[i].zfill(2) + moteipv6Addr_temp[i + 1].zfill(2) + ":"
                elif((moteipv6Addr_temp[i] == '0') & (moteipv6Addr_temp[i + 1] == '0') & (MarkerFlag == False)):
                    # represent sequence of zeros to ::
                    moteipv6Addr += ":"
                    MarkerFlag = True
                    
        # delete last colon ":"
        moteipv6Addr = moteipv6Addr[0:len(moteipv6Addr) - 1]

        # initialize MarkerFlag var to use in next for loop
        MarkerFlag = False

        for a in recv_data:
            # check CoAP_PAYLOAD_MARKER (0xFF)
            if(int(a) == 255):
                MarkerFlag = True
                continue

            if(MarkerFlag == True):
                # change str to int to hex
                moteDataStr += format(int(a), 'x')

        MarkerFlag = False

        print moteipv6Addr
        print moteDataStr

        socket.sendto(data.upper(), self.client_address)

        


if __name__ == "__main__":
    HOST = "localhost"
    PORT = 25800

    server = SocketServer.UDPServer((HOST, PORT), UDPHandler)
    server.serve_forever()