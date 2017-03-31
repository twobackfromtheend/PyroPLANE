import pyroplane.database.database as db
import sqlalchemy as sq
import pandas as pd
import time
import tqdm
from collections import OrderedDict


def analyse_all_player_hits():
    session = db.Session()

    count = session.query(db.Player.rplayer_id, sq.sql.func.count(
        '*').label('replay_count')).group_by(db.Player.rplayer_id).subquery()

    count_hits = session.query(db.Hit, db.Player.rplayer_id, sq.sql.func.count(
        '*').label('hits')).join(db.Player).group_by(db.Player.rplayer_id).subquery()

    count_pass = session.query(db.Hit, db.Player.rplayer_id, sq.sql.func.count(
        '*').label('passes')).filter(db.Hit.pass_ > 0).join(db.Player).group_by(db.Player.rplayer_id).subquery()
    count_assist = session.query(db.Hit, db.Player.rplayer_id, sq.sql.func.count(
        '*').label('assists')).filter(db.Hit.pass_ == 2).join(db.Player).group_by(db.Player.rplayer_id).subquery()
    count_shot = session.query(db.Hit, db.Player.rplayer_id, sq.sql.func.count(
        '*').label('shots')).filter(db.Hit.shot > 0).join(db.Player).group_by(db.Player.rplayer_id).subquery()
    count_shot_ot = session.query(db.Hit, db.Player.rplayer_id, sq.sql.func.count(
        '*').label('shots_ot')).filter(db.Hit.shot == 2).join(db.Player).group_by(db.Player.rplayer_id).subquery()
    count_goal = session.query(db.Hit, db.Player.rplayer_id, sq.sql.func.count(
        '*').label('goals')).filter(db.Hit.goal > 0).join(db.Player).group_by(db.Player.rplayer_id).subquery()
    count_assisted_goal = session.query(db.Hit, db.Player.rplayer_id, sq.sql.func.count(
        '*').label('assisted_goals')).filter(db.Hit.goal == 2).join(db.Player).group_by(db.Player.rplayer_id).subquery()

    count_dribble = session.query(db.Hit, db.Player.rplayer_id, sq.sql.func.count(
        '*').label('dribbles')).filter(db.Hit.dribble == 2).join(db.Player).group_by(db.Player.rplayer_id).subquery()
    count_save = session.query(db.Hit, db.Player.rplayer_id, sq.sql.func.count(
        '*').label('saves')).filter(db.Hit.save > 0).join(db.Player).group_by(db.Player.rplayer_id).subquery()
    count_fail_save = session.query(db.Hit, db.Player.rplayer_id, sq.sql.func.count(
        '*').label('failed_saves')).filter(db.Hit.save == -1).join(db.Player).group_by(db.Player.rplayer_id).subquery()

    ave_hit_dist = session.query(db.Hit, db.Player.rplayer_id, sq.sql.func.avg(db.Hit.distance).label(
        'hitdist')).filter(db.Hit.distance > 750).join(db.Player).group_by(db.Player.rplayer_id).subquery()
    count_50 = session.query(db.Hit, db.Player.rplayer_id, sq.sql.func.count(
        '*').label('_50s')).filter(db.Hit.distance < 500).join(db.Player).group_by(db.Player.rplayer_id).subquery()
    ave_shot_distance = session.query(db.Hit, db.Player.rplayer_id, sq.sql.func.avg(db.Hit.distance).label('shotdist')).filter(
        db.Hit.shot > 0).filter(db.Hit.distance > 750).join(db.Player).group_by(db.Player.rplayer_id).subquery()
    ave_shot_ot_distance = session.query(db.Hit, db.Player.rplayer_id, sq.sql.func.avg(db.Hit.distance).label('shot_otdist')).filter(
        db.Hit.shot == 2).filter(db.Hit.distance > 750).join(db.Player).group_by(db.Player.rplayer_id).subquery()

    count_block_shot = session.query(db.Hit, db.Player.rplayer_id, sq.sql.func.count('*').label('blocked_shots')).filter(
        db.Hit.shot > 0).filter(db.Hit.distance < 300).join(db.Player).group_by(db.Player.rplayer_id).subquery()

    print('hi')

    x = session.query(db.RPlayer.name, db.RPlayer.id, db.RTeam.name, count.c.replay_count, count_hits.c.hits, count_pass.c.passes, count_assist.c.assists, count_dribble.c.dribbles, count_shot.c.shots, count_shot_ot.c.shots_ot, count_goal.c.goals, count_assisted_goal.c.assisted_goals, count_save.c.saves, count_fail_save.c.failed_saves, ave_hit_dist.c.hitdist, count_50.c._50s, ave_shot_distance.c.shotdist, ave_shot_ot_distance.c.shot_otdist, count_block_shot.c.blocked_shots)\
        .join(db.RTeam)\
        .outerjoin(count, db.RPlayer.id == count.c.rplayer_id)\
        .outerjoin(count_hits, db.RPlayer.id == count_hits.c.rplayer_id)\
        .outerjoin(count_pass, db.RPlayer.id == count_pass.c.rplayer_id)\
        .outerjoin(count_assist, db.RPlayer.id == count_assist.c.rplayer_id)\
        .outerjoin(count_shot, db.RPlayer.id == count_shot.c.rplayer_id)\
        .outerjoin(count_shot_ot, db.RPlayer.id == count_shot_ot.c.rplayer_id)\
        .outerjoin(count_goal, db.RPlayer.id == count_goal.c.rplayer_id)\
        .outerjoin(count_assisted_goal, db.RPlayer.id == count_assisted_goal.c.rplayer_id)\
        .outerjoin(count_dribble, db.RPlayer.id == count_dribble.c.rplayer_id)\
        .outerjoin(count_save, db.RPlayer.id == count_save.c.rplayer_id)\
        .outerjoin(count_fail_save, db.RPlayer.id == count_fail_save.c.rplayer_id)\
        .outerjoin(ave_hit_dist, db.RPlayer.id == ave_hit_dist.c.rplayer_id)\
        .outerjoin(count_50, db.RPlayer.id == count_50.c.rplayer_id)\
        .outerjoin(ave_shot_distance, db.RPlayer.id == ave_shot_distance.c.rplayer_id)\
        .outerjoin(ave_shot_ot_distance, db.RPlayer.id == ave_shot_ot_distance.c.rplayer_id)\
        .outerjoin(count_block_shot, db.RPlayer.id == count_block_shot.c.rplayer_id)\
        .order_by(db.RPlayer.rteam_id)

    replay = pd.read_sql_query(
        x.selectable,
        db.engine,
        index_col='rplayers_id',
    )

    replay.columns = replay.columns.str.replace('^anon_[0-9]+_', '')

    velocities = pd.read_sql_query(session.query(db.Hit, db.RPlayer.id).join(db.Player).join(db.RPlayer).selectable,
                                   db.engine
                                   )

    # print(velocities[:5])
    magic_vel = 0.0043527
    velocities['speed'] = ((velocities['hits_vx'] * magic_vel)**2 + (velocities[
                           'hits_vy'] * magic_vel)**2 + (velocities['hits_vz'] * magic_vel)**2)**0.5

    hitvel = velocities.groupby('rplayers_id')['speed'].mean()
    shotvel = velocities[velocities.hits_shot > 0].groupby('rplayers_id')[
        'speed'].mean()
    # print(hitvel)

    replay['hitvel'] = hitvel
    replay['shotvel'] = shotvel

    # print(velocities)
    # return

    with open("all_player_hit_analysis.txt", 'w') as f:
        replay.to_csv(f, index=False)

    print('done')


