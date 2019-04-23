
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
            guess2 = (AC2[0] + t1[0], AC2[1] + t1[1])
            #print("AB: " + str(AB))
            #print("AC1: " + str(AC1))
            #print("AC2: " + str(AC2))
            #print("theta: " + str(theta))
            print("guess1: " + str(guess1))
            print("guess2: " + str(guess2))
            prediction_list.append(guess1)
            prediction_list.append(guess2)

    if len(prediction_list) > 0:
        gx = 0
        gy = 0
        for p in prediction_list:
            gx += p[0]
            gy += p[1]
        return gx / len(prediction_list), gy / len(prediction_list)
    else:
        return None
