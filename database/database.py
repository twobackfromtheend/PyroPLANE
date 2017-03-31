import datetime as dt
import time
import sqlalchemy as sq
import Levenshtein as lv
import sys
import os
import tqdm
import pysickle.game
from sqlalchemy.ext.declarative import declarative_base
from pickle import load
# import Levenshtein as lv
# import time
import pyroplane.anal.hit as h
from pyroplane.anal.ahit import AHit

# with open('a.db','w') as f:
#     f.write('')

global tmtxtmd5
tmtxtmd5 = ''
global engine
engine = sq.create_engine('sqlite:///a.db',)
session_factory = sq.orm.sessionmaker(bind=engine)
Session = sq.orm.scoped_session(session_factory)

Base = declarative_base()

gameTeamTable = sq.Table('gameteamtable', Base.metadata,
                         sq.Column('replays_id', sq.Integer,
                                   sq.ForeignKey('replays.id')),
                         sq.Column('rteams_id', sq.Integer,
                                   sq.ForeignKey('rteams.id'))
                         )


class Replay(Base):
    __tablename__ = 'replays'

    id = sq.Column(sq.Integer, primary_key=True)
    name = sq.Column(sq.String)
    filePath = sq.Column(sq.String)
    maxFrameNo = sq.Column(sq.Integer)
    maxTimeRemaining = sq.Column(sq.Integer)

    # header stuff
    dateTime = sq.Column(sq.DateTime)
    map = sq.Column(sq.String)
    replayID = sq.Column(sq.String)

    rteams = sq.orm.relationship(
        'RTeam',
        secondary=gameTeamTable,
        back_populates='replays')
    teams = sq.orm.relationship(
        'Team',
        back_populates='replay'
    )
    players = sq.orm.relationship(
        'Player',
        back_populates='replay'
    )
    ball = sq.orm.relationship(
        'Ball',
        uselist=False,
        back_populates='replay'
    )
    hits = sq.orm.relationship(
        'Hit',
        back_populates='replay'
    )
    goals = sq.orm.relationship(
        'Goal',
        back_populates='replay'
    )
    frameVar = sq.Column(sq.Integer)
    frames = sq.orm.relationship(
        'Frame',
        back_populates='replay'
    )
    positions = sq.orm.relationship(
        'Position',
        back_populates='replay'
    )
    velocities = sq.orm.relationship(
        'Velocity',
        back_populates='replay'
    )
    ballframes = sq.orm.relationship(
        'BallFrame',
        back_populates='replay'
    )

    def import_replay(filePath):
        startTime = time.time()
        session = Session()
        # check if filepath has been added
        exists = session.query(Replay).filter(
            Replay.filePath == filePath).count()
        if exists:
            print('Replay file already added to database. (File Path check)')
            return None
        with open(filePath, 'rb') as f:
            _pysickle = load(f)

        # check if replayid has been added
        replayID = _pysickle.metadata['Id']['Value']
        exists = session.query(Replay).filter(
            Replay.replayID == replayID).count()
        if exists:
            print('Replay file already added to database. (Replay ID check)')
            return None

        _pysickle.hits = h.Hit._add_all_hits2(_pysickle)
        if len(_pysickle.hits) == 0:
            print("Warning: No hits found.")
        # print('Hits:', _pysickle.hits)
        h.Hit.get_firstHit(_pysickle)

        loadTime = time.time()
        print('Loaded pysickle in', '{:.2}'.format(loadTime - startTime), 's')

        # add replay
        try:
            dateTime = dt.datetime.strptime(_pysickle.metadata['Date'][
                                            'Value'], '%Y-%m-%d %H-%M-%S')
        except ValueError:
            dateTime = dt.datetime.strptime(_pysickle.metadata['Date'][
                                            'Value'], '%Y-%m-%d:%H-%M')
        replay = Replay(
            filePath=filePath,
            maxFrameNo=_pysickle.maxFrameNo,
            dateTime=dateTime,
            map=_pysickle.metadata['MapName']['Value'],
            replayID=replayID  # redundant but looks good.
        )
        session.add(replay)
        session.commit()

        frameVar = Frame.add_frames(_pysickle.frames, replay, session)
        replay.frameVar = frameVar
        # replay's frame x can be accessed with id=frameVar+x

        # teams, players and game scores
        gameScore = {}
        print('Adding players and teams.')

        for _team in _pysickle.teams:
            team = Team.add_team(replay, _team.colour)
            players = []
            for _player in _team.players:
                player = Player.add_player(_player, replay, team, session)
                players.append(player)
                print('Added player: ' + str(_player.name))
            RTeam.add_rteam(team, replay, session)
            for player in players:
                RPlayer.add_rplayer(player, session)

            gameScore[team.colour] = dict(
                name=team.rteam.name,
                goals=0)
        print('Adding ball.')
        Ball.add_ball(_pysickle.ball, replay, session)
        print('Done.')
        print('Adding goals.')
        Goal.add_goals(_pysickle.goals, replay, session)
        print('Done.')
        print('Adding hits.')
        AHit.analyse_game_hits(_pysickle)
        Hit.add_hits(_pysickle.hits, replay, session)
        print('Done.')

        print('Parsed replay, adding to database.')
        # x = session.query(Player.positions).filter_by(('name')==(_player.name)).count()

        replay.name = Replay.get_name(_pysickle, replay, gameScore)
        session.commit()
        endTime = time.time()
        print('Finished parsing: ', replay.name, ' in', '{:.2}'.format(
            endTime - loadTime), 's', ' (Total time:', '{:.2}'.format(endTime - startTime), 's)')
        Session.remove()

        # for player in replay.players:
        # print(player.name, len(player.positions))
        return replay

    def get_name(pysickle, replay, gameScore):
        for goal in pysickle.goals:
            try:
                gameScore[goal.player.team.colour]['goals'] += 1
            except KeyError:
                gameScore[goal.player.team.colour]['goals'] = 1

        gameName = ''
        for teamScore in gameScore.values():
            gameName += str(teamScore['name']) + \
                ': ' + str(teamScore['goals']) + ', '
        gameName = gameName.rstrip(', ')
        return gameName

    def refresh_all_teamNames():
        session = Session()
        session.query(RTeam).delete()
        session.query(RPlayer).delete()
        startTime = time.time()
        replays = session.query(Replay).all()
        for replay in tqdm.tqdm(replays):
            with open(os.devnull, "w") as devnull:
                sys.stdout = devnull

                gameScore = {}
                for team in replay.teams:
                    RTeam.add_rteam(team, replay, session)
                    for player in team.players:
                        RPlayer.add_rplayer(player, session)
                    gameScore[team.colour] = dict(
                        name=team.rteam.name,
                        goals=0)

            replay.name = Replay.get_name(replay, replay, gameScore)
            # print(replay.name)
        session.commit()
        Session.remove()
        sys.stdout = sys.__stdout__
        duration = '{:.2}'.format(time.time() - startTime)
        print('Completed renaming of', len(
            replays), 'replays in', duration, 's')


