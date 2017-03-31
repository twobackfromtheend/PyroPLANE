import pyroplane.misc as misc
from pyroplane.misc import div
# from anal.aposition import APosition
# import database as db


class AHit:
    goal_x = 830
    goal_y = 5100
    goal_z = 650

    shot_off_x = 1100
    shot_off_z = 1000
    magic_vel = 0.0043527

    normal_g = -1.219

    cutoff_time_to_goal = 60

    def __init__(self):
        pass

    def analyse_player_hits(self):
        session = db.Session()

        x = session.query(db.Hit)\
            .filter(db.Hit.player_id.in_(self.playerIDs))\
            .join(db.Replay)\
            .join(db.Player)\
            .filter(db.Player.id.in_(self.playerIDs))\
            .join(db.Team)
        # print(len(x.all()))
        # print(time.time()-_time)
        _time = time.time()
        hits = pd.read_sql_query(
            x.selectable,
            db.engine
        )

        print(hit[:5])
        pass

    @classmethod
    def analyse_game_hits(cls, game):
        # # check if first hit is analysed
        # try:
            # if game.hits[0].isAnalysed: return
        # except: pass

        hits = game.hits
        hits.sort(key=lambda x: x.frameNo)

        hits = cls.find_hit_types(hits, game)

        # get hit positions
        # hitAPositions = cls.get_hit_positions(hits)
        # # get average shot distance
        # this is for per player!
        # averageShotDistance = cls.get_average_shot_distance(hits)

        # for hit in hits:
        # hit.isAnalysed = True

    @classmethod
    def find_hit_types(cls, hits, game):
        for hitNo in range(len(hits)):
            if hitNo > 0:
                previousHit = hits[hitNo - 1]
            else:
                previousHit = None
            hit = hits[hitNo]
            try:
                nextHit = hits[hitNo + 1]
            except IndexError:
                nextHit = None
            lastFramePosition = None
            # prevent hits from passing through goals
            for goal in game.goals:
                if previousHit:
                    if previousHit.frameNo < goal.frameNo <= hit.frameNo:
                        previousHit = None
                if nextHit:
                    if hit.frameNo <= goal.frameNo < nextHit.frameNo:
                        nextHit = None
                        lastFramePosition = game.ball.positions[
                            goal.frameNo - 1]

            # 1st pass
            cls.find_shot(hit)
            cls.find_pass(hit, nextHit)
            cls.find_save(previousHit, hit, game)
            cls.find_dribble(previousHit, hit, nextHit)
            cls.get_hit_distance(hit, nextHit, lastFramePosition)

        cls.find_goal(hits, game)
        # needed shots to have been parsed

        for hitNo in range(len(hits)):
            if hitNo > 0:
                previousHit = hits[hitNo - 1]
            else:
                previousHit = None
            hit = hits[hitNo]
            try:
                nextHit = hits[hitNo + 1]
            except IndexError:
                nextHit = None
            # prevent hits from passing through goals
            for goal in game.goals:
                if previousHit:
                    if previousHit.frameNo < goal.frameNo <= hit.frameNo:
                        previousHit = None
                if nextHit:
                    if hit.frameNo <= goal.frameNo < nextHit.frameNo:
                        nextHit = None

            # find assists and secondary assists. needed goals parsed.
            cls.find_pass(hit, nextHit, previousHit, passNo=2)
            cls.find_assisted_goal(previousHit, hit)

        return hits

    def find_dribble(previousHit, hit, nextHit):
        if previousHit:
            isStart = (previousHit.player != hit.player)
        else:
            isStart = True
        if nextHit:
            if hit.player == nextHit.player:
                if isStart:
                    hit.dribble = 2
                else:
                    hit.dribble = 1
            else:
                hit.dribble = 0
        else:
            hit.dribble = 0
        return hit.dribble

    def find_pass(hit, nextHit=None, previousHit=None, passNo=1):
        # 2 passes
        if passNo == 1:  # 1st pass
            if nextHit:
                if (hit.player.team == nextHit.player.team) and (hit.player is not nextHit.player):
                    hit.pass_ = 1
                    # print('found pass')
                    return hit.pass_
        else:
            # 2nd pass
            if hit.pass_ == 1 and nextHit.goal:
                hit.pass_ = 2  # assist.
                if previousHit:
                    if previousHit.pass_ == 1:
                        previousHit.pass_ = 3  # secondary assist.
                    return hit.pass_
            return

        hit.pass_ = 0
        return hit.pass_

    @classmethod
    def find_shot(cls, hit):
        try:
            if (hit.player.team.colour == 'orange') and (hit.velocity[1] < 0):
                direction = 0
            elif (hit.player.team.colour == 'blue') and (hit.velocity[1] > 0):
                direction = 1
            else:
                hit.shot = 0
                return
        except TypeError:
            print('typeerror, hit has no velocity')
            print(hit.frameNo)
            print(hit.position)
            return

        goal_x = cls.goal_x
        goal_y = cls.goal_y
        goal_z = cls.goal_z

        shot_off_x = cls.shot_off_x
        shot_off_z = cls.shot_off_z

        if hit.velocity[0] == 0:
            x = hit.position[0]
        else:
            # find y=mx+c equation.
            m = hit.velocity[1] / hit.velocity[0]  # gradient
            # c=y-mx, sub in position of hit values.
            c = hit.position[1] - m * hit.position[0]
            # find position at y=+-5100
            # x=(y-c)/m
            if direction:
                x = (goal_y - c) / m
            else:
                x = (-goal_y - c) / m

        # convert velocity to same units as distance.
        magic_vel = cls.magic_vel

        # to add: distance/speed calculation to rule out stupidly slow hits.
        distance_to_goal = (
            (x - hit.position[0])**2 + (goal_y - abs(hit.position[1]))**2)**0.5
        hit.distanceToGoal = distance_to_goal
        time_to_goal = distance_to_goal / \
            ((hit.velocity[0] * magic_vel)**2 +
             (hit.velocity[1] * magic_vel)**2)**0.5

        if (abs(x) > shot_off_x) or (time_to_goal > cls.cutoff_time_to_goal):
            hit.shot = 0
        else:
            z = cls.find_z(hit.position, hit.velocity, time_to_goal, magic_vel)
            if (goal_z > z) and (goal_x > (abs(x))):
                # allowing z to go below 0 as much as it wants. can't calculate
                # bounces yet
                hit.shot = 2
                # print('Found shot')
            elif (shot_off_z > z) and (shot_off_x > abs(x)):
                hit.shot = 1
            else:
                hit.shot = 0
        # if hit.shot:
            # print(time_to_goal)
            # print(distance_to_goal)

        return hit.shot

    @classmethod
    def find_z(cls, position, velocity, time_to_goal, magic_vel):
        normal_g = cls.normal_g

        ini_z_vel = velocity[2] * magic_vel

        d_z = ini_z_vel * time_to_goal + 0.5 * normal_g * (time_to_goal**2)
        z = position[2] + d_z

        return z

    def find_goal(hits, game):
        for hit in hits:
            hit.goal = 0

        # print('\nGoal Frames in Game')
        # for goal in game.goals:
            # print(goal.frameNo)

        for i in range(len(game.goals)):
            goal = game.goals[i]
            try:
                previousGoalFrame = game.goals[i - 1].frameNo
            except KeyError:
                previousGoalFrame = 0

            goalScorer = goal.player
            # find last shot by player
            foundGoal = False
            potentialGoal = None
            for hitNo in range(len(hits) - 1):
                hit = hits[hitNo]
                nextHit = hits[hitNo + 1]
                # prevent hits from passing through goals
                if nextHit:
                    for _goal in game.goals:
                        if hit.frameNo <= _goal.frameNo < nextHit.frameNo:
                            nextHit = None
                            break

                if hit.shot and hit.player == goalScorer and (goal.frameNo - 100) < hit.frameNo <= goal.frameNo:
                    if potentialGoal:
                        if hit.frameNo > potentialGoal.frameNo:
                            potentialGoal = hit
                    else:
                        potentialGoal = hit
            if potentialGoal:
                potentialGoal.goal = 1
            else:
                print('Cannot find shot that results in goal by ' + goalScorer.name)

                print('Using his last touch.')
                lastHitFrameNo = previousGoalFrame
                for hit in hits:
                    if hit.player == goalScorer and lastHitFrameNo < hit.frameNo <= goal.frameNo:
                        lastHit = hit
                        lastHitFrameNo = hit.frameNo
                try:
                    potentialGoal = lastHit
                    lastHit.goal = 1
                except UnboundLocalError:
                    print('Cannot find touch that results in goal by ' +
                          goalScorer.name)
                    return
            # print('Found goal for '+goal.player._name+'.')
            # print('Goal Frame: '+str(goal.frameNo)+'   Shot Frame: '+str(potentialGoal.frameNo))

    def find_assisted_goal(previousHit, hit):
        if previousHit:
            if previousHit.pass_ and hit.goal == 1:
                hit.goal = 2  # find assisted goal
                return hit.goal

    def find_save(previousHit, hit, game):
        if previousHit:
            if previousHit.shot:
                saveBuffer = 40
                if (previousHit.player.team != hit.player.team) and ((hit.frameNo - previousHit.frameNo) < saveBuffer):
                    for goal in game.goals:
                        if hit.frameNo < goal.frameNo < (hit.frameNo + saveBuffer):
                            hit.save = -1
                            return hit.save
                        else:
                            hit.save = 1
                            return hit.save

        hit.save = 0
        return hit.save

    @staticmethod
    def get_average_shot_distance(hits):
        shotDistances = []
        for hit in hits:
            if hit.shot:
                shotDistances.append(hit.distanceToGoal)
        averageShotDistance = div(sum(shotDistances), len(shotDistances))

        return averageShotDistance

    # def get_hit_positions(hits):
        # positions = []
        # for hit in hits:
        # position = hit.position
        # player = hit.player
        # # _half,_third,_height = APosition.get_positions_analysis([position],player)
        # _half,_third,_height = APosition.get_half_third_height_ball(position,colour = player.team.colour)
        # hit.half = _half
        # hit.third = _third
        # hit.height = _height

    def get_hit_distance(hit, nextHit, lastFramePosition):
        if nextHit:
            hit.distance = misc.find_distance(hit.position, nextHit.position)
        else:
            hit.distance = misc.find_distance(hit.position, lastFramePosition)
        return hit.distance

    def get_average_hit_distance(hits):
        distances = []
        for hit in hits:
            if hit.distance:
                distances.append(hit.distance)
        averageDistance = div(sum(distances), len(distances))

        return averageDistance

    def get_average_dribble_distance(hits):
        i = 0
        dribbleDistances = []
        dribbleHitNo = []
        while i < len(hits):
            # find full dribble
            hit = hits.iloc[i, :]
            dribbleHits = []
            if hit.hits_dribble == 2:
                dribbleHits.append(hit)
                i += 1
                # print(hits)
                while hits.ix[i, 'hits_dribble']:
                    hit = hits.iloc[i, :]
                    dribbleHits.append(hit)
                    i += 1
                # add last dribble hit - it has .dribble=0
                dribbleHits.append(hits.iloc[i, :])
                dribbleDistance = misc.find_distance(dribbleHits[0].loc[
                                                     ['hits_x', 'hits_y', 'hits_z']].values, dribbleHits[-1].loc[['hits_x', 'hits_y', 'hits_z']].values)
                dribbleDistances.append(dribbleDistance)
                dribbleHitNo.append(len(dribbleHits))

            i += 1
        aveDribbleDistance = div(sum(dribbleDistances), len(dribbleDistances))
        aveDribbleHits = div(sum(dribbleHitNo), len(dribbleHitNo))

        return aveDribbleDistance, aveDribbleHits
        # i = 0
        # dribbleDistances = []
        # dribbleHitNo = []
        # while i < len(hits):
        # # find full dribble
        # hit = hits[i]
        # dribbleHits = []
        # if hit.dribble == 2:
        # dribbleHits.append(hit)
        # i += 1
        # while hits[i].dribble:
        # dribbleHits.append(hit)
        # i += 1
        # # add last dribble hit - it has .dribble=0
        # dribbleHits.append(hits[i])

        # dribbleDistance = misc.find_distance(dribbleHits[0].position,dribbleHits[-1].position)
        # dribbleDistances.append(dribbleDistance)
        # dribbleHitNo.append(len(dribbleHits))

        # i += 1
        # aveDribbleDistance = div(sum(dribbleDistances),len(dribbleDistances))
        # aveDribbleHits = div(sum(dribbleHitNo),len(dribbleHitNo))

        # return aveDribbleDistance,aveDribbleHits
