#
#   2017.07.09
#   modified by Yoo DongHwa
#

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
        recv_data  = dict['rssi_to_meter']

        # original recv_addr form is ex) "14-15-92-cc-00-00-00-01"
        recv_addr = recv_addr.split('-')

        moteipv6Addr      = ""

        for i in range(0, 8):
            if(i % 2 == 0):
                if(i == 0):
                    # this is prefix
                    moteipv6Addr += "bbbb::" + recv_addr[i].zfill(2) + recv_addr[i + 1].zfill(2) + ":"
                else:
                    moteipv6Addr += recv_addr[i].zfill(2) + recv_addr[i + 1].zfill(2) + ":"
                    
        # delete last colon ":"
        moteipv6Addr = moteipv6Addr[0:len(moteipv6Addr) - 1]

        print moteipv6Addr
        print recv_data

        socket.sendto(data.upper(), self.client_address)

        


if __name__ == "__main__":
    HOST = "localhost"
    PORT = 25801
    # server receives packet from
    # openwsn-sw\software\openvisualizer\openvisualizer\moteState\moteState.py L273
    server = SocketServer.UDPServer((HOST, PORT), UDPHandler)
    server.serve_forever()