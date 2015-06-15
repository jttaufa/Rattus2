'''
    File:
        Telnet_RXTX.py
    Author:
        Jonathon Taufatofua, 2015
        University of Queensland
    Description:
        The RxTxThread handles most of the Telnet transmission and string
        parsing using the telnetlib Telnet library.
'''
import getpass
import sys
from telnetlib import Telnet, AYT, NOP
import os
import threading as thr
from time import sleep


def cmdSet2Str(cmdSet):
    '''Parse the command set into valid communication format

    cmdSet2Str([[cmd]]) -> string
    '''
    strOut = ''
    for cmd in cmdSet:
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

def connectToServer(hostIP = "10.10.100.254", port = 8899):
    HOST = hostIP #Host IP Address
    PORT = port   #Host port number

    pingStr = "ping "+HOST #Attempt to ping host
    if (os.system(pingStr)==0): #Host able to be pinged
        print "Robot found...", #Comma prevents printed line from wrapping
        try: #Attempt to connect to remote host
            tn = Telnet(host = HOST, port = PORT)
            print "Connected!"
        except Exception as E: #Failed connection
            print "Connection failed!"
            raise E
    else:                       #Host not found
        print "Host not found"
        raise ValueError('Could not connect to a host')

    print "Transmitting..."
    cmdSet = [['SPL','!C'], #Clear buffer
              ['SPL','!?'], #Request command buffer
              ['SPL','!N'], #Request ID
              ['CMD','1',50,51,52], #Transmit commands
              ['CMD','A',98,99,100],
              ['SPL','!?'], #Request command buffer
              ['SPL','!N']] #Request ID
    cmdSetStr = cmdSet2Str(cmdSet)
    tn.write(cmdSetStr)

    sleep(0.5) #Wait after transmitting
    return tn

class RxTxThread(thr.Thread):
    '''Thread that handles all the data transmission and reception from the
    remote robot host.
    '''
    rxTextList = []
    def __init__(self, controller, name, host, port):
        self.controller = controller
        self._stop = thr.Event()
        self.tn = connectToServer(host, port)
        thr.Thread.__init__(self,name=name)
 
    def run(self):
        '''Main thread operation listens for incoming data and appends it to
        the list of received data
        '''
        while (not self._stop.isSet()):
            if (self.tn.sock_avail()):
                print "Receiving..."
                rcvStr = ''
                while (self.tn.sock_avail()):
                    rcvStr += self.tn.read_very_eager() 
                
                self.rxTextList.append(self.parseRcvStr(rcvStr))
                messages = self.parseRcvStr(rcvStr)
                print messages
                self.controller.processMessages(messages)
            sleep(0.1)
        self.tn.close() #Close socket on exit

    def getRXText(self):
        '''Returns list of received commmands
        getRXText(void) -> list(msg)
        '''
        return self.rxTextList

    def stop(self):
        '''Stop thread'''
        print "Stopped: "+self.name
        self._stop.set()

    def checkConnection(self):
        '''Checks connection to remote host'''
        print self.tn.get_socket().sendall(AYT + NOP)
        

    def getTN(self):
        '''Returns the Telnet object'''
        return self.tn

    def setTN(self, tn):
        '''Closes the Telnet interface and sets a new one'''
        self.tn.close()
        self.tn = tn

    def parseRcvStr(self,rxStr):
        '''Converts rxStr into a format able to be interpreted by the program'''
        msgsOut = []
        msgs = rxStr.splitlines()
        for msg in msgs:
            if (len(msg) == 0): #Ignore blank messages
                continue
            if (msg[0:2] == "->"):    #Command
                cmd = msg.strip("->") #Strip prefix
                vals = cmd.split("|") #Separate command values
                #Cast to required datatypes
                cmdParams = [    vals[0],
                             ord(vals[1]),
                             ord(vals[2]),
                             ord(vals[3])]
                msgsOut.append(cmdParams)
            else:                     #Special
                msgsOut.append(msg)
        return msgsOut

    def txCmd(self,cmd):
        '''Transmits a command to remote host'''
        self.tn.write(cmd)



if __name__ == "__main__":
    HOST = "10.10.100.254"
    PORT = 8899


    class Controller():
        def __init__(self):
            pass
        def processMessages(msgs):
            print msgs

    emptyController = Controller()

    rxThread = RxTxThread(emptyController, "rxtxThread", HOST, PORT)
    rxThread.start()

    rxThread.stop()