class RTeam(Base):
    __tablename__ = 'rteams'
    id = sq.Column(sq.Integer, primary_key=True)
    name = sq.Column(sq.String)
    replays = sq.orm.relationship(
        'Replay',
        secondary=gameTeamTable,
        back_populates='rteams')
    teams = sq.orm.relationship(
        'Team',
        back_populates='rteam'
    )
    rplayers = sq.orm.relationship(
        'RPlayer',
        back_populates='rteam'
    )

    def add_rteam(team, replay, session):
        teamName = TeamName.get_team_name(team, session)
        # check if team already added
        exists = session.query(RTeam).filter(
            RTeam.name == teamName).one_or_none()
        if exists:
            print('Already added real team: ', teamName)
            rteam = exists
        else:
            rteam = RTeam(name=teamName)
            session.add(rteam)

            print('Added real team: ', teamName)

        rteam.replays.append(replay)
        team.rteam = rteam
        session.commit()


class RPlayer(Base):
    __tablename__ = 'rplayers'
    id = sq.Column(sq.Integer, primary_key=True)
    name = sq.Column(sq.String)
    players = sq.orm.relationship(
        'Player',
        back_populates='rplayer'
    )
    rteam_id = sq.Column(sq.Integer, sq.ForeignKey('rteams.id'))
    rteam = sq.orm.relationship(
        'RTeam',
        back_populates='rplayers'
    )

    def add_rplayer(player, session):
        playerName = PlayerName.get_player_name(player, session)
        # check if team already added
        exists = session.query(RPlayer).filter(
            RPlayer.name == playerName).one_or_none()
        if exists:
            print('Already added real player: ', playerName)
            rplayer = exists
        else:
            rteam = player.team.rteam
            rplayer = RPlayer(name=playerName, rteam=player.team.rteam)
            session.add(rplayer)

            print('Added real player: ', playerName)

        player.rplayer = rplayer
        session.commit()
        return rplayer


