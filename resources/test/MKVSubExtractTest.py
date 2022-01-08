#!/usr/bin/env python

import sys
import os
import time
import unittest

MY_DIR = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.abspath(os.path.join(MY_DIR, "../lib")))

from MKVSubExtract import MKVExtractor

# Global movie path not checked into repo
movie_path = "/Users/scottbrown/Movies/Sherlock Holmes/cbgb-sherlockholmes720.mkv"


class TestProcess(unittest.TestCase):
    def test_get_track(self):
        x = MKVExtractor()
        sub_track = x.getSubTrack(movie_path)
        self.assertEqual(sub_track, 3)

    def test_extract_srt(self):
        x = MKVExtractor()
        sub_track = x.getSubTrack(movie_path)
        x.startExtract(movie_path, sub_track)

        self.assertTrue(x.isRunning())
        self.assertTrue(x.progress < 100)

        prevProgress = 0
        while x.isRunning():
            # self.assertTrue(x.getSubFile() == None)
            self.assertTrue(x.progress >= prevProgress)
            print("Progress: %d" % x.progress)
            prevProgress = x.progress
            time.sleep(0.1)

        self.assertEqual(x.progress, 100)

        sub_file = x.getSubFile()
        self.assertTrue(sub_file is not None)
        self.assertTrue(os.path.isfile(sub_file))


if __name__ == "__main__":
    unittest.main()