#!/usr/bin/python3

from PacketRW import PacketRW
from Hotspot import Hotspot
from Robot import Robot

import json
import math
import random
import select
import socket
import sys
import threading
import time
import sdl2.ext


quit_event = threading.Event()


server_host = '127.0.0.1'
server_port = 8888


last_robot_id = 0
robots = dict()

hotspots = [Hotspot(1, 1), Hotspot(5, 5), Hotspot(3, 4)]

world_lock = threading.Lock()

def new_robot():
    with world_lock:
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
    with world_lock:
        global robots
        robots[robot_id] = None

def handle_strength_request(robot):
    # it takes time to sample
    time.sleep(1)
    with world_lock:
        # TODO: actually compute strengths based on hotspots
        return [1, 2, 3, 4, 5]

def handle_move_request(robot, delta_x, delta_y):
    # it takes time to move
    time.sleep(1)
    with world_lock:
        # apply motion
        robot.x = robot.x + delta_x*random.uniform(10/9, 9/10)
        robot.y = robot.y + delta_y*random.uniform(10/9, 9/10)
        pass

def handle_position_prediction(robot, px, py):
    with world_lock:
        robot.px = px
        robot.py = py

def get_draw_data():
    global robots
    global hotspots
    robots_out = []
    hotspots_out = []
    with world_lock:
        for robot in robots.values():
            robots_out.append((robot.x, robot.y, robot.px, robot.py))
        for hotspot in hotspots:
            hotspots_out.append((hotspot.x, hotspot.y))
    return robots_out, hotspots_out

def robot_thread(conn, addr):
    # create a robot for this connection
    robot_id, robot = new_robot()
    print('connection from ', addr)
    print(f'robot id: {robot_id}')

    rw = PacketRW(conn)
    while not quit_event.is_set():
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

def server_task():
    allthreads = []
    # start TCP server
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((server_host, server_port))
        s.listen()
        # spawn a robot thread for each incoming connection
        while not quit_event.is_set():
            conn, addr = s.accept()
            thread = threading.Thread(target=robot_thread, args=(conn, addr))
            thread.start()
            allthreads.append(thread)

def draw():
    renderer.fill((0,0,400,400), color=sdl2.ext.Color(200,200,200))

    PIXELS_PER_METER = 40

    robots, hotspots = get_draw_data()

    for r in robots:
        x = math.floor(r[0]*PIXELS_PER_METER)
        y = math.floor(r[1]*PIXELS_PER_METER)
        robot_rect = (x - 5, y - 5, 11, 11)
        renderer.draw_rect([robot_rect], color=sdl2.ext.Color(200, 0, 0))
        if r[2] and r[3]:
            px = math.floor(r[2]*PIXELS_PER_METER)
            py = math.floor(r[3]*PIXELS_PER_METER)
            pred_rect = (px - 2, py - 2, 5, 5)
            renderer.fill([pred_rect], color=sdl2.ext.Color(200, 0, 0))
            renderer.draw_line((x, y, px, py), color=sdl2.ext.Color(200, 0, 0))

    for h in hotspots:
        x = math.floor(h[0]*PIXELS_PER_METER)
        y = math.floor(h[1]*PIXELS_PER_METER)
        renderer.draw_line((x - 5, y - 5, x + 5, y + 5), color=sdl2.ext.Color(0, 0, 200))
        renderer.draw_line((x + 5, y - 5, x - 5, y + 5), color=sdl2.ext.Color(0, 0, 200))

    renderer.present()

# spawn server listen
server_thread = threading.Thread(target=server_task)
server_thread.start()

sdl2.ext.init()
window = sdl2.ext.Window("Simulation View", size=(400, 400))
window.show()
renderer = sdl2.ext.Renderer(window)

draw()

while not quit_event.is_set():
    events = sdl2.ext.get_events()
    for event in events:
        if event.type == sdl2.SDL_QUIT:
            quit_event.set()
            print('quit signal set')
    draw()
    sdl2.SDL_Delay(16)

sdl2.ext.quit()

print('waiting for threads to exit...')