class Team(Base):
    __tablename__ = 'teams'
    id = sq.Column(sq.Integer, primary_key=True)
    colour = sq.Column(sq.String)
    replay_id = sq.Column(sq.Integer, sq.ForeignKey('replays.id'))
    replay = sq.orm.relationship(
        'Replay',
        back_populates='teams'
    )
    rteam_id = sq.Column(sq.Integer, sq.ForeignKey('rteams.id'))
    rteam = sq.orm.relationship(
        'RTeam',
        back_populates='teams'
    )
    players = sq.orm.relationship(
        'Player',
        back_populates='team'
    )

    def add_team(replay, colour):
        team = Team(replay=replay, colour=colour)
        return team


class Player(Base):
    __tablename__ = 'players'
    id = sq.Column(sq.Integer, primary_key=True)
    name = sq.Column(sq.String)
    gameID = sq.Column(sq.Integer)
    replay_id = sq.Column(sq.Integer, sq.ForeignKey('replays.id'))
    replay = sq.orm.relationship(
        'Replay',
        back_populates='players'
    )
    team_id = sq.Column(sq.Integer, sq.ForeignKey('teams.id'))
    team = sq.orm.relationship(
        'Team',
        back_populates='players'
    )

    positions = sq.orm.relationship(
        'Position',
        back_populates='player'
    )
    velocities = sq.orm.relationship(
        'Velocity',
        back_populates='player'
    )
    hits = sq.orm.relationship(
        'Hit',
        back_populates='player'
    )
    goals = sq.orm.relationship(
        'Goal',
        back_populates='player'
    )

    rplayer_id = sq.Column(sq.Integer, sq.ForeignKey('rplayers.id'))
    rplayer = sq.orm.relationship(
        'RPlayer',
        back_populates='players',
    )

    def add_player(_player, replay, team, session):
        player = Player(
            name=_player.name,
            gameID=_player.gameID,
            replay=replay,
            team=team,
        )
        session.add(player)
        session.commit()
        Position.add_player_positions(player, _player, session)
        Velocity.add_player_velocities(player, _player, session)

        return player


class Ball(Base):
    __tablename__ = 'balls'
    id = sq.Column(sq.Integer, primary_key=True)
    replay_id = sq.Column(sq.Integer, sq.ForeignKey('replays.id'))
    replay = sq.orm.relationship(
        'Replay',
        back_populates='ball'
    )
    ballframes = sq.orm.relationship(
        'BallFrame',
        back_populates='ball'
    )

    def add_ball(pysickleball, replay, session):
        ball = Ball(
            replay=replay,
        )
        session.add(ball)
        session.commit()
        BallFrame.add_ballframes(ball, pysickleball, session)

        return ball


class BallFrame(Base):
    __tablename__ = 'ballframes'
    id = sq.Column(sq.Integer, primary_key=True)
    ball_id = sq.Column(sq.Integer, sq.ForeignKey('balls.id'))
    ball = sq.orm.relationship(
        'Ball',
        back_populates='ballframes'
    )

    x = sq.Column(sq.Integer)
    y = sq.Column(sq.Integer)
    z = sq.Column(sq.Integer)

    vx = sq.Column(sq.Integer)
    vy = sq.Column(sq.Integer)
    vz = sq.Column(sq.Integer)

    frameNo = sq.Column(sq.Integer)
    frame_id = sq.Column(sq.Integer)

    replay_id = sq.Column(sq.Integer, sq.ForeignKey('replays.id'))
    replay = sq.orm.relationship(
        'Replay',
        back_populates='ballframes'
    )

    def add_ballframes(ball, pysickleball, session):
        bf = []
        bid = ball.id
        rid = ball.replay.id
        frameVar = ball.replay.frameVar

        for frameNo in range(len(pysickleball.positions)):
            try:
                vx = pysickleball.velocities[frameNo][0]
            except KeyError:
                vx = None
            try:
                vy = pysickleball.velocities[frameNo][1]
            except KeyError:
                vy = None
            try:
                vz = pysickleball.velocities[frameNo][2]
            except KeyError:
                vz = None
            ballframe = dict(
                frameNo=frameNo,
                frame_id=frameVar + frameNo,
                x=pysickleball.positions[frameNo][0],
                y=pysickleball.positions[frameNo][1],
                z=pysickleball.positions[frameNo][2],
                vx=vx,
                vy=vy,
                vz=vz,
                ball_id=bid,
                replay_id=rid,
            )
            bf.append(ballframe)

        session.execute(BallFrame.__table__.insert(), bf)


