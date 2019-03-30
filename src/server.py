#!/usr/bin/python3

import json
import random
import socket
import threading
import time

server_host = '127.0.0.1'
server_port = 8888


last_robot_id = 0
robots = dict()

robots_lock = threading.Lock()

class Robot:
    def __init__(self):
        self.x = random.random()*10
        self.y = random.random()*10
        self.px = None
        self.py = None

def new_robot():
    with robots_lock:
        # Generate a new robot id
        global last_robot_id
        global robots
        robot_id = last_robot_id + 1
        last_robot_id = robot_id
        # Create a new robot object and assign in dictionary
        robot = Robot()
        robots[robot_id] = robot
        return robot_id, robot

def remove_robot(robot_id):
    with robots_lock:
        global robots
        robots[robot_id] = None


def handle_strength_request(robot):
    # it takes time to sample
    time.sleep(1)
    with robots_lock:
        # TODO: actually compute strengths based on hotspots
        return [1, 2, 3, 4, 5]

def handle_move_request(robot, delta_x, delta_y):
    # it takes time to move
    time.sleep(1)
    with robots_lock:
        # apply motion
        robot.x = delta_x*random.uniform(10/9, 9/10)
        robot.y = delta_y*random.uniform(10/9, 9/10)
        pass

def handle_position_prediction(robot, px, py):
    with robots_lock:
        robot.px = px
        robot.py = py

class PacketRW:
    def __init__(self, conn):
        self.all_bytes = bytes()
        self.conn = conn

    def recv(self):
        while True:
            # find the first complete packet in the buffer
            pos = self.all_bytes.find(b'\x00')
            if pos == -1:
                # no valid packets in buffer, receive more data
                self.all_bytes += self.conn.recv(1024)
            else:
                #print('all_bytes:', repr(self.all_bytes))
                # a packet is in the buffer, decode and return
                packet = self.all_bytes[0:pos]
                self.all_bytes = self.all_bytes[pos+1:]
                #print('all_bytes (after removal):', repr(self.all_bytes))
                return json.loads(packet)

    def send(self, d):
        json_packet = json.dumps(d, separators=(',', ':'))
        self.conn.sendall(json_packet.encode() + b'\x00')

def robot_thread(conn, addr):
    # create a robot for this connection
    robot_id, robot = new_robot()
    print('connection from ', addr)
    print(f'robot id: {robot_id}')

    rw = PacketRW(conn)
    while True:
        d = rw.recv()
        print(repr(d))

        if d['type'] == 'strength_request':
            strengths = handle_strength_request(robot)
            rw.send({'type': 'strengths', 'strengths': strengths})
        elif d['type'] == 'move_request':
            handle_move_request(robot, d['dx'], d['dy'])
        elif d['type'] == 'position_prediction':
            handle_position_prediction(robot, d['px'], d['py'])

    # close this connection
    print('closing connection ', addr)
    conn.sendall(b'goodbye')
    conn.close()
    # remove this connection's robot
    remove_robot(robot_id)


# start TCP server
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((server_host, server_port))
    s.listen()
    # spawn a robot thread for each incoming connection
    while True:
        conn, addr = s.accept()
        thread = threading.Thread(target=robot_thread, args=(conn, addr))
        thread.start()