def analyse_all_positions():
    session = db.Session()

    gameFrames = {}  # replayid:[(start,end),..]
    replays = session.query(db.Replay).all()
    for replay in replays:
        frames = get_game_frames(replay)
        gameFrames[replay.id] = frames

    # print(gameFrames)

    # count = session.query(db.Player.rplayer_id, sq.sql.func.count('*').label('replay_count')).group_by(db.Player.rplayer_id).subquery()

    # count_positions = session.query(db.Position, db.Player.rplayer_id, sq.sql.func.count('*').label('positions')).join(db.Player).group_by(db.Player.rplayer_id).subquery()
    # count_game_positions = session.query(db.Position, db.Player.rplayer_id, sq.sql.func.count('*').label('game_positions')).join(db.Player).filter(sq.or_(sq.and_(sq.or_(db.Position.frameNo.between(frames[0],frames[1]) for frames in gameFrames[replayid]),db.Position.replay_id==replayid) for replayid in gameFrames)).group_by(db.Player.rplayer_id).subquery()
    # count_half_attacking = session.query(db.Position, db.Player.rplayer_id, sq.sql.func.count('*').label('attacking_half')).join(db.Player).filter(db.Position.y>0).group_by(db.Player.rplayer_id).subquery()
    # count_half_defending = session.query(db.Position, db.Player.rplayer_id, sq.sql.func.count('*').label('defending_half')).join(db.Player).filter(db.Position.y<0).group_by(db.Player.rplayer_id).subquery()

    print('hi')

    a = time.time()
    rplayers = session.query(db.RPlayer).all()
    # i=0
    for rplayer in tqdm.tqdm(rplayers, leave=True):
        # i += 1
        # if i>2: break
        rpid = rplayer.id
        # print('\n',rid)
        pids, rids = zip(*session.query(db.Player.id,
                                        db.Player.replay_id).filter(db.Player.rplayer_id == rpid).all())
        print(pids, rids)

        _gameFrames = {}
        for rid in rids:
            _gameFrames[rid] = gameFrames[rid]

        # limit to 5 games
        _temp_gameFrames = {}
        i = 0
        for rid in rids:
            if i > 5:
                break
            _temp_gameFrames[rid] = gameFrames[rid]
            i += 1

        print(_temp_gameFrames)
        p = session.query(
            db.Position,
            db.BallFrame.x,
            db.BallFrame.y,
            db.BallFrame.z,
            db.Team.colour,
            # db.Velocity.speed
        )\
            .filter(db.Position.player_id.in_(pids))\
            .filter(sq.or_(sq.and_(sq.or_(db.Position.frameNo.between(frames[0], frames[1]) for frames in _temp_gameFrames[replayid]), db.Position.replay_id == replayid) for replayid in _temp_gameFrames))\
            .join(db.Player).join(db.Team)\
            .join(db.BallFrame, db.BallFrame.frame_id == db.Position.frame_id)\
            # .join(db.Velocity, sq.and_(db.Position.frame_id==db.Velocity.frame_id,db.Position.player_id==db.Velocity.player_id))\

        # velocity join takes a long time.
        # TESTING ABOVE
        # p = session.query(
        #     db.Position,
        #     db.BallFrame.x,
        #     db.BallFrame.y,
        #     db.BallFrame.z,
        #     db.Team.colour,
        #     db.Velocity.speed
        # )\
        #     .filter(db.Position.player_id.in_(pids))\
        #     .filter(sq.or_(sq.and_(sq.or_(db.Position.frameNo.between(frames[0],frames[1]) for frames in _gameFrames[replayid]),db.Position.replay_id==replayid) for replayid in _gameFrames))\
        #     .join(db.Velocity, sq.and_(db.Position.frame_id==db.Velocity.frame_id,db.Position.player_id==db.Velocity.player_id))\
        #     .join(db.Player).join(db.Team)\
        #     .join(db.BallFrame,db.BallFrame.frame_id==db.Position.frame_id)\

        # END REAL PART

        # p = session.query(db.Position,db.BallFrame.x,db.BallFrame.y,db.BallFrame.z,db.Team.colour)\
        # .filter(db.Position.player_id.in_(pids))\
        # .filter(sq.or_(sq.and_(sq.or_(db.Position.frameNo.between(frames[0],frames[1]) for frames in _gameFrames[replayid]),db.Position.replay_id==replayid) for replayid in _gameFrames))\
        # .join(db.Player).join(db.Team)\
        # .join(db.BallFrame,db.BallFrame.frame_id==db.Position.frame_id)\

        positions = pd.read_sql_query(
            p.selectable,
            db.engine
        )
        # print(positions.columns.values)
        # print('\n\n\n')
        # print(positions[:5])
        # print('\n\n\n')
        # print(positions.describe())

        print(positions, "!!!!!!!")
        _positions1 = analyse_position(positions)
        _positions2 = analyse_position_velocity(positions)

        # _positions = {**(_positions1), **_positions2}
        _positions = OrderedDict()
        for key, value in _positions1.items():
            _positions[key] = value
        for key, value in _positions2.items():
            _positions[key] = value
        # print(_positions)

        try:
            for key, value in _positions.items():
                positional_analysis[key].append(value)
            positional_analysis['name'].append(rplayer.name)
            positional_analysis['team'].append(rplayer.rteam.name)
            positional_analysis['games'].append(len(pids))
        except UnboundLocalError:
            positional_analysis = OrderedDict()
            positional_analysis['name'] = [rplayer.name]
            positional_analysis['team'] = [rplayer.rteam.name]
            positional_analysis['games'] = [len(pids)]
            for key, value in _positions.items():
                positional_analysis[key] = [value]

        # print(positional_analysis)

    positional_analysis = pd.DataFrame.from_dict(positional_analysis)

    # print(positional_analysis)

    # replay = pd.read_sql_query(
    # x.selectable,
    # db.engine
    # )

    # replay.columns = replay.columns.str.replace('^anon_[0-9]+_','')

    print('duration:', int(time.time() - a))
    with open("all_player_position_analysis1.txt", 'w') as f:
        positional_analysis.to_csv(f, index=False)

    print('done')


