import os
import re
import subprocess

def log(*args):
    for arg in args:
        print arg
        
class MP4Extractor:
    def __init__(self, toolsDir=''):
        self.toolsDir = toolsDir
        self.progress = 0

    def getSubTrack(self, filePath):
        infoPath = os.path.join(self.toolsDir, "mp4box")
        process = subprocess.Popen([infoPath, "-info", filePath], stdout=subprocess.PIPE)
        output = process.communicate()[0]
        retcode = process.poll()
        if retcode != 0:
            log("Bad return code when running mp4box: %d" % retcode)
            return None
    
        tracks = {}
        trackNumber = None
        for line in output.splitlines():
            r = re.search('Track # (\d+)', line)
            if r:
                trackNumber = int(r.group(1))
                trackID = trackNumber
                r = re.search('TrackID (\d+)', line)
                if r:
                    trackID = int(r.group(1))
                tracks[trackNumber] = { 'TID': trackID }

            r = re.search('Language "(.*)" - Type', line)
            if r:
                language = r.group(1)
                tracks[trackNumber]['language'] = language

            r = re.search('Type.+:(.+)"', line)
            if r:
                trackType = r.group(1)
                tracks[trackNumber]['type'] = trackType
    
        subTrackID = None
        for track in tracks.values():
            log("Track info: %s" % track)
            if 'type' not in track or track['type'] != 'tx3g':
                continue
            if 'language' in track and track['language'] != 'English':
                continue
            subTrackID = track['TID']
            break
            
        if subTrackID != None:
            print 'Found subtitle track: %d' % subTrackID
        return subTrackID
    
    def startExtract(self, filePath, trackID):
        self.progress = 0
        extractPath = os.path.join(self.toolsDir, "mp4box")
        self.srtPath = os.path.splitext(filePath)[0] + ".srt"
        self.result = subprocess.call([extractPath, "-srt", str(trackID), filePath])
        
        #Rename the file
        head = os.path.splitext(os.path.basename(self.srtPath))[0]
        log("Checking for srt file that begins with %s" % head)
        for filename in os.listdir(os.path.split(filePath)[0]):
            if filename.endswith(".srt") and filename.startswith(head):
                oldsrt = os.path.join(os.path.split(filePath)[0], filename)
                log("Renaming the srt file mp4 box produced from %s to %s" % (oldsrt, self.srtPath))
                os.rename(oldsrt, self.srtPath)
                break
        
    def cancelExtract(self):
        pass
        
    def isRunning(self):
        return False
    
    def getSubFile(self):
        if self.result == 0:
            return self.srtPath
        return None

