import pyroplane.anal.item as Item
from pyroplane.anal.collision import Collision
import pandas as pd

class Hit:

    def __init__(self,frameNo,hitter,velocity,ballPosition,distance):
        self.frameNo = frameNo
        self.player = hitter
        self.velocity = velocity
        self.position = ballPosition
        self.distance = distance

        try:
            hitter.hits.append(self)
        except AttributeError:
            hitter.hits = [self]
        return

    @classmethod
    def add_all_hits(cls, game):
        hits = []
        frameNo = 10
        buffer = False  # if true, allow ball to go beyond mindistance before catching
        lastHitter = None
        hitter = None

        # game.ball.distances = []

        while frameNo < len(game.ball.positions):
            # get closest distance between ball and player
            # print(list(game.ball.positions.keys()))
            ballPosition = game.ball.positions[frameNo]
            minDistance = 2000
            for player in game.players:
                playerPosition = player.positions[frameNo]
                distance = Item.find_distance(playerPosition, ballPosition)
                try:
                    if distance and (distance < minDistance):
                        minDistance = distance
                        hitter = player
                except:  # TypeError:
                    pass  # distance probably not found, no car

            # check if hitter has left buffer distance or someone else has come close to the ball.
            if minDistance < 500:
                # print(minDistance, hitter, frameNo)
                collideDist = Collision.check_collision(hitter, game.ball, frameNo)
                if collideDist:
                    # print('frame')
                    # print(frameNo)
                    # print(minDistance)
                    # print(collideDist)
                    # print('\n')
                    # find closest approach (look for frame where hit occurs)
                    nextFrameNo = frameNo + 1
                    nextDistance = Collision.check_collision(hitter, game.ball, nextFrameNo)
                    # if distance between ball and car is greater the next frame, hit occurs on this frame.
                    if not nextDistance:
                        nextDistance = 1000

                    # print(nextDistance)
                    # print('\n')
                    if nextDistance >= collideDist:
                        if (hitter==lastHitter) and buffer: pass
                        else:
                            # print('checked distance')
                            try:
                                velocity = game.ball.velocities[frameNo+1]
                            except KeyError:
                                for x in range(1,-2,-1): #check next frame then previous
                                    try:
                                        velocity = game.ball.velocities[frameNo+x]
                                        break
                                    except KeyError: pass
                                    # print(minDistance)
                                    # print('cannot find vel for frame ' + str(frameNo+x))
                                velocity = False
                            if velocity:
                                hit = cls(frameNo,hitter,velocity,game.ball.positions[frameNo],minDistance)
                                # print('found hit,printing frame no and distance')
                                # print(frameNo)
                                # print(minDistance)

                                hits.append(hit)
                                buffer = True
                                lastHitter = hitter
                    else:
                        # set buffer to false when no collision detected.
                        buffer = False

            else: buffer = False

            # if minDistance < 300:
                # try:
                    # if collideDist:
                        # game.ball.distances.append(str(collideDist))
                    # else:
                        # game.ball.distances.append('playerdist: ' + str(minDistance))
                # except UnboundLocalError:
                    # game.ball.distances.append('playerdist: ' + str(minDistance))
            # else:
                # game.ball.distances.append('playerdist: ' + str(minDistance))
            frameNo += 1
        return hits

    @classmethod
    def _add_all_hits(cls,game):
        hits = []
        frameNo = 5
        buffer = False  # if true, allow ball to go beyond mindistance before catching
        lastHitter = None
        hitter = None
        while frameNo < game.maxFrameNo:
            #get closest distance between ball and player
            ballPosition = game.ball.positions[frameNo]
            minDistance = 500
            for player in game.players:
                playerPosition = player.positions[frameNo]
                distance = Item.find_distance(playerPosition,ballPosition)
                try:
                    if distance < minDistance:
                        minDistance = distance
                        hitter = player
                except TypeError:
                    pass  # distance probably not found, no car

            # check if hitter has left buffer distance or someone else has come close to the ball.
            bufferDistance = 300
            if (hitter == lastHitter) and buffer:
                if minDistance < bufferDistance:
                    frameNo += 1
                    continue
                elif minDistance > bufferDistance:
                    buffer = False

            if minDistance < 250:  # will add a hit once past this point
                # find closest approach (look for frame where hit occurs)
                nextDistance = 0
                nextFrameNo = frameNo + 1

                try:
                    playerNextPosition = hitter.positions[nextFrameNo]
                except IndexError:
                    if nextFrameNo >= game.maxFrameNo:
                        break
                ballNextPosition = game.ball.positions[nextFrameNo]
                nextDistance = Item.find_distance(playerNextPosition, ballNextPosition)
                # if distance between ball and car is greater the next frame, hit occurs on this frame.
                # print(nextDistance, minDistance)
                if nextDistance > minDistance:
                    try:
                        velocity = game.ball.velocities[frameNo+1]
                    except KeyError:
                        for x in range(1, -2, -1):  # check next frame then previous
                            try:
                                velocity = game.ball.velocities[frameNo + x]
                                break
                            except KeyError:
                                pass
                            # print(minDistance)
                            # print('cannot find vel for frame ' + str(frameNo+x))
                        velocity = False
                    if velocity:
                        hit = cls(frameNo,hitter,velocity,ballPosition,playerPosition,minDistance)
                    print('found hit, f:%s, dist:%s' % (frameNo, minDistance))


                    hits.append(hit)
                    buffer = True
                    lastHitter = hitter
            frameNo += 1
        return hits

    def get_firstHit(game):
        for goalNo in range(len(game.goals)):
            if goalNo == 0: #get first kickoff
                startFrameNo = 0
            else:
                startFrameNo = (game.goals[goalNo-1].frameNo)

            hitFrameNo = game.maxFrameNo
            for hit in game.hits:
                if startFrameNo < hit.frameNo < hitFrameNo:
                    hitFrameNo = hit.frameNo
            # print(game.goals)
            game.goals[goalNo].firstHit = hitFrameNo


    @classmethod
    def _add_all_hits2(cls, game):
        hits = []

        # import all positions (players + ball)
        pos_dict = {}
        i = 0

        non_spectators = []
        for player in game.players:
            # check if player is just spectator.
            if all(v[0] is None for v in player.positions):
                # all positions are None (at least for x)
                continue
            non_spectators.append(player)
            x, y, z = zip(*player.positions)
            pos_dict[str(i) + player.name + 'x'] = x
            pos_dict[str(i) + player.name + 'y'] = y
            pos_dict[str(i) + player.name + 'z'] = z
            i += 1
        ballx, bally, ballz = zip(*game.ball.positions)
        pos_dict['ballx'] = ballx
        pos_dict['bally'] = bally
        pos_dict['ballz'] = ballz

        pos_table = pd.DataFrame(pos_dict)
        # print(pos_table)

        # find all distances
        i = 0
        for player in non_spectators:
            pos_table[player.name + 'd'] = ((pos_table[str(i) + player.name + 'x'] - pos_table['ballx'])**2 + (pos_table[str(i) + player.name + 'y'] - pos_table['bally'])**2 + (pos_table[str(i) + player.name + 'z'] - pos_table['ballz'])**2)**0.5
            i += 1
        # print(pos_table)
        ### PREP DONE. DISTANCES FOUND.

        # ACTUAL CHECKING
        frameNo = 5
        buffer = False  # if true, allow ball to go beyond mindistance before looking for next hit
        lastHitter = None
        hitter = None
        while frameNo < game.maxFrameNo:
            # get closest distance between ball and player
            ballPosition = game.ball.positions[frameNo]
            minDistance = 500
            for player in non_spectators:
                distance = pos_table[player.name + 'd'][frameNo]
                try:
                    if distance < minDistance:
                        minDistance = distance
                        hitter = player
                except TypeError:
                    pass  # distance probably not found, no car

            # check if hitter has left buffer distance or someone else has come close to the ball.
            bufferDistance = 300
            if (hitter == lastHitter) and buffer:
                if minDistance < bufferDistance:
                    frameNo += 1
                    continue
                elif minDistance > bufferDistance:
                    buffer = False

            if minDistance < 250:  # will add a hit once past this point
                # find closest approach (look for frame where hit occurs)
                nextDistance = 0
                nextFrameNo = frameNo + 1

                try:
                    nextDistance = pos_table[player.name + 'd'][nextFrameNo]
                except IndexError:
                    if nextFrameNo >= game.maxFrameNo:
                        break
                    print("ERROR IN HIT.PY LINE 262")

                # if distance between ball and car is greater the next frame, hit occurs on this frame.
                # print(nextDistance, minDistance)
                if nextDistance > minDistance:
                    try:
                        velocity = game.ball.velocities[frameNo+1]
                    except KeyError:
                        for x in [1, -1, 2, -2, 3, 4, 5]:  # check next frame then previous
                            try:
                                velocity = game.ball.velocities[frameNo + x]
                                break
                            except KeyError:
                                pass
                            # print(minDistance)
                            # print('cannot find vel for frame ' + str(frameNo+x))
                        velocity = None
                    if velocity:
                        # playerPosition = hitter.positions[frameNo]
                        hit = cls(frameNo,hitter,velocity,ballPosition,minDistance)
                        # print('found hit, f:%s, p:%s, dist:%s' % (frameNo, hitter.name, minDistance))
                        hits.append(hit)
                    else:
                        print('WARNING: Found hit without ball velocity. F: %s, P: %s' % (frameNo, hitter.name))
                        print('Ignoring hit.')

                    buffer = True
                    lastHitter = hitter
            frameNo += 1
        return hits

    def sort_hits(game):
        pass
