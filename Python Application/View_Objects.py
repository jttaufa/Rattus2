'''
    File:
        View_Objects.py
    Author:
        Jonathon Taufatofua, 2015
        University of Queensland
    Description:
        This file contains some of the objects needed for displaying to the
        UI.
'''
from Tkinter import *
from math import sqrt, atan, atan2, degrees, radians, cos

class JoystickFrame(Frame):
    '''Frame for displaying the control joystick'''
    frameWidth = 400
    frameHeight = 400
    jsWidth = 350
    jsHeight = 350

    keyboardReady = False #Flag indicating a key is pressed
    jsKey = ''            #Char for pressed key
    def __init__(self,master, width = frameWidth, height = frameHeight):
        Frame.__init__(self, master, width = width, height = height,
                       padx = 5, pady = 5)

        self.jsPanel = JoystickPanel(self, width = self.jsWidth,
                                     height = self.jsHeight)
        self.rbtText = RobotText(self, width = 40)

        self.master.bind("<space>", self._keySpace)
        self.bind("<Key>", self._keyPress)
        self.bind("<KeyRelease>",self._keyRelease)
        
        self.jsPanel.pack(ipadx = 3, ipady = 3)
        self.rbtText.pack()
        self.pack(ipadx = 3, ipady= 3)
        self.focus_set()

    def getJSHandle(self):
        '''Return handle of joystick panel'''
        return self.jsPanel

    def getTextHandle(self):
        '''Return handle of text display box'''
        return self.rbtText

    def keyReady(self):
        '''Return the keyboard ready state'''
        return self.keyboardReady

    def getJSKey(self):
        '''Return the char of the pressed key '''
        outChar = self.jsKey
        self.jsKey = ''            #Clear char
        self.keyboardReady = False #Clear flag
        return outChar

    def _keyPress(self, event):
        '''Check if valid keypress performed and set flags if so'''
        keyList = ['m','w','a','s','d','q','!',' ',
                   'r','1','2','3','4','5','6','7']
        char = event.char
        if char in keyList:
            self.keyboardReady = True
            self.jsKey = char

    def _keyRelease(self, event):
        '''Check if a key has been released and print to terminal'''
        if event.char in ['w','a','s','d']:
            print event.char
            print "Valid Key!"
    
    def _keySpace(self, event):
        '''Callback for spacebar key'''
        speeds = self.jsPanel.getSpeeds()
        str1 = "Motor L: "+str(speeds[0])+"\t Motor R: "+str(speeds[1])
        self.rbtText.config(state = NORMAL)
        self.rbtText.insert(END, str1+"\n")
        self.rbtText.config(state = DISABLED)


class RobotText(Text):
    '''Text box for displaying messages from and for robot'''
    def __init__(self, master, width, height = 10):
        Text.__init__(self, master, width = width, height = height,
                      padx = 5, pady = 5, state=DISABLED)
    def setText(self, text):
        '''Set the text display'''
        self.config(state = NORMAL)
        self.insert(END, text)
        self.config(state = DISABLED)
        self.yview(END)
        
