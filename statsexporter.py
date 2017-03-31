import pyroplane.anal
from pyroplane.anal.aplayer import APlayer
from pyroplane.anal.ateam import ATeam
import pyroplane.database.database as db
import pyroplane.misc

class StatsExporter:

    def __init__(self,dataOptions,typeOptions):
        # data accepting
        (self.replayIDs,self.rTeamIDs,self.rPlayerIDs) = dataOptions

        for x in typeOptions[0]:
            self.plotBy = x
            self.plotByData = typeOptions[0][x]

        self.plotOvertime,_,_,_,self.plotBall = typeOptions[1]


        session = db.Session()

        self.replays = {} # id:frames

        if self.replayIDs:
            results = session.query(db.Replay).filter(db.Replay.id.in_(self.replayIDs)).all()
            for replay in results:
                frames = misc.get_game_frames(self,replay)
                self.replays[replay.id] = frames
        # print(frames)



        output = ''
        if self.rPlayerIDs:
            for rPlayerID in self.rPlayerIDs:
                aPlayer = APlayer(rPlayerID,self.replays,self.plotBy,self.plotByData,self.plotOvertime)
                output += APlayer.output_all(aPlayer)
                # print(output)

        # self.output = ''
        self.output = output
        db.Session.remove()

    def get_header(self):
        header = ''
        header += 'Games Selected: '
        for game in games:
            header += str(game.fileName)+' ('+str(game._name)+'), '
        header.rstrip(', ')
        header += '\n'
        if self.players:
            header += 'Players Selected: '
            for player in self.players:
                header += str(player.name)+' ('+str(player._name)+'), '
            header.rstrip(', ')
            header += '\n'
        elif self.teams:
            header += 'Teams Selected: '
            for team in teams:
                header += str(team._name)+', '
            header.rstrip(', ')
            header += '\n'
        header += 'Data Gathered by: '
        header += str(self.plotBy).title()+' ('+str(self.plotByData)+')'
        header += '\n'

        if not self.plotOvertime:
            header += 'Overtime not inluded.\n'


# team stats:
    # total hits
        # attacking half (%), defending half (%)
    # total shots (on target) (% of hits)
        # average shot distance from goal
        # total goals (% of shots)
            #  total assisted (% of goals)

    # total passes (% of hits)
        # total assists (% of passes)
            # total secondary assists
        # average pass distance
    # total dribbles (% of hits)
        # average dribble distance)
    # total saves (failed)

    # possession (by hit) (by position)

    # average position - can use player position analysis functions.
        # attacking half %, defending half %
        # attacking third, middle third, defending third
        # on ground, under goal, above goal.
        #!!! % time with x players behind ball
            # 0, 1, 2, 3
        # in box %

    # average speed
        # attacking half, defending half


# player stats:
    # total hits
        # attacking half (%), defending half (%)
    # total shots (on target) (% of hits)
        # average shot distance from goal
        # total goals(% of shots)
            # total assisted (% of goals)

    # total passes (% of hits)
        # total assists (% of passes)
            # total secondary assists
        # average pass distance
    # total dribbles (% of hits)
        # average dribble distance
    # total saves (failed)

    # possession (by hit) (by position)

    # average position - can use player position analysis functions.
        # attacking half %, defending half %
        # attacking third, middle third, defending third
        # on ground, under goal, above goal
        #!!! % time behind ball, % in front of ball
        # in box %

    # average speed
        # attacking half, defending half



    # player
        # hits
            # avehitdistance
            # half (1 for attacking half, 0 for defending half)
            # shot (1 for shot, 2 for shot on target)
            # aveshotdistance
            # goal (1 for goal, 2 for assisted goal)
            # pass_ (1 for pass, 2 for assist, 3 for secondary assist)
            # avepassdistance
            # dribble (1 for dribble, (2 for start))
            # avedribbledistance, avedribblehits
            # saves (1 for save, -1 for failed save)
        # possession
            # h:
            # p:

        # position
            # total:number of frames
            # average:
            # averageV:
            # half:{0:,1:}
            # third:{-1:,0:,1:}
            # height:{0:,1:,2:}
            # ball {0:,1:}
            # # for team:
            # ball {0:,1:,2:,3:) for number of players in front of ball
            # # box:%
        # speed
            # average:
            # half:{0:,1:}
