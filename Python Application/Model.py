'''
    File:
        Model.py
    Author:
        Jonathon Taufatofua, 2015
        University of Queensland
    Description:
        The Model class contains the major operational methods for controlling
        the Rattus robot. This includes the saving and loading of command
        sequences and robot configuration parameters.
'''


class Model():
    def __init__(self, cmdList = [], config = ["Rattus1",("10.10.100.254", 8899),(1,0,0)]):
        self.cmdList = cmdList
        self.config = config

    def convCommands(self):
        ''' Converts data in command arrays for motor directions into signed    
        8-bit format for intepretation by the robot.

        #Adjusts motor directions to signed 8 bit
        '''
        convCmdList = []
        for cmd in self.cmdList:
            convCmd = []
            if (cmd[0] == 'CMD'):
                convCmd.append(cmd[0])
                convCmd.append(cmd[1])
                convCmd.append(toInt8_t(cmd[2]))
                convCmd.append(toInt8_t(cmd[3]))
                convCmd.append(cmd[4])
            else:
                convCmd.append(cmd[0])
            convCmdList.append(convCmd)
        return convCmdList


    def saveCommands(self,filename):
        '''Saves the command set as a provided filename. 

        saveCommands(str) -> None
        '''

        #Check file extension - (.irat)
        if (filename[-5:] != '.irat'):
            filename += '.irat'
        savefile = open(filename, 'w')

        #Write one line per command
        for cmd in self.cmdList:
            outStr=''
            for val in cmd:
                outStr += str(val)+','
            outStr = outStr.strip(',')
            savefile.write(outStr+'\n')
        savefile.close()

        
    def loadCommands(self, filename):
        ''' Loads the command set from a provided filename. Returns true if
        file successfully loaded, false otherwise.

        loadCommands(str) -> bool
        '''
        if (filename[-5:] != '.irat'):
            print "Invalid filetype"
            return False
        self.cmdList = [] #Clear list
        loadfile = open(filename,'r')

        for line in loadfile:
            cmd = []
            linesplit = line.strip('\n').split(',')
            cmd.append(linesplit[0])
            cmd.append(linesplit[1])
            cmd.append(int(linesplit[2]))
            cmd.append(int(linesplit[3]))
            cmd.append(int(linesplit[4]))
            self.cmdList.append(cmd)
        return True

    def getCommands(self):
        ''' Returns the command list '''
        return self.cmdList

    def clearCommands(self):
        ''' Clears the command list '''
        self.cmdList = []

    def getConfig(self):
        '''Returns the current Rattus configuration'''
        return self.config

    def getConfigName(self):
        return self.config[0]

    def getHost(self):
        return self.config[1][0]
    def getPort(self):
        return self.config[1][1]

    def getPIDParams(self):
        return self.config[2]

    def saveConfig(self, filename):
        '''Saves the rat configuration as a provided filename. 

        saveConfig(str) -> None
        '''
        #Check file extension - (.iratc)
        if (filename[-6:] != '.iratc'):
            filename += '.iratc'
        savefile = open(filename, 'w')

        #Write one line per config parameter
        savefile.write(self.config[0]+'\n')         #Name
        savefile.write(self.config[1][0]+'\n')      #IP
        savefile.write(str(self.config[1][1])+'\n') #PORT
        outStr=''
        for param in self.config[2]:                #PID Parameters
            outStr += str(param)+','
        outStr = outStr.strip(',')
        savefile.write(outStr)        
        savefile.close()        

    def loadConfig(self, filename='default.iratc'):
        ''' Loads the configuration from a provided filename. Returns true if
        file successfully loaded, false otherwise.

        loadConfig(str) -> bool
        '''
        if (filename[-6:] != '.iratc'):
            print "Invalid filetype"
            return False
        self.config = [] #Clear list
        loadfile = open(filename,'r')

        iLine = 0
        cfg = []
        for line in loadfile:
            linesplit = line.strip('\n').split(',')
            if (iLine == 0):
                cfg.append(linesplit[0])
            elif (iLine == 1):
                cfg.append(tuple(linesplit,))
            elif(iLine == 2):
                cfg[1] += (int(linesplit[0]),)
            elif(iLine == 3):
                cfg.append(tuple(int(j) for j in linesplit))
            iLine += 1
        self.config = cfg[:]
        return True

def toInt8_t(num): #Convert signed value -128<=num<=127 to a signed 8-bit rep
    #Invalid value
    if (num > 127) or (num<-128) or (not isinstance(num, int)):
        print "Invalid input for signed 8-bit conversion"
        return None

    if (num >= 0):
        return num
    elif (num < 0):
        return 256 + num    

def cmdSet2Str(cmdSet):
    strOut = ''
    for cmd in cmdSet:
        print cmd
        if cmd[0] == 'CMD': #Command
            strOut += 'c'
            strOut += cmd[1]
            strOut += str(chr(cmd[2]))
            strOut += str(chr(cmd[3]))
            strOut += str(chr(cmd[4]))
            strOut += 'C'
        elif cmd[0] == 'SPL': #Special Command
            strOut += cmd[1]
    return strOut


if __name__ == '__main__':
    defaultCmdList =    [['CMD','A',-1,-2,3],
                        ['CMD','B',-4,5,6],
                        ['CMD','C',-7,-8,9]]    
    defaultConfig = ["Robert",("10.10.100.254", 8899),(1,0,0)] 
    
    a = Model(defaultCmdList)
    a.saveConfig("default.iratc")
    b = Model(defaultCmdList, defaultConfig)
    a.saveCommands("fishy.irat")
    #print b.loadCommands('fishy.irat')
    #print a.getCommands()
    #print b.getCommands()
    #print b.convCommands()
