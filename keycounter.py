
import sys
from PyQt6 import QtWidgets, QtCore, QtWidgets
import os.path

try:
    import urllib.request as urllib2
except ImportError:
    import urllib2

import urllib
from datetime import datetime
from sys import platform as _platform

# -----------------------------------------------

TOTALFILE = "total.txt"


if _platform == "darwin":
    from Foundation import NSObject, NSLog
    from Cocoa import NSEvent, NSKeyDownMask, NSKeyDown
    import string
elif _platform == "win32":
    ##import pyHook
    import pyWinhook as pyHook


def loadFile():

    if os.path.exists(TOTALFILE):
        f = open(TOTALFILE, "r")
        return f.read() 
    else:  ## initialize totals file if it does not exist.
        f = open(TOTALFILE, 'a+')
        f.write('0')
        f.close 


class KeyCounter(QtCore.QObject):
    '''
    Create an object that counts global keyboard presses

    The current count can be accessed at `keyCount`
    '''
    def __init__(self):
        super(KeyCounter, self).__init__()
        self.keyCount = 0
        if _platform == "win32":
            self.setupKeyCounterWin()
        elif _platform == "darwin":
            self.setupKeyCounterMac()

    def setupKeyCounterMac(self):
        mask = NSKeyDownMask
        NSEvent.addGlobalMonitorForEventsMatchingMask_handler_(mask, self.macCountKey)
        NSEvent.addLocalMonitorForEventsMatchingMask_handler_(mask, self.macCountKey)

    def macCountKey(self, event):
        eventCharAscii = ord(event._.characters)
        
        
        if eventCharAscii > 32 and eventCharAscii < 127:
            self.keyCount += 1

    def countKey(self, event):
        '''
        Increment the keyCount variable if an ascii key was pressed
        '''

        # if just basic keys are of interest:
        #if event.Ascii > 32 and event.Ascii < 127:
        self.keyCount += 1
        return True # Don't block key handling

    def setupKeyCounterWin(self):
        '''
        Setup the hook for monitoring global key presses
        '''
        hm = pyHook.HookManager()
        # watch for all keyboard events
        hm.KeyDown = self.countKey
        # set the hook
        hm.HookKeyboard()


class KeyCounterGui(QtWidgets.QWidget):
    '''
    Provide a GUI displaying the number of recorded keyboard Presses

    Will include some controls for saving to files or uploading online
    '''

    def __init__(self):
        super(KeyCounterGui, self).__init__()
        self.keyCounter = KeyCounter()
        self.initUI()


    def initUI(self):

        label = QtWidgets.QLabel('Characters pressed:')
        totalLabel = QtWidgets.QLabel('Total (so far):')

        self.counter = QtWidgets.QLabel()
        self.total = QtWidgets.QLabel()

        saveButton = QtWidgets.QPushButton('Save')
        saveButton.clicked.connect(self.saveToFile)

        resetButton = QtWidgets.QPushButton('Reset')
        resetButton.clicked.connect(self.resetCounter)

        postButton = QtWidgets.QPushButton('Post to Google')
        postButton.clicked.connect(self.postCount)

        grid = QtWidgets.QGridLayout()
        grid.setSpacing(10)

        grid.addWidget(label, 1, 0)
        grid.addWidget(self.counter,1 , 1)
 
        grid.addWidget(totalLabel, 2, 0)
        grid.addWidget(self.total, 2, 1)

        grid.addWidget(resetButton, 3, 0)
        grid.addWidget(saveButton, 3, 1)
        grid.addWidget(postButton, 4, 0)

        self.total.setText(loadFile())

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.updateCounter)
        self.timer.start(1000)

        self.setLayout(grid)

        self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle('Keystroke Counter')
        #self.setWindowIcon(QtWidgets.QIcon('web.png'))

        self.show()

    def updateCounter(self):
        keyCount = self.keyCounter.keyCount
        self.counter.setText(str(keyCount))



    def saveToFile(self):

        keyCount = self.keyCounter.keyCount
        with open('count.txt', 'a') as f:
            f.write('%s, %s\n' % (datetime.now(), keyCount))


        totalCounter= loadFile()
        if totalCounter == None:
            totalCounter = 0

        ttl = int(totalCounter)+int(keyCount)
        ##print("Total now: ", ttl)    
                          
        with open(TOTALFILE, 'w') as f2:
            f2.write(str(ttl))


    def resetCounter(self):
        self.keyCounter.keyCount = 0

    def postCount(self):
        keyCount = self.keyCounter.keyCount
        postCountToGoogleForm(keyCount)


#Remote Google Form logs post
def postCountToGoogleForm(keyCount):
    url="" #Specify Google Form URL here
    klog={'some_field':keyCount} #Specify the Field Name here
    try:
        dataenc = urllib.urlencode(klog)
        req = urllib2.Request(url,dataenc)
        response = urllib2.urlopen(req)
    except Exception as e:
        print(e)
    return True

def main():
    app = QtWidgets.QApplication(sys.argv)
    ex = KeyCounterGui()
    
    #sys.exit(app.exec())
    returnCode = app.exec()

    # save the counter when closing the app.
    ex.saveToFile()

    return returnCode;



if __name__ == '__main__':
    main()


