import os
import re
import threading
import subprocess
import select
import fcntl

class MKVExtractor:
    def __init__(self, toolsDir=''):
        self.toolsDir = toolsDir
        self.progress = 0;

    def getSubTrack(self, filePath):
        '''Uses mkvinfo to find the track that contains the subtitles'''
        infoPath = os.path.join(self.toolsDir, "mkvinfo")
        proc = subprocess.Popen([infoPath, filePath], stdout=subprocess.PIPE)
        output = proc.communicate()[0]
        
        tracks = {}
        trackNumber = None
        for line in output.splitlines():
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
            if 'codec' in track and track['codec'] != 'S_TEXT/UTF8':
                continue
            subTrackID = track['TID']
            break
        
        return subTrackID
    
    def startExtract(self, filePath, trackID):
        extractPath = os.path.join(self.toolsDir, "mkvextract")
        srtPath = os.path.splitext(filePath)[0] + ".srt"
        args = [extractPath, "tracks", filePath, str(trackID) + ':' + srtPath]
        
        self.proc = subprocess.Popen(args, stdout=subprocess.PIPE,
                                     stderr=subprocess.STDOUT)
        
        self.mThread = threading.Thread(target=self.monitorThread)
        self.mThread.setDaemon(True)
        self.mThread.start()
        
    def monitorThread(self):
        '''Monitor Thread is running as long as the process is running'''
        outfile=self.proc.stdout 
        outfd=outfile.fileno() 
        file_flags = fcntl.fcntl(outfd, fcntl.F_GETFL) 
        fcntl.fcntl(outfd, fcntl.F_SETFL, file_flags | os.O_NDELAY) 

        while not self.proc.poll(): 
            ready = select.select([outfd],[],[]) # wait for input 
            if outfd in ready[0]: 
                outchunk = outfile.read() 
                if outchunk == '': 
                    break 
            select.select([],[],[],.1) # give a little time for buffers to fill 

            # extract percentages from string "Progress: n%"
            r = re.search('Progress:\s+(\d+)', outchunk)
            if r:
                self.progress = int(r.group(1))
    
    def cancelExtract(self):
        returnCode = self.proc.poll()
        if returnCode is not None:
            return
        self.proc.terminate()
        
    def isRunning(self):
        return self.mThread.isAlive()
