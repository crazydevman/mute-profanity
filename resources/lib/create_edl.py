'''
Created on Apr 7, 2012

@author: Scott Brown

Command line tool used to create an EDL

'''

import sys
from EDLManager import EDLManager
import filter

def main():
    args = sys.argv
    if len(args) < 3:
        print "Usage: srtFile filterFile"
        sys.exit()

    categories = filter.parse_file(args[2])
    profanity = filter.get_all_words(categories)
    worker = EDLManager(args[1], profanity)
    
    if len(args) == 4:
        worker.setEDLName(args[3])
        
    worker.updateEDL()
    
    print "EDL file %s created / or updated" % worker.edlLoc
    
if __name__ == '__main__':
    main()

