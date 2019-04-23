
import math
import numpy.matlib

class Node:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.neighbors = []
        self.dv_table = {}
        self.px = None
        self.py = None

# Returns the actual distance between two nodes
def distance(a, b):
    return math.sqrt((a.x - b.x)*(a.x - b.x) + (a.y - b.y)*(a.y - b.y))

def triangulate(tri_data):
    # tri_data should be of the form: [(x, y, dist), (x, y, dist), ... ]

    # Satellite locations
    sat_0_location = numpy.array([tri_data[0][0], tri_data[0][1]])
    sat_1_location = numpy.array([tri_data[1][0], tri_data[1][1]])
    sat_2_location = numpy.array([tri_data[2][0], tri_data[2][1]])

    # Satellite distances
    rho_0 = tri_data[0][2]
    rho_1 = tri_data[1][2]
    rho_2 = tri_data[2][2]

    # Estimated location
    ru_hat = numpy.array((sat_0_location + sat_1_location + sat_2_location)/3)

    for i in range(10):
        # Calculate distances from current estimate to satellite locations
        rho_0_hat = numpy.linalg.norm(sat_0_location - ru_hat)
        rho_1_hat = numpy.linalg.norm(sat_1_location - ru_hat)
        rho_2_hat = numpy.linalg.norm(sat_2_location - ru_hat)

        # Calculate unit vector in direction of satellite
        unit_0 = (sat_0_location - ru_hat)/rho_0_hat
        unit_1 = (sat_1_location - ru_hat)/rho_1_hat
        unit_2 = (sat_2_location - ru_hat)/rho_2_hat

        # Set up linear equation for approximate adjustment
        delta_rho_vector = numpy.matrix([rho_0_hat - rho_0, rho_1_hat - rho_1, rho_2_hat - rho_2]).T
        unit_vector_matrix = numpy.matrix([[unit_0[0], unit_0[1]], [unit_1[0], unit_1[1]], [unit_2[0], unit_2[1]]])

        # Solve linear equation
        delta_ru_hat = numpy.linalg.inv(unit_vector_matrix.T*unit_vector_matrix)*unit_vector_matrix.T*delta_rho_vector

        # Apply adjustment
        ru_hat[0] += delta_ru_hat[0]
        ru_hat[1] += delta_ru_hat[1]

    return ru_hat[0], ru_hat[1]

