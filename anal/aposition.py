import numpy as np
import statistics as s
import pyroplane.misc
import pyroplane.database.database as db, sqlalchemy as sq, time, pandas as pd


class APosition:
    magic_vel = 0.0043527

    def __init__(self):
        pass


    # def analyse_player_position(self):
        # session = db.Session()
        # gameFrames = {} # replayid:[(start,end),..]
        # for playerID in self.playerIDs:
            # player = session.query(db.Player).filter(db.Player.id==playerID).one()
            # frames = misc.get_game_frames(self,player.replay)
            # gameFrames[player.replay.id] = frames
            # # print(self.playerIDs,playerID)
            # # stadium
            # # map = player.replay.map
            # # half
            # # a = time.time()
            # # x = session.query(db.Position).join(db.BallFrame,sq.and_(db.Position.frameNo==db.BallFrame.frameNo,db.Position.replay_id==db.BallFrame.replay_id)).filter(db.Position.player_id==playerID).all()
            # # print(x)
        # print(gameFrames)
        # for replayid in gameFrames:
            # totalFrames = sum((frame[1]-frame[0]) for frame in gameFrames[replayid])
            # print(replayid,totalFrames)

        # a = time.time()

        # # x = session.query(db.Position, db.BallFrame, db.Replay.map, db.Team.colour)\
        # x = session.query(db.Position.x,db.Position.y,db.Position.z, db.BallFrame.x,db.BallFrame.y,db.BallFrame.z, db.Replay.map, db.Team.colour)\
            # .filter(db.Position.player_id.in_(self.playerIDs))\
            # .filter(sq.or_(sq.and_(sq.or_(db.Position.frameNo.between(frames[0],frames[1]) for frames in gameFrames[replayid]),db.Position.replay_id==replayid) for replayid in gameFrames))\
            # .join(db.BallFrame,db.BallFrame.frame_id==db.Position.frame_id)\
            # .join(db.Replay)\
            # .join(db.Player)\
            # .filter(db.Player.id.in_(self.playerIDs))\
            # .join(db.Team)
        # # print(len(x.all()))
        # # print(time.time()-_time)
        # _time = time.time()
        # positions = pd.read_sql_query(
                # x.selectable,
                # db.engine
            # )

        # print('Total Frames: ',len(positions))
        # # print(positions[['positions_id','players_id']][:5])
            # # try:
                # # positions = pd.concat([positions,_positions])
                # # print(2,len(positions),len(positions.columns.values))
            # # except UnboundLocalError:
                # # positions = _positions
                # # print(1,len(positions),len(positions.columns.values))
        # # print(positions)
        # print('Total Duration:','{:.3}'.format(time.time()-a))
        # position = APosition.analyse_position(positions)

            # if not positions.empty:
                # if player.team.colour == 'orange':
                    # position['half'][0] += hn
                    # position['half'][1] += hp

                    # position['third'][-1] += tn
                    # position['third'][0] += tm
                    # position['third'][1] += tp

                    # position['height'][0] += ht0
                    # position['height'][1] += ht1
                    # position['height'][2] += ht2

                    # position['ball'][0] += bn
                    # position['ball'][1] += bp


                    # positions['positions_y'] = positions['positions_y']*-1

                # elif player.team.colour == 'blue':
                    # position['half'][0] += hp
                    # position['half'][1] += hn

                    # position['third'][-1] += tp
                    # position['third'][0] += tm
                    # position['third'][1] += tn

                    # position['height'][0] += ht0
                    # position['height'][1] += ht1
                    # position['height'][2] += ht2

                    # position['ball'][0] += bp
                    # position['ball'][1] += bn

                # try:
                    # allPositions += positions
                # except UnboundLocalError:
                    # allPositions = positions

        # print(position)






    def analyse_position(positions):

        position = {
            'half': {0:0,1:0},
            'third': {-1:0,0:0,1:0},
            'height':  {0:0,1:0,2:0},
            'ball': {0:0,1:0},
            'total': 0,
            }
        # for normal maps:
        maps = ['stadium_p','park_p','park_night_p','park_rainy_p','utopiastadium_dusk_p','trainstation_p','trainstation_night_p','eurostadium_p','eurostadium_rainy_p','wasteland_p']
        positions.replays_map = positions.replays_map.str.lower()


        _positions = positions.ix[positions.replays_map.isin(maps),:]

        print(_positions[:5])
        # todo: check for special maps
        print(_positions.columns.values)
        # print(pd.unique(positions.replays_map.ravel()))


        _positions.ix[_positions.teams_colour=='orange', 'positions_y'] = _positions.ix[_positions.teams_colour=='orange', 'positions_y']*-1
        # print(_positions[['_positions_y','teams_colour']][:5])

        # _positions = pd.concat([orange_positions,blue_positions])

        # orange_positions = _positions[_positions['teams_colour']=='orange']
        # print(orange_positions[['_positions_y','teams_colour']][:5])
        # print('concat',time.time()-a)


        # half
        # a = time.time()
        hp = _positions['positions_y'][_positions['positions_y'] > 0].count()
        hn = _positions['positions_y'][_positions['positions_y'] <= 0].count()
        # print('half:',hp,hn)
        position['half'][1] += hp
        position['half'][0] += hn

        # third
        tp = _positions['positions_y'][_positions['positions_y'] >= 3400].count()
        tm = _positions['positions_y'][(_positions['positions_y'] > -3400) & (_positions['positions_y'] < 3400)].count()
        tn = _positions['positions_y'][_positions['positions_y'] <= -3400].count()
        # print('third:',tp,tm,tn)
        position['third'][1] += tp
        position['third'][0] += tm
        position['third'][-1] += tn

        # height
        ht0 = _positions['positions_z'][_positions['positions_z'] < 25].count()
        ht1 = _positions['positions_z'][(_positions['positions_z'] >= 25) & (_positions['positions_z'] <= 840) ].count()
        ht2 = _positions['positions_z'][_positions['positions_z'] > 840].count()
        # print('height:',ht0,ht1,ht2)
        position['height'][0] += ht0
        position['height'][1] += ht1
        position['height'][2] += ht2

        if 'ballframes_y' in _positions.columns.values:
            # ball
            # print(_positions.head())
            bp = _positions['positions_y'][_positions['positions_y'] >= _positions['ballframes_y']].count()
            bn = _positions['positions_y'][_positions['positions_y'] < _positions['ballframes_y']].count()
            # print('ball:',bp,bn)
            position['ball'][1] += bp
            position['ball'][0] += bn


        position['total'] += _positions['replays_map'].count()

        average = _positions[['positions_x','positions_y','positions_z']].mean(numeric_only=True)
        std = _positions[['positions_x','positions_y','positions_z']].std()
        position['average'] = average.values.tolist()
        position['averageV'] = std.values.tolist()

        # print(_positions[['positions_x','positions_y','positions_z']].skew())
        # print(_positions[['positions_x','positions_y','positions_z']].kurt())

        print('Average:\n',average)

        print(position)
        return position


    @classmethod
    def get_positions_speed_analysis(cls,positions,speeds,player,ballPositions):
        speed = {
        'half':{
            0:[], 1:[]},
        'third':{
            -1:[], 0:[], 1:[]},
        'height':{
            0:[], 1:[], 2:[]},
        'ball':{
            0:[],1:[]}
        }
        position = {
        'half':{
            0:0, 1:0},
        'third':{
            -1:0, 0:0, 1:0},
        'height':{
            0:0, 1:0, 2:0},
        'ball':{
            0:0, 1:0}
        }

        for frameNo in positions:
            pos_a = cls.get_half_third_height_ball(positions[frameNo],ballPositions[frameNo],player.team.colour)
            try:
                _speed = speeds[frameNo]
            except KeyError:
                _speed = None
            if pos_a:
                half_,third_,height_,ballHalf_ = pos_a
                position['half'][half_] += 1
                position['third'][third_] += 1
                position['height'][height_] += 1
                position['ball'][ballHalf_] += 1

                if _speed:
                    speed['half'][half_].append(_speed)
                    speed['third'][third_].append(_speed)
                    speed['height'][height_].append(_speed)
                    speed['ball'][ballHalf_].append(_speed)

        return position, speed

    @classmethod
    def get_positions_analysis(cls,positions,player,ballPositions=None):
        half = {0:0,1:0}
        third = {-1:0,0:0,1:0}
        height = {0:0,1:0,2:0}
        if ballPositions: # to compare to
            ballHalf = {0:0,1:0}
            for i in range(len(positions)):
                pos_a = cls.get_half_third_height_ball(positions[i],ballPositions[i],player.team.colour)
                if pos_a:
                    half_,third_,height_,ballHalf_ = pos_a
                    half[half_] += 1
                    third[third_] += 1
                    height[height_] += 1
                    ballHalf[ballHalf_] += 1
            return half,third,height,ballHalf

        else:
            for i in range(len(positions)):
                pos_a = cls.get_half_third_height_ball(positions[i],colour=player.team.colour)
                if pos_a:
                    half_,third_,height_ = pos_a
                    half[half_] += 1
                    third[third_] += 1
                    height[height_] += 1
            return half,third,height

    @classmethod
    def get_speed(cls,velocity):
        magic_vel = cls.magic_vel #convert velocity to same units as distance.

        x,y,z = velocity
        speed = ((x*magic_vel)**2+(y*magic_vel)**2+(z*magic_vel)**2)**0.5
        return speed


    def get_half_third_height_ball(position,ballPosition=None,colour=None):
        x = position[0]
        y = position[1]
        z = position[2]

        try:
            if colour == 'orange':
                #horizontal
                if y> 0 :
                    half = 1 #orange
                else: half = 0 #blue

                if y > 3400:
                    third = 1 #orange
                elif y < -3400:
                    third = -1 #blue
                else: third = 0
            elif colour == 'blue':
                #horizontal
                if y> 0 :
                    half = 0 #orange
                else: half = 1 #blue

                if y > 3400:
                    third = -1 #orange
                elif y < -3400:
                    third = 1 #blue
                else: third = 0
            elif colour == 'ball':
                if y> 0 :
                    half = 1 #orange
                else: half = 0 #blue

                if y > 3400:
                    third = 1 #orange
                elif y < -3400:
                    third = -1 #blue
                else: third = 0

            #vertical
            if ballPosition: #is car
                if z < 25:
                    height = 0 #on ground
                elif z < 450:
                    height = 1 #between goal and ground
                else: height = 2
            else: # is ball
                if z < 100:
                    height = 0 #on ground
                elif z < 450:
                    height = 1 #between goal and ground
                else: height = 2

            if ballPosition:
                ball_y = ballPosition[1]

                #check if behind ball
                if colour == 'orange':
                    if y > ball_y: ball = 0 #behind ball if y > ball y
                    else: ball = 1
                elif colour == 'blue':
                    if y < ball_y: ball = 0
                    else: ball = 1
                else:
                    print('what is this team colour: ' + str(colour))
                return (half,third,height,ball)

            return (half,third,height)

        except TypeError: return False


    def get_average_position(dict):
        allPlayerPositions = []
        for player in dict:
            if player.team.colour == 'blue':
                for position in dict[player]:
                    position = misc.make_orange_side(position,player)
                    allPlayerPositions.append(position)
            else:
                allPlayerPositions += dict[player]

        values = allPlayerPositions
        try:
            (x,y,z) = zip(*values)
            x = list(x)
            y = list(y)
            z = list(z)
        except TypeError:
            print(values[:10])
            print('Cannot unzip values')
            return None
        except ValueError:
            print(values[:10])
            print('Cannot unzip values')
            return None
        i=0
        while i <(len(x)):
            if (x[i] is None) or (y[i] is None) and (z[i] is None):
                # print(x)
                # print(x[i],y[i],z[i])
                x.pop(i)
                y.pop(i)
                z.pop(i)
            else: i+=1

        try:
            a = (s.mean(x), s.mean(y), s.mean(z))
        except TypeError:
            for no in range(len(x)):
                if not isinstance(x[no],int):
                    print(no)
                    print(x[no])
                    # print(x[:10])

        # a = (s.median(x),s.median(y),np.percentile(z,70))
        # v = ((s.pstdev(x,a[0])-1800)*5,(s.pstdev(y,a[1])-2400)*5,(s.pstdev(z,a[2])-50)*5)
        #variance is too much with this data.

        #return separate 25,75% ranges.
        v = []
        for axis in (x,y):
            v.append([np.percentile(axis,25),np.percentile(axis,75)])
        v.append([np.percentile(z,25),np.percentile(z,90)])


        return(a,v)


    def analyse_game_possession(game):
        try:
            if game.isPossessionAnalysed: return
        except: pass

        for player in game.players:
            player.possessionH = []
            player.possessionP = []

        for frameNo in game._framesToParse:

            ballPosition = game.ball.positions[frameNo]
            minDistance = 50000
            closestPlayer = None
            for player in game.players:
                playerPosition = player.positions[frameNo]
                distance = misc.find_distance(playerPosition,ballPosition)
                #check if closest
                if distance < minDistance:
                    minDistance = distance
                    # print(str(frameNo)+', '+str(distance)+', '+player.name)
                    closestPlayer = player

            closestPlayer.possessionP.append(frameNo)
            # print(player.name)

            hitter = None
            _HitFrameNo = 0
            for hit in game.hits:
                if _HitFrameNo < hit.frameNo <= frameNo:
                    hitter = hit.player

            hitter.possessionH.append(frameNo)

        # for player in game.players:
            # print(player.name)
            # print(len(player.possessionP))
        game.isPossessionAnalysed = True
