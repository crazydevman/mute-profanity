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
import tempfile
import Queue

class Process(object):
    def __init__(self, args):
        if os.name == 'nt':
            self.proc = subprocess.Popen(args, stdout=subprocess.PIPE, universal_newlines=True)
            self.stdout = self.proc.stdout
        else:
            self._unix_lock = threading.RLock()

            self._unix_complete = False
            self._unix_exit_code = None
            self._unix_output = None

            self._unix_fifo = tempfile.NamedTemporaryFile()
            #self._unix_fifo_name = os.path.join(tempfile.gettempdir(), 'fifo')

            t = threading.Thread(target=self.unix_execute, args=(args, ))
            t.setDaemon(True)
            t.start()

    def unix_execute(self, args):
        """
        This should execute in another process/thread, as it blocks till execution is complete
        """
        cmd = ' '.join("'" + arg + "'" for arg in args) + " > " + self._unix_fifo.name
        print 'Executing this command: ' + cmd
        #xbmc.executebuiltin('System.Exec(%s)' % cmd)
        self._unix_exit_code = os.system(cmd)

        print "Done..."
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
            with open(self._unix_fifo.name, 'r') as file:
                for line in self.read_file(file):
                    print "Read the line: %s" % line
                    print "Which has len of %d" % len(line)
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
            self._unix_complete = True
            self._unix_exit_code = 1

    def get_outlines(self):
        if os.name == 'nt':
            return self.stdout.readlines()
        else:
            with open(self._unix_fifo.name, 'rU') as file:
                lines = []
                for line in self.read_file(file):
                    lines.append(line)
                return lines

    def read_file(self, file):
        line = []
        while True:
            c = file.read(1)
            if not c:
                if self._unix_complete:
                    if line:
                        yield ''.join(line)
                    break
                else:
                    time.sleep(.1)
                    continue

            if c in ('\n', '\r'):
                full = ''.join(line)
                print "Yielding line: %s" % full
                line = []
                yield full
            else:
                line.append(c)

