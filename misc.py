import pyroplane.database as db


def load_game(self,parent,gameFile):
    from pickle import load
    from anal.hit import Hit
    from datapicker import DataPicker

    game = load(gameFile)
    gameFile.seek(0)
    game.hits = Hit.add_all_hits(game)
    Hit.get_firstHit(game)
    game._frames_to_parse = get_game_frames(self,game)



    # give teams the standard names
    for team in game.teams:
        team._name = DataPicker.get_team_name(parent,team)
    # give players their standard names
    for team in game.teams:
            for player in team.players:
                playerName = DataPicker.get_player_name(parent,player,team)
                if playerName:
                    player._name = playerName
                else:
                    player._name = player.name
                # print(player.name + ' is ' + player._name)
    return game


def get_game_frames(self,game):
    frames = []

    if self.plotBy == 'goals':
        noOfGoals = len(game.goals)
        if ':' in self.plotByData:
            firstGoal,lastGoal = list(int(x) for x in self.plotByData.split(':'))
            if firstGoal < 0:
                if -firstGoal > noOfGoals:
                    firstGoal = 0
                else:
                    firstGoal += noOfGoals
            if lastGoal < 0:
                if -lastGoal > noOfGoals:
                    lastGoal = 0
                else:
                    lastGoal += noOfGoals
            elif lastGoal == 0:
                lastGoal = noOfGoals
            goalsToPlot = list(range(firstGoal,lastGoal))
        elif self.plotByData == '0':
                goalsToPlot = list(range(noOfGoals))
        else:
            goalsToPlot = []
            for x in self.plotByData.split():
                if int(x) <= noOfGoals:
                    goalsToPlot.append(int(x)-1)

        # add all frames for goals in goalsToPlot
        for goal in goalsToPlot:
            frames.append((game.goals[goal].firstHitFrame,game.goals[goal].frameNo))
            # print(frames)

        # remove last goal phase is not plotting overtime
        if not self.plotOvertime:
            frames.pop()

    elif self.plotBy == 'time':
        _frames = []

        gameFrames = []
        for goal in game.goals:
            firstFrame = goal.firstHitFrame
            lastFrame = goal.frameNo
            for frameNo in range(firstFrame,lastFrame):
                gameFrames.append(frameNo)


        startTime = int(self.plotByData[0])
        if startTime == 0:
            startTime = 10000000
        endTime = int(self.plotByData[1])

        if self.plotOvertime:
            for frame in game.frames:
                if endTime <= frame.timeRemaining <= startTime:
                    _frames.append(frame.frameNo)
        else:
            for frame in game.frames:
                if (endTime <= frame.timeRemaining <= startTime) and (not frame.isOvertime):
                    _frames.append(frame.frameNo)

        # remove frames not in gameFrames
        i = 0
        while i < len(_frames):
            frame = _frames[i]
            if frame not in gameFrames:
                _frames.remove(frame)
            else:
                i += 1
        # print('_frames',_frames)
        # convert to ranges:
        startFrame = None
        for i in range(len(_frames)):
            if startFrame is None:
                startFrame = _frames[i]
                continue
            frame = _frames[i]
            try:
                # check next frame
                if _frames[i+1] == frame+1:
                    # ignore if next frame is in list
                    continue
                else:
                    # add new range if next frame is end
                    frames.append((startFrame,frame))

                    # reset
                    startFrame = None
            except IndexError:
                # last frame
                frames.append((startFrame,frame))


    return frames


def merge_dicts(dicts):
    result = {}
    for dict in dicts:
        for key1,value in dict.items():
            result[key1] = {}

            for key2,value2 in value.items():
                try:
                    result[key1][key2] += value2
                except KeyError:
                    result[key1][key2] = value2
                # if type(value2) is list:
                    # try:
                        # result[key1][key2] += value2
                    # except KeyError:
                        # result[key1][key2] = value2
                # else:
                    # try:
                        # result[key1][key2] += value2
                    # except KeyError:
                        # result[key][key2] = value2

    return result


def find_distance(a,b):
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


def div(a,b):
    if b != 0:
        return a/b
    else:
        return 0


def make_orange_side(position,player):
    # print('making orange')
    # print(position)

    if player.team.colour == 'blue':
        return [position[0],-position[1],position[2]]
    elif player.team.colour == 'orange':
        return position

