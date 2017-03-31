#! python3

import pyroplane.database.database as db

from pyroplane.root import RootWindow
from pyroplane.datapicker import DataPicker
from pyroplane.typepicker import TypePicker
from pyroplane.exportbutton import ExportButton
from pyroplane.advancedplot import AdvancedPlot



root = RootWindow()
root.dataPicker = DataPicker(root)
root.typePicker = TypePicker(root)
root.exportButton = ExportButton(root)
root.advancedPlot = AdvancedPlot(root)
root.root.mainloop()





# root
    # dataPicker
        # allGames []
        # allGameNames.get()
        # allGameFileNames []
        # also assigned all players and teams their _name.
        # allGameData - team and player info per game
        # curatedTeamNames.get() list in box
        # curatedPlayerNames.get()
        # gameBox.curselection() list of selected (number) - allGames
        # teamBox.curselection() - curatedTeamNames
        # playerBox.curselection() - curatedPlayerNames
    # typePicker
        # plotOvertime.get() 1/0
        # plotHeat.get()
        # plotLine.get()
        # plotBall.get()
    # exportButton
    # advancedPlot
        # aPlotFrame
        # dataList
