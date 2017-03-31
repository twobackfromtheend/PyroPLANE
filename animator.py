from pickle import load
import matplotlib.pyplot as plt
from matplotlib import gridspec
import matplotlib.animation as animation
from matplotlib.widgets import Slider
import math as m
import time
import numpy as np
from random import randrange
import pyroplane.anal.hit as h
import pyroplane.database.database as db

# import threed

# with open('0A7FA6BF473E7267C9246F8FF54A02B8.pysickle','rb') as f:
# replay = load(f)
# replay.hits = h.Hit.add_all_hits(replay)
# h.Hit.get_firstHit(replay)


class _Replay:

    def __init__(self, gameid):
        session = db.Session()
        replay = session.query(db.Replay).filter(
            db.Replay.id == gameid).all()[0]
        self.name = replay.name
        self.map = replay.map
        self.maxFrameNo = replay.maxFrameNo
        self.teams = []
        self.players = []
        for _team in replay.teams:
            team = {'players': [], 'colour': _team.colour}
            self.teams.append(team)
            for _player in _team.players:
                player = {
                    'positions': {position.frameNo: (position.x, position.y, position.z) for position in _player.positions},
                    'rotations': {rotation.frameNo: (rotation.pitch, rotation.yaw, rotation.roll) for rotation in _player.positions},
                    'name': _player.name,
                }
                team['players'].append(player)
                self.players.append(player)
                print(player['name'])

        # self.ball = {'positions': {position.frameNo:(position.x,position.y,position.z) for position in replay.ball.ballframes}}
        self.ball = {'positions': [
            (position.x, position.y, position.z) for position in replay.ball.ballframes]}
        self.ball['positions'] = np.array(self.ball['positions'])
        print(type(self.ball))
        hits = session.query(db.Hit, db.RPlayer.name).filter(
            db.Hit.replay_id == gameid).join(db.Player).join(db.RPlayer).all()
        self.hits = []
        for _hit in hits:
            hit = _hit[0].__dict__
            hit['player'] = _hit[1]
            self.hits.append(hit)

        frames = session.query(db.Frame).filter(
            db.Frame.replay_id == gameid).all()
        # print(frames)
        self.frames = {}
        for frame in frames:
            self.frames[frame.frameNo] = {
                'timeRemaining': frame.timeRemaining,
                'isOvertime': frame.isOvertime
            }
        # print(self.frames.keys())


