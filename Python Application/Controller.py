'''
    File:
        Controller.py
    Author:
        Jonathon Taufatofua, 2015
        University of Queensland
    Description:
        The Controller class handles most of the routing of data between the
        Telnet rxtx thread and the back-end model operation.
'''
import threading as thr
from Telnet_RXTX import RxTxThread
from View_Objects import *
from Model import Model
#from View import View

import Tkinter as tk

     

class TimerThread(thr.Thread):
    ''' This thread is used for retrieving information from the joystick and
    then transmitting it to the robot after a set time
    '''
    stopped = thr.Event()
    def __init__(self, controller, name):  
        thr.Thread.__init__(self, name = name)
        self.controller = controller #MVC Controller
        
    def run(self):
        '''While thread is running, block every 100ms'''
        while not self.stopped.wait(0.1):
            self.controller.transmitControl()
 
    def pause(self, enable):
        '''Allows the user to pause the timer'''
        if enable:
            self.stopped.set()
        else:
            self.stopped.clear()
            self.run()


class Controller():
    '''Main class for controlling the operations of the application'''
    def __init__(self):
        #Create a new Tkinter interface
        self.root = Tk()
        #Set an exit protocol
        self.root.protocol("WM_DELETE_WINDOW", self.exitRoot)

        #Create a model
        self.model = Model()
        self.model.loadConfig() #Load default configuration parameters
        #self.view  = View()

        #Start timer thread
        self.txTimer = TimerThread(self, "tmr")
        #Create joystick interface
        self.jsFrame = JoystickFrame(self.root)
        self.joystick = self.jsFrame.getJSHandle()
        self.statusBox = self.jsFrame.getTextHandle()

        #Initialise a telnet rxtx thread for wireless communication
        self.rxThread = RxTxThread(self,"rxtxthread", self.model.getHost(), self.model.getPort())
        if (self.rxThread.getTN() == 0):
            self.statusBox.setText('Could not establish a connection. Terminating...')
            return
        #Start Threads
        self.rxThread.start()
        self.txTimer.start()

        self.statusBox.setText('Connected\n')

        print self.rxThread.getRXText()

        self.rxThread.checkConnection()
        self.root.mainloop()

    def processMessages(self, messages):
        '''Displays received messages in a window box'''
        for msg in messages:
            self.statusBox.setText(msg + '\n')

    def transmitControl(self):
        '''Transmits the coordinates of the joystick if it it being actuated.
        Not complete in interfacing.'''
        if not self.joystick.isReleased():         #Joystick in use
            spdL,spdR =  self.joystick.getSpeeds() #Retrieve position as speeds
            print spdL, spdR
        if self.jsFrame.keyReady():                # WASD Control
            keyChar = self.jsFrame.getJSKey()      # Retrieve valid keypresses
            self.statusBox.setText("Pressed: "+keyChar+"\n")

            self.rxThread.txCmd(keyChar)           #Transmit typed character

    def exitRoot(self):
        '''Protocol for exiting main application'''
        self.rxThread.txCmd('!') #Stop robot
        self.txTimer.pause(True) #Stop timer
        self.rxThread.stop()     #Stop thread
        self.root.destroy()     

    
if __name__ == "__main__":
    #Create a controller for mainloop operation
    controller = Controller()
 
