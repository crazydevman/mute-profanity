#!/usr/bin/env python
'''
Created on Sept 10, 2012

@author: Scott Brown
'''

import time
import subprocess
import threading
import os

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
        
        #TODO: xbmc execute script?
        self.proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        
        self.mThread = threading.Thread(target=self.monitorThread)
        self.mThread.setDaemon(True)
        self.mThread.start()
        
    def monitorThread(self):
        '''Monitor Thread is running as long as the process is running'''
        logfile = self.proc.stderr
        output = self.proc.stdout
        
        while not self.proc.poll():
            line = logfile.readline()
            if line != '':
                log(line)
            else:
                break
            
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