import os
import re
import subprocess

def getSubTrack(filePath, toolsDir):
    
    if not os.path.isdir(toolsDir):
        toolsDir = os.path.split(toolsDir)
    
    infoPath = os.path.join(toolsDir, "mkvinfo")
    output = subprocess.check_output([infoPath, filePath])
    
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
            
    if subTrackID != None:
        print 'Found subtitle track: %d' % subTrackID
    return subTrackID

def extractFromMKV(filePath, toolsDir, trackID):
    
    if not os.path.isdir(toolsDir):
        toolsDir = os.path.split(toolsDir)    
    
    extractPath = os.path.join(toolsDir, "mkvextract")
    srtPath = os.path.splitext(filePath)[0] + ".srt"
    return subprocess.call([extractPath, "tracks", filePath, str(trackID) + ':' + srtPath])

