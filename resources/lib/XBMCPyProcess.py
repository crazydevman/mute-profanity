#!/usr/bin/env python

import subprocess
import popen2
import os
import signal
import threading

class Process(object):
    def __init__(self, args):
        if os.name == 'nt':
            self.proc = subprocess.Popen(args, stdout=subprocess.PIPE, universal_newlines=True)
            self.stdout = self.proc.stdout
        else:
            self.proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print self.proc.communicate()[0]
            #self.stdout = self.proc.stdout
            #self.proc = popen2.Popen3(args, capturestderr=True)
            #self.proc.tochild.close()
            #self.stdout = self.proc.fromchild
            
            print 'pid %d created' % self.proc.pid
            
            #t = threading.Thread(target=self._unix_reading_thread)
            #t.setDaemon(True)
            #t.start()
            
    def start_monitor_thread(self, OnRead=None, OnFinish=None):
        if os.name == 'nt':
            target = self.windows_reading_thread
        else:
            target = self._unix_reading_thread
            
        t = threading.Thread(target=self._unix_reading_thread, args=(OnRead,OnFinish))
        t.start()
        return t
    
    def _windows_reading_thread(self, OnRead, OnFinish):
        while not self.proc.poll(): 
            line = outfile.readline()
            if OnRead:
                OnRead(line)
            if not len(line):
                break
        
        self.proc.wait()
        if OnFinish:
            OnFinish()
            
    def _unix_reading_thread(self, OnRead, OnFinish):
        import select
        import fcntl
        
        outfile=self.proc.fromchild
        outfd=outfile.fileno() 
        file_flags = fcntl.fcntl(outfd, fcntl.F_GETFL) 
        fcntl.fcntl(outfd, fcntl.F_SETFL, file_flags | os.O_NDELAY)
        
        while True:
            if self.poll() != None:
                if OnFinish:
                    OnFinish()
                break
            
            rlist, wlist, xlist = select.select([outfd], [], [], .1)
            if not rlist:
                continue
            
            outchunk = outfile.read()
            if outchunk:
                if OnRead:
                    OnRead(outchunk)
            else:
                break
        
        self.proc.wait()
        
    def wait(self):
        return self.proc.wait()
            
    def poll(self):
        if os.name == 'nt':
            return self.proc.poll()
        else:
            result = self.proc.poll()
            if result == -1:
                return None
            return result
        
    def kill(self):
        if os.name == 'nt':
            self.proc.kill()
        else:
            os.kill(self.proc.pid, signal.SIGKILL)
            self.proc.wait()