class ReplayMap:

    def new_replay(root):
        (gameids, _, __) = root.dataPicker.get_data_options()
        replay = _Replay(gameids[0])
        print('done')
        # print(replay.teams[0].keys())
        # print(replay.teams[0].players.keys())
        ReplayMap(replay)

    def __init__(self, replay):
        self.frameNo = 0
        # print(replay.players)

        fig = plt.figure(figsize=(8, 10))
        gs = gridspec.GridSpec(3, 3, height_ratios=[20, 1, 1])
        map = plt.subplot(gs[0, :], facecolor='lightgrey', aspect='equal')
        # map = fig.add_subplot(311,axisbg='white',aspect='equal')
        map.set_title(replay.name)

        map.set_xlim([-4200, 4200])
        map.set_ylim([-5200, 5200])
        # map.axis('equal')
        map.axes.get_xaxis().set_ticks([])
        map.axes.get_yaxis().set_ticks([])
        # map.set_axis_off()

        self.quivers = []
        self.names = []
        frameNo = self.frameNo
        for team in replay.teams:
            colour = team['colour']
            for player in team['players']:
                yaw = player['rotations'][frameNo][1]
                try:
                    x = m.cos(m.pi * -yaw)
                    y = m.sin(m.pi * -yaw)
                except TypeError:
                    x = 0
                    y = 1
                position = player['positions'][frameNo]
                if position[2] is None:
                    position = [100000, 100000]

                playerColour = ReplayMap.create_player_colour(colour)
                quiver = map.quiver(position[0], position[
                                    1], x, y, color=playerColour, scale=30, width=0.015, headlength=0.5, headwidth=1, pivot='mid')
                self.quivers.append(quiver)
                self.names.append(player['name'])

        ballPosition = replay.ball['positions'][frameNo]
        self.ball = plt.scatter(ballPosition[0], ballPosition[1])

        text = ""
        self.timeRemaining = plt.text(-4000, -5000, text)
        self.isOvertime = plt.text(4000, -5000, text, color='red')
        self.hitCheck = plt.text(0, -5000, text, ha='center')
        self.hitType = plt.text(0, -4500, text, ha='center')
        self.hits = {}
        for hit in replay.hits:
            self.hits[hit['frameNo']] = hit

        axFrame = plt.subplot(gs[1, 1])
        axSpeed = plt.subplot(gs[2, 1])
        # axFrame = plt.axes([0.25, 0.1, 0.65, 0.03])
        # axSpeed = plt.axes([0.25, 0.15, 0.65, 0.03])
        self.sFrame = Slider(axFrame, 'Frame Number', 0,
                             replay.maxFrameNo, valinit=0)
        self.sSpeed = Slider(axSpeed, 'FPS', 0, 500, valinit=100)
        self.sFrame.on_changed(self.update_slider)
        self.sSpeed.on_changed(self.update_slider)

        self.FPS = 100
        self.buffer = 0
        self.isPaused = False

        map.legend(self.quivers, self.names, fontsize=8,
                   fancybox=True, framealpha=0.4)

        # self.i = 0
        # self.start = time.time()
        anim = animation.FuncAnimation(fig, self.update_plot, fargs=(
            replay,), interval=50, blit=False, repeat=True)

        self.fig = fig
        self.map = map
        plt.tight_layout()
        fig.show()

    def update_plot(plot, _, replay):
        # print(_)
        # print(plot.i)
        # if plot.i == 100:
            # print(time.time()-plot.start)
        # plot.i += 1
        startFrame = plot.frameNo

        if plot.isPaused == True:
            return

        maxBuffer = 50
        if plot.buffer < maxBuffer:
            plot.buffer += plot.FPS
            return
        else:
            plot.buffer = 0
            if plot.FPS / maxBuffer > 1:
                plot.frameNo += plot.FPS / maxBuffer
            else:
                plot.frameNo += 1
        if plot.frameNo >= replay.maxFrameNo:
            plot.frameNo = 0
            plot.isPaused = True
            return

        frameNo = int(plot.frameNo)
        # print(frameNo)
        i = 0
        for team in replay.teams:
            for player in team['players']:
                quiver = plot.quivers[i]
                try:
                    yaw = player['rotations'][frameNo][1]
                    x = m.cos(m.pi * -yaw)
                    y = m.sin(m.pi * -yaw)
                    quiver.set_UVC(x, y)
                except KeyError:
                    pass
                except TypeError:
                    pass

                try:
                    position = player['positions'][frameNo]
                    quiver.set_offsets([position[0], position[1]])
                except KeyError:
                    pass

                i += 1

        ballPosition = replay.ball['positions'][frameNo]
        plot.ball.set_offsets([ballPosition[0], ballPosition[1]])

        for frameNo in range(startFrame, frameNo + 1):
            if frameNo in plot.hits:
                hit = plot.hits[frameNo]
                # print(hit)
                plot.hitCheck.set_text(hit['player'])
                hitType = ''
                # print(hit)
                if hit['goal']:
                    hitType += 'Goal, '
                if hit['save'] > 0:
                    hitType += 'Save, '
                if hit['pass_'] == 1:
                    hitType += 'Pass, '
                elif hit['pass_'] == 2:
                    hitType += 'Assist, '
                if hit['dribble']:
                    hitType += 'Dribble, '
                if hit['shot'] == 1:
                    hitType += 'Shot, '
                elif hit['shot'] == 2:
                    hitType += 'Shot on Target, '
                plot.hitType.set_text(hitType.rstrip(', '))

        plot.timeRemaining.set_text(replay.frames[frameNo]['timeRemaining'])
        if replay.frames[frameNo]['isOvertime']:
            plot.isOvertime.set_text('OVERTIME')
        # print(plot.timeRemaining)
        plot.sFrame.set_val(plot.frameNo)

        return

    def create_player_colour(teamColour):
        if teamColour == 'orange':
            playerColour = [
                255 - randrange(80), 153 + randrange(-100, 101, 50), randrange(80)]
        elif teamColour == 'blue':
            playerColour = [
                74 + randrange(-50, 111, 40), 134 + randrange(-100, 101, 50), 232 + randrange(-100, 21, 30)]
        else:
            print('Unknown team colour: ' + str(teamColour))
            return None
        for i in range(len(playerColour)):
            playerColour[i] = playerColour[i] / 255
        # print(playerColour)
        return playerColour

    def update_slider(self, val):
        speed = self.sSpeed.val
        frameNo = int(self.sFrame.val)
        self.frameNo = frameNo
        self.FPS = speed


# replay = _Replay(1)
# ReplayMap(replay)
