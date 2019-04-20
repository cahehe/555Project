#!/usr/bin/python3

import math

class Node:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.neighbors = []
        self.dv_table = {}

#rover_list = [ Rover('r1', 0, 0), Rover('r2', 1, 0), Rover('r3', 1, 1), Rover('r4', 0, 1) ];
#bee_list = [ Node('b1', 0.5, 0.5) ];

rover_list = [
    Node('r1', 0, 0),
    Node('r2', 0, 2),
];

bee_list = [
    Node('b1', 0.5, 0.5),
    Node('b2', 1.0, 1.0),
    Node('b3', 1.5, 1.5),
    Node('b4', 0.0, 1.0),
    Node('b5', 0.5, 1.5),
];

node_list = rover_list + bee_list

def distance(a, b):
    return math.sqrt((a.x - b.x)*(a.x - b.x) + (a.y - b.y)*(a.y - b.y))

def find_node(id):
    for node in node_list:
        if node.id == id:
            return node
    return None

def triangulate(tri_data):
    prediction_list = []

    for i1 in range(len(tri_data)):
        t1 = tri_data[i1]
        for i2 in range(i1 + 1, len(tri_data)):
            t2 = tri_data[i2]
            AB = (t2[0] - t1[0], t2[1] - t1[1])
            d = math.sqrt(AB[0]*AB[0] + AB[1]*AB[1])
            l1 = t1[2]
            l2 = t2[2]
            if l1 + l2 < d:
                # No solution here
                continue
            # Possible angle opposite from l2
            theta = math.acos((d*d + l1*l1 - l2*l2)/(2*d*l1))
            AC1 = (math.cos(theta)*AB[0]*l1/d + math.sin(theta)*AB[1]*l1/d, -math.sin(theta)*AB[0]*l1/d + math.cos(theta)*AB[1]*l1/d)
            AC2 = (math.cos(theta)*AB[0]*l1/d - math.sin(theta)*AB[1]*l1/d,  math.sin(theta)*AB[0]*l1/d + math.cos(theta)*AB[1]*l1/d)
            guess1 = (AC1[0] + t1[0], AC1[1] + t1[1])
            guess2 = (AC2[0] + t2[0], AC2[1] + t2[1])
            print("theta: " + str(theta))
            print("guess1: " + str(guess1))
            print("guess2: " + str(guess2))

    return 0, 0

max_range = 0.9

for node in node_list:
    for other_node in node_list:
        if node != other_node:
            d = distance(node, other_node)
            if d < max_range:
                node.neighbors.append(other_node)

for rover in rover_list:
    rover.dv_table[rover.id] = 0

    for iteration in range(10):
        for node in node_list:
            if rover.id in node.dv_table:
                for n in node.neighbors:
                    # Send the DV packet
                    if not rover.id in n.dv_table or node.dv_table[rover.id] + 1 < n.dv_table[rover.id]:
                        print(node.id + ' updating neighbor ' + n.id + ' to ' + str(node.dv_table[rover.id] + 1))
                        n.dv_table[rover.id] = node.dv_table[rover.id] + 1

# Calculate distance per hop approximation (correction) per rover
for rover in rover_list:
    cv_distsum = 0
    cv_hopsum = 0
    # Total distances and hops to all other rovers
    for other_rover in rover_list:
        if rover != other_rover:
            cv_distsum += distance(rover, other_rover)
            cv_hopsum += rover.dv_table[other_rover.id]
    # Correction value is quotient of these
    rover.cv = cv_distsum / cv_hopsum

# Hand waving: Assume corrections have flooded the network

for node in node_list:
    # Find the closest rover to each bee in terms of hops
    if node in rover_list:
        # Rovers need not apply
        continue

    nearest_rover_id = min(node.dv_table, key=node.dv_table.get)
    print('closest rover to node ' + node.id + ': ' + nearest_rover_id)

    nearest_rover = find_node(nearest_rover_id)
    # This is the cv that would have arrived
    node.cv = nearest_rover.cv

    tri_data = []
    for rover in rover_list:
        dist_estimate = node.cv * node.dv_table[rover.id]
        tri_data.append((rover.x, rover.y, dist_estimate))

    # Calculate position from approximate rover distances
    node.px, node.py = triangulate(tri_data)

print('[nodes]')
print(len(node_list))
for node in node_list:
    print(node.id)
    print(node.x, node.y)
    print(len(node.neighbors))
    print('neighbors: ' + ' '.join(b.id for b in node.neighbors))
    print('correction: ' + str(node.cv))
    for rover in rover_list:
        print('hops to ' + rover.id + ': ' + str(node.dv_table[rover.id]))
        print('approximate distance to rover ' + rover.id + ': ' + str(node.cv * node.dv_table[rover.id]))
        print('actual distance to rover ' + rover.id + ': ' + str(distance(node, rover)))

