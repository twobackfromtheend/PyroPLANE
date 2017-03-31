import tkinter as tk
from tkinter import ttk
from tkinter import simpledialog

class AdvancedPlot:
    
    def __init__(self,parent):
        self.parent = parent
        # parent.windowFrame.grid_columnconfigure(4,weight=1,minsize=100)
        self.aPlotFrame = ttk.Frame(parent.typePicker.typePickerWindow,height=100,width=100,relief='groove')
        
        
        
        addGroupButton = ttk.Button(self.aPlotFrame,text='Add Data Group',width=15,command=self.add_data_group)
        addGroupButton.grid(row=0,column=0,sticky='we',padx=5,pady=(10,3))
        
        self.dataList = []
        self.dataNameList = []
        self.curatedData = tk.Variable()
        self.dataBox = tk.Listbox(
            self.aPlotFrame,
            width=16,
            height=5, 
            listvariable=self.curatedData,
            selectmode='extended',
            activestyle='dotbox',
            relief='flat',
            exportselection=False)
        # self.dataBox.bind('<<ListboxSelect>>',self.update_player_names)
        self.dataBox.grid(row=1,column=0,sticky='we',padx=10,pady=10)
        self.dataBox.bind('<Delete>',self.delete_data)
        self.dataBox.bind('<Double-1>',self.rename_entry)
        # todo: update status bar when selected - show additional options
        
        
        # todo: add help button to explain stuff
        
    def delete_data(self,event):
        # print('delete')
        selection = list(self.dataBox.curselection())
        # reverse-sort it so shifting the other indexes after it doesnt matter.
        selection.sort(reverse=True)
        # print(selection)
        for x in selection:
            # remove listbox entry, remove data group entry
            del self.dataList[x]
            del self.dataNameList[x]
            self.curatedData.set(tuple(self.dataNameList))
        
        
    def rename_entry(self,event):
        try:
            selectNo = self.dataBox.curselection()[0]
        except IndexError: return
        selection = self.dataNameList[selectNo]
        newName = simpledialog.askstring('Rename Data Group', 'Old name was: '+selection+'\nNew name:')
        if newName:
            self.dataNameList[selectNo] = newName
            self.curatedData.set(tuple(self.dataNameList))
        
        
    def add_data_group(self):
        dataPicker = self.parent.dataPicker
        allData = {}
           
        gamesSelected = []
        for x in dataPicker.gameBox.curselection():
            gamesSelected.append(dataPicker.allGames[x])
            allData['games'] = gamesSelected
            recommendedTitle = str(len(gamesSelected))+' games'
            
        teamsSelected = []
        for x in dataPicker.teamBox.curselection():
            teamsSelected.append(dataPicker.curatedTeamNames.get()[x])
            allData['teams'] = teamsSelected
            recommendedTitle = str(len(teamsSelected))+' teams in '+str(len(gamesSelected))+' games'
            
        playersSelected = []
        for x in dataPicker.playerBox.curselection():
            playersSelected.append(dataPicker.curatedPlayerNames.get()[x])
            allData['players'] = playersSelected
            recommendedTitle = str(len(playersSelected))+' players in '+str(len(gamesSelected))+' games' 


            
        if allData:
            # other options:
            typeOptions = self.parent.typePicker.get_type_options()
            allData['typeOptions'] = typeOptions
        
            self.dataNameList.append(recommendedTitle)
            self.dataBox.insert('end',recommendedTitle)
            self.dataList.append(allData)
      
        pass
        
        
    def show_help(self):
        if self.helpWindow:
            self.helpWindow.destroy()
        self.helpWindow = tk.Toplevel()
        top.title("Help")
        msg = tk.Message(helpWindow,text=helpText)
        msg.pack()
        