class Frame(Base):
    __tablename__ = 'frames'

    id = sq.Column(sq.Integer, primary_key=True)

    replay_id = sq.Column(sq.Integer, sq.ForeignKey('replays.id'))
    replay = sq.orm.relationship(
        'Replay',
        back_populates='frames'
    )
    frameNo = sq.Column(sq.Integer)
    timeRemaining = sq.Column(sq.Integer)
    isOvertime = sq.Column(sq.Boolean)

    def add_frames(pysickleframes, replay, session):
        fs = []
        rid = replay.id
        add = rid * 1000000000

        maxTimeRemaining = 0
        for frame in pysickleframes:
            f = dict(
                id=add + frame.frameNo,
                replay_id=rid,
                frameNo=frame.frameNo,
                timeRemaining=frame.timeRemaining,
                isOvertime=frame.isOvertime
            )
            fs.append(f)
            # print(frame.timeRemaining)
            if frame.timeRemaining > maxTimeRemaining:
                maxTimeRemaining = frame.timeRemaining

        session.execute(Frame.__table__.insert(), fs)
        replay.maxTimeRemaining = maxTimeRemaining
        return add


class Position(Base):
    __tablename__ = 'positions'
    id = sq.Column(sq.Integer, primary_key=True)
    frameNo = sq.Column(sq.Integer)
    frame_id = sq.Column(sq.Integer)
    x = sq.Column(sq.Integer)
    y = sq.Column(sq.Integer)
    z = sq.Column(sq.Integer)
    pitch = sq.Column(sq.Float)
    yaw = sq.Column(sq.Float)
    roll = sq.Column(sq.Float)

    player_id = sq.Column(sq.Integer, sq.ForeignKey('players.id'))
    player = sq.orm.relationship(
        'Player',
        back_populates='positions'
    )
    replay_id = sq.Column(sq.Integer, sq.ForeignKey('replays.id'))
    replay = sq.orm.relationship(
        'Replay',
        back_populates='positions'
    )

    def add_player_positions(player, pysickleplayer, session):
        p = []
        pid = player.id
        rid = player.replay.id
        frameVar = player.replay.frameVar

        for frameNo in range(len(pysickleplayer.positions)):
            try:
                pitch = pysickleplayer.rotations[frameNo][0]
            except KeyError:
                pitch = None
            try:
                yaw = pysickleplayer.rotations[frameNo][1]
            except KeyError:
                yaw = None
            try:
                roll = pysickleplayer.rotations[frameNo][2]
            except KeyError:
                roll = None
            position = dict(
                frameNo=frameNo,
                frame_id=frameVar + frameNo,
                x=pysickleplayer.positions[frameNo][0],
                y=pysickleplayer.positions[frameNo][1],
                z=pysickleplayer.positions[frameNo][2],
                pitch=pitch,
                yaw=yaw,
                roll=roll,

                player_id=pid,
                replay_id=rid
            )
            p.append(position)
        # session.bulk_insert_mappings(Position,p)
        session.execute(Position.__table__.insert(), p)

    def get_positions(player, frames):
        session = Session()
        # frames is [(startFrame,endFrame),..]
        positions = session.query(Position.x, Position.y, Position.z).filter(Position.player_id == player.id).filter(
            sq.or_(Position.frameNo.between(frame[0], frame[1]) for frame in frames))
        return positions