def analyse_position(_positions):

    position = (
        ('half0', 0),
        ('half1', 0),
        ('third-1', 0),
        ('third0', 0),
        ('third1', 0),
        ('height0', 0),
        ('height1', 0),
        ('height2', 0),
        ('ball0', 0),
        ('ball1', 0),
        ('total', 0),
    )

    # print(_positions[:5])
    # todo: check for special maps
    # print(_positions.columns.values)
    # print(pd.unique(positions.replays_map.ravel()))
    position = OrderedDict(position)

    _positions.ix[_positions.teams_colour == 'orange', 'positions_y'] = _positions.ix[
        _positions.teams_colour == 'orange', 'positions_y'] * -1

    # half
    # a = time.time()
    hp = _positions['positions_y'][_positions['positions_y'] > 0].count()
    hn = _positions['positions_y'][_positions['positions_y'] <= 0].count()
    # print('half:',hp,hn)
    position['half1'] += hp
    position['half0'] += hn

    # third
    tp = _positions['positions_y'][_positions['positions_y'] >= 3400].count()
    tm = _positions['positions_y'][
        (_positions['positions_y'] > -3400) & (_positions['positions_y'] < 3400)].count()
    tn = _positions['positions_y'][_positions['positions_y'] <= -3400].count()
    # print('third:',tp,tm,tn)
    position['third1'] += tp
    position['third0'] += tm
    position['third-1'] += tn

    # height
    ht0 = _positions['positions_z'][_positions['positions_z'] < 25].count()
    ht1 = _positions['positions_z'][(_positions['positions_z'] >= 25) & (
        _positions['positions_z'] <= 840)].count()
    ht2 = _positions['positions_z'][_positions['positions_z'] > 840].count()
    # print('height:',ht0,ht1,ht2)
    position['height0'] += ht0
    position['height1'] += ht1
    position['height2'] += ht2

    if 'ballframes_y' in _positions.columns.values:
        # ball
        # print(_positions.head())
        bp = _positions['positions_y'][_positions[
            'positions_y'] >= _positions['ballframes_y']].count()
        bn = _positions['positions_y'][_positions[
            'positions_y'] < _positions['ballframes_y']].count()
        # print('ball:',bp,bn)
        position['ball1'] += bp
        position['ball0'] += bn

    position['total'] += _positions['teams_colour'].count()

    average = _positions[['positions_x', 'positions_y',
                          'positions_z']].mean(numeric_only=True)
    std = _positions[['positions_x', 'positions_y', 'positions_z']].std()
    position_average = average.values.tolist()
    print(position_average)
    print(average)
    print(_positions)
    print(_positions[['positions_x', 'positions_y', 'positions_z']])
    position['averagex'] = position_average[0]
    position['averagey'] = position_average[1]
    position['averagez'] = position_average[2]
    # position['averageV'] = std.values.tolist()

    # print(_positions[['positions_x','positions_y','positions_z']].skew())
    # print(_positions[['positions_x','positions_y','positions_z']].kurt())

    # print('Average:\n',average)

    # print(position)

    return position


