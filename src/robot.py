#!/usr/bin/python3

from PacketRW import PacketRW

import json
import socket

server_host = '127.0.0.1'
server_port = 8889
robot_id = 1

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as serverSock:
    serverSock.connect((server_host, server_port))

    rw = PacketRW(serverSock)
    rw.send({'type': 'strength_request'})
    print('received response ', repr(rw.recv()))
    rw.send({'type': 'move_request', 'dx': 0.5, 'dy': 0.5})
    rw.send({'type': 'position_prediction', 'px': 0.5, 'py': 0.5})


