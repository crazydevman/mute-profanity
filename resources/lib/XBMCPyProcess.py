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

class Process(object):
    def __init__(self, args):
        if os.name == 'nt':
            self.proc = subprocess.Popen(args, stdout=subprocess.PIPE, universal_newlines=True)
            self.stdout = self.proc.stdout
        else:
            #self.proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            #print self.proc.communicate()[0]
            #self.stdout = self.proc.stdout

            carr = multiprocessing.Array('c', 1024000) #TODO: determine size
            self._unix_proccess = multiprocessing.Process(target=self.unix_execute, args=(args, carr))
            self._unix_proccess.start()
            self._unix_out = carr

            print 'pid %d created' % self._unix_proccess.pid
            
            #t = threading.Thread(target=self._unix_reading_thread)
            #t.setDaemon(True)
            #t.start()

    def unix_execute(self, args, carr):
        """
        This should execute in another process, as it blocks
        """
        cmd = ' '.join(args)
        print 'Executing this command: ' + cmd
        code, output = commands.getstatusoutput(cmd)
        carr.value = output
            
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
        if self._unix_proccess.is_alive():
            self._unix_proccess.join()

        if OnRead:
            for line in self.get_outlines():
                print "Calling OnRead for line: %s" % line
                OnRead(line)
        if OnFinish:
            OnFinish()
        
    def wait(self):
        if os.name == 'nt':
            return self.proc.wait()
        elif self._unix_proccess.is_alive():
            self._unix_proccess.join()
            
    def poll(self):
        if os.name == 'nt':
            return self.proc.poll()
        else:
            if self._unix_proccess.is_alive():
                return None
            return self._unix_proccess.exitcode
        
    def kill(self):
        if os.name == 'nt':
            self.proc.kill()
        elif self._unix_proccess.is_alive():
            self._unix_proccess.terminate()

    def get_outlines(self):
        if os.name == 'nt':
            return self.stdout.readlines()
        else:
            return re.split('\r|\n', self._unix_out.value)

