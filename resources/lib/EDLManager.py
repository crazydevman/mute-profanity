"""
Created on Apr 7, 2012
Last Update on Apr 23, 2015

@author: Scott Brown
"""

import sys
import re
import os

MUTE_PROFANITY_MARKER_START = "###### This section is automatically maintained by the Mute Profanity plugin ######"
MUTE_PROFANITY_MARKER_END = "###### END Mute Profanity plugin section ######"

class EDLManager(object):
    def __init__(self, srtLoc, fileLoc, blocked_words, safety=.35):
        """
        Constructor
        """
        self.srtLoc = srtLoc
        self.blocked_words = blocked_words
        self.safety = safety
        self.edlLoc = os.path.splitext(fileLoc)[0] + ".edl"
        self.modify_srt = False
        
    def setEDLName(self, name):
        self.edlLoc = name
        
    def _prepareEDL(self):
        """
        Prepares the EDL file by removing the section that is managed by this plugin
        """
        if not os.path.isfile(self.edlLoc):
            edlFile = open(self.edlLoc, 'w')
        else:
            edlFile = open(self.edlLoc, 'r+')
            inMPSection = False
            lines_to_write = []
            for line in edlFile.readlines():
                if inMPSection:
                    if line.startswith(MUTE_PROFANITY_MARKER_END):
                        inMPSection = False
                elif not line.startswith(MUTE_PROFANITY_MARKER_START):
                    lines_to_write.append(line)
                else:
                    inMPSection = True

            edlFile.seek(0)
            if lines_to_write:
                print "About to write these lines: %s" % str(lines_to_write)
                edlFile.writelines(lines_to_write)

        edlFile.write("\n")
        edlFile.write(MUTE_PROFANITY_MARKER_START)
        edlFile.write("\n")
        return edlFile
        
    def updateEDL(self):
        try:
            srtFile = open(self.srtLoc, 'rU')
        except IOError:
            print "Cannot open .srt file"
            sys.exit()
        
        try:
            edlFile = self._prepareEDL()
        except:
            print "Unable to write to edl file"
            sys.exit()
        
        ignored = ["<i>", "</i>", "<b>", "</b>", "<u>", "</u>", " '", "' ", "\"", "[", "]", "{", "}"]
        one_char = ["&nbsp;", "\r\n", "\n", "\r", "<br>", ".", ",", "?", "!", ";"]

        print ("profanity: %s" % self.blocked_words)
        
        lines = []
        readLines = srtFile.readlines()
        if len(readLines[1].strip()) == 0:
            print "Stupid SRT file didn't do formatting correctly, fix it"
            for i in range(len(readLines)):
                if i % 2 == 0 or i >= len(readLines) -1:
                    lines.append(readLines[i])
        else:
            lines.extend(readLines)
  
        #print "New lines: %s" % lines

        # loop through subtitles
        i = 0
        while True:
            # read caption number
            if i >= len(lines):
                break
            
            num = lines[i]
            i+=1
            if len(num) == 0:
                # end of file
                break
        
            # read time span of caption
            times = lines[i].strip()
            i+=1
            if len(times) == 0:
                times = srtFile.readline().strip()
        
            # read next lines into single subtitle string
            subtitle = ""
            line = lines[i]
            i+=1
            while line != '\n' and i < len(lines): # blank line indicates end of subtitle
                subtitle += line.lower()
                line = lines[i]
                i+=1
        
            # modify to remove characters that don't apply to our calculation
            for ignore in ignored:
                subtitle = subtitle.replace(ignore, "")
            for one in one_char:
                subtitle = subtitle.replace(one, " ")
            subtitle = subtitle.strip()
            subtitle = subtitle.strip(' -?!.')
            
            # find matches, store timing and muted word in mutes array
            mutes = []
            for word in self.blocked_words:
                word = word.replace('*', '\w*')
                regex = r"\b" + word + r"\b"
                iterator = re.finditer(regex, subtitle, re.IGNORECASE)
                for match in iterator:
                    #print "match: %s" % match
                    if match.start() not in [x[0] for x in mutes]:
                        mute = (match.start(), (match.end() - match.start()), match.group(0))
                        mutes.append(mute)
                    else:
                        print 'skipping match because this word was already matched'
            
            if mutes:
                mutes = sorted(mutes, key=lambda mute:mute[0])
                print "Subtitle: '%s'\n->Mute at %s" % (subtitle, mutes)

                # convert time to seconds
                tStart = (sfloat(times, 0, 2) * 3600.0 + 
                      sfloat(times, 3, 5) * 60.0 + 
                      sfloat(times, 6, 8) + 
                      sfloat(times, 9, 12) / 1000.0)
                tFinish = (sfloat(times, 17, 19) * 3600.0 + 
                       sfloat(times, 20, 22) * 60.0 + 
                       sfloat(times, 23, 25) + 
                       sfloat(times, 26, 29) / 1000.0)
                tDuration = tFinish - tStart
                durationPerChar = tDuration / len(subtitle)
            
                for mute in mutes:
                    mStart = max(0, mute[0] * durationPerChar - self.safety) + tStart
                    mFinish = min((mute[1] * durationPerChar) + (tStart + mute[0] * durationPerChar) + self.safety, tFinish)
                    edlFile.write("%09.3f\t%09.3f\t1\t#Muted:'%s'\n" % (mStart, mFinish, mute[2]))

        edlFile.write(MUTE_PROFANITY_MARKER_END)
        edlFile.write("\n")
        # close files    
        edlFile.close()
        print "Done creating the EDL"

        if self.modify_srt:
            print "Overwriting the existing srt file with stars"
            print "First create a new file with the swears blocked out"
            NewSRTFile = self.open_file(self.srtLoc + ".tmp", 'w')
            srtFile.seek(0)
            for line in srtFile.readlines():
                for word in self.blocked_words:
                    word = word.replace('*', '\w*')
                    regex = r"\b(?i)" + word + r"\b"
                    line = re.sub(regex, "*****", line)
                NewSRTFile.write(line)

            NewSRTFile.close()
            srtFile.close()

            print "New file created, move the original srt so it's not lost"
            self.rename(self.srtLoc, self.srtLoc + ".bak")
            print "New path for original srt file: " + self.srtLoc + ".bak (not edited)"
            print "Now move the newly created srt file to the original location"
            self.rename(self.srtLoc + ".tmp", self.srtLoc)
            print "Done with srt file edit"
        else:
            srtFile.close()


    def open_file(self, filePath, mode):
        return open(filePath, mode)

    def rename(self, src, dst):
        os.rename(src, dst)

def sfloat(times, start, end):
    try:
        return float(times[start:end])    
    except:
        print "Failure on string %s " % times
        return 0
