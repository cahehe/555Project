#!/usr/bin/python3

import sdl2.ext
import math
import numpy.matlib
import numpy
import random
import World


def random_set(rover_num, rover_radius, bee_num, bee_radius):
    rover_list = []
    bee_list = []

    for i in range(rover_num):
        x = math.cos(i/rover_num*2*math.pi)*rover_radius
        y = math.sin(i/rover_num*2*math.pi)*rover_radius
        rover_list.append((x, y))

    for i in range(bee_num):
        x = random.uniform(-bee_radius, bee_radius)
        y = random.uniform(-bee_radius, bee_radius)
        bee_list.append((x, y))

    return rover_list, bee_list

def even_set(rover_num, rover_radius, bee_num, bee_radius):
    rover_list = []
    bee_list = []

    for i in range(rover_num):
        x = math.cos(i/rover_num*2*math.pi)
        y = math.sin(i/rover_num*2*math.pi)
        rover_list.append((x, y))

    for i in range(bee_num):
        for j in range(bee_num):
            bee_list.append(((i/(bee_num - 1) - 0.5)*2*bee_radius, (j/(bee_num - 1) - 0.5)*2*bee_radius))

    return rover_list, bee_list

def get_point_pixels(x, y):
    ORIGIN_X_PIXELS = 300
    ORIGIN_Y_PIXELS = 300
    PIXELS_PER_METER = 180
    return math.floor(x*PIXELS_PER_METER + ORIGIN_X_PIXELS), math.floor(y*PIXELS_PER_METER + ORIGIN_Y_PIXELS)

def draw_world(world):
    renderer.fill((0,0,600,600), color=sdl2.ext.Color(200,200,200))

    for node in world.node_list:
        for n in node.neighbors:
            x0, y0 = get_point_pixels(node.x, node.y)
            x1, y1 = get_point_pixels(n.x, n.y)
            renderer.draw_line((x0, y0, x1, y1), color=sdl2.ext.Color(100, 100, 100))

    for node in world.bee_list:
        x, y = get_point_pixels(node.x, node.y)
        bee_rect = (x - 3, y - 3, 7, 7)
        renderer.fill([bee_rect], color=sdl2.ext.Color(200, 0, 0))
        if node.px != None and node.py != None:
            px, py = get_point_pixels(node.px, node.py)
            pred_rect = (px - 5, py - 5, 11, 11)
            renderer.draw_rect([pred_rect], color=sdl2.ext.Color(200, 0, 0))
            renderer.draw_line((x, y, px, py), color=sdl2.ext.Color(200, 0, 0))

    for node in world.rover_list:
        x, y = get_point_pixels(node.x, node.y)
        rover_rect = (x - 4, y - 4, 9, 9)
        renderer.fill([rover_rect], color=sdl2.ext.Color(0, 0, 200))


def compare_methods():
    results = []

    for i in range(300):
        world = World.World(*random_set(3, 1.5, 20, 1.5))

        world.compute_dv_hop()
        dv_hop_error = world.rms_error()

        world.compute_dv_distance(0.05)
        dv_distance_error = world.rms_error()

        world.compute_direct_distance(0.05)
        direct_distance_error = world.rms_error()

        if dv_hop_error and dv_distance_error and direct_distance_error:
            results.append((dv_hop_error, dv_distance_error, direct_distance_error))

    print('# of tests surveyed: ' + str(len(results)))
    print('DV-Hop Error: ' + str(numpy.mean([r[0] for r in results])) + ' ± ' + str(numpy.std([r[0] for r in results])))
    print('DV-Distance Error: ' + str(numpy.mean([r[1] for r in results])) + ' ± ' + str(numpy.std([r[1] for r in results])))
    print('Direct Ping Error: ' + str(numpy.mean([r[2] for r in results])) + ' ± ' + str(numpy.std([r[2] for r in results])))

def compute_and_draw():
    world = World.World(*random_set(3, 1.5, 20, 1.5))
    #world = World.World(*even_set(3, 1, 4, 0.6))
    world.compute_dv_hop()
    #world.compute_dv_distance(0.2)
    #world.compute_direct_distance(0.2)

    draw_world(world)
    renderer.present()

    print('RMS Error: ' + str(world.rms_error()))

def interactive_mode():
    sdl2.ext.init()
    window = sdl2.ext.Window("Simulation View", size=(600, 600))
    window.show()
    renderer = sdl2.ext.Renderer(window)

    compute_and_draw()

    quit = False
    while not quit:
        events = sdl2.ext.get_events()
        for event in events:
            if event.type == sdl2.SDL_QUIT:
                quit = True
            if event.type == sdl2.SDL_KEYDOWN:
                compute_and_draw()

compare_methods()

#interactive_mode()

