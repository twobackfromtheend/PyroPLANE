import os
import sys
import hashlib
import time
import tqdm
import tkinter as tk
from tkinter import ttk
import pyroplane.tooltip as tooltip
import pyroplane.database.database as db


class DataPicker:
        # parse games in filelist

    def __init__(self, parent):
        parent.dataPicker = self
        self.parent = parent

        # import starting files
        filePaths = self.import_starting_files(parent)
        self.allGameFileNames = []
        parent.status.set('Importing ' + str(len(filePaths)) + ' file(s).')

        # parse games in filelist
        self.allGameIDs = []
        self.curatedRTeamIDs = []
        self.curatedRPlayerIDs = []
        self.allGameNames = tk.Variable()

        # ADD DATA PICKER

        self.dataPicker = ttk.Panedwindow(
            parent.windowFrame, orient='horizontal')

        gamePicker = ttk.Labelframe(
            self.dataPicker, text='Game(s):', width=160, height=100)
        teamPicker = ttk.Labelframe(
            self.dataPicker, text='Team(s):', width=100, height=100)
        playerPicker = ttk.Labelframe(
            self.dataPicker, text='Player(s):', width=100, height=100)
        self.dataPicker.add(gamePicker, weight=16)
        self.dataPicker.add(teamPicker, weight=10)
        self.dataPicker.add(playerPicker, weight=10)
        self.dataPicker.grid(row=0, column=0, sticky='nesw')
        parent.windowFrame.grid_rowconfigure(0, weight=1, minsize=200)
        parent.windowFrame.grid_columnconfigure(0, weight=5, minsize=400)

        listBoxRelief = 'flat'

        # game picker
        gameButtonText = tk.StringVar()
        gameButtonText.set('Select All')
        self.gameBox = tk.Listbox(
            gamePicker,
            width=35,
            height=10,
            listvariable=self.allGameNames,
            selectmode='extended',
            activestyle='dotbox',
            relief=listBoxRelief,
            exportselection=False)
        self.gameBox.bind('<<ListboxSelect>>', self.update_team_names)
        self.gameBox.bind('<Motion>', self.gameMotion)
        self.gameBox.pack(fill='both', expand=True)

        gameSelectButton = ttk.Button(gamePicker, textvariable=gameButtonText,
                                      width=13, command=lambda: self.select_x(self.gameBox, gameButtonText))
        gameSelectButton.pack(pady=3)
        gamePicker.grid_columnconfigure(0, weight=1)

        # team picker
        teamButtonText = tk.StringVar()
        teamButtonText.set('Select All')

        self.curatedTeamNames = tk.Variable()
        self.teamBox = tk.Listbox(
            teamPicker,
            width=16,
            height=10,
            listvariable=self.curatedTeamNames,
            selectmode='extended',
            activestyle='dotbox',
            relief=listBoxRelief,
            exportselection=False)
        self.teamBox.bind('<<ListboxSelect>>', self.update_player_names)
        self.teamBox.pack(fill='both', expand=True)
        teamSelectButton = ttk.Button(teamPicker, textvariable=teamButtonText,
                                      width=13, command=lambda: self.select_x(self.teamBox, teamButtonText))
        teamSelectButton.pack(pady=3)
        teamPicker.grid_columnconfigure(0, weight=1)

        # player picker
        playerButtonText = tk.StringVar()
        playerButtonText.set('Select All')

        self.curatedPlayerNames = tk.Variable()
        self.playerBox = tk.Listbox(
            playerPicker,
            width=20,
            height=10,
            listvariable=self.curatedPlayerNames,
            selectmode='extended',
            activestyle='dotbox',
            relief=listBoxRelief,
            exportselection=False)
        self.playerBox.pack(fill='both', expand=True)
        playerSelectButton = ttk.Button(playerPicker, textvariable=playerButtonText,
                                        width=13, command=lambda: self.select_x(self.playerBox, playerButtonText))
        playerSelectButton.pack(pady=3)
        playerPicker.grid_columnconfigure(0, weight=1)

        # read starting database
        session = db.Session()
        replays = session.query(db.Replay.name, db.Replay.id).order_by(
            db.Replay.dateTime).all()
        db.Session.remove()
        for (replayName, replayID) in replays:
            self.gameBox.insert('end', replayName)
            self.allGameIDs.append(replayID)

        # finish importing starting files
        for gamePath in tqdm.tqdm(filePaths):
            match = self.parent.get_file_name(gamePath)
            if match:
                fileName = match.group(1)
                self.add_game(gamePath, fileName)

    def import_starting_files(self, parent):
        filePaths = sys.argv[1:]
        noOfInputFiles = len(filePaths)
        for filePath in filePaths:
            match = self.parent.get_file_name(filePath)
            if match:
                fileName = match.group(1)

            else:
                filePaths.remove(filePath)
        # import starting files
        self.allGameFileNames = []
        parent.status.set('Importing ' + str(len(filePaths)) + ' file(s).')
        # messagebox.showinfo(message='Importing '+ str(len(filePaths)) + ' file(s).')
        return filePaths

    def add_game(self, filePath, fileName):
        with open(os.path.join(self.parent.rootPath, 'teams.txt'), 'rb') as f:
            tmtxt = f.read()
        tmtxtmd5 = hashlib.md5(tmtxt).digest()
        if tmtxtmd5 != db.tmtxtmd5:
            print('Updating team names and player names.')
            db.TeamName.load_teams_txt(os.path.join(
                self.parent.rootPath, 'teams.txt'))
            db.tmtxtmd5 = tmtxtmd5

        replay = db.Replay.import_replay(filePath)

        if replay:
            self.gameBox.insert('end', replay.name)
            self.allGameIDs.append(replay.id)

            self.parent.status.set('Imported ' + fileName + '.')

        return replay

    def refresh_all_teamNames(root):
        with open(os.path.join(root.rootPath, 'teams.txt'), 'rb') as f:
            tmtxt = f.read()
        tmtxtmd5 = hashlib.md5(tmtxt).digest()
        if tmtxtmd5 != db.tmtxtmd5:
            print('Updating team names and player names.')
            db.TeamName.load_teams_txt(
                os.path.join(root.rootPath, 'teams.txt'))
            db.tmtxtmd5 = tmtxtmd5

        db.Replay.refresh_all_teamNames()

        session = db.Session()
        replays = session.query(db.Replay.name, db.Replay.id).order_by(
            db.Replay.dateTime).all()
        db.Session.remove()
        root.dataPicker.allGameNames.set(())
        root.dataPicker.allGameIDs = []
        for (replayName, replayID) in replays:
            root.dataPicker.gameBox.insert('end', replayName)
            root.dataPicker.allGameIDs.append(replayID)

    def update_team_names(self, *args):
        # startTime = time.time()
        gamesSelected = self.gameBox.curselection()
        session = db.Session()

        list_of_teams = ()
        rteamIDs = []
        for x in gamesSelected:
            gameID = self.allGameIDs[x]
            rteams = session.query(db.RTeam).join(
                db.Replay.rteams).filter(db.Replay.id == gameID)
            for rteam in rteams:
                if rteam.name not in list_of_teams:
                    list_of_teams += (rteam.name,)
                    rteamIDs.append(rteam.id)
        db.Session.remove()
        self.curatedTeamNames.set(list_of_teams)
        self.curatedRTeamIDs = rteamIDs

        # print('Completed in',time.time()-startTime)
        self.update_player_names()

    def update_player_names(self, *args):
        # startTime = time.time()

        gamesSelected = self.gameBox.curselection()
        teamsSelected = self.teamBox.curselection()

        if teamsSelected:
            session = db.Session()

            list_of_players = ()
            rplayerIDs = []

            teamsSelectedNames = [self.curatedRTeamIDs[x]
                                  for x in teamsSelected]
            gamesSelectedID = [self.allGameIDs[x] for x in gamesSelected]

            rplayers = session.query(db.RPlayer).join(db.Player).join(db.RTeam).join(db.Replay).filter(
                db.Replay.id.in_(gamesSelectedID)).filter(db.RTeam.id.in_(teamsSelectedNames)).all()
            for rplayer in rplayers:
                if rplayer.name not in list_of_players:
                    list_of_players += (rplayer.name,)
                    rplayerIDs.append(rplayer.id)
            self.curatedPlayerNames.set(list_of_players)
            self.curatedRPlayerIDs = rplayerIDs
            db.Session.remove()
        else:
            self.curatedPlayerNames.set(())
            self.curatedRPlayerIDs = []
        # print('Completed in',time.time()-startTime)

    def select_x(self, listBox, textVariable):
        selection = textVariable.get()
        if 'All' in selection:
            listBox.select_set(0, 1000)
        elif 'None' in selection:
            listBox.selection_clear(0, 1000)
        if listBox.curselection():
            textVariable.set('Select None')
        else:
            textVariable.set('Select All')
        self.update_team_names()

    def get_data_options(self):
        gamesSelected = self.gameBox.curselection()
        teamsSelected = self.teamBox.curselection()
        playersSelected = self.playerBox.curselection()

        gameids = [self.allGameIDs[x] for x in gamesSelected]
        rteamids = [self.curatedRTeamIDs[x] for x in teamsSelected]
        rplayerids = [self.curatedRPlayerIDs[x] for x in playersSelected]

        return (gameids, rteamids, rplayerids)

    def gameMotion(self, event):
        x, y = event.x, event.y
        try:
            gameID = self.allGameIDs[self.gameBox.nearest(y)]
        except IndexError:
            return
        session = db.Session()
        game = session.query(db.Replay).filter(db.Replay.id == gameID).one()
        text = 'Map: ' + game.map + ', ' + 'Date: ' + \
            game.dateTime.strftime('%Y-%m-%d %H:%M') + \
            ', ID: ' + str(game.replayID) + '\n'
        for team in game.teams:
            text += team.rteam.name + ': ' + team.colour.title() + ', '
        text = text[:-2]
        tip = tooltip.ToolTip(self.gameBox, text, x, y)
        # ttp = tooltip.CreateToolTip(self.gameBox, text)
