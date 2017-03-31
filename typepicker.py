import tkinter as tk
from tkinter import ttk


class TypePicker:
    
    def __init__(self,parent):    
        # parent.typePicker = self
        self.parent = parent
        self.typePickerWindow = ttk.Panedwindow(parent.windowFrame,orient='horizontal')
        # self.dataPicker.grid(row=0,column=1,sticky='nesw')

        parent.windowFrame.grid_columnconfigure(1,weight=1,minsize=200)

        self.plotGoalTimeFrame = ttk.Frame(self.typePickerWindow,relief='groove')
        # self.plotGoalTimeFrame.grid(row=0,column=1,ipady=10,padx=(20),sticky='we')
        
        self.plotGoalTimeFrame.grid_rowconfigure(0,weight=0)
        self.plotGoalTimeFrame.grid_rowconfigure(1,weight=2)
        self.plotGoalTimeFrame.grid_rowconfigure(2,weight=0)
        self.plotGoalTimeFrame.grid_rowconfigure(3,weight=2)
        self.plotGoalTimeFrame.grid_columnconfigure(0,weight=2)
        self.plotBy = tk.StringVar()
        self.plotBy.set('goals')
        # plot by goals
        ttk.Radiobutton(self.plotGoalTimeFrame,text='Plot by goals',
            variable=self.plotBy,
            value='goals',
            command=self.update_plot_by,
            width=13).grid(row=0,column=0,padx=10,pady=(20,0),sticky='w')
        
        self.goalFrame = ttk.Frame(self.plotGoalTimeFrame,height=10)
        
        isGoalCommand = self.goalFrame.register(self.isGoal)
        self.goalEntryText = tk.StringVar()
        goalEntry = ttk.Entry(self.goalFrame,
            textvariable=self.goalEntryText,
            width=10,
            validate='focusout',
            validatecommand=(isGoalCommand,'%V','%P'),
            invalidcommand=lambda:parent.status.set('Invalid goal entry. Insert goal numbers separated by space. Can be negative. E.g. -1 for last goal. 0 for all goals.'))


        
        ttk.Label(self.goalFrame,text='Goals:').grid(row=0,column=0)
        goalEntry.grid(row=0,column=1,sticky='e')
        self.goalFrame.grid_columnconfigure(0,weight=1)
        self.goalFrame.grid_columnconfigure(1,weight=3)
        
        self.goalFrame.grid(row=1,pady=(0,20))
        self.goalEntryText.set('0')
        
        # plot by time
        ttk.Radiobutton(self.plotGoalTimeFrame,
            text='Plot by time',
            variable=self.plotBy,
            value='time',
            command=self.update_plot_by,width=13).grid(row=2,column=0,sticky='w',padx=10,pady=(10,0))
        self.timeFrame = tk.Frame(self.plotGoalTimeFrame,height=10)
        
        #for validating time input
        isTimeCommand = self.timeFrame.register(self.isTime)

        self.startTime=tk.IntVar()
        # startTime.set()
        startTimeEntry = ttk.Entry(self.timeFrame,
            textvariable=self.startTime,
            width=5,
            validate='all',
            validatecommand=(isTimeCommand,'%V','%P'),
            invalidcommand=lambda: parent.status.set('Invalid start time. This is the number of seconds remeining on the countdown.'))
        
        self.endTime=tk.IntVar()
        # endTime.set('End time (s)')
        endTimeEntry = ttk.Entry(self.timeFrame,
            textvariable=self.endTime,
            width=5,validate='all',
            validatecommand=(isTimeCommand,'%V','%P'),
            invalidcommand=lambda: parent.status.set('Invalid end time. This is the number of seconds remaining on the countdown.'))

        ttk.Label(self.timeFrame,text='Start (s):').grid(row=0,column=0)
        startTimeEntry.grid(row=0,column=1,pady=5)
        ttk.Label(self.timeFrame,text='End (s):').grid(row=1,column=0)
        endTimeEntry.grid(row=1,column=1)
        self.timeFrame.grid(row=3,column=0,pady=(0,20))

        
        # second column - adding stuff
        # parent.windowFrame.grid_columnconfigure(2,weight=1,minsize=170)

        plotTypeFrame = ttk.Frame(self.typePickerWindow,relief='groove')
        # plotTypeFrame.grid(row=0,column=2,ipady=20,sticky='we')
        plotTypeFrame.grid_columnconfigure(0,weight=1,minsize=1)
        plotTypeFrame.grid_columnconfigure(1,weight=1,minsize=170)


        self.plotOvertime = tk.IntVar()
        self.plotOvertime.set(1)
        plotOvertimeCheck = ttk.Checkbutton(plotTypeFrame,text='Include Overtime',variable=self.plotOvertime,command=lambda:print(self.plotOvertime.get()))

        plotOvertimeCheck.grid(column=1,row=0,padx=(20,30),pady=(30,20),sticky='we')


        self.plotHeat = tk.IntVar()
        heatCheck = ttk.Checkbutton(plotTypeFrame,text='Heatmap',variable=self.plotHeat,command=self.update_heat_check)
        self.normaliseHeat = tk.IntVar()
        self.heatNormalise = ttk.Checkbutton(plotTypeFrame,text='Normalise',variable=self.normaliseHeat)
        self.plotLine = tk.IntVar()
        lineCheck = ttk.Checkbutton(plotTypeFrame,text='Line',variable=self.plotLine)
        self.plotHeat.set(1)
        self.normaliseHeat.set(1)

        heatCheck.grid(column=1,row=1,padx=(20,30),sticky='we')
        self.heatNormalise.grid(column=1,row=2,padx=(30,30),sticky='we')
        lineCheck.grid(column=1,row=3,padx=(20,30),pady=3,sticky='ew')

        # plotTypeFrame.grid_rowconfigure(1,minsize=30)
        
        self.plotBall = tk.IntVar()
        ballCheck = ttk.Checkbutton(plotTypeFrame,text='Include ball',variable=self.plotBall)
        ballCheck.grid(column=1,row=4,padx=(20,30),pady=(20,0),sticky='we')
        
        self.typePickerWindow.add(self.plotGoalTimeFrame,weight=10)
        self.typePickerWindow.add(plotTypeFrame,weight=10)
        self.typePickerWindow.grid(row=0,column=1,sticky='nsew',padx=10)
            
            
    def update_plot_by(self):
        plotBy = self.plotBy.get()
        if plotBy == 'goals':
            for child in self.timeFrame.winfo_children():
                child['state']='disable'
            for child in self.goalFrame.winfo_children():
                child['state']='normal'
            pass
        elif plotBy == 'time':
            for child in self.goalFrame.winfo_children():
                child['state']='disable'
            for child in self.timeFrame.winfo_children():
                child['state']='normal'
            pass
        pass
        
    def update_heat_check(self):
        if self.plotHeat.get():
            self.heatNormalise.configure(state='normal')
        else:
            self.heatNormalise.configure(state='disabled')
    
    def isTime(self,why,text):
        if why == 'key':
            if (text) and (text != '-'):
                try:
                    int(text)
                except ValueError:
                    return False
        elif why == 'focusout':
            if text:
                try:
                    int(text)
                except ValueError:
                    return False
        return True
        
    def isGoal(self,why,text):
        try:
            if ':' in text:
                y = list(int(x) for x in text.split(':'))
                if len(y) != 2: return False
                
                print('Start: ' + str(y[0]) + '   End: ' + str(y[1]))
            else:
                print(str(list(int(x) for x in text.split())))
        except ValueError:
            print(text)
            return False
        return True
            
    
    def get_type_options(self):
        plotBy = self.plotBy.get()
        if plotBy == 'goals':
            a = {plotBy:self.goalEntryText.get()}
        elif plotBy == 'time':
            a = {plotBy:[self.startTime.get(),self.endTime.get()]}
        b = (self.plotOvertime.get(),self.plotHeat.get(),self.normaliseHeat.get(),self.plotLine.get(),self.plotBall.get())
        
        return((a,b))