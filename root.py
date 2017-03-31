import os
import sys
import re
import tkinter as tk
from tkinter import filedialog
import time
import tqdm
from pyroplane.datapicker import DataPicker
from pyroplane.typepicker import TypePicker
from pyroplane.advancedplot import AdvancedPlot
import pyroplane.database.database as db
import pyroplane.anal.areplay as ar
from pyroplane.animator import ReplayMap


class RootWindow:

    def __init__(self):
        if getattr(sys, 'frozen', False):
            self.rootPath = os.path.dirname(sys.executable)
        elif __file__:
            self.rootPath = os.path.dirname(__file__)

        # self.rootPath = os.path.dirname(__file__)

        # create main window
        self.root = tk.Tk()
        self.root.option_add('*tearOff', tk.FALSE)
        self.root.withdraw()
        self.win = tk.Toplevel(self.root)

        self.win.title('Analyser')
        self.menuBar = self.create_menu_bar(self.win)
        self.win.config(menu = self.menuBar)

        # s = ttk.Style()
        # print(s.theme_names())
        # print(s.theme_use('winnative'))

        # window frame
        windowFrame = tk.Frame(self.win)
        self.windowFrame = windowFrame

        windowFrame.config(
            width = 500,
            height = 200,
            )

        windowFrame.pack(fill='both',expand=True,padx=30,pady=10)
        # print('hi')

        # status bar
        self.status = tk.StringVar()
        sBFrame = tk.Frame(self.win,borderwidth=1,height=1,relief='groove')

        statusBar = tk.Label(sBFrame, textvariable=self.status, anchor='w',width='100')
        self.statusBar = statusBar
        statusBar.pack(fill='both', expand=1)
        sBFrame.pack(fill='x',pady=(5,0),anchor='s',)

        # root.mainloop()

    # @staticmethod
    def create_menu_bar(self,parent):
        menubar = tk.Menu(parent)
        menubar.add_command(
            label="Add Replay",
            command = lambda: RootWindow.add_file(self))
        menubar.add_command(
            label="Add Replays from Folder",
            command = lambda: RootWindow.add_folder(self))
        menubar.add_command(
            label="Show Advanced",
            command=self.show_advanced)

        toolsMenu = tk.Menu(menubar)
        menubar.add_cascade(label='Tools',menu=toolsMenu)
        toolsMenu.add_command(
            label='Refresh teams',
            command = lambda: DataPicker.refresh_all_teamNames(self))
        menubar.add_command(
            label="Test",
            command=self.test)

        analysisMenu = tk.Menu(menubar)
        menubar.add_cascade(label='Analysis',menu=analysisMenu)
        analysisMenu.add_command(
            label='Analyse All Hits',
            command = ar.analyse_all_player_hits)
        analysisMenu.add_command(
            label='Analyse All Positions',
            command = ar.analyse_all_positions)
        analysisMenu.add_command(
            label='Game Analyser',
            command = lambda: ReplayMap.new_replay(self))

        return menubar

    # @classmethod
    def add_file(self):
        filePath = filedialog.askopenfilename(parent=self.win,initialdir=self.rootPath)
        match = self.get_file_name(filePath)
        if match:
            fileName = match.group(1)
            self.dataPicker.add_game(filePath,fileName)

            return fileName
        else:
            self.status.set('Failed to import 1 file. Ensure it is a .pysickle file.')


    def add_folder(self):
        folderPath = filedialog.askdirectory(parent=self.win,initialdir=self.rootPath)
        if folderPath:
            startTime = time.time()
            files = os.listdir(folderPath)
            noOfFiles = len(files)
            addedFiles = 0
            failedFiles = 0
            for _file in tqdm.tqdm(files):
                filePath = os.path.join(folderPath,_file)
                print(filePath)
                # print('hi')
                match = self.get_file_name(filePath)
                if match:
                    fileName = match.group(1)
                    try:
                        self.dataPicker.add_game(filePath,fileName)
                    except KeyError:
                        print(sys.exc_info())

                    addedFiles += 1
                    print('Completed: ',addedFiles,'/',noOfFiles,'\n')

                else:
                    failedFiles += 1
            if failedFiles:
                self.status.set('Imported '+str(addedFiles)+' files successfully. Failed to import '+str(failedFiles)+' files. Ensure you have not added non-.pysickle files.')
            else:
                self.status.set('Imported '+str(addedFiles)+' files.')
            endTime = time.time()
            duration = '{:.3}'.format(endTime-startTime)
            print('Total time taken for',addedFiles,'-',duration,'s')

    @staticmethod
    def get_file_name(filePath):
        match = re.search(r'(\w*.pysickle)$',filePath)
        return match

    def show_advanced(self):
        currentLabel = self.menuBar.entrycget(2,'label')
        if 'Show' in currentLabel:
            self.typePicker.typePickerWindow.add(self.advancedPlot.aPlotFrame,weight=10)
            # self.advancedPlot.aPlotFrame.grid(row=0,column=3,ipady=10)

            self.menuBar.entryconfig(2,label='Hide Advanced')
        elif 'Hide' in currentLabel:
            self.typePicker.typePickerWindow.remove(self.advancedPlot.aPlotFrame)
            # self.menuBar.entryconfig(1,label='Show Advanced Plot')

            self.menuBar.entryconfig(2,label='Show Advanced')

    def test(self):
        test.test(self)
