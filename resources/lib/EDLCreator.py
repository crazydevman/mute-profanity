'''
Created on Apr 7, 2012

@author: Scott Brown
'''
#TODO:
#Extract srt from mp4 (use mp4Box)
#Option to edit srt file and **** profanity and/or make "profanity-bleeped only" srt
#DONE -- Determine how to make find command search for complete words
#Option to export edl as txt for use in audacity
#Option to import existing edl with skips
#DONE -- Expand profanity list
#Option to have categories of profanity bleeped (profanities, vulgarities, sexual explicits)

import sys
import re

class EDLCreator(object):
    '''
    classdocs
    '''

    def __init__(self, srtLoc, filterLoc, safety=.35):
        '''
        Constructor
        '''
        self.srtLoc = srtLoc
        self.filterLoc = filterLoc
        self.safety = safety
        self.edlLoc = srtLoc[:-3] + "edl"
        
    def setEDLName(self, name):
        self.edlLoc = name
        
    def createEDL(self):
        try:
            srtFile = open(self.srtLoc, 'rU')
            filterFile = open(self.filterLoc, 'rU')
            edlFile = open(self.edlLoc, 'w')
        except IOError:
            print "Cannot open file"
            sys.exit()
        #ignored = []
        ignored = ["<i>", "</i>", "<b>", "</b>", "<u>", "</u>", " '", "' ", "\"", "[", "]", "{", "}"]
        one_char = ["&nbsp;", "\r\n", "\n", "\r", "<br>", ".", ",", "?", "!", ";"]

        # create profanity list from filter
        profanity = []
        for line in filterFile:
            profanity.append(line[:-1].lower())
        filterFile.close()

        print ("profanity: %s" % profanity)
        
        lines = []
        readLines = srtFile.readlines()
        if len(readLines[1].strip()) == 0:
            print "Stupid SRT file didn't do formatting correctly, fix it"
            for i in range(len(readLines)):
                if i % 2 == 0 or i >= len(readLines) -1:
                    lines.append(readLines[i])
        else:
            lines.extend(readLines)
  
        print "New lines: %s" % lines

        # loop through subtitles
        i = 0
        while True:
            # read caption number
            if i >= len(lines):
                break;
            
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
                srtFile.newlines
        
            # read next lines into single subtitle string
            subtitle = ""
            line = lines[i]
            i+=1
            while (line != '\n'): # blank line indicates end of subtitle
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
            
            
            mutes = []
        
            for word in profanity:
				regex = r"\b" + re.escape(word) + r"\b"
				iterator = re.finditer(regex, subtitle, re.IGNORECASE)
				for match in iterator:					
					mute = (match.start(), len(word))
					mutes.append(mute)   
        
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
                    edlFile.write(str(mStart) + "\t" + str(mFinish) + "\t1\n");
            
        # close files    
        edlFile.close()
        filterFile.close()
        srtFile.close()

def sfloat(times, start, end):
    try:
        return float(times[start:end])    
    except:
        print "Failure on string %s " % times
        return 0
