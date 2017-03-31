from pyroplane.anal.car import Car
import pyroplane.anal.item as Item
import math as m


class Collision:
    allCollisions = []

    def __init__(self, player, frameNo):
        self.player = player
        self.frameNo = frameNo

    def check_collision(player, ball, frameNo):
        try:
            playerPosition = player.positions[frameNo]
            playerRotation = player.rotations[frameNo]
            ballPosition = ball.positions[frameNo]
        except IndexError:
            return False
        except KeyError:
            return False

        playerHitbox = Car.get_hitbox(player)

        # move ball position
        ballPositionNew = list(ballPos - playerPos for ballPos, playerPos in zip(ballPosition, playerPosition))

        ballPosition = Collision.unrotate_ball(playerRotation, ballPositionNew)
        # with open('ballpositions.txt','a') as o:
            # try:
                # for x in ballPosition:
                    # o.write(str(x)+',')
                # o.write('\n')
            # except TypeError:
                # print(ballPositionNew)
                # print(ballPosition)

        distance = Collision.get_plane_ball_distances(playerHitbox, ballPosition)
        # print(isCollide)
        if distance < 200:
            return distance
        else:
            return False

    def unrotate_ball(playerRotation, ballPositionNew):
        pitch_, yaw_, roll_ = playerRotation

        ballPosition = Collision.yaw(playerRotation, ballPositionNew, yaw_)
        ballPosition = Collision.pitch(playerRotation, ballPosition, pitch_)
        ballPosition = Collision.roll(playerRotation, ballPosition, roll_)

        return ballPosition

    def get_vector2D(x, y):
        angle = m.atan2(y, x) / m.pi
        # returns 1 for back, 0.5 for up, 0 for forward, -0.5 for down, -1 for back.
        magnitude = (x**2 + y**2)**0.5
        return(angle, magnitude)

    def pitch(playerRotation, ballPositionNew, pitch):
        # do pitch: (rotation around y) z is vertical axis, x is horizontal axis.
        # pitch is -0.5(up) to -1(forward) to 1(forward) to 0.5(down)
        # get angle

        (ballAngle, magnitude) = Collision.get_vector2D(ballPositionNew[0], ballPositionNew[2])
        #convert to -0.5(down) to 0.5(up)
        # if pitch < 0:
            # playerAngle = 1+pitch
        # elif pitch > 0:
            # playerAngle = 1-pitch
        # else: pass
        playerAngle = pitch

        ballAngleNew = ballAngle - playerAngle
        # if ballAngleNew > 1: ballAngleNew -= 2
        # elif ballAngleNew <= -1: ballAngleNew += 2
        # return the range to 1to-1.

        ballPosition = []
        ballPosition.append(magnitude * m.cos(m.pi * ballAngleNew))
        ballPosition.append(ballPositionNew[1])
        ballPosition.append(magnitude * m.sin(m.pi * ballAngleNew))

        return ballPosition

    def yaw(playerRotation, ballPositionNew, yaw):
        # do yaw: (rotation around z)
        # -0.5(orange goal) to -1(left) to 1(left) to 0.5(blue goal) to 0(right)

        (ballAngle, magnitude) = Collision.get_vector2D(ballPositionNew[0], ballPositionNew[1])

        # playerAngle = -yaw
        playerAngle = -yaw
        # orange goal is positive Y, but negative yaw value initially.

        ballAngleNew = ballAngle - playerAngle

        ballPosition = []
        ballPosition.append(magnitude * m.cos(m.pi * ballAngleNew))
        ballPosition.append(magnitude * m.sin(m.pi * ballAngleNew))
        ballPosition.append(ballPositionNew[2])

        return ballPosition

    def roll(playerRotation, ballPositionNew, roll):
        # do roll (rotation around x)
        # -0.5(rolled right) to -1(flat) to 1(flat) to  0.5 (left)
        # -0.5 (rolled right) to 0 (upsidedown) to 0.5 (left)
        (ballAngle, magnitude) = Collision.get_vector2D(ballPositionNew[1], ballPositionNew[2])

        # if roll <= 0:
            # playerAngle = -(roll + 1)
        # elif roll > 0:
            # playerAngle = -(roll - 1)
        # playerAngle = -roll + 1
        playerAngle = -roll
        ballAngleNew = ballAngle - playerAngle

        ballPosition = []
        ballPosition.append(ballPositionNew[0])
        ballPosition.append(magnitude * m.cos(m.pi * ballAngleNew))
        ballPosition.append(magnitude * m.sin(m.pi * ballAngleNew))

        return ballPosition


    def check_hitbox(playerHitbox,ballPosition):
        x,y,z = ballPosition

        # get max car value in the ball quadrant.
        # if x >= 0:
            # car_x = playerHitbox[0]/2
        # else: car_x = -playerHitbox[0]/2

        # if y >= 0:
            # car_y = playerHitbox[1]/2
        # else: car_y = -playerHitbox[1]/2

        # if z >= 0:
            # car_z = playerHitbox[2]/2
        # else: car_z = -playerHitbox[2]/2


        # absolute value everything so that i only need to care about the positive quadrant
        ballPosition = (abs(x), abs(y), abs(z))
        car_eighth = (playerHitbox[0] / 2, playerHitbox[1] / 2, playerHitbox[2] / 2)

        distance = Collision.get_plane_ball_distances(car_eighth, ballPosition)

        # with open('balldistance.txt','a') as o:
            # o.write(str(int(distance))+'\n')
        if distance < 120:
            return distance


    def get_plane_ball_distances(playerHitbox, ballPosition):
        x, y, z = ballPosition

        # absolute value everything so that i only need to care about the positive quadrant
        ballPosition = (abs(x), abs(y), abs(z))
        car_eighth = (playerHitbox[0] / 2, playerHitbox[1] / 2, playerHitbox[2] / 2)

        # do x
        # front of car. find if ball is within the front area. use the ball value if it is.
        # if ball is not, use the max car value.
        x_to_check = car_eighth[0]
        y_to_check = min(ballPosition[1], car_eighth[1])
        z_to_check = min(ballPosition[2], car_eighth[2])

        point = (x_to_check, y_to_check, z_to_check)

        # find distance for plane with x-axis normal
        x_dist = Item.find_distance(point, ballPosition)

        # do y
        x_to_check = min(ballPosition[0], car_eighth[0])
        y_to_check = car_eighth[1]
        z_to_check = min(ballPosition[2], car_eighth[2])

        point = (x_to_check, y_to_check, z_to_check)

        # find distance for plane with x-axis normal
        y_dist = Item.find_distance(point, ballPosition)

        # do z
        x_to_check = min(ballPosition[0], car_eighth[0])
        y_to_check = min(ballPosition[1], car_eighth[1])
        z_to_check = car_eighth[2]

        point = (x_to_check, y_to_check, z_to_check)

        #find distance for plane with x-axis normal
        z_dist = Item.find_distance(point, ballPosition)

        return min(x_dist, y_dist, z_dist)


