'''
Created on Sept 16, 2012

@author: fauxpaux (modified code from Scott Brown)
'''

import sys
import re
import xbmc

class NewSRTCreator(object):
    '''
    classdocs
    '''

    def __init__(self, srtLoc, filterLoc):
        '''
        Constructor
        '''
        self.srtLoc = srtLoc
        self.filterLoc = filterLoc
        self.srtNewLoc = srtLoc[:-3] + "tmp"
        
    def setNewSRTName(self, name):
        self.srtNewLoc = name
        
    def createNewSRT(self):
        try:
            srtFile = open(self.srtLoc, 'rU')
            filterFile = open(self.filterLoc, 'rU')
            NewSRTFile = open(self.srtNewLoc, 'w')
        except IOError:
            xbmc.log("Cannot open file")
            sys.exit()
            
        # create profanity list from filter
        profanity = []
        for line in filterFile:
            if len(line):
                asRegex = line.strip().lower().replace('*', '\w*')
                profanity.append(asRegex)
        filterFile.close()

        lines = []
        readLines = srtFile.readlines()
        if len(readLines[1].strip()) == 0:
            for i in range(len(readLines)):
                if i % 2 == 0 or i >= len(readLines) -1:
                    lines.append(readLines[i])
        else:
            lines.extend(readLines)
  
        # loop through subtitles
        i = 0
        while True:
            if i >= len(lines):
                break;
            
            num = lines[i]
            if len(num) == 0:
                # end of file
                break
        
        
            # loop through filter list replacing any matches with asterisks
            subtitle = lines[i]
            for word in profanity:
                regex = r"\b(?i)" + word + r"\b"
                subtitle = re.sub(regex, "*****", subtitle)
            NewSRTFile.write(subtitle)
            i+=1

            
        # close files 
        NewSRTFile.close()
        filterFile.close()
        srtFile.close()
        return True

