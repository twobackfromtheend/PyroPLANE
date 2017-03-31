def get_position(actorData):
    try:
        position = list(actorData[1]['data']['TAGame.RBActor_TA:ReplicatedRBState']['pos'])
        position[0] = -position[0]

        return position
    except KeyError:
        print('Cannot find position for ' + actorData[0])
        pass
    return False

def get_velocity(actorData):
    try:
        velocity = list(actorData[1]['data']['TAGame.RBActor_TA:ReplicatedRBState']['vec1'])
        velocity[0] = -velocity[0]
        return velocity
    except KeyError:
        # print('Cannot find velocity for ' + actorData[0])
        pass
    return False

def get_rotation(actorData):
    try:
        rotation = list(actorData[1]['data']['TAGame.RBActor_TA:ReplicatedRBState']['rot'])
        # rotation[0] = -rotation[0]
        return rotation
    except KeyError:
        # print('Cannot find rotation for ' + actorData[0])
        pass
    return False

def find_distance(a, b):
    try:
        if len(a) == len(b):
            i = 0
            distance = 0
            while i < len(a):
                # print(a)
                # print(b)
                distance += ((abs(a[i]-b[i]))**2)
                # print(distance)
                i += 1
            distance = distance**(0.5)
            return distance
        else:
            print(a)
            print(b)
            print('They do not have the same number of coordinates')
    except TypeError:
        return False
