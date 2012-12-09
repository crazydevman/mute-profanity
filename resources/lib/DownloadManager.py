#!/usr/bin/env python
'''
Created on Sept 10, 2012

@author: Scott Brown
'''

import time
import threading
from multiprocessing import Process, Array
import os

import SubDownloader

def log(*args):
    for arg in args:
        print arg
        
def ProcessTarget(filePath, language, c_arr):
    srtFile = SubDownloader.FindSubtitles(filePath, language)
    c_arr.value = srtFile

class Manager:
    def __init__(self):
        self.mThread = None
        self.srtPath = None
        
    def startDL(self, filePath, language):
        #path = os.path.join(os.path.dirname(__file__), "SubDownloader.py")
        #args = ["python", path, filePath, language]
        #log('executing args: %s' % args)
        
        #TODO: xbmc execute script?
        #self.proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        self.c_arr = Array('c', 256)
        self.proc = Process(target=ProcessTarget, args=(filePath, language, self.c_arr))
        self.proc.start()
    
    def cancelDL(self):
        self.proc.terminate()
        
    def isRunning(self):
        try:
            return self.proc.is_alive()
        except:
            return False
    
    def getSubFile(self):
        self.srtPath = self.c_arr.value
        if len(self.srtPath) == 0:
            return None
        return self.srtPath