class JoystickPanel(Canvas):
    '''Panel for drawing joystick object'''
    #Drawing sizes
    canvasWidth = 300
    canvasHeight = 300
    orCircDia = 30          #Circle at origin
    jsCircDia = 25          #Joystick shift circle
    bdCircDia = canvasWidth #Bounding circle
    withinCanvas = False    #Check if joystick within canvas/bounding circle
    #Motor speeds from joystick (int)
    spdL = 0
    spdR = 0
    jsReleased = True       #Joystick not being actuated
    
    def __init__(self, parent, width = canvasWidth, height = canvasHeight):
        Canvas.__init__(self, parent, width = width, height = height,
                        relief = SUNKEN)
        self.parent = parent
        self.canvasWidth = width
        self.canvasHeight = height

        #Define origin coordinates
        self.x0 = width/2
        self.y0 = height/2
        self.origin = (self.x0, self.y0)

        #Draw crosshair
        self.create_line(self.x0, 0, self.x0, height, dash = (2,2))
        self.create_line(0, self.y0, width, self.y0, dash = (2,2))

        orCirc = self._circleBBox(self.origin, self.orCircDia)
        self.create_oval(orCirc,fill = 'white')
        bdCirc = self.create_oval(0,0,self.canvasWidth,self.canvasHeight)

        #Draw initial joystick position
        jsCirc = self._circleBBox(self.origin, self.jsCircDia)
        self.stick = self.create_oval(jsCirc, fill = 'black')
        self.stickLine = self.create_line(self.origin, self.origin, width = 2)

        #Bind mouse actions to panel
        self.bind("<B1-Motion>", self._moveJS)
        self.bind("<ButtonRelease-1>", self._releaseJS)
        self.bind("<Leave>", self._leaveCanvas)
        self.bind("<Enter>", self._enterCanvas)

    def getParent(self):
        '''Return parent object'''
        return self.parent

    def _moveJS(self, event):
        ''' Callback for when joystick is dragged '''
        if (self.withinCanvas): #Only if mouse is in canvas
            self.jsReleased = False #Joystick is controlling
            #Calculate position in polar coordinates relative to origin
            dx = event.x - self.origin[0]
            dy = self.origin[1] - event.y #Inverted as y-axis is flipped

            dist = sqrt(pow(dx,2) + pow(dy,2)) #Limits max speed
            theta = - degrees(atan2(float(dx),float(dy))) #Sets relative dir/spd
            
            #Scale relative directions/speeds
            dynSpd = 100 * cos(2.0 * radians(theta))
            #Save to motor variable as percentage of allowed speed
            if ((theta >=0) and (theta < 90)):
                motR = 100
                motL = dynSpd
            elif ((theta >= 90) and (theta <=180)):
                motR = -dynSpd
                motL = -100
            elif ((theta >=-180) and (theta < -90)):
                motR = -100
                motL = -dynSpd
            elif ((theta >=-90) and (theta <= 0)):
                motR = dynSpd
                motL = 100

            #Scale max absolute speed
            maxSpd = (dist - self.orCircDia/2) / (
                self.bdCircDia/2 - self.orCircDia/2)
            #Constrain
            if (maxSpd < 0): maxSpd = 0.0
            elif (maxSpd > 1): maxSpd = 1.0

            #Set local speed
            self.spdL = int(motL * maxSpd)
            self.spdR = int(motR * maxSpd)
            
            #Redraw joystick
            jsCirc = self._circleBBox((event.x, event.y), self.jsCircDia)
            self.coords(self.stick, jsCirc)
            self.coords(self.stickLine, (self.origin[0],self.origin[1],
                                         event.x, event.y))

    def _releaseJS(self, event):
        ''' Callback for when joystick is released '''
        jsCirc = self._circleBBox(self.origin, self.jsCircDia)
        self.coords(self.stick, jsCirc)
        self.coords(self.stickLine, (self.origin[0],self.origin[1],
                                     self.origin[0],self.origin[1]))
        
        self.spdL = 0
        self.spdR = 0
        print "Joystick Released"
        self.jsReleased = True

    def _leaveCanvas(self, event):
        '''Mouse is no longer in canvas'''
        self.withinCanvas = False

    def _enterCanvas(self, event):
        '''Mouse has entered canvas'''
        self.withinCanvas = True

    def _circleBBox(self, centre, size):
        '''Returns the bounding box coordinates of a circle with a particular
        size centered on (x,y)

        __circleBBox( (int, int), int) -> ((int, int),(int, int))
        '''
        x,y = centre
        topLeft = (x - size/2, y - size/2)
        botRight = (x + size/2, y + size/2)

        return (topLeft[0], topLeft[1], botRight[0], botRight[1])

    def isReleased(self):
        '''Joystick is not being actuated'''
        return self.jsReleased

    def getSpeeds(self):
        '''Returns the calculated motor speeds'''
        return (self.spdL, self.spdR)


if __name__ == '__main__':
    root = Tk()

    a = JoystickFrame(root)
    #x0,y0 =  a.getSpeeds()
    #print x0, y0

    mainloop()
