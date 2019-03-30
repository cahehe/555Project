#!/usr/bin/python3

import json
import socket

server_host = '127.0.0.1'
server_port = 8888
robot_id = 1

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as serverSock:
    serverSock.connect((server_host, server_port))

    json_packet = json.dumps({'type': 'strength_request'}, separators=(',', ':'))
    serverSock.sendall(json_packet.encode() + b'\x00')

    json_packet = json.dumps({'type': 'move_request', 'dx': 0.5, 'dy': 0.5}, separators=(',', ':'))
    serverSock.sendall(json_packet.encode() + b'\x00')

    json_packet = json.dumps({'type': 'position_prediction', 'px': 0.5, 'py': 0.5}, separators=(',', ':'))
    serverSock.sendall(json_packet.encode() + b'\x00')

    data = serverSock.recv(1024)


print('received response ', repr(data))