class World:
    def __init__(self, rover_positions, bee_positions):
        self.rover_list = []
        index = 0
        for pos in rover_positions:
            self.rover_list.append(Node('r' + str(index), *pos))
            index += 1

        self.bee_list = []
        index = 0
        for pos in bee_positions:
            self.bee_list.append(Node('b' + str(index), *pos))
            index += 1

        self.node_list = self.rover_list + self.bee_list

        # Always use normalized range
        max_range = 1.0

        # Compute neighboring nodes
        for node in self.node_list:
            for other_node in self.node_list:
                if node != other_node:
                    d = distance(node, other_node)
                    if d < max_range:
                        node.neighbors.append(other_node)

    # Looks up a node by id
    def find_node(self, id):
        for node in self.node_list:
            if node.id == id:
                return node
        return None

    def clear_computation(self):
        for node in self.node_list:
            node.dv_table = {}
            node.px = None
            node.py = None

    def compute_dv_hop(self):
        self.clear_computation()

        for rover in self.rover_list:
            rover.dv_table[rover.id] = 0

            for iteration in range(10):
                for node in self.node_list:
                    if rover.id in node.dv_table:
                        for n in node.neighbors:
                            # Send the DV packet
                            if not rover.id in n.dv_table or node.dv_table[rover.id] + 1 < n.dv_table[rover.id]:
                                #print(node.id + ' updating neighbor ' + n.id + ' to ' + str(node.dv_table[rover.id] + 1))
                                n.dv_table[rover.id] = node.dv_table[rover.id] + 1

        # Calculate distance per hop approximation (correction) per rover
        for rover in self.rover_list:
            cv_distsum = 0
            cv_hopsum = 0
            # Total distances and hops to all other rovers
            for other_rover in self.rover_list:
                if rover != other_rover:
                    if not other_rover.id in rover.dv_table:
                        return False, 'Nodes are not strongly connected'

                    cv_distsum += distance(rover, other_rover)
                    cv_hopsum += rover.dv_table[other_rover.id]
            # Correction value is quotient of these
            rover.cv = cv_distsum / cv_hopsum

        # Hand waving: Assume corrections have flooded the network

        for node in self.node_list:
            # Find the closest rover to each bee in terms of hops
            if node in self.rover_list:
                # Rovers need not apply
                continue

            if len(node.dv_table) < 3:
                # This node was not reached by enough rovers, ignore
                continue

            nearest_rover_id = min(node.dv_table, key=node.dv_table.get)

            nearest_rover = self.find_node(nearest_rover_id)
            # This is the cv that would have arrived
            node.cv = nearest_rover.cv

            tri_data = []
            for rover in self.rover_list:
                dist_estimate = node.cv * node.dv_table[rover.id]
                tri_data.append((rover.x, rover.y, dist_estimate))

            # Calculate position from approximate rover distances
            node.px, node.py = triangulate(tri_data)

        return True

    def compute_dv_distance(self, noise_scale):
        self.clear_computation()

        for rover in self.rover_list:
            rover.dv_table[rover.id] = 0

            for iteration in range(10):
                for node in self.node_list:
                    if rover.id in node.dv_table:
                        for n in node.neighbors:
                            # TODO: Add noise!
                            dist = distance(node, n) + numpy.random.normal(scale=noise_scale)
                            # Send the DV packet
                            if not rover.id in n.dv_table or node.dv_table[rover.id] + dist < n.dv_table[rover.id]:
                                #print(node.id + ' updating neighbor ' + n.id + ' to ' + str(node.dv_table[rover.id] + 1))
                                n.dv_table[rover.id] = node.dv_table[rover.id] + dist

        for node in self.node_list:
            if node in self.rover_list:
                # Rovers need not apply
                continue

            if len(node.dv_table) < 3:
                # This node was not reached by enough rovers, ignore
                continue

            tri_data = []
            for rover_id, dist in node.dv_table.items():
                rover = self.find_node(rover_id)
                tri_data.append((rover.x, rover.y, dist))

            # Calculate position from calculated rover distances
            node.px, node.py = triangulate(tri_data)

    def compute_direct_distance(self, noise_scale):
        self.clear_computation()

        for node in self.node_list:
            if node in self.rover_list:
                # Rovers need not apply
                continue

            if len(self.rover_list) < 3:
                # This node was not reached by enough rovers, ignore
                continue

            tri_data = []
            for rover in self.rover_list:
                # TODO: Add noise!
                dist = distance(node, rover) + numpy.random.normal(scale=noise_scale)
                tri_data.append((rover.x, rover.y, dist))

            # Calculate position from direct rover distances
            node.px, node.py = triangulate(tri_data)

    def rms_error(self):
        sq_error_sum = 0
        sq_error_num = 0
        for node in self.node_list:
            if node.px and node.py:
                sq_error_sum += (node.x - node.px)*(node.x - node.px) + (node.y - node.py)*(node.y - node.py)
                sq_error_num += 1
        if sq_error_num == 0:
            return None
        return math.sqrt(sq_error_sum / sq_error_num)

    def dump(self):
        print('[nodes]')
        for node in self.node_list:
            print(node.id)
            print(node.x, node.y)
            print(len(node.neighbors))
            print('neighbors: ' + ' '.join(b.id for b in node.neighbors))
            print('correction: ' + str(node.cv))
            for rover in rover_list:
                print('hops to ' + rover.id + ': ' + str(node.dv_table[rover.id]))
                print('approximate distance to rover ' + rover.id + ': ' + str(node.cv * node.dv_table[rover.id]))
                print('actual distance to rover ' + rover.id + ': ' + str(distance(node, rover)))

            if node.px != None and node.py != None:
                print('predicted location: (' + str(node.px) + ', ' + str(node.py) + ')')

