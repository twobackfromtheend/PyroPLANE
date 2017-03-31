import pyroplane.misc as misc
import tkinter.filedialog
import math
import time
import tqdm
import pandas as pd
import numpy as np
import sqlalchemy as sq
from pyroplane.anal import hit
import pyroplane.database.database as db


import matplotlib.pyplot as plt
from matplotlib import cm, colors
from mpl_toolkits.mplot3d import Axes3D


class GamePlotter:
    allPlots = []  # removed addition to save memory

    x_range = [-4200, 4200]
    y_range = [-5200, 5200]
    z_range = [0, 3000]

    x_step = 800
    y_step = 800
    z_step = 400

    colormap = cm.gist_heat

    pointSizeFactor = 1
    normaliseMaxSize = 75

    def __init__(self, parent, dataOptions, typeOptions):
        self.parent = parent
        # data accepting
        (gameids, rteamids, rplayerids) = dataOptions
        for x in typeOptions[0]:
            self.plotBy = x
            self.plotByData = typeOptions[0][x]

        self.plotOvertime, self.plotHeat, self.normaliseHeat, self.plotLine, self.plotBall = typeOptions[
            1]

        # player/team._name:data
        subPlotRows = 1
        subPlotColumns = 1
        subPlotNumber = 1

        session = db.Session()
        if rplayerids:
            # if there are players selected
            noOfPlots = len(rplayerids)
            subPlotRows = math.floor(math.sqrt(noOfPlots))
            subPlotColumns = math.ceil(noOfPlots / subPlotRows)
            print('Plotting a %sx%s grid.' % (subPlotColumns, subPlotRows))

            fig = plt.figure(figsize=(subPlotColumns * 4, subPlotRows * 4))
            fig.subplots_adjust(bottom=0.05, top=0.95, left=0.02, right=0.98)

            # plot players separately
            for rplayerid in rplayerids:
                (playerName,) = session.query(db.RPlayer.name).filter(
                    db.RPlayer.id == rplayerid).one()
                print('Plot %s - %s' % (subPlotNumber, playerName))
                ax = fig.add_subplot(
                    subPlotRows, subPlotColumns, subPlotNumber, projection='3d', facecolor='black')
                ax.set_title(playerName, color='w')
                subPlotNumber += 1

                positionsToPlot = []

                # find players
                playerIDs = session.query(db.Player.id).join(db.RPlayer).join(db.Replay).filter(
                    db.RPlayer.id == rplayerid).filter(db.Replay.id.in_(gameids)).all()
                playerIDs = list(x for (x,) in playerIDs)
                print('Found %s games for %s.' % (len(playerIDs), playerName))

                startTime = time.time()
                # print(playerIDs)
                gameFrames = {}  # replayid:[(start,end),..]
                for playerID in playerIDs:
                    player = session.query(db.Player).filter(
                        db.Player.id == playerID).one()
                    frames = misc.get_game_frames(self, player.replay)
                    gameFrames[player.replay.id] = frames

                x = session.query(db.Position, db.Replay.map, db.Team.colour)\
                    .filter(db.Position.player_id.in_(playerIDs))\
                    .filter(sq.or_(sq.and_(sq.or_(db.Position.frameNo.between(frames[0], frames[1]) for frames in gameFrames[replayid]), db.Position.replay_id == replayid) for replayid in gameFrames))\
                    .join(db.Replay)\
                    .join(db.Player)\
                    .filter(db.Player.id.in_(playerIDs))\
                    .join(db.Team)

                positions = pd.read_sql_query(
                    x.selectable,
                    db.engine
                )
                positions.ix[positions.teams_colour == 'orange', 'positions_y'] = positions.ix[
                    positions.teams_colour == 'orange', 'positions_y'] * -1

                # print(positions[:5])

                positionsToPlot = positions.ix[
                    :, ['positions_x', 'positions_y', 'positions_z']].values.tolist()

                duration = '{:.2}'.format(time.time() - startTime)
                print('Got', len(positionsToPlot), 'frames in', duration, 's')
                self.create_axes(ax)
                if self.plotLine:
                    self.plot_line(ax, positionsToPlot)
                if self.plotHeat:
                    self.plot_heat(ax, positionsToPlot)

            plt.show()

        elif rteamids:
            noOfPlots = len(rteamids)
            subPlotRows = math.floor(math.sqrt(noOfPlots))
            subPlotColumns = math.ceil(noOfPlots / subPlotRows)
            print('Plotting a %sx%s grid.' % (subPlotColumns, subPlotRows))

            fig = plt.figure(figsize=(subPlotColumns * 4, subPlotRows * 4))

            # plot teams separately
            for rteamid in rteamids:
                (teamName,) = session.query(db.RTeam.name).filter(
                    db.RTeam.id == rteamid).one()
                print('Plot %s - %s.' % (subPlotNumber, teamName))
                ax = fig.add_subplot(
                    subPlotRows, subPlotColumns, subPlotNumber, projection='3d', facecolor='black')
                ax.set_title(teamName, color='w')

                subPlotNumber += 1

                positionsToPlot = []

                # find teams
                teams = session.query(db.Team).join(db.RTeam).join(db.Replay).filter(
                    db.RTeam.id == rteamid).filter(db.Replay.id.in_(gameids)).all()
                print('Found %s games for %s.' % (len(teams), teamName))

                startTime = time.time()

                for team in teams:
                    replay = team.replay
                    frames = misc.get_game_frames(self, replay)
                    # print(frames)
                    for player in team.players:
                        positions = db.Position.get_positions(player, frames)
                        if team.colour == 'orange':
                            for position in positions:
                                positionsToPlot.append(
                                    [position.x, -position.y, position.z])
                        elif team.colour == 'blue':
                            for position in player.positions:
                                positionsToPlot.append(
                                    [position.x, position.y, position.z])

                duration = '{:.2}'.format(time.time() - startTime)
                print('Got %s frames in %ss.' %
                      (len(positionsToPlot), duration))
                self.create_axes(ax)
                if self.plotLine:
                    self.plot_line(ax, positionsToPlot)
                if self.plotHeat:
                    self.plot_heat(ax, positionsToPlot)

            # GamePlotter.allPlots.append(plt)
            plt.show()

    @classmethod
    def create_axes(cls, ax):
        # ax = plt.Axes(fig)
        # ax = fig.gca(projection = '3d')
        ax.autoscale_view('tight')

        cls.plot_stadium(ax)
        ax.set_xlim3d(cls.x_range)
        ax.set_ylim3d(cls.y_range)
        ax.set_zlim3d(cls.z_range)
        ax.axis('equal')
        ax.set_axis_off()

        return ax

    @classmethod
    def normalise(cls, listData):
        print('Normalising heatmap.')
        maxSize = cls.normaliseMaxSize
        listCount = len(listData)
        listData = np.array(listData)
        listData = listData**0.5
        # for i in range(len(listData)):
        #     listData[i] = math.sqrt(listData[i])
        #     # listData[i] = math.log2(listData[i])

        maxi = listCount * 0.01 / maxSize
        # maxi = max(listData)/maxSize
        norm = listData / float(maxi)
        # norm = list([float(i) / maxi] for i in listData)
        return norm

    def remove_nones(pos_x, pos_y, pos_z):
        i = 0
        pos_x = list(pos_x)
        pos_y = list(pos_y)
        pos_z = list(pos_z)
        while i < len(pos_x):
            if pos_x[i] is None:
                # print(x)
                # print(x[i],y[i],z[i])
                pos_x.pop(i)
                pos_y.pop(i)
                pos_z.pop(i)
            else:
                i += 1
        return(pos_x, pos_y, pos_z)

    def plot_heat(self, ax, positions):
        (pos_x, pos_y, pos_z, point_size) = self.get_heatmap(positions)
        if self.normaliseHeat:
            point_size = self.normalise(point_size)

        # adds alpha
        cmap = self.__class__.colormap
        _cmap = cmap(np.arange(cmap.N))
        _cmap[:, -1] = np.linspace(0.3, 1, cmap.N)
        _cmap = colors.ListedColormap(_cmap)

        heat = ax.scatter(
            pos_x,
            pos_y,
            pos_z,
            s=point_size,
            marker='o',
            c=point_size,
            cmap=_cmap,
            edgecolor='none',
        )


    @classmethod
    def get_heatmap(cls, positions):
        i = 0
        while i < len(positions):
            if positions[i][0] is None:
                positions.pop(i)
            else:
                i += 1

        a = {}  # position:value
        for position in positions:
            plotx = position[0] // cls.x_step * cls.x_step + 0.5 * cls.x_step
            ploty = position[1] // cls.y_step * cls.y_step + 0.5 * cls.y_step
            plotz = position[2] // cls.z_step * cls.z_step + 0.5 * cls.z_step

            try:
                a[(plotx, ploty, plotz)] += 1
            except KeyError:
                a[(plotx, ploty, plotz)] = 1

        pos_x = []
        pos_y = []
        pos_z = []

        point_size = []

        for point in a:
            pos_x.append(point[0])
            pos_y.append(point[1])
            pos_z.append(point[2])
            point_size.append((a[point]) * (cls.pointSizeFactor**2))

        return (pos_x, pos_y, pos_z, point_size)

    @staticmethod
    def plot_line(ax, positions):
        pos_x, pos_y, pos_z = zip(*positions)
        pos_x, pos_y, pos_z = GamePlotter.remove_nones(pos_x, pos_y, pos_z)

        line = ax.plot(pos_x, pos_y, pos_z, '-')
        markers = ax.plot(pos_x, pos_y, pos_z, '.', markersize=0.2)


        positions = []
        velocities = []
        lengths = []
        for hit in game.hits:
            if (hit.player == game.players[number]) and (startFrame <= hit.frameNo <= endFrame):
                positions.append(hit.position)
                if hit.velocity:
                    velocities.append(hit.velocity)
                    length = (
                        hit.velocity[0]**2 + hit.velocity[1]**2 + hit.velocity[2]**2)**0.5
                    print(hit.velocity)
                else:
                    velocities.append((0, 0, -1))
                    length = 500000

                lengths.append(length / 30)
        print(lengths)

        pos_x, pos_y, pos_z = zip(*positions)
        u, v, w = zip(*velocities)

        cmap = cm.viridis
        norm = colors.Normalize(vmin=0, vmax=max(lengths))

        for x in range(len(positions)):
            hit = ax.quiver(
                pos_x[x],
                pos_y[x],
                pos_z[x],
                u[x],
                v[x],
                w[x],
                length=lengths[x],
                colors=cmap(norm(lengths[x])),
                pivot='tail')

    @classmethod
    def plot_stadium(cls, ax):
        positions = []
        for z in cls.z_range:
            for y in cls.y_range:
                for x in cls.x_range:
                    positions.append((x, y, z))

        pos_x, pos_y, pos_z = zip(*positions)

        stadium = ax.scatter(
            pos_x,
            pos_y,
            pos_z,
            s=1,
            marker='o',)

    def plot_stuff():
        # create figure
        fig = plt.figure()
        # create 3d axis
        ax = plt.Axes(fig, [0., 0., 1., 1.])
        ax = fig.gca(projection='3d')

        players_to_plot = []
        data = []

        g = input('Split by goal(s)? ')
        if g:
            g_ = list(int(x) - 1 for x in input('Choose goals to add (1 to ' +
                                                str(len(game.goals)) + '):').split())

            for goalNo in g_:
                if (goalNo >= len(game.goals)) or (goalNo < 0):
                    print('Selected invalid goal')
                    return

        for number in players_to_plot:
            if input('Plot heatmap? '):
                if g:
                    for goalNo in g_:
                        startFrame = game.goals[goalNo].firstHit
                        endFrame = game.goals[goalNo].frameNo
                        plot_heat(ax, number, startFrame, endFrame)
                else:
                    plot_heat(ax, number)

            if input('Plot line? '):
                if g:
                    for goalNo in g_:
                        startFrame = game.goals[goalNo].firstHit
                        endFrame = game.goals[goalNo].frameNo
                        plot_line(ax, number, startFrame, endFrame)
                else:
                    plot_line(ax, number)

            if input('Plot hits? '):
                if g:
                    for goalNo in g_:
                        startFrame = game.goals[goalNo].firstHit
                        endFrame = game.goals[goalNo].frameNo
                        plot_hits(ax, number, startFrame, endFrame)
                else:
                    plot_hits(ax, number)

        plot_stadium(ax)
        ax.set_xlim3d(x_range)
        ax.set_ylim3d(y_range)
        ax.set_zlim3d(z_range)
        ax.axis('equal')
        # ax.set_aspect('0.5')

        # ax.xaxis.set_ticks([])
        # ax.yaxis.set_ticks([])
        # ax.zaxis.set_ticks([])
        ax.set_axis_off()
        plt.show()

        plot_stuff()

        while input('Plot another? '):
            plot_stuff()
