'''
Created on Apr 7, 2012

@author: Scott Brown
'''

import xbmcgui
import xbmcplugin

class UIManager(object):
    '''
    classdocs
    '''

    def __init__(self, plugin):
        '''
        Constructor
        '''
        self.plugin = plugin
        
    def showSimpleListing(self, listing, isDir=True):
        print "plugin: %s" % self.plugin        
        # send each item to xbmc
        for item in listing:
            print "adding item: %s" % item[0]
            print "url will go to %s" % item[1] 
            listItem = xbmcgui.ListItem(item[0])
            xbmcplugin.addDirectoryItem(self.plugin,item[1],listItem, isDir)
            
        # tell xbmc we have finished creating
        xbmcplugin.endOfDirectory(self.plugin)
        
    def showThumbnailListing(self, listing):
        for item in listing:
            listItem = xbmcgui.ListItem(label=item[0], thumbnailImage=item[1])
            xbmcplugin.addDirectoryItem(self.plugin,item[2],listItem)
            
        # tell xbmc we have finished creating
        xbmcplugin.endOfDirectory(self.plugin)
        