class Velocity(Base):
    __tablename__ = 'velocities'
    id = sq.Column(sq.Integer, primary_key=True)
    frameNo = sq.Column(sq.Integer)
    frame_id = sq.Column(sq.Integer)
    x = sq.Column(sq.Integer)
    y = sq.Column(sq.Integer)
    z = sq.Column(sq.Integer)
    speed = sq.Column(sq.Integer)

    player_id = sq.Column(sq.Integer, sq.ForeignKey('players.id'))
    player = sq.orm.relationship(
        'Player',
        back_populates='velocities'
    )
    replay_id = sq.Column(sq.Integer, sq.ForeignKey('replays.id'))
    replay = sq.orm.relationship(
        'Replay',
        back_populates='velocities'
    )

    def add_player_velocities(player, pysickleplayer, session):
        v = []
        pid = player.id
        rid = player.replay.id
        frameVar = player.replay.frameVar

        for frameNo in pysickleplayer.velocities:  # is dict
            velocity = dict(
                frameNo=frameNo,
                frame_id=frameVar + frameNo,
                x=pysickleplayer.velocities[frameNo][0],
                y=pysickleplayer.velocities[frameNo][1],
                z=pysickleplayer.velocities[frameNo][2],
                player_id=pid,
                speed=Velocity.get_speed(pysickleplayer.velocities[frameNo]),
                replay_id=rid
            )
            v.append(velocity)
        session.execute(Velocity.__table__.insert(), v)

    def get_speed(velocity):
        total = 0
        for x in velocity:
            total += x**2
        speed = total**0.5
        return speed


class Hit(Base):
    __tablename__ = 'hits'

    id = sq.Column(sq.Integer, primary_key=True)
    replay_id = sq.Column(sq.Integer, sq.ForeignKey('replays.id'))
    replay = sq.orm.relationship(
        'Replay',
        back_populates='hits'
    )
    player_id = sq.Column(sq.Integer, sq.ForeignKey('players.id'))
    player = sq.orm.relationship(
        'Player',
        back_populates='hits'
    )
    frameNo = sq.Column(sq.Integer)
    # frame_id = sq.Column(sq.Integer)

    x = sq.Column(sq.Integer)
    y = sq.Column(sq.Integer)
    z = sq.Column(sq.Integer)

    vx = sq.Column(sq.Integer)
    vy = sq.Column(sq.Integer)
    vz = sq.Column(sq.Integer)

    pass_ = sq.Column(sq.Integer)
    dribble = sq.Column(sq.Integer)
    shot = sq.Column(sq.Integer)
    goal = sq.Column(sq.Integer)
    save = sq.Column(sq.Integer)
    distance = sq.Column(sq.Integer)
    distanceToGoal = sq.Column(sq.Integer)

    def add_hits(pysicklehits, replay, session):
        h = []
        rid = replay.id
        for hit in pysicklehits:
            pgameid = hit.player.gameID

            player = session.query(Player).join(Replay).filter(
                Replay.id == rid).filter(Player.gameID == pgameid).one()

            try:
                distanceToGoal = hit.distanceToGoal
            except AttributeError:
                distanceToGoal = -1

            _hit = dict(
                replay_id=rid,
                player_id=player.id,
                frameNo=hit.frameNo,
                # frame_id = hit.frameNo + replay.frameVar,

                x=hit.position[0],
                y=hit.position[1],
                z=hit.position[2],

                vx=hit.velocity[0],
                vy=hit.velocity[1],
                vz=hit.velocity[2],

                pass_=hit.pass_,
                dribble=hit.dribble,
                shot=hit.shot,
                goal=hit.goal,
                save=hit.save,
                distance=hit.distance,
                distanceToGoal=distanceToGoal,
            )
            h.append(_hit)
        session.execute(Hit.__table__.insert(), h)

    def recalculate_all_hits():
        pass