def analyse_position_velocity(_positions):
    position = OrderedDict()
    magic_vel = 0.0043527

    position['averagevel'] = _positions['velocities_speed'].mean() * magic_vel
    position['averagevel_half0'] = _positions[_positions[
        'positions_y'] < 0]['velocities_speed'].mean() * magic_vel
    position['averagevel_half1'] = _positions[_positions[
        'positions_y'] > 0]['velocities_speed'].mean() * magic_vel

    position['averagevel_third1'] = _positions[_positions[
        'positions_y'] >= 3400]['velocities_speed'].mean() * magic_vel
    position['averagevel_third0'] = _positions[(_positions['positions_y'] > -3400) & (
        _positions['positions_y'] < 3400)]['velocities_speed'].mean() * magic_vel
    position['averagevel_third-1'] = _positions[_positions['positions_y']
                                                <= -3400]['velocities_speed'].mean() * magic_vel

    position['averagevel_height0'] = _positions[_positions[
        'positions_z'] < 25]['velocities_speed'].mean() * magic_vel
    position['averagevel_height1'] = _positions[(_positions['positions_z'] >= 25) & (
        _positions['positions_z'] <= 840)]['velocities_speed'].mean() * magic_vel
    position['averagevel_height2'] = _positions[_positions[
        'positions_z'] > 840]['velocities_speed'].mean() * magic_vel

    if 'ballframes_y' in _positions.columns.values:
        position['averagevel_ball0'] = _positions[_positions['positions_y']
                                                  < _positions['ballframes_y']]['velocities_speed'].mean() * magic_vel
        position['averagevel_ball1'] = _positions[_positions['positions_y'] >=
                                                  _positions['ballframes_y']]['velocities_speed'].mean() * magic_vel

    return position


def get_game_frames(game):
    frames = []

    noOfGoals = len(game.goals)
    goalsToPlot = list(range(noOfGoals))

    # add all frames for goals in goalsToPlot
    for goal in goalsToPlot:
        frames.append(
            (game.goals[goal].firstHitFrame, game.goals[goal].frameNo))
        # print(frames)

    return frames
