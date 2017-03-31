import pyroplane.misc
from pyroplane.misc import div
import pyroplane.database.database as db
import sqlalchemy as sq, pandas as pd, time
from pyroplane.anal.aposition import APosition
from pyroplane.anal.ahit import AHit




class APlayer:
    def __init__(self,rPlayerID,replays,plotBy,plotByData,plotOvertime):
        self.rPlayerID = rPlayerID
        self.playerIDs = []
        self.ballObjects = []
        self.hits = []

        self.plotBy = plotBy
        self.plotByData = plotByData
        self.plotOvertime = plotOvertime
        # self.positions = []
        # self.ballPositions = []
        # self.velocities = []


        self.parse_player(replays)

        pass

    def parse_player(self,replays):
        session = db.Session()
        # get RPlayer
        rPlayer = session.query(db.RPlayer).filter(db.RPlayer.id==self.rPlayerID).one()
        print('\nAnalysing '+rPlayer.name)

        # get players:
        playerIDs = session.query(db.Player.id).join(db.RPlayer).join(db.Replay).filter(db.Replay.id.in_(replays.keys())).filter(db.RPlayer.id==self.rPlayerID).all()
        for (playerID,) in playerIDs:
            self.playerIDs.append(playerID)
        # position
        # self.position = self.analyse_player_position()
        # hits
        self.hits = self.analyse_player_hits()
















        # # add player and ball objects from games

        # for game in games:
            # # game._framesToParse = misc.get_game_frames(self,game)

            # for player in game.players:
                # try:
                    # if player._name == self._name:
                        # # get position stuff
                        # player._framesToParse = misc.get_game_frames(self,game)
                        # self.playerObjects.append(player)
                        # self.ballObjects.append(game.ball)


                        # AHit.analyse_game_hits(game)
                        # APosition.analyse_game_possession(game)
                # except AttributeError:
                    # print(player.name+' has no ._name')
                    # print(game._name)
                    # return



        # position, speed = self.analyse_player_positions_and_speed()
        # hits = self.analyse_player_hits()
        possession = self.analyse_player_possession()

        self.position = position
        self.speed = speed
        self.possession = possession
        self.hits = hits


        pass

    def analyse_player_positions_and_speed(self):
        positions = []
        speeds = []
        half = []
        third = []
        height = []
        ballHalf = []
        allPlayerPositions = {}
        allPlayerSpeeds = []
        # positions = []
        # ballPositions = []
        # speeds = []


        for player,ball in zip(self.playerObjects,self.ballObjects):
            playerPositions = {} # frameNo:position. To sync with playerSpeeds
            ballPositions = {}
            playerSpeeds = {}
            for frameNo in player._framesToParse:
                playerPositions[frameNo] = player.positions[frameNo]
                ballPositions[frameNo] = (ball.positions[frameNo])
                try:
                    playerSpeeds[frameNo] = APosition.get_speed(player.velocities[frameNo])
                except:
                    # print('Cannot find velocity for '+player.name+' at frame '+str(frameNo))
                    # print(list(x for x in list(player.velocities.keys()) if abs(x-frameNo)< 10))
                    # print(list(player.velocities.keys()))
                    # break
                    pass

            _positions, _speeds = APosition.get_positions_speed_analysis(playerPositions,playerSpeeds,player,ballPositions)

            x = []
            for value in playerPositions.values():
                x.append(value)
            allPlayerPositions[player] = x

            allPlayerSpeeds += list(playerSpeeds.values())



            positions.append(_positions)
            speeds.append(_speeds)

        speed = misc.merge_dicts(speeds)
        position = misc.merge_dicts(positions)

        total = 0
        for key in half:
            total += half[key]

        averagePosition,averagePositionV = APosition.get_average_position(allPlayerPositions)

        position['average'] = averagePosition
        position['averageV'] = averagePositionV
        position['total'] = sum(len(allPlayerPositions[x]) for x in allPlayerPositions)

        averageSpeed = div(sum(allPlayerSpeeds),len(allPlayerSpeeds))

        speed['average'] = averageSpeed
        print('Raw Position Data:')
        print(position)
        print('Raw Speed Data:')
        print('Total Speeds: '+str(len(allPlayerSpeeds)))
        y = {}
        for x in speed:
            if type(speed[x]) is list:
                y[x]=len(speed[x])
            elif type(speed[x]) is dict:
                y[x] = {}
                for q in speed[x]:
                    y[x][q] = len(speed[x][q])
            else:
                y[x] = speed[x]
        print(y)

        return position,speed

    def analyse_player_position(self):
        session = db.Session()
        gameFrames = {} # replayid:[(start,end),..]
        for playerID in self.playerIDs:
            player = session.query(db.Player).filter(db.Player.id==playerID).one()
            frames = misc.get_game_frames(self,player.replay)
            gameFrames[player.replay.id] = frames
            # print(self.playerIDs,playerID)
            # stadium
            # map = player.replay.map
            # half
            # a = time.time()
            # x = session.query(db.Position).join(db.BallFrame,sq.and_(db.Position.frameNo==db.BallFrame.frameNo,db.Position.replay_id==db.BallFrame.replay_id)).filter(db.Position.player_id==playerID).all()
            # print(x)
        print(gameFrames)
        for replayid in gameFrames:
            totalFrames = sum((frame[1]-frame[0]) for frame in gameFrames[replayid])
            print(replayid,totalFrames)

        a = time.time()

        # x = session.query(db.Position, db.BallFrame, db.Replay.map, db.Team.colour)\
        x = session.query(db.Position.x,db.Position.y,db.Position.z, db.BallFrame.x,db.BallFrame.y,db.BallFrame.z, db.Replay.map, db.Team.colour)\
            .filter(db.Position.player_id.in_(self.playerIDs))\
            .filter(sq.or_(sq.and_(sq.or_(db.Position.frameNo.between(frames[0],frames[1]) for frames in gameFrames[replayid]),db.Position.replay_id==replayid) for replayid in gameFrames))\
            .join(db.BallFrame,db.BallFrame.frame_id==db.Position.frame_id)\
            .join(db.Replay)\
            .join(db.Player)\
            .filter(db.Player.id.in_(self.playerIDs))\
            .join(db.Team)
        # print(len(x.all()))
        # print(time.time()-_time)
        _time = time.time()
        positions = pd.read_sql_query(
                x.selectable,
                db.engine
            )

        print('Total Frames: ',len(positions))
        # print(positions[['positions_id','players_id']][:5])
            # try:
                # positions = pd.concat([positions,_positions])
                # print(2,len(positions),len(positions.columns.values))
            # except UnboundLocalError:
                # positions = _positions
                # print(1,len(positions),len(positions.columns.values))
        # print(positions)
        print('Total Duration:','{:.3}'.format(time.time()-a))
        position = APosition.analyse_position(positions)






    def analyse_player_hits(self):
        session = db.Session()

        x = session.query(db.Hit,db.Replay.map,db.Team.colour)\
            .filter(db.Hit.player_id.in_(self.playerIDs))\
            .join(db.Replay)\
            .join(db.Player)\
            .filter(db.Player.id.in_(self.playerIDs))\
            .join(db.Team)\
        # print(len(x.all()))
        # print(time.time()-_time)
        # _time = time.time()
        hits = pd.read_sql_query(
                x.selectable,
                db.engine
            )

        print(hits[:5])

        positions = hits.loc[:,['hits_x','hits_y','hits_z','replays_map','teams_colour']].rename(columns={'hits_x':'positions_x','hits_y':'positions_y','hits_z':'positions_z'})
        _hits = APosition.analyse_position(positions)

        keyNames = ['shot','goal','pass_','dribble','save']

        for item in keyNames:
            _hits[item] = {}

        totalHits = hits.hits_id.count()
        # print(_hits)

        for key in keyNames:
            counts = hits['hits_'+key].value_counts()

            # print(counts)
            for value in counts.index:
                _hits[key][value] = counts[value]
        # print(_hits)


        averageHitDistance = hits[hits['hits_distance']!=0]['hits_distance'].mean()
        averageShotDistance = hits[(hits['hits_distance']!=0) & (hits['hits_shot']>0)]['hits_distance'].mean()
        averagePassDistance = hits[(hits['hits_distance']!=0) & (hits['hits_pass_']>0)]['hits_distance'].mean()
        _hits['aveHitDistance'] = averageHitDistance
        _hits['aveShotDistance'] = averageShotDistance
        _hits['avePassDistance'] = averagePassDistance

        averageDribbleDistance, averageDribbleHits = AHit.get_average_dribble_distance(hits)
        _hits['aveDribbleDistance'] = averageDribbleDistance
        _hits['aveDribbleHits'] = averageDribbleHits
        print(_hits)
        return _hits







    # def analyse_player_hits(self):
        # self.hits = []
        # for player in self.playerObjects:
            # for hit in player.hits:
                # if hit.frameNo in player._framesToParse:
                    # self.hits.append(hit)
        # print('Found hits: '+str(len(self.hits)))
        # keyNames = ['half','third','height','shot','goal','pass_','dribble','save']

        # _hits = {item:{} for item in keyNames}

        # for hit in self.hits:
            # for key in _hits:
                # value = getattr(hit,key)
                # try:
                    # # print(key)
                    # # print(value)
                    # _hits[key][value] += 1

                # except KeyError:
                    # _hits[key][value] = 1
                # # _hits[key].append(getattr(hit,key))

        # totalHits = len(self.hits)

        # # hits = {}
        # # for key1,value1 in _hits.items():
            # # hits[key1] = {}
            # # for key2,value2 in value1.items():
                # # # convert raw numbers to %
                # # newValue = value2/totalHits
                # # hits[key1][key2] = newValue

        # hits = _hits
        # hits['total'] = totalHits
        # print('Raw Hit data:')
        # print(hits)

        # averageHitDistance = AHit.get_average_hit_distance(self.hits)
        # hits['aveHitDistance'] = averageHitDistance
        # averageShotDistance = AHit.get_average_shot_distance(self.hits)
        # hits['aveShotDistance'] = averageShotDistance

        # averagePassDistance = AHit.get_average_hit_distance(list(hit for hit in self.hits if hit.pass_))
        # hits['avePassDistance'] = averagePassDistance

        # averageDribbleDistance,averageDribbleHits = AHit.get_average_dribble_distance(self.hits)
        # hits['aveDribbleDistance'] = averageDribbleDistance
        # hits['aveDribbleHits'] = averageDribbleHits
        # # print(hits)
        # return hits

    def analyse_player_possession(self):
        possessionP = 0
        possessionH = 0
        totalFrames = 0
        for player in self.playerObjects:
            # print('Analysing '+str(len(player._framesToParse))+' frames')
            for frame in player._framesToParse:
                if frame in player.possessionP:
                    possessionP += 1
                if frame in player.possessionH:
                    possessionH += 1
            totalFrames += len(player._framesToParse)
        possession = {'h':possessionH/totalFrames,'p':possessionP/totalFrames}

        return possession

    def output_all(player):
        hitsTotal = player.hits.get('total',0)
        # print(player.hits)
        averageHitDistance = player.hits['aveHitDistance']
        hitsAttacking = player.hits['half'].get(1,0)
        shotsTotal = sum(player.hits['shot'][x] for x in player.hits['shot'] if x)
        averageShotDistance = round(player.hits['aveShotDistance'])

        goalsTotal = sum(player.hits['goal'][x] for x in player.hits['goal'] if x)
        assistedTotal = player.hits['goal'].get(2,0)

        passesTotal = sum(player.hits['pass_'][x] for x in player.hits['pass_'] if x)
        assistsTotal = player.hits['pass_'].get(2,0)
        secondAssistsTotal = player.hits['pass_'].get(3,0)
        averagePassDistance = player.hits['avePassDistance'] # sum(hit.distance for hit in player.hits if hit.pass_>=1)/passesTotal

        dribblesTotal = player.hits['dribble'].get(2,0)
        averageDribbleDistance = player.hits['aveDribbleDistance'] # sum(hit.distance for hit in player.hits if hit.dribble==1)/dribblesTotal
        averageDribbleHits = "{:.2}".format(float(player.hits['aveDribbleHits']))

        savesTotal = player.hits['save'].get(1,0)
        failedSavesTotal = player.hits['save'].get(-1,0)

        # # get hit variables
        # for hit in player.hits:
            # if hit.half == 1:
                # hitsAttacking += 1
            # if hit.shot >= 1:
                # shotsTotal += 1
            # if hit.goal >= 1:
                # goalsTotal += 1
                # if hit.goal == 2:
                    # assistedTotal += 1
            # if hit.pass_ >= 1:
                # passesTotal += 1
                # if hit.pass_ == 2:
                    # assistsTotal += 1
                # elif hit.pass_ == 3:
                    # secondAssistsTotal += 1
            # if hit.dribble == 2:
                # dribblesTotal += 1
            # if hit.save == 1:
                # savesTotal += 1
            # elif hit.save == -1:
                # failedSavesTotal += 1

        averagePosition = player.position['average']
        averagePositionV = player.position['averageV']



        output = player._name+'\n'
        output += 'Total Hits: '+str(hitsTotal)+'\n'
        output += 'Average Hit Distance: '+str(round(averageHitDistance))+'\n'
        # hits
        # hitsDefending = sum(hit.half==0 for hit in player.hits)
        output += '    Attacking Half: '+str(hitsAttacking)+' ('+"{:.1%}".format(div(hitsAttacking,hitsTotal))+')    Defending Half: '+str(hitsTotal-hitsAttacking)+' ('+"{:.1%}".format(div((hitsTotal-hitsAttacking),hitsTotal))+')\n'
            # shots
        output +='Total Shots: '+str(shotsTotal)+' ('+"{:.1%}".format(div(shotsTotal,hitsTotal))+')\n'
        output += '    Average Shot Distance: '+str(round(averageShotDistance))+'\n'
        output += '    Total Goals: '+str(goalsTotal)+' ('+"{:.1%}".format(div(goalsTotal,shotsTotal))+')\n'
        output += '        Was Assisted: '+str(assistedTotal)+' ('+"{:.1%}".format(div(assistedTotal,goalsTotal))+')\n'
            # passes
        output += 'Total Passes: '+str(passesTotal)+' ('+"{:.1%}".format(div(passesTotal,hitsTotal))+')\n'
        output += '    Total Assists: '+str(assistsTotal)+' ('+"{:.1%}".format(div(assistsTotal,passesTotal))+')\n'
        output += '        Secondary Assists: '+str(secondAssistsTotal)+' ('+"{:.1%}".format(div(secondAssistsTotal,passesTotal))+')\n'
        output += '    Average Pass Distance: '+str(round(averagePassDistance))+'\n'
            # dribbles
        output += 'Total Dribbles: '+str(dribblesTotal)+' ('+"{:.1%}".format(div(dribblesTotal,hitsTotal))+')\n'
        output += '    Average Dribble Distance: '+str(round(averageDribbleDistance))+'\n'
        output += '    Average Dribble Hits: '+str(averageDribbleHits)+'\n'
            # saves
        output += 'Total Saves: '+str(savesTotal)+' ('+"{:.1%}".format(div(savesTotal,hitsTotal))+')\n'
        output += '    Failed Saves: '+str(failedSavesTotal)+' ('+"{:.1%}".format(div(failedSavesTotal,hitsTotal))+')\n'


        # possession
        output += '\n'
        output += 'Possession (by hit): ' + "{:.1%}".format(player.possession['h']) +'\n'
        output += 'Possession (by position): ' + "{:.1%}".format(player.possession['p']) +'\n'

        # position
        positionsTotal = player.position['total']
        inAttHalf = player.position['half'][1]
        inAttThird = player.position['third'][1]
        inMidThird = player.position['third'][0]
        inOwnThird = player.position['third'][-1]
        onGround = player.position['height'][0]
        underGoal = player.position['height'][1]
        aboveGoal = player.position['height'][2]

        frontOfBall = player.position['ball']

        output += '\n'
        output += 'Average Position: ' + str(list(int(x) for x in averagePosition)) + '   v: ' + str(list(list(int(y) for y in x) for x in averagePositionV))+'\n'
        # print(player.position)

        output += 'In Attacking Half: '+"{:.1%}".format(div(inAttHalf,positionsTotal))+'    Defending Half: '+"{:.1%}".format(div((positionsTotal-inAttHalf),positionsTotal))+'\n'

        output += 'In Attacking Third: '+"{:.1%}".format(div(inAttThird,positionsTotal))+'    Middle Third: '+"{:.1%}".format(div(inMidThird,positionsTotal))+'    Defending Third: '+"{:.1%}".format(div(inOwnThird,positionsTotal))+'\n'

        output += 'On Ground: '+"{:.1%}".format(div(onGround,positionsTotal))+'    Under Goal: '+"{:.1%}".format(div(underGoal,positionsTotal))+"    Above Goal: "+"{:.1%}".format(div(aboveGoal,positionsTotal))+'\n'
        output += 'In Front of Ball: '+"{:.1%}".format(div(frontOfBall[1],positionsTotal))+'    Behind Ball: '+"{:.1%}".format(div(frontOfBall[0],positionsTotal))+'\n'

        # speed
        averageSpeed = player.speed['average']
        speedAttacking = div(sum(player.speed['half'][1]),len(player.speed['half'][1]))
        speedDefending = div(sum(player.speed['half'][0]),len(player.speed['half'][0]))

        output += '\n'
        output += 'Average Speed: ' + str(round(averageSpeed)) + '\n'

        output += '    In Attacking Half: ' + str(round(speedAttacking)) + '    In Defending Half: ' + str(round(speedDefending))

        output += '\n\n'


        return output