class Goal(Base):
    __tablename__ = 'goals'

    id = sq.Column(sq.Integer, primary_key=True)
    replay_id = sq.Column(sq.Integer, sq.ForeignKey('replays.id'))
    replay = sq.orm.relationship(
        'Replay',
        back_populates='goals'
    )
    player_id = sq.Column(sq.Integer, sq.ForeignKey('players.id'))
    player = sq.orm.relationship(
        'Player',
        back_populates='goals'
    )
    frameNo = sq.Column(sq.Integer)
    firstHitFrame = sq.Column(sq.Integer)

    def add_goals(pysicklegoals, replay, session):
        g = []
        rid = replay.id
        for goal in pysicklegoals:
            pgameid = goal.player.gameID
            player = session.query(Player).join(Replay).filter(
                Replay.id == rid).filter(Player.gameID == pgameid).one()
            _goal = dict(
                replay_id=rid,
                player_id=player.id,
                frameNo=goal.frameNo,
                firstHitFrame=goal.firstHit
            )
            g.append(_goal)

        session.execute(Goal.__table__.insert(), g)


class TeamName(Base):
    __tablename__ = 'teamnames'

    id = sq.Column(sq.Integer, primary_key=True)
    name = sq.Column(sq.String)
    players = sq.orm.relationship(
        'PlayerName',
        back_populates='teamName'
    )

    def load_teams_txt(filePath):
        session = Session()
        try:
            x = session.query(TeamName).delete()
            y = session.query(PlayerName).delete()
            if x:
                print('Deleted ' + str(x) + ' rows from Team Names.')
            if y:
                print('Deleted ' + str(y) + ' rows from Player Names.')
        except:
            print('Cannot delete current name data.')
        with open(filePath, 'r') as teamFile:
            for line in teamFile:
                names = (list(x.rstrip() for x in line.split(',')))
                # print(names)
                _teamName = names[0]
                if _teamName:
                    teamName = TeamName(name=_teamName)
                    session.add(teamName)

                    for playerName in names[1:]:
                        if playerName:
                            session.add(PlayerName(
                                name=playerName, teamName=teamName))

        # for x in session.query(TeamName).all():
            # print(x.name)
            # y = session.query(TeamName).join(PlayerName).filter(TeamName.id ==x.id).count()
            # print(y)

        session.commit()

    def get_team_name(team, session):
        teamid = team.id
        teams = {}
        # session.commit()
        playerNames = session.query(Player.name).join(
            Team).filter(Player.team_id == team.id).all()
        # print(type(players),players)
        for (playerName,) in playerNames:
            # read every line for name.
            for tn in session.query(TeamName):
                teamName = tn.name
                # find levenshtein distance between text name and player name
                for (pn,) in session.query(PlayerName.name).join(TeamName).filter(TeamName.id == tn.id).all():
                    ratio = lv.ratio(playerName, pn)
                    # print(player.name, pn.name, '{:.1%}'.format(ratio))
                    if ratio > 0.5:
                        try:
                            teams[teamName] += 1
                        except KeyError:
                            teams[teamName] = 1
        # find teamname with most players
        print(teams)
        if teams:
            teamName = max(teams, key=lambda key: teams[key])
            print('Found team: ', teamName)
        else:
            teamName = team.colour.capitalize()

        return teamName


class PlayerName(Base):
    __tablename__ = 'playernames'

    id = sq.Column(sq.Integer, primary_key=True)
    name = sq.Column(sq.String)
    teamName_id = sq.Column(sq.Integer, sq.ForeignKey('teamnames.id'))
    teamName = sq.orm.relationship(
        'TeamName',
        back_populates='players'
    )

    def get_player_name(player, session):
        teamName = player.team.rteam.name
        playerNames = session.query(PlayerName.name).join(
            TeamName).filter(TeamName.name == teamName)
        names = {}
        for (playerName,) in playerNames:
            ratio = lv.ratio(player.name, playerName)
            if playerName in player.name:
                ratio += (len(playerName) * 0.1)
            if ratio > 0.4:
                names[playerName] = ratio
                print(playerName + ', ' + player.name +
                      ', ' + "{:.1%}".format(ratio))
        if names:
            playerName = max(names, key=lambda key: names[key])
            print('Found ', playerName)
        else:
            playerName = player.name
            print('Cannot find name for', player.name)
        return playerName


Base.metadata.create_all(engine)


# Session = create_game_database()
# session = Session()

# class RPlayer(Base):
# __tablename__ = 'rplayers'

# id = sq.Column(sq.Integer, primary_key=True)
# name = sq.Column(sq.String)
# _name = sq.Column(sq.String)
# team = sq.Column()
# player = sq.Column()
