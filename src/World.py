
import random
import threading
import time

class Robot:
    def __init__(self):
        self.x = random.random()*10
        self.y = random.random()*10
        self.px = None
        self.py = None

class Hotspot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class World:
    def __init__(self):
        self.lock = threading.Lock()
        self.last_robot_id = 0
        self.robots = dict()
        self.hotspots = [Hotspot(1, 1), Hotspot(5, 5), Hotspot(3, 4)]

    def new_robot(self):
        with self.lock:
            # Generate a new robot id
            robot_id = self.last_robot_id + 1
            self.last_robot_id = robot_id
            # Create a new robot object and assign in dictionary
            robot = Robot()
            self.robots[robot_id] = robot
            return robot_id, robot

    def remove_robot(self, robot_id):
        with self.lock:
            self.robots[robot_id] = None

    def handle_strength_request(self, robot):
        # it takes time to sample
        time.sleep(1)
        with self.lock:
            # TODO: actually compute strengths based on self.hotspots
            return [1, 2, 3, 4, 5]

    def handle_move_request(self, robot, delta_x, delta_y):
        # it takes time to move
        time.sleep(1)
        with self.lock:
            # apply motion
            robot.x = robot.x + delta_x*random.uniform(10/9, 9/10)
            robot.y = robot.y + delta_y*random.uniform(10/9, 9/10)
            pass

    def handle_position_prediction(self, robot, px, py):
        with self.lock:
            robot.px = px
            robot.py = py

    def get_draw_data(self):
        robots_out = []
        hotspots_out = []
        with self.lock:
            for robot in self.robots.values():
                robots_out.append((robot.x, robot.y, robot.px, robot.py))
            for hotspot in self.hotspots:
                hotspots_out.append((hotspot.x, hotspot.y))
        return robots_out, hotspots_out

