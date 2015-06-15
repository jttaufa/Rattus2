from Tkinter import *



class CmdListSection(Frame):
    def __init__(self, master, *args, **kwargs):
        Frame.__init__(self, master, *args, **kwargs)

        self.scrollbar = Scrollbar(self, command = self.scrollLists)
        self.cmdPW = PanedWindow(self, sashrelief = SUNKEN, bg = 'white')

        self.frame1 = Frame(self.cmdPW)
        self.frame2 = Frame(self.cmdPW)
        
        self.cmdList1 = CmdList(self.frame1, yscrollcommand = self.scrollBar,
                                activestyle = 'none', exportselection = False)
        self.cmdList2 = CmdList(self.frame2, yscrollcommand = self.scrollBar, activestyle = 'none',
                                exportselection = False, takefocus = False)

        self.lbl1 = Label(self.frame1, text = "Type")
        self.lbl2 = Label(self.frame2, text = "Value")

        self.lbl1.pack(side=TOP, fill = X)
        self.cmdList1.pack(side=TOP, fill = BOTH, expand = True)
        self.lbl2.pack(side=TOP, fill = X)
        self.cmdList2.pack(side=TOP, fill = BOTH, expand = True)


        self.cmdPW.add(self.frame1)
        self.cmdPW.add(self.frame2)


        self.cmdPW.paneconfigure(self.frame1, minsize = 100)
        self.cmdPW.paneconfigure(self.frame2, minsize = 100)
        #self.cmdPW.paneconfigure(self.frame1, padx = 10)
        #self.cmdPW.paneconfigure(self.frame2, padx = 10)

        self.scrollbar.pack(side=RIGHT, fill= Y, expand = True)
        self.cmdPW.pack(side = RIGHT, fill = BOTH, expand = True)

        self.master.bind('<ButtonRelease-1>', self.selectIndices)
        self.master.bind('<KeyRelease-Shift_L>', self.selectIndices)
        self.master.bind('<KeyRelease-Shift_R>', self.selectIndices)

    def scrollLists(self, *args):
        self.cmdList1.yview(*args)
        self.cmdList2.yview(*args)

    def scrollBar(self, *args):
        self.cmdList1.yview_moveto(args[0])
        self.cmdList2.yview_moveto(args[0])
        self.scrollbar.set(*args)

    def selectIndices(self, event):
        indices = []
        indices+=(self.cmdList1.curselection())
        #indices+=(self.cmdList2.curselection())

        self.cmdList1.selection_clear(0,END)
        self.cmdList2.selection_clear(0,END)
        for index in indices:
            self.cmdList1.selection_set(index)
            self.cmdList2.selection_set(index)
        #print self.cmdList1.curselection()

    def deleteItems(self):
        for index in reversed(self.cmdList1.curselection()):
            self.cmdList1.delete(index)
            self.cmdList2.delete(index)
        
    def addItems(self, indices, commands):
        #Create a cmd object for processing
        #for index in reversed(indices):
        #reverse list of indices
        #   insert END command into the box at index specified by index
        #   
        for index in reversed(indices):
            command = commands.pop()
            print command
            self.cmdList1.insert(index, command.getTypeStr())
            self.cmdList2.insert(index, command.getValStr())


class CmdListFrame(Frame):
    def __init__(self, master, *args, **kwargs):
        Frame.__init__(self, master, *args, **kwargs)

        self.scrollbar = Scrollbar(self, command = self.scrollLists)
        self.cmdList1 = CmdList(self, yscrollcommand = self.scrollBar, activestyle = 'none',
                                exportselection = False)
        self.cmdList2 = CmdList(self, yscrollcommand = self.scrollBar, activestyle = 'none',
                                exportselection = False, takefocus = False)
        self.cmdList3 = CmdList(self, yscrollcommand = self.scrollBar, activestyle = 'none',
                                exportselection = False, takefocus = False)
        self.scrollbar.pack(side=RIGHT, fill= Y)
        self.cmdList3.pack(side=RIGHT, fill = Y)
        self.cmdList2.pack(side=RIGHT, fill = Y)
        self.cmdList1.pack(side=RIGHT, fill = Y)

        self.master.bind('<ButtonRelease-1>', self.selectIndices)
        self.master.bind('<KeyRelease-Shift_L>', self.selectIndices)
        self.master.bind('<KeyRelease-Shift_R>', self.selectIndices)

    def scrollLists(self, *args):
        self.cmdList1.yview(*args)
        self.cmdList2.yview(*args)
        self.cmdList3.yview(*args)

    def scrollBar(self, *args):
        self.cmdList1.yview_moveto(args[0])
        self.cmdList2.yview_moveto(args[0])
        self.cmdList3.yview_moveto(args[0])
        self.scrollbar.set(*args)

    def selectIndices(self, event):
        indices = []
        indices+=(self.cmdList1.curselection())
        #indices+=(self.cmdList2.curselection())
        #indices+=(self.cmdList3.curselection())

        self.cmdList1.selection_clear(0,END)
        self.cmdList2.selection_clear(0,END)
        self.cmdList3.selection_clear(0,END)
        for index in indices:
            self.cmdList1.selection_set(index)
            self.cmdList2.selection_set(index)
            self.cmdList3.selection_set(index)
        

class CmdList(Listbox):
    def __init__(self, master, *args, **kwargs):
        Listbox.__init__(self, master, selectmode=EXTENDED, *args, **kwargs)

        i=0
        while (i < 20):
            self.insert(END, str(i)+'\t'+'fish')
            i+=1


def delete(event):
    cmdFrame.deleteItem()

if __name__ == "__main__":
    root = Tk()

    #root.bind("<n>", delete)
    
    cmdFrame = CmdListSection(root)
    cmdFrame.pack(fill=BOTH, expand = True)

    #cmdFrame.deleteItems()

    mainloop()
