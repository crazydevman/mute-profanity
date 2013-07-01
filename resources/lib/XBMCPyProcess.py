#!/usr/bin/env python

import subprocess
import popen2
import os
import commands
import signal
import threading
import multiprocessing
import threading
import time
import re
import xbmc

class Process(object):
    def __init__(self, args):
        if os.name == 'nt':
            self.proc = subprocess.Popen(args, stdout=subprocess.PIPE, universal_newlines=True)
            self.stdout = self.proc.stdout
        else:
            #self.proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            #print self.proc.communicate()[0]
            #self.stdout = self.proc.stdout

            #carr = multiprocessing.Array('c', 1024000) #TODO: determine size
            #self._unix_proccess = multiprocessing.Process(target=self.unix_execute, args=(args, carr))
            #self._unix_proccess.start()
            #self._unix_out = carr

            #print 'pid %d created' % self._unix_proccess.pid

            #TODO: locks
            t = threading.Thread(target=self.unix_execute(args))
            t.setDaemon(True)
            t.start()

            self._unix_complete = False
            self._unix_exit_code = None
            self._unix_output = None

    def unix_execute(self, args):
        """
        This should execute in another process, as it blocks
        """
        cmd = ' '.join(args) + " > /tmp/run.out"
        print 'Executing this command: ' + cmd
        #xbmc.executebuiltin('System.Exec(%s)' % cmd)
        self._unix_exit_code = os.system(cmd)
        #self._unix_exit_code, self._unix_output = commands.getstatusoutput(cmd)
        #self._unix_exit_code = 0
        #self._unix_output = "line1\nline2"
        self._unix_complete = True
            
    def start_monitor_thread(self, OnRead=None, OnFinish=None):
        if os.name == 'nt':
            target = self._windows_reading_thread
        else:
            target = self._unix_reading_thread
            
        t = threading.Thread(target=target, args=(OnRead,OnFinish))
        t.start()
        return t
    
    def _windows_reading_thread(self, OnRead, OnFinish):
        while not self.proc.poll(): 
            line = self.stdout.readline()
            if OnRead:
                OnRead(line)
            if not len(line):
                break
        
        self.proc.wait()
        if OnFinish:
            OnFinish()
            
    def _unix_reading_thread(self, OnRead, OnFinish):

        if OnRead:
            for line in self.get_outlines():
                print "Calling OnRead for line: %s" % line
                OnRead(line)
        if OnFinish:
            OnFinish()
        
    def wait(self):
        if os.name == 'nt':
            return self.proc.wait()
        else:
            while not self._unix_complete:
                time.sleep(.05)
            
    def poll(self):
        if os.name == 'nt':
            return self.proc.poll()
        else:
            return self._unix_exit_code
        
    def kill(self):
        if os.name == 'nt':
            self.proc.kill()
        else:
            #TODO: handle kill
            pass

    def get_outlines(self):
        if os.name == 'nt':
            return self.stdout.readlines()
        else:
            return re.split('\r|\n', self._unix_output)

