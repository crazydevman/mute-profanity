#!/usr/bin/env python

import sys
import os
import unittest

MY_DIR = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.abspath(os.path.join(MY_DIR, '../lib')))

from XBMCPyProcess import Process

def PrintLine(line):
    print line


class TestProcess(unittest.TestCase):
    
    def test_sleep(self):
        args = ['sleep', '3000']
        proc = Process(args)
        
        #Test the command ran without problem
        self.assertEqual(proc.poll(), None)
        
        #Test killing
        proc.kill()
        
        #Test poll returns now
        self.assertTrue(proc.poll() is not None)
        
    def test_get_output(self):
        args = ['python', 'PrintNumExec.py', '10']
        proc = Process(args)
        
        #Test the command ran without problem
        self.assertEqual(proc.poll(), None)

        proc.wait()

        for i, line in enumerate(proc.get_outlines()):
            self.assertEqual(line, "%d\n" % (i+1))
            lastline = line

        self.assertTrue(proc.poll() is not None)
        self.assertEqual(lastline, "10\n")
        
    def test_pipe_output(self):
        args = ['python', 'PrintNumExec.py', '12']
        proc = Process(args)
        
        #Test the command ran without problem
        self.assertEqual(proc.poll(), None)

        self.lastLine = None
        self.finished = False
        mThread = proc.start_monitor_thread(self._ReadProgress, self._FinishExtract)

        mThread.join()

        self.assertTrue(self.finished)
        self.assertEqual(self.lastLine, "12\n")

    def _ReadProgress(self, line):
        self.lastLine = line

    def _FinishExtract(self):
        self.finished = True

    #def test_mkvextract(self):
    #    movie_path = '/??.mkv'
    #    args = ["mkvextract", "tracks", movie_path, '3:/tmp/myfile.srt']
    #    proc = Process(args)
    #    
    #    #Test the command ran without problem
    #    self.assertEqual(proc.poll(), None)
    #    
    #    proc.start_monitor_thread(PrintLine)

if __name__ == '__main__':
    unittest.main()