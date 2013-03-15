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
        self.assertTrue(proc.poll() != None)
        
    def test_get_output(self):
        args = ['python', 'PrintNumExec.py', '10']
        proc = Process(args)
        
        #Test the command ran without problem
        self.assertEqual(proc.poll(), None)
        
        for line in proc.stdout.readlines():
            print "Line: %s" % line
        
        self.assertTrue(proc.poll() != None)
        
    def test_pipe_output(self):
        args = ['python', 'PrintNumExec.py', '12']
        proc = Process(args)
        
        #Test the command ran without problem
        self.assertEqual(proc.poll(), None)
        
        while not proc.poll():
            line = proc.stdout.readline()
            if not line:
                break
            print "Line: %s" % line
            
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