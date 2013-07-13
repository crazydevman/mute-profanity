import os
import re

from XBMCPyProcess import Process
import ssatool

def log(*args):
    arr = []
    for arg in args:
        arr.append(str(arg))
    print ' '.join(arr)

class MKVExtractor:
    def __init__(self, toolsDir=''):
        log("toolsDir: %s" % toolsDir)

        self.toolsDir = toolsDir
        self.progress = 0
        self.mThread = None
        self.trackExt = None

    def getSubTrack(self, filePath):
        """Uses mkvinfo to find the track that contains the subtitles"""
        infoPath = os.path.join(self.toolsDir, "mkvinfo")
        log('path to executable mkvinfo: %s' % infoPath)
        log('path of file to check %s' % filePath)
        proc = Process([infoPath, filePath])
        proc.wait()
        output = proc.get_outlines()
        log('output was %s' % output)
        log('Result was %d' % proc.poll())
        
        tracks = {}
        trackNumber = None
        for line in output:
            r = re.search('[+] Track number: (\d+)', line)
            if r:
                trackNumber = int(r.group(1))
                trackID = trackNumber
                r = re.search('track ID .*: (\d+)', line)
                if r:
                    trackID = int(r.group(1))
                tracks[trackNumber] = { 'TID': trackID }
                continue
    
            r = re.search('[+] Track type: (.+)', line)
            if r:
                trackType = r.group(1)
                tracks[trackNumber]['type'] = trackType
                continue
    
            r = re.search('[+] Language: (.+)', line)
            if r:
                language = r.group(1)
                tracks[trackNumber]['language'] = language
                continue
            
            r = re.search('[+] Codec ID: (.+)', line)
            if r:
                codec = r.group(1)
                tracks[trackNumber]['codec'] = codec
                continue
        
        subTrackID = None
        for track in tracks.values():
            if track['type'] != 'subtitles':
                continue
            if 'language' in track and track['language'] != 'eng':
                continue
            if 'codec' in track and track['codec'] == 'S_TEXT/SSA':
                subTrackID = track['TID']
                self.trackExt = '.ssa'
                continue # keep looking for srt
            if 'codec' in track and track['codec'] == 'S_TEXT/ASS':
                subTrackID = track['TID']
                self.trackExt = '.ass'
                continue # keep looking for srt
            if 'codec' in track and track['codec'] == 'S_TEXT/UTF8':
                subTrackID = track['TID']
                self.trackExt = ".srt"
                break # srt trumps other formats
        
        return subTrackID
    
    def startExtract(self, filePath, trackID):
        self.progress = 0
        extractPath = os.path.join(self.toolsDir, "mkvextract")
        self.outPath = os.path.splitext(filePath)[0] + self.trackExt
        args = [extractPath, "tracks", filePath , str(trackID) + ':' + self.outPath]
        log('executing args: %s' % args)
        
        self.proc = Process(args)
        self.mThread = self.proc.start_monitor_thread(self._ReadProgress, self._FinishExtract)
        
    def _ReadProgress(self, line):
        #log('Reading line: ', line)
        # extract percentages from string "Progress: n%"
        r = re.search("Progress:\s+(\d+)", line)
        if r:
            self.progress = int(r.group(1))
            
    def _FinishExtract(self):
        log("Ending execution")
        try:
            self.proc.kill()
        except:
            pass
        self.mThread = None
    
    def cancelExtract(self):
        returnCode = self.proc.poll()
        if returnCode is not None:
            return
        self.proc.kill()
        
    def isRunning(self):
        if self.mThread:
            return self.mThread.isAlive()
        return False
    
    def getSubFile(self):
        if self.progress != 100:
            if self.proc.poll() != 0:
                return None
            
        if self.trackExt == '.srt':
            return self.outPath
        
        #Convert the SSA file to SRT
        try:
            return ssatool.main(self.outPath)
        except:
            log("Unable to perform the conversion from SSA to SRT")
        return None