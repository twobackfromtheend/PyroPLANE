from tkinter import *


class ToolTip():
    allTips = {} # widget:tooltip
    
    def __init__(self, widget, text, x,y):
        if widget in ToolTip.allTips:
            lastTip = ToolTip.allTips[widget]
            if lastTip.text == text:
                lastTip.x = x
                lastTip.y = y
                return
            else:
                lastTip.hidetip()
                
        self.widget = widget
        self.text = text
        self.tipwindow = None
        self.id = None
        # self.x = self.y = 0
        self.x = x
        self.y = y
        self._id1 = self.widget.bind("<Enter>", self.enter)
        self._id2 = self.widget.bind("<Leave>", self.leave)
        self._id3 = self.widget.bind("<ButtonPress>", self.leave)
        
        self.schedule()

        ToolTip.allTips[widget] = self

    def enter(self, event=None):
        self.schedule()

    def leave(self, event=None):
        self.unschedule()
        self.hidetip()

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(500, self.showtip)

    def unschedule(self):
        id = self.id
        self.id = None
        if id:
            self.widget.after_cancel(id)

    def showtip(self):
        if self.tipwindow:
            return
        if self not in ToolTip.allTips.values():
            return
        # The tip window must be completely outside the button;
        # otherwise when the mouse enters the tip window we get
        # a leave event and it disappears, and then we get an enter
        # event and it reappears, and so on forever :-(
        x = self.widget.winfo_rootx() + self.x + 10
        y = self.widget.winfo_rooty() + self.y + 10 #self.widget.winfo_height() 
            
        self.tipwindow = tw = Toplevel(self.widget)
        
        tw.wm_overrideredirect(1)
        tw.wm_geometry("+%d+%d" % (x, y))
        self.showcontents()

    def showcontents(self):
        text = self.text
        print('Showing Tooltip:',text)
        label = Label(
            self.tipwindow, 
            text=text, 
            justify=LEFT,
            background="#eeeeee", 
            relief='flat', 
            borderwidth=1,
            font=('helvetica','8')
            )
        label.pack(ipadx=2,ipady=1)

    def hidetip(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()
