import tkinter as tk
import os.path
from tkinter import ttk
from pyroplane.plotter.plotter import GamePlotter
from pyroplane.statsexporter import StatsExporter

class ExportButton:

    def __init__(self,parent):
        # parent.typePicker = self
        self.parent = parent
        parent.windowFrame.grid_columnconfigure(2,weight=1,minsize=100)


        exportFrame = ttk.Frame(parent.windowFrame,height=100,width=100,relief='flat')
        exportFrame.grid(row=0,column=2,pady=(0,1),padx=(20,0),sticky='we')
        exportFrame.grid_columnconfigure(0,weight=1,minsize=120)
        exportFrame.grid_rowconfigure(0,weight=1,minsize=53)
        exportFrame.grid_rowconfigure(1,weight=1,minsize=50)
        exportFrame.grid_rowconfigure(2,weight=1,minsize=50)
        exportFrame.grid_rowconfigure(3,weight=1,minsize=53)


        statFrame = ttk.Frame(exportFrame,height=55,width=100)
        statFrame.pack_propagate(0)
        statsButton = ttk.Button(statFrame,text='Export Stats',command=self.export_stats,style=None)
        statsButton.pack(fill='both',expand=True)
        statFrame.grid(row=0,rowspan=2,column=0,sticky='nwe')


        plotFrame = ttk.Frame(exportFrame,height=55,width=100)
        plotFrame.pack_propagate(0)
        plotButton = ttk.Button(plotFrame,text='Make Plot',command=self.add_plot,style=None)
        plotButton.pack(fill='both',expand=True)
        plotFrame.grid(row=2,rowspan=2,column=0,sticky='swe')

        bothFrame = ttk.Frame(exportFrame,height=100,width=100,)
        bothFrame.pack_propagate(0)
        bothButton = ttk.Button(bothFrame,text='Do Both',command=self.do_both,style=None)
        bothButton.pack(fill='both',expand=True)
        bothFrame.grid(row=1,rowspan=2,column=0,sticky='wens')


    def export_stats(self):
        dataOptions = self.parent.dataPicker.get_data_options()
        typeOptions = self.parent.typePicker.get_type_options()

        if dataOptions[0] and (dataOptions[1] or dataOptions[2]):

            newStats = StatsExporter(dataOptions,typeOptions)
            i = 2
            outputPath = 'output.txt'
            while os.path.isfile(os.path.join(self.parent.rootPath,outputPath)):
                outputPath = 'output ('+str(i)+').txt'
                i += 1
            with open(os.path.join(self.parent.rootPath,outputPath),'w') as f:
                f.write(newStats.output)

            self.parent.status.set('Output successfully written to '+outputPath+'.')

        else:
            print('Ensure at least a game and a team or player is selected.')

        pass

    def add_plot(self):
        dataOptions = self.parent.dataPicker.get_data_options()
        typeOptions = self.parent.typePicker.get_type_options()
        if dataOptions[0] and (dataOptions[1] or dataOptions[2]):
            newPlot = GamePlotter(self,dataOptions,typeOptions)
        else:
            print('Ensure at least a game and a team or player is selected.')
        pass

    def do_both(self):
        self.add_plot()
        self.export_stats()
        pass
