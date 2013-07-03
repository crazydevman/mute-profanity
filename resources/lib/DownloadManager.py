#!/usr/bin/env python
'''
Created on Sept 10, 2012

@author: Scott Brown
'''

import time
import threading
import os
from XBMCPyProcess import Process

def log(*args):
    for arg in args:
        print arg

class Manager:
    def __init__(self):
        self.mThread = None
        self.srtPath = None
        
    def startDL(self, filePath, language):
        path = os.path.join(os.path.dirname(__file__), "SubDownloader.py")
        args = ["python", path, filePath, language]
        log('executing args: %s' % args)
        
        self.proc = Process(args)
        log('proc created')
        
        self.mThread = threading.Thread(target=self.monitorThread)
        self.mThread.setDaemon(True)
        self.mThread.start()
        
    def monitorThread(self):
        '''Monitor Thread is running as long as the process is running'''
        output = self.proc.stdout
        
        while not self.proc.poll():
            line = output.readline()
            if line != '':
                log(line)
            
        exitCode = self.proc.poll()
        log("Script completed with exit code: %d" % exitCode)
        if exitCode == 0:
            self.srtPath = output.readline()
    
    def cancelDL(self):
        returnCode = self.proc.poll()
        if returnCode is not None:
            return
        self.proc.kill()
        
    def isRunning(self):
        if self.mThread:
            return self.mThread.isAlive()
        return False
    
    def getSubFile(self):
        return self.srtPath