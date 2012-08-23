import os
import re
import subprocess


def getSubTrack(filePath, toolsDir):
    if not os.path.isdir(toolsDir):
        toolsDir = os.path.split(toolsDir)
    
    infoPath = os.path.join(toolsDir, "mp4box")
    output = subprocess.check_output([infoPath, "-info", filePath])

tracks = {}
trackNumber = None
for line in output.splitlines():
	r = re.search('Track # (\d+)', line)
	if r:
		trackNumber = int(r.group(1))
		trackID = trackNumber
		print trackNumber
		r = re.search('TrackID (\d+)', line)
		if r:
			trackID = int(r.group(1))
			print trackID
		tracks[trackNumber] = { 'TID': trackID }
		continue

	r = re.search('Language "(.*)" - Type', line)
	if r:
		language = r.group(1)
		tracks[trackNumber]['language'] = language
		

	r = re.search('Type.+:(.+)"', line)
	if r:
		trackType = r.group(1)
		tracks[trackNumber]['type'] = trackType
		continue

subTrackID = None
for track in tracks.values():
	if track['type'] != 'tx3g':
		continue
	if 'language' in track and track['language'] != 'English':
		continue
	subTrackID = track['TID']
	break
		
    if subTrackID != None:
        print 'Found subtitle track: %d' % subTrackID
    return subTrackID

def extractFromMP4(filePath, toolsDir, trackID):
    
    if not os.path.isdir(toolsDir):
        toolsDir = os.path.split(toolsDir)    
    
	extractPath = os.path.join(toolsDir, "mp4box")
	srtPath = os.path.splitext(filePath)[0] + ".srt"
	subprocess.call([extractPath, "-srt", str(trackID), filePath])
	for filename in os.listdir(os.path.split(filePath)[0]):
		if filename.endswith(".srt"):
			oldsrt = os.path.split(filePath)[0] + "/" + filename
			os.rename(oldsrt, srtPath)
			break
    return srtPath

