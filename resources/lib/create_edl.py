'''
Created on Apr 7, 2012

@author: Scott Brown

Command line tool used to create an EDL

'''

import sys
from resources.lib.EDLManager import EDLManager

def main():
    args = sys.argv
    if len(args) < 3:
        print "Usage: srtFile filterFile"
        sys.exit()
        
    worker = EDLManager(args[1], args[2]);
    
    if len(args) == 4:
        worker.setEDLName(args[3])
        
    worker.createEDL()
    
    print "EDL file %s created" % worker.edlLoc
    
if __name__ == '__main__':
    main()

